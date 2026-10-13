"""Crisp text (decisions/0038): the game is drawn at its layout size and
doubled, and the reading font is drawn over it at full size.

Pyxel can only start once per process, and another test starts the game,
so these checks run the game in a process of their own."""

import subprocess
import sys
from pathlib import Path

import pyxel

from game import config
from game.app import App
from game.config import Col
from game.gfx import display
from game.scenes.base import Scene
from game.systems.input import ScriptedInput
from game.ui import font
from game.ui.text import BIG_CHAR_W, BIG_LINE_H


class Art(Scene):
    def draw(self):
        pyxel.cls(Col.WHITE)
        pyxel.pset(10, 10, Col.MAROON)
        font.text(100, 100, "HELLO", Col.NAVY)
        display.camera(50, 0)
        font.text(150, 150, "W", Col.NAVY)      # lands at x = 100 on the screen
        display.camera()


class Cover(Scene):
    overlay = True

    def draw(self):
        pyxel.rect(90, 90, 80, 30, Col.YELLOW)  # over "HELLO"


_app = None


def make(*scenes):
    global _app
    if _app is None:
        _app = App(input_source=ScriptedInput([]), headless=True, display_scale=2,
                   start_scene=scenes[0])
    else:
        _app.scenes.replace(scenes[0](_app))
    for s in scenes[1:]:
        _app.scenes.push(s(_app))
    _app.draw()
    return _app


def colours(x0, y0, w, h):
    return {pyxel.pget(x, y) for x in range(x0, x0 + w) for y in range(y0, y0 + h)}


def check_screen_is_twice_the_layout():
    make(Art)
    assert (pyxel.width, pyxel.height) == (config.SCREEN_W * 2, config.SCREEN_H * 2)


def check_art_is_doubled_exactly():
    make(Art)
    assert colours(20, 20, 2, 2) == {Col.MAROON}
    assert pyxel.pget(19, 20) == Col.WHITE and pyxel.pget(22, 20) == Col.WHITE


def check_text_is_drawn_at_full_size_where_it_was_laid_out():
    make(Art)
    box = colours(200, 200, 5 * BIG_CHAR_W * 2, BIG_LINE_H * 2)
    assert Col.NAVY in box
    assert colours(200 - 40, 200, 30, 30) == {Col.WHITE}         # nothing left of it
    assert Col.NAVY in colours(200, 300, 16, BIG_LINE_H * 2)      # the camera-shifted "W"


def check_an_overlay_covers_the_text_beneath_it():
    make(Art, Cover)
    assert colours(200, 200, 5 * BIG_CHAR_W * 2, 20) == {Col.YELLOW}


class Tall(Scene):
    def draw(self):
        pyxel.cls(Col.WHITE)
        font.text(100, 100, "Hgjy", Col.NAVY)


def check_crisp_font_fits_the_layout():
    make(Tall)
    assert font.crisp().text_width("M") <= BIG_CHAR_W * 2     # one character per 16-pixel cell
    rows = [y for y in range(150, 280) if Col.NAVY in colours(200, y, 6 * BIG_CHAR_W * 2, 1)]
    assert rows and rows[0] >= 200 - 2 and rows[-1] < 200 + BIG_LINE_H * 2, (rows[0], rows[-1])


def test_crisp_display():
    root = Path(__file__).resolve().parent.parent
    run = subprocess.run([sys.executable, "-m", "tests.test_display"], cwd=root,
                         capture_output=True, text=True, timeout=120)
    assert run.returncode == 0, run.stdout + run.stderr[-2000:]


if __name__ == "__main__":
    failed = 0
    for name, check in list(globals().items()):
        if name.startswith("check_"):
            try:
                check()
            except AssertionError as e:
                failed += 1
                print(f"FAILED {name}: {e}")
    sys.exit(1 if failed else 0)
