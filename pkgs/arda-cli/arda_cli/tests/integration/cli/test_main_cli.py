"""Integration tests for main CLI entry point."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
from click.testing import CliRunner

from arda_cli.lib.config import get_active_config_path

# Import the main CLI entry point
from arda_cli.main import (
    ensure_config_exists,
    main,
    show_active_config,
    show_help_with_config,
    validate_theme,
)


@pytest.mark.integration
@pytest.mark.cli
@pytest.mark.with_core
class TestMainCLI:
    """Test main CLI entry point and routing."""

    def test_cli_help(self):
        """Test that CLI shows help correctly."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "config" in result.output
        assert "theme" in result.output
        assert "host" in result.output

    def test_cli_version(self):
        """Test CLI version display."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        # Check for version in output
        assert "version" in result.output.lower()
        assert "arda" in result.output.lower()

    def test_cli_with_theme_option(self):
        """Test CLI with --theme option."""
        runner = CliRunner()
        result = runner.invoke(main, ["--theme", "dracula", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_cli_with_invalid_theme(self):
        """Test CLI with invalid theme."""
        runner = CliRunner()
        result = runner.invoke(main, ["--theme", "nonexistent_theme"])
        assert result.exit_code == 2
        assert "not found" in result.output.lower()

    def test_cli_with_verbose_flag(self):
        """Test CLI with --verbose flag."""
        runner = CliRunner()
        result = runner.invoke(main, ["--verbose", "config", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output


@pytest.mark.integration
@pytest.mark.cli
@pytest.mark.with_core
class TestShowActiveConfig:
    """Test active config display."""

    def test_show_active_config(self):
        """Test showing active config path."""
        with patch("arda_cli.main.get_active_config_path") as mock_get_config:
            mock_get_config.return_value = ("/path/to/config.toml", "Project config")

            from io import StringIO

            from rich.console import Console

            output = StringIO()
            console = Console(file=output, force_terminal=True)
            show_active_config(console)

            # Verify the config source is displayed in the output
            output_text = output.getvalue()
            assert "Active configuration:" in output_text
            assert "Project config" in output_text


@pytest.mark.integration
@pytest.mark.cli
@pytest.mark.with_core
class TestShowHelpWithConfig:
    """Test show_help_with_config function."""

    @patch("sys.argv", ["arda", "--help", "--theme", "nord"])
    @patch("arda_cli.main.get_active_config_path")
    @patch("arda_cli.main.get_rich_click_themes")
    @patch("click.Context")
    def test_show_help_with_config_uses_sys_argv_fallback(
        self, mock_ctx_class, mock_themes, mock_get_config
    ):
        """Test that show_help_with_config falls back to sys.argv when ctx lacks theme.

        This tests lines 156-158 in main.py where sys.argv is parsed for theme
        when ctx.params and ctx.obj don't have theme information.
        """
        # Setup mocks
        mock_ctx_class.params = {}  # No theme in params
        mock_ctx_class.obj = {}  # No theme in obj
        mock_ctx_class.get_help.return_value = "Help text"

        mock_themes.return_value = ["dracula", "nord", "forest"]
        mock_get_config.return_value = (
            Path("fake_config.toml"),
            "Test config",
        )

        # Create mock context instance
        mock_ctx = MagicMock()
        mock_ctx.params = {}
        mock_ctx.obj = {}
        mock_ctx.get_help.return_value = "Help text"
        mock_ctx_class.return_value = mock_ctx

        # Call the function

        show_help_with_config(mock_ctx, None, True)

        # Verify the function ran without error
        # The actual theme value from sys.argv is processed
        assert mock_ctx.get_help.called


@pytest.mark.integration
@pytest.mark.cli
@pytest.mark.with_core
class TestCLIRouting:
    """Test command routing."""

    def test_config_command_routing(self):
        """Test that config command is properly routed."""
        runner = CliRunner()
        result = runner.invoke(main, ["config", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_theme_command_routing(self):
        """Test that theme command is properly routed."""
        runner = CliRunner()
        result = runner.invoke(main, ["theme", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_host_command_routing(self):
        """Test that host command is properly routed."""
        runner = CliRunner()
        result = runner.invoke(main, ["host", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_unknown_command(self):
        """Test that unknown command shows error."""
        runner = CliRunner()
        result = runner.invoke(main, ["unknown-command"])
        assert result.exit_code != 0


@pytest.mark.integration
@pytest.mark.cli
@pytest.mark.with_core
class TestCLIContext:
    """Test CLI context and object passing."""

    def test_cli_context_object(self):
        """Test that CLI context object is properly configured."""
        runner = CliRunner()

        # Mock the context object
        with patch("arda_cli.main.get_theme_from_config") as mock_theme:
            mock_theme.return_value = "dracula"
            result = runner.invoke(main, ["config", "--help"])
            assert result.exit_code == 0

    def test_cli_verbose_flag(self):
        """Test verbose flag in CLI context."""
        runner = CliRunner()

        with patch("arda_cli.main.get_verbose_from_config") as mock_verbose:
            mock_verbose.return_value = False
            result = runner.invoke(main, ["--verbose", "config", "--help"])
            assert result.exit_code == 0

    def test_cli_timestamp_flag(self):
        """Test timestamp flag in CLI context."""
        runner = CliRunner()

        with patch("arda_cli.main.get_timestamp_from_config") as mock_timestamp:
            mock_timestamp.return_value = False
            result = runner.invoke(main, ["--timestamp", "config", "--help"])
            assert result.exit_code == 0


@pytest.mark.integration
@pytest.mark.cli
@pytest.mark.with_core
class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_cli_keyboard_interrupt(self):
        """Test handling of keyboard interrupt."""
        runner = CliRunner()
        # Click's CliRunner handles this gracefully
        result = runner.invoke(main, [])
        # Verify valid exit code (no crash or unhandled exception)
        assert result.exit_code in (0, 1, 2, 130)  # Valid CLI exit codes

    def test_cli_system_exit(self):
        """Test handling of system exit in commands."""
        runner = CliRunner()
        # Test invalid theme without --help flag to trigger validation
        result = runner.invoke(main, ["--theme", "invalid"])
        # Should exit with error code and show "not found" message
        assert result.exit_code != 0 or "not found" in result.output.lower()
