"""Building card: what a building or landmark is and what's inside.
Shown when the player faces a door, landmark or shuttle sign and presses Z.
Interiors are deferred (decisions/0012), so this is how buildings are explored.
Text uses the big reading font (decisions/0018)."""

import pyxel

from game.config import SCREEN_H, SCREEN_W, Col
from game.systems.input import Action
from game.ui import font
from game.ui.text import BIG_CHAR_W, BIG_LINE_H, wrap
from game.world.locations import Location

from .base import Scene

CARD_X, CARD_Y = 6, 6
CARD_W, CARD_H = SCREEN_W - 12, SCREEN_H - 12
PAD = 8
MAX_CHARS = (CARD_W - 2 * PAD) // BIG_CHAR_W
HEADER_H = 18
BODY_TOP = HEADER_H + 22
FOOTER_H = 16
VISIBLE_LINES = (CARD_H - BODY_TOP - FOOTER_H) // BIG_LINE_H

KIND_COLORS = {
    "academic": Col.DARK_BLUE,
    "residence": Col.ORANGE,
    "campus": Col.GRAY,
    "athletics": Col.GREEN,
    "landmark": Col.BROWN,
    "transit": Col.MAROON,
}


def card_lines(loc: Location) -> list[tuple[str, int]]:
    """Body text as (line, colour) pairs, already wrapped to the card width."""
    lines: list[tuple[str, int]] = []
    lines += [(s, Col.BLACK) for s in wrap(loc.blurb, MAX_CHARS)]
    if loc.inside:
        lines.append(("", Col.BLACK))
        lines.append(("WHAT'S HERE", Col.MAROON))
        for item in loc.inside:
            for i, s in enumerate(wrap(item, MAX_CHARS - 2)):
                lines.append((("- " if i == 0 else "  ") + s, Col.BLACK))
    if loc.url:
        lines.append(("", Col.BLACK))
        for s in wrap("MORE: " + loc.url, MAX_CHARS):
            lines.append((s, Col.DARK_BLUE))
    return lines


class BuildingCardScene(Scene):
    overlay = True

    def __init__(self, app, location: Location):
        super().__init__(app)
        self.loc = location
        self.lines = card_lines(location)
        self.scroll = 0

    @property
    def max_scroll(self) -> int:
        return max(0, len(self.lines) - VISIBLE_LINES)

    def update(self) -> None:
        if self.input.pressed(Action.DOWN):
            self.scroll = min(self.max_scroll, self.scroll + 1)
        if self.input.pressed(Action.UP):
            self.scroll = max(0, self.scroll - 1)
        if self.input.pressed(Action.CONFIRM) or self.input.pressed(Action.CANCEL):
            self.app.scenes.pop()

    def draw(self) -> None:
        # dim the world behind the card
        pyxel.dither(0.5)
        pyxel.rect(0, 0, SCREEN_W, SCREEN_H, Col.NAVY)
        pyxel.dither(1.0)

        x, y, w, h = CARD_X, CARD_Y, CARD_W, CARD_H
        pyxel.rect(x, y, w, h, Col.WHITE)
        pyxel.rectb(x, y, w, h, Col.NAVY)
        pyxel.rectb(x + 1, y + 1, w - 2, h - 2, Col.NAVY)
        pyxel.rect(x + 2, y + 2, w - 4, HEADER_H - 2, Col.MAROON)
        font.text(x + PAD, y + 4, self.loc.name.upper()[:MAX_CHARS], Col.WHITE)

        label = self.loc.kind_label
        tag_col = KIND_COLORS.get(self.loc.kind, Col.GRAY)
        pyxel.rect(x + PAD, y + HEADER_H + 4, font.width(label) + 8, 15, tag_col)
        font.text(x + PAD + 4, y + HEADER_H + 5, label, Col.WHITE)

        top = y + BODY_TOP
        for i, (s, col) in enumerate(self.lines[self.scroll:self.scroll + VISIBLE_LINES]):
            font.text(x + PAD, top + i * BIG_LINE_H, s, col)

        # footer: scroll arrows + close hint
        fy = y + h - FOOTER_H + 1
        pyxel.line(x + 4, fy - 2, x + w - 5, fy - 2, Col.GRAY)
        if self.scroll > 0:
            pyxel.tri(x + PAD, fy + 9, x + PAD + 8, fy + 9, x + PAD + 4, fy + 4, Col.MAROON)
        if self.scroll < self.max_scroll:
            pyxel.tri(x + PAD + 12, fy + 4, x + PAD + 20, fy + 4, x + PAD + 16, fy + 9, Col.MAROON)
        footer = "Z: CLOSE"
        font.text(x + w - PAD - font.width(footer), fy, footer, Col.DARK_BLUE)
