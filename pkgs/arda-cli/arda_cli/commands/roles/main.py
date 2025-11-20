"""Role management command."""

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
def roles(ctx: click.Context, verbose: bool | None) -> None:
    """Role management commands."""
    # Show help if no options provided
    if check_and_show_help(ctx):
        return

    console = get_console_from_ctx(ctx)

    # Use --verbose flag if provided, otherwise use config default
    if verbose is None:
        verbose = ctx.obj.get("verbose", False)

    if verbose:
        console.print("\n[info]i Verbose mode enabled[/info]")

    console.print("Role management - coming soon!")

    if verbose:
        console.print("\n[dim]Available operations:[/dim]")
        console.print("  [dim]• List all roles[/dim]")
        console.print("  [dim]• Assign roles to hosts[/dim]")
        console.print("  [dim]• Create new role definitions[/dim]")
