"""ID check at a campus gate: choose your Fordham ID card or your phone
(Apple Wallet / Google Wallet), tap it on the reader, get the green light."""

import pyxel

from game.config import SCREEN_H, SCREEN_W, Col
from game.systems.id_check import CHOICES, IdCheck
from game.systems.input import Action
from game.ui import font

from .base import Scene

PANEL_X, PANEL_Y = 16, 14
PANEL_W, PANEL_H = SCREEN_W - 32, 112
READER_X, READER_Y = PANEL_X + PANEL_W - 54, PANEL_Y + 30


def _draw_card(x: float, y: float) -> None:
    pyxel.rect(x, y, 44, 28, Col.WHITE)
    pyxel.rectb(x, y, 44, 28, Col.NAVY)
    pyxel.rect(x + 1, y + 1, 42, 7, Col.MAROON)
    pyxel.text(x + 4, y + 2, "FORDHAM", Col.WHITE)
    pyxel.rect(x + 4, y + 11, 10, 13, Col.PEACH)        # photo
    pyxel.rect(x + 6, y + 13, 6, 5, Col.BROWN)
    pyxel.line(x + 17, y + 13, x + 39, y + 13, Col.GRAY)  # name
    pyxel.line(x + 17, y + 17, x + 34, y + 17, Col.GRAY)
    pyxel.line(x + 17, y + 21, x + 37, y + 21, Col.GRAY)


def _draw_phone(x: float, y: float) -> None:
    pyxel.rect(x, y, 24, 40, Col.NAVY)
    pyxel.rect(x + 2, y + 4, 20, 30, Col.LIGHT_BLUE)
    pyxel.rect(x + 3, y + 10, 18, 12, Col.MAROON)          # ID card in the wallet app
    pyxel.rect(x + 4, y + 12, 5, 6, Col.PEACH)
    pyxel.line(x + 11, y + 13, x + 19, y + 13, Col.WHITE)
    pyxel.line(x + 11, y + 16, x + 17, y + 16, Col.WHITE)
    pyxel.rect(x + 9, y + 36, 6, 2, Col.GRAY)


def _draw_reader(green: bool) -> None:
    x, y = READER_X, READER_Y
    pyxel.rect(x + 14, y + 40, 8, 34, Col.GRAY)            # post
    pyxel.rect(x, y, 36, 44, Col.NAVY)
    pyxel.rect(x + 4, y + 4, 28, 16, Col.DARK_BLUE)        # screen
    pyxel.text(x + 6, y + 9, "TAP ID", Col.WHITE)
    col = Col.LIME if green else Col.RED
    pyxel.circ(x + 18, y + 31, 6, col)
    pyxel.circb(x + 18, y + 31, 6, Col.WHITE)


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
        pyxel.dither(0.5)
        pyxel.rect(0, 0, SCREEN_W, SCREEN_H, Col.NAVY)
        pyxel.dither(1.0)

        x, y, w, h = PANEL_X, PANEL_Y, PANEL_W, PANEL_H
        pyxel.rect(x, y, w, h, Col.WHITE)
        pyxel.rectb(x, y, w, h, Col.NAVY)
        pyxel.rectb(x + 1, y + 1, w - 2, h - 2, Col.NAVY)
        pyxel.rect(x + 2, y + 2, w - 4, 16, Col.MAROON)
        font.text(x + 8, y + 4, "FORDHAM ID CHECK", Col.WHITE)

        _draw_reader(c.light_green)

        if c.state == "choose":
            font.text(x + 8, y + 26, "How will you tap in?", Col.BLACK)
            for i, label in enumerate(CHOICES):
                ly = y + 50 + i * 22
                if i == c.choice:
                    pyxel.tri(x + 8, ly + 2, x + 8, ly + 10, x + 13, ly + 6, Col.MAROON)
                lines = [label] if len(label) <= 16 else label.replace(" (", "\n(").split("\n")
                for j, line in enumerate(lines):
                    font.text(x + 18, ly + j * 12, line, Col.BLACK if i == c.choice else Col.GRAY)
            pyxel.text(x + 8, y + h - 9, "UP/DOWN: CHOOSE   Z: TAP", Col.DARK_BLUE)
        else:
            # slide the card/phone from the left to the reader
            start_x, end_x = x + 14, READER_X - 30
            px = start_x + (end_x - start_x) * c.tap_progress
            if c.choice == 0:
                _draw_card(px, READER_Y + 10)
            else:
                _draw_phone(px + 8, READER_Y + 2)
            if c.light_green:
                font.text(READER_X - 6, READER_Y - 13, "BEEP!", Col.GREEN)
            if c.state == "granted":
                pyxel.rect(x + 8, y + h - 24, 112, 16, Col.GREEN)
                font.text(x + 14, y + h - 22, "ACCESS GRANTED", Col.WHITE)
                if (pyxel.frame_count // 8) % 2 == 0:
                    pyxel.text(x + 128, y + h - 17, "Z: CONTINUE", Col.DARK_BLUE)
