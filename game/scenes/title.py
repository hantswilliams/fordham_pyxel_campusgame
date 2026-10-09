import pyxel

from game.config import SCREEN_H, SCREEN_W, Col
from game.systems.input import Action
from game.ui import font

from .base import Scene
from .intro import IntroScene


_title_cache: dict[str, pyxel.Image] = {}


def _big_title(y: int, s: str) -> None:
    """Draw `s` at twice the reading font's size, centred, with a shadow."""
    if s not in _title_cache:
        img = pyxel.Image(font.width(s) + 2, 14)
        img.cls(Col.BLACK)
        img.text(1, 0, s, Col.NAVY, font.font())
        img.text(0, 0, s, Col.WHITE, font.font())
        _title_cache[s] = img
    img = _title_cache[s]
    # blt scales around the centre of the source rectangle
    pyxel.blt((SCREEN_W - img.width) / 2, y, img, 0, 0, img.width, img.height,
              Col.BLACK, scale=2.0)


def centered_text(y: int, s: str, col: int) -> None:
    pyxel.text((SCREEN_W - len(s) * 4) // 2, y, s, col)


class TitleScene(Scene):
    def update(self) -> None:
        if self.input.pressed(Action.CONFIRM):
            self.app.scenes.replace(IntroScene(self.app))

    def draw(self) -> None:
        pyxel.cls(Col.MAROON)
        # simple gothic-arch frame
        pyxel.rectb(16, 16, SCREEN_W - 32, SCREEN_H - 32, Col.WHITE)
        pyxel.rectb(19, 19, SCREEN_W - 38, SCREEN_H - 38, Col.WHITE)

        font.centered(40, "WELCOME TO", Col.PEACH)
        # big title: the reading font drawn at 2x, with a navy shadow
        _big_title(62, "FORDHAM")
        _big_title(90, "CAMPUS QUEST")

        if (pyxel.frame_count // 15) % 2 == 0:
            font.centered(128, "PRESS Z / ENTER TO START", Col.YELLOW)

        centered_text(160, "PROTOTYPE - PLACEHOLDER ART", Col.GRAY)
