"""Configuration loader with YAML parsing."""

from pathlib import Path
from typing import Any, Optional

import yaml

from .models import Config


_config_instance: Optional["ConfigManager"] = None


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


class ConfigManager:
    """Configuration manager - singleton instance loaded once at startup."""
    
    _instance: Optional["ConfigManager"] = None
    
    def __init__(self, config_dir: str):
        """Initialize configuration manager.
        
        Args:
            config_dir: Path to configuration directory (not file)
        """
        self.config_dir = Path(config_dir)
        self._config: Optional[Config] = None
    
    @classmethod
    def get_instance(cls, config_dir: Optional[str] = None) -> "ConfigManager":
        """Get or create the singleton ConfigManager instance.
        
        Args:
            config_dir: Configuration directory path (required on first call)
            
        Returns:
            ConfigManager singleton instance
            
        Raises:
            RuntimeError: If config_dir not provided on first call
        """
        if cls._instance is None:
            if config_dir is None:
                raise RuntimeError(
                    "ConfigManager not initialized. "
                    "Call ConfigManager.get_instance(config_dir='/path/to/config') first."
                )
            cls._instance = cls(config_dir)
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing)."""
        cls._instance = None
    
    def _find_config_file(self) -> Path:
        """Find configuration file in the config directory.
        
        Search order:
        1. {config_dir}/madousho.yaml
        2. {config_dir}/config.yaml
        
        Returns:
            Path to the found configuration file
            
        Raises:
            FileNotFoundError: If no configuration file is found
        """
        candidates = [
            self.config_dir / "madousho.yaml",
            self.config_dir / "config.yaml",
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        raise FileNotFoundError(
            f"No configuration file found in {self.config_dir}.\n"
            f"Expected one of: madousho.yaml, config.yaml"
        )
    
    @property
    def config(self) -> Config:
        """Get the loaded configuration.
        
        Returns:
            Validated Config object
            
        Raises:
            RuntimeError: If configuration not loaded yet
        """
        if self._config is None:
            self._load_config()
        return self._config
    
    def _load_config(self) -> None:
        """Load and validate configuration from the config directory."""
        config_file = self._find_config_file()
        yaml_config = load_yaml(str(config_file))
        yaml_config = normalize_keys(yaml_config)
        
        try:
            self._config = Config.model_validate(yaml_config)
        except Exception as e:
            raise ValueError(f"Invalid configuration: {e}")


def get_config() -> Config:
    """Get the global configuration instance.
    
    Returns:
        Validated Config object
        
    Raises:
        RuntimeError: If ConfigManager not initialized
    """
    return ConfigManager.get_instance().config


def init_config(config_dir: str) -> Config:
    """Initialize the configuration manager and return the config.
    
    Args:
        config_dir: Path to configuration directory
        
    Returns:
        Validated Config object
    """
    return ConfigManager.get_instance(config_dir).config
