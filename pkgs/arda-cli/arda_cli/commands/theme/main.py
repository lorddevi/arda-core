"""Theme management command."""

import click
import rich_click as rclick
from rich.console import Console

from arda_cli.commands.theme.list import list
from arda_cli.commands.theme.preview import preview


def show_theme_help(ctx: click.Context) -> None:
    """Show help with extra help panel."""
    # Get base help
    click.echo(ctx.get_help())

    # Get theme colors
    from rich_click.rich_help_configuration import RichHelpConfiguration

    theme_name = ctx.obj.get("theme", "dracula") if ctx.obj else "dracula"
    config = RichHelpConfiguration(theme=theme_name, enable_theme_env_var=True)

    # Get styles for different content types
    helptext_style = str(config.style_helptext_first_line or "default")
    option_style = str(config.style_option or "#5e81ac")

    # Create styled content using the builder API
    # This is much simpler than manually creating Text objects and tuples!
    from arda_cli.lib.output import ExtraHelpPanelBuilder

    builder = ExtraHelpPanelBuilder(
        title="Extra Help",
        theme=theme_name,
        helptext_style=helptext_style,
    )

    builder.add_description("Examples:").add_command(
        "arda theme list", "List all available themes", option_style
    ).add_command(
        "arda --theme nord preview", "Preview the nord theme", option_style
    ).add_command(
        "arda theme preview", "Preview the current theme", option_style
    ).add_spacer().add_description("To preview a different theme:").add_command(
        "arda --theme <name> preview", "Preview a specific theme", option_style
    ).add_spacer().add_description("To change the theme permanently:").add_command(
        "arda config set theme <theme>", "Set in project config", option_style
    ).add_command(
        "arda config --global set theme <theme>", "Set in user config", option_style
    )

    panel = builder.build()
    console = Console()
    console.print(panel)

    # Show active config (blank line before and after, matching arda --help)
    from arda_cli.lib.config import get_active_config_path

    _config_path, config_source = get_active_config_path()
    console.print(
        f"\n[dim]Active configuration:[/dim] [white]{config_source}[/white]\n"
    )


def theme_help_callback(
    ctx: click.Context, param: click.Parameter, value: bool
) -> None:
    """Show help with extra help panel."""
    if not value:
        return
    show_theme_help(ctx)
    ctx.exit()


@rclick.group(invoke_without_command=True)
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

    """
    ctx.ensure_object(dict)

    # Show full help with Extra Help panel when no subcommand is provided
    # This ensures 'arda theme' shows the same output as 'arda theme --help'
    if ctx.invoked_subcommand is None:
        show_theme_help(ctx)
        ctx.exit()


# Register sub-commands
theme.add_command(list)
theme.add_command(preview)
