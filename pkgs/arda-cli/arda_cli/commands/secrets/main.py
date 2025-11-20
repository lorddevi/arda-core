"""Secret management command."""

import click
import rich_click as rclick

from arda_cli.lib.helpers import check_and_show_help, get_console_from_ctx


@rclick.command()
@click.pass_context
def secrets(ctx: click.Context) -> None:
    """Secret management commands."""
    # Show help if no options provided
    if check_and_show_help(ctx):
        return

    console = get_console_from_ctx(ctx)

    console.print("Secret management - coming soon!")
