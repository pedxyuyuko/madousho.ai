"""CLI entry point for Madousho.ai."""

import typer

from madousho.commands import serve, verify

try:
    from madousho._version import version as __version__
except (ImportError, ModuleNotFoundError):
    __version__ = "0.0.0.dev0"

app = typer.Typer()

# Register command modules at top level (no nesting)
app.add_typer(serve.app)
app.add_typer(verify.app)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose/debug logging"
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Output logs in JSON format"
    ),
    config_path: str = typer.Option(
        "config",
        "--config-path",
        "-d",
        help="Set configuration root directory (sets MADOUSHO_CONFIG_PATH env var)",
        envvar="MADOUSHO_CONFIG_PATH",
    ),
):
    """Madousho.ai CLI."""
    # Set MADOUSHO_CONFIG_PATH environment variable
    import os
    os.environ["MADOUSHO_CONFIG_PATH"] = config_path

    # Store options in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["json_output"] = json_output


@app.command()
def version():
    """Show version and exit."""
    typer.echo(__version__)


if __name__ == "__main__":
    app()
