"""Role management command."""

import click
import rich_click as rclick

from arda_cli.lib.output import get_output_manager


@rclick.command(no_args_is_help=True)
@click.pass_context
def roles(ctx: click.Context) -> None:
    """Role management commands."""
    output = get_output_manager(ctx)

    output.info("Role management - coming soon!")

    # Verbose operations list (only shown with --verbose)
    output.section("Available operations")
    output.debug("• List all roles")
    output.debug("• Assign roles to hosts")
    output.debug("• Create new role definitions")
