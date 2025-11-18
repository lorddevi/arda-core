"""Prefix utilities for Arda CLI

This module provides utilities for adding hostname and timestamp prefixes to output.
Used to provide context for operations targeting specific hosts.
"""

import datetime
from rich.text import Text
from typing import Optional, Dict


def with_host_prefix(hostname: str, message: str, theme_colors: Dict[str, str]) -> Text:
    """Add hostname prefix to a message

    Args:
        hostname: Name of the host
        message: Message to prefix
        theme_colors: Dictionary of theme colors

    Returns:
        Text object with hostname prefix

    Example:
        >>> text = with_host_prefix("nixos-01", "Installing packages...", colors)
        >>> console.print(text)
        [nixos-01]: Installing packages...
    """
    text = Text()

    # Add opening bracket
    text.append("[", style=theme_colors.get("hostname_brackets", "dim white"))

    # Add hostname
    text.append(hostname, style=theme_colors.get("hostname_name", "white"))

    # Add closing bracket and colon
    text.append("]: ", style=theme_colors.get("hostname_colon", "dim white"))

    # Add message
    text.append(message, style=theme_colors.get("output", "white"))

    return text


def with_timestamp(message: str, theme_colors: Dict[str, str], format_str: str = "%H:%M:%S") -> Text:
    """Add timestamp prefix to a message

    Args:
        message: Message to prefix
        theme_colors: Dictionary of theme colors
        format_str: Timestamp format string (default: "%H:%M:%S")

    Returns:
        Text object with timestamp prefix

    Example:
        >>> text = with_timestamp("Starting installation", colors)
        >>> console.print(text)
        [14:23:45] Starting installation
    """
    text = Text()

    # Get current timestamp
    timestamp = datetime.datetime.now().strftime(format_str)

    # Add opening bracket and timestamp
    text.append(f"[{timestamp}]", style=theme_colors.get("timestamp", "dim white"))

    # Add space separator
    text.append(" ", style="none")

    # Add message
    text.append(message, style=theme_colors.get("output", "white"))

    return text


def with_full_context(
    hostname: str,
    message: str,
    theme_colors: Dict[str, str],
    timestamp: bool = False,
    format_str: str = "%H:%M:%S"
) -> Text:
    """Add hostname and optional timestamp prefix to a message

    Args:
        hostname: Name of the host
        message: Message to prefix
        theme_colors: Dictionary of theme colors
        timestamp: Whether to include timestamp
        format_str: Timestamp format string

    Returns:
        Text object with full context prefix

    Example:
        >>> text = with_full_context("nixos-01", "Installing...", colors, timestamp=True)
        >>> console.print(text)
        [14:23:45] [nixos-01]: Installing...
    """
    text = Text()

    # Add timestamp if enabled
    if timestamp:
        timestamp_str = datetime.datetime.now().strftime(format_str)
        text.append(f"[{timestamp_str}]", style=theme_colors.get("timestamp", "dim white"))
        text.append(" ", style="none")

    # Add hostname prefix
    text.append("[", style=theme_colors.get("hostname_brackets", "dim white"))
    text.append(hostname, style=theme_colors.get("hostname_name", "white"))
    text.append("]: ", style=theme_colors.get("hostname_colon", "dim white"))

    # Add message
    text.append(message, style=theme_colors.get("output", "white"))

    return text


def with_network_prefix(network: str, hostname: str, message: str, theme_colors: Dict[str, str]) -> Text:
    """Add network and hostname prefix to a message

    Args:
        network: Network name (e.g., "prod", "staging", "dev")
        hostname: Name of the host
        message: Message to prefix
        theme_colors: Dictionary of theme colors

    Returns:
        Text object with network and hostname prefix

    Example:
        >>> text = with_network_prefix("prod", "web-01", "Rebooting...", colors)
        >>> console.print(text)
        [PROD] [web-01]: Rebooting...
    """
    text = Text()

    # Add network in brackets
    text.append("[", style="bold")
    text.append(network.upper(), style=theme_colors.get("network_prod", "bold red"))
    text.append("] ", style="none")

    # Add hostname prefix
    text.append("[", style=theme_colors.get("hostname_brackets", "dim white"))
    text.append(hostname, style=theme_colors.get("hostname_name", "white"))
    text.append("]: ", style=theme_colors.get("hostname_colon", "dim white"))

    # Add message
    text.append(message, style=theme_colors.get("output", "white"))

    return text


def get_host_color(hostname: str, theme_colors: Dict[str, str]) -> str:
    """Get a color for a specific hostname

    Args:
        hostname: Name of the host
        theme_colors: Dictionary of theme colors

    Returns:
        Color string to use for this host

    Example:
        >>> color = get_host_color("web-01", colors)
        >>> # Returns "cyan" for first host, "green" for second, etc.
    """
    # Simple hash-based color selection
    # This ensures same hostname always gets same color
    color_palette = [
        "cyan",
        "green",
        "yellow",
        "magenta",
        "blue",
        "bright_green",
        "bright_yellow",
        "bright_magenta",
    ]

    # Simple hash function
    hash_val = sum(ord(c) for c in hostname)
    color_index = hash_val % len(color_palette)

    return color_palette[color_index]
