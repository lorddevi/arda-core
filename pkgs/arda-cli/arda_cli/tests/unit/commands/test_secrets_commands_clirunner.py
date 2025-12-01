"""CliRunner tests for secrets commands."""

import pytest

from arda_cli.main import main as arda_main
from arda_cli.tests.unit.commands import BaseCommandTest


@pytest.mark.unit
@pytest.mark.with_core
class TestSecretsCommandsWithCliRunner(BaseCommandTest):
    """Test secrets commands using CliRunner."""

    def test_secrets_help(self, runner):
        """Test: arda secrets --help."""
        result = self.invoke_command(
            runner, arda_main, ["secrets", "--help"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_secrets_no_subcommand(self, runner):
        """Test: arda secrets (no subcommand)."""
        result = self.invoke_command(
            runner, arda_main, ["secrets"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Secret management" in result.output or "Usage:" in result.output

    def test_secrets_with_verbose(self, runner):
        """Test: arda --verbose secrets."""
        result = self.invoke_command(
            runner, arda_main, ["--verbose", "secrets"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Secret management" in result.output or "Usage:" in result.output
