# Configuration System

**Location:** `src/madousho/config/`

## OVERVIEW

Pydantic v2-based configuration with YAML loading, hyphen-to-underscore normalization, singleton ConfigManager, and optional typehint validation for flow plugins.

## STRUCTURE

```
config/
├── models.py            # Pydantic v2 models (Config, APIConfig, ProviderConfig)
├── loader.py            # ConfigManager singleton, YAML loading, normalization
├── typehint_models.py   # TypeHintDefinition, TypeHintValidator for flow configs
└── __init__.py
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Main config model | `models.py` | Config, APIConfig, ProviderConfig (Pydantic v2) |
| Config loader | `loader.py` | ConfigManager singleton, load_yaml, normalize_keys |
| Typehint validation | `typehint_models.py` | TypeHintDefinition, TypeHintValidator, TypeHintType enum |
| Global config access | `loader.py:get_config()` | Get singleton config instance |
| Config initialization | `loader.py:init_config()` | Initialize ConfigManager with config_dir |

## CONVENTIONS

- **Pydantic v2 syntax**: Use `model_validate()`, `model_dump()` (NOT v1 `.dict()`, `.parse_obj()`)
- **Extra fields forbidden**: All models use `extra="forbid"` (unknown fields rejected)
- **Hyphen-to-underscore normalization**: YAML keys auto-converted recursively (`default-model-group` → `default_model_group`)
- **Singleton pattern**: ConfigManager uses class-level `_instance` with get_instance() accessor
- **Field validators**: Use `@field_validator` decorator (Pydantic v2, NOT `@validator`)
- **Type hints required**: All functions and methods have full type annotations
- **Config reset for testing**: `ConfigManager.reset_instance()` for test isolation

## ANTI-PATTERNS (THIS MODULE)

- DO NOT use Pydantic v1 methods (`.dict()`, `.parse_obj()`, `@validator`)
- DO NOT add extra fields to config models (rejected by `extra="forbid"`)
- DO NOT skip type hints on functions or method parameters
- DO NOT access config directly (use `get_config()` or `ConfigManager.get_instance()`)
- DO NOT modify singleton pattern (thread safety depends on get_instance logic)
- DO NOT bypass normalization (hyphenated YAML keys must convert to underscores)
- DO NOT use `@validator` decorator (Pydantic v2 uses `@field_validator`)

## UNIQUE PATTERNS

- **Recursive key normalization**: `normalize_keys()` converts hyphens to underscores at all nesting levels
- **Typehint validation**: Optional `config.typehint.yaml` for flow plugins to validate against global config
- **MODEL_GROUP type**: Special type that validates against global `model_groups` or falls back to `default_model_group`
- **Field path syntax**: Typehint uses `.path.to.field` format for nested field validation
- **Config reset for tests**: `reset_instance()` class method for test isolation (singleton pattern)

## KEY CLASSES

### Config (models.py)

Main application configuration:
```python
class Config(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    api: APIConfig
    provider: Dict[str, ProviderConfig]
    default_model_group: str
    model_groups: Dict[str, List[str]]
```

### APIConfig (models.py)

API server configuration:
```python
class APIConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    host: str
    port: int  # Validated: 1-65535
    token: Optional[str] = None
```

### ProviderConfig (models.py)

LLM provider configuration:
```python
class ProviderConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    type: str
    endpoint: str
    api_key: str
```

### ConfigManager (loader.py)

Singleton configuration manager:
- `get_instance(config_dir)` - Get or create singleton instance
- `reset_instance()` - Reset singleton (for testing)
- `config` property - Lazy load config on first access
- `_find_config_file()` - Search for madousho.yaml or config.yaml

### TypeHintDefinition (typehint_models.py)

Typehint definition for flow configs:
```python
class TypeHintDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    field_typehint: Dict[str, str]  # field_path -> type mapping
```

Supported types: `MODEL_GROUP`, `STRING`, `INTEGER`, `BOOLEAN`, `LIST`, `DICT`

### TypeHintValidator (typehint_models.py)

Validates flow config against typehint definition:
- `validate()` - Run validation, returns bool
- `get_errors()` - Get list of error messages
- `get_warnings()` - Get list of warning messages
- Supports global config references (for MODEL_GROUP validation)

## CONFIG FILE FORMAT

Example `madousho.yaml`:
```yaml
api:
  token: ""  # Empty = auto-generate
  host: "0.0.0.0"
  port: 8000

provider:
  my_provider:
    type: "openai-compatible"
    endpoint: "https://api.example.com/v1"
    api-key: "sk-xxxxyourapi"  # Hyphenated keys auto-converted

default_model_group: "default"
model_groups:
  default:
    - "my_provider/gpt-4"
    - "my_provider/fallback1"
  fast:
    - "my_provider/haiku"
```

## FLOW PLUGIN CONFIG

Flow plugins have their own `config.yaml`:
```yaml
name: "my_flow"
model_group: "default"  # Validated against global model_groups
max_retries: 3
timeout: 30.0
```

Optional `config.typehint.yaml` for validation:
```yaml
field_typehint:
  .model_group: "MODEL_GROUP"  # Validates against global config
  .max_retries: "INTEGER"
  .timeout: "INTEGER"
  .name: "STRING"
```

## TESTING

Tests in `tests/config/`:
- `test_models.py` - Pydantic model validation tests (valid/invalid configs)
- `test_loader.py` - ConfigManager singleton, YAML loading, normalization tests
- `test_typehint_models.py` - TypeHintDefinition and TypeHintValidator tests
- `test_integration.py` - End-to-end config loading tests

Test patterns:
- `pytest.raises(ValidationError)` for negative tests
- Direct model instantiation for validation tests
- `ConfigManager.reset_instance()` for test isolation
