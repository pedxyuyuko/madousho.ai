"""CLI entry point for Madousho.ai."""

import os
from typing import Optional

import typer

from madousho.commands.serve import serve
from madousho.commands.verify import verify

try:
    from madousho._version import version as __version__
except (ImportError, ModuleNotFoundError):
    __version__ = "0.0.0.dev0"

app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose/debug logging"),
    json_output: bool = typer.Option(False, "--json", help="Output logs in JSON format"),
    config_path: Optional[str] = typer.Option(None, "--config-path", "-d", help="Set configuration root directory (sets MADOUSHO_CONFIG_PATH env var)", envvar="MADOUSHO_CONFIG_PATH"),
):
    """Madousho.ai CLI."""
    # Set MADOUSHO_CONFIG_PATH environment variable if --config-path is provided
    if config_path is not None:
        os.environ["MADOUSHO_CONFIG_PATH"] = config_path
    
    # Store global options in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["json_output"] = json_output
    
    if ctx.invoked_subcommand is None:
        typer.echo(__version__)
        ctx.exit()


@app.command()
def version():
    """Show version and exit."""
    typer.echo(__version__)

@app.command(name="serve", help=serve.__doc__)
def serve_cmd(ctx: typer.Context):
    return serve(
        verbose=ctx.obj.get("verbose", False),
        json_output=ctx.obj.get("json_output", False),
        config_path=os.environ.get("MADOUSHO_CONFIG_PATH")
    )

@app.command(name="verify", help=verify.__doc__)
def verify_cmd(ctx: typer.Context):
    return verify(
        verbose=ctx.obj.get("verbose", False),
        json_output=ctx.obj.get("json_output", False),
        config_path=os.environ.get("MADOUSHO_CONFIG_PATH")
    )

if __name__ == "__main__":
    app()
