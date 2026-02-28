"""Madousho CLI - Command Line Interface."""

import typer
from typing import Optional
from pathlib import Path
import importlib.metadata
from typer import CallbackParam
import os

from .commands import run_cmd, validate_cmd, show_config_cmd


app = typer.Typer()


def find_config_file(custom_path: Optional[str] = None) -> Path:
    """
    Find configuration file using 4-layer search strategy.
    
    Search order:
    1. custom_path (CLI --config parameter)
    2. Environment variable MADOUSHO_CONFIG
    3. ./madousho.yaml or ./config/madousho.yaml
    4. ~/.config/madousho/madousho.yaml
    
    Args:
        custom_path: Optional path provided via CLI --config option
        
    Returns:
        Path to the found configuration file
        
    Raises:
        FileNotFoundError: If no configuration file is found in any location
    """
    # Layer 1: CLI --config parameter
    if custom_path:
        path = Path(custom_path)
        if path.exists():
            return path
        else:
            raise FileNotFoundError(f"Configuration file not found: {custom_path}")
    
    # Layer 2: Environment variable MADOUSHO_CONFIG
    env_path = os.environ.get("MADOUSHO_CONFIG")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path
        else:
            raise FileNotFoundError(f"Configuration file from MADOUSHO_CONFIG not found: {env_path}")
    
    # Layer 3: Current directory - ./madousho.yaml or ./config/madousho.yaml
    cwd = Path.cwd()
    
    # Try ./madousho.yaml
    path = cwd / "madousho.yaml"
    if path.exists():
        return path
    
    # Try ./config/madousho.yaml
    path = cwd / "config" / "madousho.yaml"
    if path.exists():
        return path
    
    # Layer 4: ~/.config/madousho/madousho.yaml
    home_config = Path.home() / ".config" / "madousho" / "madousho.yaml"
    if home_config.exists():
        return home_config
    
    # No configuration file found - raise user-friendly error
    raise FileNotFoundError(
        "No configuration file found. Searched in the following locations:\n"
        f"  1. CLI --config parameter (not provided)\n"
        f"  2. Environment variable MADOUSHO_CONFIG (not set)\n"
        f"  3. {cwd / 'madousho.yaml'} (not found)\n"
        f"  4. {cwd / 'config' / 'madousho.yaml'} (not found)\n"
        f"  5. {home_config} (not found)\n"
        "\nPlease create a configuration file or specify one using --config option."
    )


def version_callback(ctx: typer.Context, param: CallbackParam, value: bool):
    if value:
        try:
            ver = importlib.metadata.version("madousho")
        except importlib.metadata.PackageNotFoundError:
            ver = "unknown"
        typer.echo(f"madousho v{ver}")
        raise typer.Exit()


@app.callback()
def callback(
    ctx: typer.Context,
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback, help="Show version and exit"),
):
    """
    Madousho AI - Advanced AI Assistant CLI
    """
    
    # Find configuration file using 4-layer search strategy
    try:
        config_path = find_config_file(str(config) if config else None)
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from None
    
    # Store global state in context object
    ctx.obj = {
        "config_path": config_path,
        "verbose": verbose,
    }


# Register subcommands
app.command("run")(run_cmd)
app.command("validate")(validate_cmd)
app.command("show-config")(show_config_cmd)


if __name__ == "__main__":
    app()
