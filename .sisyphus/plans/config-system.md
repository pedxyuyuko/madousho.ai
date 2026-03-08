# Config System Implementation with Pydantic

## TL;DR

> **Quick Summary**: Create a Pydantic v2-based configuration system for madousho.ai that loads YAML configs with flexible path handling (via `MADOUSHO_CONFIG_PATH` base directory + filepath argument), provides type-safe validation, and exposes a global singleton instance. The loader tries `.yaml` first, then `.yml`. Supports relative paths, absolute paths, and paths with or without extensions. **Note**: Environment variables are ONLY used for base directory path, NOT for overriding individual config values.
> 
> **Deliverables**:
> - `src/madousho/config/__init__.py` - Config package with global instance
> - `src/madousho/config/models.py` - Pydantic models matching YAML structure
> - `src/madousho/config/loader.py` - YAML loading logic with flexible path support (relative/absolute, .yaml/.yml, with/without extension)
> - Updated `pyproject.toml` - Add `pydantic-settings` and `pyyaml` dependencies
> 
> **Estimated Effort**: Short
> **Parallel Execution**: NO - sequential (3 tasks)
> **Critical Path**: Task 1 → Task 2 → Task 3

---

## Context

### Original Request
读取 `config/madousho.example.yaml` 创建 `src/config/` 包，使用 Pydantic 来验证配置，创建全局配置实例，一次 init 所有地方都可以 load 这个 config 而不需要重新传入路径。

### Updated Requirements
- **Code Language**: All code in English (comments, docstrings, identifiers)
- **Environment Variables**: ONLY `MADOUSHO_CONFIG_PATH` for custom config directory path (not file path)
- **File Extension**: Supports both `.yaml` and `.yml` (tries `.yaml` first, then `.yml`)
- **NO Value Override**: Individual config values CANNOT be overridden by environment variables

### Interview Summary
**Key Discussions**:
- **Config Structure**: Match existing `madousho.example.yaml` structure (api, provider, model_groups)
- **Singleton Pattern**: Module-level global variable (`_cached_config`), NOT `@lru_cache()`
- **Config API**: `init_config(filepath)` for loading, `get_config()` (no params) for access
- **Extension Fallback**: Try `.yaml` first, then `.yml`

---

## Work Objectives

### Core Objective
Build a type-safe, validated configuration system that loads from YAML files with a customizable path and provides a global singleton instance.

### Concrete Deliverables
- `src/madousho/config/__init__.py` - Package root exposing `config` and `get_config()`
- `src/madousho/config/models.py` - Pydantic models: `ApiConfig`, `ProviderConfig`, `ModelGroupConfig`, `Config`
- `src/madousho/config/loader.py` - YAML loader with custom path support via `MADOUSHO_CONFIG_PATH`
- `pyproject.toml` - Add `pydantic>=2.0`, `pydantic-settings>=2.0`, `pyyaml>=6.0`

### Definition of Done
- [x] `from madousho.config import config` works from anywhere in the project
- [x] `config.api.token` returns validated value from YAML file
- [x] `MADOUSHO_CONFIG_PATH=/path/to/custom python app.py` loads custom config from directory
- [x] Invalid config (wrong type) raises `pydantic.ValidationError`
- [x] All code comments and docstrings in English

### Must Have
- Pydantic v2 validation on all config fields
- Custom config directory path via `MADOUSHO_CONFIG_PATH` environment variable (tries madousho.yaml, then madousho.yml)
- Global singleton instance accessible via `from madousho.config import config`
- Nested model structure matching YAML (api, provider, model_groups)
- All code in English

### Must NOT Have (Guardrails)
- **NO** environment variable override for individual config values (e.g., `MADOUSHO_API__TOKEN`)
- **NO** CLI commands for config management (out of scope)
- **NO** `@lru_cache()` decorator - use simple global variable caching
- **NO** Chinese comments or docstrings in code

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO (minimal project)
- **Automated tests**: NO (user did not request tests)
- **Framework**: None for this task
- **Agent-Executed QA**: YES (mandatory for all tasks)

### QA Policy
Every task MUST include agent-executed QA scenarios:
- **Import Test**: Verify `from madousho.config import config` works
- **Value Test**: Verify config values match YAML
- **Custom Path Test**: Verify `MADOUSHO_CONFIG_PATH` loads from directory with .yaml/.yml fallback
- **Validation Test**: Verify invalid config raises ValidationError

---

## Execution Strategy

### Sequential Execution (3 tasks)

