"""Serve command for Madousho.ai API server."""

import os

import typer

from madousho.config.loader import init_config, get_config_file
from madousho.logging.config import configure_logging
from loguru import logger

app = typer.Typer()


@app.command()
def serve(ctx: typer.Context):
    """Madousho.ai API server."""
    verbose = ctx.obj.get("verbose", False)
    json_output = ctx.obj.get("json_output", False)
    config_path = os.environ.get("MADOUSHO_CONFIG_PATH")

    # Set MADOUSHO_CONFIG_PATH environment variable if config_path is provided
    if config_path is not None:
        os.environ["MADOUSHO_CONFIG_PATH"] = config_path

    # Get the actual config file path that will be used
    resolved_config_path = get_config_file(None)

    # Load configuration
    _ = init_config()

    # Initialize logging with global options
    configure_logging(level="DEBUG" if verbose else None, is_json=json_output)

    # Output startup information
    logger.info(f"Configuration loaded from: {resolved_config_path}")
