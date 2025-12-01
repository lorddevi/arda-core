"""Unit tests for pytest_helpers module.

This test suite ensures comprehensive coverage of all helper functions
used throughout the arda-core testing infrastructure.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from arda_cli.testing.helpers.pytest_helpers import (
    MockNixCommand,
    MockSubprocessResult,
    TempDirectory,
    assert_config_values,
    assert_file_contains,
    assert_file_exists,
    assert_theme_config,
    cleanup_temp_file,
    create_mock_nix_eval_failure,
    create_mock_nix_eval_success,
    create_temp_config_file,
    create_test_theme_config,
)


class TestCreateTempConfigFile:
    """Test create_temp_config_file function."""

    @pytest.mark.unit
    def test_create_temp_config_with_tomli_w(self):
        """Test config file creation using tomli_w."""
        config_dict = {
            "theme": {"default": "dracula"},
            "output": {"verbose": True, "timestamp": False},
        }

        config_path = create_temp_config_file(config_dict)

        assert config_path.exists()
        assert config_path.suffix == ".toml"

        # Clean up
        cleanup_temp_file(config_path)

    @pytest.mark.unit
    def test_create_temp_config_with_string_output(self):
        """Test config file creation handles different config types."""
        config_dict = {"theme": {"default": "solarized"}}

        config_path = create_temp_config_file(config_dict)

        assert config_path.exists()
        assert config_path.suffix == ".toml"

        # Clean up
        cleanup_temp_file(config_path)


class TestAssertConfigValues:
    """Test assert_config_values function."""

    @pytest.mark.unit
    def test_assert_config_values_all_match(self):
        """Test assertion passes when all values match."""
        config = {"theme": "dracula", "verbose": True, "timestamp": False}
        expected = {"theme": "dracula", "verbose": True, "timestamp": False}

        assert_config_values(config, expected)

    @pytest.mark.unit
    def test_assert_config_values_missing_key(self):
        """Test assertion fails when key is missing."""
        config = {"theme": "dracula", "verbose": True}
        expected = {"theme": "dracula", "verbose": True, "timestamp": False}

        with pytest.raises(AssertionError, match="Key 'timestamp' not found in config"):
            assert_config_values(config, expected)

    @pytest.mark.unit
    def test_assert_config_values_wrong_value(self):
        """Test assertion fails when value doesn't match."""
        config = {"theme": "dracula", "verbose": True}
        expected = {"theme": "forest", "verbose": True}

        with pytest.raises(AssertionError, match="Expected theme=forest"):
            assert_config_values(config, expected)

    @pytest.mark.unit
    def test_assert_config_values_partial_match(self):
        """Test assertion passes when checking subset of values."""
        config = {
            "theme": "dracula",
            "verbose": True,
            "timestamp": False,
            "extra": "value",
        }
        expected = {"theme": "dracula", "verbose": True}

        assert_config_values(config, expected)


class TestMockSubprocessResult:
    """Test MockSubprocessResult class."""

    @pytest.mark.unit
    def test_mock_result_with_strings(self):
        """Test MockSubprocessResult with string inputs."""
        result = MockSubprocessResult(stdout="success", stderr="error", returncode=1)

        assert result.stdout == b"success"
        assert result.stderr == b"error"
        assert result.returncode == 1

    @pytest.mark.unit
    def test_mock_result_with_bytes(self):
        """Test MockSubprocessResult with bytes inputs."""
        result = MockSubprocessResult(stdout=b"success", stderr=b"error", returncode=0)

        assert result.stdout == b"success"
        assert result.stderr == b"error"
        assert result.returncode == 0

    @pytest.mark.unit
    def test_mock_result_defaults(self):
        """Test MockSubprocessResult with default values."""
        result = MockSubprocessResult()

        assert result.stdout == b""
        assert result.stderr == b""
        assert result.returncode == 0


class TestCreateMockNixEval:
    """Test create_mock_nix_eval_success and create_mock_nix_eval_failure."""

    @pytest.mark.unit
    def test_create_mock_nix_eval_success(self):
        """Test successful nix eval mock."""
        result = create_mock_nix_eval_success("mock output")

        assert isinstance(result, MockSubprocessResult)
        assert result.stdout == b"mock output"
        assert result.stderr == b""
        assert result.returncode == 0

    @pytest.mark.unit
    def test_create_mock_nix_eval_failure(self):
        """Test failed nix eval mock."""
        result = create_mock_nix_eval_failure("error message")

        assert isinstance(result, MockSubprocessResult)
        assert result.stdout == b""
        assert result.stderr == b"error message"
        assert result.returncode == 1


