"""Gradient utilities for Arda CLI

This module provides gradient text rendering capabilities using Rich's Text objects.
Gradients are created by applying different colors to individual characters.
"""

from rich.text import Text
from typing import List, Tuple


def gradient_text(text: str, start_color: str, end_color: str) -> Text:
    """Create text with gradient color effect

    Args:
        text: Text to apply gradient to
        start_color: Color for the start of the text
        end_color: Color for the end of the text

    Returns:
        Text object with gradient styling applied

    Example:
        >>> from rich.console import Console
        >>> console = Console()
        >>> gradient = gradient_text("GRADIENT", "red", "blue")
        >>> console.print(gradient)
    """
    result = Text()
    result.append(text)

    # Apply gradient by styling character ranges
    length = len(text)
    if length <= 1:
        result.stylize(start_color, 0, length)
    else:
        # Apply start color to first 1/3
        result.stylize(start_color, 0, max(1, length // 3))
        # Apply middle color to middle 1/3 (if length > 2)
        if length > 2:
            middle_color = start_color
            result.stylize(middle_color, length // 3, (length * 2) // 3)
        # Apply end color to last 1/3
        result.stylize(end_color, (length * 2) // 3, length)

    return result


def multi_color_gradient(text: str, *colors: str) -> Text:
    """Create text with multiple color gradient

    Args:
        text: Text to apply gradient to
        *colors: Variable number of colors to transition through

    Returns:
        Text object with multi-color gradient

    Example:
        >>> gradient = multi_color_gradient("RAINBOW", "red", "green", "blue")
        >>> console.print(gradient)
    """
    if not colors:
        return Text(text)

    result = Text()
    length = len(text)
    num_colors = len(colors)

    if num_colors == 1:
        result.append(text, style=colors[0])
    else:
        # Distribute characters across colors
        for i, char in enumerate(text):
            # Calculate which color this character should be
            color_index = int(i * num_colors / length)
            if color_index >= num_colors:
                color_index = num_colors - 1
            result.append(char, style=colors[color_index])

    return result


def gradient_bar(length: int, start_color: str = "dim cyan", end_color: str = "cyan") -> Text:
    """Create a horizontal gradient bar using block characters

    Args:
        length: Length of the bar in characters
        start_color: Color for the left side of the bar
        end_color: Color for the right side of the bar

    Returns:
        Text object containing the gradient bar

    Example:
        >>> bar = gradient_bar(40, "green", "bright_green")
        >>> console.print(bar)
    """
    result = Text()

    for i in range(length):
        # Determine color for this position
        if i < length * 0.3:
            color = start_color
        elif i > length * 0.7:
            color = end_color
        else:
            color = end_color

        result.append("█", style=color)

    return result


def gradient_horizontal_line(length: int, color: str = "cyan") -> Text:
    """Create a horizontal line with optional gradient effect

    Args:
        length: Length of the line
        color: Color of the line (defaults to cyan)

    Returns:
        Text object containing the horizontal line

    Example:
        >>> line = gradient_horizontal_line(60, "green")
        >>> console.print(line)
    """
    result = Text()
    result.append("─" * length, style=color)
    return result


def gradient_vertical_lines(height: int, start_color: str, end_color: str) -> List[Text]:
    """Create multiple vertical gradient lines

    Args:
        height: Number of lines to create
        start_color: Color for the top line
        end_color: Color for the bottom line

    Returns:
        List of Text objects, each representing a vertical line

    Example:
        >>> lines = gradient_vertical_lines(5, "dim green", "bright_green")
        >>> for line in lines:
        ...     console.print(line)
    """
    lines = []
    for i in range(height):
        # Interpolate color based on position
        if i < height * 0.5:
            color = start_color
        else:
            color = end_color

        lines.append(Text("█", style=color))

    return lines
