"""Configuration file handling for Arda CLI."""

import tomllib
from pathlib import Path

import tomli_w  # type: ignore

DEFAULT_CONFIG_NAME = "arda.toml"


def get_active_config_path() -> tuple[Path | None, str]:
    """Get the path to the active configuration file.

    Returns:
        Tuple of (config_path, source) where:
        - config_path: Path to the active config file, or None
        - source: Description of where the config was found

    Priority order:
    1. Project config (etc/arda.toml) - highest priority
    2. XDG user config (~/.config/arda/arda.toml) - medium priority
    3. None (will use package defaults) - lowest priority

    """
    # Project-level config (highest priority)
    project_config = Path.cwd() / "etc" / DEFAULT_CONFIG_NAME
    if project_config.exists():
        return (project_config, str(project_config))

    # XDG user config (medium priority)
    xdg_config = Path.home() / ".config" / "arda" / DEFAULT_CONFIG_NAME
    if xdg_config.exists():
        return (xdg_config, str(xdg_config))

    # No config file found - will use package defaults
    return (None, "package defaults")


def get_config_path() -> Path | None:
    """Find the first existing config file in search paths.

    Returns:
        Path to the config file, or None if not found

    Search order:
    1. ~/.config/arda/arda.toml (XDG user config)
    2. ./etc/arda.toml (project-level config)
    3. ./arda.toml (current directory)
    4. ./arda_cli/arda.toml (package default/fallback)

    """
    # Define search paths in priority order (highest to lowest)
    search_paths = [
        # Project-level config - highest priority
        Path.cwd() / "etc" / DEFAULT_CONFIG_NAME,
        # XDG config directory (user-level) - medium priority
        Path.home() / ".config" / "arda" / DEFAULT_CONFIG_NAME,
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
        with open(default_config_path, "rb") as f:
            return tomllib.load(f)

    # Return hardcoded default if file doesn't exist
    return {
        "theme": {"default": "dracula"},
        "output": {"verbose": False, "timestamp": True},
    }


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


def get_verbose_from_config() -> bool:
    """Get the verbose setting from config file.

    Returns:
        Verbose setting (default: False)

    """
    config = load_config()

    # Try to get verbose from config
    if "output" in config:
        output_config = config["output"]
        if "verbose" in output_config:
            return bool(output_config["verbose"])

    return False


def get_timestamp_from_config() -> bool:
    """Get the timestamp setting from config file.

    Returns:
        Timestamp setting (default: True)

    """
    config = load_config()

    # Try to get timestamp from config
    if "output" in config:
        output_config = config["output"]
        if "timestamp" in output_config:
            return bool(output_config["timestamp"])

    return True


def get_config_for_viewing(
    force_global: bool = False, force_local: bool = False
) -> dict:
    """Get configuration with priority order for viewing.

    Reads config from highest priority to lowest:
    1. Project config (etc/arda.toml) - highest priority
    2. XDG user config (~/.config/arda/arda.toml) - medium priority
    3. Package defaults - lowest priority (NEVER read directly, only used as fallback)

    Args:
        force_global: If True, only read from XDG config
        force_local: If True, only read from project config

    Returns:
        Merged configuration dictionary with values from highest priority source
        that contains each setting

    """
    # Define search paths in reverse priority order (lowest to highest)
    # Package defaults is handled separately and not included in search paths
    search_paths: list[Path] = []

    # Add paths based on force flags
    if force_local:
        # Only read from project config
        project_config = Path.cwd() / "etc" / DEFAULT_CONFIG_NAME
        search_paths.append(project_config)
    elif force_global:
        # Only read from XDG config
        xdg_config = Path.home() / ".config" / "arda" / DEFAULT_CONFIG_NAME
        search_paths.append(xdg_config)
    else:
        # Normal priority order (project → XDG → package defaults)
        search_paths = [
            # XDG config directory (user-level) - medium priority
            Path.home() / ".config" / "arda" / DEFAULT_CONFIG_NAME,
            # Project-level config - highest priority
            Path.cwd() / "etc" / DEFAULT_CONFIG_NAME,
        ]

    # Merge configs in reverse order (lowest to highest priority)
    merged_config: dict = {}

    for config_path in search_paths:
        if config_path.exists():
            try:
                with open(config_path, "rb") as f:
                    config_data = tomllib.load(f)
                    # Merge with higher priority overriding lower
                    merged_config = _deep_merge(merged_config, config_data)
            except OSError:
                # Skip invalid or unreadable config files
                pass

    # If no configs found, return package defaults (never read package config directly)
    if not merged_config:
        return load_default_config()

    return merged_config


def get_config_for_writing(
    force_global: bool = False, force_local: bool = False
) -> Path:
    """Get config file path for writing configuration changes.

    Priority order (when no force flags):
    1. Project config (etc/arda.toml) - highest priority (created if needed)
    2. XDG user config (~/.config/arda/arda.toml) - if project doesn't exist

    With force flags:
    - force_local: Always use project config (create if needed)
    - force_global: Always use XDG user config (create if needed)

    Args:
        force_global: If True, force writing to XDG config
        force_local: If True, force writing to project config

    Returns:
        Path to the config file that should be modified

    """
    # Determine which config to use based on force flags
    if force_local:
        # Force project config
        project_config = Path.cwd() / "etc" / DEFAULT_CONFIG_NAME
        project_config.parent.mkdir(parents=True, exist_ok=True)
        return project_config

    elif force_global:
        # Force XDG config
        xdg_config = Path.home() / ".config" / "arda" / DEFAULT_CONFIG_NAME
        xdg_config.parent.mkdir(parents=True, exist_ok=True)
        return xdg_config

    else:
        # Default priority: project config takes precedence
        project_config = Path.cwd() / "etc" / DEFAULT_CONFIG_NAME

        # If project config exists, use it
        if project_config.exists():
            return project_config

        # Otherwise, fall back to XDG config
        xdg_config = Path.home() / ".config" / "arda" / DEFAULT_CONFIG_NAME

        # Create XDG directory if it doesn't exist
        xdg_config.parent.mkdir(parents=True, exist_ok=True)

        return xdg_config


def set_config_value(
    config_path: Path,
    section: str,
    setting: str,
    value: str | bool,
) -> None:
    """Set a configuration value in the specified config file.

    Args:
        config_path: Path to the config file to modify
        section: Configuration section (e.g., 'theme', 'output')
        setting: Setting name (e.g., 'default', 'verbose')
        value: Value to set (will be converted to appropriate type)

    """
    # Load existing config or start with defaults
    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                config_data = tomllib.load(f)
        except Exception:
            # If file exists but can't be read, start fresh
            config_data = {}
    else:
        # If file doesn't exist, start with package defaults
        config_data = load_default_config()

    # Ensure section exists
    if section not in config_data:
        config_data[section] = {}
    elif not isinstance(config_data[section], dict):
        # Replace non-dict section with dict
        config_data[section] = {}

    # Set the value
    config_data[section][setting] = value

    # Write back to file
    with open(config_path, "wb") as f:
        tomli_w.dump(config_data, f)


def get_valid_config_keys() -> list[tuple[str, str]]:
    """Get list of all valid configuration keys.

    Returns:
        List of (section, setting) tuples representing valid configuration keys

    """
    return [
        ("theme", "default"),
        ("output", "verbose"),
        ("output", "timestamp"),
    ]


def _deep_merge(base: dict, update: dict) -> dict:
    """Recursively merge two dictionaries.

    Args:
        base: Base dictionary
        update: Dictionary to merge into base

    Returns:
        Merged dictionary

    """
    result = base.copy()
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
