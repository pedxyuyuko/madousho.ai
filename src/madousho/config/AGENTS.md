# src/madousho/config/ KNOWLEDGE BASE

**Generated:** 2026-03-03
**Commit:** 3b8ad40
**Branch:** master

## OVERVIEW

Configuration system with Pydantic v2 models, YAML loading, and environment variable overrides.

## STRUCTURE

```
config/
├── models.py           # Pydantic models (APIConfig, ProviderConfig, Config)
├── loader.py           # YAML loader with env var overrides (145 lines)
├── typehint_models.py  # Type-hinted model variants (169 lines)
└── __init__.py         # Package exports
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Config models | `models.py:6-40` | `APIConfig`, `ProviderConfig`, `Config` |
| Port validation | `models.py:15-20` | `validate_port` validator |
| YAML loading | `loader.py:22-46` | `load_yaml()` function |
| Env overrides | `loader.py:48-92` | `get_env_overrides()` with `MADOUSHO_*` prefix |
| Deep merge | `loader.py:95-113` | `deep_merge()` for nested overrides |
| Main loader | `loader.py:116-145` | `load_config()` - validate + return Config |
| Type hints | `typehint_models.py` | Enhanced type-hinted variants |

## CONVENTIONS

- **Model naming**: `{Scope}Config` (e.g., `APIConfig`, `ProviderConfig`)
- **Validation**: Use `@field_validator` decorator (Pydantic v2)
- **Config dict**: Always `ConfigDict(extra="forbid")` for strict validation
- **Key normalization**: Hyphens in YAML auto-converted to underscores
- **Pydantic v2**: Use `model_validate()`, `model_dump()` (NOT v1 methods)

## ANTI-PATTERNS (THIS MODULE)

- DO NOT use Pydantic v1 syntax (`.dict()`, `.parse_obj()`)
- DO NOT use `model_dump()` before validation completes
- DO NOT add fields to models without updating loader tests
- DO NOT bypass `normalize_keys()` - YAML may contain hyphens
- DO NOT change env var prefix from `MADOUSHO_`
- DO NOT add extra fields to config models (rejected by validation)

## UNIQUE STYLES

- **Env var nesting**: `MADOUSHO_PROVIDER_OPENAI_API_KEY` → `{"provider": {"openai": {"api_key": "..."}}}`
- **Int conversion**: Env vars auto-converted to int if numeric (line 85-88)
- **Deep merge strategy**: Override dict recursively merged into base (not shallow replace)
- **Hyphen normalization**: YAML keys with hyphens auto-converted to underscores

## NOTES

- **Port validation**: Must be 1-65535 (validated in `APIConfig.validate_port`)
- **Extra fields**: All models reject extra fields - critical for catching typos
- **Test coverage**: Dedicated test file `tests/config/test_models.py` with 250+ lines
- **4-layer search**: CLI param → env var → cwd → ~/.config (enforced by cli.py)
- **Auto-int conversion**: Numeric env vars auto-converted to int (loader.py:85-88)
- **Extra fields**: All models reject extra fields - critical for catching typos
- **Test coverage**: Dedicated test file `tests/config/test_models.py` with 250+ lines
- **4-layer search**: CLI param → env var → cwd → ~/.config (enforced by cli.py)
