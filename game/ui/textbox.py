"""The Pokemon-style text box used for dialogue and intro captions
(decisions/0018): big black pixel text on white, double border, 3 lines."""

import pyxel

from game.config import SCREEN_H, SCREEN_W, Col

from . import font
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
    pyxel.rect(x, y, BOX_W, BOX_H, Col.WHITE)
    pyxel.rectb(x, y, BOX_W, BOX_H, Col.NAVY)
    pyxel.rectb(x + 1, y + 1, BOX_W - 2, BOX_H - 2, Col.NAVY)
    pyxel.rectb(x + 3, y + 3, BOX_W - 6, BOX_H - 6, Col.MAROON)

    if speaker:
        tw = font.width(speaker) + 12
        pyxel.rect(x + 8, y - 13 - GROW, tw, 15 + GROW, Col.MAROON)
        pyxel.rectb(x + 8, y - 13 - GROW, tw, 15 + GROW, Col.NAVY)
        font.text(x + 14, y - 12 - GROW, speaker, Col.WHITE)

    remaining = revealed
    for i, line in enumerate(lines[:LINES]):
        font.text(x + PAD_X, y + PAD_Y + i * BIG_LINE_H, line[:max(0, remaining)], TEXT_COLOR)
        remaining -= len(line)

    if complete and (pyxel.frame_count // 8) % 2 == 0:
        ax, ay = x + BOX_W - 16, y + BOX_H - 10
        pyxel.tri(ax, ay, ax + 8, ay, ax + 4, ay + 4, Col.MAROON)
