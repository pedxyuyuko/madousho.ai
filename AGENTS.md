# PROJECT KNOWLEDGE BASE

**Generated:** 2026-03-13
**Repository:** github.com/pedxyuyuko/madousho-ai
**Package:** madousho-ai (魔导书 - Systematic AI Agent Framework)

## OVERVIEW

Python-based systematic AI agent framework with database-backed flows/tasks, Typer CLI, SQLAlchemy + Alembic migrations, YAML configuration.

## STRUCTURE

```
.
├── src/madousho/          # Main package (CLI, commands, models, database, config, logging)
├── tests/                 # Pytest test suite (90% coverage required)
├── alembic/               # Database migrations
├── config/                # YAML configuration files
├── .github/workflows/     # CI/CD: PyPI publish on release
└── pyproject.toml         # Build config, dependencies, pytest/coverage settings
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| CLI entry point | `src/madousho/cli.py` | Typer app, `madousho` command |
| Commands | `src/madousho/commands/` | `serve.py`, `verify.py` |
| Database models | `src/madousho/models/` | SQLAlchemy, `flow.py`, `task.py` |
| DB connection | `src/madousho/database/` | SQLite with WAL mode |
| Config loading | `src/madousho/config/loader.py` | YAML, pydantic-settings |
| Logging setup | `src/madousho/logging/` | Loguru, `get_logger()` |
| Migrations | `alembic/versions/` | Auto-generated versions |
| Tests | `tests/` | `test_*.py`, pytest-asyncio |

## CONVENTIONS

- **Python 3.10+** required
- **Type hints** mandatory (coverage excludes TYPE_CHECKING blocks)
- **Async tests** use `pytest-asyncio` with `asyncio_mode = auto`
- **Version auto-gen** via setuptools_scm from git tags
- **YAML config** with example/mock variants

## ANTI-PATTERNS (THIS PROJECT)

- DO NOT modify `src/madousho/_version.py` (auto-generated)
- DO NOT skip coverage requirements (90% minimum enforced)
- DO NOT use nested CLI commands (flat structure only)
- Avoid modifying migrations in `alembic/versions/` after merge

## UNIQUE STYLES

- **Flat CLI**: All commands registered at top-level (no nesting)
- **Config via env**: `MADOUSHO_CONFIG_PATH` sets config root
- **Japanese comments**: Mixed with English (e.g., logging exports)
- **SQLite WAL**: Database configured with write-ahead logging

## COMMANDS

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests (90% coverage required)
pytest

# Run with coverage
pytest --cov --cov-fail-under=90

# Build distribution
python -m build

# CLI usage (after install)
madousho --help
madousho serve
madousho verify
madousho version
```

## NOTES

- **CI/CD**: GitHub Actions publishes to PyPI on release tag
- **TestPyPI**: Untagged commits → dev version to TestPyPI
- **PyPI**: Tagged releases → official PyPI
- **Database**: Default SQLite at `./madousho.db` (configurable)
