"""CliRunner tests for theme commands.

This module tests the Click command layer for 'arda theme' using CliRunner
to achieve high pytest coverage (target: 80%+).

Tests cover:
- Theme list command
- Theme preview command
- Help callbacks
- Context object passing
"""

import pytest

# Import commands to test
from arda_cli.main import main as arda_main

# Import base test infrastructure
from arda_cli.tests.unit.commands import BaseCommandTest


@pytest.mark.unit
@pytest.mark.theme
@pytest.mark.with_core
class TestThemeCommandsWithCliRunner(BaseCommandTest):
    """Test theme commands using CliRunner for high pytest coverage.

    This test class covers the Click command layer which cannot be tested
    with direct function calls. Using CliRunner allows us to test:
    - Click decorators and callbacks
    - Command argument parsing
    - Context object passing
    - Help callbacks
    """

    # ============================================================
    # TEST THEME LIST COMMAND
    # ============================================================

    def test_list_command_basic(self, runner):
        """Test: arda theme list (list all themes)."""
        result = self.invoke_command(
            runner, arda_main, ["theme", "list"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Available Rich-Click Themes" in result.output

    def test_list_command_with_verbose(self, runner):
        """Test: arda --verbose theme list (list themes with verbose output)."""
        result = self.invoke_command(
            runner, arda_main, ["--verbose", "theme", "list"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Available Rich-Click Themes" in result.output
        assert "Total themes:" in result.output

    def test_list_help(self, runner):
        """Test: arda theme list --help (show list command help)."""
        result = self.invoke_command(
            runner, arda_main, ["theme", "list", "--help"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Usage:" in result.output

    # ============================================================
    # TEST THEME PREVIEW COMMAND
    # ============================================================

    def test_preview_command_basic(self, runner):
        """Test: arda theme preview (preview current theme)."""
        result = self.invoke_command(
            runner, arda_main, ["theme", "preview"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Current Theme:" in result.output

    def test_preview_with_verbose(self, runner):
        """Test: arda --verbose theme preview (preview with verbose output)."""
        result = self.invoke_command(
            runner, arda_main, ["--verbose", "theme", "preview"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Current Theme:" in result.output

    def test_preview_with_theme_flag(self, runner):
        """Test: arda --theme nord theme preview (preview specific theme)."""
        result = self.invoke_command(
            runner,
            arda_main,
            ["--theme", "nord", "theme", "preview"],
            standalone_mode=False,
        )
        assert result.exit_code == 0
        assert "Current Theme:" in result.output
        assert "NORD" in result.output

    def test_preview_help(self, runner):
        """Test: arda theme preview --help (show preview command help)."""
        result = self.invoke_command(
            runner, arda_main, ["theme", "preview", "--help"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Usage:" in result.output

    # ============================================================
    # TEST THEME GROUP
    # ============================================================

    def test_theme_help(self, runner):
        """Test: arda theme --help (show theme group help)."""
        result = self.invoke_command(
            runner, arda_main, ["theme", "--help"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "Theme management" in result.output

    def test_theme_no_subcommand(self, runner):
        """Test: arda theme (no subcommand, should show help)."""
        result = self.invoke_command(
            runner, arda_main, ["theme"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Usage:" in result.output

    # ============================================================
    # TEST FLAGS
    # ============================================================

    def test_list_with_timestamp_flag(self, runner):
        """Test: arda --timestamp theme list (list with timestamps)."""
        result = self.invoke_command(
            runner, arda_main, ["--timestamp", "theme", "list"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Available Rich-Click Themes" in result.output

    def test_preview_with_timestamp_flag(self, runner):
        """Test: arda --timestamp theme preview (preview with timestamps)."""
        result = self.invoke_command(
            runner,
            arda_main,
            ["--timestamp", "theme", "preview"],
            standalone_mode=False,
        )
        assert result.exit_code == 0
        assert "Current Theme:" in result.output

    def test_list_with_both_verbose_and_timestamp(self, runner):
        """Test: arda --verbose --timestamp theme list."""
        result = self.invoke_command(
            runner,
            arda_main,
            ["--verbose", "--timestamp", "theme", "list"],
            standalone_mode=False,
        )
        assert result.exit_code == 0
        assert "Available Rich-Click Themes" in result.output

    def test_preview_with_multiple_flags(self, runner):
        """Test: arda --verbose --timestamp theme preview."""
        result = self.invoke_command(
            runner,
            arda_main,
            ["--verbose", "--timestamp", "theme", "preview"],
            standalone_mode=False,
        )
        assert result.exit_code == 0
        assert "Current Theme:" in result.output
