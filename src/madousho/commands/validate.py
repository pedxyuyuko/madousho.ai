from madousho.logger import logger

"""Validate command - Validate the configuration file."""

import typer


def validate_cmd(ctx: typer.Context):
    """
    Validate the configuration file.
    
    Loads and validates the configuration file against the Pydantic models.
    Outputs success message or detailed error information.
    """
    config_path = ctx.obj["config_path"]
    
    try:
        from madousho.config.loader import load_config
        load_config(str(config_path))
        logger.success("Configuration is valid")
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        raise typer.Exit(code=1) from None
