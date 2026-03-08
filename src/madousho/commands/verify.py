"""Verify command for Madousho.ai configuration validation."""

import os
from pathlib import Path
from typing import Optional

from loguru import logger
from pydantic import ValidationError
import yaml

from madousho.config.models import Config
from madousho.config.loader import get_config_file


def verify_config(filepath: Optional[str] = None) -> bool:
    """Verify configuration file format and structure.

    Args:
        filepath: Optional path to config file. If None, uses default resolution.

    Returns:
        True if configuration is valid, False otherwise.
    """
    try:
        config_path = get_config_file(filepath)
        logger.info(f"Verifying configuration file: {config_path}")

        # Check if file exists
        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            return False

        # Load and parse YAML
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Validate against Pydantic model
        config = Config.model_validate(data)

        logger.info("Configuration file is valid")
        logger.info(f"  - API: host={config.api.host}, port={config.api.port}")
        logger.info(f"  - Default model group: {config.default_model_group}")
        logger.info(f"  - Providers: {', '.join(config.provider.keys())}")
        logger.info(f"  - Model groups: {', '.join(config.model_groups.keys())}")

        return True

    except FileNotFoundError as e:
        logger.error(str(e))
        return False
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error: {e}")
        return False
    except ValidationError as e:
        logger.error("Configuration validation failed")
        for error in e.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            msg = error["msg"]
            error_type = error["type"]
            logger.error(f"  - {field}: {msg} (type: {error_type})")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False


def verify(
    verbose: bool = False, json_output: bool = False, config_path: Optional[str] = None
):
    """Verify configuration file format and structure."""
    # Set MADOUSHO_CONFIG_PATH environment variable if config_path is provided
    if config_path is not None:
        os.environ["MADOUSHO_CONFIG_PATH"] = config_path

    from madousho.logging.config import configure_logging

    # Initialize logging with global options
    configure_logging(level="DEBUG" if verbose else None, is_json=json_output)

    # Verify configuration
    is_valid = verify_config(None)

    # Exit with appropriate code
    if is_valid:
        logger.info("✓ Configuration verification passed")
    else:
        logger.error("✗ Configuration verification failed")
        exit(1)
