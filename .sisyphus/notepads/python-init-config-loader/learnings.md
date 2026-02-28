## Task 5: Configuration Loader Implementation

### Key Learnings

1. **YAML Key Format Mismatch**: The config YAML files use hyphenated keys (e.g., `api-key`) while Pydantic models expect underscore keys (e.g., `api_key`). Solution: Added `normalize_keys()` function to recursively convert hyphens to underscores in all dictionary keys.

2. **Environment Variable Parsing**: Nested env vars like `MADOUSHO_PROVIDER_EXAMPLE_API_KEY=xyz` are parsed by:
   - Removing the prefix (`MADOUSHO_`)
   - Converting to lowercase
   - Splitting by underscore
   - Building nested dict structure

3. **Type Conversion**: Environment variables are strings by default. The loader attempts to convert values to integers automatically for numeric config values like ports.

4. **Error Handling**: Clear error messages are provided for:
   - Missing files: `FileNotFoundError`
   - Invalid YAML: `ValueError` with yaml.YAMLError details
   - Invalid config: `ValueError` with Pydantic validation errors

### Functions Implemented

- `load_yaml(path: str) -> dict`: Load and parse YAML file
- `get_env_overrides(prefix: str = "MADOUSHO_") -> dict`: Scan env vars for overrides
- `deep_merge(base: dict, override: dict) -> dict`: Recursive dict merge
- `load_config(config_path: str) -> Config`: Main entry point with validation

### Evidence Files

- `.sisyphus/evidence/task-5-load-yaml.txt`: YAML loading verification
- `.sisyphus/evidence/task-5-env-override.txt`: Environment override verification  
- `.sisyphus/evidence/task-5-missing-file.txt`: Error handling verification
