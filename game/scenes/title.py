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
    """With a saved game (decisions/0031): CONTINUE drops you back where you
    were; NEW GAME forgets the save and starts again from the train."""

    def __init__(self, app):
        super().__init__(app)
        self.can_continue = bool(app.progress.started)
        self.cursor = 0

    def update(self) -> None:
        if self.can_continue and (self.input.pressed(Action.UP) or self.input.pressed(Action.DOWN)):
            self.cursor = 1 - self.cursor
            return
        if self.input.pressed(Action.CONFIRM):
            if self.can_continue and self.cursor == 0:
                from .overworld import OverworldScene  # avoid an import cycle
                self.app.scenes.replace(OverworldScene(self.app))
            else:
                if self.can_continue:
                    self.app.new_game()
                self.app.scenes.replace(IntroScene(self.app))

    def draw(self) -> None:
        pyxel.cls(Col.MAROON)
        dy = (SCREEN_H - 192) // 2      # laid out for 192 px tall; centred on a taller screen
        # simple gothic-arch frame
        pyxel.rectb(16, 16, SCREEN_W - 32, SCREEN_H - 32, Col.WHITE)
        pyxel.rectb(19, 19, SCREEN_W - 38, SCREEN_H - 38, Col.WHITE)

        font.centered(dy + 40, "WELCOME TO", Col.PEACH)
        # big title: the reading font drawn at 2x, with a navy shadow
        _big_title(dy + 62, "FORDHAM")
        _big_title(dy + 90, "CAMPUS QUEST")

        if self.can_continue:
            for i, label in enumerate(("CONTINUE", "NEW GAME")):
                y = dy + 122 + i * 16
                col = Col.YELLOW if i == self.cursor else Col.PEACH
                font.centered(y, label, col)
                if i == self.cursor and (pyxel.frame_count // 15) % 2 == 0:
                    w = font.width(label)
                    x = (SCREEN_W - w) // 2 - 12
                    pyxel.tri(x, y + 2, x, y + 10, x + 5, y + 6, Col.YELLOW)
        elif (pyxel.frame_count // 15) % 2 == 0:
            font.centered(dy + 128, "PRESS Z / ENTER TO START", Col.YELLOW)

        centered_text(dy + 160, "PROTOTYPE - PLACEHOLDER ART", Col.GRAY)
