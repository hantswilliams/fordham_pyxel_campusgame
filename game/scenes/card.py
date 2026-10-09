"""Building card: what a building or landmark is and what's inside.
Shown when the player faces a door, landmark or shuttle sign and presses Z.
Interiors are deferred (decisions/0012), so this is how buildings are explored."""

import pyxel

from game.config import SCREEN_H, SCREEN_W, Col
from game.systems.input import Action
from game.ui.text import CHAR_W, LINE_H, wrap
from game.world.locations import Location

from .base import Scene

CARD_X, CARD_Y = 16, 18
CARD_W, CARD_H = SCREEN_W - 32, SCREEN_H - 36
PAD = 8
MAX_CHARS = (CARD_W - 2 * PAD) // CHAR_W
ROW_H = LINE_H + 1

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
    lines += [(s, Col.NAVY) for s in wrap(loc.blurb, MAX_CHARS)]
    if loc.inside:
        lines.append(("", Col.NAVY))
        lines.append(("WHAT'S HERE", Col.MAROON))
        for item in loc.inside:
            for i, s in enumerate(wrap(item, MAX_CHARS - 2)):
                lines.append((("- " if i == 0 else "  ") + s, Col.NAVY))
    if loc.url:
        lines.append(("", Col.NAVY))
        for s in wrap("MORE: " + loc.url, MAX_CHARS):
            lines.append((s, Col.DARK_BLUE))
    return lines


class BuildingCardScene(Scene):
    overlay = True

    def __init__(self, app, location: Location):
        super().__init__(app)
        self.loc = location
        self.lines = card_lines(location)
        self.visible = (CARD_H - 44) // ROW_H
        self.scroll = 0
        self.opened_frame = pyxel.frame_count

    def update(self) -> None:
        max_scroll = max(0, len(self.lines) - self.visible)
        if self.input.pressed(Action.DOWN):
            self.scroll = min(max_scroll, self.scroll + 1)
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
        pyxel.rect(x, y, w, 16, Col.MAROON)
        pyxel.text(x + PAD, y + 5, self.loc.name.upper(), Col.WHITE)

        label = self.loc.kind_label
        tag_col = KIND_COLORS.get(self.loc.kind, Col.GRAY)
        pyxel.rect(x + PAD, y + 20, len(label) * CHAR_W + 6, 9, tag_col)
        pyxel.text(x + PAD + 3, y + 22, label, Col.WHITE)

        top = y + 34
        for i, (s, col) in enumerate(self.lines[self.scroll:self.scroll + self.visible]):
            pyxel.text(x + PAD, top + i * ROW_H, s, col)

        footer = "Z: CLOSE"
        if len(self.lines) > self.visible:
            footer = "UP/DOWN: SCROLL   " + footer
        pyxel.text(x + w - PAD - len(footer) * CHAR_W, y + h - 9, footer, Col.GRAY)
