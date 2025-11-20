"""Secret management command."""

import click
import rich_click as rclick

from arda_cli.lib.helpers import get_console_from_ctx


@rclick.command()
@click.pass_context
def secrets(ctx: click.Context) -> None:
    """Secret management commands."""
    console = get_console_from_ctx(ctx)

    # Check verbose setting from global config
    verbose = ctx.obj.get("verbose", False)

    if verbose:
        console.print("\n[info]i Verbose mode enabled[/info]")

    console.print("Secret management - coming soon!")

    if verbose:
        console.print("\n[dim]Available operations:[/dim]")
        console.print("  [dim]• List all secrets[/dim]")
        console.print("  [dim]• Encrypt new secrets[/dim]")
        console.print("  [dim]• Decrypt and view secrets[/dim]")
        console.print("  [dim]• Rotate secret keys[/dim]")
