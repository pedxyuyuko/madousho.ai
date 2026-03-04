# src/madousho/commands/ KNOWLEDGE BASE

**Generated:** 2026-03-03
**Commit:** 3b8ad40
**Branch:** master

## OVERVIEW

CLI command implementations for the madousho CLI. Each command is a function registered with the Typer app.

## STRUCTURE

```
commands/
├── __init__.py         # Exports command functions
├── run.py              # `madousho run` - Start service (74 lines)
└── validate.py         # `madousho validate` - Validate config (23 lines)
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Run command | `run.py:8-25` | `run_cmd()` - loads config, starts service |
| Validate command | `validate.py:8-23` | `validate_cmd()` - validates config file |
| Command exports | `__init__.py` | Imports for cli.py registration |
| Command registration | `cli.py:121-122` | `app.command()` calls |

## CONVENTIONS

- **Function naming**: `{action}_cmd` suffix (e.g., `run_cmd`, `validate_cmd`)
- **Context parameter**: First param is always `ctx: typer.Context`
- **Config access**: Via `ctx.obj["config_path"]` and `ctx.obj["verbose"]`
- **Error handling**: Use `typer.Exit(code=1)` for failures
- **Logging**: Use logger from `madousho.logger` (not print)

## ANTI-PATTERNS (THIS MODULE)

- DO NOT access config directly - always use `ctx.obj`
- DO NOT print to stdout - use logger from `madousho.logger`
- DO NOT catch exceptions silently - let Typer handle or exit with code
- DO NOT add commands without registering in `cli.py`
- DO NOT bypass config loader - use `load_config()` from `config.loader`

## NOTES

- **Registration**: Commands registered in `cli.py:121-122` via `app.command()`
- **Config loading**: Each command calls `load_config()` from `config.loader`
- **Logger**: Import from `madousho.logger` - configured in CLI callback
- **Context structure**: `ctx.obj` contains `config_path`, `verbose`, `config`
