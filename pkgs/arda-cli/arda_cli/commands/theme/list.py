"""List all available themes."""

import click
import rich_click as rclick

from arda_cli.lib.output import get_output_manager
from arda_cli.lib.theme import get_rich_click_themes


@rclick.command()
@click.pass_context
def list(ctx: click.Context) -> None:
    """List all available rich-click themes."""
    output = get_output_manager(ctx)

    output.info("Available Rich-Click Themes")

    # Show total count in verbose mode
    if output.verbose:
        total_themes = len(get_rich_click_themes())
        output.debug(f"Total themes: {total_themes}")

    output.spacer()

    for theme_name in get_rich_click_themes():
        # Print theme name (simpler formatting for list)
        output.console.print(f"  [accent]{theme_name}[/accent]")

    output.spacer()

    # Show helpful info
    output.console.print(
        "Note: Themes can be combined with formats (slim, modern, nu, robo)"
    )
    output.console.print("Example: 'dracula-modern', 'forest-slim', 'nord-nu'")

    output.spacer()

    output.console.print(
        "[dim]To preview a theme, use:[/dim] "
        "[command]arda --theme <name> preview[/command]"
    )
    output.console.print(
        "[dim]Example:[/dim] [command]arda --theme nord preview[/command]"
    )
