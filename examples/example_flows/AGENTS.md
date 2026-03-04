# Example Flow - AGENTS.md

## OVERVIEW

This example demonstrates the Madousho.ai Task system with proper modular architecture. It shows how to create reusable Task classes and compose them in a Flow.

## STRUCTURE

```
example_flows/
├── src/
│   ├── main.py              # Flow definition (ExampleFlow)
│   └── tasks/               # Task module
│       ├── __init__.py      # Task exports
│       ├── search.py        # SearchTask
│       ├── summarize.py     # SummarizeTask
│       └── fetch.py         # DataFetchTask
├── config.yaml              # Flow configuration
├── config.typehint.yaml     # Type hints for config
└── pyproject.toml           # Project metadata
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Flow definition | `src/main.py` | ExampleFlow class, exports `FlowClass` |
| Task definitions | `src/tasks/*.py` | Individual Task classes |
| Task exports | `src/tasks/__init__.py` | `__all__` exports |
| Flow config | `config.yaml` | Custom configuration values |
| Type hints | `config.typehint.yaml` | Config field type hints |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `ExampleFlow` | class | src/main.py:7 | Main Flow demonstrating Task system |
| `SearchTask` | class | src/tasks/search.py:5 | Simulated search task |
| `SummarizeTask` | class | src/tasks/summarize.py:5 | Simulated summarization task |
| `DataFetchTask` | class | src/tasks/fetch.py:5 | Data fetch task with retry support |
| `FlowClass` | variable | src/main.py:59 | Required export for framework |

## CONVENTIONS

- **Task module structure**: Each Task in its own file under `src/tasks/`
- **Task naming**: `{Action}Task` (e.g., `SearchTask`, `SummarizeTask`)
- **Task inheritance**: All Tasks inherit from `TaskBase`
- **Label convention**: Task label matches class name (lowercase, e.g., `"search"`)
- **Logging**: Use `logger.debug()` for Flow execution logs (NOT `print()`)
- **Exports**: `FlowClass = ExampleFlow` is required (framework reads this variable)
- **Imports**: Flow imports tasks from `src.tasks` module using relative imports

## ANTI-PATTERNS (THIS EXAMPLE)

- DO NOT use `print()` - always use `logger.debug()` from `madousho.logger`
- DO NOT put all Tasks in main.py - use `src/tasks/` module
- DO NOT skip `FlowClass` export - framework requires it
- DO NOT use absolute imports for tasks - use relative imports (`from .tasks import ...`)
- DO NOT make `run()` method async - must be synchronous (`def run`, not `async def run`)
- DO NOT spawn tasks from within other tasks - tasks cannot spawn
- DO NOT bypass `register_task()` - UUID required for persistence
- DO NOT modify task state directly - use FlowBase methods

## TASK IMPLEMENTATION PATTERN

```python
from madousho.flow.tasks.base import TaskBase

class MyTask(TaskBase):
    """Task description."""
    
    def __init__(self, param: str):
        super().__init__(label="my_task")
        self.param = param
    
    def run(self):
        # Task logic here
        return {"result": "value"}
```

### Key Requirements:
- Inherit from `TaskBase`
- Call `super().__init__(label="...")` with lowercase label
- Implement synchronous `run()` method (NOT async)
- Return dict with task results

## FLOW IMPLEMENTATION PATTERN

```python
from madousho.flow.base import FlowBase
from madousho.logger import logger
from .tasks import MyTask

class MyFlow(FlowBase):
    """Flow description."""
    
    def run(self):
        logger.debug("Starting flow")
        
        # Sequential execution
        result = self.run_task(MyTask("param"))
        
        # Parallel execution
        results = self.run_parallel(
            MyTask("param1"),
            MyTask("param2"),
            timeout=30.0
        )
        
        # Conditional retry
        retry_result = self.retry_until(
            task_factory=lambda: MyTask("retry_param"),
            condition=lambda r: r.get("success") == True,
            max_retries=3
        )
        
        logger.debug("Flow completed")
        return results

# Required export
FlowClass = MyFlow
```

## TASK SYSTEM FEATURES

### 1. Sequential Execution
```python
result = self.run_task(SearchTask("query"))
```
- Registers task with Flow
- Executes task synchronously
- Saves result to task.json
- Returns task result

### 2. Parallel Execution
```python
results = self.run_parallel(
    DataFetchTask("source_1"),
    DataFetchTask("source_2"),
    timeout=30.0
)
```
- Executes all tasks concurrently
- Returns results list (in input order)
- Raises exception if any task fails

### 3. Task Query by Label
```python
search_tasks = self.get_tasks('search')
fetch_tasks = self.get_tasks('fetch')
```
- Query tasks by label (not unique)
- Returns list of task states
- Label only meaningful within current Flow

### 4. Conditional Retry
```python
result = self.retry_until(
    task_factory=lambda: DataFetchTask("flaky", fail_count=2),
    condition=lambda r: r.get("attempt", 0) > 2,
    max_retries=5
)
```
- Retry until condition is met
- Task factory creates new task instance each retry
- Raises exception after max_retries

## LOGGING

Use `logger.debug()` for all Flow logs:

```python
from madousho.logger import logger

logger.debug("Starting flow")
logger.debug(f"  ✓ Task completed: {result}")
logger.debug("Flow completed successfully!")
```

**Why debug level?**
- Flow execution logs are verbose
- Users can enable with `--verbose` flag
- Keeps normal output clean

## CONFIGURATION

### config.yaml
Custom configuration values (no strict schema):

```yaml
# Flow 的配置
# 这里面的配置项都是自定义的 没有硬性规定

example_use_model_group: ""
example_endpoint: ""
```

### config.typehint.yaml
Type hints for config fields (optional):

```yaml
field_typehint:
  # 路径：类型
  ".example_use_model_group": "MODEL_GROUP"
```

## RUNNING THE EXAMPLE

```bash
# Install in development mode
pip install -e .

# Run the flow
madousho run --file examples/example_flows
```

## TESTING

```bash
# Run tests (if tests exist)
python -m pytest
```

## NOTES

- **Task state persistence**: Tasks are persisted to `data/flow/{uuid}/` as JSON
- **Atomic writes**: Uses `AtomicJsonWriter` with tempfile + fsync + os.replace
- **Flow UUID**: Generated on Flow instantiation
- **Task UUID**: Generated automatically via `register_task()`
- **Crash recovery**: Running tasks marked as failed on restart
