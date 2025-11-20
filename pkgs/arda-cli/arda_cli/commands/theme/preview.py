"""Preview the current theme."""

import click
import rich_click as rclick

from arda_cli.lib.console import (
    print_error,
    print_info,
    print_success,
    print_warning,
)
from arda_cli.lib.helpers import get_console_from_ctx
from arda_cli.lib.theme import get_rich_click_themes


@rclick.command()
@click.argument("theme_name", required=False)
@click.pass_context
def preview(ctx: click.Context, theme_name: str | None) -> None:
    """Preview a theme.

    Args:
        ctx: Click context object
        theme_name: Optional theme name to preview. If not provided,
                   uses the current theme from global config.

    """
    console = get_console_from_ctx(ctx)

    # Check verbose setting from global config
    verbose = ctx.obj.get("verbose", False)

    # Use provided theme name or fall back to current theme
    if theme_name:
        # Validate the theme name
        available_themes = [t.lower() for t in get_rich_click_themes()]
        if theme_name.lower() not in available_themes:
            print_error(f"Theme '{theme_name}' not found.", console)
            console.print(
                "\n[dim]Use '[/dim][command]arda theme list[/command]"
                "[dim]' to see all available themes.[/dim]"
            )
            ctx.exit(1)
        # Use the provided theme
        preview_theme = theme_name.lower()
    else:
        # Use the current theme from context
        preview_theme = ctx.obj["theme"]

    if verbose:
        console.print("\n[dim]Theme configuration:[/dim]")
        console.print(f"  [dim]• Previewing theme: {preview_theme}[/dim]")
        console.print(f"  [dim]• Verbose mode: {verbose}[/dim]")
        console.print(
            f"  [dim]• Timestamp enabled: {ctx.obj.get('timestamp', False)}[/dim]\n"
        )

    console.print(f"Current Theme: {preview_theme.upper()}\n")

    # Use styled console helpers to show themed message types
    print_info("Information", console)
    print_success("Success message", console)
    print_warning("Warning message", console)
    print_error("Error message", console)

    # Show plain output example
    console.print("> Command output")
    console.print("[dim]Muted text[/dim]")
