"""Text box overlay with a typewriter effect. Confirm reveals the full line,
then advances; after the last line the overlay closes."""

import pyxel

from game.config import SCREEN_H, SCREEN_W, Col
from game.systems.input import Action
from game.ui.text import CHAR_W, LINE_H, wrap

from .base import Scene

BOX_MARGIN = 6
BOX_H = 52
PADDING = 7
VISIBLE_LINES = 4
CHARS_PER_FRAME = 2


class DialogueScene(Scene):
    overlay = True

    def __init__(self, app, lines: list[str], speaker: str = "",
                 on_close=None):
        super().__init__(app)
        self.speaker = speaker
        self.on_close = on_close
        inner_w = SCREEN_W - 2 * BOX_MARGIN - 2 * PADDING
        max_chars = inner_w // CHAR_W
        # Split every source line into pages of VISIBLE_LINES wrapped lines.
        self.pages: list[list[str]] = []
        for line in lines:
            wrapped = wrap(line, max_chars)
            for i in range(0, len(wrapped), VISIBLE_LINES):
                self.pages.append(wrapped[i:i + VISIBLE_LINES])
        self.page = 0
        self.revealed = 0

    @property
    def _page_len(self) -> int:
        return sum(len(s) for s in self.pages[self.page])

    def update(self) -> None:
        if self.revealed < self._page_len:
            self.revealed += CHARS_PER_FRAME
            if self.input.pressed(Action.CONFIRM) or self.input.pressed(Action.CANCEL):
                self.revealed = self._page_len
            return
        if self.input.pressed(Action.CONFIRM) or self.input.pressed(Action.CANCEL):
            self.page += 1
            self.revealed = 0
            if self.page >= len(self.pages):
                self.app.scenes.pop()
                if self.on_close:
                    self.on_close()

    def draw(self) -> None:
        x = BOX_MARGIN
        y = SCREEN_H - BOX_H - BOX_MARGIN
        w = SCREEN_W - 2 * BOX_MARGIN
        pyxel.rect(x, y, w, BOX_H, Col.WHITE)
        pyxel.rectb(x, y, w, BOX_H, Col.NAVY)
        pyxel.rectb(x + 2, y + 2, w - 4, BOX_H - 4, Col.MAROON)

        if self.speaker:
            tw = len(self.speaker) * CHAR_W + 8
            pyxel.rect(x + 6, y - 7, tw, 10, Col.MAROON)
            pyxel.text(x + 10, y - 5, self.speaker, Col.WHITE)

        if self.page >= len(self.pages):
            return
        remaining = self.revealed
        for i, line in enumerate(self.pages[self.page]):
            shown = line[:max(0, remaining)]
            remaining -= len(line)
            pyxel.text(x + PADDING, y + PADDING + 2 + i * (LINE_H + 2),
                       shown, Col.NAVY)

        if self.revealed >= self._page_len and (pyxel.frame_count // 8) % 2 == 0:
            ax, ay = x + w - 12, y + BOX_H - 9
            pyxel.tri(ax, ay, ax + 6, ay, ax + 3, ay + 3, Col.MAROON)
