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


@rclick.command()
@click.pass_context
def preview(ctx: click.Context) -> None:
    """Preview the current theme."""
    console = get_console_from_ctx(ctx)

    # Check verbose setting from global config
    verbose = ctx.obj.get("verbose", False)

    # Preview current theme
    theme_name = ctx.obj["theme"]

    if verbose:
        console.print("\n[dim]Theme configuration:[/dim]")
        console.print(f"  [dim]• Active theme: {theme_name}[/dim]")
        console.print(f"  [dim]• Verbose mode: {verbose}[/dim]")
        console.print(
            f"  [dim]• Timestamp enabled: {ctx.obj.get('timestamp', False)}[/dim]\n"
        )

    console.print(f"Current Theme: {theme_name.upper()}\n")

    # Use styled console helpers to show themed message types
    print_info("Information", console)
    print_success("Success message", console)
    print_warning("Warning message", console)
    print_error("Error message", console)

    # Show plain output example
    console.print("> Command output")
    console.print("[dim]Muted text[/dim]")
