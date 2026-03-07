# Flow Engine

**Location:** `src/madousho/flow/`

## OVERVIEW

Core flow execution engine: FlowBase ABC, TaskBase ABC, async persistence layer, plugin loader, and thread-safe registry.

## STRUCTURE

```
flow/
├── base.py              # FlowBase ABC (run_task, run_parallel, retry_until)
├── storage.py           # FlowStorage, AtomicJsonWriter, FlowIndex (JSONL)
├── loader.py            # Plugin loading (load_plugin, import_flow_module)
├── registry.py          # FlowRegistry singleton (thread-safe)
├── models.py            # FlowPlugin, FlowPluginConfig, PluginLoadResult
├── tasks/
│   ├── base.py          # TaskBase ABC (synchronous run() method)
│   └── __init__.py
└── __init__.py
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Flow execution | `base.py` | FlowBase.run_task(), run_parallel(), retry_until() |
| Task persistence | `storage.py` | AtomicJsonWriter, FlowIndex (JSONL lazy loading) |
| Plugin loading | `loader.py` | load_plugin(), import_flow_module(), validate_flow_config() |
| Flow registry | `registry.py` | FlowRegistry singleton (double-checked locking) |
| Task ABC | `tasks/base.py` | TaskBase with synchronous run() method |
| Flow models | `models.py` | FlowPlugin, FlowPluginConfig, PluginLoadResult |

## CONVENTIONS

- **Task lifecycle**: `pending` → `running` → `completed` | `failed` (managed by FlowBase)
- **Synchronous tasks**: Task.run() MUST be synchronous (FlowBase runs in executor for parallel)
- **Single responsibility**: Each task does ONE thing only
- **No task spawning**: Tasks cannot spawn other tasks (only FlowBase can)
- **UUID requirement**: All tasks registered via FlowBase.register_task() for UUID + persistence
- **Async storage**: All storage operations are async (AtomicJsonWriter.write, FlowIndex.append_flow)
- **Atomic writes**: Storage uses tempfile + fsync + os.replace for crash safety
- **Flow isolation**: Each plugin loaded as unique package (`{name}_{version}.main`)

## ANTI-PATTERNS (THIS MODULE)

- DO NOT make Task.run() async (must be synchronous - FlowBase handles executor)
- DO NOT bypass FlowBase.register_task() (UUID required for persistence)
- DO NOT modify task state directly (use FlowBase.run_task() or run_parallel())
- DO NOT spawn tasks from within Task.run() (tasks cannot spawn)
- DO NOT skip FlowClass export in plugin main.py (loader requires: `FlowClass = YourFlow`)
- DO NOT create FlowBase subclass without implementing run() method (abstract)
- DO NOT use storage directly (use FlowBase methods: run_task, run_parallel, get_tasks)
- DO NOT catch exceptions in Task.run() silently (let FlowBase handle failures)

## UNIQUE PATTERNS

- **Retry until condition**: `retry_until(task_factory, condition, max_retries)` - creates new task instance per retry
- **Parallel execution**: `run_parallel(*tasks, timeout)` - uses asyncio.gather with run_in_executor
- **Label-based querying**: `get_tasks(label)` - returns all tasks with matching label (flow-scoped)
- **JSONL lazy loading**: FlowIndex reads line-by-line with early exit (limit/offset pagination)
- **Plugin package isolation**: Each plugin version loaded as separate Python package (prevents conflicts)
- **Orphaned task recovery**: `recover_orphaned_tasks()` marks running tasks without started_at as failed

## KEY CLASSES

### FlowBase

Abstract base class for all flows. Provides:
- `run_task(task, timeout)` - Register + execute + save result
- `run_parallel(*tasks, timeout)` - Execute multiple tasks concurrently
- `retry_until(task_factory, condition, max_retries)` - Retry until condition met
- `get_tasks(label)` - Query tasks by label
- `register_task(task, timeout)` - Register task with UUID

### TaskBase

Abstract base class for all tasks:
- Synchronous `run()` method (required)
- `label` for grouping (not unique)
- State: `_state`, `_result`, `_error`, `_uuid`, `_flow`
- Cannot spawn tasks

### FlowStorage

Async storage layer:
- `create_flow(uuid, name, description, context)` - Create flow directory
- `register_task(task_id, label, flow_uuid, timeout)` - Register task in meta.json
- `update_task_state(flow_uuid, task_id, state, result, error, messages)` - Update task state
- `get_tasks(label, flow_uuid)` - Get tasks by label
- `recover_orphaned_tasks()` - Recover crashed tasks

### AtomicJsonWriter

Atomic JSON file writes:
- Write to tempfile
- fsync to disk
- os.replace to target
- fsync directory (ensure rename persisted)

### FlowIndex

JSONL-based global index:
- Append-only for new flows
- Line-by-line reading for lazy loading
- Supports limit/offset pagination
- Atomic rewrites for updates

## PLUGIN STRUCTURE

Flow plugins must have:

```
plugin-root/
├── pyproject.toml       # name, version, author metadata
├── config.yaml          # Flow-specific configuration
├── config.typehint.yaml # (Optional) Typehint definition for validation
└── src/
    ├── __init__.py
    └── main.py          # Must export: FlowClass = YourFlowClass
```

## FLOW LOADING PROCESS

1. Load `pyproject.toml` for metadata (name, version, author)
2. Load `config.yaml` and validate against Pydantic models
3. (Optional) Load `config.typehint.yaml` and validate against global config
4. Import `src/main.py` as unique package (`{name}_{version}.main`)
5. Extract `FlowClass` variable from module
6. Instantiate flow: `FlowClass(flow_config, global_config)`
7. Register in FlowRegistry

## TESTING

Tests in `tests/flow/`:
- `test_base.py` - FlowBase ABC tests
- `test_base_extensions.py` - Extended FlowBase tests (retry_until, run_parallel)
- `test_tasks.py` - Task system tests
- `test_storage.py` - FlowStorage, AtomicJsonWriter tests
- `test_loader.py` - Plugin loading tests
- `test_registry.py` - FlowRegistry singleton tests
- `test_models.py` - Flow model tests
- `test_config_validation.py` - Flow config validation tests
- `test_integration.py` - End-to-end flow tests
