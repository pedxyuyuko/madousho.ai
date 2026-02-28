# Python Project Initialization + Configuration Loader

## TL;DR

> **Quick Summary**: Initialize Python 3.14 project with src/ layout and implement a type-safe configuration loader with Pydantic validation, YAML parsing, and environment variable overrides.
> 
> **Deliverables**:
> - src/madousho/ package structure with __init__.py
> - src/madousho/config/loader.py - Main configuration loader
> - src/madousho/config/models.py - Pydantic models for validation
> - src/madousho/config/__init__.py - Public API exports
> - tests/config/ - Test suite for configuration loader
> - requirements.txt - Dependencies (pyyaml, pydantic, pytest)
> - pyproject.toml - Project metadata and build configuration
> 
> **Estimated Effort**: Short
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Task 1 → Task 2 → Task 3

---

## Context

### Original Request
1. Initialize basic Python project structure
2. Implement configuration loader based on @config/ files

### Interview Summary
**Key Discussions**:
- **Python Version**: 3.14 with venv + pip
- **Project Layout**: src/ layout (src/madousho/)
- **Validation**: Pydantic for type-safe configuration
- **Testing**: pytest for test infrastructure

**Research Findings**:
- **Config Format**: YAML with custom prefix comments (#MH|, #NR|, etc.)
- **Config Structure**: api (host, port, token), provider (dict), model_groups (dict)
- **Env Override**: MADOUSHO_ prefix for all settings
- **Existing Files**: config/madousho.yaml (active), config/madousho.example.yaml (template)

### Metis Review
**Identified Gaps** (addressed):
- **Error handling**: Added explicit error messages for missing/invalid config values
- **Edge cases**: Added tests for malformed YAML, missing files, invalid env vars
- **Guardrails**: Explicit exclusion of hot-reloading, encryption, distributed config
- **Acceptance criteria**: Added specific test coverage and performance benchmarks

---

## Work Objectives

### Core Objective
Initialize a production-ready Python project structure and implement a robust, type-safe configuration loader that validates YAML configs with Pydantic and supports environment variable overrides.

### Concrete Deliverables
- src/madousho/ package with proper __init__.py
- Configuration loader module (loader.py + models.py)
- pytest test suite with 90%+ coverage
- requirements.txt with pinned dependencies
- pyproject.toml for project metadata

### Definition of Done
- [ ] `python -m pytest tests/` passes with 0 failures
- [ ] `python -c "from madousho.config import load_config"` succeeds
- [ ] Config loading completes in <100ms
- [ ] All Pydantic models validate correctly

### Must Have
- Pydantic v2 validation for all config sections
- Environment variable override (MADOUSHO_ prefix)
- Clear error messages for invalid configs
- Test coverage for happy path and error cases

### Must NOT Have (Guardrails)
- NO hot-reloading of configs at runtime
- NO automatic config file creation/modification
- NO encryption/decryption of sensitive values
- NO integration with external config services
- NO dynamic schema migration

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.
> Acceptance criteria requiring "user manually tests/confirms" are FORBIDDEN.

### Test Decision
- **Infrastructure exists**: NO
- **Automated tests**: TDD
- **Framework**: pytest
- **If TDD**: Each task follows RED (failing test) → GREEN (minimal impl) → REFACTOR

### QA Policy
Every task MUST include agent-executed QA scenarios (see TODO template below).
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Frontend/UI**: Use Playwright (playwright skill) — Navigate, interact, assert DOM, screenshot
- **TUI/CLI**: Use interactive_bash (tmux) — Run command, send keystrokes, validate output
- **API/Backend**: Use Bash (curl) — Send requests, assert status + response fields
- **Library/Module**: Use Bash (bun/node REPL) — Import, call functions, compare output

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — Project scaffolding):
├── Task 1: Project structure + pyproject.toml [quick]
├── Task 2: requirements.txt with dependencies [quick]
└── Task 3: pytest configuration + initial test structure [quick]

Wave 2 (After Wave 1 — Config loader implementation):
├── Task 4: Pydantic models for config validation [unspecified-high]
├── Task 5: Config loader with YAML parsing + env override [unspecified-high]
└── Task 6: Config module public API + exports [quick]

Wave 3 (After Wave 2 — Testing):
├── Task 7: Unit tests for Pydantic models [deep]
├── Task 8: Unit tests for config loader [deep]
└── Task 9: Integration tests + coverage verification [deep]

