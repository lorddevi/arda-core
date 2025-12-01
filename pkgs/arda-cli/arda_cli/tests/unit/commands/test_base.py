"""Unit tests for commands/base.py infrastructure.

This test suite ensures comprehensive coverage of all base classes,
fixtures, and utilities used throughout the command testing layer.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from arda_cli.tests.unit.commands.base import BaseCommandTest, CommandContextHelper


class MockCommand:
    """Mock Click command for testing."""

    def __init__(self, name="test_command"):
        self.name = name


class TestBaseCommandTest:
    """Test BaseCommandTest class."""

    @pytest.mark.unit
    def test_base_command_test_has_no_init(self):
        """Test that BaseCommandTest can be instantiated."""
        test = BaseCommandTest()
        assert test is not None

    @pytest.mark.unit
    def test_invoke_command_basic(self):
        """Test invoke_command with basic parameters."""
        test = BaseCommandTest()
        runner = CliRunner()  # Create directly instead of using fixture
        mock_cmd = MockCommand()

        # Mock the invoke method to avoid actually running commands
        with patch.object(runner, "invoke", return_value=MagicMock()) as mock_invoke:
            result = test.invoke_command(runner, mock_cmd, ["arg1", "arg2"])

            # Verify invoke was called
            assert mock_invoke.called

            # Get the call arguments
            call_args, call_kwargs = mock_invoke.call_args
            assert call_args[0] == mock_cmd
            assert call_kwargs["args"] == ["arg1", "arg2"]
            assert call_kwargs["catch_exceptions"] is False
            assert call_kwargs["standalone_mode"] is False

    @pytest.mark.unit
    def test_invoke_command_with_env(self):
        """Test invoke_command with environment variables."""
        test = BaseCommandTest()
        runner = CliRunner()
        mock_cmd = MockCommand()

        with patch.object(runner, "invoke", return_value=MagicMock()) as mock_invoke:
            env = {"TEST_VAR": "test_value"}
            result = test.invoke_command(runner, mock_cmd, [], env=env)

            # Verify env was passed
            _, call_kwargs = mock_invoke.call_args
            assert "env" in call_kwargs
            assert call_kwargs["env"] == env

    @pytest.mark.unit
    def test_invoke_command_with_obj(self):
        """Test invoke_command with context object."""
        test = BaseCommandTest()
        runner = CliRunner()
        mock_cmd = MockCommand()

        with patch.object(runner, "invoke", return_value=MagicMock()) as mock_invoke:
            obj = {"key": "value"}
            result = test.invoke_command(runner, mock_cmd, [], obj=obj)

            # Verify obj was passed
            _, call_kwargs = mock_invoke.call_args
            assert "obj" in call_kwargs
            assert call_kwargs["obj"] == obj

    @pytest.mark.unit
    def test_invoke_command_with_options(self):
        """Test invoke_command with various options."""
        test = BaseCommandTest()
        runner = CliRunner()
        mock_cmd = MockCommand()

        with patch.object(runner, "invoke", return_value=MagicMock()) as mock_invoke:
            result = test.invoke_command(
                runner,
                mock_cmd,
                [],
                catch_exceptions=True,
                standalone_mode=False,
            )

            _, call_kwargs = mock_invoke.call_args
            assert call_kwargs["catch_exceptions"] is True
            assert call_kwargs["standalone_mode"] is False

    @pytest.mark.unit
    def test_invoke_command_without_env_and_obj(self):
        """Test invoke_command without optional parameters."""
        test = BaseCommandTest()
        runner = CliRunner()
        mock_cmd = MockCommand()

        with patch.object(runner, "invoke", return_value=MagicMock()) as mock_invoke:
            result = test.invoke_command(runner, mock_cmd, [])

            # Verify neither env nor obj is in kwargs
            _, call_kwargs = mock_invoke.call_args
            assert "env" not in call_kwargs
            assert "obj" not in call_kwargs

    @pytest.mark.unit
    def test_invoke_command_returns_result(self):
        """Test that invoke_command returns the result from runner.invoke."""
        test = BaseCommandTest()
        runner = CliRunner()
        mock_cmd = MockCommand()

        expected_result = MagicMock()
        with patch.object(
            runner, "invoke", return_value=expected_result
        ) as mock_invoke:
            result = test.invoke_command(runner, mock_cmd, [])

            # Verify the result is returned
            assert result == expected_result

    @pytest.mark.unit
    def test_assert_command_success_without_output_check(self):
        """Test assert_command_success without output check."""
        test = BaseCommandTest()

        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.output = "Command succeeded"

        # Should not raise any error
        test.assert_command_success(mock_result)

    @pytest.mark.unit
    def test_assert_command_success_with_output_check(self):
        """Test assert_command_success with output check."""
        test = BaseCommandTest()

        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.output = "Command succeeded with important info"

        # Should not raise any error
        test.assert_command_success(mock_result, output_contains="important info")

    @pytest.mark.unit
    def test_assert_command_success_with_mixed_case(self):
        """Test assert_command_success handles case-insensitive matching."""
        test = BaseCommandTest()

        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.output = "IMPORTANT INFO"

        # Should match case-insensitively
        test.assert_command_success(mock_result, output_contains="important info")

    @pytest.mark.unit
    def test_assert_command_success_fails_on_nonzero_exit(self):
        """Test assert_command_success fails on non-zero exit code."""
        test = BaseCommandTest()

        mock_result = MagicMock()
        mock_result.exit_code = 1
        mock_result.output = "Command failed"

        # Should raise AssertionError
        with pytest.raises(AssertionError, match="Command failed with exit code 1"):
            test.assert_command_success(mock_result)

    @pytest.mark.unit
    def test_assert_command_success_fails_on_missing_output(self):
        """Test assert_command_success fails on missing expected output."""
        test = BaseCommandTest()

        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.output = "Some other output"

        # Should raise AssertionError
        with pytest.raises(AssertionError, match="Expected 'missing text' in output"):
            test.assert_command_success(mock_result, output_contains="missing text")

    @pytest.mark.unit
    def test_assert_command_failure_without_error_check(self):
        """Test assert_command_failure without error check."""
        test = BaseCommandTest()

        mock_result = MagicMock()
        mock_result.exit_code = 1
        mock_result.output = "Command failed"

        # Should not raise any error
        test.assert_command_failure(mock_result)

    @pytest.mark.unit
    def test_assert_command_failure_with_error_check(self):
        """Test assert_command_failure with error check."""
        test = BaseCommandTest()

        mock_result = MagicMock()
        mock_result.exit_code = 1
        mock_result.output = "Command failed with error"

        # Should not raise any error
        test.assert_command_failure(mock_result, error_contains="error")

    @pytest.mark.unit
    def test_assert_command_failure_with_mixed_case(self):
        """Test assert_command_failure handles case-insensitive matching."""
        test = BaseCommandTest()

        mock_result = MagicMock()
        mock_result.exit_code = 1
        mock_result.output = "ERROR MESSAGE"

        # Should match case-insensitively
        test.assert_command_failure(mock_result, error_contains="error message")

    @pytest.mark.unit
    def test_assert_command_failure_fails_on_zero_exit(self):
        """Test assert_command_failure fails on zero exit code."""
        test = BaseCommandTest()

        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.output = "Command succeeded"

        # Should raise AssertionError
        with pytest.raises(AssertionError, match="should have failed but succeeded"):
            test.assert_command_failure(mock_result)

    @pytest.mark.unit
    def test_assert_command_failure_fails_on_missing_error_text(self):
        """Test assert_command_failure fails on missing expected error text."""
        test = BaseCommandTest()

        mock_result = MagicMock()
        mock_result.exit_code = 1
        mock_result.output = "Some error"

        # Should raise AssertionError
        with pytest.raises(
            AssertionError, match="Expected 'missing error' in error output"
        ):
            test.assert_command_failure(mock_result, error_contains="missing error")

    @pytest.mark.unit
    def test_assert_help_output_success(self):
        """Test assert_help_output succeeds on help output."""
        test = BaseCommandTest()

        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.output = "Usage: arda [OPTIONS] COMMAND"

        # Should not raise any error
        test.assert_help_output(mock_result)

    @pytest.mark.unit
    def test_assert_help_output_with_help_text(self):
        """Test assert_help_output succeeds on text containing help."""
        test = BaseCommandTest()

        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.output = "Help: This is help text"

        # Should not raise any error
        test.assert_help_output(mock_result)

    @pytest.mark.unit
    def test_assert_help_output_fails_on_nonzero_exit(self):
        """Test assert_help_output fails on non-zero exit code."""
        test = BaseCommandTest()

        mock_result = MagicMock()
        mock_result.exit_code = 1
        mock_result.output = "Usage: arda [OPTIONS]"

        # Should raise AssertionError
        with pytest.raises(AssertionError):
            test.assert_help_output(mock_result)

    @pytest.mark.unit
    def test_assert_help_output_fails_on_invalid_output(self):
        """Test assert_help_output fails on invalid output."""
        test = BaseCommandTest()

        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.output = (
            "This is random output without usage or any assistance text"
        )

        # Should raise AssertionError
        with pytest.raises(AssertionError):
            test.assert_help_output(mock_result)


class TestCommandContextHelper:
    """Test CommandContextHelper class."""

    @pytest.mark.unit
    def test_create_base_context(self):
        """Test create_base_context creates expected context."""
        context = CommandContextHelper.create_base_context()

        assert isinstance(context, dict)
        assert context["theme"] == "dracula"
        assert context["verbose"] is False
        assert context["timestamp"] is False
        assert context["force_global"] is False
        assert context["force_local"] is False

    @pytest.mark.unit
    def test_create_config_context_default(self):
        """Test create_config_context with default parameters."""
        context = CommandContextHelper.create_config_context()

        assert isinstance(context, dict)
        assert context["theme"] == "dracula"
        assert context["verbose"] is False
        assert context["timestamp"] is False
        assert context["force_global"] is False
        assert context["force_local"] is False

    @pytest.mark.unit
    def test_create_config_context_force_global(self):
        """Test create_config_context with force_global=True."""
        context = CommandContextHelper.create_config_context(force_global=True)

        assert context["force_global"] is True
        assert context["force_local"] is False
        # Other values should still be present
        assert context["theme"] == "dracula"

    @pytest.mark.unit
    def test_create_config_context_force_local(self):
        """Test create_config_context with force_local=True."""
        context = CommandContextHelper.create_config_context(force_local=True)

        assert context["force_local"] is True
        assert context["force_global"] is False
        # Other values should still be present
        assert context["theme"] == "dracula"

    @pytest.mark.unit
    def test_create_config_context_both_flags(self):
        """Test create_config_context with both flags."""
        context = CommandContextHelper.create_config_context(
            force_global=True, force_local=True
        )

        assert context["force_global"] is True
        assert context["force_local"] is True

    @pytest.mark.unit
    def test_create_theme_context_default(self):
        """Test create_theme_context with default theme."""
        context = CommandContextHelper.create_theme_context()

        assert context["theme"] == "dracula"
        assert context["verbose"] is False
        assert context["timestamp"] is False
        assert context["force_global"] is False
        assert context["force_local"] is False

    @pytest.mark.unit
    def test_create_theme_context_custom(self):
        """Test create_theme_context with custom theme."""
        context = CommandContextHelper.create_theme_context(theme="nord")

        assert context["theme"] == "nord"
        assert context["verbose"] is False
        assert context["timestamp"] is False
        assert context["force_global"] is False
        assert context["force_local"] is False

    @pytest.mark.unit
    def test_create_theme_context_various_themes(self):
        """Test create_theme_context with various themes."""
        themes = ["dracula", "nord", "forest", "solarized", "default"]

        for theme_name in themes:
            context = CommandContextHelper.create_theme_context(theme=theme_name)
            assert context["theme"] == theme_name
            # Verify all expected keys are present
            assert "verbose" in context
            assert "timestamp" in context
            assert "force_global" in context
            assert "force_local" in context

    @pytest.mark.unit
    def test_all_contexts_are_dicts(self):
        """Test that all context methods return dicts."""
        contexts = [
            CommandContextHelper.create_base_context(),
            CommandContextHelper.create_config_context(),
            CommandContextHelper.create_config_context(force_global=True),
            CommandContextHelper.create_config_context(force_local=True),
            CommandContextHelper.create_theme_context(),
            CommandContextHelper.create_theme_context(theme="nord"),
        ]

        for context in contexts:
            assert isinstance(context, dict)

    @pytest.mark.unit
    def test_contexts_are_independent(self):
        """Test that contexts created separately are independent."""
        context1 = CommandContextHelper.create_config_context(force_global=True)
        context2 = CommandContextHelper.create_config_context(force_local=True)

        # Modifying one should not affect the other
        assert context1["force_global"] is True
        assert context1["force_local"] is False
        assert context2["force_global"] is False
        assert context2["force_local"] is True


class TestIntegration:
    """Integration tests combining multiple features."""

    @pytest.mark.unit
    def test_full_command_test_workflow(self):
        """Test a complete workflow using BaseCommandTest methods."""
        test = BaseCommandTest()
        runner = CliRunner()  # Use CliRunner directly
        mock_cmd = MockCommand()

        # Mock invoke to return a successful result
        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.output = "Command executed successfully"

        with patch.object(runner, "invoke", return_value=mock_result):
            # Invoke command
            result = test.invoke_command(runner, mock_cmd, ["arg1"])

            # Assert success
            test.assert_command_success(result)

    @pytest.mark.unit
    def test_failure_workflow(self):
        """Test failure handling workflow."""
        test = BaseCommandTest()
        runner = CliRunner()
        mock_cmd = MockCommand()

        # Mock invoke to return a failed result
        mock_result = MagicMock()
        mock_result.exit_code = 1
        mock_result.output = "Command failed with error"

        with patch.object(runner, "invoke", return_value=mock_result):
            # Invoke command
            result = test.invoke_command(runner, mock_cmd, ["arg1"])

            # Assert failure
            test.assert_command_failure(result, error_contains="error")

    @pytest.mark.unit
    def test_help_workflow(self):
        """Test help output workflow."""
        test = BaseCommandTest()
        runner = CliRunner()
        mock_cmd = MockCommand()

        # Mock invoke to return help result
        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.output = "Usage: arda [OPTIONS]"

        with patch.object(runner, "invoke", return_value=mock_result):
            # Invoke command
            result = test.invoke_command(runner, mock_cmd, ["--help"])

            # Assert help output
            test.assert_help_output(result)

    @pytest.mark.unit
    def test_help_output_invalid_should_fail(self):
        """Test that assert_help_output fails on invalid output."""
        test = BaseCommandTest()

        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.output = "Some random output without usage or assistance text"

        # Should raise AssertionError
        with pytest.raises(AssertionError):
            test.assert_help_output(mock_result)

    @pytest.mark.unit
    def test_context_helper_with_config_command(self):
        """Test creating context for a config command."""
        context = CommandContextHelper.create_config_context(force_global=True)

        # This context should have all required keys for config commands
        expected_keys = ["theme", "verbose", "timestamp", "force_global", "force_local"]
        for key in expected_keys:
            assert key in context

    @pytest.mark.unit
    def test_context_helper_with_theme_command(self):
        """Test creating context for a theme command."""
        context = CommandContextHelper.create_theme_context(theme="nord")

        # This context should have all required keys for theme commands
        assert context["theme"] == "nord"
        expected_keys = ["theme", "verbose", "timestamp", "force_global", "force_local"]
        for key in expected_keys:
            assert key in context
