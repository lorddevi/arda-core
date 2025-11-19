"""Arda CLI main entry point

Arda uses rich-click's built-in themes for unified styling across
all help text and command output.
"""

import sys
import os

# IMPORTANT: Parse theme from command-line BEFORE importing rich_click
# This ensures the environment variable is set before rich_click reads it
if '--theme' in sys.argv:
    try:
        theme_index = sys.argv.index('--theme')
        if theme_index + 1 < len(sys.argv):
            theme = sys.argv[theme_index + 1]
            os.environ['RICH_CLICK_THEME'] = theme
            # Store in a global variable for later use
            _GLOBAL_THEME = theme
    except (ValueError, IndexError):
        _GLOBAL_THEME = "dracula"
else:
    _GLOBAL_THEME = "dracula"

# Now import rich_click AFTER setting the environment variable
import click
import rich_click as rclick
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import get_console
from rich_click.patch import patch
from rich_click import RichHelpConfiguration

# Patch click with the theme configuration
# RichHelpConfiguration theme parameter requires rich-click >= 1.9.0
try:
    # Try with theme parameter (rich-click >= 1.9.0)
    config = RichHelpConfiguration(theme=_GLOBAL_THEME, enable_theme_env_var=True)
    patch(rich_config=config)
except TypeError:
    # Fallback for rich-click < 1.9.0 (uses env var only)
    # The RICH_CLICK_THEME env var will still be respected
    patch()


# Get available rich-click themes
def get_rich_click_themes():
    """Get list of available rich-click themes"""
    # Hardcoded list of built-in rich-click themes
    return [
        "dracula", "dracula-dark", "dracula-slim", "dracula-modern",
        "forest", "forest-dark", "forest-slim", "forest-modern",
        "solarized", "solarized-dark", "solarized-slim", "solarized-modern",
        "nord", "nord-dark", "nord-slim", "nord-modern",
        "quartz", "quartz-dark", "quartz-slim", "quartz-modern",
        "monokai", "monokai-dark", "monokai-slim", "monokai-modern"
    ]


def check_and_show_help(ctx: click.Context) -> bool:
    """Check if any options were provided, return True if help should be shown

    Returns:
        True if help should be shown, False if command should continue
    """
    # Check if any options were provided (excluding False for flags)
    if ctx.params and any(v is not None and v is not False for v in ctx.params.values()):
        # Options were provided, don't show help
        return False

    # No options provided, show help
    ctx.get_help()
    return True


@rclick.group(
    no_args_is_help=True,
    context_settings={'help_option_names': ['-h', '--help']}
)
@click.option(
    '--theme',
    type=click.Choice(get_rich_click_themes(), case_sensitive=False),
    default='dracula',
    help='Rich-click theme to use (color + format)'
)
@click.option(
    '--timestamp',
    is_flag=True,
    help='Add timestamps to output'
)
@click.pass_context
def main(ctx: click.Context, theme: str, timestamp: bool) -> None:
    """Arda - minimal infrastructure management for NixOS

    A modern CLI tool with rich theming and beautiful output.
    Uses rich-click's built-in themes for unified styling.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Store theme settings
    ctx.obj['theme'] = theme.lower()
    ctx.obj['timestamp'] = timestamp

    # Get themed console
    console = get_console()
    ctx.obj['console'] = console

    # Show welcome message with theme
    if ctx.invoked_subcommand is None:
        # Only show if running arda without subcommand
        show_welcome(console, theme)


def show_welcome(console: Console, theme: str) -> None:
    """Show welcome message with theme styling"""
    # Create title with rich text
    title = f"ARDA CLI"

    # Create welcome panel
    panel = Panel(
        f"[bold]{title}[/bold]\n\n"
        f"Theme: [accent]{theme.upper()}[/accent]\n"
        f"Welcome to Arda - Infrastructure Management for NixOS\n\n"
        f"Use [command]arda --help[/command] for available commands",
        border_style="border",
        padding=(1, 2)
    )

    console.print(panel)
    console.print()


@rclick.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def host(ctx: click.Context, verbose: bool) -> None:
    """Host management commands

    Manage your NixOS hosts with beautiful, themed output.
    """
    # Show help if no options provided
    if check_and_show_help(ctx):
        return

    console = ctx.obj['console']
    theme = ctx.obj['theme']

    if verbose:
        console.print("\nVerbose mode enabled")

    console.print("\nHost management - coming soon!")

    # Show example of themed output
    console.print("\n✓ System checks passed")
    console.print("⚠  1 host needs attention")
    console.print("ℹ  Total hosts: 5")


@rclick.command()
@click.pass_context
def roles(ctx: click.Context) -> None:
    """Role management commands"""
    # Show help if no options provided
    if check_and_show_help(ctx):
        return

    console = ctx.obj['console']

    console.print("Role management - coming soon!")


@rclick.command()
@click.pass_context
def secrets(ctx: click.Context) -> None:
    """Secret management commands"""
    # Show help if no options provided
    if check_and_show_help(ctx):
        return

    console = ctx.obj['console']

    console.print("Secret management - coming soon!")


@rclick.command()
@click.pass_context
def templates(ctx: click.Context) -> None:
    """Template management commands"""
    # Show help if no options provided
    if check_and_show_help(ctx):
        return

    console = ctx.obj['console']

    console.print("Template management - coming soon!")


@rclick.command()
@click.option(
    '--list',
    '-l',
    is_flag=True,
    help='List all available rich-click themes'
)
@click.pass_context
def theme(ctx: click.Context, list: bool) -> None:
    """Theme management and preview

    View available rich-click themes or preview the current theme.
    """
    console = ctx.obj['console']

    if list:
        console.print("Available Rich-Click Themes\n")

        for theme_name in get_rich_click_themes():
            console.print(f"  [accent]{theme_name}[/accent]")

        console.print("\nNote: Themes can be combined with formats (slim, modern)")
        console.print("Example: 'dracula-modern', 'forest-slim', 'nord-dark'")
    else:
        # Preview current theme
        theme = ctx.obj['theme']
        console.print(f"Current Theme: {theme.upper()}\n")

        console.print("ℹ  Information")
        console.print("✓ Success message")
        console.print("⚠ Warning message")
        console.print("✗ Error message")
        console.print("> Command output")
        console.print("Muted text")


# Register commands with the main group
main.add_command(host)
main.add_command(roles)
main.add_command(secrets)
main.add_command(templates)
main.add_command(theme)


if __name__ == "__main__":
    main()
