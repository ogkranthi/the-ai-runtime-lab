"""Terminal presentation helpers: boxed tables and banners, no dependencies.

Pure stdlib so the workshop output looks good with nothing installed. Color is
ANSI and turns itself off when stdout is not a terminal, so piping to a file or
another program stays clean.

A cell is either a string, or a (text, color) tuple to color that one cell. The
table pads on the visible text, then wraps color around it, so alignment holds.
"""
from __future__ import annotations

import sys
from typing import List, Optional, Sequence, Tuple, Union

Cell = Union[str, Tuple[str, str]]

# ANSI codes
RESET = "\033[0m"
BOLD = "1"
DIM = "2"
RED = "31"
GREEN = "32"
YELLOW = "33"
CYAN = "36"


def color_on() -> bool:
    return sys.stdout.isatty()


def style(text: str, *codes: str) -> str:
    if not codes or not color_on():
        return text
    return f"\033[{';'.join(codes)}m{text}{RESET}"


def _text(cell: Cell) -> str:
    return cell[0] if isinstance(cell, tuple) else cell


def _truncate(text: str, cap: int) -> str:
    if cap and len(text) > cap:
        return text[: cap - 1] + "…"
    return text


def _render_cell(cell: Cell, width: int) -> str:
    text = _truncate(_text(cell), width)
    padded = text.ljust(width)
    if isinstance(cell, tuple):
        return style(padded, cell[1])
    return padded


def table(headers: Sequence[str], rows: Sequence[Sequence[Cell]],
          caps: Optional[Sequence[int]] = None) -> str:
    """Render a boxed table. `caps` optionally caps each column's width."""
    cols = len(headers)
    caps = list(caps) if caps else [60] * cols
    widths = [len(h) for h in headers]
    for row in rows:
        for i in range(cols):
            widths[i] = max(widths[i], len(_truncate(_text(row[i]), caps[i])))
    widths = [min(widths[i], caps[i]) for i in range(cols)]

    def line(left: str, mid: str, right: str) -> str:
        return left + mid.join("─" * (widths[i] + 2) for i in range(cols)) + right

    out = [line("┌", "┬", "┐")]
    head = "│ " + " │ ".join(
        style(headers[i].ljust(widths[i]), BOLD) for i in range(cols)
    ) + " │"
    out.append(head)
    out.append(line("├", "┼", "┤"))
    for row in rows:
        cells = " │ ".join(_render_cell(row[i], widths[i]) for i in range(cols))
        out.append("│ " + cells + " │")
    out.append(line("└", "┴", "┘"))
    return "\n".join(out)


def banner(text: str, color: str = GREEN) -> str:
    """A single-line rounded banner, centered text, colored border."""
    inner = f"  {text}  "
    width = len(inner)
    top = "╭" + "─" * width + "╮"
    mid = "│" + inner + "│"
    bot = "╰" + "─" * width + "╯"
    return "\n".join(style(s, color) for s in (top, mid, bot))


def rule(text: str, color: str = CYAN) -> str:
    bar = "━" * 3
    return style(f"{bar} {text} {bar}", BOLD, color)
