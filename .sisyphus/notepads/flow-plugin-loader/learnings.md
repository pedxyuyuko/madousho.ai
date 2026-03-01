# Task 9: Flow Loader Core Implementation - Learnings

## Implementation Summary

Successfully implemented flow loading and instantiation logic in `src/madousho/flow/loader.py`.

### Functions Implemented

1. **`load_pyproject_metadata(plugin_path: Path) -> FlowPluginMetadata`**
   - Reads plugin metadata from `pyproject.toml` using Python's built-in `tomllib` (Python 3.11+)
   - Extracts: name, version, description, author
   - Fallbacks: uses directory name if name missing, "0.0.0" if version missing
   - Properly handles TOML parsing errors

2. **`import_flow_module(plugin_path: Path) -> ModuleType`**
   - Dynamically imports `src/main.py` from plugin
   - Creates unique module names to avoid conflicts: `madousho_flow_{plugin_name}_{id}`
   - Handles FileNotFoundError, SyntaxError, ImportError
   - Registers module in `sys.modules` for proper cleanup

3. **`load_plugin(plugin_path: Path, global_config: Dict) -> PluginLoadResult`**
   - Orchestrates the complete plugin loading process
   - Steps:
     1. Validate flow config (Task 7 - already implemented)
     2. Load metadata from pyproject.toml
     3. Import src/main.py module
     4. Get FlowClass using `get_flow_class()` from base.py
     5. Instantiate flow with `flow_config` and `global_config`
     6. Create FlowPlugin and return success result
   - Accumulates errors and warnings throughout the process
   - Returns `PluginLoadResult` with success/failure status

### Key Design Decisions

1. **TOML vs YAML**: Used `tomllib` (built-in Python 3.11+) for pyproject.toml parsing instead of yaml, as pyproject.toml is TOML format by specification.

2. **FlowClass Export**: Following the updated design, flow plugins must export a `FlowClass` variable in their `src/main.py`:
   ```python
   from madousho.flow.base import FlowBase
   
   class MyFlow(FlowBase):
       def run(self, **kwargs):
           pass
   
   FlowClass = MyFlow  # Required export
   ```

3. **Config Passing**: Flow instances receive both `flow_config` (from config.yaml) and `global_config` (from madousho.yaml) during instantiation.

4. **Error Accumulation**: Errors are accumulated throughout the loading process rather than failing fast, providing better debugging information.

### Test Coverage

Created comprehensive test suite in `tests/flow/test_loader.py` with 25 tests:

- **TestLoadPyprojectMetadata** (6 tests): Valid/invalid TOML, missing files, fallback behavior
- **TestImportFlowModule** (5 tests): Valid imports, missing files, syntax errors, unique naming
- **TestLoadPlugin** (13 tests): Success cases, error cases, typehint validation, config passing
- **TestLoadPluginIntegration** (1 test): Complete lifecycle test

All tests pass: **25/25** ✓

### Dependencies

- `tomllib`: Built-in Python 3.11+ for TOML parsing
- `importlib.util`: For dynamic module loading
- Existing imports: `yaml`, `pydantic`, pathlib, typing

### Files Modified

1. `src/madousho/flow/loader.py` - Added 3 new functions (+ imports)
2. `tests/flow/test_loader.py` - New test file with 25 tests

### Verification

```bash
# All flow tests pass
pytest tests/flow/ -v -p no:asyncio
# Result: 94 passed (including 25 new loader tests)

# Import verification
python -c "from madousho.flow.loader import load_pyproject_metadata, import_flow_module, load_plugin"
# Result: All imports successful
```

## Notes for Future Tasks

- Dependency validation (tools/mcps) postponed to future task
- CLI integration will be added in Task 10
- The loader properly separates concerns: config validation (Task 7) vs. module loading (Task 9)
- Flow instantiation happens after all validation, ensuring clean error messages


## Task 11: Integration Tests - Summary

Successfully created comprehensive integration tests in `tests/flow/test_integration.py` with 23 test cases covering:

### Test Coverage
1. **Happy Path Tests (3 tests)**
   - Complete plugin loading workflow
   - Plugin with full configuration
   - Plugin execution after loading

2. **Error Handling Tests (7 tests)**
   - Missing config.yaml (2 tests)
   - Invalid config.yaml (2 tests)
   - Missing FlowClass export (3 tests)

3. **MODEL_GROUP Validation Tests (4 tests)**
   - Model group not in global config
   - Empty model group with no default
   - Model group success with valid config
   - Model group uses global default

4. **Mixed Mode Error Reporting (2 tests)**
   - Multiple plugins with mixed success/failure
   - Clear error messages for different failure types

5. **Flow Registration & Retrieval (4 tests)**
   - Register loaded flow to registry
   - Register multiple flows
   - Prevent duplicate registration
   - End-to-end: load → register → execute

6. **Edge Cases (3 tests)**
   - Empty pyproject.toml
   - Unicode content support
   - Nested directory structures

### Results
- **All 23 tests pass** ✓
- **Integration test coverage: 89.63%** (loader.py: 85%, base.py: 91%, registry.py: 97%, models.py: 100%)
- **Combined with unit tests: 93.78% coverage** ✓

### Key Features
- Module-level helper function `create_valid_plugin()` for reusable test setup
- Realistic temporary directory structures for each test
- Comprehensive error message validation
- End-to-end workflow testing (load → register → execute)
- Mixed mode testing (some plugins succeed, others fail with clear errors)

### Files Created
1. `tests/flow/test_integration.py` - 809 lines, 23 tests

### Test Execution
```bash
# Run integration tests
pytest tests/flow/test_integration.py -v -p no:asyncio

# Run with coverage
pytest tests/flow/test_integration.py tests/flow/test_loader.py --cov=madousho.flow --cov-fail-under=90
```
