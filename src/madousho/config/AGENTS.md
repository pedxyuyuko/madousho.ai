# Config - Pydantic Models + YAML Loader

## OVERVIEW

Configuration system using Pydantic v2 models with YAML file loading and singleton caching.

## STRUCTURE

```
config/
├── __init__.py         # Exports: Config, ApiConfig, ProviderConfig, etc.
├── models.py           # Pydantic model definitions
└── loader.py           # YAML loading, file resolution, caching
```

## WHERE TO LOOK

| Component | File | Purpose |
|-----------|------|---------|
| Pydantic models | `models.py` | `Config`, `ApiConfig`, `ProviderConfig`, `SqliteConfig`, `DatabaseConfig` |
| File resolution | `loader.py` | `get_config_file()` - resolves `.yaml`/`.yml` extensions |
| Caching | `loader.py` | `_cached_config` global, `init_config()`, `get_config()` |
| Exports | `__init__.py` | `get_config`, `init_config` (no module-level singleton) |

## CONVENTIONS

- **Model hierarchy**: `Config` contains `ApiConfig`, `DatabaseConfig`, `Dict[str, ProviderConfig]`, `Dict[str, List[str]]` for model_groups
- **Field aliases**: Use `alias="api-key"` for YAML key with hyphen (Pydantic v2)
- **Default factories**: Use `Field(default_factory=ConfigClass)` for nested defaults
- **Config path resolution**: `.yaml` tried first, then `.yml`, then error
- **Environment override**: `MADOUSHO_CONFIG_PATH` env var sets config root directory
- **Lazy init**: `get_config()` calls `init_config()` if `_cached_config is None`
- **Auto token generation**: `ApiConfig.token` auto-generates 32-char hex token (128-bit) if empty, with WARNING log. Token is automatically saved to config file on `madousho serve` startup.
- **Config persistence**: Use `save_config()` to persist runtime changes (e.g., auto-generated token) to YAML file. Only modified fields are updated, preserving original formatting.

## CONFIGURATION EXAMPLE

```yaml
api:
  token: "test-token"
  host: "0.0.0.0"
  port: 8000

provider:
  openai:
    type: "openai-compatible"
    endpoint: "https://api.openai.com/v1"
    api-key: "sk-test"

default_model_group: "default"
model_groups:
  default:
    - "openai/gpt-4"
    - "openai/gpt-3.5-turbo"

database:
  url: "sqlite:///./data/madousho.db"
  sqlite:
    wal_enabled: true
    pool_size: 50
```

## ANTI-PATTERNS

- **DO NOT** access config dict keys directly - use Pydantic model attributes
- **DO NOT** call `init_config()` multiple times - use `get_config()` to access cached
- **DO NOT** hardcode config file paths - use `get_config_file()` for resolution
- **DO NOT** bypass validation - always use `Config.model_validate(data)` for new configs

## TESTING

Tests use `tempfile.TemporaryDirectory()` for isolated config files:
```python
with tempfile.TemporaryDirectory() as tmpdir:
    config_file = Path(tmpdir) / "test.yaml"
    config_file.write_text(yaml_content)
    os.environ["MADOUSHO_CONFIG_PATH"] = tmpdir
    config = init_config()
```

See: `tests/test_config.py` for comprehensive test patterns.
