"""General helper functions for CLI commands."""

from typing import TYPE_CHECKING, cast

import click

if TYPE_CHECKING:
    from rich.console import Console


def check_and_show_help(ctx: click.Context) -> bool:
    """Check if any options were provided, return True if help should be shown.

    Args:
        ctx: Click context to check

    Returns:
        True if help should be shown, False if command should continue

    """
    # Check if any options were provided (excluding False for flags)
    if ctx.params and any(
        v is not None and v is not False for v in ctx.params.values()
    ):
        # Options were provided, don't show help
        return False

    # No options provided, show help
    ctx.get_help()
    return True


def get_console_from_ctx(ctx: click.Context) -> "Console":
    """Get console from Click context.

    Args:
        ctx: Click context object

    Returns:
        Console instance from context

    Raises:
        KeyError: If console not in context

    """
    console = ctx.obj.get("console")
    if console is None:
        raise KeyError("Console not found in context. Did you set ctx.obj['console']?")
    return cast("Console", console)


def get_theme_from_ctx(ctx: click.Context) -> str:
    """Get theme name from Click context.

    Args:
        ctx: Click context object

    Returns:
        Theme name string

    """
    return cast(str, ctx.obj.get("theme", "dracula"))
