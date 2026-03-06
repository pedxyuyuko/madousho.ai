from madousho.logger import logger
from madousho.config.loader import get_config

"""Validate command - Validate the configuration file."""

import typer


def validate_cmd(ctx: typer.Context):
    """
    Validate the configuration file.
    
    Loads and validates the configuration file against the Pydantic models.
    Outputs success message or detailed error information.
    """
    try:
        get_config()
        logger.success("Configuration is valid")
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        raise typer.Exit(code=1) from None