class TestCleanupTempFile:
    """Test cleanup_temp_file function."""

    @pytest.mark.unit
    def test_cleanup_temp_file_exists(self):
        """Test cleanup deletes existing file."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(b"test")

        assert tmp_path.exists()

        cleanup_temp_file(tmp_path)

        assert not tmp_path.exists()

    @pytest.mark.unit
    def test_cleanup_temp_file_none(self):
        """Test cleanup handles None gracefully."""
        cleanup_temp_file(None)

    @pytest.mark.unit
    def test_cleanup_temp_file_not_exists(self):
        """Test cleanup handles non-existent file gracefully."""
        fake_path = Path("nonexistent_file_12345.txt")
        cleanup_temp_file(fake_path)


class TestTempDirectory:
    """Test TempDirectory context manager."""

    @pytest.mark.unit
    def test_temp_directory_creates_and_cleans_up(self):
        """Test TempDirectory creates and cleans up temp directory."""
        with TempDirectory() as temp_dir:
            assert isinstance(temp_dir, Path)
            assert temp_dir.exists()
            assert temp_dir.is_dir()

        # Directory should be cleaned up after context
        assert not temp_dir.exists()

    @pytest.mark.unit
    def test_temp_directory_isolated(self):
        """Test each TempDirectory instance is isolated."""
        with TempDirectory() as temp_dir1:
            with TempDirectory() as temp_dir2:
                assert temp_dir1 != temp_dir2


class TestCreateTestThemeConfig:
    """Test create_test_theme_config function."""

    @pytest.mark.unit
    def test_create_test_theme_config_default(self):
        """Test default theme config creation."""
        config = create_test_theme_config()

        assert "theme" in config
        assert "name" in config["theme"]
        assert config["theme"]["name"] == "dracula"
        assert config["verbose"] is False
        assert config["timestamp"] is True

    @pytest.mark.unit
    def test_create_test_theme_config_custom(self):
        """Test custom theme config creation."""
        config = create_test_theme_config("forest")

        assert config["theme"]["name"] == "forest"
        assert "primary_color" in config["theme"]
        assert "secondary_color" in config["theme"]


class TestAssertThemeConfig:
    """Test assert_theme_config function."""

    @pytest.mark.unit
    def test_assert_theme_config_correct(self):
        """Test assertion passes with correct theme."""
        config = create_test_theme_config("nord")
        assert_theme_config(config, "nord")

    @pytest.mark.unit
    def test_assert_theme_config_missing_section(self):
        """Test assertion fails when theme section is missing."""
        config = {"verbose": False, "timestamp": True}

        with pytest.raises(AssertionError, match="Config missing 'theme' section"):
            assert_theme_config(config, "dracula")

    @pytest.mark.unit
    def test_assert_theme_config_missing_name(self):
        """Test assertion fails when theme name is missing."""
        config = {"theme": {"primary_color": "#282936"}}

        with pytest.raises(AssertionError, match="Theme missing 'name' field"):
            assert_theme_config(config, "dracula")

    @pytest.mark.unit
    def test_assert_theme_config_wrong_name(self):
        """Test assertion fails when theme name doesn't match."""
        config = {"theme": {"name": "forest"}}

        with pytest.raises(AssertionError, match="Expected theme 'dracula'"):
            assert_theme_config(config, "dracula")


class TestMockNixCommand:
    """Test MockNixCommand class."""

    @pytest.mark.unit
    def test_mock_nix_command_success(self):
        """Test MockNixCommand with success=True."""
        mock_cmd = MockNixCommand(success=True, output="success output")

        assert mock_cmd.success is True
        assert mock_cmd.output == "success output"
        assert mock_cmd.call_count == 0

        # First call
        result = mock_cmd()
        assert mock_cmd.call_count == 1
        assert isinstance(result, MockSubprocessResult)
        assert result.stdout == b"success output"
        assert result.returncode == 0

        # Second call
        result2 = mock_cmd()
        assert mock_cmd.call_count == 2

    @pytest.mark.unit
    def test_mock_nix_command_failure(self):
        """Test MockNixCommand with success=False."""
        mock_cmd = MockNixCommand(success=False, output="error output")

        assert mock_cmd.success is False
        assert mock_cmd.output == "error output"

        result = mock_cmd()
        assert isinstance(result, MockSubprocessResult)
        assert result.stderr == b"error output"
        assert result.returncode == 1

    @pytest.mark.unit
    def test_mock_nix_command_multiple_calls(self):
        """Test MockNixCommand tracks call count."""
        mock_cmd = MockNixCommand(success=True, output="output")

        for i in range(1, 6):
            mock_cmd()
            assert mock_cmd.call_count == i


class TestAssertFileOperations:
    """Test assert_file_exists and assert_file_contains functions."""

    @pytest.mark.unit
    def test_assert_file_exists_success(self):
        """Test assertion passes when file exists."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(b"test")

        assert_file_exists(tmp_path)

        # Clean up
        cleanup_temp_file(tmp_path)

    @pytest.mark.unit
    def test_assert_file_exists_failure(self):
        """Test assertion fails when file doesn't exist."""
        fake_path = Path("nonexistent_file_12345.txt")

        with pytest.raises(AssertionError, match="file should exist"):
            assert_file_exists(fake_path)

    @pytest.mark.unit
    def test_assert_file_contains_success(self):
        """Test assertion passes when file contains content."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write("Hello, world!")

        assert_file_contains(tmp_path, "Hello")

        # Clean up
        cleanup_temp_file(tmp_path)

    @pytest.mark.unit
    def test_assert_file_contains_failure(self):
        """Test assertion fails when file doesn't contain content."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write("Hello, world!")

        with pytest.raises(AssertionError, match="should contain 'Goodbye'"):
            assert_file_contains(tmp_path, "Goodbye")

        # Clean up
        cleanup_temp_file(tmp_path)

    @pytest.mark.unit
    def test_assert_file_contains_with_description(self):
        """Test assertion with custom description."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write("test content")

        assert_file_contains(tmp_path, "test", "config file")

        # Clean up
        cleanup_temp_file(tmp_path)
