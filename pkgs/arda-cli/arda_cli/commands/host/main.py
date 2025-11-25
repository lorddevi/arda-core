"""Host management command."""

import click
import rich_click as rclick

from arda_cli.lib.output import get_output_manager, show_command_help


def host_help_callback(ctx: click.Context, param: click.Parameter, value: bool) -> None:
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
    callback=host_help_callback,
    help="Show this help message and exit.",
)
@click.pass_context
def host(ctx: click.Context) -> None:
    """Host management commands.

    Manage your NixOS hosts with beautiful, themed output.
    """
    output = get_output_manager(ctx)

    # Show help when no subcommand is provided (matching arda --help)
    if ctx.invoked_subcommand is None:
        show_command_help(ctx)
        ctx.exit()

    output.info("Host management - coming soon!")

    # Show example of themed output
    output.success("System checks passed")
    output.warning("1 host needs attention")
    output.info("Total hosts: 5")

    # Verbose operations list (only shown with --verbose)
    output.section("Available operations")
    output.debug("• List all hosts")
    output.debug("• Deploy configuration")
    output.debug("• Update host settings")
