"""Theme management command."""

import click
import rich_click as rclick

from arda_cli.commands.theme.list import list
from arda_cli.commands.theme.preview import preview


@rclick.group()
@click.pass_context
def theme(ctx: click.Context) -> None:
    """Theme management and preview.

    View available rich-click themes or preview the current theme.
    """
    pass


# Register sub-commands
theme.add_command(list)
theme.add_command(preview)
