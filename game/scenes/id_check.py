"""ID check at a campus gate: choose your Fordham ID card or your phone
(Apple Wallet / Google Wallet), tap it on the reader, get the green light."""

import pyxel

from game.config import SCREEN_W, Art, Col
from game.systems.id_check import CARD, CHOICES, IdCheck
from game.systems import controls
from game.systems.input import Action
from game.ui import font, frames
from game.ui.text import GROW, TEXT_H

from .base import Scene

PANEL_X, PANEL_Y = 16, 14
PANEL_W, PANEL_H = SCREEN_W - 32, 112 + 4 * GROW + 8
READER_X, READER_Y = PANEL_X + PANEL_W - 54, PANEL_Y + 30


def _letter(u, x: float, y: float, text: str, col: int, cell: float) -> None:
    """Words at full detail, on a pen from frames.art (in its units)."""
    font.letter(u.img, u.ox + x * 2, u.oy + y * 2, text, col, cell * 2)


def _card(u) -> None:
    """A Fordham ID card, 44 x 28, at full detail."""
    u.rrect(0, 0, 44, 28, 2.5, Art.OUTLINE)
    u.rrect(0.5, 0.5, 43.5, 27.5, 2, Art.SIGN_BD)
    u.rect(0.5, 2, 43.5, 8.5, Col.MAROON)
    u.rrect(0.5, 0.5, 43.5, 6, 2, Col.MAROON)
    _letter(u, 4, 2.4, "FORDHAM", Col.WHITE, 4)
    u.rect(4, 11, 14, 24, Art.SHIRT_B)                  # the photo
    u.oval(6, 12.5, 12, 19, Art.SKIN1)
    u.oval(5.5, 11.5, 12.5, 15.5, Art.HAIR_BR)
    u.rrect(5, 19.5, 13, 24, 1.5, Col.MAROON)
    for y, w in ((13, 22), (17, 17), (21, 20)):          # name, school, number
        u.rect(17, y, 17 + w, y + 1.5, Art.UI_LINE if w == 17 else Col.STONE_SH)


def _phone(u) -> None:
    """A phone showing the ID in its wallet, 24 x 40, at full detail."""
    u.rrect(0, 0, 24, 40, 3.5, Art.IRON)
    u.rrect(1.5, 3, 22.5, 36, 1, Art.PANE_HI)
    u.rect(9, 1.2, 15, 2, Art.IRON_HI)
    u.rrect(3, 10, 21, 22, 1.5, Col.MAROON)             # the card in the wallet app
    u.oval(4.5, 12, 9.5, 17.5, Art.SKIN1)
    u.oval(4.2, 11.5, 9.8, 14.5, Art.HAIR_BR)
    u.rect(11, 13, 19, 14, Col.WHITE)
    u.rect(11, 16, 17, 17, Art.PANE_HI)
    u.rect(4, 25, 20, 26, Art.UI_LINE)
    u.rect(9, 37.5, 15, 38.5, Art.IRON_HI)


def _reader(u, green: bool) -> None:
    """The ID card reader on its post, 36 x 74, its light green or red."""
    u.rect(14, 40, 22, 74, Art.POST)
    u.rect(18, 40, 22, 74, Art.POST_DK)
    u.rrect(0, 0, 36, 44, 3, Art.OUTLINE)
    u.rrect(1, 1, 35, 43, 2.5, Art.POST_DK)
    u.rrect(4, 4, 32, 20, 1.5, Col.DARK_BLUE)           # the screen
    u.rect(5, 5, 31, 6, Col.LIGHT_BLUE)
    _letter(u, 7, 9.5, "TAP ID", Col.WHITE, 4)
    light = Art.GRASS if green else Art.TAILLIGHT
    u.oval(11, 24, 25, 38, Col.WHITE)
    u.oval(12, 25, 24, 37, light)
    u.oval(14, 26.5, 18, 30, Art.PANE_HI if green else Col.PINK)


