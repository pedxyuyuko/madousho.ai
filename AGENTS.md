# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-28
**Commit:** HEAD
**Branch:** master

## OVERVIEW

Madousho.ai (魔导书) - Systematic AI Agent Framework with fixed flow control + AI-executed steps. Python CLI application using Typer, Pydantic for config validation, and YAML configuration.

## STRUCTURE

```
madousho_ai/
├── src/madousho/        # Main package (CLI, commands, config)
├── tests/               # Pytest test suite
├── config/              # Default configuration files
├── .github/workflows/   # CI/CD (PyPI publish on release)
└── pyproject.toml       # Build system, metadata, entry point
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| CLI entry point | `src/madousho/cli.py` | Typer app, `madousho` command |
| Command implementations | `src/madousho/commands/` | run.py, validate.py |
| Configuration models | `src/madousho/config/models.py` | Pydantic models |
| Config loader | `src/madousho/config/loader.py` | YAML + env overrides |
| Tests | `tests/` | pytest, 90% coverage required |
| CI/CD | `.github/workflows/` | TestPyPI on master, PyPI on release |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `app` | Typer | cli.py:13 | Main CLI application |
| `find_config_file` | fn | cli.py:16 | 4-layer config search |
| `run_cmd` | fn | commands/run.py:8 | Start service stub |
| `validate_cmd` | fn | commands/validate.py:8 | Validate config |
| `Config` | class | config/models.py:33 | Main config model |
| `load_config` | fn | config/loader.py:116 | Load + validate config |

## CONVENTIONS

- **Python 3.14+** (unusual - targets future Python version)
- **Pydantic v2** with `model_validate()`, `model_dump()` (not v1 methods)
- **Extra fields forbidden** in all Pydantic models (`extra="forbid"`)
- **Hyphen-to-underscore** normalization in config loader
- **Environment overrides** via `MADOUSHO_*` prefix

## ANTI-PATTERNS (THIS PROJECT)

- DO NOT use Pydantic v1 syntax (`.dict()`, `.parse_obj()`)
- DO NOT add extra fields to config models (rejected by validation)
- DO NOT modify config search order (4-layer strategy is intentional)
- DO NOT skip type hints (project uses full typing)

## UNIQUE STYLES

- **4-layer config search**: CLI param → env var → cwd → ~/.config
- **Config normalization**: YAML hyphens auto-converted to underscores
- **Env var overrides**: `MADOUSHO_API_PORT=9000` → `{"api": {"port": 9000}}`

## COMMANDS

```bash
# Development install
pip install -e .

# Run tests (90% coverage required)
python -m pytest

# Build distribution
python -m build

# CLI usage
madousho run --config ./config/madousho.yaml
madousho validate
madousho --version
```

## NOTES

- **Entry point**: `madousho = "madousho.cli:app"` in pyproject.toml
- **Test coverage**: pytest configured with `--cov-fail-under=90`
- **CI/CD**: TestPyPI on master push, PyPI on release published
- **Config files**: `config/madousho.yaml` (default), `config/madousho.example.yaml` (template)
