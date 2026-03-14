"""Tests for global CLI options (--verbose, --json, --config-path)."""

import re
from unittest.mock import patch

from typer.testing import CliRunner
from madousho.cli import app

runner = CliRunner()


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    ansi_pattern = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_pattern.sub("", text)


def test_verbose_flag_in_help():
    """Test that --verbose flag is shown in help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    clean_output = strip_ansi(result.stdout)
    assert "--verbose" in clean_output
    assert "-v" in clean_output


def test_json_flag_in_help():
    """Test that --json flag is shown in help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    clean_output = strip_ansi(result.stdout)
    assert "--json" in clean_output


def test_config_path_flag_in_help():
    """Test that --config-path flag is shown in help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    clean_output = strip_ansi(result.stdout)
    assert "--config-path" in clean_output
    assert "-d" in clean_output


@patch("madousho.commands.serve.start_http_server")
def test_serve_with_verbose_flag(mock_start_server):
    """Test that serve command accepts --verbose flag (global option before subcommand)."""
    result = runner.invoke(app, ["--verbose", "serve"])
    assert result.exit_code == 0
    mock_start_server.assert_called_once()


@patch("madousho.commands.serve.start_http_server")
def test_serve_with_json_flag(mock_start_server):
    """Test that serve command accepts --json flag (global option before subcommand)."""
    result = runner.invoke(app, ["--json", "serve"])
    assert result.exit_code == 0
    mock_start_server.assert_called_once()


@patch("madousho.commands.serve.start_http_server")
def test_serve_with_config_path_flag(mock_start_server):
    """Test that serve command accepts --config-path flag (global option before subcommand)."""
    result = runner.invoke(app, ["--config-path", "config", "serve"])
    assert result.exit_code == 0
    mock_start_server.assert_called_once()


@patch("madousho.commands.serve.start_http_server")
def test_serve_with_short_verbose_flag(mock_start_server):
    """Test that serve command accepts -v short flag (global option before subcommand)."""
    result = runner.invoke(app, ["-v", "serve"])
    assert result.exit_code == 0
    mock_start_server.assert_called_once()


@patch("madousho.commands.serve.start_http_server")
def test_serve_with_short_config_path_flag(mock_start_server):
    """Test that serve command accepts -d short flag (global option before subcommand)."""
    result = runner.invoke(app, ["-d", "config", "serve"])
    assert result.exit_code == 0
    mock_start_server.assert_called_once()


@patch("madousho.commands.serve.start_http_server")
def test_serve_with_all_flags(mock_start_server):
    """Test that serve command accepts all global flags together."""
    result = runner.invoke(
        app, ["--verbose", "--json", "--config-path", "config", "serve"]
    )
    assert result.exit_code == 0
    mock_start_server.assert_called_once()
