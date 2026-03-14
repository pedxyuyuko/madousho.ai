"""Configuration loader for Madousho.ai."""

import os
import re
from pathlib import Path
import yaml
from loguru import logger
from .models import Config

_cached_config: Config | None = None
_cached_config_path: Path | None = None


def get_config_file(filepath: str | None = None) -> Path:
    """Resolve the configuration file path.

    Args:
        filepath: Optional path to config file. If absolute, used directly.
                  If relative, joined with MADOUSHO_CONFIG_PATH env var.
                  If None, defaults to "madousho" filename.

    Returns:
        Path to the configuration file.

    Raises:
        FileNotFoundError: If neither .yaml nor .yml file exists.
    """
    base_dir = os.environ.get("MADOUSHO_CONFIG_PATH", "config")

    if filepath is None:
        filename = "madousho"
    elif os.path.isabs(filepath):
        return _resolve_file_extension(Path(filepath))
    else:
        filename = filepath

    config_path = Path(base_dir) / filename
    return _resolve_file_extension(config_path)


def _resolve_file_extension(config_path: Path) -> Path:
    """Try .yaml first, then .yml extension.

    Args:
        config_path: Path without extension or with extension.

    Returns:
        Path with valid extension.

    Raises:
        FileNotFoundError: If neither extension exists.
    """
    if config_path.suffix in (".yaml", ".yml"):
        if config_path.exists():
            return config_path
        raise FileNotFoundError(f"Config file not found: {config_path}")

    yaml_path = config_path.with_suffix(".yaml")
    if yaml_path.exists():
        return yaml_path

    yml_path = config_path.with_suffix(".yml")
    if yml_path.exists():
        return yml_path

    return yaml_path


def _load_from_file(config_path: Path) -> Config:
    """Load and validate configuration from YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Validated Config instance.

    Raises:
        yaml.YAMLError: If YAML parsing fails.
        pydantic.ValidationError: If validation fails.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return Config.model_validate(data)


def init_config(filepath: str | None = None) -> Config:
    """Initialize configuration from file and update cache.

    Args:
        filepath: Optional path to config file. Resolved using get_config_file().

    Returns:
        The loaded Config instance.
    """
    global _cached_config, _cached_config_path

    config_path = get_config_file(filepath)
    _cached_config = _load_from_file(config_path)
    _cached_config_path = config_path
    return _cached_config


def get_config() -> Config:
    """Get the cached configuration instance.

    Returns:
        The cached Config instance.
    """
    global _cached_config

    if _cached_config is None:
        _cached_config = init_config()
    return _cached_config


def save_config() -> None:
    """Save the cached configuration back to the YAML file.

    This is useful when configuration values are auto-generated (like API token)
    and need to be persisted for future use.

    Uses regex to update only the token line, preserving all comments and formatting.

    Raises:
        ValueError: If no configuration has been loaded yet.
        IOError: If writing to the config file fails.
    """
    global _cached_config, _cached_config_path

    if _cached_config is None:
        raise ValueError("No configuration loaded. Call init_config() first.")

    if _cached_config_path is None:
        raise ValueError("No config file path available.")

    _update_token_in_file(_cached_config_path, _cached_config.api.token)

    logger.info(f"Configuration saved to: {_cached_config_path}")


def _update_token_in_file(filepath: Path, new_token: str) -> None:
    """Update only the token line in the config file using regex.

    This preserves all comments, formatting, and other content.

    Args:
        filepath: Path to the YAML config file.
        new_token: The new token value to set.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(
        r'^(\s*token:\s*)".*"(.*?)$',
        rf'\1"{new_token}"\2',
        content,
        flags=re.MULTILINE,
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def get_config_path() -> Path | None:
    """Get the path of the loaded configuration file.

    Returns:
        The config file path if loaded, None otherwise.
    """
    return _cached_config_path
