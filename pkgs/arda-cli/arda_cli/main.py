"""Arda CLI main entry point

Arda is a minimal infrastructure management tool for NixOS with support
for theming, gradients, and beautiful terminal output.
"""

from pathlib import Path
import click
import rich_click as rclick
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich_click.patch import patch

from .theme import ThemeManager
from .styling import gradient_text, gradient_horizontal_line

# Patch Click to use rich-click for help text
patch()

# Initialize theme manager
THEMES_DIR = Path(__file__).parent / "themes"
theme_manager = ThemeManager(THEMES_DIR)


def show_header(console: Console, title: str, icon: str = "") -> None:
    """Display a consistently styled header with gradient text and horizontal line

    Args:
        console: The themed console to print to
        title: The title text to display
        icon: Optional emoji icon to prepend
    """
    # Create styled header with icon if provided
    if icon:
        header_text = f"{icon}  {title}"
    else:
        header_text = title

    # Print gradient header and horizontal line
    console.print(gradient_text(header_text, "cyan", "bright_cyan"))
    console.print(gradient_horizontal_line(60, "cyan"))
    console.print()


def invoke_help_if_no_options(ctx: click.Context) -> None:
    """Callback to show help if no options are provided to a subcommand

    This ensures that commands like 'arda host' show help by default,
    similar to how 'arda' shows help.
    """
    # Check if any options were provided
    if ctx.params and any(v is not None for v in ctx.params.values()):
        # Options were provided, don't show help
        return

    # No options provided, show help
    ctx.get_help()


@rclick.group(no_args_is_help=True)
@click.option(
    '--theme',
    type=click.Choice(theme_manager.list_themes(), case_sensitive=False),
    default='greyscale',
    help='Color theme to use'
)
@click.option(
    '--timestamp',
    is_flag=True,
    help='Add timestamps to output'
)
@click.pass_context
def main(ctx: click.Context, theme: str, timestamp: bool) -> None:
    """Arda - minimal infrastructure management for NixOS

    A modern CLI tool with rich theming, gradient support, and beautiful output.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Store theme settings
    ctx.obj['theme'] = theme.lower()
    ctx.obj['timestamp'] = timestamp

    # Get themed console
    console = theme_manager.get_console(theme)
    ctx.obj['console'] = console

    # Store theme colors for styling functions
    ctx.obj['theme_colors'] = theme_manager.get_colors(theme)

    # Show welcome message with theme
    if ctx.invoked_subcommand is None:
        # Only show if running arda without subcommand
        show_welcome(console, theme)


def show_welcome(console: Console, theme: str) -> None:
    """Show welcome message with theme styling"""
    # Create gradient title
    title = gradient_text("ARDA CLI", "white", "bright_white" if theme == "greyscale" else "cyan")

    # Create welcome panel
    panel = Panel(
        f"{title}\n\n"
        f"[muted]Theme:[/muted] [accent]{theme.upper()}[/accent]\n"
        f"[muted]Welcome to Arda - Infrastructure Management for NixOS[/muted]\n\n"
        f"[info]Use [command]arda --help[/command] for available commands[/info]",
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
    console = ctx.obj['console']
    theme = ctx.obj['theme']

    # Display header with consistent styling
    show_header(console, "HOST MANAGEMENT", "🖥️")

    if verbose:
        console.print("\n[info]Verbose mode enabled[/info]")

    console.print("\n[info]Host management - coming soon![/info]")

    # Show example of themed output
    console.print("\n[success]✓[/success] System checks passed")
    console.print("[warning]⚠[/warning] 1 host needs attention")
    console.print("[muted]ℹ[/muted] Total hosts: 5")


@rclick.command()
@click.pass_context
def roles(ctx: click.Context) -> None:
    """Role management commands"""
    console = ctx.obj['console']

    show_header(console, "ROLE MANAGEMENT", "⚙️")
    console.print("[info]Role management - coming soon![/info]")


@rclick.command()
@click.pass_context
def secrets(ctx: click.Context) -> None:
    """Secret management commands"""
    console = ctx.obj['console']

    show_header(console, "SECRET MANAGEMENT", "🔐")
    console.print("[info]Secret management - coming soon![/info]")


@rclick.command()
@click.pass_context
def templates(ctx: click.Context) -> None:
    """Template management commands"""
    console = ctx.obj['console']

    show_header(console, "TEMPLATE MANAGEMENT", "📦")
    console.print("[info]Template management - coming soon![/info]")


@rclick.command()
@click.option(
    '--list',
    '-l',
    is_flag=True,
    help='List all available themes'
)
@click.pass_context
def theme(ctx: click.Context, list: bool) -> None:
    """Theme management and preview

    View available themes or preview the current theme.
    """
    console = ctx.obj['console']

    if list:
        console.print("[title]Available Themes[/title]\n")

        for theme_name in theme_manager.list_themes():
            # Get theme colors
            colors = theme_manager.get_colors(theme_name)

            # Show theme name with example colors
            example = Text()
            example.append("  ", style="none")
            example.append("●", style=colors.get('info', 'white'))
            example.append(" ●", style=colors.get('success', 'green'))
            example.append(" ●", style=colors.get('warning', 'yellow'))
            example.append(" ●", style=colors.get('error', 'red'))

            console.print(f"[accent]{theme_name.upper()}[/accent]")
            console.print(example)
            console.print()
    else:
        # Preview current theme
        theme = ctx.obj['theme']
        console.print(f"[title]Current Theme: {theme.upper()}[/title]\n")

        colors = theme_manager.get_colors(theme)

        console.print(f"[info]ℹ Information[/info]")
        console.print(f"[success]✓ Success message[/success]")
        console.print(f"[warning]⚠ Warning message[/warning]")
        console.print(f"[error]✗ Error message[/error]")
        console.print(f"[command]> Command output[/command]")
        console.print(f"[muted]Muted text[/muted]")
        console.print(f"[accent]Accented text[/accent]")


if __name__ == "__main__":
    main()
