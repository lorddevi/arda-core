"""Configuration management commands."""

from typing import Any

import click
import rich_click as rclick

from arda_cli.lib.config import (
    get_config_for_viewing,
    get_config_for_writing,
    set_config_value,
)

ALLOWED_KEYS = {
    ("theme", "default"),
    ("output", "verbose"),
    ("output", "timestamp"),
}


@rclick.group()
@click.pass_context
def config(ctx: click.Context) -> None:
    """View and modify Arda configuration.

    The 'view' command shows current settings, while 'set' modifies configuration.

    Settings are read in priority order:
    1. XDG user config (~/.config/arda/arda.toml)
    2. Project config (etc/arda.toml)
    3. Package defaults

    The 'set' command writes to:
    1. XDG user config (if it exists)
    2. Project config (created if needed)

    Examples:
        arda config view              # View all settings
        arda config view theme.default  # View specific setting
        arda config set theme.default nord  # Set a value

    """
    pass


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

    # Get the full config with priority
    config_data = get_config_for_viewing()

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

    The value will be written to the highest-priority config file:
    1. XDG user config (if it exists)
    2. Project config (created if needed)

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
        config_path = get_config_for_writing()
        set_config_value(config_path, section, setting, parsed_value)
        output.success(f"Updated {key} = {parsed_value!r}")
        output.debug(f"Configuration written to: {config_path}")
    except Exception as e:
        output.error(f"Failed to update configuration: {e}")


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