Wave FINAL (After ALL tasks — independent review, 4 parallel):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)

Critical Path: Task 1 → Task 4 → Task 5 → Task 7 → F1-F4
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 3 (Waves 1, 2, 3)
```

### Dependency Matrix

- **1-3**: — — 4-6, 7
- **4**: 1, 2 — 5, 6, 7
- **5**: 4 — 6, 8
- **6**: 4, 5 — 8, 9
- **7**: 4 — 9, F1-F4
- **8**: 5, 6 — 9, F1-F4
- **9**: 7, 8 — F1-F4

### Agent Dispatch Summary

- **1**: **3** — T1-T3 → `quick`
- **2**: **3** — T4 → `unspecified-high`, T5 → `unspecified-high`, T6 → `quick`
- **3**: **3** — T7-T9 → `deep`
- **FINAL**: **4** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. Project Structure + pyproject.toml

  **What to do**:
  - Create src/madousho/ directory with __init__.py (exports: __version__ = "0.1.0")
  - Create tests/ directory with tests/__init__.py and tests/conftest.py
  - Create pyproject.toml with project metadata (name, version, description, requires-python = ">=3.14")
  - Create .gitignore for Python (venv/, __pycache__/, .pytest_cache/, .mypy_cache/)
  - Create README.md with project description and setup instructions

  **Must NOT do**:
  - Do not add any source code beyond __init__.py
  - Do not configure CI/CD yet
  - Do not add pre-commit hooks

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple file creation with standard Python project templates
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Tasks 4, 5, 6, 7, 8, 9
  - **Blocked By**: None (can start immediately)

  **References**:
  - PEP 517/518 - pyproject.toml standard
  - src/ layout pattern: https://hynek.me/articles/testing-packaging/

  **Acceptance Criteria**:
  - [ ] src/madousho/__init__.py exists with __version__ = "0.1.0"
  - [ ] tests/conftest.py exists (empty is OK)
  - [ ] pyproject.toml is valid TOML with required fields
  - [ ] python -m pytest --collect-only shows 0 tests collected (no errors)

  **QA Scenarios**:
  ```
  Scenario: Verify project structure
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: ls -la src/madousho/
      2. Verify: __init__.py exists
      3. Run: python -c "import sys; sys.path.insert(0, 'src'); import madousho; print(madousho.__version__)"
    Expected Result: Outputs "0.1.0"
    Failure Indicators: ImportError or wrong version
    Evidence: .sisyphus/evidence/task-1-structure-test.txt

  Scenario: Verify pytest setup
    Tool: Bash
    Preconditions: pytest installed
    Steps:
      1. Run: python -m pytest --collect-only 2>&1
      2. Verify: Exit code 0, no errors
    Expected Result: "collected 0 items" with exit code 0
    Failure Indicators: pytest error or test failure
    Evidence: .sisyphus/evidence/task-1-pytest-check.txt
  ```

  **Evidence to Capture**:
  - [ ] Directory structure listing
  - [ ] pytest collection output

  **Commit**: YES (groups with 2, 3)
  - Message: `chore(python): init project structure`
  - Files: `src/madousho/__init__.py`, `pyproject.toml`, `tests/conftest.py`, `.gitignore`
  - Pre-commit: `python -m pytest --collect-only`

- [x] 2. Requirements.txt with Dependencies

  **What to do**:
  - Create requirements.txt with pinned versions:
    - pyyaml>=6.0,<7.0 (YAML parsing)
    - pydantic>=2.0,<3.0 (validation)
    - pydantic-settings>=2.0,<3.0 (env var support)
    - pytest>=7.0,<8.0 (testing)
    - pytest-cov>=4.0,<5.0 (coverage)
  - Install dependencies in venv

  **Must NOT do**:
  - Do not add unnecessary dependencies
  - Do not use unpinned versions
  - Do not add dev tools beyond pytest

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Standard dependency management
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: Tasks 4, 5, 6, 7, 8, 9
  - **Blocked By**: None

  **References**:
  - PyYAML docs: https://pyyaml.org/wiki/PyYAMLDocumentation
  - Pydantic docs: https://docs.pydantic.dev/latest/
  - pytest docs: https://docs.pytest.org/

  **Acceptance Criteria**:
  - [ ] requirements.txt exists with all 5 dependencies
  - [ ] All versions are pinned with >= and < constraints
  - [ ] pip install -r requirements.txt succeeds
  - [ ] python -c "import yaml, pydantic, pytest" succeeds

  **QA Scenarios**:
  ```
  Scenario: Verify dependencies install
    Tool: Bash
    Preconditions: venv activated
    Steps:
      1. Run: pip install -r requirements.txt
      2. Verify: Exit code 0, no errors
      3. Run: python -c "import yaml, pydantic, pytest; print('OK')"
    Expected Result: Outputs "OK"
    Failure Indicators: ImportError or pip error
    Evidence: .sisyphus/evidence/task-2-deps-install.txt

  Scenario: Verify import works
    Tool: Bash
    Preconditions: Dependencies installed
    Steps:
      1. Run: python -c "from pydantic import BaseModel; from yaml import safe_load; print('All imports OK')"
    Expected Result: Outputs "All imports OK"
    Evidence: .sisyphus/evidence/task-2-import-check.txt
  ```

  **Evidence to Capture**:
  - [ ] pip install output
  - [ ] Import verification output

  **Commit**: YES (groups with 1, 3)
  - Message: `chore(python): init project structure`
  - Files: `requirements.txt`
  - Pre-commit: `pip install -r requirements.txt`

- [x] 3. Pytest Configuration + Initial Test Structure

  **What to do**:
  - Create pytest.ini or configure in pyproject.toml:
    - testpaths = ["tests"]
    - python_files = ["test_*.py"]
    - python_functions = ["test_*"]
    - addopts = "-v --tb=short"
  - Create tests/config/ directory with tests/config/__init__.py
  - Create tests/conftest.py with pytest fixtures for config testing
  - Create example test: tests/config/test_loader.py with one passing test

  **Must NOT do**:
  - Do not implement actual tests for config loader yet (Task 7-9)
  - Do not add complex fixtures beyond basic path fixtures
  - Do not configure coverage thresholds yet

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Standard pytest configuration
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: Tasks 7, 8, 9
  - **Blocked By**: None

  **References**:
  - pytest config: https://docs.pytest.org/en/latest/reference/customize.html
  - conftest.py pattern: https://docs.pytest.org/en/latest/how-to/fixtures.html

  **Acceptance Criteria**:
  - [ ] pytest.ini or [tool.pytest] in pyproject.toml exists
  - [ ] tests/config/__init__.py exists
  - [ ] tests/config/test_loader.py exists with at least 1 test
  - [ ] python -m pytest tests/ passes with 0 failures

  **QA Scenarios**:
  ```
  Scenario: Verify pytest configuration
    Tool: Bash
    Preconditions: pytest installed
    Steps:
      1. Run: python -m pytest tests/ -v
      2. Verify: Exit code 0, at least 1 test collected
    Expected Result: "1 passed" or more
    Failure Indicators: pytest error or test failure
    Evidence: .sisyphus/evidence/task-3-pytest-run.txt

  Scenario: Verify test discovery
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -m pytest --collect-only tests/
      2. Verify: Shows test_loader.py with test functions
    Expected Result: Lists test functions from test_loader.py
    Evidence: .sisyphus/evidence/task-3-test-discovery.txt
  ```

  **Evidence to Capture**:
  - [ ] pytest run output
  - [ ] Test discovery output

  **Commit**: YES (groups with 1, 2)
  - Message: `chore(python): init project structure`
  - Files: `pytest.ini`, `tests/config/__init__.py`, `tests/config/test_loader.py`
  - Pre-commit: `python -m pytest tests/`

- [x] 4. Pydantic Models for Config Validation

  **What to do**:
  - Create src/madousho/config/models.py with Pydantic v2 models:
    - APIConfig: host (str), port (int), token (str, optional)
    - ProviderConfig: type (str), endpoint (str), api_key (str)
    - ModelGroupConfig: Dict[str, List[str]] for provider/model mappings
    - Main Config: api (APIConfig), provider (Dict[str, ProviderConfig]), model_groups (Dict[str, List[str]])
  - Add field validators (e.g., port must be 1-65535, host must be valid IP)
  - Add model_config with extra='forbid' to catch typos
  - Export all models from module

  **Must NOT do**:
  - Do not implement loading logic (Task 5)
  - Do not add environment variable handling (Task 5)
  - Do not add custom validation beyond Pydantic validators

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires careful Pydantic model design with proper typing
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (sequential within wave)
  - **Blocks**: Tasks 5, 6, 7
  - **Blocked By**: Tasks 1, 2 (project structure + deps)

  **References**:
  - Pydantic docs: https://docs.pydantic.dev/latest/concepts/models/
  - Pydantic validators: https://docs.pydantic.dev/latest/concepts/validators/
  - config/madousho.yaml - actual config structure to match

  **Acceptance Criteria**:
  - [ ] src/madousho/config/models.py exists with all 4 model classes
  - [ ] All models use Pydantic BaseModel
  - [ ] Field validators for port range and host format
  - [ ] model_config with extra='forbid' on all models
  - [ ] python -c "from madousho.config.models import Config" succeeds

  **QA Scenarios**:
  ```
  Scenario: Valid config model instantiation
    Tool: Bash
    Preconditions: Models defined, dependencies installed
    Steps:
      1. Run: python -c "
