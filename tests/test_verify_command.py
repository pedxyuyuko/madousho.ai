"""Tests for the verify CLI command."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from madousho.cli import app

runner = CliRunner()


class TestVerifyCommand:
    """Test cases for the verify CLI command."""

    def test_verify_valid_config(self):
        """Test verifying a valid configuration file."""
        # Use the example config which is valid
        result = runner.invoke(app, ["--config-path", "config", "verify"])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()

    def test_verify_missing_file(self):
        """Test verifying a non-existent configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Point to a directory with no config file
            result = runner.invoke(app, ["--config-path", tmpdir, "verify"])
            assert result.exit_code == 1
            assert "not found" in result.output.lower()

    def test_verify_invalid_yaml(self):
        """Test verifying a file with invalid YAML syntax."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file with invalid YAML
            invalid_yaml = Path(tmpdir) / "madousho.yaml"
            invalid_yaml.write_text("invalid: yaml: syntax: [")

            result = runner.invoke(app, ["--config-path", tmpdir, "verify"])
            assert result.exit_code == 1
            assert "yaml" in result.output.lower() or "parsing" in result.output.lower()

    def test_verify_missing_required_fields(self):
        """Test verifying a config file missing required fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a config file missing required fields
            incomplete_config = Path(tmpdir) / "madousho.yaml"
            incomplete_config.write_text("api:\n  token: test\n")

            result = runner.invoke(app, ["--config-path", tmpdir, "verify"])
            assert result.exit_code == 1
            assert (
                "validation" in result.output.lower()
                or "required" in result.output.lower()
            )

    def test_verify_verbose_mode(self):
        """Test verify command with verbose flag."""
        result = runner.invoke(app, ["--verbose", "--config-path", "config", "verify"])
        assert result.exit_code == 0
        # Verbose mode should show more details
        assert "DEBUG" in result.output or "valid" in result.output.lower()

    def test_verify_json_output(self):
        """Test verify command with JSON output format."""
        result = runner.invoke(app, ["--json", "--config-path", "config", "verify"])
        assert result.exit_code == 0
        # JSON output should contain JSON-formatted logs
        assert "{" in result.output and "}" in result.output

    def test_verify_with_custom_config_file(self):
        """Test verifying a specific config file using --config-path."""
        # Use the mock config file
        result = runner.invoke(app, ["--config-path", "config", "verify"])
        assert result.exit_code == 0
