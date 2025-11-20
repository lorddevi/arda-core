"""Host management command."""

import click
import rich_click as rclick

from arda_cli.lib.helpers import get_console_from_ctx


@rclick.command()
@click.pass_context
def host(ctx: click.Context) -> None:
    """Host management commands.

    Manage your NixOS hosts with beautiful, themed output.
    """
    console = get_console_from_ctx(ctx)

    # Check verbose setting from global config
    verbose = ctx.obj.get("verbose", False)

    # Show verbose output if enabled
    if verbose:
        console.print("\n[info]i Verbose mode enabled[/info]")
        console.print("[dim]Configuration:[/dim]")
        console.print(f"  [dim]• Theme: {ctx.obj.get('theme', 'unknown')}[/dim]")
        console.print(f"  [dim]• Timestamp: {ctx.obj.get('timestamp', False)}[/dim]")
        console.print(f"  [dim]• Verbose: {verbose}[/dim]")

    console.print("\nHost management - coming soon!")

    # Show example of themed output
    console.print("\n✓ System checks passed")
    console.print("⚠  1 host needs attention")
    console.print("i  Total hosts: 5")

    if verbose:
        console.print("\n[dim]Available operations:[/dim]")
        console.print("  [dim]• List all hosts[/dim]")
        console.print("  [dim]• Deploy configuration[/dim]")
        console.print("  [dim]• Update host settings[/dim]")
