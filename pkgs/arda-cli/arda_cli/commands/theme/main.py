"""Theme management command."""

import click
import rich_click as rclick
from rich.console import Console

from arda_cli.commands.theme.list import list
from arda_cli.commands.theme.preview import preview


def show_theme_help(ctx: click.Context) -> None:
    """Show help with custom formatting for the command instruction."""
    # Get base help
    click.echo(ctx.get_help())

    # Show custom formatted instruction
    console = Console()
    console.print("\n[bold]To preview a different theme:[/bold]")
    console.print("  [bold cyan]arda --theme <name> preview[/bold cyan]\n")

    # Show active config
    from arda_cli.lib.config import get_active_config_path
    config_path, config_source = get_active_config_path()
    console.print(f"[dim]Active configuration:[/dim] [white]{config_source}[/white]\n")


def theme_help_callback(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    """Callback to show help with custom formatting."""
    if not value:
        return
    show_theme_help(ctx)
    ctx.exit()


@rclick.group()
@click.option(
    "--help",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=theme_help_callback,
    help="Show this help message and exit.",
)
@click.pass_context
def theme(ctx: click.Context) -> None:
    """Theme management and preview.

    View available rich-click themes or preview the current theme.

    To preview a different theme, use: arda --theme <name> preview


    Examples:
        arda theme list              # List all available themes
        arda --theme nord preview    # Preview the nord theme
        arda theme preview           # Preview the current theme

    """
    ctx.ensure_object(dict)


# Register sub-commands
theme.add_command(list)
theme.add_command(preview)
