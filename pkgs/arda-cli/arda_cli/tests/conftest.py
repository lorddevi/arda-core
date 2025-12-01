"""Global pytest fixtures for arda-cli tests."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file for testing.

    Args:
        tmp_path: pytest built-in fixture for temporary directories

    Returns:
        Path: Path to a temporary config.toml file

    """
    config_path = tmp_path / "test_config.toml"
    config_path.touch()
    return config_path


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory structure.

    Args:
        tmp_path: pytest built-in fixture for temporary directories

    Returns:
        Path: Path to temporary project directory

    """
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    etc_dir = project_dir / "etc"
    etc_dir.mkdir()
    return project_dir


@pytest.fixture
def mock_config_path(tmp_path):
    """Create mock config directory and file for testing.

    Args:
        tmp_path: pytest built-in fixture for temporary directories

    Returns:
        dict: Dictionary with 'config_dir' and 'config_file' paths

    """
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "arda.toml"
    config_file.touch()
    return {"config_dir": config_dir, "config_file": config_file}


@pytest.fixture
def mock_xdg_config_dir(tmp_path):
    """Create mock XDG config directory for testing.

    Args:
        tmp_path: pytest built-in fixture for temporary directories

    Returns:
        dict: Dictionary with XDG config paths

    """
    home_dir = tmp_path / "home" / "user"
    home_dir.mkdir(parents=True)
    xdg_config = home_dir / ".config" / "arda"
    xdg_config.mkdir(parents=True)
    config_file = xdg_config / "arda.toml"
    config_file.touch()
    return {
        "home_dir": home_dir,
        "xdg_config_dir": xdg_config,
        "config_file": config_file,
    }


@pytest.fixture
def rich_console_mock():
    """Create a mock Rich console for output tests.

    Returns:
        MagicMock: Mocked Rich console with print method

    """
    mock = MagicMock()
    mock.print = MagicMock()
    mock.rule = MagicMock()
    mock.print_json = MagicMock()
    mock.print_table = MagicMock()
    return mock


@pytest.fixture
def mock_theme_colors():
    """Create mock theme color mappings.

    Returns:
        dict: Dictionary of theme to color mappings

    """
    return {
        "dracula": "cyan",
        "nord": "bright_cyan",
        "forest": "green",
        "solarized": "cyan",
        "default": "blue",
    }


@pytest.fixture
def mock_path_exists(monkeypatch):
    """Mock pathlib.Path.exists in tests.

    Usage:
        def test_something(mock_path_exists):
            # Path.exists will return True
            mock_path_exists.return_value = True
            assert some_path.exists()
    """

    def _mock_exists(path):
        return False

    monkeypatch.setattr("pathlib.Path.exists", _mock_exists)
    return _mock_exists


@pytest.fixture
def mock_path_home(monkeypatch):
    """Mock pathlib.Path.home for testing.

    Args:
        monkeypatch: pytest fixture for monkey-patching

    Returns:
        function: Mock function for Path.home

    """

    def _mock_home():
        return Path("/mock/home")

    monkeypatch.setattr("pathlib.Path.home", _mock_home)
    return _mock_home


@pytest.fixture
def mock_path_cwd(monkeypatch):
    """Mock pathlib.Path.cwd for testing.

    Args:
        monkeypatch: pytest fixture for monkey-patching

    Returns:
        function: Mock function for Path.cwd

    """

    def _mock_cwd():
        return Path("/mock/cwd")

    monkeypatch.setattr("pathlib.Path.cwd", _mock_cwd)
    return _mock_cwd


@pytest.fixture
def mock_sys_argv(monkeypatch):
    """Mock sys.argv for testing command-line argument parsing.

    Args:
        monkeypatch: pytest fixture for monkey-patching

    Returns:
        function: Function to set mock argv values

    Usage:
        def test_something(mock_sys_argv):
            mock_sys_argv(["arda", "--theme", "nord", "config", "list"])

    """

    def _mock_argv(argv_list):
        monkeypatch.setattr("sys.argv", argv_list)

    return _mock_argv


@pytest.fixture
def sample_config_toml():
    """Provide a sample valid TOML config for testing.

    Returns:
        str: Sample TOML configuration

    """
    return """[theme]
default = "dracula"

[output]
verbose = false
timestamp = true
"""


@pytest.fixture
def mock_themes_list():
    """Provide a list of valid themes for testing.

    Returns:
        list: List of valid theme names

    """
    return [
        "default",
        "dracula",
        "nord",
        "forest",
        "solarized",
        "dracula-slim",
        "dracula-modern",
        "dracula-nu",
        "dracula-robo",
        "nord-slim",
        "nord-modern",
        "nord-nu",
        "nord-robo",
    ]


@pytest.fixture(autouse=True)
def reset_modules():
    """Reset modules and module-level cache between tests to avoid state leakage.

    This fixture is automatically used for all tests.
    It ensures tests don't interfere with each other.
    """
    # Store modules that might be modified
    import sys

    original_modules = set(sys.modules.keys())

    yield

    # Remove any modules that were imported during the test
    # but weren't present before
    modules_to_remove = set(sys.modules.keys()) - original_modules
    for module in modules_to_remove:
        if module.startswith("arda_cli"):
            del sys.modules[module]

    # Reset main module's default config cache to avoid pollution
    # This fixes issues where DEFAULT_THEME/VERBOSE/TIMESTAMP are cached
    # from a previous test's working directory or environment
    try:
        from arda_cli.main import reset_default_config_cache

        reset_default_config_cache()
    except ImportError:
        # Module might not be importable during early test collection
        pass
