# tests/ KNOWLEDGE BASE

**Generated:** 2026-03-03
**Commit:** 3b8ad40
**Branch:** master

## OVERVIEW

Pytest test suite with 90% coverage requirement. Mirrors src/ structure with dedicated test modules.

## STRUCTURE

```
tests/
├── conftest.py         # Pytest fixtures (minimal)
├── __init__.py         # Package marker
├── config/             # Config system tests
│   ├── test_models.py
│   ├── test_loader.py
│   ├── test_integration.py
│   └── test_typehint_models.py
├── flow/               # Flow engine tests
│   ├── test_base.py
│   ├── test_models.py
│   ├── test_loader.py
│   ├── test_registry.py
│   ├── test_config_validation.py
│   └── test_integration.py
└── commands/           # CLI command tests
    └── test_*.py
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Task | Location | Notes |
|------|----------|-------|
| Config tests | `tests/config/` | Models, loader, integration, typehint models |
| Flow tests | `tests/flow/` | Base, models, loader, registry, storage, tasks |
| Command tests | `tests/commands/` | CLI command handlers |
| Fixtures | `conftest.py` | Currently minimal (monkeypatch, tmp_path) |
| Coverage config | `pytest.ini` | `--cov-fail-under=90` |
| Pytest config | `pyproject.toml` | `[tool.pytest.ini_options]` - strict markers, strict config |
| Flow tests | `tests/flow/` | Base, models, loader, registry |
| Command tests | `tests/commands/` | CLI command handlers |
| Fixtures | `conftest.py` | Currently minimal (expand as needed) |
| Coverage config | `pytest.ini` | `--cov-fail-under=90` |

## CONVENTIONS

- **File naming**: `test_*.py` (primary) or `*_test.py` (supported)
- **Function naming**: `test_<scenario>_<condition>` (e.g., `test_valid_port_boundaries`)
- **Class naming**: `Test<ClassName>` (e.g., `TestAPIConfig`)
- **Docstrings**: Every test method includes descriptive docstring
- **Boundary testing**: Explicit tests for edge cases (min/max values)
- **Extra field rejection**: Consistent pattern testing `extra="forbid"`

## ANTI-PATTERNS (THIS MODULE)

- DO NOT skip docstrings in test methods
- DO NOT use parametrize without clear test case names
- DO NOT test implementation details - test behavior
- DO NOT skip boundary value tests for validators
- DO NOT use fixtures without documenting in conftest.py
- DO NOT reduce coverage below 90% (CI will fail)

## UNIQUE STYLES

- **Triple-comment line markers**: Every line starts with 2-char marker + `|` (editor/plugin generated)
- **Docstring-heavy tests**: Each test method has descriptive documentation
- **Boundary testing pattern**: Explicit min/max value tests for validators
- **Extra fields rejection testing**: Consistent ValidationError assertions
- **Dual naming support**: Both `test_*.py` and `*_test.py` recognized
- **Monkeypatch cleanup**: `monkeypatch.delenv(key, raising=False)` before tests
- **Environment override testing**: MADOUSHO_* prefix patterns tested extensively
- **Normalization testing**: Hyphen-to-underscore conversion in config loader
- **Docstring-heavy tests**: Each test method has descriptive documentation
- **Boundary testing pattern**: Explicit min/max value tests for validators
- **Extra fields rejection testing**: Consistent ValidationError assertions
- **Dual naming support**: Both `test_*.py` and `*_test.py` recognized

## COMMANDS

```bash
# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=madousho --cov-report=term-missing

# Run specific test file
python -m pytest tests/config/test_models.py -v

# Run specific test class
python -m pytest tests/config/test_models.py::TestAPIConfig -v

# Run specific test method
python -m pytest tests/config/test_models.py::TestAPIConfig::test_valid_port_boundaries -v
```

## NOTES

- **Coverage enforcement**: `--cov-fail-under=90` in pytest.ini
- **Strict markers**: `--strict-markers` prevents undefined markers
- **Strict config**: `--strict-config` catches invalid pytest config
- **Python 3.14 target**: Tests target future Python version
- **No fixtures**: conftest.py currently empty - add fixtures as needed
- **CI integration**: Tests run automatically on master push (TestPyPI workflow)
- **Test discovery**: `test_*.py` and `*_test.py` patterns supported
- **Verbose output**: `-v` flag in pytest.ini for detailed test output
- **Strict markers**: `--strict-markers` prevents undefined markers
- **Strict config**: `--strict-config` catches invalid pytest config
- **Python 3.14 target**: Tests target future Python version
- **No fixtures**: conftest.py currently empty - add fixtures as needed
- **CI integration**: Tests run automatically on master push (TestPyPI workflow)
