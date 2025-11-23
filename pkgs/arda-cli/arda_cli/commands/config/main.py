"""Configuration management commands."""

from typing import Any

import click

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


@click.group(invoke_without_command=True)
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
    """
    if ctx.invoked_subcommand is None:
        # Show help if no subcommand is provided
        click.echo(ctx.get_help())


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
        # Show all settings
        output.section("Configuration")
        theme_val = config_data.get("theme", {}).get("default", "dracula")
        verbose_val = config_data.get("output", {}).get("verbose", False)
        timestamp_val = config_data.get("output", {}).get("timestamp", True)

        output.info(f"Theme: {theme_val}")
        output.info(f"Verbose: {verbose_val}")
        output.info(f"Timestamp: {timestamp_val}")
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
            output.info(f"{key} = {value!r}")


@config.command(name="set")
@click.argument("key", nargs=1, type=str)
@click.argument("value", nargs=1, type=str)
@click.pass_context
def set_config(ctx: click.Context, key: str, value: str) -> None:
    """Set a configuration value.

    KEY should be in format 'section.key' (e.g., 'theme.default').

    VALUE should be the appropriate type:
    - theme.default: string (e.g., 'nord', 'dracula')
    - output.verbose: boolean ('true' or 'false')
    - output.timestamp: boolean ('true' or 'false')

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
    key_parts = key.split(".")
    if len(key_parts) != 2:
        output.error("Invalid key format. Use 'section.key' (e.g., 'theme.default')")
        return

    key_tuple = tuple(key_parts)
    if key_tuple not in ALLOWED_KEYS:
        valid_keys = ", ".join(f"{k[0]}.{k[1]}" for k in sorted(ALLOWED_KEYS))
        output.error(f"Invalid configuration key: {key}")
        output.info(f"Valid keys: {valid_keys}")
        return

    section, setting = key_parts

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
