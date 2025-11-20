"""Arda CLI main entry point.

Arda uses rich-click's built-in themes for unified styling across
all help text and command output.
"""

import click
import rich_click as rclick
from rich import get_console
from rich.console import Console
from rich.panel import Panel

# Import commands from commands/ directory
from arda_cli.commands.host.main import host
from arda_cli.commands.roles.main import roles
from arda_cli.commands.secrets.main import secrets
from arda_cli.commands.templates.main import templates
from arda_cli.commands.theme import theme

# Import theme handling from lib
from arda_cli.lib.theme import get_rich_click_themes, patch_rich_click

# Patch click with theme configuration
patch_rich_click()


@rclick.group(
    no_args_is_help=True, context_settings={"help_option_names": ["-h", "--help"]}
)
@click.option(
    "--theme",
    type=str,
    default="dracula",
    help=(
        "Rich-click theme to use (see 'theme --list' for all options, "
        "e.g., dracula, forest, solarized)"
    ),
)
@click.option("--timestamp", is_flag=True, help="Add timestamps to output")
@click.pass_context
def main(ctx: click.Context, theme: str, timestamp: bool) -> None:
    """Arda - minimal infrastructure management for NixOS.

    A modern CLI tool with rich theming and beautiful output.
    Uses rich-click's built-in themes for unified styling.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Validate theme
    available_themes = get_rich_click_themes()
    if theme.lower() not in [t.lower() for t in available_themes]:
        console = get_console()
        console.print(f"[error]Error:[/error] Theme '{theme}' not found.")
        console.print(
            "Use [command]arda theme --list[/command] to see all available themes."
        )
        ctx.exit(1)

    # Store theme settings
    ctx.obj["theme"] = theme.lower()
    ctx.obj["timestamp"] = timestamp

    # Get themed console
    console = get_console()
    ctx.obj["console"] = console

    # Show welcome message with theme
    if ctx.invoked_subcommand is None:
        # Only show if running arda without subcommand
        show_welcome(console, theme)


def show_welcome(console: Console, theme: str) -> None:
    """Show welcome message with theme styling."""
    # Create title with rich text
    title = "ARDA CLI"

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


# Register commands with the main group
main.add_command(host)
main.add_command(roles)
main.add_command(secrets)
main.add_command(templates)
main.add_command(theme)


if __name__ == "__main__":
    main()
