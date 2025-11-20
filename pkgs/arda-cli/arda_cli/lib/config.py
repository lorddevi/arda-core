"""Configuration file handling for Arda CLI."""

import tomllib
from pathlib import Path

DEFAULT_CONFIG_NAME = "arda.toml"


def get_config_path() -> Path | None:
    """Find the first existing config file in search paths.

    Returns:
        Path to the config file, or None if not found

    Search order:
    1. ~/.config/arda/arda.toml (XDG standard)
    2. /etc/arda/arda.toml (system-wide)
    3. ./etc/arda.toml (project-level)
    4. ./arda.toml (current directory)
    5. ./arda_cli/arda.toml (default/fallback)

    """
    # Define search paths
    search_paths = [
        # XDG config directory
        Path.home() / ".config" / "arda" / DEFAULT_CONFIG_NAME,
        # System-wide config
        Path("/etc/arda") / DEFAULT_CONFIG_NAME,
        # Project-level config
        Path.cwd() / "etc" / DEFAULT_CONFIG_NAME,
        # Current directory
        Path.cwd() / DEFAULT_CONFIG_NAME,
    ]

    # Find first existing config
    for config_path in search_paths:
        if config_path.exists():
            return config_path

    # Check for default config in package (fallback)
    # This will be handled by load_default_config()
    return None


def load_config() -> dict:
    """Load configuration from file.

    Returns:
        Dictionary containing config settings

    """
    config_path = get_config_path()

    if config_path and config_path.exists():
        try:
            with open(config_path, "rb") as f:
                return tomllib.load(f)
        except Exception:
            # Silently fall back to default config
            return load_default_config()
    else:
        return load_default_config()


def load_default_config() -> dict:
    """Load default configuration from package.

    Returns:
        Dictionary containing default config

    """
    # Get the path to the default config file in the package
    package_dir = Path(__file__).parent.parent
    default_config_path = package_dir / DEFAULT_CONFIG_NAME

    if default_config_path.exists():
        try:
            with open(default_config_path, "rb") as f:
                return tomllib.load(f)
        except Exception:
            # Silently fall back to hardcoded default
            pass  # noqa: S110

    # Return hardcoded default if file doesn't exist
    return {"theme": {"default": "dracula"}, "output": {}}


def get_theme_from_config() -> str:
    """Get the theme setting from config file.

    Returns:
        Theme name string (default: "dracula")

    """
    config = load_config()

    # Try to get theme from config
    if "theme" in config:
        theme_config = config["theme"]
        if "default" in theme_config:
            return str(theme_config["default"])

    return "dracula"
