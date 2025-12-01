"""CliRunner tests for templates commands."""

import pytest

from arda_cli.main import main as arda_main
from arda_cli.tests.unit.commands import BaseCommandTest


@pytest.mark.unit
@pytest.mark.with_core
class TestTemplatesCommandsWithCliRunner(BaseCommandTest):
    """Test templates commands using CliRunner."""

    def test_templates_help(self, runner):
        """Test: arda templates --help."""
        result = self.invoke_command(
            runner, arda_main, ["templates", "--help"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_templates_no_subcommand(self, runner):
        """Test: arda templates (no subcommand)."""
        result = self.invoke_command(
            runner, arda_main, ["templates"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Template" in result.output or "Usage:" in result.output

    def test_templates_with_verbose(self, runner):
        """Test: arda --verbose templates."""
        result = self.invoke_command(
            runner, arda_main, ["--verbose", "templates"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Template" in result.output or "Usage:" in result.output
