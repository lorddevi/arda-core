"""Role management command."""

import click
import rich_click as rclick

from arda_cli.lib.helpers import get_console_from_ctx


@rclick.command()
@click.pass_context
def roles(ctx: click.Context) -> None:
    """Role management commands."""
    console = get_console_from_ctx(ctx)

    # Check verbose setting from global config
    verbose = ctx.obj.get("verbose", False)

    if verbose:
        console.print("\n[info]i Verbose mode enabled[/info]")

    console.print("Role management - coming soon!")

    if verbose:
        console.print("\n[dim]Available operations:[/dim]")
        console.print("  [dim]• List all roles[/dim]")
        console.print("  [dim]• Assign roles to hosts[/dim]")
        console.print("  [dim]• Create new role definitions[/dim]")
