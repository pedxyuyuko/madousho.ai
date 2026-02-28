"""Configuration loader with YAML parsing and environment variable overrides."""

import os
from pathlib import Path
from typing import Any

import yaml

from .models import Config


def normalize_keys(obj: Any) -> Any:
    """Recursively convert hyphenated keys to underscores."""
    if isinstance(obj, dict):
        return {k.replace('-', '_'): normalize_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_keys(item) for item in obj]
    else:
        return obj


def load_yaml(path: str) -> dict:
    """Load and parse a YAML file.
    
    Args:
        path: Path to the YAML file
        
    Returns:
        Parsed YAML content as a dictionary
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the YAML is invalid
    """
    file_path = Path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
            return content if content is not None else {}
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {path}: {e}")


def get_env_overrides(prefix: str = "MADOUSHO_") -> dict:
    """Scan environment variables and build override dictionary.
    
    Args:
        prefix: Prefix for environment variables (default: MADOUSHO_)
        
    Returns:
        Nested dictionary of overrides from environment variables
        
    Example:
        MADOUSHO_API_PORT=9000 -> {"api": {"port": 9000}}
        MADOUSHO_PROVIDER_EXAMPLE_API_KEY=xyz -> {"provider": {"example": {"api_key": "xyz"}}}
    """
    overrides: dict[str, Any] = {}
    
    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue
        
        # Remove prefix and split by underscore
        parts = key[len(prefix):].lower().split('_')
        
        # Build nested dict
        current = overrides
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                # If existing value is not a dict, replace it
                current[part] = {}
            current = current[part]
        
        # Set the final value
        final_key = parts[-1]
        final_value: Any = value
        
        # Try to convert to int if possible
        try:
            final_value = int(value)
        except ValueError:
            pass
        
        current[final_key] = final_value
    
    return overrides


def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge two dictionaries.
    
    Args:
        base: Base dictionary
        override: Dictionary with values to override
        
    Returns:
        Merged dictionary with override values taking precedence
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def load_config(config_path: str) -> Config:
    """Load configuration from YAML file with environment variable overrides.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Validated Config object
        
    Raises:
        FileNotFoundError: If the configuration file does not exist
        ValueError: If the YAML is invalid or config validation fails
    """
    # Load YAML
    yaml_config = load_yaml(config_path)
    
    # Normalize keys (convert hyphens to underscores)
    yaml_config = normalize_keys(yaml_config)
    
    # Get environment overrides
    env_overrides = get_env_overrides()
    
    # Merge configs
    merged = deep_merge(yaml_config, env_overrides)
    
    # Validate and return Config object
    try:
        return Config.model_validate(merged)
    except Exception as e:
        raise ValueError(f"Invalid configuration: {e}")
