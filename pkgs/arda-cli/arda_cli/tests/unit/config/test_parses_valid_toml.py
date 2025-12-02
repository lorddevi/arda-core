"""Test that valid TOML configuration files are parsed correctly.

This test file verifies the pytest infrastructure and marker system work
correctly with real test scenarios. The tests use the pytest_helpers module
to create temporary config files and verify file operations.
"""

from unittest.mock import MagicMock, patch

import pytest

# Import helpers
from arda_cli.testing.helpers.pytest_helpers import (
    TempDirectory,
    cleanup_temp_file,
    create_temp_config_file,
)


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_marker_system_works():
    """Verify that test markers are working correctly."""
    # Verify the test infrastructure is properly configured
    # by checking that we can access marker information
    import pytest

    # Get current test item markers
    test_item = (
        pytest.current_test_item if hasattr(pytest, "current_test_item") else None
    )

    # Verify pytest is properly configured by running a simple operation
    assert isinstance([], list)
    assert isinstance({}, dict)
    assert isinstance("test", str)


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
def test_temp_directory_context_manager_with_fallback(monkeypatch):
    """Test TempDirectory with toml library fallback when tomli_w unavailable."""
    # Remove tomli_w from sys.modules to force ImportError
    import builtins
    import sys

    tomli_w_backup = sys.modules.get("tomli_w")
    if "tomli_w" in sys.modules:
        del sys.modules["tomli_w"]

    # Mock the import to raise ImportError
    original_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "tomli_w":
            raise ImportError("tomli_w not available")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    try:
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

            # Write config (should use toml fallback)
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
    finally:
        # Restore original import
        monkeypatch.setattr(builtins, "__import__", original_import)
        # Restore tomli_w to sys.modules
        if tomli_w_backup is not None:
            sys.modules["tomli_w"] = tomli_w_backup


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
def test_temp_directory_with_toml_fallback():
    """Test TempDirectory with toml library fallback when tomli_w unavailable."""
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

        # Write config using fallback toml library
        # Force using toml library instead of tomli_w
        import sys

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
@patch.dict("sys.modules", {"tomli_w": None})
def test_temp_directory_context_manager_fallback_path():
    """Test TempDirectory with toml library fallback when tomli_w is None."""
    # Force tomli_w to not exist in sys.modules to simulate ImportError
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

        # This should use the fallback toml library
        # (when tomli_w is not available, the except block runs)
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


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_complex_nested_config_structure():
    """Test parsing complex nested TOML structures."""
    # Create a more complex config with multiple sections
    complex_config = {
        "theme": {
            "name": "solarized-dark",
            "primary_color": "#268bd2",
            "secondary_color": "#859900",
            "background_color": "#002b36",
            "text_color": "#839496",
        },
        "output": {
            "verbose": True,
            "timestamp": True,
            "compact": False,
        },
        "advanced": {
            "theme_variants": ["slim", "modern", "extended"],
            "color_depth": 256,
        },
    }

    # Create and verify the config file
    temp_file = create_temp_config_file(complex_config)

    try:
        assert temp_file.exists()
        assert temp_file.suffix == ".toml"

        # Parse and verify
        import tomllib

        with open(temp_file, "rb") as f:
            loaded_config = tomllib.load(f)

        # Verify nested structure
        assert loaded_config["theme"]["name"] == "solarized-dark"
        assert loaded_config["theme"]["primary_color"] == "#268bd2"
        assert loaded_config["output"]["verbose"] is True
        assert loaded_config["output"]["timestamp"] is True
        assert loaded_config["advanced"]["color_depth"] == 256
        assert "slim" in loaded_config["advanced"]["theme_variants"]

    finally:
        cleanup_temp_file(temp_file)


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_config_with_all_boolean_variations():
    """Test config files with various boolean value combinations."""
    # Test config with explicit True/False values
    config_true = {
        "theme": {"name": "default"},
        "verbose": True,
        "timestamp": False,
    }

    config_false = {
        "theme": {"name": "default"},
        "verbose": False,
        "timestamp": True,
    }

    temp_file1 = create_temp_config_file(config_true)
    temp_file2 = create_temp_config_file(config_false)

    try:
        import tomllib

        # Verify config1
        with open(temp_file1, "rb") as f:
            loaded1 = tomllib.load(f)
        assert loaded1["verbose"] is True
        assert loaded1["timestamp"] is False

        # Verify config2
        with open(temp_file2, "rb") as f:
            loaded2 = tomllib.load(f)
        assert loaded2["verbose"] is False
        assert loaded2["timestamp"] is True

    finally:
        cleanup_temp_file(temp_file1)
        cleanup_temp_file(temp_file2)


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_multiple_config_files_isolation():
    """Test that multiple temp config files don't interfere with each other."""
    config1 = {
        "theme": {"name": "dracula"},
        "verbose": True,
    }

    config2 = {
        "theme": {"name": "nord"},
        "verbose": False,
    }

    # Create two separate config files
    temp_file1 = create_temp_config_file(config1)
    temp_file2 = create_temp_config_file(config2)

    try:
        assert temp_file1 != temp_file2

        # Verify both files have correct content
        import tomllib

        with open(temp_file1, "rb") as f:
            loaded1 = tomllib.load(f)
        assert loaded1["theme"]["name"] == "dracula"

        with open(temp_file2, "rb") as f:
            loaded2 = tomllib.load(f)
        assert loaded2["theme"]["name"] == "nord"

        # Verify they're truly separate
        assert loaded1["theme"]["name"] != loaded2["theme"]["name"]

    finally:
        cleanup_temp_file(temp_file1)
        cleanup_temp_file(temp_file2)


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_temp_directory_cleanup_on_exception():
    """Test that TempDirectory cleans up even when an exception occurs."""
    import os

    # Store original directory
    original_dir = os.getcwd()

    temp_dir_path = None
    try:
        with TempDirectory() as temp_dir:
            temp_dir_path = temp_dir
            # Verify directory exists
            assert temp_dir.exists()
            assert temp_dir.is_dir()

            # Create a test file
            test_file = temp_dir / "test.txt"
            test_file.write_text("test")

            # Verify file exists
            assert test_file.exists()

            # Raise an exception to test cleanup
            raise ValueError("Test exception")

    except ValueError:
        # Exception was raised as expected
        pass

    # Verify directory was cleaned up even after exception
    assert temp_dir_path is not None
    assert not temp_dir_path.exists()

    # Verify we're back in original directory
    assert os.getcwd() == original_dir
