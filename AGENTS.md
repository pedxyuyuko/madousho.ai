# PROJECT KNOWLEDGE BASE

**Generated:** 2026-03-06
**Commit:** 3b8ad40
**Branch:** master

## OVERVIEW

Madousho.ai (魔导书) - Systematic AI Agent Framework with fixed flow control + AI-executed steps. Python CLI application using Typer, Pydantic v2, FastAPI, YAML configuration, and task-based flow execution with atomic JSON persistence.

## STRUCTURE

```
madousho_ai/
├── src/madousho/        # Main package (CLI, API, config, flow engine)
├── tests/               # Pytest suite (90% coverage required)
├── config/              # Default YAML configs (not packaged)
├── examples/            # Example flows with task patterns
├── plugins/             # Reserved for Git-based plugin system
├── data/                # Flow persistence (task states, metadata)
├── .github/workflows/   # CI/CD (TestPyPI on master, PyPI on release)
└── pyproject.toml       # Build system, metadata, entry points
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| CLI entry point | `src/madousho/cli.py` | Typer app, 4-layer config search |
| REST API | `src/madousho/api/` | FastAPI, auth middleware, health check |
| Flow engine | `src/madousho/flow/` | FlowBase, TaskBase, storage, loader |
| Config models | `src/madousho/config/models.py` | Pydantic v2, extra="forbid" |
| Config loader | `src/madousho/config/loader.py` | YAML + env overrides (MADOUSHO_*) |
| Typehint validator | `src/madousho/config/typehint_models.py` | Config field validation |
| Plugin loader | `src/madousho/flow/loader.py` | Dynamic flow plugin loading |
| Task persistence | `src/madousho/flow/storage.py` | AtomicJsonWriter, JSONL index |
| Tests | `tests/` | Mirrors src/ structure, 90% coverage |
| CI/CD | `.github/workflows/` | TestPyPI (master), PyPI (release) |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `app` | Typer | cli.py:13 | Main CLI application |
| `find_config_file` | fn | cli.py:16 | 4-layer config search |
| `create_app` | fn | api/app.py:16 | FastAPI factory |
| `FlowBase` | class | flow/base.py:11 | Flow execution base class |
| `TaskBase` | class | flow/tasks/base.py:10 | Task abstract base class |
| `FlowStorage` | class | flow/storage.py:181 | Task persistence layer |
| `FlowLoader` | fn | flow/loader.py:257 | Plugin loading (load_plugin) |
| `FlowRegistry` | class | flow/registry.py:7 | Global flow singleton |
| `Config` | class | config/models.py:33 | Main config model |
| `load_config` | fn | config/loader.py:116 | Load + validate config |
| `TypeHintValidator` | class | config/typehint_models.py | Config field validation |
| `AtomicJsonWriter` | class | flow/storage.py:14 | Atomic JSON writes |
| `retry_until` | method | flow/base.py:242 | Retry task with condition |
| `run_parallel` | method | flow/base.py:189 | Parallel task execution |

## CONVENTIONS

- **Python 3.10+** (pyproject.toml requires >=3.10)
- **Pydantic v2** with `model_validate()`, `model_dump()` (NOT v1 methods)
- **Extra fields forbidden** in config models (`extra="forbid"`)
- **Hyphen-to-underscore** normalization in config loader
- **Environment overrides** via `MADOUSHO_*` prefix
- **Full type hints required** (no skipping type annotations)
- **Task-based execution**: Flows execute via discrete Task instances
- **Flow persistence**: Task states persisted with atomic writes
- **Logger usage**: Use `logger.debug()` for Flow logs (NOT print)

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
- DO NOT access config directly in commands - use `ctx.obj`

## UNIQUE STYLES

- **3-layer config search**: CLI param → cwd (./config/ or ./madousho.yaml) → ~/.config/madousho/
- **Config normalization**: YAML hyphens auto-converted to underscores recursively
- **Env var overrides**: Via pydantic-settings (not implemented in loader yet)
- **Task lifecycle**: `pending` → `running` → `completed` | `failed`
- **Atomic persistence**: AtomicJsonWriter uses tempfile + fsync + os.replace
- **JSONL indexing**: Global flow index for lazy loading
- **Orphan recovery**: `recover_orphaned_tasks()` handles crashed processes

## COMMANDS

```bash
# Development install
pip install -e ".[dev]"

# Run tests (90% coverage required)
python -m pytest

# Run with coverage report
python -m pytest --cov=madousho --cov-report=term-missing

# Build distribution
python -m build

# CLI usage
madousho --version
madousho run --config ./config/madousho.yaml
madousho run --file examples/example_flows
madousho validate
madousho serve
```

## NOTES

- **Entry point**: `madousho = "madousho.cli:app"` in pyproject.toml
- **Missing `__main__.py`**: Prevents `python -m madousho` execution
- **Test coverage**: pytest configured with `--cov-fail-under=90`
- **CI/CD**: TestPyPI on master push, PyPI on release published
- **Config files**: `config/madousho.yaml` (default), `config/madousho.example.yaml` (template)
- **Version management**: setuptools_scm from git tags, writes to `src/madousho/_version.py`
- **Flow storage**: `data/flow/{uuid}/meta.json` + `{task_uuid}.json`
- **Coverage excludes**: cli.py, logger.py, commands/* (hard to test)
- **No linting configured**: No Ruff/Flake8/Black/mypy (CI only runs tests + build)
- **API module under-exported**: `api/__init__.py` only exports FastAPI class, not `create_app`
