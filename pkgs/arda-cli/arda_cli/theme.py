"""Theme management for Arda CLI

This module provides theme loading and management functionality for the Arda CLI.
Themes are defined in YAML files and loaded dynamically.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.theme import Theme


class ThemeManager:
    """Manages YAML-based themes for Arda CLI

    Themes are stored as YAML files in the themes/ directory.
    Each theme defines colors for different message types and UI elements.
    """

    def __init__(self, themes_dir: Path):
        """Initialize ThemeManager

        Args:
            themes_dir: Path to directory containing theme YAML files
        """
        self.themes_dir = Path(themes_dir)
        self.themes: Dict[str, Dict] = {}
        self.load_themes()

    def load_themes(self) -> None:
        """Load all themes from YAML files in themes directory

        Raises:
            FileNotFoundError: If themes directory doesn't exist
            yaml.YAMLError: If theme file is invalid YAML
        """
        if not self.themes_dir.exists():
            self._create_default_themes()
            return

        # Load all .yaml and .yml files
        for theme_file in self.themes_dir.glob("*.yaml"):
            self._load_theme_file(theme_file)
        for theme_file in self.themes_dir.glob("*.yml"):
            self._load_theme_file(theme_file)

    def _load_theme_file(self, theme_file: Path) -> None:
        """Load a single theme file

        Args:
            theme_file: Path to theme YAML file

        Raises:
            yaml.YAMLError: If file contains invalid YAML
        """
        theme_name = theme_file.stem
        try:
            with open(theme_file, 'r') as f:
                theme_data = yaml.safe_load(f)
            if theme_data and isinstance(theme_data, dict):
                self.themes[theme_name] = theme_data
        except yaml.YAMLError as e:
            print(f"Warning: Could not load theme '{theme_name}': {e}")

    def _create_default_themes(self) -> None:
        """Create default theme files if themes directory doesn't exist"""
        self.themes_dir.mkdir(parents=True, exist_ok=True)

        default_themes = {
            "greyscale": {
                "info": "white",
                "success": "white",
                "warning": "white",
                "error": "bold white",
                "command": "bold white",
                "accent": "white",
                "muted": "dim white",
                "title": "bold white",
                "border": "white",
                "hostname_brackets": "dim white",
                "hostname_name": "white",
                "hostname_colon": "dim white",
                "timestamp": "dim white",
                "output": "white",
                "debug": "dim white"
            },
            "matrix": {
                "info": "green",
                "success": "bright_green",
                "warning": "bright_yellow",
                "error": "bright_red",
                "command": "bold green",
                "accent": "cyan",
                "muted": "dim green",
                "title": "bold green",
                "border": "green",
                "hostname_brackets": "dim green",
                "hostname_name": "bright_green",
                "hostname_colon": "dim green",
                "timestamp": "dim green",
                "output": "green",
                "debug": "dim green"
            },
            "ocean": {
                "info": "deep_sky_blue1",
                "success": "spring_green1",
                "warning": "turquoise",
                "error": "red1",
                "command": "bold deep_sky_blue1",
                "accent": "turquoise",
                "muted": "dim deep_sky_blue1",
                "title": "bold deep_sky_blue1",
                "border": "deep_sky_blue1",
                "hostname_brackets": "dim deep_sky_blue1",
                "hostname_name": "turquoise",
                "hostname_colon": "dim deep_sky_blue1",
                "timestamp": "dim deep_sky_blue1",
                "output": "deep_sky_blue1",
                "debug": "dim deep_sky_blue1"
            }
        }

        for name, theme in default_themes.items():
            theme_file = self.themes_dir / f"{name}.yaml"
            with open(theme_file, 'w') as f:
                yaml.dump(theme, f, default_flow_style=False, sort_keys=False)
            self.themes[name] = theme

    def get_console(self, theme_name: str = "greyscale") -> Console:
        """Get a Console instance with the specified theme

        Args:
            theme_name: Name of theme to use (default: greyscale)

        Returns:
            Console instance configured with the theme

        Raises:
            KeyError: If theme_name doesn't exist (will fallback to greyscale)
        """
        if theme_name not in self.themes:
            print(f"Warning: Theme '{theme_name}' not found, using 'greyscale'")
            theme_name = "greyscale"

        theme = Theme(self.themes[theme_name])
        return Console(theme=theme)

    def get_colors(self, theme_name: str = "greyscale") -> Dict:
        """Get the color dictionary for a theme

        Args:
            theme_name: Name of theme

        Returns:
            Dictionary of color definitions
        """
        if theme_name not in self.themes:
            return self.themes.get("greyscale", {})
        return self.themes[theme_name]

    def list_themes(self) -> List[str]:
        """List all available theme names

        Returns:
            List of theme names
        """
        return sorted(self.themes.keys())

    def has_theme(self, theme_name: str) -> bool:
        """Check if a theme exists

        Args:
            theme_name: Name of theme to check

        Returns:
            True if theme exists, False otherwise
        """
        return theme_name in self.themes
