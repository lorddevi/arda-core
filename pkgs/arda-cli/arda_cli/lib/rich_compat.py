"""Compatibility layer for Rich library operations.

This module provides a compatibility layer to handle differences between
Rich library versions, particularly for API changes that may break in
different versions.
"""

from rich import get_console as _get_rich_console
from rich.console import Console
from rich.text import Text


def get_console() -> Console:
    """Get the default Rich console instance.

    This wrapper ensures compatibility across Rich library versions.

    Returns:
        Console: A Rich Console instance

    """
    try:
        console = _get_rich_console()
        return console
    except Exception:
        # Fallback: create a new console instance
        return Console()


def get_text_plain(text_obj: Text | str) -> str:
    """Get plain text from a Rich Text object.

    This wrapper handles the difference between Rich versions where .plain
    might be a property or method.

    Args:
        text_obj: A Rich Text object or string

    Returns:
        str: The plain text content

    """
    if isinstance(text_obj, str):
        return text_obj

    # Try accessing .plain as an attribute (Rich < 14)
    if hasattr(text_obj, "plain"):
        plain_value = text_obj.plain
        if callable(plain_value):
            return plain_value()
        return plain_value

    # Try accessing .plain as a method (Rich >= 14)
    if hasattr(text_obj, "get_plain"):
        return text_obj.get_plain()

    # Fallback: convert to string
    return str(text_obj)
