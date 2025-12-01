"""Test config command workflows with real file system.

This test file verifies the config system works correctly with real
file system operations, including config file discovery, loading,
and writing.
"""

# Import from the actual arda_cli package
import sys
import tempfile
import tomllib
from pathlib import Path
from pathlib import Path as PathLib
from unittest.mock import patch

import pytest

# Add parent directory to path to import arda_cli
sys.path.insert(0, str(PathLib(__file__).parent.parent.parent.parent.parent))

from arda_cli.lib.config import (
    get_config_for_viewing,
    get_config_path,
    get_theme_from_config,
    get_timestamp_from_config,
    get_verbose_from_config,
    load_config,
    set_config_value,
)


@pytest.fixture(autouse=True)
def clean_config_state():
    """Ensure clean config state before each test.

    This fixture runs before every test in this file to ensure no
    config files from previous tests pollute the test environment.
    """
    # Clean up any config files that might exist
    project_config = Path.cwd() / "etc" / "arda.toml"
    if project_config.exists():
        project_config.unlink()

    xdg_config = Path.home() / ".config" / "arda" / "arda.toml"
    if xdg_config.exists():
        xdg_config.unlink()

    # Ensure etc directory doesn't exist if empty
    etc_dir = Path.cwd() / "etc"
    if etc_dir.exists() and not any(etc_dir.iterdir()):
        etc_dir.rmdir()

    # Ensure XDG config directory doesn't exist if empty
    xdg_dir = Path.home() / ".config" / "arda"
    if xdg_dir.exists() and not any(xdg_dir.iterdir()):
        xdg_dir.rmdir()

    # Yield to run the test
    yield

    # Clean up after test
    if project_config.exists():
        project_config.unlink()

    if xdg_config.exists():
        xdg_config.unlink()

    if etc_dir.exists() and not any(etc_dir.iterdir()):
        etc_dir.rmdir()

    if xdg_dir.exists() and not any(xdg_dir.iterdir()):
        xdg_dir.rmdir()



@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.config
@pytest.mark.with_core
def test_config_file_discovery_in_temp_directory():
    """Test that config files are discovered correctly in temp directories."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a config file in the temp directory
        config_dir = temp_path / "etc"
        config_dir.mkdir()
        config_file = config_dir / "arda.toml"

        config_content = """[theme]
default = "solarized"

[output]
verbose = true
timestamp = false
"""
        config_file.write_text(config_content)

        # Test get_config_path finds the file
        with patch("pathlib.Path.cwd", return_value=temp_path):
            found_path = get_config_path()
            assert found_path == config_file
            assert found_path.exists()


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.config
@pytest.mark.with_core
def test_config_loading_from_file():
    """Test that config values are loaded correctly from files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a config file
        config_dir = temp_path / "etc"
        config_dir.mkdir()
        config_file = config_dir / "arda.toml"

        config_content = """[theme]
default = "ocean"

[output]
verbose = true
timestamp = false
"""
        config_file.write_text(config_content)

        # Load config and verify values
        with patch("pathlib.Path.cwd", return_value=temp_path):
            config = load_config()

            assert config["theme"]["default"] == "ocean"
            assert config["output"]["verbose"] is True
            assert config["output"]["timestamp"] is False


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.config
@pytest.mark.with_core
def test_config_getter_functions():
    """Test that config getter functions work with real files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a config file with custom values
        config_dir = temp_path / "etc"
        config_dir.mkdir()
        config_file = config_dir / "arda.toml"

        config_content = """[theme]
default = "forest"

[output]
verbose = true
timestamp = false
"""
        config_file.write_text(config_content)

        # Test getter functions
        with patch("pathlib.Path.cwd", return_value=temp_path):
            theme = get_theme_from_config()
            verbose = get_verbose_from_config()
            timestamp = get_timestamp_from_config()

            assert theme == "forest"
            assert verbose is True
            assert timestamp is False


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.config
@pytest.mark.with_core
def test_config_set_value():
    """Test that config values can be set and written correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a config directory
        config_dir = temp_path / "etc"
        config_dir.mkdir()
        config_file = config_dir / "arda.toml"

        # Set a config value
        set_config_value(config_file, "theme", "default", "monokai")
        set_config_value(config_file, "output", "verbose", True)

        # Verify the file was created
        assert config_file.exists()

        # Verify the values can be read back from the temp file
        with open(config_file, "rb") as f:
            config = tomllib.load(f)
        assert config["theme"]["default"] == "monokai"
        assert config["output"]["verbose"] is True


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.config
def test_config_priority_project_over_user():
    """Test that project config takes priority over user config."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        user_path = temp_path / "user_home"
        user_path.mkdir()

        # Create both project and user configs
        project_config = temp_path / "etc" / "arda.toml"
        project_config.parent.mkdir(parents=True)
        project_config.write_text("""[theme]
default = "project_theme"

[output]
verbose = false
""")

        user_config = user_path / ".config" / "arda" / "arda.toml"
        user_config.parent.mkdir(parents=True)
        user_config.write_text("""[theme]
default = "user_theme"

[output]
verbose = true
""")

        # Get config with priority (project should win)
        with (
            patch("pathlib.Path.cwd", return_value=temp_path),
            patch("pathlib.Path.home", return_value=user_path),
        ):
            config = get_config_for_viewing()

            # Project config should override user config
            assert config["theme"]["default"] == "project_theme"
            assert config["output"]["verbose"] is False


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.config
@pytest.mark.with_core
def test_config_writing_creates_directory():
    """Test that writing config creates necessary directories."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a config path that doesn't exist yet
        config_file = temp_path / "subdir" / "deep" / "etc" / "arda.toml"

        # Set a value (should create directories)
        set_config_value(config_file, "theme", "default", "deep_test")

        # Verify directories were created
        assert config_file.parent.exists()
        assert config_file.exists()

        # Verify value was written
        with open(config_file, "rb") as f:
            config = tomllib.load(f)
        assert config["theme"]["default"] == "deep_test"


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.config
@pytest.mark.with_core
def test_config_default_values_when_no_file():
    """Test that default values are returned when no config file exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Mock cwd to point to empty directory
        with patch("pathlib.Path.cwd", return_value=temp_path):
            # Should return default config
            theme = get_theme_from_config()
            verbose = get_verbose_from_config()
            timestamp = get_timestamp_from_config()

            # Should return defaults (from arda.toml)
            assert theme == "forest"
            assert verbose is False
            assert timestamp is True


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.config
@pytest.mark.with_core
def test_config_file_priority_order():
    """Test the priority order of config file discovery."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        home_path = temp_path / "home"
        home_path.mkdir()

        # Create config in project-level etc/
        project_config = temp_path / "etc" / "arda.toml"
        project_config.parent.mkdir()
        project_config.write_text("""[theme]
default = "project"
""")

        # Create config in XDG user directory
        xdg_config = home_path / ".config" / "arda" / "arda.toml"
        xdg_config.parent.mkdir(parents=True)
        xdg_config.write_text("""[theme]
default = "user"
""")

        # Test get_config_path finds project config (highest priority)
        with (
            patch("pathlib.Path.cwd", return_value=temp_path),
            patch("pathlib.Path.home", return_value=home_path),
        ):
            found_path = get_config_path()
            assert found_path == project_config
            assert found_path.exists()
            assert found_path.parent.name == "etc"