def _draw_card(x: float, y: float) -> None:
    if frames.art(x, y, _card):
        return
    pyxel.rect(x, y, 44, 28, Col.WHITE)
    pyxel.rectb(x, y, 44, 28, Col.NAVY)
    pyxel.rect(x + 1, y + 1, 42, 7, Col.MAROON)
    pyxel.text(x + 4, y + 2, "FORDHAM", Col.WHITE)
    pyxel.rect(x + 4, y + 11, 10, 13, Col.PEACH)        # photo


def _draw_phone(x: float, y: float) -> None:
    if frames.art(x, y, _phone):
        return
    pyxel.rect(x, y, 24, 40, Col.NAVY)
    pyxel.rect(x + 2, y + 4, 20, 30, Col.LIGHT_BLUE)
    pyxel.rect(x + 3, y + 10, 18, 12, Col.MAROON)          # ID card in the wallet app


def _draw_reader(green: bool) -> None:
    x, y = READER_X, READER_Y
    if frames.art(x, y, lambda u: _reader(u, green)):
        return
    pyxel.rect(x + 14, y + 40, 8, 34, Col.GRAY)            # post
    pyxel.rect(x, y, 36, 44, Col.NAVY)
    pyxel.rect(x + 4, y + 4, 28, 16, Col.DARK_BLUE)        # screen
    pyxel.text(x + 6, y + 9, "TAP ID", Col.WHITE)
    pyxel.circ(x + 18, y + 31, 6, Col.LIME if green else Col.RED)


class IdCheckScene(Scene):
    overlay = True

    def __init__(self, app, on_done=None):
        super().__init__(app)
        self.check = IdCheck()
        self.on_done = on_done

    def update(self) -> None:
        c = self.check
        if self.input.pressed(Action.UP):
            c.move(-1)
        elif self.input.pressed(Action.DOWN):
            c.move(1)
        elif self.input.pressed(Action.CONFIRM):
            c.confirm()
        c.tick()
        if c.state == "done":
            self.app.scenes.pop()
            if self.on_done:
                self.on_done()

    def draw(self) -> None:
        c = self.check
        frames.dim()
        x, y, w, h = PANEL_X, PANEL_Y, PANEL_W, PANEL_H
        frames.box(x, y, w, h, radius=8)
        frames.header(x + 2.5, y + 2.5, w - 5, 16 + GROW)
        font.text(x + 8, y + 4, "FORDHAM ID CHECK", Col.WHITE)

        _draw_reader(c.light_green)

        if c.state == "choose":
            font.text(x + 8, y + 26 + GROW, "How will you tap in?", Col.BLACK)
            ly = y + 46 + 2 * GROW
            for i, label in enumerate(CHOICES):
                if i == c.choice:
                    frames.cursor(x + 8, ly + 2)
                lines = [label] if len(label) <= 16 else label.replace(" (", "\n(").split("\n")
                for j, line in enumerate(lines):
                    font.text(x + 18, ly + j * (12 + GROW), line, Col.BLACK if i == c.choice else Col.GRAY)
                ly += len(lines) * (12 + GROW) + 8   # a gap between options, however many lines
            font.text(x + 8, y + h - TEXT_H - 4, f"UP/DOWN: CHOOSE   {controls.key('confirm')}: TAP", Col.DARK_BLUE)
        else:
            # slide the card/phone from the left to the reader
            start_x, end_x = x + 14, READER_X - 30
            px = start_x + (end_x - start_x) * c.tap_progress
            if c.choice == CARD:
                _draw_card(px, READER_Y + 10)
            else:
                _draw_phone(px + 8, READER_Y + 2)
            if c.light_green:
                font.text(READER_X - 6, READER_Y - 13, "BEEP!", Col.GREEN)
            if c.state == "granted":
                gw = font.width("ACCESS GRANTED") + 16
                frames.pill(x + 8, y + h - 24 - GROW, gw, 16 + GROW, Col.GREEN, radius=4, shine=Art.LEAF_LT)
                font.text(x + 16, y + h - 22 - GROW, "ACCESS GRANTED", Col.WHITE)
                if (pyxel.frame_count // 8) % 2 == 0:
                    font.text(x + 16 + gw, y + h - 22 - GROW, f"{controls.key('confirm')}: CONTINUE", Col.DARK_BLUE)
