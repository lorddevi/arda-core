"""Theme handling for rich-click integration."""

import os
import sys

# IMPORTANT: Parse theme from command-line BEFORE importing rich_click
# This ensures the environment variable is set before rich_click reads it
global _GLOBAL_THEME
_GLOBAL_THEME = "dracula"

if "--theme" in sys.argv:
    try:
        theme_index = sys.argv.index("--theme")
        if theme_index + 1 < len(sys.argv):
            theme_value = sys.argv[theme_index + 1]
            os.environ["RICH_CLICK_THEME"] = theme_value
            _GLOBAL_THEME = theme_value
    except (ValueError, IndexError):
        _GLOBAL_THEME = "dracula"
else:
    _GLOBAL_THEME = "dracula"


def get_rich_click_themes() -> list[str]:
    """Get list of available rich-click themes."""
    # Hardcoded list of built-in rich-click themes
    return [
        "dracula",
        "dracula-dark",
        "dracula-slim",
        "dracula-modern",
        "forest",
        "forest-dark",
        "forest-slim",
        "forest-modern",
        "solarized",
        "solarized-dark",
        "solarized-slim",
        "solarized-modern",
        "nord",
        "nord-dark",
        "nord-slim",
        "nord-modern",
        "quartz",
        "quartz-dark",
        "quartz-slim",
        "quartz-modern",
        "monokai",
        "monokai-dark",
        "monokai-slim",
        "monokai-modern",
    ]


def patch_rich_click() -> None:
    """Patch click with the theme configuration.

    RichHelpConfiguration theme parameter requires rich-click >= 1.9.0
    """
    from rich_click import RichHelpConfiguration
    from rich_click.patch import patch

    # Patch click with the theme configuration
    try:
        # Try with theme parameter (rich-click >= 1.9.0)
        config = RichHelpConfiguration(theme=_GLOBAL_THEME, enable_theme_env_var=True)
        patch(rich_config=config)
    except TypeError:
        # Fallback for rich-click < 1.9.0 (uses env var only)
        # The RICH_CLICK_THEME env var will still be respected
        patch()


def get_current_theme() -> str:
    """Get the currently active theme name."""
    return _GLOBAL_THEME