import sys; sys.path.insert(0, 'src')
from madousho.config.models import Config, APIConfig
api = APIConfig(host='0.0.0.0', port=8000, token='test')
cfg = Config(api=api, provider={}, model_groups={})
print(f'Valid: {cfg.api.host}:{cfg.api.port}')"
    Expected Result: Outputs "Valid: 0.0.0.0:8000"
    Failure Indicators: ValidationError or ImportError
    Evidence: .sisyphus/evidence/task-4-valid-model.txt

  Scenario: Invalid port rejected
    Tool: Bash
    Preconditions: Models defined
    Steps:
      1. Run: python -c "
import sys; sys.path.insert(0, 'src')
from madousho.config.models import APIConfig
try:
    api = APIConfig(host='0.0.0.0', port=99999, token='test')
    print('ERROR: Should have failed')
except Exception as e:
    print(f'Rejected: {type(e).__name__}')"
    Expected Result: Outputs "Rejected: ValidationError"
    Failure Indicators: Model accepts invalid port
    Evidence: .sisyphus/evidence/task-4-invalid-port.txt
  ```

  **Evidence to Capture**:
  - [ ] Valid model instantiation output
  - [ ] Invalid port rejection output

  **Commit**: YES (groups with 5)
  - Message: `feat(config): add Pydantic models`
  - Files: `src/madousho/config/models.py`
  - Pre-commit: `python -c "from madousho.config.models import Config"`

- [x] 5. Config Loader with YAML Parsing + Env Override

  **What to do**:
  - Create src/madousho/config/loader.py with:
    - load_yaml(path: str) -> dict: Load and parse YAML file
    - get_env_overrides(prefix: str = "MADOUSHO_") -> dict: Scan env vars, build override dict
    - deep_merge(base: dict, override: dict) -> dict: Recursive merge
    - load_config(config_path: str = "config/madousho.yaml") -> Config: Main entry point
  - Implement env var parsing: MADOUSHO_API_PORT=9000 → {"api": {"port": 9000}}
  - Handle nested keys: MADOUSHO_PROVIDER_EXAMPLE_API_KEY=xyz
  - Validate final config with Pydantic models
  - Raise clear errors for missing required fields

  **Must NOT do**:
  - Do not modify config files
  - Do not add hot-reloading
  - Do not add encryption/decryption
  - Do not add distributed config support

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Core business logic with env var parsing complexity
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 4)
  - **Parallel Group**: Wave 2 (after Task 4)
  - **Blocks**: Tasks 6, 8, 9
  - **Blocked By**: Task 4 (models)

  **References**:
  - PyYAML docs: https://pyyaml.org/wiki/PyYAMLDocumentation
  - Pydantic settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
  - config/madousho.yaml - test data

  **Acceptance Criteria**:
  - [ ] src/madousho/config/loader.py exists with all 4 functions
  - [ ] load_config() returns validated Config model
  - [ ] Environment variables override YAML values
  - [ ] Clear error messages for missing/invalid config
  - [ ] Loading completes in <100ms

  **QA Scenarios**:
  ```
  Scenario: Load config from YAML
    Tool: Bash
    Preconditions: Config file exists at config/madousho.yaml
    Steps:
      1. Run: python -c "
