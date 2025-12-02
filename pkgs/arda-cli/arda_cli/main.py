"""Arda CLI main entry point.

Arda uses rich-click's built-in themes for unified styling across
all help text and command output.
"""

import warnings
from importlib.metadata import version as get_version

import click
import rich_click as rclick
from rich.console import Console
from rich.panel import Panel

# Import tomli_w conditionally (for config file creation)
try:
    import tomli_w
except ImportError:
    # tomli_w may not be available in all environments
    tomli_w = None

# Import commands from commands/ directory
from arda_cli.commands.config.main import config
from arda_cli.commands.flakes.main import flakes
from arda_cli.commands.host.main import host
from arda_cli.commands.roles.main import roles
from arda_cli.commands.secrets.main import secrets
from arda_cli.commands.theme.main import theme
from arda_cli.lib.config import (
    get_active_config_path,
    get_theme_from_config,
    get_timestamp_from_config,
    get_verbose_from_config,
)
from arda_cli.lib.output import create_error_panel

# Import theme handling from lib
from arda_cli.lib.theme import get_rich_click_themes, patch_rich_click

# Suppress rich_click warnings about invalid themes (we handle this ourselves)
warnings.filterwarnings("ignore", message="RichClickTheme.*not found")

# Patch click with theme configuration
patch_rich_click()


# Module-level defaults - computed lazily to avoid test pollution
# These values are computed on first module import and then cached.
# In tests, they can be reset by clearing _default_config_cache.
def _get_default_config() -> tuple[str, bool, bool]:
    """Get default config values from config files or defaults."""
    from arda_cli.lib.config import (
        get_theme_from_config,
    )

    return (
        get_theme_from_config(),
        get_verbose_from_config(),
        get_timestamp_from_config(),
    )


# Cache for default config values (None = not yet computed)
_default_config_cache: tuple[str, bool, bool] | None = None


def _get_default_theme() -> str:
    """Get default theme (reads config on first call, then cached)."""
    global _default_config_cache
    if _default_config_cache is None:
        _default_config_cache = _get_default_config()
    return _default_config_cache[0]


def _get_default_verbose() -> bool:
    """Get default verbose setting (reads config on first call, then cached)."""
    global _default_config_cache
    if _default_config_cache is None:
        _default_config_cache = _get_default_config()
    return _default_config_cache[1]


def _get_default_timestamp() -> bool:
    """Get default timestamp setting (reads config on first call, then cached)."""
    global _default_config_cache
    if _default_config_cache is None:
        _default_config_cache = _get_default_config()
    return _default_config_cache[2]


def reset_default_config_cache() -> None:
    """Reset the cached default config values.

    This is useful in tests to ensure clean state between test runs.
    """
    global _default_config_cache
    _default_config_cache = None


# Export as module-level constants for click defaults
# These are computed on first module import
DEFAULT_THEME = _get_default_theme()
DEFAULT_VERBOSE = _get_default_verbose()
DEFAULT_TIMESTAMP = _get_default_timestamp()


def ensure_config_exists() -> None:
    """Ensure a configuration file exists.

    If no configuration file is found, automatically creates a project-level
    configuration file with default settings. Reports when creating a new config.
    """
    from pathlib import Path

    # Check if any config file exists
    config_path, _config_source = get_active_config_path()

    if config_path is None:
        # No config found - create project-level config
        project_config = Path.cwd() / "etc" / "arda.toml"

        # Ensure etc directory exists
        project_config.parent.mkdir(parents=True, exist_ok=True)

        # Create config with defaults
        from arda_cli.lib.config import load_default_config

        default_config = load_default_config()

        with open(project_config, "wb") as f:
            tomli_w.dump(default_config, f)

        # Report creation
        console = Console()
        console.print(
            f"[yellow]⚠[/yellow] "
            f"Configuration file not found. "
            f"Created default configuration at {project_config}"
        )
        console.print()


def show_active_config(console: Console) -> None:
    """Show the active configuration file path."""
    _config_path, config_source = get_active_config_path()
    console.print(
        f"\n[dim]Active configuration:[/dim] [white]{config_source}[/white]\n"
    )


