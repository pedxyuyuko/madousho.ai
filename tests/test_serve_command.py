from typer.testing import CliRunner
from madousho.cli import app

runner = CliRunner()


def test_serve_help():
    """Test that serve --help shows help text."""
    result = runner.invoke(app, ["serve", "--help"])
    assert result.exit_code == 0
    assert "Madousho.ai API server" in result.stdout


def test_serve_command():
    """Test that serve command executes successfully."""
    result = runner.invoke(app, ["serve"])
    assert result.exit_code == 0