import sys; sys.path.insert(0, 'src')
from madousho.config.loader import load_config
cfg = load_config('config/madousho.yaml')
print(f'Host: {cfg.api.host}, Port: {cfg.api.port}')"
    Expected Result: Outputs "Host: 0.0.0.0, Port: 8000"
    Failure Indicators: FileNotFoundError or ValidationError
    Evidence: .sisyphus/evidence/task-5-load-yaml.txt

  Scenario: Env var overrides YAML
    Tool: Bash
    Preconditions: Config file exists
    Steps:
      1. Run: MADOUSHO_API_PORT=9999 python -c "
import sys, os; sys.path.insert(0, 'src')
from madousho.config.loader import load_config
cfg = load_config('config/madousho.yaml')
print(f'Port: {cfg.api.port}')"
    Expected Result: Outputs "Port: 9999" (not 8000)
    Failure Indicators: Port is still 8000
    Evidence: .sisyphus/evidence/task-5-env-override.txt

  Scenario: Missing config file error
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "
import sys; sys.path.insert(0, 'src')
from madousho.config.loader import load_config
try:
    cfg = load_config('nonexistent.yaml')
    print('ERROR: Should have failed')
except Exception as e:
    print(f'Error: {type(e).__name__}')"
    Expected Result: Outputs error message with FileNotFoundError
    Failure Indicators: No error or unclear error
    Evidence: .sisyphus/evidence/task-5-missing-file.txt
  ```

  **Evidence to Capture**:
  - [ ] YAML loading output
  - [ ] Env override output
  - [ ] Error handling output

  **Commit**: YES (groups with 4)
  - Message: `feat(config): implement loader`
  - Files: `src/madousho/config/loader.py`
  - Pre-commit: `python -c "from madousho.config.loader import load_config; print(load_config('config/madousho.yaml').api.host)"`

- [x] 6. Config Module Public API + Exports

  **What to do**:
  - Create src/madousho/config/__init__.py
  - Export public API:
    - load_config function (from loader)
    - Config, APIConfig, ProviderConfig, ModelGroupConfig models
  - Add __all__ list for explicit exports
  - Add module docstring explaining usage
  - Create simple usage example in docstring

  **Must NOT do**:
  - Do not add additional functionality
  - Do not expose internal functions (load_yaml, get_env_overrides, deep_merge)
  - Do not add CLI interface

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple module exports and documentation
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (after Task 5)
  - **Blocks**: Tasks 8, 9
  - **Blocked By**: Tasks 4, 5 (models + loader)

  **References**:
  - Python __all__ convention: https://docs.python.org/3/tutorial/modules.html
  - src/madousho/__init__.py - package-level exports pattern

  **Acceptance Criteria**:
  - [ ] src/madousho/config/__init__.py exists
  - [ ] from madousho.config import load_config succeeds
  - [ ] from madousho.config import Config succeeds
  - [ ] __all__ list defined with all public exports
  - [ ] Module docstring with usage example

  **QA Scenarios**:
  ```
  Scenario: Import from public API
    Tool: Bash
    Preconditions: Config module complete
    Steps:
      1. Run: python -c "
