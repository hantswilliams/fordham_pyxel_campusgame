"""Building card: what a building or landmark is and what's inside.
Shown when the player faces a door, landmark or shuttle sign and presses Z.
Interiors are deferred (decisions/0012), so this is how buildings are explored.
Text uses the big reading font (decisions/0018). Buildings with a drawn
picture (assets/buildings/<id>/card.png, decisions/0020) show it at the top
of the card; it scrolls away with the text."""

import pyxel

from game.gfx import display

from game.config import SCREEN_H, SCREEN_W, Art, Col
from game.gfx.building_art import card_fine_image, card_image
from game.systems import controls
from game.systems.input import Action
from game.ui import font, frames
from game.ui.text import BIG_CHAR_W, BIG_LINE_H, GROW, wrap
from game.world.locations import Location

from .base import Scene

CARD_X, CARD_Y = 6, 6
CARD_W, CARD_H = SCREEN_W - 12, SCREEN_H - 12
PAD = 8
MAX_CHARS = (CARD_W - 2 * PAD) // BIG_CHAR_W
HEADER_H = 18 + GROW
BODY_TOP = HEADER_H + 22
FOOTER_H = 16 + GROW
VISIBLE_LINES = (CARD_H - BODY_TOP - FOOTER_H) // BIG_LINE_H
# with a picture, the kind tag sits on the picture and the body starts higher
PIC_W, PIC_H = 228, 88  # card.png size; centred on a wider card
PIC_BODY_TOP = HEADER_H + 4
PIC_VISIBLE_LINES = (CARD_H - PIC_BODY_TOP - FOOTER_H) // BIG_LINE_H
PIC_LINES = -(-(PIC_H + 4) // BIG_LINE_H)  # text lines the picture takes up

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
    if loc.real_entrance:
        # every door faces south in the game; say where it really is (D-0021)
        lines.append(("", Col.BLACK))
        lines.append(("IN REAL LIFE", Col.MAROON))
        lines += [(s, Col.BLACK) for s in wrap(loc.real_entrance, MAX_CHARS)]
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
        building = getattr(app, "buildings", {}).get(location.id)
        self.picture = card_image(building) if building else None
        # on the full-size screen, the picture at twice the detail (decisions/0045)
        self.fine = card_fine_image(building) if building and display.active else None

    @property
    def body_top(self) -> int:
        return PIC_BODY_TOP if self.picture else BODY_TOP

    @property
    def visible_lines(self) -> int:
        return PIC_VISIBLE_LINES if self.picture else VISIBLE_LINES

    @property
    def total_lines(self) -> int:
        return len(self.lines) + (PIC_LINES if self.picture else 0)

    @property
    def max_scroll(self) -> int:
        return max(0, self.total_lines - self.visible_lines)

    def update(self) -> None:
        if self.input.pressed(Action.DOWN):
            self.scroll = min(self.max_scroll, self.scroll + 1)
        if self.input.pressed(Action.UP):
            self.scroll = max(0, self.scroll - 1)
        if self.input.pressed(Action.CONFIRM) or self.input.pressed(Action.CANCEL):
            self.app.scenes.pop()

    def draw(self) -> None:
        frames.dim()                                # the world behind, dimmed
        x, y, w, h = CARD_X, CARD_Y, CARD_W, CARD_H
        frames.box(x, y, w, h, radius=8)
        frames.header(x + 2.5, y + 2.5, w - 5, HEADER_H - 1)
        font.text(x + PAD, y + 4, self.loc.name.upper()[:MAX_CHARS], Col.WHITE)

        top = y + self.body_top
        if not self.picture:
            self._draw_tag(x + PAD, y + HEADER_H + 4)
        display.clip(x + 2, top, w - 4, self.visible_lines * BIG_LINE_H)
        first = 0
        if self.picture:
            py = top + 1 - self.scroll * BIG_LINE_H
            px = x + (w - PIC_W) // 2
            self._draw_picture(px, py, (x + 2, top, w - 4, self.visible_lines * BIG_LINE_H))
            self._draw_tag(px + 4, py + PIC_H - 19 - GROW)  # on the lawn, not the building
            first = PIC_LINES
        for i, (s, col) in enumerate(self.lines):
            row = first + i - self.scroll
            if 0 <= row < self.visible_lines:
                font.text(x + PAD, top + row * BIG_LINE_H, s, col)
        display.clip()

        # footer: scroll arrows + close hint
        fy = y + h - FOOTER_H + 1
        frames.rect(x + 6, fy - 2, w - 12, 0.5, Art.UI_LINE)
        if self.scroll > 0:
            frames.arrow(x + PAD, fy + 4, down=False)
        if self.scroll < self.max_scroll:
            frames.arrow(x + PAD + 12, fy + 4)
        footer = controls.fmt("{confirm}: CLOSE")
        font.text(x + w - PAD - font.width(footer), fy, footer, Col.DARK_BLUE)

    def _draw_tag(self, tx: int, ty: int) -> None:
        label = self.loc.kind_label
        tag_col = KIND_COLORS.get(self.loc.kind, Col.GRAY)
        frames.pill(tx, ty, font.width(label) + 12, 15 + GROW, tag_col, radius=4)
        font.text(tx + 6, ty + 1, label, Col.WHITE)

    def _draw_picture(self, px: int, py: int, clip) -> None:
        fine = self.fine
        if fine is not None and frames.picture(fine, fine.width, fine.height, px, py, clip):
            return
        img = self.picture
        pyxel.blt(px, py, img, 0, 0, min(img.width, PIC_W), min(img.height, PIC_H))
        pyxel.rectb(px - 1, py - 1, PIC_W + 2, PIC_H + 2, Col.NAVY)
