# Test Suite

**Location:** `tests/`

## OVERVIEW

Pytest-based test suite with 90% coverage requirement, organized to mirror `src/madousho/` structure. Uses pytest-asyncio for async tests, pytest-cov for coverage enforcement.

## STRUCTURE

```
tests/
├── __init__.py              # Package marker
├── conftest.py              # Pytest fixtures (minimal)
├── config/                  # Configuration tests (~1269 lines)
│   ├── __init__.py
│   ├── test_models.py       # Pydantic model validation (258 lines)
│   ├── test_loader.py       # ConfigManager, YAML loading (377 lines)
│   ├── test_typehint_models.py  # TypeHintValidator (311 lines)
│   └── test_integration.py  # End-to-end config tests (323 lines)
└── flow/                    # Flow engine tests (~3557 lines)
    ├── test_base.py         # FlowBase ABC (277 lines)
    ├── test_base_extensions.py  # retry_until, run_parallel (406 lines)
    ├── test_tasks.py        # TaskBase, task lifecycle (146 lines)
    ├── test_storage.py      # FlowStorage, AtomicJsonWriter (465 lines)
    ├── test_loader.py       # Plugin loading (531 lines)
    ├── test_registry.py     # FlowRegistry singleton (110 lines)
    ├── test_models.py       # FlowPlugin models (177 lines)
    ├── test_config_validation.py  # Flow config validation (633 lines)
    └── test_integration.py  # End-to-end flow tests (812 lines)
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Config model tests | `config/test_models.py` | APIConfig, ProviderConfig, Config validation |
| Config loader tests | `config/test_loader.py` | ConfigManager singleton, normalize_keys, YAML loading |
| Typehint tests | `config/test_typehint_models.py` | TypeHintDefinition, TypeHintValidator |
| FlowBase tests | `flow/test_base.py` | FlowBase instantiation, run_task, context |
| FlowBase extensions | `flow/test_base_extensions.py` | run_parallel, retry_until, get_tasks |
| Task tests | `flow/test_tasks.py` | TaskBase, task lifecycle, UUID assignment |
| Storage tests | `flow/test_storage.py` | AtomicJsonWriter, FlowIndex, FlowStorage |
| Plugin loader tests | `flow/test_loader.py` | load_plugin, validate_flow_config, import_flow_module |
| Registry tests | `flow/test_registry.py` | FlowRegistry singleton, thread safety |
| Integration tests | `flow/test_integration.py` | End-to-end flow execution |

## CONVENTIONS

- **Test file naming**: `test_*.py` (prefix) or `*_test.py` (suffix)
- **Test function naming**: `test_{feature}_{scenario}` (e.g., `test_valid_port_boundaries`)
- **Test class naming**: `Test*` (e.g., `TestAPIConfig`, `TestFlowBaseInstantiation`)
- **Docstrings required**: Each test method has descriptive docstring explaining purpose
- **90% coverage enforced**: `--cov-fail-under=90` in pytest configuration
- **Coverage exclusions**: cli.py, logger.py, commands/*, tests/*, temp directories
- **Async tests**: Use `@pytest.mark.asyncio` decorator, `asyncio_mode = auto`
- **Test isolation**: Use `ConfigManager.reset_instance()`, `FlowRegistry.reset_instance()`

## ANTI-PATTERNS (THIS MODULE)

- DO NOT skip docstrings on test methods (required for test documentation)
- DO NOT share state between tests (use fixtures or reset singletons)
- DO NOT test implementation details (test behavior, not internal state)
- DO NOT skip coverage exclusions in pyproject.toml (cli.py, logger.py excluded by design)
- DO NOT use `print()` in tests (use pytest output or logger)
- DO NOT catch exceptions silently in tests (let pytest handle failures)

## UNIQUE PATTERNS

- **Singleton reset for testing**: `ConfigManager.reset_instance()`, `FlowRegistry.reset_instance()` for test isolation
- **Mock classes for ABC testing**: Create concrete subclasses for testing abstract bases
  ```python
  class MockFlow(FlowBase):
      def run(self):
          return "mock"
  
  class MockTask(TaskBase):
      def run(self):
          return {"result": "mock"}
  ```
- **Pytest.raises for negative tests**: `pytest.raises(ValidationError)` for validation failures
- **Direct model instantiation**: Test Pydantic models directly without fixtures
  ```python
  def test_valid_config(self):
      config = Config(api=..., provider=..., default_model_group="...")
  ```
- **Async test functions**: Use `async def test_...()` with `@pytest.mark.asyncio`
- **Temporary directory fixtures**: Use `tmp_path` for file I/O tests (AtomicJsonWriter, FlowStorage)

## TEST CATEGORIES

### Unit Tests

Test individual classes/functions in isolation:

**Config tests** (`tests/config/`):
- `test_models.py` - Pydantic validation (valid/invalid configs, field validators)
- `test_loader.py` - ConfigManager singleton, normalize_keys, YAML parsing
- `test_typehint_models.py` - TypeHintValidator with various type scenarios

**Flow tests** (`tests/flow/`):
- `test_base.py` - FlowBase instantiation, run_task, context management
- `test_tasks.py` - TaskBase, task lifecycle, UUID assignment
- `test_registry.py` - FlowRegistry singleton, thread safety

### Integration Tests

Test component interactions:

- `tests/config/test_integration.py` - End-to-end config loading with YAML files
- `tests/flow/test_integration.py` - Full flow execution with task persistence
- `tests/flow/test_config_validation.py` - Flow plugin config validation against typehint

### Async Tests

Test async storage operations:

```python
@pytest.mark.asyncio
async def test_write_creates_file(self, tmp_path):
    """Test that write creates the target file."""
    path = tmp_path / "test.json"
    await AtomicJsonWriter.write(path, {"key": "value"})
    assert path.exists()
