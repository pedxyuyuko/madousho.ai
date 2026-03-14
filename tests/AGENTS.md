# Tests - pytest Test Suite

## OVERVIEW

pytest-based test suite with 90% coverage enforcement. Class-based organization, comprehensive fixture usage, temporary file isolation.

## STRUCTURE

```
tests/
├── __init__.py
├── test_cli.py
├── test_config.py          # Config loading, validation, caching
├── test_database.py        # Database singleton, session management
├── test_global_options.py  # CLI global options (--verbose, --json)
├── test_serve_command.py   # serve command tests
└── test_verify_command.py  # verify command tests
```

## TEST FRAMEWORK

- **Runner**: pytest 7.4+
- **Coverage**: 90% minimum required (`--cov-fail-under=90`)
- **Async support**: `pytest-asyncio` with `asyncio_mode = auto`
- **CLI testing**: `typer.testing.CliRunner`
- **Config**: `pytest.ini` + `pyproject.toml`

## CONVENTIONS

- **File naming**: `test_*.py` (pytest default)
- **Function naming**: `test_*` functions
- **Class organization**: Group related tests in classes with descriptive names
- **Docstrings**: Each test class has docstring explaining purpose
- **AAA pattern**: Arrange-Act-Assert structure in test functions

## FIXTURE PATTERNS

### Singleton Reset (autouse)
```python
@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset Database singleton between tests."""
    yield
    Database.get_instance().dispose()
    Database._instance = None
```

### Temporary Config Files
```python
with tempfile.TemporaryDirectory() as tmpdir:
    config_file = Path(tmpdir) / "madousho.yaml"
    config_file.write_text(yaml_content)
    os.environ["MADOUSHO_CONFIG_PATH"] = tmpdir
    # Run test...
```

### CLI Runner
```python
from typer.testing import CliRunner
runner = CliRunner()
result = runner.invoke(app, ["command", "--option", "value"])
assert result.exit_code == 0
```

## WHERE TO LOOK

| Test File | Coverage | Key Patterns |
|-----------|----------|--------------|
| `test_config.py` | Config loading | YAML parsing, Pydantic validation, caching, file resolution |
| `test_database.py` | Database | Singleton pattern, session context manager, SQLite PRAGMA |
| `test_cli.py` | CLI | Basic CLI invocation, version command |
| `test_serve_command.py` | serve command | Command invocation with config |
| `test_verify_command.py` | verify command | Config validation, error cases |
| `test_global_options.py` | Global flags | --verbose, --json options across commands |

## COVERAGE EXCLUSIONS

From `pyproject.toml`:
- `src/madousho/cli.py` - CLI entry point
- `src/madousho/_version.py` - Auto-generated
- `src/madousho/commands/*` - Command modules
- `src/madousho/logging/*` - Logging configuration

## RUNNING TESTS

```bash
# Basic run
pytest

# With coverage
pytest --cov

# Specific file
pytest tests/test_config.py -v

# Specific test function
pytest tests/test_database.py::TestDatabaseSingleton::test_singleton_pattern

# With coverage report
pytest --cov --cov-report=html
```

## ANTI-PATTERNS

- **DO NOT** skip singleton reset in fixtures - causes test pollution
- **DO NOT** use absolute paths in tests - use `tempfile.TemporaryDirectory()`
- **DO NOT** test implementation details - test behavior and outputs
- **DO NOT** ignore coverage failures - 90% is a hard requirement

## RELATED

- Root: `./AGENTS.md` for project-wide conventions
- Config: `src/madousho/config/AGENTS.md` for configuration patterns
- Database: `src/madousho/database/AGENTS.md` for singleton pattern
