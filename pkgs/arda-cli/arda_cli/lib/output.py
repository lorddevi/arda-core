"""Centralized output management system.

This module provides a unified interface for all console output operations,
including themes, verbosity levels, tags, timestamps, and debugging features.
"""

from __future__ import annotations

import time
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
from rich_click.rich_help_configuration import RichHelpConfiguration


class VerbosityLevel(Enum):
    """Verbosity levels for different output detail.

    QUIET:    Errors only (no normal output)
    NORMAL:   Standard output (default)
    VERBOSE:  Additional info
    DEBUG:    Full debugging traces
    """

    QUIET = 0
    NORMAL = 1
    VERBOSE = 2
    DEBUG = 3


class MessageType(Enum):
    """Types of messages with associated tags and colors."""

    INFO = ("i", "info")
    SUCCESS = ("✓", "success")
    WARNING = ("⚠", "warning")
    ERROR = ("✗", "error")
    DEBUG = ("DBG", "debug")


class OutputManager:
    """Centralized output management with themes, verbosity, and tags.

    This class provides a unified interface for all console output operations,
    handling themes, timestamps, verbosity levels, and message formatting.

    Example:
        output = OutputManager(ctx, theme="nord", verbose=True, timestamps=True)
        output.info("Starting operation")
        output.debug("Configuration loaded")
        output.success("Operation complete!")

    """

    def __init__(
        self,
        ctx: click.Context,
        theme: str,
        verbose: bool,
        timestamps: bool,
    ):
        """Initialize OutputManager with settings.

        Args:
            ctx: Click context object
            theme: Theme name (e.g., 'nord', 'dracula', 'forest')
            verbose: Enable verbose output (--verbose flag)
            timestamps: Enable timestamps in output

        """
        self.ctx = ctx
        self.theme = theme
        self.verbose = verbose
        self.timestamps = timestamps

        # Set console
        self.console = Console()

        # Load theme colors
        self.colors = self._load_theme_colors()

        # Step counter for step tracking
        self._step_counter = 0

    # ============================================================================
    # CORE MESSAGE METHODS
    # ============================================================================

    def info(self, message: str, verbose_only: bool = False) -> None:
        """Print info message with [i INFO] tag.

        Args:
            message: The message to display
            verbose_only: If True, only show when --verbose is enabled

        """
        if verbose_only and not self.verbose:
            return

        timestamp = self._get_timestamp()
        tag = self._format_tag("INFO", self.colors["tag_info"])
        self._print_line(timestamp, tag, message)

    def success(self, message: str, verbose_only: bool = False) -> None:
        """Print success message with [✓ SUCCESS] tag.

        Args:
            message: The message to display
            verbose_only: If True, only show when --verbose is enabled

        """
        if verbose_only and not self.verbose:
            return

        timestamp = self._get_timestamp()
        tag = self._format_tag("SUCCESS", self.colors["tag_success"])
        self._print_line(timestamp, tag, message)

    def warning(self, message: str, verbose_only: bool = False) -> None:
        """Print warning message with [⚠ WARN] tag.

        Args:
            message: The message to display
            verbose_only: If True, only show when --verbose is enabled

        """
        if verbose_only and not self.verbose:
            return

        timestamp = self._get_timestamp()
        tag = self._format_tag("WARN", self.colors["tag_warning"])
        self._print_line(timestamp, tag, message)

    def error(self, message: str, verbose_only: bool = False) -> None:
        """Print error message with [✗ ERROR] tag.

        Args:
            message: The message to display
            verbose_only: If True, only show when --verbose is enabled

        """
        if verbose_only and not self.verbose:
            return

        timestamp = self._get_timestamp()
        tag = self._format_tag("ERROR", self.colors["tag_error"])
        self._print_line(timestamp, tag, message)

    def debug(self, message: str) -> None:
        """Print debug message (only when --verbose enabled).

        Args:
            message: The debug message to display

        """
        if not self.verbose:
            return

        timestamp = self._get_timestamp()
        tag = self._format_tag("DEBUG", self.colors["tag_debug"])
        self._print_line(timestamp, tag, message)

    # ============================================================================
    # SECTION AND LAYOUT METHODS
    # ============================================================================

    def section(self, title: str | None = None) -> None:
        """Print a section separator with optional title.

        Args:
            title: Optional title to display in the center of the separator

        """
        if title:
            # Wrap title in brackets (preserve aesthetic preference)
            title_with_brackets = (
                f"[{self.colors['separator']}][[{self.colors['separator']}]"
                f"[{self.colors['separator_text']}]{title}[/{self.colors['separator_text']}]"
                f"[{self.colors['separator']}]][/{self.colors['separator']}]"
            )
            separator = Rule(
                title=title_with_brackets,
                style=self.colors["separator"],
                characters="─",
            )
        else:
            separator = Rule(style=self.colors["separator"], characters="─")

        self.console.print(separator)

    def spacer(self, lines: int = 1) -> None:
        """Print empty lines for spacing.

        Args:
            lines: Number of empty lines to print (default: 1)

        """
        for _ in range(lines):
            self.console.print()

    # ============================================================================
    # ADVANCED FEATURES
    # ============================================================================

    def tag(self, content: str, color: str | None = None) -> None:
        """Create a custom tag with square brackets.

        Args:
            content: The content to put in the tag
            color: Color for the tag content (default: uses theme default)

        """
        if color is None:
            color = self.colors["tag_info"]

        timestamp = self._get_timestamp()
        tag = self._format_tag(content, color)
        self.console.print(f"{timestamp}{tag}")

    def step(self, message: str) -> None:
        """Print a numbered step (for debugging processes).

        Args:
            message: The step message

        """
        if not self.verbose:
            return

        self._step_counter += 1
        step_num = f"{self._step_counter:03d}"

        timestamp = self._get_timestamp()
        tag = self._format_tag(f"STEP {step_num}", "cyan")
        self._print_line(timestamp, tag, message)

    def trace(self, message: str) -> None:
        """Print execution trace (only in debug mode).

        Args:
            message: The trace message

        """
        if not self.verbose:
            return

        timestamp = self._get_timestamp()
        self.console.print(f"{timestamp}[dim]→ {message}[/dim]")

    # ============================================================================
    # DEBUGGING HELPERS
    # ============================================================================

    def trace_function_entry(
        self,
        func_name: str,
        args: dict[str, Any] | None = None,
    ) -> None:
        """Trace function entry with parameters.

        Args:
            func_name: Name of the function
            args: Dictionary of function arguments

        """
        if not self.verbose:
            return

        msg = f"→ Entering {func_name}"
        if args:
            args_str = ", ".join(f"{k}={v}" for k, v in args.items())
            msg += f" with args: {args_str}"

        self.debug(msg)

    def trace_function_exit(
        self,
        func_name: str,
        result: Any | None = None,
    ) -> None:
        """Trace function exit with result.

        Args:
            func_name: Name of the function
            result: Function return value (optional)

        """
        if not self.verbose:
            return

        msg = f"← Exiting {func_name}"
        if result:
            msg += f" -> {result}"

        self.debug(msg)

    @contextmanager
    def timer(self, operation: str) -> Generator[None, None, None]:
        """Time an operation (shows duration in verbose mode).

        Args:
            operation: Name of the operation being timed

        Example:
            with output.timer("Host deployment"):
                deploy_to_host(hostname)

        """
        if not self.verbose:
            yield
            return

        start = time.time()
        self.debug(f"⏱ Starting {operation}")

        try:
            yield
            duration = time.time() - start
            self.debug(f"✓ {operation} complete ({duration:.3f}s)")
        except Exception as e:
            duration = time.time() - start
            self.debug(f"✗ {operation} failed after {duration:.3f}s: {e}")
            raise

    def print_header(self, text: str, border_style: str | None = None) -> None:
        """Print a header with a bordered panel.

        Args:
            text: Header text
            border_style: Border color (default: uses theme border color)

        """
        if border_style is None:
            border_style = self.colors["separator"]

        panel = Panel(
            f"[bold]{text}[/bold]",
            border_style=border_style,
            padding=(1, 2),
        )
        self.console.print(panel)

    # ============================================================================
    # INTERNAL METHODS
    # ============================================================================

    def _get_timestamp(self) -> str:
        """Get formatted timestamp string.

        Returns:
            Formatted timestamp with brackets, or empty string if timestamps disabled

        """
        if not self.timestamps:
            return ""

        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp_color = self.colors["timestamp"]
        return (
            f"[{timestamp_color}][[/{timestamp_color}]"
            f"[{timestamp_color}]{timestamp_str}[/{timestamp_color}]"
            f"[{timestamp_color}]][/{timestamp_color}] "
        )

    def _format_tag(self, tag_content: str, color: str) -> str:
        """Format tag with square brackets.

        Args:
            tag_content: Content for the tag (e.g., "INFO", "SUCCESS")
            color: Color for the tag

        Returns:
            Formatted tag string with square brackets

        """
        bracket_color = self.colors["tag_brackets"]
        return (
            f"[{bracket_color}][[/{bracket_color}]"
            f"[bold {color}]{tag_content}[/bold {color}]"
            f"[{bracket_color}]][/{bracket_color}]"
        )

    def _print_line(
        self,
        timestamp: str,
        tag: str,
        message: str,
    ) -> None:
        """Print a formatted line with timestamp, tag, and message.

        Args:
            timestamp: Formatted timestamp string
            tag: Formatted tag string
            message: The message content

        """
        text_color = self.colors["text"]
        self.console.print(f"{timestamp}{tag} [{text_color}]{message}[/{text_color}]")

    def _load_theme_colors(self) -> dict[str, str]:
        """Load theme colors with fallbacks.

        Returns:
            Dictionary mapping color names to color values

        """
        config = RichHelpConfiguration(
            theme=self.theme,
            enable_theme_env_var=True,
        )

        return {
            # Tags
            "tag_info": str(config.style_option or "cyan"),
            "tag_success": "green",
            "tag_warning": "yellow",
            "tag_error": "red",
            "tag_debug": "dim",
            # Brackets (for square brackets around tags)
            "tag_brackets": str(
                config.style_footer_text or config.style_epilog_text or "dim"
            ),
            # Text
            "text": str(config.style_helptext or "default"),
            "text_dim": "dim",
            # Timestamps
            "timestamp": str(config.style_option or "cyan"),
            # Separators
            "separator": str(
                config.style_options_panel_border
                or config.style_commands_panel_border
                or "dim"
            ),
            "separator_text": str(config.style_helptext_first_line or "default"),
        }


