"""Preview the current theme."""

import sys

import click
import rich_click as rclick

from arda_cli.lib.output import get_output_manager


@rclick.command()
@click.pass_context
def preview(ctx: click.Context) -> None:
    """Preview the current theme.

    Use --theme <name> before this command to preview a different theme.

    Example: arda --theme nord preview

    """
    output = get_output_manager(ctx)

    # Get the current theme from context
    preview_theme = ctx.obj["theme"]

    # Verbose configuration info
    if output.verbose:
        output.trace("Theme configuration:")
        output.debug(f"Current theme: {preview_theme}")
        output.debug(f"Verbose mode: {output.verbose}")
        output.debug(f"Timestamp enabled: {output.timestamps}")
        output.spacer()

    # Section header for top section
    output.section("Theme Info")

    # First line: Current Theme
    # Print with custom formatting to match original
    output.console.print(
        f"[{output.colors['text']}]Current Theme:[/{output.colors['text']}] "
        f"[{output.colors['separator_text']}]{preview_theme.upper()}[/{output.colors['separator_text']}]"
    )
    output.spacer()

    # Instructions
    output.console.print(
        f"[{output.colors['text']}]Preview a different theme:[/{output.colors['text']}]"
    )
    output.console.print("  [command]arda --theme <name> preview[/command]")
    output.spacer()
    output.console.print(
        f"[{output.colors['text']}]"
        f"To see all available themes:[/{output.colors['text']}]"
    )
    output.console.print("  [command]arda theme list[/command]")
    output.spacer()

    # Section 1: Message Types (no timestamps)
    output.section("Message Types")

    # Temporarily disable timestamps for this section
    original_timestamps = output.timestamps
    output.timestamps = False

    output.info("Information")
    output.success("Success message")
    output.warning("Warning message")
    output.error("Error message")

    # Restore original timestamp setting
    output.timestamps = original_timestamps
    output.spacer()

    # Section 2: Message Types With Timestamps
    output.section("Message Types With Timestamps")

    # Temporarily enable timestamps for these examples
    output.timestamps = True

    output.info("Information")
    output.success("Success message")
    output.warning("Warning message")
    output.error("Error message")

    # Restore original timestamp setting
    output.timestamps = original_timestamps
    output.spacer()

    # Section 3: Example Help
    output.section("Example Help")
    output.spacer()

    # Walk up to parent context
    parent_ctx = ctx
    while parent_ctx.parent is not None:
        parent_ctx = parent_ctx.parent

    # Get help text using the parent context's get_help() method
    help_text = parent_ctx.get_help()

    # Print help text directly to preserve ANSI codes
    sys.stdout.write(help_text)
