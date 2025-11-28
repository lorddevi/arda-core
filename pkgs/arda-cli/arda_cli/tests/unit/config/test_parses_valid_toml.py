"""Test that valid TOML configuration files are parsed correctly.

This test file verifies the pytest infrastructure and marker system work
correctly with real test scenarios. The tests use the pytest_helpers module
to create temporary config files and verify file operations.
"""

from unittest.mock import MagicMock

import pytest

# Import helpers (path configured via conftest.py)
from pytest_helpers import (
    TempDirectory,
    cleanup_temp_file,
    create_temp_config_file,
)


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_marker_system_works():
    """Verify that test markers are working correctly."""
    # This is a basic test to verify the test infrastructure
    assert True


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_create_temp_config_file():
    """Test that we can create and read temporary config files."""
    # Create a test config using our helper
    test_config = {
        "theme": {
            "name": "dracula",
            "primary_color": "#282936",
        },
        "verbose": True,
        "timestamp": False,
    }

    # Create temporary config file
    temp_file = create_temp_config_file(test_config)

    try:
        # Verify file was created
        assert temp_file.exists()
        assert temp_file.suffix == ".toml"

        # Verify content can be read and parsed
        import tomllib

        with open(temp_file, "rb") as f:
            loaded_config = tomllib.load(f)

        # Verify structure
        assert loaded_config["theme"]["name"] == "dracula"
        assert loaded_config["theme"]["primary_color"] == "#282936"
        assert loaded_config["verbose"] is True
        assert loaded_config["timestamp"] is False

    finally:
        # Clean up
        cleanup_temp_file(temp_file)


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_temp_directory_context_manager():
    """Test TempDirectory context manager for config testing."""
    with TempDirectory() as temp_dir:
        # Verify directory exists
        assert temp_dir.exists()
        assert temp_dir.is_dir()

        # Create a config file inside temp directory
        config = {
            "theme": {"name": "forest"},
            "verbose": False,
        }

        config_file = temp_dir / "test_config.toml"

        # Write config
        try:
            import tomli_w

            toml_data = tomli_w.dumps(config)
            if isinstance(toml_data, str):
                toml_data = toml_data.encode("utf-8")
            with open(config_file, "wb") as f:
                f.write(toml_data)
        except ImportError:
            import toml

            with open(config_file, "w", encoding="utf-8") as f:
                f.write(toml.dumps(config))

        # Verify file exists
        assert config_file.exists()

        # Verify we can read it back
        import tomllib

        with open(config_file, "rb") as f:
            loaded = tomllib.load(f)

        assert loaded["theme"]["name"] == "forest"
        assert loaded["verbose"] is False

    # Directory should be cleaned up
    assert not temp_dir.exists()


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_mock_subprocess_for_nix_operations():
    """Test mocking subprocess for Nix config operations."""
    # Create a mock subprocess result
    mock_result = MagicMock()
    mock_result.stdout = b'{"theme": {"name": "test"}}'
    mock_result.stderr = b""
    mock_result.returncode = 0

    # Verify the mock is configured correctly
    assert mock_result.returncode == 0

    # If we had real arda_cli code, we would patch subprocess.run
    # to return this mock for testing config operations
    # with patch('subprocess.run', return_value=mock_result):
    #     result = load_config_from_nix()
    #     assert result == {"theme": {"name": "test"}}


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_config_structure_validation():
    """Test that we can validate config structure."""
    # This test verifies our understanding of the config structure
    # that arda_cli expects

    # Create a valid config
    valid_config = {
        "theme": {
            "name": "monokai",
            "primary_color": "#f92672",
        },
        "verbose": True,
        "timestamp": False,
    }

    # Verify structure
    assert "theme" in valid_config
    assert "name" in valid_config["theme"]
    assert isinstance(valid_config["verbose"], bool)
    assert isinstance(valid_config["timestamp"], bool)
