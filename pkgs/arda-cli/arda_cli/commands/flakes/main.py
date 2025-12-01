"""Flakes management command."""

import click
import rich_click as rclick

from arda_cli.lib.output import get_output_manager, show_command_help


def flakes_help_callback(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    """Show help with active configuration."""
    if not value:
        return
    show_command_help(ctx)
    ctx.exit()


@rclick.group()
@click.option(
    "--help",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=flakes_help_callback,
    help="Show this help message and exit.",
)
@click.pass_context
def flakes(ctx: click.Context) -> None:
    """Flakes management commands.

    Create and manage Arda worlds using flakes.
    """
    # Show help when no subcommand is provided
    if ctx.invoked_subcommand is None:
        show_command_help(ctx)
        ctx.exit()


# Import subcommands
from arda_cli.commands.flakes.create import create  # noqa: E402

flakes.add_command(create)
