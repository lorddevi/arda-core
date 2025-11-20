"""Secret management command."""

import click
import rich_click as rclick

from arda_cli.lib.helpers import check_and_show_help, get_console_from_ctx


@rclick.command()
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=None,
    help="Enable verbose output (overrides config default)",
)
@click.pass_context
def secrets(ctx: click.Context, verbose: bool | None) -> None:
    """Secret management commands."""
    # Show help if no options provided
    if check_and_show_help(ctx):
        return

    console = get_console_from_ctx(ctx)

    # Use --verbose flag if provided, otherwise use config default
    if verbose is None:
        verbose = ctx.obj.get("verbose", False)

    if verbose:
        console.print("\n[info]ℹ Verbose mode enabled[/info]")

    console.print("Secret management - coming soon!")

    if verbose:
        console.print("\n[dim]Available operations:[/dim]")
        console.print("  [dim]• List all secrets[/dim]")
        console.print("  [dim]• Encrypt new secrets[/dim]")
        console.print("  [dim]• Decrypt and view secrets[/dim]")
        console.print("  [dim]• Rotate secret keys[/dim]")
