"""The Pokemon-style text box used for dialogue and intro captions
(decisions/0018): big black text on white, 3 lines, in a rounded box with
a maroon name tab (decisions/0045)."""

import pyxel

from game.config import SCREEN_H, SCREEN_W, Art, Col

from . import font, frames
from .text import BIG_CHAR_W, BIG_LINE_H, GROW

MARGIN = 4
PAD_X = 10
PAD_Y = 8
LINES = 3
BOX_H = LINES * BIG_LINE_H + 2 * PAD_Y
BOX_W = SCREEN_W - 2 * MARGIN
MAX_CHARS = (BOX_W - 2 * PAD_X) // BIG_CHAR_W
TEXT_COLOR = Col.BLACK


def box_top() -> int:
    return SCREEN_H - BOX_H - MARGIN


def draw_text_box(lines: list[str], revealed: int, complete: bool,
                  speaker: str = "") -> None:
    x, y = MARGIN, box_top()
    frames.box(x, y, BOX_W, BOX_H)              # rounded, with a soft drop (decisions/0045)
    if speaker:
        tw = font.width(speaker) + 16
        frames.pill(x + 8, y - 13 - GROW, tw, 17 + GROW, Col.MAROON, shine=Art.MAROON_LT)
        font.text(x + 16, y - 12 - GROW, speaker, Col.WHITE)

    remaining = revealed
    for i, line in enumerate(lines[:LINES]):
        font.text(x + PAD_X, y + PAD_Y + i * BIG_LINE_H, line[:max(0, remaining)], TEXT_COLOR)
        remaining -= len(line)

    if complete and (pyxel.frame_count // 8) % 2 == 0:
        frames.arrow(x + BOX_W - 18, y + BOX_H - 11)
