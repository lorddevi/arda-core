"""List all available themes."""

import click
import rich_click as rclick

from arda_cli.lib.helpers import get_console_from_ctx
from arda_cli.lib.theme import get_rich_click_themes


@rclick.command()
@click.pass_context
def list(ctx: click.Context) -> None:
    """List all available rich-click themes."""
    console = get_console_from_ctx(ctx)

    # Check verbose setting from global config
    verbose = ctx.obj.get("verbose", False)

    console.print("Available Rich-Click Themes\n")

    if verbose:
        total_themes = len(get_rich_click_themes())
        console.print(f"[dim]Total themes: {total_themes}[/dim]\n")

    for theme_name in get_rich_click_themes():
        console.print(f"  [accent]{theme_name}[/accent]")

    console.print(
        "\nNote: Themes can be combined with formats (slim, modern, nu, robo)"
    )
    console.print("Example: 'dracula-modern', 'forest-slim', 'nord-nu'")
