"""Configuration management commands."""

from typing import Any

import click
import rich_click as rclick
from rich.console import Console

from arda_cli.lib.config import (
    get_active_config_path,
    get_config_for_viewing,
    get_config_for_writing,
    load_default_config,
    set_config_value,
)

ALLOWED_KEYS = {
    ("theme", "default"),
    ("output", "verbose"),
    ("output", "timestamp"),
}


def show_config_help(ctx: click.Context) -> None:
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
    from arda_cli.lib.output import ExtraHelpPanelBuilder

    builder = ExtraHelpPanelBuilder(
        title="Extra Help",
        theme=theme_name,
        helptext_style=helptext_style,
    )

    builder.add_description("Examples:").add_command(
        "arda config view", "View all settings", option_style
    ).add_command(
        "arda config view theme.default", "View specific setting", option_style
    ).add_command(
        "arda config set theme.default nord", "Set a value", option_style
    ).add_command(
        "arda config --local set theme nord", "Set in project config", option_style
    ).add_command(
        "arda config --global set theme nord", "Set in XDG config", option_style
    )

    panel = builder.build()
    console = Console()
    console.print(panel)

    # Show active config
    _config_path, config_source = get_active_config_path()
    console.print(f"[dim]Active configuration:[/dim] [white]{config_source}[/white]\n")


def config_help_callback(
    ctx: click.Context, param: click.Parameter, value: bool
) -> None:
    """Show help with extra help panel."""
    if not value:
        return
    show_config_help(ctx)
    ctx.exit()


@rclick.group(invoke_without_command=True)
@click.option(
    "--global",
    "force_global",
    is_flag=True,
    help="Use global XDG config (~/.config/arda/arda.toml)",
)
@click.option(
    "--local",
    "force_local",
    is_flag=True,
    help="Use local project config (etc/arda.toml)",
)
@click.option(
    "--help",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=config_help_callback,
    help="Show this help message and exit.",
)
@click.pass_context
def config(ctx: click.Context, force_global: bool, force_local: bool) -> None:
    """View and modify Arda configuration.

    The 'view' command shows current settings, while 'set' modifies configuration.

    Settings are read in priority order:
    1. Project config (etc/arda.toml)
    2. XDG user config (~/.config/arda/arda.toml)
    3. Package defaults

    Use --global to force using the XDG config location.
    Use --local to force using the project config location.



    Examples:
        arda config view              # View all settings
        arda config view theme.default  # View specific setting
        arda config set theme.default nord  # Set a value
        arda config --local set theme nord  # Set in project config
        arda config --global set theme nord  # Set in XDG config

    """
    # Store the force flags in context
    ctx.ensure_object(dict)
    ctx.obj["force_global"] = force_global
    ctx.obj["force_local"] = force_local

    # Validate that both flags aren't used together
    if force_global and force_local:
        click.echo("Error: Cannot use both --global and --local together", err=True)
        ctx.exit(1)

    # Show full help with Extra Help panel when no subcommand is provided
    # This ensures 'arda config' shows the same output as 'arda config --help'
    if ctx.invoked_subcommand is None:
        show_config_help(ctx)
        ctx.exit()


