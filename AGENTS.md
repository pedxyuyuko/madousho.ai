# PROJECT KNOWLEDGE BASE

**Generated:** 2026-03-06
**Commit:** $(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
**Branch:** $(git branch --show-current 2>/dev/null || echo "unknown")

## OVERVIEW

Madousho.ai (魔导书) - Systematic AI Agent Framework with fixed flow control + AI-executed steps. Python CLI application using Typer, Pydantic v2 for config validation, YAML configuration, and task-based flow execution with persistence.

## STRUCTURE

```
madousho_ai/
├── src/madousho/        # Main package (CLI, commands, config, flow engine)
│   ├── cli.py           # Typer CLI entry point
│   ├── logger.py        # Loguru-based logging
│   ├── _version.py      # Auto-generated version (setuptools_scm)
│   ├── commands/        # CLI commands (serve, validate)
│   ├── config/          # Configuration system (Pydantic v2 models, YAML loader)
│   ├── flow/            # Flow engine (FlowBase, TaskBase, storage, loader, registry)
│   └── api/             # REST API (FastAPI routes, middleware)
├── tests/               # Pytest test suite (90% coverage required)
├── config/              # Default configuration files
├── examples/            # Example flows and plugin templates
├── plugins/             # Reserved for Git-based plugin system
├── data/                # Flow persistence (task states, flow metadata)
├── .github/workflows/   # CI/CD (TestPyPI on master, PyPI on release)
└── pyproject.toml       # Build system, metadata, entry point
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| CLI entry point | `src/madousho/cli.py` | Typer app, `madousho` command, 4-layer config search |
| Command implementations | `src/madousho/commands/` | serve.py, validate.py |
| Flow engine core | `src/madousho/flow/` | base.py (FlowBase), tasks/base.py (TaskBase), storage.py (AtomicJsonWriter) |
| Flow plugin loader | `src/madousho/flow/loader.py` | Plugin import, config validation, typehint checking |
| Flow registry | `src/madousho/flow/registry.py` | Thread-safe singleton registry |
| Configuration models | `src/madousho/config/models.py` | Pydantic v2 models (Config, APIConfig, ProviderConfig) |
| Config loader | `src/madousho/config/loader.py` | YAML + env overrides, hyphen-to-underscore normalization |
| Typehint validation | `src/madousho/config/typehint_models.py` | TypeHintDefinition, TypeHintValidator for flow config validation |
| Tests | `tests/` | pytest, 90% coverage required |
| CI/CD | `.github/workflows/` | TestPyPI on master push, PyPI on release published |
| Example flows | `examples/example_flows/` | Plugin template with SearchTask, SummarizeTask, DataFetchTask |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `app` | Typer | cli.py:12 | Main CLI application |
| `find_config_dir` | fn | cli.py:15 | 3-layer config search (CLI param → cwd → ~/.config) |
| `validate_cmd` | fn | commands/validate.py:9 | Validate config command |
| `serve_cmd` | fn | commands/serve.py | Start API server command |
| `Config` | class | config/models.py:33 | Main config model (Pydantic v2) |
| `ConfigManager` | class | config/loader.py:50 | Singleton config manager |
| `load_config` | fn | config/loader.py:132 | Load + validate config |
| `TypeHintValidator` | class | config/typehint_models.py:45 | Flow config typehint validation |
| `FlowBase` | class | flow/base.py:11 | Abstract base class for all flows |
| `TaskBase` | class | flow/tasks/base.py:10 | Abstract base class for all tasks |
| `FlowStorage` | class | flow/storage.py:181 | Task persistence with AtomicJsonWriter |
| `FlowLoader` | fn | flow/loader.py:285 | Plugin loading (load_plugin) |
| `FlowRegistry` | class | flow/registry.py:7 | Thread-safe flow registry singleton |
| `get_flow_class` | fn | flow/base.py:323 | Extract FlowClass from plugin module |
| `retry_until` | method | flow/base.py:242 | Retry task until condition met |
| `run_parallel` | method | flow/base.py:189 | Execute tasks in parallel |

## CONVENTIONS

- **Python 3.10+** (pyproject.toml specifies >=3.10)
- **Pydantic v2** with `model_validate()`, `model_dump()` (NOT v1 `.dict()`, `.parse_obj()`)
- **Extra fields forbidden** in all Pydantic models (`extra="forbid"`)
- **Hyphen-to-underscore** normalization in config loader (YAML keys auto-converted)
- **Singleton patterns** for ConfigManager and FlowRegistry (thread-safe with double-checked locking)
- **Full type hints required** (no skipping type annotations)
- **Task-based execution**: Flows execute via discrete Task instances with lifecycle tracking
- **Flow persistence**: Task states persisted to JSON with atomic writes (tempfile + fsync + os.replace)
- **Async persistence layer**: All storage operations are async (AtomicJsonWriter, FlowIndex)
- **Logger binding**: Use `logger.bind(plugin="...")` for plugin context in logs

## ANTI-PATTERNS (THIS PROJECT)

- DO NOT use Pydantic v1 syntax (`.dict()`, `.parse_obj()`) - use `model_dump()`, `model_validate()`
- DO NOT add extra fields to config models (rejected by `extra="forbid"` validation)
- DO NOT modify config search order (3-layer strategy is intentional)
- DO NOT skip type hints (project uses full typing)
- DO NOT use `python -m madousho` (missing `__main__.py` - use `madousho` command directly)
- DO NOT create tasks without inheriting `TaskBase`
- DO NOT make `run()` method async (must be synchronous)
- DO NOT spawn tasks from within other tasks (tasks cannot spawn)
- DO NOT bypass `register_task()` - UUID required for persistence
- DO NOT modify task state directly (use FlowBase methods: `run_task()`, `run_parallel()`)
- DO NOT print to stdout - use logger from `madousho.logger`
- DO NOT catch exceptions silently - let Typer handle or exit with code
- DO NOT skip `FlowClass = YourFlowClass` export in plugin main.py
- DO NOT create flow plugins without `config.yaml` (required for validation)

## UNIQUE STYLES

- **3-layer config search**: CLI param → cwd (./config/ or ./madousho.yaml) → ~/.config/madousho/
- **Config normalization**: YAML hyphens auto-converted to underscores recursively
- **Env var overrides**: Via pydantic-settings (not implemented in loader yet)
- **Task lifecycle**: `pending` → `running` → `completed` | `failed`
- **Atomic persistence**: AtomicJsonWriter uses tempfile + fsync + os.replace for crash safety
- **JSONL indexing**: Global flow index (`data/flow/flows.jsonl`) for lazy loading
- **Plugin isolation**: Each plugin loaded as unique Python package (`{name}_{version}.main`)
- **Typehint validation**: Optional `config.typehint.yaml` for flow config validation against global config
- **Retry pattern**: `retry_until(task_factory, condition, max_retries)` for conditional retries
- **Thread-safe registry**: Double-checked locking in FlowRegistry singleton

## COMMANDS

```bash
# Development install
pip install -e ".[dev]"

# Run tests (90% coverage required)
python -m pytest --cov --cov-fail-under=90
python -m pytest tests/flow/        # Run specific test directory
python -m pytest -m asyncio         # Run only async tests

# Build distribution
python -m build

# CLI usage
madousho --version
madousho run --config ./config/madousho.yaml
madousho validate
madousho serve
```

## NOTES

- **Entry point**: `madousho = "madousho.cli:app"` in pyproject.toml
- **Test coverage**: Enforced at 90% via `--cov-fail-under=90`
- **Coverage exclusions**: cli.py, logger.py, commands/*, tests/*, temp directories
- **CI/CD**: TestPyPI on master push (unconventional), PyPI on release published
- **Version management**: setuptools_scm from git tags (writes to `src/madousho/_version.py`)
- **Config files**: `config/madousho.yaml` (default), `config/madousho.example.yaml` (template), `config/madousho.mock.yml` (CI testing)
- **Flow storage**: `data/flow/{uuid}/` with meta.json + {task_uuid}.json files
- **Plugin structure**: Plugins must have `pyproject.toml`, `config.yaml`, `src/main.py` with `FlowClass` export
- **Thread safety**: FlowRegistry uses threading.Lock for concurrent access
- **Async compatibility**: Storage layer is async, but task `run()` methods are synchronous (run in executor)
- **Known issues**:
  - Python version in pyproject.toml was >=3.14 (should be >=3.10) - FIXED
  - Version hardcoded in `__init__.py` but should import from `_version.py`
  - Missing `__main__.py` prevents `python -m madousho` execution (by design - use CLI command)

## SUBDIRECTORY DOCUMENTATION

- `src/madousho/flow/AGENTS.md` - Flow engine architecture, task lifecycle, persistence patterns
- `src/madousho/config/AGENTS.md` - Configuration system, Pydantic models, typehint validation
- `tests/AGENTS.md` - Test suite architecture, pytest patterns, coverage configuration, test categories
