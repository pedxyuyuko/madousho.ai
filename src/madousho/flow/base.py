"""Flow base class - All flows must inherit from this."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type


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
        flow_config: Dict[str, Any],
        global_config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化 flow 实例。
        
        Args:
            flow_config: flow 自己的配置（来自 config.yaml）
            global_config: 全局配置（来自 madousho.yaml，用于 MODEL_GROUP 等验证）
        
        Note:
            配置验证由框架在实例化之前完成，__init__ 只负责赋值。
        """
        self.flow_config = flow_config
        self.global_config = global_config or {}
    
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
