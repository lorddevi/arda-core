"""Arda CLI main entry point.

Arda uses rich-click's built-in themes for unified styling across
all help text and command output.
"""

import warnings

import click
import rich_click as rclick
from rich.console import Console
from rich.panel import Panel

# Import commands from commands/ directory
from arda_cli.commands.config.main import config
from arda_cli.commands.host.main import host
from arda_cli.commands.roles.main import roles
from arda_cli.commands.secrets.main import secrets
from arda_cli.commands.templates.main import templates
from arda_cli.commands.theme.main import theme
from arda_cli.lib.config import (
    get_active_config_path,
    get_theme_from_config,
    get_timestamp_from_config,
    get_verbose_from_config,
)
from arda_cli.lib.output import create_error_panel

# Import theme handling from lib
from arda_cli.lib.theme import get_rich_click_themes, get_theme_color, patch_rich_click

# Suppress rich_click warnings about invalid themes (we handle this ourselves)
warnings.filterwarnings("ignore", message="RichClickTheme.*not found")

# Patch click with theme configuration
patch_rich_click()

# Get default settings from config
DEFAULT_THEME = get_theme_from_config()
DEFAULT_VERBOSE = get_verbose_from_config()
DEFAULT_TIMESTAMP = get_timestamp_from_config()


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
        import tomli_w

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
    theme = "dracula"  # default
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

    # Map theme to appropriate color
    path_color = get_theme_color(theme)

    # Then show active configuration
    _config_path, config_source = get_active_config_path()
    console = Console()
    console.print(
        f"\n[dim]Active configuration:[/dim] "
        f"[{path_color}]{config_source}[/{path_color}]\n"
    )
    ctx.exit()


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
        show_help_with_config(ctx, None, True)


def show_welcome(console: Console, theme: str) -> None:
    """Show welcome message with theme styling."""
    # Create title with rich text
    title = "ARDA CLI"

    # Show active config
    show_active_config(console)

    # Create welcome panel
    panel = Panel(
        f"[bold]{title}[/bold]\n\n"
        f"Theme: [accent]{theme.upper()}[/accent]\n"
        f"Welcome to Arda - Infrastructure Management for NixOS\n\n"
        f"Use [command]arda --help[/command] for available commands",
        border_style="border",
        padding=(1, 2),
    )

    console.print(panel)
    console.print()


def custom_format_help(
    ctx: click.Context, cmd: click.Command, formatter: click.HelpFormatter
) -> None:
    """Format custom help to show active config file."""
    # Get the original help text
    formatter.write(cmd.get_help(ctx))
    formatter.write("\n")

    # Get the active config file
    _config_path, config_source = get_active_config_path()

    # Show active configuration
    from rich import get_console

    console = get_console()
    console.print(
        f"\n[dim]Active configuration:[/dim] [white]{config_source}[/white]\n"
    )


# Register commands with the main group
main.add_command(config)
main.add_command(host)
main.add_command(roles)
main.add_command(secrets)
main.add_command(templates)
main.add_command(theme)


if __name__ == "__main__":
    main()
