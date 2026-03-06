# src/madousho/ KNOWLEDGE BASE

**Generated:** 2026-03-06
**Commit:** 3b8ad40
**Branch:** master

## OVERVIEW

Main application package containing CLI entry point, REST API, command implementations, configuration system, flow engine, and logging.

## STRUCTURE

```
src/madousho/
├── cli.py              # Typer CLI app, 4-layer config search (126 lines)
├── logger.py           # Loguru-based logging (26 lines)
├── __init__.py         # Version import from _version.py (4 lines)
├── _version.py         # setuptools_scm generated version
├── commands/           # CLI command implementations
│   ├── __init__.py     # Exports run_cmd, validate_cmd
│   ├── run.py          # `madousho run` command (74 lines)
│   └── validate.py     # `madousho validate` command (23 lines)
├── config/             # Configuration system
│   ├── __init__.py     # Exports models + load_config
│   ├── models.py       # Pydantic v2 config models (41 lines)
│   ├── loader.py       # YAML loader with env overrides (145 lines)
│   └── typehint_models.py  # Type-hinted model variants + validator
├── flow/               # Flow engine
│   ├── __init__.py     # Exports FlowBase
│   ├── base.py         # FlowBase class, task execution (361 lines)
│   ├── loader.py       # FlowLoader plugin loading (332 lines)
│   ├── models.py       # Flow data models (66 lines)
│   ├── registry.py     # FlowRegistry singleton (93 lines)
│   ├── storage.py      # FlowStorage task persistence (454 lines)
│   └── tasks/          # Task system
│       ├── __init__.py # Package marker
│       └── base.py     # TaskBase abstract class (96 lines)
└── api/                # FastAPI REST API
    ├── __init__.py     # Re-exports FastAPI class
    ├── app.py          # FastAPI app factory (45 lines)
    ├── middleware/
    │   ├── __init__.py
    │   └── auth.py     # TokenAuthMiddleware
    └── routes/
        ├── __init__.py
        └── health.py   # Health check endpoint
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| CLI registration | `cli.py:13` | `app = typer.Typer()` |
| Config search logic | `cli.py:16-79` | `find_config_file()` - 4 layers |
| Command handlers | `commands/*.py` | `run_cmd`, `validate_cmd` |
| Config models | `config/models.py` | `Config`, `APIConfig`, `ProviderConfig` |
| Config loading | `config/loader.py` | `load_config()` with env overrides |
| Typehint validation | `config/typehint_models.py` | `TypeHintValidator` for config fields |
| Flow engine | `flow/` | See `flow/AGENTS.md` |
| Logger setup | `logger.py` | Loguru configuration |
| API factory | `api/app.py` | `create_app()` - FastAPI instance |
| API middleware | `api/middleware/auth.py` | TokenAuthMiddleware |
| API routes | `api/routes/health.py` | Health check endpoint |
| Flow storage | `flow/storage.py` | AtomicJsonWriter, FlowIndex, FlowStorage |

## CONVENTIONS

- **Command naming**: `{action}_cmd` (e.g., `run_cmd`, `validate_cmd`)
- **Context passing**: Typer `ctx: typer.Context` with `ctx.obj` for shared state
- **Config models**: All use `ConfigDict(extra="forbid")` for strict validation
- **Type hints**: Full typing required (Python 3.10+)
- **Pydantic v2**: Use `model_validate()`, `model_dump()` (NOT v1 methods)
- **Logger usage**: Use `logger.debug()` for Flow logs (NOT print)

## ANTI-PATTERNS (THIS PACKAGE)

- DO NOT import commands directly in cli.py - use `app.command()` registration
- DO NOT use Pydantic v1 methods (`.dict()`, `.parse_obj()`)
- DO NOT bypass config loader - always use `load_config()`
- DO NOT modify `ctx.obj` structure without updating all commands
- DO NOT use `python -m madousho` - missing `__main__.py`
- DO NOT skip type hints - project uses full typing
- DO NOT print to stdout - use logger from `madousho.logger`
- DO NOT catch exceptions silently - let Typer handle or exit with code
- DO NOT access config directly in commands - use `ctx.obj`

## UNIQUE STYLES

- **4-layer config search**: CLI → env → cwd → ~/.config (intentional order)
- **Hyphen normalization**: `normalize_keys()` converts YAML hyphens to underscores
- **Env var pattern**: `MADOUSHO_<section>_<key>` → nested dict overrides
- **Version management**: setuptools_scm from git tags (writes to `_version.py`)

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `app` | Typer | cli.py:13 | Main CLI application |
| `find_config_file` | fn | cli.py:16 | 4-layer config search |
| `run_cmd` | fn | commands/run.py:8 | Run flow command |
| `validate_cmd` | fn | commands/validate.py:8 | Validate config command |
| `create_app` | fn | api/app.py:16 | FastAPI factory |
| `Config` | class | config/models.py:33 | Main config model |
| `load_config` | fn | config/loader.py:116 | Load + validate config |
| `TypeHintValidator` | class | config/typehint_models.py | Config field validation |
| `FlowBase` | class | flow/base.py:11 | Flow execution base class |
| `TaskBase` | class | flow/tasks/base.py:10 | Task abstract base class |
| `FlowStorage` | class | flow/storage.py:181 | Task persistence layer |
| `FlowLoader` | fn | flow/loader.py:257 | Plugin loading |
| `FlowRegistry` | class | flow/registry.py:7 | Global flow singleton |
| `AtomicJsonWriter` | class | flow/storage.py:14 | Atomic JSON writes |

## NOTES

- **Entry point**: `madousho = "madousho.cli:app"` in pyproject.toml
- **Version import**: `__init__.py` imports from `_version.py` (setuptools_scm)
- **Missing `__main__.py`**: Prevents `python -m madousho` execution
- **API under-exported**: `api/__init__.py` only exports `FastAPI` class, not `create_app`
- **Config not packaged**: `config/*.yaml` in repo root, not installed with package
- **No linting**: No Ruff/Flake8/Black/mypy configured (CI only runs tests + build)
