"""Configuration loader with YAML parsing."""

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

def load_config(config_path: str) -> Config:
    """Load configuration from YAML file.
    
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
    
    # Validate and return Config object
    try:
        return Config.model_validate(yaml_config)
    except Exception as e:
        raise ValueError(f"Invalid configuration: {e}")
