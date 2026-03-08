from typer.testing import CliRunner

from madousho.cli import app

runner = CliRunner()


def test_version_command():
    """Test that the version command returns exit code 0 and non-empty output."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout.strip()  # Non-empty string check
