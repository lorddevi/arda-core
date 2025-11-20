"""Theme management command."""

import click
import rich_click as rclick

from arda_cli.lib.helpers import get_console_from_ctx
from arda_cli.lib.theme import get_rich_click_themes


@rclick.command()
@click.option("--list", "-l", is_flag=True, help="List all available rich-click themes")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=None,
    help="Enable verbose output (overrides config default)",
)
@click.pass_context
def theme(ctx: click.Context, list: bool, verbose: bool | None) -> None:
    """Theme management and preview.

    View available rich-click themes or preview the current theme.
    """
    console = get_console_from_ctx(ctx)

    # Use --verbose flag if provided, otherwise use config default
    if verbose is None:
        verbose = ctx.obj.get("verbose", False)

    if list:
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
    else:
        # Preview current theme
        theme = ctx.obj["theme"]

        if verbose:
            console.print("\n[dim]Theme configuration:[/dim]")
            console.print(f"  [dim]• Active theme: {theme}[/dim]")
            console.print(f"  [dim]• Verbose mode: {verbose}[/dim]")
            console.print(
                f"  [dim]• Timestamp enabled: {ctx.obj.get('timestamp', False)}[/dim]\n"
            )

        console.print(f"Current Theme: {theme.upper()}\n")

        console.print("i  Information")
        console.print("✓ Success message")
        console.print("⚠ Warning message")
        console.print("✗ Error message")
        console.print("> Command output")
        console.print("Muted text")
