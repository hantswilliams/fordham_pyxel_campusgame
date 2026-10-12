"""The game's reading font (decisions/0018, 0036): DotGothic16, a free pixel
font (assets/fonts/LICENSE-DotGothic16.txt), drawn at 15 px where it renders
crisply. Sized for the 384 x 288 screen; PixelMplus 12 was used at 256 x 192.
Larger and crisper than Pyxel's built-in 4x6 font, for Pokemon-style
readable text boxes."""

import pyxel

from game import config

from .text import BIG_CHAR_W

FONT_PATH = config.ROOT / "assets" / "fonts" / "DotGothic16-Regular.ttf"
FONT_SIZE = 15
# DotGothic16 leaves 4 empty rows above its capitals; shift it up so (x, y)
# is the top-left of the text, as with the old font
TEXT_DY = -4

_font: pyxel.Font | None = None


def font() -> pyxel.Font:
    global _font
    if _font is None:
        _font = pyxel.Font(str(FONT_PATH), FONT_SIZE)
    return _font


def text(x: float, y: float, s: str, col: int) -> None:
    """Draw `s` in the reading font. (x, y) is the top-left of the text."""
    pyxel.text(x, y + TEXT_DY, s, col, font())


def width(s: str) -> int:
    return len(s) * BIG_CHAR_W


def centered(y: float, s: str, col: int, cx: float = config.SCREEN_W / 2) -> None:
    text(cx - width(s) / 2, y, s, col)
