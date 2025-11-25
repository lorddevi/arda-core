"""Role management command."""

import click
import rich_click as rclick

from arda_cli.lib.output import get_output_manager, show_command_help


def roles_help_callback(
    ctx: click.Context, param: click.Parameter, value: bool
) -> None:
    """Show help with active configuration."""
    if not value:
        return
    show_command_help(ctx)
    ctx.exit()


@rclick.command()
@click.option(
    "--help",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=roles_help_callback,
    help="Show this help message and exit.",
)
@click.pass_context
def roles(ctx: click.Context) -> None:
    """Role management commands."""
    # Show help when no subcommand is provided (matching arda --help)
    if ctx.invoked_subcommand is None:
        show_command_help(ctx)
        ctx.exit()

    output = get_output_manager(ctx)
    output.info("Role management - coming soon!")

    # Verbose operations list (only shown with --verbose)
    output.section("Available operations")
    output.debug("• List all roles")
    output.debug("• Assign roles to hosts")
    output.debug("• Create new role definitions")
