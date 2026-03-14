# Madousho.ai - Project Knowledge Base

**Generated:** 2026-03-14
**Stack:** Python 3.10+ | SQLAlchemy 2.0 | Pydantic v2 | Typer CLI | Alembic | Loguru

## OVERVIEW

Madousho.ai (魔导书) - Systematic AI Agent Framework. Python package with Typer CLI, SQLAlchemy ORM, Pydantic configuration, and structured logging via Loguru.

## STRUCTURE

```
./
├── src/madousho/        # Main package (CLI, commands, models, database, config, logging)
├── tests/               # pytest test suite (90% coverage required)
├── config/              # YAML configuration files (app-level, not source)
├── alembic/             # Database migrations
├── pyproject.toml       # Build config, dependencies, entry points
└── pytest.ini           # Test configuration
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| CLI entry point | `src/madousho/cli.py` | Typer app, `madousho` command |
| Commands | `src/madousho/commands/` | `serve.py`, `verify.py` |
| Database models | `src/madousho/models/` | Flow, Task (UUID primary keys) |
| DB connection | `src/madousho/database/` | Singleton `Database` class |
| Config loading | `src/madousho/config/` | YAML loader + Pydantic models |
| Logging | `src/madousho/logging/` | Loguru configuration |
| Tests | `tests/` | pytest, 90% coverage enforced |
| Migrations | `alembic/versions/` | Alembic migration scripts |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `app` | Typer | `cli.py:12` | Main CLI application |
| `Database` | Singleton | `database/connection.py:15` | DB connection manager |
| `Config` | Pydantic | `config/models.py:49` | Root config model |
| `Flow`, `Task` | SQLAlchemy | `models/` | ORM models |
| `configure_logging` | Function | `logging/config.py:23` | Loguru setup |
| `get_config` | Function | `config/loader.py:101` | Config singleton access |

## CONVENTIONS

- **UUID primary keys**: `String(36)` with `uuid.uuid4()` default (not autoincrement IDs)
- **Singleton pattern**: `Database` class uses `__new__` + `_instance` for single connection
- **Config caching**: `_cached_config` global, lazy initialization via `get_config()`
- **Timestamps**: `datetime.now(timezone.utc)` for all `created_at` fields
- **JSON columns**: Store structured data (task lists, messages, results) as `JSON` type
- **SQLite optimization**: WAL mode, connection pooling, PRAGMA settings via event listeners
- **Loguru sinks**: Console + file (100MB rotation, 7-day retention, zip compression)

## ANTI-PATTERNS (THIS PROJECT)

- **DO NOT** use autoincrement IDs - UUID required for all models
- **DO NOT** call `Database()` directly - use `Database.get_instance()`
- **DO NOT** access config dict directly - use `get_config()` or `config` singleton
- **DO NOT** initialize logging multiple times - `configure_logging()` is one-time setup
- **DO NOT** commit/rollback manually - use `db.session()` context manager
- **DO NOT** hardcode config paths - use `get_config_file()` with env var support

## UNIQUE STYLES

- **Chinese comments**: Core infrastructure files use Chinese docstrings/comments
- **Dual config**: `.yaml` and `.yml` both supported, `.yaml` tried first
- **Strict coverage**: 90% minimum enforced in CI (`--cov-fail-under=90`)
- **Version from git**: `setuptools_scm` auto-generates version from tags
- **Environment override**: `MADOUSHO_CONFIG_PATH` env var sets config root directory

## COMMANDS

```bash
# Development
uv sync                    # Install dependencies (project uses uv)
pytest                     # Run tests (90% coverage required)
pytest --cov               # With coverage report

# CLI usage
madousho --help            # Show CLI help
madousho serve             # Start API server
madousho verify            # Validate configuration
madousho version           # Show version

# Database migrations
alembic revision --autogenerate -m "msg"   # Create migration
alembic upgrade head                       # Apply migrations

# Build & publish
python -m build            # Build distribution packages
```

## NOTES

- **Python 3.10+** required (type hints with `|` union syntax)
- **Logs directory**: `./logs/` - auto-created by logging config
- **Default database**: `sqlite:///./madousho.db` (configurable via YAML)
- **CI/CD**: GitHub Actions - test on push to master, publish on release
- **Package name**: `madousho-ai` on PyPI, import as `madousho`
