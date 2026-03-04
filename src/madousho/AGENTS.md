# src/madousho/ KNOWLEDGE BASE

**Generated:** 2026-03-03
**Commit:** 3b8ad40
**Branch:** master

## OVERVIEW

Main application package containing CLI entry point, command implementations, configuration system, flow engine, and logging.

## STRUCTURE

```
src/madousho/
├── cli.py              # Typer CLI app, 4-layer config search
├── logger.py           # Loguru-based logging
├── __init__.py         # Package marker (version hardcoded - bug)
├── _version.py         # setuptools_scm generated version
├── commands/           # CLI command implementations
│   ├── run.py          # `madousho run` command
│   └── validate.py     # `madousho validate` command
├── config/             # Configuration system
│   ├── models.py       # Pydantic v2 config models
│   ├── loader.py       # YAML loader with env overrides
│   └── typehint_models.py  # Type-hinted model variants
└── flow/               # Flow engine
    ├── base.py         # FlowBase, step primitives
    ├── loader.py       # FlowLoader (328 lines)
    ├── models.py       # Flow data models
    └── registry.py     # FlowRegistry
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| CLI registration | `cli.py:13` | `app = typer.Typer()` |
| Config search logic | `cli.py:16-79` | `find_config_file()` - 4 layers |
| Command handlers | `commands/*.py` | `run_cmd`, `validate_cmd` |
| Config models | `config/models.py` | `Config`, `APIConfig`, `ProviderConfig` |
| Config loading | `config/loader.py` | `load_config()` with env overrides |
| Flow engine | `flow/` | See `flow/AGENTS.md` |
| Logger setup | `logger.py` | Loguru configuration |

## CONVENTIONS

- **Command naming**: `{action}_cmd` (e.g., `run_cmd`, `validate_cmd`)
- **Context passing**: Typer `ctx: typer.Context` with `ctx.obj` for shared state
- **Config models**: All use `ConfigDict(extra="forbid")` for strict validation
- **Type hints**: Full typing required (Python 3.14+ target)
- **Pydantic v2**: Use `model_validate()`, `model_dump()` (NOT v1 methods)

## ANTI-PATTERNS (THIS PACKAGE)

- DO NOT import commands directly in cli.py - use `app.command()` registration
- DO NOT use Pydantic v1 methods (`.dict()`, `.parse_obj()`)
- DO NOT bypass config loader - always use `load_config()`
- DO NOT modify `ctx.obj` structure without updating all commands
- DO NOT use `python -m madousho` - missing `__main__.py`
- DO NOT skip type hints - project uses full typing

## UNIQUE STYLES

- **4-layer config search**: CLI → env → cwd → ~/.config (intentional order)
- **Hyphen normalization**: `normalize_keys()` converts YAML hyphens to underscores
- **Env var pattern**: `MADOUSHO_<section>_<key>` → nested dict overrides
- **Version management**: setuptools_scm from git tags (hardcoded version is a bug)

## NOTES

- **Entry point registration**: `app.command("run")(run_cmd)` in cli.py:121
- **Config path resolution**: Happens in callback before any command executes
- **Logger setup**: Loguru-based, configured with CLI flags (--verbose, --json)
- **Version bug**: `__init__.py` has hardcoded "0.1.0" but should import from `_version.py`
- **Python version bug**: `pyproject.toml` requires `>=3.14` (should be `>=3.10`)
