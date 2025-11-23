"""Template management command."""

import click
import rich_click as rclick

from arda_cli.lib.output import get_output_manager


@rclick.command(no_args_is_help=True)
@click.pass_context
def templates(ctx: click.Context) -> None:
    """Template management commands."""
    output = get_output_manager(ctx)

    output.info("Template management - coming soon!")

    # Verbose operations list (only shown with --verbose)
    output.section("Available operations")
    output.debug("• List all templates")
    output.debug("• Create new template")
    output.debug("• Apply template to host")
    output.debug("• Update template definition")
