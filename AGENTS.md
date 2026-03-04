# PROJECT KNOWLEDGE BASE

**Generated:** 2026-03-03
**Commit:** 3b8ad40
**Branch:** master

## OVERVIEW

Madousho.ai (魔导书) - Systematic AI Agent Framework with fixed flow control + AI-executed steps. Python CLI application using Typer, Pydantic v2 for config validation, and YAML configuration.

## STRUCTURE

```
madousho_ai/
├── src/madousho/        # Main package (CLI, commands, config, flow)
├── tests/               # Pytest test suite (90% coverage required)
├── config/              # Default configuration files
├── examples/            # Example flows and template projects
├── plugins/             # Reserved for Git-based plugin system
├── .github/workflows/   # CI/CD (TestPyPI on master, PyPI on release)
└── pyproject.toml       # Build system, metadata, entry point
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| CLI entry point | `src/madousho/cli.py` | Typer app, `madousho` command |
| Command implementations | `src/madousho/commands/` | run.py, validate.py |
| Flow engine | `src/madousho/flow/` | base.py, loader.py, models.py, registry.py |
| Configuration models | `src/madousho/config/models.py` | Pydantic v2 models |
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
| `FlowBase` | class | flow/base.py | Base flow class |
| `FlowLoader` | class | flow/loader.py | Flow definition loader |
| `FlowRegistry` | class | flow/registry.py | Flow registration |

## CONVENTIONS

- **Python 3.14+** (unusual - targets future Python version)
- **Pydantic v2** with `model_validate()`, `model_dump()` (not v1 methods)
- **Extra fields forbidden** in all Pydantic models (`extra="forbid"`)
- **Hyphen-to-underscore** normalization in config loader
- **Environment overrides** via `MADOUSHO_*` prefix
- **Full type hints required** (no skipping type annotations)

## ANTI-PATTERNS (THIS PROJECT)

- DO NOT use Pydantic v1 syntax (`.dict()`, `.parse_obj()`)
- DO NOT add extra fields to config models (rejected by validation)
- DO NOT modify config search order (4-layer strategy is intentional)
- DO NOT skip type hints (project uses full typing)
- DO NOT use `python -m madousho` (missing `__main__.py`)

## UNIQUE STYLES

- **4-layer config search**: CLI param → env var → cwd → ~/.config
- **Config normalization**: YAML hyphens auto-converted to underscores
- **Env var overrides**: `MADOUSHO_API_PORT=9000` → `{"api": {"port": 9000}}`
- **Triple-comment line markers** in tests (editor/plugin generated)
- **Docstring-heavy test methods** with descriptive documentation

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
- **Version management**: setuptools_scm from git tags (hardcoded in `__init__.py` is a bug)
- **Python version bug**: `pyproject.toml` requires `>=3.14` (should be `>=3.10`)
