"""
Utility functions for text display and formatting.
"""
import textwrap


def format_with_margin(text: str, margin: str = "  ", max_width: int = 85) -> str:
    """
    Format text with left margin and word wrapping.

    Args:
        text: Text to format
        margin: Left margin string (default: 2 spaces)
        max_width: Maximum line width including margin

    Returns:
        Formatted text with margins and wrapping
    """
    # Calculate available width after margin
    available_width = max_width - len(margin)

    # Split by existing newlines first
    paragraphs = text.split('\n')
    result = []

    for paragraph in paragraphs:
        if not paragraph.strip():
            result.append(margin)  # Empty line
            continue

        # Word wrap the paragraph
        wrapped = textwrap.fill(
            paragraph,
            width=available_width,
            initial_indent='',
            subsequent_indent='',
            break_long_words=False,
            break_on_hyphens=False
        )

        # Add margin to each line
        for line in wrapped.split('\n'):
            result.append(margin + line)

    return '\n'.join(result)


def safe_print(text: str, margin: str = "  "):
    """
    Print with left margin (for game text that bypasses curses).

    Use this instead of print() for game messages to ensure
    consistent formatting across all terminal sizes.
    """
    formatted = format_with_margin(text, margin, max_width=85)
    print(formatted)
