"""CliRunner tests for roles commands."""

import pytest

from arda_cli.main import main as arda_main
from arda_cli.tests.unit.commands import BaseCommandTest


@pytest.mark.unit
@pytest.mark.with_core
class TestRolesCommandsWithCliRunner(BaseCommandTest):
    """Test roles commands using CliRunner."""

    def test_roles_help(self, runner):
        """Test: arda roles --help."""
        result = self.invoke_command(
            runner, arda_main, ["roles", "--help"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_roles_no_subcommand(self, runner):
        """Test: arda roles (no subcommand)."""
        result = self.invoke_command(
            runner, arda_main, ["roles"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Role management" in result.output or "Usage:" in result.output

    def test_roles_with_verbose(self, runner):
        """Test: arda --verbose roles."""
        result = self.invoke_command(
            runner, arda_main, ["--verbose", "roles"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Role management" in result.output or "Usage:" in result.output
