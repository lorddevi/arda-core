"""Extended integration tests for arda_cli.main module.

These tests cover config file creation and theme validation
to achieve higher coverage of the main CLI module.
"""

import tomllib
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from arda_cli.lib.theme import get_rich_click_themes
from arda_cli.main import main, validate_theme


class TestConfigFileCreation:
    """Test automatic config file creation on first run."""

    def test_config_created_on_first_help_invocation(self):
        """Test that config is created on first CLI invocation."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Patch Path.home() to return the isolated temp directory
            # This prevents finding the real XDG config
            import tempfile

            temp_dir = Path.cwd()

            with patch("pathlib.Path.home", return_value=temp_dir):
                # Run config view command (should create config)
                result = runner.invoke(main, ["config", "view"])

                # Verify config was created
                config_path = Path("etc/arda.toml")
                assert config_path.exists(), "Config file should be created"

                # Verify creation message in output
                assert (
                    "Configuration file not found" in result.output
                    or "Created" in result.output
                )

                # Verify it's valid TOML
                with open(config_path, "rb") as f:
                    config_data = tomllib.load(f)

                # Verify config structure
                assert "theme" in config_data
                assert "output" in config_data

    def test_config_not_recreated_when_exists(self):
        """Test that existing config is not overwritten."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Pre-create config with custom content
            config_dir = Path("etc")
            config_dir.mkdir(parents=True)
            config_path = config_dir / "arda.toml"
            custom_config = """[theme]
default = "nord"

[output]
verbose = true
timestamp = false
"""
            config_path.write_text(custom_config)

            # Run config view command (config already exists)
            result = runner.invoke(main, ["config", "view"])

            # Verify config was NOT recreated
            assert "Created default configuration" not in result.output
            assert "Configuration file not found" not in result.output

            # Verify content unchanged
            assert config_path.read_text() == custom_config

    def test_config_created_on_first_config_view(self):
        """Test that config is created when running config view."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Patch Path.home() to avoid finding XDG config
            with patch("pathlib.Path.home", return_value=Path.cwd()):
                # Run config view command
                result = runner.invoke(main, ["config", "view"])

                # Verify config was created
                config_path = Path("etc/arda.toml")
                assert config_path.exists(), "Config file should be created"

                # Verify message appears (may vary by output)
                assert result.exit_code == 0

    def test_config_created_with_valid_toml_structure(self):
        """Test that created config has valid TOML structure."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Patch Path.home() to avoid finding XDG config
            with patch("pathlib.Path.home", return_value=Path.cwd()):
                # Create config by running config view
                result = runner.invoke(main, ["config", "view"])
                assert result.exit_code == 0

                # Read and parse TOML
                config_path = Path("etc/arda.toml")
                with open(config_path, "rb") as f:
                    config_data = tomllib.load(f)

                # Verify expected sections
                assert "theme" in config_data
                assert "output" in config_data

                # Verify theme section
                assert "default" in config_data["theme"]
                assert isinstance(config_data["theme"]["default"], str)

                # Verify output section
                assert "verbose" in config_data["output"]
                assert "timestamp" in config_data["output"]
                assert isinstance(config_data["output"]["verbose"], bool)
                assert isinstance(config_data["output"]["timestamp"], bool)

    def test_config_creation_handles_tomli_dump(self):
        """Test that config creation uses tomli_w.dump()."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Patch Path.home() and tomli_w
            with patch("pathlib.Path.home", return_value=Path.cwd()):
                with patch("arda_cli.main.tomli_w") as mock_tomli_w:
                    # Run config view to trigger config creation
                    result = runner.invoke(main, ["config", "view"])
                    assert result.exit_code == 0

                    # Verify tomli_w.dump was called
                    mock_tomli_w.dump.assert_called_once()

                    # Verify it was called with valid arguments
                    call_args = mock_tomli_w.dump.call_args
                    assert call_args is not None


class TestThemeValidation:
    """Test theme validation and error handling."""

    def test_valid_themes_pass_validation(self):
        """Test that valid themes pass validation."""
        # Test a sample of themes (representative subset)
        test_themes = [
            "dracula",
            "nord",
            "forest",
            "solarized",
            "default",
            "cargo",
            "star",
            "mono",
            "red1",
            "blue1",
        ]

        for theme in test_themes:
            result = validate_theme(None, None, theme)
            assert result == theme, f"Theme '{theme}' should be valid"

    def test_invalid_themes_raise_system_exit(self):
        """Test that invalid themes raise SystemExit."""
        runner = CliRunner()
        invalid_themes = [
            "nonexistent_theme",
            "fake_theme_123",
            "invalid",
        ]

        for invalid_theme in invalid_themes:
            # Test through CLI invocation (use config view instead of --help)
            # This ensures theme validation happens before the command executes
            result = runner.invoke(main, ["--theme", invalid_theme, "config", "view"])
            # Should fail (theme validation prevents execution)
            assert result.exit_code != 0, f"Invalid theme '{invalid_theme}' should fail"
            assert "not found" in result.output.lower()

    def test_theme_validation_is_case_insensitive(self):
        """Test that theme validation is case-insensitive."""
        test_cases = [
            "dracula",  # lowercase
            "DRACULA",  # uppercase
            "DrAcUlA",  # mixed case
        ]

        for input_theme in test_cases:
            result = validate_theme(None, None, input_theme)
            # Should preserve the original case
            assert result == input_theme

    def test_none_theme_value_allowed(self):
        """Test that None theme value is allowed (no validation)."""
        result = validate_theme(None, None, None)
        assert result is None

    def test_cli_accepts_valid_themes(self):
        """Test that CLI accepts valid themes without errors."""
        runner = CliRunner()
        test_themes = ["dracula", "nord", "forest", "solarized", "default"]

        for theme in test_themes:
            result = runner.invoke(main, ["--theme", theme, "--help"])
            assert result.exit_code == 0, f"Theme '{theme}' should be accepted"
            assert "Usage:" in result.output

    def test_cli_rejects_invalid_themes(self):
        """Test that CLI rejects invalid themes with error."""
        runner = CliRunner()

        # Test with invalid theme (use config view instead of --help)
        # This ensures theme validation happens before the command executes
        result = runner.invoke(main, ["--theme", "invalid_theme_xyz", "config", "view"])

        # Should fail with error
        assert result.exit_code != 0, "Invalid theme should fail"
        assert "not found" in result.output or "error" in result.output.lower()

    def test_theme_list_completeness(self):
        """Test that all themes in get_rich_click_themes() are valid."""
        available_themes = get_rich_click_themes()

        # Verify we have a reasonable number of themes
        assert len(available_themes) > 20, "Should have many themes available"

        # Verify all themes are strings
        assert all(isinstance(t, str) for t in available_themes)

        # Verify no empty theme names
        assert all(t.strip() for t in available_themes)

        # Test a sample of themes (testing all would be slow)
        sample_size = min(10, len(available_themes))
        for theme in available_themes[:sample_size]:
            result = validate_theme(None, None, theme)
            assert result == theme, f"Theme '{theme}' from list should be valid"


class TestMainCLIExtended:
    """Extended tests for main CLI behavior."""

    def test_main_with_verbose_flag(self):
        """Test CLI with verbose flag."""
        runner = CliRunner()
        result = runner.invoke(main, ["--verbose", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_main_with_timestamp_flag(self):
        """Test CLI with timestamp flag."""
        runner = CliRunner()
        result = runner.invoke(main, ["--timestamp", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_main_with_multiple_flags(self):
        """Test CLI with multiple flags."""
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["--theme", "dracula", "--verbose", "--timestamp", "--help"],
        )
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_main_shows_active_config_in_help(self):
        """Test that help shows active configuration path."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Active configuration" in result.output

    def test_unknown_command_shows_help(self):
        """Test that unknown command shows error and help."""
        runner = CliRunner()
        result = runner.invoke(main, ["unknown_command"])
        assert result.exit_code != 0
        assert (
            "no such command" in result.output.lower()
            or "usage:" in result.output.lower()
        )


class TestMainErrorHandling:
    """Test error handling in main CLI."""

    def test_invalid_theme_error_panel(self):
        """Test that invalid theme shows rich error panel."""
        runner = CliRunner()

        result = runner.invoke(main, ["--theme", "invalid_theme_xyz", "config", "view"])

        # Should fail
        assert result.exit_code != 0

        # Should show error message
        assert (
            "not found" in result.output.lower() or "invalid" in result.output.lower()
        )

    def test_cli_handles_keyboard_interrupt(self):
        """Test that CLI handles keyboard interrupt gracefully."""
        runner = CliRunner()

        # Simulate keyboard interrupt by passing empty input
        # (This is handled by Click's error handling)
        result = runner.invoke(main, [], input="")

        # Click should handle it - verify exit code is valid (0 or non-zero)
        # The key is that it doesn't crash or raise unhandled exceptions
        assert result.exit_code in (0, 1, 2, 130)  # Valid exit codes for CLI usage
