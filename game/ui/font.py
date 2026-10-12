"""The game's reading font.

Layout is the same as before (decisions/0018, 0036): monospace, 8 layout
pixels per character, 17 per line. How it's drawn depends on the screen:

- Crisp text (decisions/0038, config.DISPLAY_SCALE = 2): M PLUS 1 Code, a
  smooth font from the same M+ family as PixelMplus, drawn at full size on
  the doubled screen (game/gfx/display.py), 16 screen pixels per character.
  assets/fonts/LICENSE-MPLUS1Code.txt; the file is cut down to Latin letters.
- Otherwise: DotGothic16, a pixel font, at 15 px on the 384 x 288 screen
  (assets/fonts/LICENSE-DotGothic16.txt).
"""

import pyxel

from game import config
from game.gfx import display

from .text import BIG_CHAR_W

FONT_PATH = config.ROOT / "assets" / "fonts" / "DotGothic16-Regular.ttf"
FONT_SIZE = 15
# DotGothic16 leaves 4 empty rows above its capitals; shift it up so (x, y)
# is the top-left of the text, as with the old font
TEXT_DY = -4

# crisp text: 32 px makes each character exactly 16 px wide, the same 8
# layout pixels as DotGothic16, so every box and menu keeps its layout
CRISP_PATH = config.ROOT / "assets" / "fonts" / "MPLUS1Code-Medium.ttf"
CRISP_SIZE = 32
CRISP_DY = -8            # capitals start where DotGothic16's did; descenders stay in the line

_font: pyxel.Font | None = None
_crisp: dict[int, pyxel.Font] = {}


def font() -> pyxel.Font:
    global _font
    if _font is None:
        _font = pyxel.Font(str(FONT_PATH), FONT_SIZE)
    return _font


def crisp(size: int = 1) -> pyxel.Font:
    """The crisp font, `size` times the usual size."""
    if size not in _crisp:
        _crisp[size] = pyxel.Font(str(CRISP_PATH), CRISP_SIZE * size)
    return _crisp[size]


def text(x: float, y: float, s: str, col: int, size: int = 1) -> None:
    """Draw `s` in the reading font. (x, y) is the top-left of the text.
    `size` 2 draws it twice as big (titles; crisp text only)."""
    cell = BIG_CHAR_W * display.scale * size
    if display.queue_text(x, y, s, col, crisp(size) if display.active else None, cell,
                          CRISP_DY * size):
        return
    pyxel.text(x, y + TEXT_DY, s, col, font())


def width(s: str) -> int:
    return len(s) * BIG_CHAR_W


def centered(y: float, s: str, col: int, cx: float = config.SCREEN_W / 2) -> None:
    text(cx - width(s) / 2, y, s, col)
