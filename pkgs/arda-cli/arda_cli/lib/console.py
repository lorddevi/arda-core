"""Console and styling helpers using Rich."""

from rich.console import Console
from rich.panel import Panel


def create_console() -> Console:
    """Create a console instance for output.

    Returns:
        Console instance ready for themed output

    """
    return Console()


def print_header(text: str, console: Console) -> None:
    """Print a header with styling.

    Args:
        text: Header text to display
        console: Console instance to use for output

    """
    panel = Panel(
        f"[bold]{text}[/bold]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)


def print_info(text: str, console: Console) -> None:
    """Print an info message.

    Args:
        text: Info message text
        console: Console instance to use for output

    """
    console.print(f"[info]i {text}[/info]")


def print_success(text: str, console: Console) -> None:
    """Print a success message.

    Args:
        text: Success message text
        console: Console instance to use for output

    """
    console.print(f"[success]✓ {text}[/success]")


def print_warning(text: str, console: Console) -> None:
    """Print a warning message.

    Args:
        text: Warning message text
        console: Console instance to use for output

    """
    console.print(f"[warning]⚠ {text}[/warning]")


def print_error(text: str, console: Console) -> None:
    """Print an error message.

    Args:
        text: Error message text
        console: Console instance to use for output

    """
    console.print(f"[error]✗ {text}[/error]")
