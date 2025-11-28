"""Shared pytest helpers and utilities for arda-core testing."""

import tempfile
from pathlib import Path
from typing import Any


def create_temp_config_file(config_dict: dict[str, Any]) -> Path:
    """Create a temporary config file for testing.

    Args:
        config_dict: Dictionary to write as TOML

    Returns:
        Path to the temporary config file

    """
    try:
        import tomli_w
    except ImportError:
        # Fallback for environments without tomli_w
        import toml

        temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        toml_str = toml.dumps(config_dict)
        temp_file.write(toml_str)
        temp_file.close()
        return Path(temp_file.name)

    temp_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".toml", delete=False)

    toml_data = tomli_w.dumps(config_dict)
    # tomli_w might return str in some versions, ensure bytes
    if isinstance(toml_data, str):
        toml_data = toml_data.encode("utf-8")
    temp_file.write(toml_data)
    temp_file.close()

    return Path(temp_file.name)


def assert_config_values(config: dict[str, Any], expected: dict[str, Any]) -> None:
    """Assert that config contains expected values.

    Args:
        config: Actual config dictionary
        expected: Expected config dictionary

    """
    for key, value in expected.items():
        assert key in config, f"Key '{key}' not found in config"
        assert config[key] == value, f"Expected {key}={value}, got {key}={config[key]}"


class MockSubprocessResult:
    """Mock subprocess.run result for testing."""

    def __init__(self, stdout: str = "", stderr: str = "", returncode: int = 0):
        self.stdout = stdout.encode() if isinstance(stdout, str) else stdout
        self.stderr = stderr.encode() if isinstance(stderr, str) else stderr
        self.returncode = returncode


def create_mock_nix_eval_success(output: str) -> MockSubprocessResult:
    """Create a mock subprocess result for successful nix eval.

    Args:
        output: The output string from nix eval

    Returns:
        MockSubprocessResult configured for success

    """
    return MockSubprocessResult(stdout=output, stderr="", returncode=0)


def create_mock_nix_eval_failure(error_message: str) -> MockSubprocessResult:
    """Create a mock subprocess result for failed nix eval.

    Args:
        error_message: The error message

    Returns:
        MockSubprocessResult configured for failure

    """
    return MockSubprocessResult(stdout="", stderr=error_message, returncode=1)


def cleanup_temp_file(path: Path | None) -> None:
    """Clean up a temporary file.

    Args:
        path: Path to the file to delete

    """
    if path and path.exists():
        path.unlink()


class TempDirectory:
    """Context manager for temporary directories."""

    def __init__(self):
        self.path: Path | None = None

    def __enter__(self) -> Path:
        """Enter the temporary directory context.

        Returns:
            Path to the created temporary directory.

        """
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the temporary directory context and clean up.

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred

        """
        if self.path and self.path.exists():
            import shutil

            shutil.rmtree(self.path)


def create_test_theme_config(theme_name: str = "dracula") -> dict[str, Any]:
    """Create a test theme configuration.

    Args:
        theme_name: Name of the theme to use

    Returns:
        Configuration dictionary with theme settings

    """
    return {
        "theme": {
            "name": theme_name,
            "primary_color": "#282936",
            "secondary_color": "#44475a",
        },
        "verbose": False,
        "timestamp": True,
    }


def assert_theme_config(config: dict[str, Any], expected_theme: str) -> None:
    """Assert that config has expected theme.

    Args:
        config: Configuration dictionary
        expected_theme: Expected theme name

    """
    assert "theme" in config, "Config missing 'theme' section"
    assert "name" in config["theme"], "Theme missing 'name' field"
    assert config["theme"]["name"] == expected_theme, (
        f"Expected theme '{expected_theme}', got '{config['theme']['name']}'"
    )


class MockNixCommand:
    """Mock Nix command for testing."""

    def __init__(self, success: bool = True, output: str = ""):
        self.success = success
        self.output = output
        self.call_count = 0

    def __call__(self, *args, **kwargs):
        """Mock function call."""
        self.call_count += 1
        if self.success:
            return create_mock_nix_eval_success(self.output)
        else:
            return create_mock_nix_eval_failure(self.output)


def assert_file_exists(path: Path, description: str = "file") -> None:
    """Assert that a file exists.

    Args:
        path: Path to the file
        description: Description for error message

    """
    assert path.exists(), f"{description} should exist at {path}"


def assert_file_contains(path: Path, content: str, description: str = "file") -> None:
    """Assert that a file contains specific content.

    Args:
        path: Path to the file
        content: Content to search for
        description: Description for error message

    """
    file_content = path.read_text()
    assert content in file_content, (
        f"{description} should contain '{content}', but got: {file_content[:100]}"
    )
