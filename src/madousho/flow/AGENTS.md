# src/madousho/flow/ KNOWLEDGE BASE

**Generated:** 2026-03-06
**Commit:** 3b8ad40
**Branch:** master

## OVERVIEW

Flow engine for Madousho.ai - Task-based execution system with fixed flow control. Tasks are atomic execution units managed by FlowBase, with lifecycle tracking, parallel execution support, and Git-based plugin loading.

## STRUCTURE

```
flow/
├── base.py         # FlowBase class, task execution methods (361 lines)
├── loader.py       # FlowLoader plugin loading (332 lines)
├── models.py       # Pydantic v2 flow data models (66 lines)
├── registry.py     # FlowRegistry singleton (93 lines)
├── storage.py      # FlowStorage task persistence (454 lines)
├── tasks/          # Task system
│   ├── __init__.py # Package marker
│   └── base.py     # TaskBase abstract class (96 lines)
└── __init__.py     # Package marker
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Flow execution | `base.py:94-105` | `run()` abstract method |
| Task registration | `base.py:107-131` | `register_task()` assigns UUID |
| Single task execution | `base.py:148-187` | `run_task()` register + execute + save |
| Parallel execution | `base.py:189-240` | `run_parallel()` asyncio.gather |
| Task retry logic | `base.py:242-289` | `retry_until()` with condition |
| Flow hooks | `base.py:291-320` | `on_start()`, `on_complete()`, `on_error()` |
| Task lifecycle | `tasks/base.py:30-96` | `pending` → `running` → `completed` \| `failed` |
| Task definition | `tasks/base.py:10-55` | `TaskBase` abstract class |
| Plugin loading | `loader.py:257-332` | `load_plugin()` - full plugin load flow |
| Config validation | `loader.py:106-163` | `validate_flow_config()` with typehint |
| Flow metadata | `loader.py:168-212` | `load_pyproject_metadata()` from pyproject.toml |
| Module import | `loader.py:215-254` | `import_flow_module()` - dynamic import |
| Atomic writes | `storage.py:14-60` | `AtomicJsonWriter` - tempfile + fsync + os.replace |
| Flow indexing | `storage.py:62-179` | `FlowIndex` - JSONL lazy loading |
| Orphan recovery | `storage.py:392-449` | `recover_orphaned_tasks()` - running but no started_at |
| Flow registry | `registry.py:7-88` | `FlowRegistry` - thread-safe singleton |

## CONVENTIONS

- **Task naming**: `{action}Task` (e.g., `SearchTask`, `SummarizeTask`)
- **Task labels**: Optional grouping via `label` parameter (not unique within Flow)
- **Single responsibility**: Each task does ONE thing only
- **Synchronous execution**: `run()` method is synchronous (not async)
- **Task lifecycle**: `pending` → `running` → `completed` \| `failed`
- **UUID assignment**: On registration via `FlowBase.register_task()`
- **Pydantic v2**: Use `model_validate()`, `model_dump()` (NOT v1 methods)
- **Type hints**: Full typing required (Python 3.10+)
- **Plugin structure**: `src/main.py` must export `FlowClass = MyFlow`

## ANTI-PATTERNS (THIS MODULE)

- DO NOT create tasks without inheriting `TaskBase`
- DO NOT make `run()` method async (must be synchronous)
- DO NOT spawn tasks from within other tasks (tasks cannot spawn)
- DO NOT bypass `register_task()` - UUID required for persistence
- DO NOT modify task state directly (use FlowBase methods)
- DO NOT use Pydantic v1 methods (`.dict()`, `.parse_obj()`)
- DO NOT skip type hints - project uses full typing
- DO NOT skip `FlowClass` export in plugin `src/main.py`
- DO NOT use absolute imports for tasks in plugins - use relative imports

## UNIQUE STYLES

- **Task-based execution model**: Flows execute via discrete Task instances
- **Task-Flow relationship**: Tasks cannot exist independently (require Flow registration)
- **Parallel execution**: `run_parallel()` uses asyncio for concurrent task execution
- **Retry mechanism**: `retry_until()` with custom condition function
- **Lifecycle hooks**: Flow-level `on_start()`, `on_complete()`, `on_error()`
- **Storage integration**: All task states persisted via FlowStorage
- **Label grouping**: Tasks can be queried by label via `get_tasks(label)`
- **Atomic writes**: AtomicJsonWriter ensures crash-safe persistence
- **JSONL indexing**: Global flows.jsonl for lazy loading without loading all flows
- **Orphan recovery**: `recover_orphaned_tasks()` detects crashed processes
- **Plugin validation**: Config validated against `config.typehint.yaml` (optional)
- **Thread-safe registry**: `FlowRegistry` uses double-checked locking

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `FlowBase` | class | base.py:11 | Flow execution base class |
| `TaskBase` | class | tasks/base.py:10 | Task abstract base class |
| `register_task` | method | base.py:107 | Register task, assign UUID |
| `run_task` | method | base.py:148 | Execute single task |
| `run_parallel` | method | base.py:189 | Execute tasks concurrently |
| `retry_until` | method | base.py:242 | Retry with condition |
| `get_tasks` | method | base.py:133 | Query tasks by label |
| `get_flow_class` | fn | base.py:323 | Extract FlowClass from module |
| `FlowStorage` | class | storage.py:181 | Task persistence layer |
| `FlowIndex` | class | storage.py:62 | JSONL flow index |
| `AtomicJsonWriter` | class | storage.py:14 | Atomic JSON writes |
| `load_plugin` | fn | loader.py:257 | Load flow plugin |
| `FlowRegistry` | class | registry.py:7 | Global flow singleton |

## NOTES

- **Task UUID**: Assigned on registration, not on instantiation
- **Task state**: Stored in `_state` attribute (private, not direct access)
- **Flow context**: Accessible via `flow.context` property
- **Storage async**: FlowStorage uses asyncio internally (wrapped by FlowBase)
- **Task result**: Stored in `_result` after successful execution
- **Task error**: Stored in `_error` string on failure
- **Atomic persistence**: tempfile + fsync + os.replace + directory fsync
- **Orphaned task detection**: Running state but no started_at = crashed process
- **File structure**: `data/flow/{uuid}/meta.json` + `{task_uuid}.json`
- **Plugin requirement**: `src/main.py` must export `FlowClass` variable
- **Config validation**: Uses `TypeHintValidator` for config.typehint.yaml
- **Registry thread-safe**: Double-checked locking pattern in `get_instance()`
