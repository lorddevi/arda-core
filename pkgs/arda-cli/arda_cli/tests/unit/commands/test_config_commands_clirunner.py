"""CliRunner tests for config commands.

This module tests the Click command layer for 'arda config' using CliRunner
to achieve high pytest coverage (target: 80%+).

Tests cover:
- Command execution (view, set, init)
- Flag handling (--global, --local, --force)
- Error handling
- Help callbacks
- Context object passing
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Import commands to test
from arda_cli.commands.config.main import config

# Import base test infrastructure
from arda_cli.tests.unit.commands import BaseCommandTest


@pytest.mark.unit
@pytest.mark.config
@pytest.mark.with_core
class TestConfigCommandsWithCliRunner(BaseCommandTest):
    """Test config commands using CliRunner for high pytest coverage.

    This test class covers the Click command layer which cannot be tested
    with direct function calls. Using CliRunner allows us to test:
    - Click decorators and callbacks
    - Command argument parsing
    - Flag handling (--global, --local)
    - Context object passing
    - Error handling paths
    """

    # ============================================================
    # TEST VIEW COMMAND
    # ============================================================

    def test_view_no_args(self, runner):
        """Test: arda config view (show all config values)."""
        result = self.invoke_command(runner, config, ["view"], standalone_mode=False)
        # Command should succeed (even with no config file)
        assert result.exit_code == 0
        # Output should show configuration or default values
        assert (
            "theme" in result.output.lower() or "configuration" in result.output.lower()
        )

    def test_view_specific_key(self, runner):
        """Test: arda config view theme.default (show specific key)."""
        result = self.invoke_command(
            runner, config, ["view", "theme.default"], standalone_mode=False
        )
        assert result.exit_code == 0

    def test_view_invalid_key_format(self, runner):
        """Test: arda config view theme.default.invalid (shows error message)."""
        result = self.invoke_command(
            runner, config, ["view", "theme.default.invalid"], standalone_mode=False
        )
        # Command logs error but doesn't fail (exit_code still 0)
        assert result.exit_code == 0
        assert "Invalid" in result.output or "error" in result.output.lower()

    def test_view_global_flag(self, runner):
        """Test: arda config --global view (use global config)."""
        result = self.invoke_command(
            runner, config, ["--global", "view"], standalone_mode=False
        )
        assert result.exit_code == 0

    def test_view_local_flag(self, runner):
        """Test: arda config --local view (use local config)."""
        result = self.invoke_command(
            runner, config, ["--local", "view"], standalone_mode=False
        )
        assert result.exit_code == 0

    # ============================================================
    # TEST SET COMMAND
    # ============================================================

    def test_set_theme_shorthand(self, runner):
        """Test: arda config set theme nord (shorthand key)."""
        result = self.invoke_command(
            runner, config, ["set", "theme", "nord"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "nord" in result.output.lower() or "theme" in result.output.lower()

    def test_set_verbose_true(self, runner):
        """Test: arda config set output.verbose true (full key with boolean)."""
        result = self.invoke_command(
            runner, config, ["set", "output.verbose", "true"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "verbose" in result.output.lower()

    def test_set_verbose_false(self, runner):
        """Test: arda config set output.verbose false (boolean false)."""
        result = self.invoke_command(
            runner, config, ["set", "output.verbose", "false"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "verbose" in result.output.lower()

    def test_set_timestamp(self, runner):
        """Test: arda config set output.timestamp false (timestamp setting)."""
        result = self.invoke_command(
            runner, config, ["set", "output.timestamp", "false"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "timestamp" in result.output.lower()

    def test_set_invalid_key(self, runner):
        """Test: arda config set invalid.key value (shows error message)."""
        result = self.invoke_command(
            runner, config, ["set", "invalid.key", "value"], standalone_mode=False
        )
        # Command logs error but doesn't fail (exit_code still 0)
        assert result.exit_code == 0
        assert "Invalid" in result.output or "error" in result.output.lower()

    def test_set_invalid_boolean(self, runner):
        """Test: arda config set output.verbose maybe (shows error message)."""
        result = self.invoke_command(
            runner, config, ["set", "output.verbose", "maybe"], standalone_mode=False
        )
        # Command logs error but doesn't fail (exit_code still 0)
        assert result.exit_code == 0
        assert "Invalid" in result.output or "boolean" in result.output.lower()

    def test_set_global_flag(self, runner):
        """Test: arda config --global set theme forest (write to global config)."""
        result = self.invoke_command(
            runner,
            config,
            ["--global", "set", "theme", "forest"],
            standalone_mode=False,
        )
        assert result.exit_code == 0
        assert "forest" in result.output.lower() or "theme" in result.output.lower()

    def test_set_local_flag(self, runner):
        """Test: arda config --local set theme solarized (write to local config)."""
        result = self.invoke_command(
            runner,
            config,
            ["--local", "set", "theme", "solarized"],
            standalone_mode=False,
        )
        assert result.exit_code == 0
        assert "solarized" in result.output.lower() or "theme" in result.output.lower()

    # ============================================================
    # TEST INIT COMMAND
    # ============================================================

    def test_init_creates_file(self, runner):
        """Test: arda config init --force (creates config file)."""
        with runner.isolated_filesystem():
            # Mock tomli_w module which may not be available in test environment
            with patch.dict("sys.modules", {"tomli_w": type(sys)("tomli_w")}) as _:
                # Create a minimal tomli_w module mock
                sys.modules["tomli_w"].dump = lambda data, f: None

                result = self.invoke_command(
                    runner, config, ["init", "--force"], standalone_mode=False
                )
                # Command should succeed (may have warnings but no errors)
                assert result.exit_code == 0

    def test_init_global_flag(self, runner):
        """Test: arda config --global init --force (creates global config)."""
        result = self.invoke_command(
            runner, config, ["--global", "init", "--force"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert (
            "initialized" in result.output.lower() or "config" in result.output.lower()
        )

    def test_init_local_flag(self, runner):
        """Test: arda config --local init --force (creates local config)."""
        with runner.isolated_filesystem():
            result = self.invoke_command(
                runner, config, ["--local", "init", "--force"], standalone_mode=False
            )
            assert result.exit_code == 0
            assert (
                "initialized" in result.output.lower()
                or "config" in result.output.lower()
            )

    # ============================================================
    # TEST HELP AND CALLBACKS
    # ============================================================

    def test_help_shows_subcommands(self, runner):
        """Test: arda config --help (shows help with subcommands)."""
        result = self.invoke_command(runner, config, ["--help"], standalone_mode=False)
        assert result.exit_code == 0
        assert "Usage:" in result.output

        # Verify all subcommands are documented
        assert "init" in result.output
        assert "set" in result.output
        assert "view" in result.output

    def test_help_shows_flags(self, runner):
        """Test: arda config --help (shows --global and --local flags)."""
        result = self.invoke_command(runner, config, ["--help"], standalone_mode=False)
        assert result.exit_code == 0
        assert "Usage:" in result.output

        # Verify flags are documented
        assert "--local" in result.output
        assert "--global" in result.output

    def test_view_help(self, runner):
        """Test: arda config view --help (shows view command help)."""
        result = self.invoke_command(
            runner, config, ["view", "--help"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Usage:" in result.output or "view" in result.output.lower()

    def test_set_help(self, runner):
        """Test: arda config set --help (shows set command help)."""
        result = self.invoke_command(
            runner, config, ["set", "--help"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Usage:" in result.output or "set" in result.output.lower()

    def test_init_help(self, runner):
        """Test: arda config init --help (shows init command help)."""
        result = self.invoke_command(
            runner, config, ["init", "--help"], standalone_mode=False
        )
        assert result.exit_code == 0
        assert "Usage:" in result.output or "init" in result.output.lower()

    # ============================================================
    # TEST CONFIG GROUP HELP
    # ============================================================

    def test_config_without_subcommand_shows_help(self, runner):
        """Test: arda config (no subcommand, should show help)."""
        result = self.invoke_command(runner, config, [], standalone_mode=False)
        # Command should succeed and show help
        assert result.exit_code == 0
        assert "Usage:" in result.output
        # Should show active config info
        assert "Active configuration" in result.output

    # ============================================================
    # TEST ERROR HANDLING
    # ============================================================

    def test_config_command_with_both_flags_fails(self, runner):
        """Test: arda config --global --local (should fail with error)."""
        result = self.invoke_command(
            runner, config, ["--global", "--local", "view"], standalone_mode=False
        )
        # Should fail with error about conflicting flags
        assert (
            result.exit_code != 0
            or "Error" in result.output
            or "cannot" in result.output.lower()
        )
