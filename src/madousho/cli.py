"""CLI entry point for Madousho.ai."""

import typer

try:
    from madousho._version import version as __version__
except (ImportError, ModuleNotFoundError):
    __version__ = "0.0.0.dev0"

app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Madousho.ai CLI."""
    if ctx.invoked_subcommand is None:
        typer.echo(__version__)
        ctx.exit()


@app.command()
def version():
    """Show version and exit."""
    typer.echo(__version__)


if __name__ == "__main__":
    app()