```
Wave 1 (Start Immediately):
├── Task 1: Add dependencies to pyproject.toml [quick]
├── Task 2: Create Pydantic models in src/madousho/config/models.py [unspecified-high]
└── Task 3: Create loader + global instance in src/madousho/config/loader.py [unspecified-high]

Critical Path: Task 1 → Task 2 → Task 3
Parallel Speedup: N/A (sequential - each task depends on previous)
```

### Dependency Matrix
- **1**: — — 2
- **2**: 1 — 3
- **3**: 2 — verification

### Agent Dispatch Summary
- **Wave 1**: **3** — T1 → `quick`, T2 → `unspecified-high`, T3 → `unspecified-high`

---

## TODOs

- [x] 1. Add Pydantic dependencies to pyproject.toml

  **What to do**:
  - Add `pydantic>=2.0` to project dependencies
  - Add `pydantic-settings>=2.0` to project dependencies (for Pydantic integration)
  - Add `pyyaml>=6.0` to project dependencies (for YAML file parsing)
  - Run `pip install -e ".[dev]"` to install new dependencies

  **Must NOT do**:
  - Do NOT modify any other sections of pyproject.toml
  - Do NOT add test dependencies unless explicitly requested

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: Simple file edit, no complex logic

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (first task)
  - **Blocks**: Task 2, Task 3
  - **Blocked By**: None

  **References**:
  - `pyproject.toml:48-55` - Current dependencies section structure
  - Official docs: `https://docs.pydantic.dev/latest/` - Pydantic v2 documentation

  **Acceptance Criteria**:
  - [x] `pyproject.toml` contains `pydantic>=2.0` in dependencies
  - [x] `pyproject.toml` contains `pydantic-settings>=2.0` in dependencies
  - [x] `pyproject.toml` contains `pyyaml>=6.0` in dependencies

  **QA Scenarios**:

  ```
  Scenario: Verify dependencies install correctly
    Tool: Bash
    Preconditions: In project root directory
    Steps:
      1. Run: pip install -e ".[dev]"
      2. Run: python -c "import pydantic; print(pydantic.__version__)"
      3. Run: python -c "import pydantic_settings; print('pydantic-settings OK')"
      4. Run: python -c "import yaml; print('pyyaml OK')"
    Expected Result: All imports succeed, pydantic version starts with "2."
    Failure Indicators: ImportError or version starts with "1."
    Evidence: .sisyphus/evidence/task-1-deps-install.txt
  ```

  **Commit**: YES (groups with 1)
  - Message: `chore(deps): add pydantic v2, pydantic-settings, and pyyaml dependencies`
  - Files: `pyproject.toml`
  - Pre-commit: `pip install -e ".[dev]"`

---