def validate_theme(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Validate that the theme is available before proceeding."""
    if value is None:
        return value

    available_themes = get_rich_click_themes()
    if value.lower() not in [t.lower() for t in available_themes]:
        # Create custom error with rich Text markup
        from rich.console import Console
        from rich.text import Text
        from rich_click.rich_help_configuration import RichHelpConfiguration

        console = Console(stderr=True, force_terminal=True)

        # Get the theme from config to use for colors
        theme = get_theme_from_config()

        # Load theme colors for message styling
        config = RichHelpConfiguration(theme=theme, enable_theme_env_var=True)

        # Use theme-appropriate colors
        error_text_color = str(config.style_option or "cyan")
        command_color = str(config.style_command or "cyan")

        # Create message with theme-aware colors
        message = Text()
        message.append("Theme '")
        message.append(value, style=f"bold {error_text_color}")
        message.append("' not found.\n\n")
        message.append("Use '")
        message.append("arda theme list", style=f"bold {command_color}")
        message.append("' to see all available themes.")

        # Use helper function with theme-aware error border color
        panel = create_error_panel(message, theme=theme)
        console.print(panel)
        ctx.exit(2)

    return value


def show_help_with_config(
    ctx: click.Context, param: click.Parameter, value: bool
) -> None:
    """Show help with active config information."""
    if not value:
        return

    # Get theme from command-line arguments (before context is populated)
    # Since this is eager, we need to get theme from params
    theme = None
    if ctx.params and "theme" in ctx.params and ctx.params["theme"]:
        theme = ctx.params["theme"]
    elif ctx.obj and "theme" in ctx.obj:
        theme = ctx.obj["theme"]
    else:
        # Fallback: try to parse from command line args
        import sys

        if "--theme" in sys.argv:
            theme_idx = sys.argv.index("--theme")
            if theme_idx + 1 < len(sys.argv):
                theme = sys.argv[theme_idx + 1]

    # If theme not found anywhere, read from config file
    # This ensures consistency between 'arda' and 'arda --help'
    if theme is None:
        theme = get_theme_from_config()

    # Validate theme before showing help
    available_themes = get_rich_click_themes()
    if theme.lower() not in [t.lower() for t in available_themes]:
        # Create custom error with rich Text markup
        from rich.text import Text

        console = Console(stderr=True, force_terminal=True)

        # Create message with rich Text
        message = Text()
        message.append("Theme '")
        message.append(theme, style="bold yellow")
        message.append("' not found.\n\n")
        message.append("Use '")
        message.append("arda theme list", style="bold cyan")
        message.append("' to see all available themes.")

        # Use helper function with theme-aware error border color
        panel = create_error_panel(message, theme=theme)
        console.print(panel)
        ctx.exit(2)

    # Show the normal help first
    click.echo(ctx.get_help())

    # Get colors directly from the theme configuration
    from rich_click.rich_help_configuration import RichHelpConfiguration

    config = RichHelpConfiguration(theme=theme, enable_theme_env_var=True)
    label_style = str(config.style_option or "dim")  # Use option style for the label
    path_style = str(config.style_command or "white")  # Use command style for the path

    # Then show active configuration
    _config_path, config_source = get_active_config_path()
    console = Console()
    console.print(
        f"\n[{label_style}]Active configuration:[/] "
        f"[{path_style}]{config_source}[/{path_style}]\n"
    )
    ctx.exit()


def show_version(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    """Show version and exit."""
    if not value:
        return

    # Get the version from the package metadata
    try:
        package_version = get_version("arda_cli")
    except Exception:
        # Fallback to a default if we can't get the version
        package_version = "unknown"

    # Display version with rich formatting
    from rich.console import Console

    console = Console()
    console.print(f"Arda CLI version: {package_version}")
    ctx.exit(0)


@rclick.group(invoke_without_command=True)
@click.option(
    "--theme",
    type=str,
    default=DEFAULT_THEME,
    callback=validate_theme,
    help=(
        "Rich-click theme to use (see 'theme list' for all options, "
        "e.g., dracula, forest, solarized)"
    ),
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=DEFAULT_VERBOSE,
    help="Enable verbose output (see config for default)",
)
@click.option(
    "--timestamp/--no-timestamp",
    default=DEFAULT_TIMESTAMP,
    help="Add timestamps to output (see config for default)",
)
@click.option(
    "--help",
    "-h",
    is_flag=True,
    is_eager=True,
    callback=show_help_with_config,
    expose_value=False,
    help="Show this help message and exit.",
)
@click.option(
    "--version",
    is_flag=True,
    is_eager=True,
    callback=show_version,
    expose_value=False,
    help="Show version and exit.",
)
@click.pass_context
def main(ctx: click.Context, theme: str, verbose: bool, timestamp: bool) -> None:
    """Arda - minimal infrastructure management for NixOS.

    A modern CLI tool with rich theming and beautiful output.
    Uses rich-click's built-in themes for unified styling.
    """
    # Ensure configuration file exists (auto-create if needed)
    ensure_config_exists()

    # Ensure context object exists
    ctx.ensure_object(dict)

    # Store settings in context (used by OutputManager)
    ctx.obj["theme"] = theme.lower()
    ctx.obj["verbose"] = verbose
    ctx.obj["timestamp"] = timestamp

    # Show help when no subcommand is provided (matching no_args_is_help behavior)
    if ctx.invoked_subcommand is None:
        # Manually show help to ensure active configuration line is displayed
        # Ensure theme is properly set in context before showing help
        # (This is needed for consistency with --help flag behavior)
        import sys

        if "--theme" in sys.argv:
            theme_idx = sys.argv.index("--theme")
            if theme_idx + 1 < len(sys.argv):
                # Override theme from command line if specified
                ctx.obj["theme"] = sys.argv[theme_idx + 1].lower()

        show_help_with_config(ctx, None, True)


# Register commands with the main group
main.add_command(config)
main.add_command(flakes)
main.add_command(host)
main.add_command(roles)
main.add_command(secrets)
main.add_command(theme)


if __name__ == "__main__":
    main()
