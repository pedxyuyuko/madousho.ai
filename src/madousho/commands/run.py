"""Run command - Start the madousho service."""

from madousho.logger import logger

import typer


def run_cmd(ctx: typer.Context):
    """
    Start the madousho service.
    
    This is a stub command that loads the configuration and prints startup information.
    Actual service implementation will be added later.
    """
    config_path = ctx.obj["config_path"]
    verbose = ctx.obj["verbose"]
    
    # Load configuration
    from madousho.config.loader import load_config
    config = load_config(str(config_path))
    
    logger.info("Starting madousho service...")
    
    if verbose:
        logger.info("Configuration loaded", config_path=str(config_path), api_host=config.api.host, api_port=config.api.port, model_groups=list(config.model_groups.keys()))
