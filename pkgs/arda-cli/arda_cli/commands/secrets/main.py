"""Secret management command."""

import click
import rich_click as rclick

from arda_cli.lib.output import get_output_manager


@rclick.command(no_args_is_help=True)
@click.pass_context
def secrets(ctx: click.Context) -> None:
    """Secret management commands."""
    output = get_output_manager(ctx)

    output.info("Secret management - coming soon!")

    # Verbose operations list (only shown with --verbose)
    output.section("Available operations")
    output.debug("• List all secrets")
    output.debug("• Encrypt new secrets")
    output.debug("• Decrypt and view secrets")
    output.debug("• Rotate secret keys")
