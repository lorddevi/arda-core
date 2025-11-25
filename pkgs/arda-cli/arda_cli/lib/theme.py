"""Theme handling for rich-click integration."""

import os
import sys

# IMPORTANT: Parse theme from command-line BEFORE importing rich_click
# This ensures the environment variable is set before rich_click reads it
from arda_cli.lib.config import get_theme_from_config

global _GLOBAL_THEME
_GLOBAL_THEME = "dracula"  # Will be updated from config below

if "--theme" in sys.argv:
    try:
        theme_index = sys.argv.index("--theme")
        if theme_index + 1 < len(sys.argv):
            theme_value = sys.argv[theme_index + 1]
            # Only set environment variable if theme is valid
            # This prevents rich-click from raising an error on invalid themes
            valid_themes = [
                "default",
                "dracula",
                "forest",
                "solarized",
                "nord",
                "quartz",
                "star",
                "quartz2",
                "cargo",
                "red1",
                "green1",
                "yellow1",
                "blue1",
                "magenta1",
                "cyan1",
                "red2",
                "green2",
                "yellow2",
                "blue2",
                "magenta2",
                "cyan2",
                "mono",
                "plain",
            ]
            if theme_value.lower() in [t.lower() for t in valid_themes]:
                os.environ["RICH_CLICK_THEME"] = theme_value
                _GLOBAL_THEME = theme_value
            else:
                # Invalid theme - fall back to config default
                _GLOBAL_THEME = get_theme_from_config()
        else:
            # --theme specified but no value, use config default
            _GLOBAL_THEME = get_theme_from_config()
    except (ValueError, IndexError):
        _GLOBAL_THEME = get_theme_from_config()
else:
    # No --theme specified, use config default
    _GLOBAL_THEME = get_theme_from_config()


def get_rich_click_themes() -> list[str]:
    """Get list of available rich-click themes."""
    # All available rich-click color palettes
    palettes = [
        "default",
        "dracula",
        "forest",
        "solarized",
        "nord",
        "quartz",
        "star",
        "quartz2",
        "cargo",
        "red1",
        "green1",
        "yellow1",
        "blue1",
        "magenta1",
        "cyan1",
        "red2",
        "green2",
        "yellow2",
        "blue2",
        "magenta2",
        "cyan2",
        "mono",
        "plain",
    ]

    # Main palettes that get format variants
    main_palettes = [
        "default",
        "dracula",
        "forest",
        "solarized",
        "nord",
        "quartz",
        "star",
        "quartz2",
        "cargo",
    ]

    # Generate all combinations: palette-format (skip box since it's default)
    themes = []
    for palette in palettes:
        # Include the base palette (box format) for all palettes
        themes.append(palette)

        # Add variants for main palettes (those without numbers in the name)
        if palette in main_palettes:
            for fmt in ["slim", "modern", "nu", "robo"]:
                themes.append(f"{palette}-{fmt}")

    return themes


def patch_rich_click() -> None:
    """Patch click with the theme configuration.

    RichHelpConfiguration theme parameter requires rich-click >= 1.9.0
    """
    from rich_click import RichHelpConfiguration
    from rich_click.patch import patch

    # Patch click with the theme configuration
    try:
        # Try with theme parameter (rich-click >= 1.9.0)
        config = RichHelpConfiguration(
            theme=_GLOBAL_THEME,
            enable_theme_env_var=True,
            # Note: Use each theme's error color - don't override panel border
        )
        patch(rich_config=config)
    except TypeError:
        # Fallback for rich-click < 1.9.0 (uses env var only)
        # The RICH_CLICK_THEME env var will still be respected
        patch()


def get_current_theme() -> str:
    """Get the currently active theme name."""
    return _GLOBAL_THEME


def get_theme_color(theme_name: str) -> str:
    """Map theme names to appropriate colors for configuration path.

    Args:
        theme_name: The name of the theme (e.g., 'dracula', 'nord', 'forest')

    Returns:
        Rich color tag appropriate for the theme

    """
    theme_lower = theme_name.lower()

    # Define theme-appropriate colors (using standard Rich colors)
    theme_colors = {
        # Dark themes with cyan accents
        "dracula": "cyan",
        "night": "cyan",
        "solarized-dark": "cyan",
        "nord": "bright_cyan",
        "one-dark": "cyan",
        # Light themes
        "solarized-light": "blue",
        "github": "blue",
        "monokai": "cyan",
        # Colorful themes
        "forest": "green",
        "gruvbox": "green",
        "quartz": "magenta",
        "rose_pine": "pink",
        "ayu": "orange",
        "tokyo-night": "blue",
        # Default fallback
        "default": "blue",
    }

    # Find matching theme (try exact match first, then partial)
    if theme_lower in theme_colors:
        return theme_colors[theme_lower]
    elif "dracula" in theme_lower or "dark" in theme_lower:
        return "cyan"
    elif "light" in theme_lower:
        return "blue"
    elif "forest" in theme_lower or "green" in theme_lower:
        return "green"
    elif "quartz" in theme_lower or "pink" in theme_lower:
        return "magenta"
    elif "nord" in theme_lower or "bright" in theme_lower:
        return "bright_cyan"
    elif "blue" in theme_lower or "ocean" in theme_lower:
        return "blue"
    else:
        return "cyan"
