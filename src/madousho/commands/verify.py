"""Verify command for Madousho.ai configuration validation."""

import os
from typing import Optional

import typer
from loguru import logger
from pydantic import ValidationError
import yaml

from madousho.config.models import Config
from madousho.config.loader import get_config_file

app = typer.Typer()


@app.command()
def verify(ctx: typer.Context):
    """Verify configuration file format and structure."""
    verbose = ctx.obj.get("verbose", False)
    json_output = ctx.obj.get("json_output", False)
    no_color = ctx.obj.get("no_color", False)
    config_path = os.environ.get("MADOUSHO_CONFIG_PATH")

    # Set MADOUSHO_CONFIG_PATH environment variable if config_path is provided
    if config_path is not None:
        os.environ["MADOUSHO_CONFIG_PATH"] = config_path

    # Initialize logging with global options
    from madousho.logging.config import configure_logging

    configure_logging(
        level="DEBUG" if verbose else None, is_json=json_output, colorize=not no_color
    )

    # Verify configuration
    is_valid = _verify_config(None)

    # Exit with appropriate code
    if is_valid:
        logger.info("✓ Configuration verification passed")
    else:
        logger.error("✗ Configuration verification failed")
        raise typer.Exit(code=1)


def _verify_config(filepath: Optional[str] = None) -> bool:
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
