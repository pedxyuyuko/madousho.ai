# Logging - Loguru Configuration

## OVERVIEW

Loguru-based logging with console + file sinks. One-time initialization via `configure_logging()`. Chinese comments in implementation.

## STRUCTURE

```
logging/
├── __init__.py         # Exports: get_logger, configure_logging
└── config.py           # Sink configuration, rotation, formatting
```

## WHERE TO LOOK

| Component | File | Purpose |
|-----------|------|---------|
| Setup | `config.py` | `configure_logging()` - one-time sink initialization |
| Logger access | `__init__.py` | `get_logger(name)` - returns bound/unbound logger |
| Formats | `config.py` | `STANDARD_FORMAT` (colored), `JSON_FORMAT` (structured) |

## CONVENTIONS

- **One-time init**: Call `configure_logging()` once at app startup, never again
- **Level resolution**: Param → `LOGURU_LEVEL` env var → default `"INFO"`
- **Color auto-detect**: Disabled when `is_json=True` or `not isatty()`
- **File sink**: `logs/madousho.log`, 100MB rotation, 7-day retention, zip compression
- **Thread-safe**: `enqueue=True` for multiprocess safety
- **Logger binding**: `get_logger("auth")` returns logger with `name=auth` bound

## FORMATS

| Format | Use Case | Color |
|--------|----------|-------|
| `STANDARD_FORMAT` | Console output | Yes (if TTY) |
| `JSON_FORMAT` | Structured logging | No |

## ANTI-PATTERNS

- **DO NOT** call `configure_logging()` multiple times - sinks accumulate
- **DO NOT** use `logger` before `configure_logging()` - default handler active
- **DO NOT** import `logger` directly in modules - use `get_logger()` for named loggers

## TESTING

Exclude from coverage (see `pyproject.toml`):
```toml
omit = ["src/madousho/logging/*"]
```

## RELATED

- Commands: `src/madousho/commands/` for startup logging init
- Config: `src/madousho/config/` for `LOGURU_LEVEL` env var
