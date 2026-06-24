"""Output helpers — ANSI color that respects NO_COLOR and non-TTY output."""

import os
import sys

_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def set_color(enabled: bool) -> None:
    """Force color on or off (overrides auto-detection)."""
    global _COLOR
    _COLOR = enabled


def paint(text: str, code: str) -> str:
    """Wrap text in an ANSI color code, or return it plain when color is off."""
    return f"\033[{code}m{text}\033[0m" if _COLOR else text
