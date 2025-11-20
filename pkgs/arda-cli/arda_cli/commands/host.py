"""Host management command."""

import click
import rich_click as rclick

from arda_cli.lib.helpers import check_and_show_help, get_console_from_ctx


@rclick.command()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def host(ctx: click.Context, verbose: bool) -> None:
    """Host management commands.

    Manage your NixOS hosts with beautiful, themed output.
    """
    # Show help if no options provided
    if check_and_show_help(ctx):
        return

    console = get_console_from_ctx(ctx)

    if verbose:
        console.print("\nVerbose mode enabled")

    console.print("\nHost management - coming soon!")

    # Show example of themed output
    console.print("\n✓ System checks passed")
    console.print("⚠  1 host needs attention")
    console.print("i  Total hosts: 5")
