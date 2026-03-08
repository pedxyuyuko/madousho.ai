"""Tests for global CLI options (--verbose, --json, --config-path)."""

from typer.testing import CliRunner
from madousho.cli import app

runner = CliRunner()


def test_verbose_flag_in_help():
    """Test that --verbose flag is shown in help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--verbose" in result.stdout
    assert "-v" in result.stdout


def test_json_flag_in_help():
    """Test that --json flag is shown in help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--json" in result.stdout


def test_config_path_flag_in_help():
    """Test that --config-path flag is shown in help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--config-path" in result.stdout
    assert "-d" in result.stdout


def test_serve_with_verbose_flag():
    """Test that serve command accepts --verbose flag (global option before subcommand)."""
    result = runner.invoke(app, ["--verbose", "serve"])
    assert result.exit_code == 0


def test_serve_with_json_flag():
    """Test that serve command accepts --json flag (global option before subcommand)."""
    result = runner.invoke(app, ["--json", "serve"])
    assert result.exit_code == 0


def test_serve_with_config_path_flag():
    """Test that serve command accepts --config-path flag (global option before subcommand)."""
    result = runner.invoke(app, ["--config-path", "config", "serve"])
    assert result.exit_code == 0


def test_serve_with_short_verbose_flag():
    """Test that serve command accepts -v short flag (global option before subcommand)."""
    result = runner.invoke(app, ["-v", "serve"])
    assert result.exit_code == 0


def test_serve_with_short_config_path_flag():
    """Test that serve command accepts -d short flag (global option before subcommand)."""
    result = runner.invoke(app, ["-d", "config", "serve"])
    assert result.exit_code == 0


def test_serve_with_all_flags():
    """Test that serve command accepts all global flags together."""
    result = runner.invoke(app, ["--verbose", "--json", "--config-path", "config", "serve"])
    assert result.exit_code == 0
