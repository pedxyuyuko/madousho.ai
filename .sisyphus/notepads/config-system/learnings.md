## Task 2: Pydantic Models Creation

### Key Learnings

1. **YAML to Pydantic Field Aliases**: The YAML uses `api-key` (hyphenated) but Pydantic field names should use underscores (`api_key`). Use `Field(alias="api-key")` to handle the conversion automatically during YAML parsing.

2. **Pydantic v2 Syntax**: 
   - No inner `class Config` needed
   - Use `Field()` for all field metadata (defaults, descriptions, aliases)
   - `default_factory=list` for mutable defaults

3. **Model Structure**:
   - `ApiConfig`: Simple flat config with token, host, port
   - `ProviderConfig`: Dict-keyed by provider name, uses alias for api-key
   - `ModelGroupConfig`: Wrapper around List[str] for model groups
   - `Config`: Root model composing all sub-configs

### Files Created
- `src/madousho/config/models.py` - 4 Pydantic models matching YAML structure

## Task 3: Configuration Loader Implementation

### Key Learnings

1. **Lazy Initialization for Module-Level Singleton**: When creating a module-level singleton instance (`config: Config = get_config()`), the `get_config()` function must handle lazy initialization. If it raises an error when `_cached_config is None`, the module import will fail. Solution: `get_config()` should auto-call `init_config()` when cache is empty.

2. **Global Variable Singleton Pattern**:
   ```python
   _cached_config: Config | None = None
   
   def get_config() -> Config:
       global _cached_config
       if _cached_config is None:
           _cached_config = init_config()
       return _cached_config
   
   config: Config = get_config()  # Safe: lazy initialization
   ```

3. **Path Resolution Strategy**:
   - Use `os.path.isabs()` to detect absolute paths
   - `MADOUSHO_CONFIG_PATH` env var as base directory (default: "config")
   - Try `.yaml` first, then `.yml` for extension fallback
   - Default filename is "madousho" when filepath is None

4. **YAML Alias Handling**: Pydantic's `Field(alias="api-key")` automatically handles YAML keys with hyphens (`api-key`) mapping to Python field names with underscores (`api_key`).

### Files Created
- `src/madousho/config/loader.py` - Config loading with singleton pattern
- `src/madousho/config/__init__.py` - Module exports

### Verified Behaviors
- `from madousho.config import config` returns Config instance (auto-initialized)
- `config is get_config()` - Singleton verified
- `config.api.port` returns int (8000 default)
- `init_config("/absolute/path")` loads from absolute path
- `init_config("relative")` loads from MADOUSHO_CONFIG_PATH/relative.yaml
- `.yml` fallback works when `.yaml` doesn't exist

## Fix: ModelGroupConfig Removed

### Issue
The original design used `ModelGroupConfig` as a wrapper class for model groups, but the actual YAML structure shows model_groups is a simple `Dict[str, List[str]]`:

```yaml
model_groups:
  example_group:
    - "example_provider/gpt-5.2"
    - "example_provider/fallback1"
```

### Changes Made
1. Removed `ModelGroupConfig` class from `models.py`
2. Changed `Config.model_groups` type from `Dict[str, ModelGroupConfig]` to `Dict[str, List[str]]`
3. Removed `ModelGroupConfig` from `__init__.py` exports

### Files Modified
- `src/madousho/config/models.py` - Removed ModelGroupConfig, updated model_groups type
- `src/madousho/config/__init__.py` - Removed ModelGroupConfig export

### Verified
- ✅ `model_groups['default']` returns `List[str]` directly
- ✅ YAML structure `Dict[str, List[str]]` correctly parsed
- ✅ `ModelGroupConfig` no longer exported (ImportError as expected)
- ✅ All syntax checks pass
