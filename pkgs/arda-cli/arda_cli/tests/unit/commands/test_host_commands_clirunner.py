"""CliRunner tests for host commands.

This module tests the Click command layer for 'arda host' using CliRunner
to achieve high pytest coverage (target: 100%).

Tests cover:
- Host command help
- Host command without subcommand
- Output messages
"""

import pytest

# Import commands to test
from arda_cli.main import main as arda_main

# Import base test infrastructure
from arda_cli.tests.unit.commands import BaseCommandTest


@pytest.mark.unit
@pytest.mark.with_core
class TestHostCommandsWithCliRunner(BaseCommandTest):
    """Test host commands using CliRunner for high pytest coverage.

    This test class covers the Click command layer which cannot be tested
    with direct function calls. Using CliRunner allows us to test:
    - Click decorators and callbacks
    - Command argument parsing
    - Context object passing
    - Help callbacks
    """

    # ============================================================
    # TEST HOST COMMAND
    # ============================================================

    def test_host_help(self, runner):
        """Test: arda host --help (show help message)."""
        result = self.invoke_command(
            runner, arda_main, ["host", "--help"], standalone_mode=False
        )
        # Command should succeed
        assert result.exit_code == 0
        # Output should show help
        assert "Usage:" in result.output or "help" in result.output.lower()

    def test_host_no_subcommand(self, runner):
        """Test: arda host (no subcommand, should show help)."""
        result = self.invoke_command(
            runner, arda_main, ["host"], standalone_mode=False
        )
        # Command should succeed and show help
        assert result.exit_code == 0
        # Should show help or coming soon message
        assert (
            "Host management" in result.output
            or "coming soon" in result.output.lower()
        )

    def test_host_with_verbose_flag(self, runner):
        """Test: arda --verbose host (host command with verbose flag)."""
        result = self.invoke_command(
            runner, arda_main, ["--verbose", "host"], standalone_mode=False
        )
        # Command should succeed
        assert result.exit_code == 0
        # Should show host management output
        assert (
            "Host management" in result.output
            or "coming soon" in result.output.lower()
        )

    def test_host_with_timestamp_flag(self, runner):
        """Test: arda --timestamp host (host command with timestamp flag)."""
        result = self.invoke_command(
            runner, arda_main, ["--timestamp", "host"], standalone_mode=False
        )
        # Command should succeed
        assert result.exit_code == 0
        # Should show host management output
        assert (
            "Host management" in result.output
            or "coming soon" in result.output.lower()
        )

    def test_host_with_theme_flag(self, runner):
        """Test: arda --theme nord host (host command with theme flag)."""
        result = self.invoke_command(
            runner, arda_main, ["--theme", "nord", "host"], standalone_mode=False
        )
        # Command should succeed
        assert result.exit_code == 0
        # Should show host management output
        assert (
            "Host management" in result.output
            or "coming soon" in result.output.lower()
        )

    def test_host_with_multiple_flags(self, runner):
        """Test: arda --verbose --timestamp --theme nord host."""
        result = self.invoke_command(
            runner,
            arda_main,
            ["--verbose", "--timestamp", "--theme", "nord", "host"],
            standalone_mode=False,
        )
        # Command should succeed
        assert result.exit_code == 0
        # Should show host management output
        assert (
            "Host management" in result.output
            or "coming soon" in result.output.lower()
        )

    def test_host_command_callback_with_help_false(self, runner):
        """Test: host command with help callback when flag not set.

        This tests the early return in host_help_callback when value is False.
        """
        # When --help is not provided, the callback value is False
        # This should trigger the early return on line 12
        result = self.invoke_command(
            runner, arda_main, ["host"], standalone_mode=False
        )
        # Should succeed (the return prevents help from being shown)
        assert result.exit_code == 0
        assert "Host management" in result.output
