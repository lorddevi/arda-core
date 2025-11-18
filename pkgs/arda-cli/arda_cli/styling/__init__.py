"""Styling utilities for Arda CLI

This module provides styling helpers including gradients and prefix utilities.
"""

from .gradients import (
    gradient_text,
    multi_color_gradient,
    gradient_bar,
    gradient_horizontal_line,
    gradient_vertical_lines,
)

from .prefixes import (
    with_host_prefix,
    with_timestamp,
    with_full_context,
    with_network_prefix,
    get_host_color,
)

__all__ = [
    # Gradients
    "gradient_text",
    "multi_color_gradient",
    "gradient_bar",
    "gradient_horizontal_line",
    "gradient_vertical_lines",
    # Prefixes
    "with_host_prefix",
    "with_timestamp",
    "with_full_context",
    "with_network_prefix",
    "get_host_color",
]