- [x] 2. Create Pydantic models matching YAML structure

  **What to do**:
  - Create `src/madousho/config/` directory
  - Create `src/madousho/config/models.py` with the following models (ALL IN ENGLISH):
  
  ```python
  """Configuration models for Madousho.ai."""
  
  from pydantic import BaseModel, Field
  from typing import Dict, List
  
  
  class ApiConfig(BaseModel):
      """API server configuration."""
      token: str = Field(default="", description="API authentication token")
      host: str = Field(default="0.0.0.0", description="Server host")
      port: int = Field(default=8000, description="Server port")
  
  
  class ProviderConfig(BaseModel):
      """Single provider configuration."""
      type: str = Field(default="openai-compatible", description="Provider type")
      endpoint: str = Field(default="", description="API endpoint URL")
      api_key: str = Field(default="", description="API key")
  
  
  class ModelGroupConfig(BaseModel):
      """Model group with fallback chain."""
      models: List[str] = Field(default_factory=list, description="List of model identifiers")
  
  
  class Config(BaseModel):
      """Root configuration model."""
      api: ApiConfig = Field(default_factory=ApiConfig, description="API server settings")
      provider: Dict[str, ProviderConfig] = Field(
          default_factory=dict, 
          description="Provider configurations keyed by name"
      )
      default_model_group: str = Field(default="", description="Default model group name")
      model_groups: Dict[str, ModelGroupConfig] = Field(
          default_factory=dict, 
          description="Model groups keyed by name"
      )
  ```

  **Must NOT do**:
  - Do NOT include loading logic in this file (that's Task 3)
  - Do NOT add methods beyond what's needed for validation
  - Do NOT use Pydantic v1 syntax (no `class Config` inner class, use `model_config` if needed)
  - Do NOT write comments or docstrings in Chinese

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: Requires understanding Pydantic v2 syntax and YAML structure mapping

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (depends on Task 1)
  - **Blocks**: Task 3
  - **Blocked By**: Task 1

  **References**:
  - `config/madousho.example.yaml:1-22` - Source YAML structure to match
  - Official docs: `https://docs.pydantic.dev/latest/concepts/models/` - Pydantic v2 model syntax
  - Official docs: `https://docs.pydantic.dev/latest/concepts/fields/` - Field usage

  **Acceptance Criteria**:
  - [x] `src/madousho/config/models.py` exists with all 4 models
  - [x] `ApiConfig` has `token`, `host`, `port` fields with correct types
  - [x] `ProviderConfig` has `type`, `endpoint`, `api_key` fields
  - [x] `ModelGroupConfig` has `models` field as List[str]
  - [x] `Config` has `api`, `provider`, `default_model_group`, `model_groups` fields
  - [x] All fields have `Field()` with `default` or `default_factory`
  - [x] All comments and docstrings are in English
  - [x] Python syntax is valid: `python -m py_compile src/madousho/config/models.py` succeeds

  **QA Scenarios**:

  ```
  Scenario: Verify models can be instantiated with valid data
    Tool: Bash
    Preconditions: models.py exists
    Steps:
      1. Run: python -c "
        from madousho.config.models import Config, ApiConfig, ProviderConfig, ModelGroupConfig
        config = Config(
            api=ApiConfig(token='test', host='localhost', port=8080),
            provider={'example': ProviderConfig(type='openai', endpoint='https://api.example.com', api_key='sk-test')},
            default_model_group='example_group',
            model_groups={'example_group': ModelGroupConfig(models=['example_provider/gpt-5.2'])}
        )
        print(f'API token: {config.api.token}')
        print(f'Provider count: {len(config.provider)}')
        print(f'Model groups: {list(config.model_groups.keys())}')
      "
    Expected Result: Prints API token, provider count (1), and model group name
    Failure Indicators: ImportError, ValidationError, or AttributeError
    Evidence: .sisyphus/evidence/task-2-models-valid.txt

  Scenario: Verify type validation rejects invalid data
    Tool: Bash
    Preconditions: models.py exists
    Steps:
      1. Run: python -c "
        from madousho.config.models import ApiConfig
        try:
            config = ApiConfig(port='not-a-number')
            print('ERROR: Should have raised ValidationError')
        except Exception as e:
            print(f'Correctly raised: {type(e).__name__}')
      "
    Expected Result: Raises ValidationError (or ValueError) for invalid port type
    Failure Indicators: No exception raised, or wrong exception type
    Evidence: .sisyphus/evidence/task-2-validation.txt

  Scenario: Verify all docstrings are in English
    Tool: Bash
    Preconditions: models.py exists
    Steps:
      1. Run: python -c "
        import re
        with open('src/madousho/config/models.py', 'r') as f:
            content = f.read()
        # Check for common Chinese characters
        chinese_chars = re.findall(r'[\\u4e00-\\u9fff]', content)
        if chinese_chars:
            print(f'ERROR: Found {len(chinese_chars)} Chinese characters')
        else:
            print('SUCCESS: No Chinese characters found')
      "
    Expected Result: No Chinese characters in the file
    Failure Indicators: Any Chinese Unicode characters detected
    Evidence: .sisyphus/evidence/task-2-english-only.txt
  ```

  **Commit**: NO (groups with 3)

---

- [x] 3. Create loader and global singleton instance

  **What to do**:
  - Create `src/madousho/config/loader.py` with custom YAML loader:
  
  ```python
  """Configuration loader for Madousho.ai."""
  
  import os
  # Global cache
  _cached_config: Config | None = None
  
  
  def get_config_file(filepath: str | None = None) -> Path:
      """
      Get the configuration file path.
      
      Args:
          filepath: Optional relative or absolute path to config file (without extension
                    or with .yaml/.yml). If None, uses default 'madousho'.
      
      Returns:
          Path to the configuration file.
          
      Notes:
          - Uses MADOUSHO_CONFIG_PATH environment variable as base directory
          - If filepath is absolute, uses it directly
          - Tries .yaml first, then .yml
          - Default filename is 'madousho' if filepath is None
      """
      base_dir = os.environ.get("MADOUSHO_CONFIG_PATH", "config")
      
      if filepath is None:
          filepath = "madousho"
      
      path = Path(filepath)
      
      # If absolute path, use directly
      if path.is_absolute():
          config_path = path
      else:
          # Relative path - join with base_dir
          config_path = Path(base_dir) / filepath
      
      # Remove existing extension if present
      if config_path.suffix in ['.yaml', '.yml']:
          base_path = config_path.with_suffix('')
      else:
          base_path = config_path
      
      # Try .yaml first, then .yml
      yaml_path = base_path.with_suffix('.yaml')
      yml_path = base_path.with_suffix('.yml')
      
      if yaml_path.exists():
          return yaml_path
      if yml_path.exists():
          return yml_path
      
      # Return .yaml path (will raise FileNotFoundError if not exists)
      return yaml_path
  
  
  def _load_from_file(config_path: Path) -> Config:
      """
      Load and validate config from YAML file.
      
      Args:
          config_path: Path to the YAML file.
      
      Returns:
          Validated Config object.
          
      Raises:
          FileNotFoundError: If config file does not exist.
          ValidationError: If config validation fails.
      """
      if not config_path.exists():
          raise FileNotFoundError(f"Config file not found: {config_path}")
      
      with open(config_path, "r", encoding="utf-8") as f:
          config_data = yaml.safe_load(f)
      
      # Handle empty YAML file
      if config_data is None:
          config_data = {}
      
      return Config.model_validate(config_data)
  
  
  def init_config(filepath: str | None = None) -> Config:
      """
      Initialize configuration from YAML file.
      
      Args:
          filepath: Optional path to config file (relative to MADOUSHO_CONFIG_PATH
                    or absolute). Can include .yaml/.yml extension or not.
                    If None, uses default 'madousho'.
      
      Returns:
          Validated Config object.
          
      Raises:
          FileNotFoundError: If config file does not exist.
          ValidationError: If config validation fails.
          
      Notes:
          This function updates the global cached config. Subsequent
          calls to get_config() will return this new instance.
      """
      global _cached_config
      config_path = get_config_file(filepath)
      _cached_config = _load_from_file(config_path)
      return _cached_config
  
  
def get_config() -> Config:
    """
    Get the cached config instance (no parameters).
    
    Returns:
        Config object. Returns same instance on repeated calls.
        
    Notes:
        Returns the config instance from the most recent init_config() call.
        If init_config() has not been called, loads default config.
    """
      global _cached_config
      if _cached_config is None:
          # First call - load default
          _cached_config = _load_from_file(get_config_file(None))
      return _cached_config
  
  
  # Global singleton instance - created on first import
  config: Config = get_config()

  ```
  
  - Create `src/madousho/config/__init__.py`:
  
  ```python
  """Configuration module for Madousho.ai."""
  
  from .loader import config, get_config, init_config
  from .models import Config, ApiConfig, ProviderConfig, ModelGroupConfig
  
  __all__ = [
      "config",
      "get_config",
      "init_config",
      "Config",
      "ApiConfig",
      "ProviderConfig",
      "ModelGroupConfig",
  ]
  ```

  **Must NOT do**:
  - Do NOT support environment variable override for individual config values
  - Do NOT require passing config path - use default or `MADOUSHO_CONFIG_PATH` env var
  - Do NOT use `@lru_cache()` - use simple global variable
  - Do NOT expose internal implementation details in `__all__`
  - Do NOT write comments or docstrings in Chinese

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: Requires understanding YAML loading, singleton pattern, and environment variable handling

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (depends on Task 2)
  - **Blocks**: None (final implementation task)
  - **Blocked By**: Task 2

  **References**:
  - `src/madousho/__init__.py:1` - Existing package `__init__.py` pattern
  - Official docs: `https://docs.pydantic.dev/latest/concepts/models/#validation` - `model_validate()` usage
  - Official docs: `https://pyyaml.org/wiki/PyYAMLDocumentation` - YAML loading with PyYAML
  - Official docs: `https://pyyaml.org/wiki/PyYAMLDocumentation` - YAML loading with PyYAML

  **Acceptance Criteria**:
  - [x] `src/madousho/config/__init__.py` exists with all exports
  - [x] `src/madousho/config/loader.py` exists with `get_config_file()`, `_load_from_file()`, `init_config()`, `get_config()`
  - [x] `from madousho.config import config` returns a Config instance
  - [x] `from madousho.config import get_config` returns same instance as `config`
  - [x] `config.api.port` returns integer from YAML (default 8000)
  - [x] `init_config("relative/path")` loads from MADOUSHO_CONFIG_PATH/relative/path.yaml
  - [x] `init_config("/absolute/path")` loads from /absolute/path.yaml
  - [x] All comments and docstrings are in English


  **QA Scenarios**:

  ```
  Scenario: Verify global config instance works from anywhere
    Tool: Bash
    Preconditions: All config files created, dependencies installed
    Steps:
      1. Run: python -c "
        from madousho.config import config
        print(f'Config type: {type(config).__name__}')
        print(f'API host: {config.api.host}')
        print(f'API port: {config.api.port}')
        print(f'Default model group: {config.default_model_group}')
      "
    Expected Result: Prints config values matching config/madousho.yaml
    Failure Indicators: ImportError, AttributeError, or wrong values
    Evidence: .sisyphus/evidence/task-3-global-config.txt

  Scenario: Verify custom config path via environment variable (directory path)
    Tool: Bash
    Preconditions: All config files created
    Steps:
      1. Create test directory and config: mkdir -p /tmp/madousho_config
      2. Create config: echo 'api:\n  port: 9999' > /tmp/madousho_config/madousho.yaml
      3. Run: MADOUSHO_CONFIG_PATH=/tmp/madousho_config python -c "
        from madousho.config import config
        print(f'Port: {config.api.port}')
        assert config.api.port == 9999, 'Custom config not loaded'
        print('SUCCESS: Custom config directory works')
      "
    Expected Result: Port is 9999 from custom config directory (loads madousho.yaml)
    Failure Indicators: Port is 8000 (from default config) or error
    Evidence: .sisyphus/evidence/task-3-custom-path.txt
  Scenario: Verify init_config with relative path (no extension)
    Tool: Bash
    Preconditions: All config files created, dependencies installed
    Steps:
      1. Create test directory: mkdir -p /tmp/cfg_test/sub
      2. Create config: echo 'api:\n  port: 1111' > /tmp/cfg_test/sub/myconfig.yaml
      3. Run: MADOUSHO_CONFIG_PATH=/tmp/cfg_test python -c "
        from madousho.config import init_config
        cfg = init_config('sub/myconfig')
        print(f'Port: {cfg.api.port}')
        assert cfg.api.port == 1111, 'Relative path config not loaded'
        print('SUCCESS: Relative path without extension works')
      "
    Expected Result: Port is 1111 from sub/myconfig.yaml
    Failure Indicators: FileNotFoundError or wrong port value
    Evidence: .sisyphus/evidence/task-3-relative-path.txt

  Scenario: Verify init_config with absolute path (no extension)
    Tool: Bash
    Preconditions: All config files created
    Steps:
      1. Create test directory: mkdir -p /tmp/abs_cfg
      2. Create config: echo 'api:\n  port: 2222' > /tmp/abs_cfg/prod.yaml
      3. Run: python -c "
        from madousho.config import init_config
        cfg = init_config('/tmp/abs_cfg/prod')
        print(f'Port: {cfg.api.port}')
        assert cfg.api.port == 2222, 'Absolute path config not loaded'
        print('SUCCESS: Absolute path works')
      "
    Expected Result: Port is 2222 from /tmp/abs_cfg/prod.yaml
    Failure Indicators: FileNotFoundError or wrong port value
    Evidence: .sisyphus/evidence/task-3-absolute-path.txt

  Scenario: Verify singleton pattern (same instance)



  Scenario: Verify singleton pattern (same instance)
    Tool: Bash
    Preconditions: All config files created
    Steps:
      1. Run: python -c "
        from madousho.config import config, get_config
        config1 = get_config()
        config2 = get_config()
        config3 = config
        print(f'config1 is config2: {config1 is config2}')
        print(f'config1 is config3: {config1 is config3}')
        assert config1 is config2, 'get_config() should return same instance'
        assert config1 is config3, 'Global config should be same as get_config()'
        print('SUCCESS: Singleton pattern verified')
      "
    Expected Result: All references point to same instance (is returns True)
    Failure Indicators: Different instances created
    Evidence: .sisyphus/evidence/task-3-singleton.txt

  Scenario: Verify missing config file raises FileNotFoundError
    Tool: Bash
    Preconditions: All config files created
    Steps:
      1. Run: MADOUSHO_CONFIG_PATH=/nonexistent_dir python -c "
        from madousho.config import config
      " 2>&1 || echo "Error caught (expected)"
    Expected Result: Raises FileNotFoundError
    Failure Indicators: No error or different error type
    Evidence: .sisyphus/evidence/task-3-missing-file.txt


  Scenario: Verify all docstrings are in English
    Tool: Bash
    Preconditions: loader.py and __init__.py exist
    Steps:
      1. Run: python -c "
        import re
        for file in ['src/madousho/config/loader.py', 'src/madousho/config/__init__.py']:
            with open(file, 'r') as f:
                content = f.read()
            chinese_chars = re.findall(r'[\\u4e00-\\u9fff]', content)
            if chinese_chars:
                print(f'ERROR in {file}: Found {len(chinese_chars)} Chinese characters')
                exit(1)
        print('SUCCESS: All files are English-only')
      "
    Expected Result: No Chinese characters in any file
    Failure Indicators: Any Chinese Unicode characters detected
    Evidence: .sisyphus/evidence/task-3-english-only.txt
  ```

  **Commit**: YES (groups 2, 3)
  - Message: `feat(config): add Pydantic-based config system with singleton pattern`
  - Files: `src/madousho/config/__init__.py`, `src/madousho/config/models.py`, `src/madousho/config/loader.py`
  - Pre-commit: `python -m py_compile src/madousho/config/*.py`

---

## Final Verification Wave

- [x] F1. **Import Test** — `quick`
  Run `python -c "from madousho.config import config, get_config, init_config, Config, ApiConfig"` from project root.
  Verify no ImportError and all exports are accessible.
  Output: `Imports [N/N] | VERDICT: PASS/FAIL`

- [x] F2. **Value Verification** — `quick`
  Run `python -c "from madousho.config import config; print(config.api.port, config.default_model_group)"`.
  Verify values match `config/madousho.example.yaml` (port=8000, default_model_group="example_group").
  Output: `Values [N/N match] | VERDICT: PASS/FAIL`

- [x] F3. **Custom Path Test** — `quick`
  Create temp directory with config, run `MADOUSHO_CONFIG_PATH=/tmp/testdir python -c "from madousho.config import config; print(config.api.port)"`.
  Verify output matches custom config value (tries madousho.yaml, then madousho.yml).
  Output: `Custom Path [PASS/FAIL] | VERDICT: PASS/FAIL`


- [x] F4. **English-Only Check** — `quick`
  Run script to check all config files for Chinese characters.
  Verify zero Chinese Unicode characters found.
  Output: `Chinese Chars [0 found] | VERDICT: PASS/FAIL`

---

## Commit Strategy

- **1**: `chore(deps): add pydantic v2, pydantic-settings, and pyyaml dependencies` — pyproject.toml, `pip install -e ".[dev]"`
- **2, 3**: `feat(config): add Pydantic-based config system with singleton pattern` — src/madousho/config/*.py, `python -m py_compile src/madousho/config/*.py`

---

## Success Criteria

### Verification Commands
```bash
# 1. Dependencies installed
python -c "import pydantic, pydantic_settings, yaml; print('All deps OK')"

# 2. Import works
python -c "from madousho.config import config; print('Import OK')"

# 4. Custom config directory works (tries .yaml then .yml)
mkdir -p /tmp/custom_config
cp config/madousho.example.yaml /tmp/custom_config/madousho.yaml
MADOUSHO_CONFIG_PATH=/tmp/custom_config python -c "from madousho.config import config; print('Custom dir OK')"

# 4b. Custom config directory with .yml fallback
mkdir -p /tmp/custom_config_yml
cp config/madousho.example.yaml /tmp/custom_config_yml/madousho.yml
MADOUSHO_CONFIG_PATH=/tmp/custom_config_yml python -c "from madousho.config import config; print('YML fallback OK')"
python -c "from madousho.config import config; assert config.api.port == 8000; print('YAML load OK')"

# 4b. Custom config file path works
cp config/madousho.example.yaml /tmp/custom.yaml
python -c "from madousho.config import init_config; cfg = init_config('/tmp/custom'); print('Custom path OK')"

# 5. Singleton pattern
python -c "from madousho.config import config, get_config; assert config is get_config(); print('Singleton OK')"

# 6. English-only code
python -c "
import re
for f in ['src/madousho/config/loader.py', 'src/madousho/config/models.py', 'src/madousho/config/__init__.py']:
    if re.findall(r'[\u4e00-\u9fff]', open(f).read()):
        print(f'FAIL: Chinese chars in {f}'); exit(1)
print('English-only OK')
"
```

### Final Checklist
- [x] All "Must Have" present (Pydantic validation, custom path, singleton, nested models, English code)
- [x] All "Must NOT Have" absent (no value override, no CLI, no dynamic reload, no Chinese)
- [x] All QA scenarios pass (import, values, custom path, singleton, English-only)
