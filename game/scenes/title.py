import pyxel

from game.config import SCREEN_H, SCREEN_W, Col
from game.systems.input import Action

from .base import Scene
from .intro import IntroScene


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

        centered_text(56, "WELCOME TO", Col.PEACH)
        # big title: draw each line twice offset for a chunky shadow
        for dx, dy, col in ((1, 1, Col.NAVY), (0, 0, Col.WHITE)):
            pyxel.text((SCREEN_W - 7 * 4) // 2 + dx, 72 + dy, "FORDHAM", col)
            pyxel.text((SCREEN_W - 12 * 4) // 2 + dx, 82 + dy, "CAMPUS QUEST", col)

        if (pyxel.frame_count // 15) % 2 == 0:
            centered_text(118, "PRESS Z / ENTER TO START", Col.YELLOW)

        centered_text(150, "ARROWS/WASD: MOVE   Z: TALK/READ", Col.PEACH)
        centered_text(160, "PROTOTYPE - PLACEHOLDER ART", Col.GRAY)
