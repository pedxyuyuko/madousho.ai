"""Flow base class - All flows must inherit from this."""
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type
from uuid import uuid4
import asyncio

from madousho.flow.tasks.base import TaskBase
from madousho.flow.storage import FlowStorage


class FlowBase(ABC):
    """
    Flow 基类 - 所有 flow 插件必须继承此类。
    
    Usage:
        class MyFlow(FlowBase):
            def run(self, **kwargs) -> Any:
                # 执行 flow 逻辑
                pass
    
    框架加载流程:
        1. 导入 flow 类的 src/main.py
        2. 找到继承 FlowBase 的类
        3. 实例化：flow_instance = FlowClass(flow_config, global_config)
        4. 框架验证配置（在 __init__ 之前）
        5. 注册到全局注册表
        6. 执行时调用 flow_instance.run()
    """
    
    def __init__(
        self,
        flow_config: Optional[Dict[str, Any]] = None,
        global_config: Optional[Dict[str, Any]] = None,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        description: str = "",
        context: Optional[Dict[str, Any]] = None
    ):
        """
        初始化 flow 实例。
        
        Args:
            flow_config: flow 自己的配置（来自 config.yaml）
            global_config: 全局配置（来自 madousho.yaml，用于 MODEL_GROUP 等验证）
            uuid: Flow UUID（可选，默认自动生成）
            name: Flow name（可选）
            description: Flow description
            context: Flow context data
        
        Note:
            配置验证由框架在实例化之前完成，__init__ 只负责赋值。
        """
        self.flow_config = flow_config or {}
        self.global_config = global_config or {}
        self._uuid = uuid or str(uuid4())
        self._name = name or self.flow_config.get("name", "unnamed_flow")
        self._description = description
        self._context = context or {}
        self._storage = FlowStorage()
        
        # 初始化 flow 存储
        asyncio.run(self._storage.create_flow(
            uuid=self._uuid,
            name=self._name,
            description=self._description,
            context=self._context
        ))
    
    @property
    def uuid(self) -> str:
        """Get the flow UUID."""
        return self._uuid
    
    @property
    def flow_uuid(self) -> str:
        """Get the flow UUID (alias for uuid)."""
        return self._uuid
    
    @property
    def name(self) -> str:
        """Get the flow name."""
        return self._name
    
    @property
    def description(self) -> str:
        """Get the flow description."""
        return self._description
    
    @property
    def context(self) -> Dict[str, Any]:
        """Get the flow context."""
        return self._context
    
    @abstractmethod
    def run(self, **kwargs) -> Any:
        """
        执行 flow 逻辑。
        
        Args:
            **kwargs: 运行时参数
        
        Returns:
            flow 执行结果
        """
        pass
    
    def register_task(self, task: TaskBase, timeout: float = 30.0) -> str:
        """
        Register a task with the flow.
        
        Args:
            task: Task instance to register
            timeout: Task timeout in seconds (default: 30.0)
        
        Returns:
            Task UUID
        """
        task_uuid = str(uuid4())
        task._uuid = task_uuid
        task._flow = self
        task._state = "pending"
        
        # Register in storage
        asyncio.run(self._storage.register_task(
            task_id=task_uuid,
            label=task.label,
            flow_uuid=self._uuid,
            timeout=timeout
        ))
        
        return task_uuid
    
    def get_tasks(self, label: str) -> List[Dict[str, Any]]:
        """
        Get all tasks with matching label (flow-scoped).
        
        Args:
            label: Task label to search for
        
        Returns:
            List of task data dicts (in registration order)
        """
        return asyncio.run(self._storage.get_tasks(
            label=label,
            flow_uuid=self._uuid
        ))
    
    def run_task(self, task: TaskBase, timeout: float = 30.0) -> Any:
        """
        Framework built-in: register + execute + save result + return.
        
        This is the main method for executing a single task.
        
        Args:
            task: Task instance to execute
            timeout: Task timeout in seconds (default: 30.0)
        
        Returns:
            Task execution result
        
        Raises:
            Exception: Task execution fails
        """
        # Register task
        self.register_task(task, timeout)
        
        # Execute task
        task._state = "running"
        try:
            result = task.run()
            task._result = result
            task._state = "completed"
        except Exception as e:
            task._error = str(e)
            task._state = "failed"
            raise
        finally:
            # Save state
            asyncio.run(self._storage.update_task_state(
                flow_uuid=self._uuid,
                task_id=task._uuid,
                state=task._state,
                result=task._result,
                error=task._error
            ))
        
        return result
    
    def run_parallel(
        self,
        *tasks: TaskBase,
        timeout: float = 30.0
    ) -> List[Any]:
        """
        Execute multiple tasks in parallel, block until all complete.
        
        Args:
            *tasks: Task instances to execute
            timeout: Task timeout in seconds (default: 30.0)
        
        Returns:
            List of task results (in input order)
        
        Raises:
            Exception: Any task fails (exceptions are propagated)
        """
        # Register all tasks first
        for task in tasks:
            self.register_task(task, timeout)
        
        # Execute in parallel using asyncio
        async def execute_all():
            async def execute_single(task: TaskBase):
                task._state = "running"
                try:
                    # Run synchronous task in executor
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, task.run)
                    task._result = result
                    task._state = "completed"
                    return result
                except Exception as e:
                    task._error = str(e)
                    task._state = "failed"
                    raise
                finally:
                    await self._storage.update_task_state(
                        flow_uuid=self._uuid,
                        task_id=task._uuid,
                        state=task._state,
                        result=task._result,
                        error=task._error
                    )
            
            # Execute all tasks concurrently
            coroutines = [execute_single(task) for task in tasks]
            results = await asyncio.gather(*coroutines, return_exceptions=False)
            return results
        
        return asyncio.run(execute_all())
    
    def retry_until(
        self,
        task_factory: Callable[[], TaskBase],
        condition: Callable[[Any], bool],
        max_retries: int = 3
    ) -> Any:
        """
        Retry task until condition is met or max_retries exhausted.
        
        Args:
            task_factory: Function that creates a new task instance
            condition: Function that checks if result is acceptable
            max_retries: Maximum number of retry attempts (default: 3)
        
        Returns:
            Task result when condition is met
        
        Raises:
            Exception: Last exception if all retries fail
        """
        last_exception: Optional[Exception] = None
        
        for attempt in range(max_retries):
            try:
                # Create new task instance
                task = task_factory()
                
                # Execute task
                result = self.run_task(task)
                
                # Check condition
                if condition(result):
                    return result  # Success
                
                # Condition not met, prepare for retry
                last_exception = Exception(
                    f"Condition not met after {attempt + 1} attempts"
                )
                
            except Exception as e:
                last_exception = e
                # Exception also triggers retry
        
        # All retries failed
        if last_exception:
            raise last_exception
        else:
            raise Exception("Unknown error in retry_until")
    
    def on_start(self) -> None:
        """
        flow 启动前的钩子（可选覆盖）。
        
        在 run() 被调用之前执行，可用于初始化资源、记录日志等。
        """
        pass
    
    def on_complete(self, result: Any) -> None:
        """
        flow 完成后的钩子（可选覆盖）。
        
        Args:
            result: flow 执行结果
        
        在 run() 成功返回后执行，可用于清理资源、记录结果等。
        """
        pass
    
    def on_error(self, error: Exception) -> None:
        """
        flow 出错时的钩子（可选覆盖）。
        
        Args:
            error: 抛出的异常
        
        在 run() 抛出异常后执行，可用于错误处理、记录日志等。
        此钩子不会重新抛出异常，仅用于清理和记录。
        """
        pass


def get_flow_class(module: Any) -> Type[FlowBase]:
    """
    从模块中获取 FlowClass 变量。
    
    Flow 插件的 src/main.py 必须导出 FlowClass 变量：
    
    Example:
        from madousho.flow.base import FlowBase
        
        class MyFlow(FlowBase):
            def run(self, **kwargs):
                pass
        
        FlowClass = MyFlow  # 必须导出
    
    Args:
        module: 导入的模块（src/main.py）
    
    Returns:
        FlowBase 的子类
    
    Raises:
        ValueError: 如果 FlowClass 不存在或不是 FlowBase 子类
    """
    if not hasattr(module, "FlowClass"):
        raise ValueError(
            f"Module {module} does not export 'FlowClass'. "
            "Please define: FlowClass = YourFlowClassName"
        )
    
    flow_class = getattr(module, "FlowClass")
    
    if not (isinstance(flow_class, type) and issubclass(flow_class, FlowBase)):
        raise ValueError(
            f"FlowClass in {module} must be a subclass of FlowBase, "
            f"got {type(flow_class)}"
        )
    
    return flow_class
