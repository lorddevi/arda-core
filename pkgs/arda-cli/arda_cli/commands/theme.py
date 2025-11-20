"""Theme management command."""

import click
import rich_click as rclick

from arda_cli.lib.helpers import get_console_from_ctx
from arda_cli.lib.theme import get_rich_click_themes


@rclick.command()
@click.option("--list", "-l", is_flag=True, help="List all available rich-click themes")
@click.pass_context
def theme(ctx: click.Context, list: bool) -> None:
    """Theme management and preview.

    View available rich-click themes or preview the current theme.
    """
    console = get_console_from_ctx(ctx)

    if list:
        console.print("Available Rich-Click Themes\n")

        for theme_name in get_rich_click_themes():
            console.print(f"  [accent]{theme_name}[/accent]")

        console.print(
            "\nNote: Themes can be combined with formats (slim, modern, nu, robo)"
        )
        console.print("Example: 'dracula-modern', 'forest-slim', 'nord-nu'")
    else:
        # Preview current theme
        theme = ctx.obj["theme"]
        console.print(f"Current Theme: {theme.upper()}\n")

        console.print("i  Information")
        console.print("✓ Success message")
        console.print("⚠ Warning message")
        console.print("✗ Error message")
        console.print("> Command output")
        console.print("Muted text")
