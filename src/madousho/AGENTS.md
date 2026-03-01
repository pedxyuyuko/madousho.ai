# src/madousho/ KNOWLEDGE BASE

## OVERVIEW

Main application package containing CLI entry point, command implementations, configuration system, and logging.

## STRUCTURE

```
src/madousho/
├── cli.py              # Typer CLI app, 4-layer config search
├── logger.py           # Loguru-based logging
├── __init__.py         # Package marker
├── commands/           # CLI command implementations
│   ├── run.py         # `madousho run` command
│   └── validate.py    # `madousho validate` command
└── config/             # Configuration system
    ├── models.py      # Pydantic config models
    └── loader.py      # YAML loader with env overrides
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| CLI registration | `cli.py:13` | `app = typer.Typer()` |
| Config search logic | `cli.py:16-79` | `find_config_file()` function |
| Command handlers | `commands/*.py` | `run_cmd`, `validate_cmd` |
| Config models | `config/models.py` | `Config`, `APIConfig`, `ProviderConfig` |
| Config loading | `config/loader.py` | `load_config()` with env overrides |

## CONVENTIONS

- **Command naming**: `{action}_cmd` (e.g., `run_cmd`, `validate_cmd`)
- **Context passing**: Typer `ctx: typer.Context` with `ctx.obj` for shared state
- **Config models**: All use `ConfigDict(extra="forbid")` for strict validation
- **Type hints**: Full typing required (Python 3.14+ target)

## ANTI-PATTERNS (THIS PACKAGE)

- DO NOT import commands directly in cli.py - use `app.command()` registration
- DO NOT use Pydantic v1 methods (`.dict()`, `.parse_obj()`)
- DO NOT bypass config loader - always use `load_config()`
- DO NOT modify `ctx.obj` structure without updating all commands

## UNIQUE STYLES

- **4-layer config search**: CLI → env → cwd → ~/.config (intentional order)
- **Hyphen normalization**: `normalize_keys()` converts YAML hyphens to underscores
- **Env var pattern**: `MADOUSHO_<section>_<key>` → nested dict overrides

## NOTES

- **Entry point registration**: `app.command("run")(run_cmd)` in cli.py:121
- **Config path resolution**: Happens in callback before any command executes
- **Logger setup**: Loguru-based, configured with CLI flags (--verbose, --json)
