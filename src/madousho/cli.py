"""Madousho CLI - Command Line Interface."""

import typer
from typing import Optional
from pathlib import Path
import importlib.metadata
from typer import CallbackParam

from .commands import run_cmd, validate_cmd
from .logger import configure_logger
from .config.loader import init_config
app = typer.Typer()


def find_config_dir(custom_path: Optional[str] = None) -> Path:
    """
    Find configuration directory using 3-layer search strategy.
    
    Search order:
    1. custom_path (CLI --config parameter, treated as directory)
    2. ./config/ directory
    3. ~/.config/madousho/ directory
    
    Args:
        custom_path: Optional path provided via CLI --config option
        
    Returns:
        Path to the found configuration directory
        
    Raises:
        FileNotFoundError: If no configuration directory is found in any location
    """
    # Layer 1: CLI --config parameter (treated as directory)
    if custom_path:
        path = Path(custom_path)
        if path.exists() and path.is_dir():
            return path
        elif path.exists() and path.is_file():
            # If a file is provided, use its parent directory
            return path.parent
        else:
            raise FileNotFoundError(f"Configuration directory not found: {custom_path}")
    
    # Layer 2: Current directory - ./config/ or ./madousho.yaml
    cwd = Path.cwd()
    
    # Try ./config/ directory
    config_dir = cwd / "config"
    if config_dir.exists() and config_dir.is_dir():
        return config_dir
    
    # Try ./madousho.yaml (use parent directory which is cwd)
    if (cwd / "madousho.yaml").exists():
        return cwd
    
    # Layer 3: ~/.config/madousho/ directory
    home_config = Path.home() / ".config" / "madousho"
    if home_config.exists() and home_config.is_dir():
        return home_config
    
    # No configuration found - raise user-friendly error
    raise FileNotFoundError(
        "No configuration found. Searched in the following locations:\n"
        f"  1. CLI --config parameter (not provided)\n"
        f"  2. {cwd / 'config'}/ (not found)\n"
        f"  3. {cwd / 'madousho.yaml'} (not found)\n"
        f"  4. {home_config}/ (not found)\n"
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
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration directory path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    json: bool = typer.Option(False, "--json", "-j", help="Output logs in JSON format"),
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback, help="Show version and exit"),
):
    """
    Madousho AI - Advanced AI Assistant CLI
    """
    
    # Find configuration directory and initialize config manager (once at startup)
    try:
        config_dir = find_config_dir(str(config) if config else None)
        init_config(str(config_dir))
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from None
    
    # Configure logger with verbose and json settings
    configure_logger(verbose=verbose, json_output=json)
    
    # Store global state in context object
    ctx.obj = {
        "config_dir": config_dir,
    }


# Register subcommands
app.command("run")(run_cmd)
app.command("validate")(validate_cmd)


if __name__ == "__main__":
    app()
