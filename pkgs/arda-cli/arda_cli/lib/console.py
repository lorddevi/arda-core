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
    console.print(f"[bold blue]i[/bold blue] {text}")


def print_success(text: str, console: Console) -> None:
    """Print a success message.

    Args:
        text: Success message text
        console: Console instance to use for output

    """
    console.print(f"[bold green]✓[/bold green] {text}")


def print_warning(text: str, console: Console) -> None:
    """Print a warning message.

    Args:
        text: Warning message text
        console: Console instance to use for output

    """
    console.print(f"[bold yellow]⚠[/bold yellow] {text}")


def print_error(text: str, console: Console) -> None:
    """Print an error message with border.

    Args:
        text: Error message text
        console: Console instance to use for output

    """
    # Use a Panel to create a bordered error box (like Click's error display)
    panel = Panel(
        f"[bold red]{text}[/bold red]",
        title="[bold red]Error[/bold red]",
        border_style="red",
        padding=(1, 2),
    )
    console.print(panel)


def print_preview_section(title: str, content: str, console: Console) -> None:
    """Print a preview section with a border (like help output).

    Args:
        title: Section title
        content: Section content
        console: Console instance to use for output

    """
    panel = Panel(
        content,
        title=f"[bold]{title}[/bold]",
        border_style="blue",
        padding=(1, 2),
    )
    console.print(panel)
