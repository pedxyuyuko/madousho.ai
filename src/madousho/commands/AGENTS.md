# Commands - CLI Subcommands

## OVERVIEW

Typer-based CLI subcommands. Each file defines a `app = typer.Typer()` instance registered in `cli.py`.

## STRUCTURE

```
commands/
├── __init__.py         # Empty (commands imported directly in cli.py)
├── serve.py            # API server startup command
└── verify.py           # Configuration validation command
```

## WHERE TO LOOK

| Command | File | Function | Purpose |
|---------|------|----------|---------|
| `madousho serve` | `serve.py` | `serve(ctx)` | Load config, init logging, start API server |
| `madousho verify` | `verify.py` | `verify(ctx)` | Validate YAML config against Pydantic models |

## CONVENTIONS

- **Typer app pattern**: Each command file has `app = typer.Typer()` + `@app.command()` decorated function
- **Context usage**: Access global options via `ctx.obj` (verbose, json_output, config_path)
- **Logging**: Call `configure_logging()` at command start, then use `logger` from loguru
- **Exit codes**: Use `typer.Exit(code=1)` for errors, implicit `0` for success
- **Helper functions**: Prefix internal helpers with `_` (e.g., `_verify_config`)

## COMMAND REGISTRATION

In `cli.py`:
```python
from madousho.commands import serve, verify
app.add_typer(serve.app)
app.add_typer(verify.app)
```

## ANTI-PATTERNS

- **DO NOT** create nested Typer apps - each command is flat, registered at top level
- **DO NOT** access `ctx.obj` without `.get()` with defaults - may be uninitialized
- **DO NOT** skip logging initialization - commands should configure logging independently

## TESTING

Commands tested via `typer.testing.CliRunner`:
```python
from typer.testing import CliRunner
runner = CliRunner()
result = runner.invoke(app, ["--option", "value"])
```

See: `tests/test_serve_command.py`, `tests/test_verify_command.py`