@config.command(name="view")
@click.argument("key", required=False)
@click.pass_context
def view_config(ctx: click.Context, key: str | None) -> None:
    """View configuration settings.

    With no arguments, shows all settings.

    With KEY, shows the value of that specific setting.
    KEY should be in format 'section.key' (e.g., 'theme.default').
    """
    # Get or create output manager
    try:
        from arda_cli.lib.output import get_output_manager

        output: Any = get_output_manager(ctx)
        # Use console directly for clean output
        console = output.console
    except Exception:
        # Fallback if output manager can't be created
        from rich.console import Console

        console = Console()

        # Simple print helper
        class SimpleOutput:
            def section(self, title: str) -> None:
                console.print(f"\n[bold]{title}[/bold]")
                console.print("─" * 50)

            def info(self, message: str) -> None:
                console.print("[cyan]i[/cyan] " + message)

            def warning(self, message: str) -> None:
                console.print(f"[yellow]⚠[/yellow] {message}")

            def error(self, message: str) -> None:
                console.print(f"[red]✗[/red] {message}")

        output = SimpleOutput()

    # Get the force flags from context
    force_global = ctx.obj.get("force_global", False) if ctx.obj else False
    force_local = ctx.obj.get("force_local", False) if ctx.obj else False

    # Get the full config with priority, respecting force flags
    config_data = get_config_for_viewing(
        force_global=force_global, force_local=force_local
    )

    if not key:
        # Show all settings with clean, color-coded output
        output.section("Configuration")

        theme_val = config_data.get("theme", {}).get("default", "dracula")
        verbose_val = config_data.get("output", {}).get("verbose", False)
        timestamp_val = config_data.get("output", {}).get("timestamp", True)

        # Color-coded output: setting name | hyphen | value
        console.print(f"[cyan]Theme[/cyan] [dim]-[/dim] [white]{theme_val}[/white]")
        console.print(f"[cyan]Verbose[/cyan] [dim]-[/dim] [white]{verbose_val}[/white]")
        console.print(
            f"[cyan]Timestamp[/cyan] [dim]-[/dim] [white]{timestamp_val}[/white]"
        )
    else:
        # Show specific key
        key_parts = key.split(".")

        # Validate the key
        if len(key_parts) != 2:
            output.error(
                "Invalid key format. Use 'section.key' (e.g., 'theme.default')"
            )
            return

        key_tuple = tuple(key_parts)
        if key_tuple not in ALLOWED_KEYS:
            valid_keys = ", ".join(f"{k[0]}.{k[1]}" for k in sorted(ALLOWED_KEYS))
            output.error(f"Invalid configuration key: {key}")
            output.info(f"Valid keys: {valid_keys}")
            return

        section, setting = key_parts

        value = config_data.get(section, {}).get(setting)

        if value is None:
            output.warning(f"Setting not found: {key}")
        else:
            # Clean color-coded output: key = value
            console.print(
                f"[cyan]{setting}[/cyan] [dim]=[/dim] [white]{value!r}[/white]"
            )


@config.command(name="set")
@click.argument("key", nargs=1, type=str)
@click.argument("value", nargs=1, type=str)
@click.pass_context
def set_config(ctx: click.Context, key: str, value: str) -> None:
    """Set a configuration value.

    KEY can be in either format:
    - Full: 'section.key' (e.g., 'theme.default')
    - Shorthand: just 'setting' (e.g., 'theme', 'verbose', 'timestamp')

    VALUE should be the appropriate type:
    - theme: string (e.g., 'nord', 'dracula', 'forest')
    - verbose: boolean ('true' or 'false')
    - timestamp: boolean ('true' or 'false')

    Examples:
        arda config set theme nord
        arda config set theme.default forest
        arda config set verbose true
        arda config set output.timestamp false
        arda config --local set theme nord  # Write to project config
        arda config --global set theme nord  # Write to XDG config

    The value will be written to the config file:
    - Use --local to write to project config (etc/arda.toml)
    - Use --global to write to XDG config (~/.config/arda/arda.toml)

    Without flags, writes to the high-priority config file (see 'arda config --help').

    Never modifies the package default configuration.

    """
    # Get or create output manager
    try:
        from arda_cli.lib.output import get_output_manager

        output: Any = get_output_manager(ctx)
    except Exception:
        # Fallback if output manager can't be created
        from rich.console import Console

        console = Console()

        # Simple print helper
        class SimpleOutput:
            def section(self, title: str) -> None:
                console.print(f"\n[bold]{title}[/bold]")
                console.print("─" * 50)

            def info(self, message: str) -> None:
                console.print("[cyan]i[/cyan] " + message)

            def success(self, message: str) -> None:
                console.print(f"[green]✓[/green] {message}")

            def debug(self, message: str) -> None:
                console.print(f"[dim]{message}[/dim]")

            def warning(self, message: str) -> None:
                console.print(f"[yellow]⚠[/yellow] {message}")

            def error(self, message: str) -> None:
                console.print(f"[red]✗[/red] {message}")

        output = SimpleOutput()

    # Get the force flags from context
    force_global = ctx.obj.get("force_global", False) if ctx.obj else False
    force_local = ctx.obj.get("force_local", False) if ctx.obj else False

    # Parse and validate key
    # Support both shorthand (theme) and full (theme.default) formats
    key = key.lower()
    if "." in key:
        # Full format: theme.default
        key_parts = key.split(".")
        if len(key_parts) != 2:
            output.error(
                "Invalid key format. Use 'section.key' (e.g., 'theme.default') "
                "or shorthand (e.g., 'theme')"
            )
            return
        key_tuple = tuple(key_parts)
        if key_tuple not in ALLOWED_KEYS:
            valid_keys = ", ".join(f"{k[0]}.{k[1]}" for k in sorted(ALLOWED_KEYS))
            output.error(f"Invalid configuration key: {key}")
            output.info(f"Valid keys: {valid_keys}")
            return
        section, setting = key_parts
    else:
        # Shorthand format: theme, verbose, timestamp
        # Map shorthand to full key
        shorthand_map = {
            "theme": ("theme", "default"),
            "verbose": ("output", "verbose"),
            "timestamp": ("output", "timestamp"),
        }

        if key not in shorthand_map:
            valid_keys = ", ".join(f"{k[0]}.{k[1]}" for k in sorted(ALLOWED_KEYS))
            output.error(f"Invalid configuration key: {key}")
            output.info(f"Valid keys: {valid_keys}")
            return

        section, setting = shorthand_map[key]

    # Parse and validate value
    try:
        parsed_value = parse_config_value(setting, value)
    except ValueError as e:
        output.error(str(e))
        return

    # Set the value
    try:
        config_path = get_config_for_writing(
            force_global=force_global, force_local=force_local
        )
        set_config_value(config_path, section, setting, parsed_value)
        output.success(f"Updated {key} = {parsed_value!r}")
        output.debug(f"Configuration written to: {config_path}")
    except Exception as e:
        output.error(f"Failed to update configuration: {e}")


