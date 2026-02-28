"""Run command - Start the madousho service."""

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
    
    typer.echo("Starting madousho service...")
    
    if verbose:
        typer.echo(f"Configuration loaded from: {config_path}")
        typer.echo(f"API host: {config.api.host}")
        typer.echo(f"API port: {config.api.port}")
        typer.echo(f"Model groups: {list(config.model_groups.keys())}")