```

## KEY TEST PATTERNS

### Testing Pydantic Models

```python
class TestAPIConfig:
    def test_valid_port_boundaries(self):
        """Test port validation at boundaries (1 and 65535)."""
        config = APIConfig(host="localhost", port=1)
        assert config.port == 1
        
        config = APIConfig(host="localhost", port=65535)
        assert config.port == 65535
    
    def test_invalid_port_zero(self):
        """Test that port=0 raises ValidationError."""
        with pytest.raises(ValidationError):
            APIConfig(host="localhost", port=0)
```

### Testing Abstract Base Classes

```python
class MockFlow(FlowBase):
    """Mock FlowBase for testing."""
    def run(self):
        return "mock_result"

class TestFlowBaseInstantiation:
    def test_flow_initialization_with_flow_config(self):
        """Test flow instance creation with flow_config."""
        flow_config = {"name": "test_flow", "example_use_model_group": "default"}
        flow = MockFlow(flow_config=flow_config)
        assert flow.name == "test_flow"
```

### Testing Singleton Patterns

```python
class TestConfigManagerSingleton:
    def test_get_instance_creates_instance(self, tmp_path):
        """Test that get_instance creates instance on first call."""
        ConfigManager.reset_instance()  # Reset for test isolation
        instance = ConfigManager.get_instance(str(tmp_path))
        assert instance is not None
        
    def test_get_instance_returns_same_instance(self, tmp_path):
        """Test that get_instance returns same instance on subsequent calls."""
        ConfigManager.reset_instance()
        instance1 = ConfigManager.get_instance(str(tmp_path))
        instance2 = ConfigManager.get_instance()
        assert instance1 is instance2
```

### Testing Async Storage

```python
@pytest.mark.asyncio
class TestAtomicJsonWriter:
    async def test_write_atomic(self, tmp_path):
        """Test that write is atomic (temp file + replace)."""
        path = tmp_path / "test.json"
        data = {"key": "value", "nested": {"a": 1}}
        
        await AtomicJsonWriter.write(path, data)
        
        assert path.exists()
        with open(path) as f:
            loaded = json.load(f)
        assert loaded == data
    
    async def test_write_creates_parent_dirs(self, tmp_path):
        """Test that write creates parent directories if missing."""
        path = tmp_path / "subdir" / "nested" / "test.json"
        
        await AtomicJsonWriter.write(path, {"key": "value"})
        
        assert path.exists()
```

### Testing Plugin Loading

```python
class TestPluginLoading:
    def test_load_plugin_success(self, example_plugin_path):
        """Test successful plugin loading."""
        result = load_plugin(example_plugin_path, global_config)
        
        assert result.success is True
        assert result.plugin is not None
        assert len(result.errors) == 0
    
    def test_load_plugin_missing_config(self, tmp_path):
        """Test plugin loading fails without config.yaml."""
        plugin_path = tmp_path / "bad_plugin"
        plugin_path.mkdir()
        
        result = load_plugin(plugin_path, global_config)
        
        assert result.success is False
        assert "config.yaml" in str(result.errors[0])
```

## FIXTURES

### Built-in Pytest Fixtures

- `tmp_path` - Temporary directory for file I/O tests
- `tmp_path_factory` - Factory for creating temporary directories
- `monkeypatch` - Patch environment variables, attributes
- `capsys` - Capture stdout/stderr

### Custom Fixtures (conftest.py)

Currently minimal - conftest.py is mostly empty. Most tests use direct instantiation.

## COVERAGE CONFIGURATION

**pyproject.toml**:
```toml
[tool.coverage.run]
branch = true
source = ["src/madousho"]
omit = [
    "*/tmp/pytest-of-*/*",
    "*/.pytest_cache/*",
    "*/tests/*",
    "src/madousho/cli.py",
    "src/madousho/logger.py",
    "src/madousho/commands/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
```

**Excluded from coverage**:
- cli.py - CLI entry point (Typer handles)
- logger.py - Logging configuration (Loguru)
- commands/* - CLI commands (thin wrappers)
- tests/* - Test code itself

## RUNNING TESTS

```bash
# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov --cov-fail-under=90

# Run specific test directory
python -m pytest tests/flow/
python -m pytest tests/config/

# Run only async tests
python -m pytest -m asyncio

# Run specific test file
python -m pytest tests/flow/test_storage.py

# Run specific test class
python -m pytest tests/flow/test_storage.py::TestAtomicJsonWriter

# Run specific test function
python -m pytest tests/flow/test_storage.py::TestAtomicJsonWriter::test_write_creates_file

# Verbose output
python -m pytest -v

# Stop on first failure
python -m pytest -x

# Show local variables on failure
python -m pytest -l
```

## TEST STATISTICS

| Directory | Files | Lines | Coverage Target |
|-----------|-------|-------|-----------------|
| tests/config/ | 5 | ~1,269 | 90% |
| tests/flow/ | 10 | ~3,557 | 90% |
| **Total** | **15** | **~4,826** | **90%** |