@config.command(name="init")
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing configuration without prompting",
)
@click.pass_context
def init_config(ctx: click.Context, force: bool) -> None:
    """Initialize a configuration file.

    Copies the default configuration to the specified location.

    Without flags, initializes the project config (etc/arda.toml).
    Use --local to explicitly initialize the project config.
    Use --global to initialize the XDG config (~/.config/arda/arda.toml).

    Examples:
        arda config init                      # Initialize project config
        arda config --local init             # Initialize project config
        arda config --global init            # Initialize XDG config
        arda config init --force             # Overwrite existing

    """
    # Get the force flags from parent context
    force_global = (
        ctx.parent.obj.get("force_global", False) if ctx.parent.obj else False
    )
    force_local = ctx.parent.obj.get("force_local", False) if ctx.parent.obj else False

    # Get or create output manager
    try:
        from arda_cli.lib.output import get_output_manager

        output: Any = get_output_manager(ctx)
    except Exception:
        # Fallback if output manager can't be created
        from rich.console import Console

        console = Console()

        # Simple print helper
        class SimpleOutput:
            def section(self, title: str) -> None:
                console.print(f"\n[bold]{title}[/bold]")
                console.print("─" * 50)

            def info(self, message: str) -> None:
                console.print("[cyan]i[/cyan] " + message)

            def success(self, message: str) -> None:
                console.print(f"[green]✓[/green] {message}")

            def warning(self, message: str) -> None:
                console.print(f"[yellow]⚠[/yellow] {message}")

            def error(self, message: str) -> None:
                console.print(f"[red]✗[/red] {message}")

        output = SimpleOutput()

    # Determine target config path
    from arda_cli.lib.config import get_config_for_writing

    target_path = get_config_for_writing(
        force_global=force_global, force_local=force_local
    )

    # Check if file already exists
    if target_path.exists():
        if not force:
            if not click.confirm(
                f"Configuration file already exists at {target_path}\nOverwrite?"
            ):
                output.info("Initialization cancelled")
                return
        output.warning(f"Overwriting existing configuration at {target_path}")

    # Create the config file with defaults
    try:
        # Ensure parent directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Load default config
        default_config = load_default_config()

        # Write to file
        import tomli_w

        with open(target_path, "wb") as f:
            tomli_w.dump(default_config, f)

        output.success(f"Configuration initialized at {target_path}")
    except Exception as e:
        output.error(f"Failed to initialize configuration: {e}")


def parse_config_value(setting: str, value: str) -> str | bool:
    """Parse and validate a configuration value based on the setting type.

    Args:
        setting: The configuration setting name
        value: The value as a string

    Returns:
        The parsed value in the correct type

    Raises:
        ValueError: If the value is invalid for the setting type

    """
    if setting == "default":
        # Theme name - keep as string
        return value

    elif setting in ("verbose", "timestamp"):
        # Boolean values
        value_lower = value.lower()
        if value_lower in ("true", "1", "yes", "on"):
            return True
        elif value_lower in ("false", "0", "no", "off"):
            return False
        else:
            valid_true = ", ".join(["true", "1", "yes", "on"])
            valid_false = ", ".join(["false", "0", "no", "off"])
            raise ValueError(
                f"Invalid boolean value for {setting}: {value!r}\n"
                f"Use: {valid_true} for true, or {valid_false} for false"
            )

    else:
        # Unknown setting
        raise ValueError(f"Unknown setting: {setting}")