# ============================================================================
# FACTORY FUNCTION
# ============================================================================


def get_output_manager(
    ctx: click.Context,
) -> OutputManager:
    """Create OutputManager from Click context.

    Args:
        ctx: Click context object containing settings

    Returns:
        Configured OutputManager instance

    Raises:
        KeyError: If required settings not in context

    Example:
        output = get_output_manager(ctx)
        output.info("Message")

    """
    theme = ctx.obj.get("theme", "dracula")
    verbose = ctx.obj.get("verbose", False)
    timestamps = ctx.obj.get("timestamp", True)

    return OutputManager(
        ctx=ctx,
        theme=theme,
        verbose=verbose,
        timestamps=timestamps,
    )


# ============================================================================
# ERROR PANEL HELPER
# ============================================================================


def create_error_panel(
    message: str | Text, title: str = "Error", theme: str | None = None
) -> Panel:
    """Create a consistent error panel with standard styling.

    Args:
        message: Error message as string or rich Text object
        title: Panel title (default: "Error")
        theme: Theme name to get error border color (default: dracula)

    Returns:
        Panel widget with consistent error styling (theme-specific red border,
        left-aligned title)

    Example:
        panel = create_error_panel("Something went wrong", theme="nord")
        console.print(panel)

        # With rich Text for colors
        from rich.text import Text
        msg = Text("Error message with ")
        msg.append("colored text", style="bold yellow")
        panel = create_error_panel(msg, theme="dracula")

    """
    # Use default theme if not specified
    if theme is None:
        theme = "dracula"

    # Get the theme's error border color
    # Handle invalid themes by falling back to dracula
    try:
        config = RichHelpConfiguration(theme=theme, enable_theme_env_var=True)
        error_border_color = str(config.style_errors_panel_border or "red")
    except Exception:
        # Invalid theme - fall back to dracula's error color
        config = RichHelpConfiguration(theme="dracula", enable_theme_env_var=True)
        error_border_color = str(config.style_errors_panel_border or "red")

    return Panel(
        message,
        title=title,
        border_style=error_border_color,
        padding=(0, 1),
        title_align="left",
    )
