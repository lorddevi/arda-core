"""Base infrastructure for Click command testing with CliRunner.

This module provides base classes and fixtures for testing Click commands
using CliRunner. It enables high pytest coverage for the command layer.
"""

import tempfile
from pathlib import Path
from typing import Any, Optional

import pytest
from click.testing import CliRunner


class BaseCommandTest:
    """Base class for Click command tests using CliRunner.

    This class provides common fixtures and utilities for testing Click commands.
    It should be inherited by all command test classes.
    """

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CliRunner fixture for testing Click commands."""
        return CliRunner()

    @pytest.fixture
    def temp_dir(self) -> Path:
        """Create a temporary directory for tests that need file operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def temp_config_dir(self, temp_dir: Path) -> Path:
        """Create a temporary directory with an etc subdirectory for config tests."""
        config_dir = temp_dir / "etc"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def invoke_command(
        self,
        runner: CliRunner,
        command: Any,
        args: list,
        *,
        env: dict[str, str] | None = None,
        catch_exceptions: bool = False,
        standalone_mode: bool = False,
        obj: dict[str, Any] | None = None,
        **kwargs: Any
    ) -> Any:
        """Invoke a Click command with CliRunner.

        This is a convenience method that wraps CliRunner.invoke with
        consistent defaults for testing arda-cli commands.

        Args:
            runner: The CliRunner instance
            command: The Click command to invoke
            args: List of command-line arguments
            env: Environment variables
            catch_exceptions: Whether to catch exceptions
            standalone_mode: Click standalone mode
            obj: Context object to pass to the command
            **kwargs: Additional keyword arguments for the command

        Returns:
            The result object from CliRunner.invoke

        """
        invoke_kwargs = {
            "args": args,
            "catch_exceptions": catch_exceptions,
            "standalone_mode": standalone_mode,
        }

        if env is not None:
            invoke_kwargs["env"] = env

        if obj is not None:
            invoke_kwargs["obj"] = obj

        return runner.invoke(command, **invoke_kwargs)

    def assert_command_success(
        self, result: Any, output_contains: str | None = None
    ) -> None:
        """Assert that a command executed successfully.

        Args:
            result: The result object from invoke_command
            output_contains: Optional string that should be in the output

        """
        assert result.exit_code == 0, (
            f"Command failed with exit code {result.exit_code}. "
            f"Output: {result.output}"
        )

        if output_contains:
            assert output_contains.lower() in result.output.lower(), (
                f"Expected '{output_contains}' in output. "
                f"Got: {result.output}"
            )

    def assert_command_failure(
        self, result: Any, error_contains: str | None = None
    ) -> None:
        """Assert that a command failed as expected.

        Args:
            result: The result object from invoke_command
            error_contains: Optional string that should be in the error output

        """
        assert result.exit_code != 0, (
            f"Command should have failed but succeeded. Output: {result.output}"
        )

        if error_contains:
            assert error_contains.lower() in result.output.lower(), (
                f"Expected '{error_contains}' in error output. "
                f"Got: {result.output}"
            )

    def assert_help_output(self, result: Any) -> None:
        """Assert that the result shows help output.

        Args:
            result: The result object from invoke_command

        """
        assert result.exit_code == 0
        assert "Usage:" in result.output or "help" in result.output.lower()


class CommandContextHelper:
    """Helper for creating context objects for command tests.

    This class provides methods to create properly formatted context objects
    that Click commands expect.
    """

    @staticmethod
    def create_base_context() -> dict[str, Any]:
        """Create a basic context object with default values."""
        return {
            "theme": "dracula",
            "verbose": False,
            "timestamp": False,
            "force_global": False,
            "force_local": False,
        }

    @staticmethod
    def create_config_context(
        force_global: bool = False, force_local: bool = False
    ) -> dict[str, Any]:
        """Create a context object for config commands."""
        context = CommandContextHelper.create_base_context()
        context["force_global"] = force_global
        context["force_local"] = force_local
        return context

    @staticmethod
    def create_theme_context(theme: str = "dracula") -> dict[str, Any]:
        """Create a context object for theme commands."""
        context = CommandContextHelper.create_base_context()
        context["theme"] = theme
        return context