import sys; sys.path.insert(0, 'src')
from madousho.config import load_config, Config
print('Public API imports OK')"
    Expected Result: Outputs "Public API imports OK"
    Failure Indicators: ImportError
    Evidence: .sisyphus/evidence/task-6-public-api.txt

  Scenario: Verify __all__ exports
    Tool: Bash
    Preconditions: Module complete
    Steps:
      1. Run: python -c "
import sys; sys.path.insert(0, 'src')
import madousho.config as cfg
print('Exports:', cfg.__all__)
print('load_config' in dir(cfg))"
    Expected Result: Shows __all__ list and True
    Failure Indicators: Missing exports
    Evidence: .sisyphus/evidence/task-6-exports.txt
  ```

  **Evidence to Capture**:
  - [ ] Public API import output
  - [ ] Exports verification output

  **Commit**: YES
  - Message: `chore(ci): finalize config module`
  - Files: `src/madousho/config/__init__.py`
  - Pre-commit: `python -c "from madousho.config import load_config, Config"`

- [x] 7. Unit Tests for Pydantic Models

  **What to do**:
  - Create tests/config/test_models.py
  - Test valid model instantiation for all model classes
  - Test field validation (invalid port, invalid host format)
  - Test extra='forbid' catches typos
  - Test nested model validation
  - Use pytest fixtures for common test data
  - Achieve 90%+ coverage on models.py

  **Must NOT do**:
  - Do not test loader functionality (Task 8)
  - Do not test env var overrides (Task 8)
  - Do not add integration tests yet (Task 9)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Comprehensive test coverage with edge cases
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (after Task 6)
  - **Blocks**: Task 9
  - **Blocked By**: Task 4 (models)

  **References**:
  - pytest docs: https://docs.pytest.org/en/latest/how-to/assert.html
  - Pydantic testing: https://docs.pydantic.dev/latest/concepts/models/#basic-usage
  - tests/conftest.py - shared fixtures

  **Acceptance Criteria**:
  - [ ] tests/config/test_models.py exists with 10+ test functions
  - [ ] All tests pass with pytest
  - [ ] Coverage on models.py >= 90%
  - [ ] Tests cover: valid instantiation, validation errors, extra fields rejected

  **QA Scenarios**:
  ```
  Scenario: Run model tests
    Tool: Bash
    Preconditions: Tests written, dependencies installed
    Steps:
      1. Run: python -m pytest tests/config/test_models.py -v
      2. Verify: All tests pass, 0 failures
    Expected Result: "passed" for all tests
    Failure Indicators: Any test failure or error
    Evidence: .sisyphus/evidence/task-7-model-tests.txt

  Scenario: Verify model test coverage
    Tool: Bash
    Preconditions: pytest-cov installed
    Steps:
      1. Run: python -m pytest tests/config/test_models.py --cov=madousho.config.models --cov-report=term-missing
      2. Verify: Coverage >= 90%
    Expected Result: Shows coverage percentage >= 90%
    Failure Indicators: Coverage < 90%
    Evidence: .sisyphus/evidence/task-7-model-coverage.txt
  ```

  **Evidence to Capture**:
  - [ ] pytest output showing all tests pass
  - [ ] Coverage report showing >= 90%

  **Commit**: YES (groups with 8, 9)
  - Message: `test(config): add test suite`
  - Files: `tests/config/test_models.py`
  - Pre-commit: `python -m pytest tests/config/test_models.py -v`

- [x] 8. Unit Tests for Config Loader

  **What to do**:
  - Create tests/config/test_loader.py
  - Test YAML file loading (valid file, missing file, malformed YAML)
  - Test environment variable override parsing
  - Test deep_merge function (nested dicts, lists, primitives)
  - Test load_config end-to-end with example config
  - Test error messages are clear and helpful
  - Achieve 90%+ coverage on loader.py

  **Must NOT do**:
  - Do not test model validation (Task 7)
  - Do not add integration tests (Task 9)
  - Do not test with real API keys

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Complex loader logic with multiple scenarios
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (after Task 6)
  - **Blocks**: Task 9
  - **Blocked By**: Task 5 (loader)

  **References**:
  - pytest tmp_path fixture: https://docs.pytest.org/en/latest/how-to/tmp_path.html
  - pytest monkeypatch: https://docs.pytest.org/en/latest/how-to/monkeypatch.html
  - config/madousho.example.yaml - test data

  **Acceptance Criteria**:
  - [ ] tests/config/test_loader.py exists with 15+ test functions
  - [ ] All tests pass with pytest
  - [ ] Coverage on loader.py >= 90%
  - [ ] Tests cover: YAML loading, env overrides, merge logic, error handling

  **QA Scenarios**:
  ```
  Scenario: Run loader tests
    Tool: Bash
    Preconditions: Tests written, config file exists
    Steps:
      1. Run: python -m pytest tests/config/test_loader.py -v
      2. Verify: All tests pass, 0 failures
    Expected Result: "passed" for all tests
    Failure Indicators: Any test failure
    Evidence: .sisyphus/evidence/task-8-loader-tests.txt

  Scenario: Verify loader test coverage
    Tool: Bash
    Preconditions: pytest-cov installed
    Steps:
      1. Run: python -m pytest tests/config/test_loader.py --cov=madousho.config.loader --cov-report=term-missing
      2. Verify: Coverage >= 90%
    Expected Result: Shows coverage >= 90%
    Failure Indicators: Coverage < 90%
    Evidence: .sisyphus/evidence/task-8-loader-coverage.txt

  Scenario: Test env override in isolation
    Tool: Bash
    Preconditions: Loader tests exist
    Steps:
      1. Run: MADOUSHO_API_PORT=7777 python -m pytest tests/config/test_loader.py::test_env_override -v
      2. Verify: Test passes with overridden value
    Expected Result: Test shows port 7777 used
    Failure Indicators: Test fails or wrong port
    Evidence: .sisyphus/evidence/task-8-env-test.txt
  ```

  **Evidence to Capture**:
  - [ ] pytest output
  - [ ] Coverage report
  - [ ] Env override test output

  **Commit**: YES (groups with 7, 9)
  - Message: `test(config): add test suite`
  - Files: `tests/config/test_loader.py`
  - Pre-commit: `python -m pytest tests/config/test_loader.py -v`

- [x] 9. Integration Tests + Coverage Verification

  **What to do**:
  - Create tests/config/test_integration.py
  - Test full config loading workflow with real config files
  - Test config/models + loader integration
  - Test cross-module behavior (models validate loader output)
  - Run full test suite with coverage on entire config module
  - Verify overall coverage >= 90%
  - Add pytest.ini coverage threshold configuration

  **Must NOT do**:
  - Do not add E2E tests beyond config module
  - Do not test unrelated modules
  - Do not add performance benchmarks yet

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Integration testing and coverage analysis
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (after Tasks 7, 8)
  - **Blocks**: Final Verification Wave
  - **Blocked By**: Tasks 7, 8 (unit tests)

  **References**:
  - pytest coverage: https://pytest-cov.readthedocs.io/
  - tests/config/test_models.py - test patterns
  - tests/config/test_loader.py - test patterns

  **Acceptance Criteria**:
  - [ ] tests/config/test_integration.py exists with 5+ integration tests
  - [ ] All integration tests pass
  - [ ] Full config module coverage >= 90%
  - [ ] pytest.ini has mincoverage = 90 configured
  - [ ] python -m pytest tests/ --cov=madousho.config passes

  **QA Scenarios**:
  ```
  Scenario: Run full test suite
    Tool: Bash
    Preconditions: All tests written
    Steps:
      1. Run: python -m pytest tests/ -v
      2. Verify: All tests pass (unit + integration)
    Expected Result: All tests pass, 0 failures
    Failure Indicators: Any test failure
    Evidence: .sisyphus/evidence/task-9-full-suite.txt

  Scenario: Verify total coverage
    Tool: Bash
    Preconditions: pytest-cov installed
    Steps:
      1. Run: python -m pytest tests/ --cov=madousho.config --cov-report=term-missing --cov-fail-under=90
      2. Verify: Exit code 0, coverage >= 90%
    Expected Result: Coverage report showing >= 90%, exit code 0
    Failure Indicators: Coverage < 90% or test failures
    Evidence: .sisyphus/evidence/task-9-total-coverage.txt

  Scenario: Integration test with real config
    Tool: Bash
    Preconditions: config/madousho.yaml exists
    Steps:
      1. Run: python -m pytest tests/config/test_integration.py::test_load_real_config -v
      2. Verify: Test loads actual config file successfully
    Expected Result: Test passes with real config values
    Failure Indicators: Test fails
    Evidence: .sisyphus/evidence/task-9-integration.txt
  ```

  **Evidence to Capture**:
  - [ ] Full test suite output
  - [ ] Coverage report with >= 90%
  - [ ] Integration test output

  **Commit**: YES (groups with 7, 8)
  - Message: `test(config): add test suite`
  - Files: `tests/config/test_integration.py`, `pytest.ini`
  - Pre-commit: `python -m pytest tests/ --cov=madousho.config --cov-fail-under=90`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)
> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run `tsc --noEmit` + linter + `bun test`. Review all changed files for: `as any`/`@ts-ignore`, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names (data/result/item/temp).
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high` (+ `playwright` skill if UI)
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration (features working together, not isolation). Test edge cases: empty state, invalid input, rapid actions. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination: Task N touching Task M's files. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **1**: `chore(python): init project structure` — pyproject.toml, requirements.txt, src/madousho/__init__.py
- **2**: `feat(config): add Pydantic models` — src/madousho/config/models.py
- **3**: `feat(config): implement loader` — src/madousho/config/loader.py
- **4**: `test(config): add test suite` — tests/config/*.py
- **5**: `chore(ci): finalize config module` — src/madousho/config/__init__.py

---

## Success Criteria

### Verification Commands
```bash
python -m pytest tests/ -v --cov=madousho.config --cov-report=term-missing  # Expected: 90%+ coverage, 0 failures
python -c "from madousho.config import load_config; cfg = load_config(); print(cfg.api.host)"  # Expected: 0.0.0.0
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass with 90%+ coverage
- [ ] Config loading <100ms startup time
