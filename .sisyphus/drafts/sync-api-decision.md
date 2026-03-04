## Critical Design Decision: Synchronous API (2026-03-04)

**Decision**: All public Task and Flow APIs are **synchronous** (`def run()`), not async.

### Rationale

- Flow 作者不需要关心异步细节
- Task 的 `run()` 是同步的
- Flow 的 `run()` 也是同步的
- 内部使用 `asyncio.run()` 封装异步实现

### API Design

```python
# Task - 同步方法
class TaskBase(ABC):
    @abstractmethod
    def run(self) -> Any:  # ← 同步
        pass

# FlowBase - 同步方法
class FlowBase:
    def wait_for_task(self, label: str, timeout: float = 30.0) -> Dict:  # ← 同步
        """内部使用 asyncio.run() + 轮询"""
        
    def run_parallel(self, *tasks: TaskBase) -> List[str]:  # ← 同步
        """内部使用 asyncio.gather() + asyncio.run()"""
        
    def retry_until(self, task_factory, condition, max_retries=3) -> Any:  # ← 同步
        """内部使用 asyncio.run() 循环重试"""
```

### Implementation Pattern

```python
# FlowBase 内部实现
class FlowBase:
    def wait_for_task(self, label: str, timeout: float = 30.0) -> Dict:
        async def _wait_async():
            start_time = time.time()
            while True:
                tasks = self.get_tasks(label)
                if tasks and tasks[-1]["status"] in ["completed", "failed"]:
                    return tasks[-1]
                if time.time() - start_time >= timeout:
                    raise TaskTimeoutError(label, f"Timeout after {timeout}s")
                await asyncio.sleep(0.5)
        
        return asyncio.run(_wait_async())  # ← 同步包装异步
    
    def run_parallel(self, *tasks: TaskBase) -> List[str]:
        async def _run_async():
            async def _run_single(task):
                result = task.run()
                return result
            return await asyncio.gather(*[_run_single(t) for t in tasks])
        
        return asyncio.run(_run_async())  # ← 同步包装异步
```

### Benefits

- ✅ Flow 作者无需理解 asyncio
- ✅ API 更简洁直观
- ✅ 向后兼容现有同步 Flow
- ✅ 内部仍然可以利用异步并发

### Trade-offs

- ⚠️ Task.run() 内部如果要用异步库，需要自己用 `asyncio.run()` 包装
- ⚠️ 不能直接 `await` Task 方法（但这不是问题，因为都是同步的）

### Updated Plan

- Task 1: `TaskBase.run()` → 同步方法
- Task 6: `FlowBase.wait_for_task()` → 同步方法
- Task 7: `FlowBase.run_parallel()` → 同步方法
- Task 8: `FlowBase.retry_until()` → 同步方法

**Status**: ✅ Plan updated to reflect this decision
