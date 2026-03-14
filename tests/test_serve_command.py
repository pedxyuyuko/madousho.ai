from unittest.mock import patch
from typer.testing import CliRunner
from madousho.cli import app

runner = CliRunner()


def test_serve_help():
    """Test that serve --help shows help text."""
    result = runner.invoke(app, ["serve", "--help"])
    assert result.exit_code == 0
    assert "Madousho.ai API server" in result.stdout


@patch("madousho.commands.serve.start_http_server")
def test_serve_command(mock_start_server):
    """Test that serve command executes successfully without blocking."""
    result = runner.invoke(app, ["serve"])
    assert result.exit_code == 0
    mock_start_server.assert_called_once()
