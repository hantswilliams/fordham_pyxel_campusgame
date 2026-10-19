"""A Pokemon-style choice: the question in the text box, the options in a
small box above it on the right, a cursor you move with UP/DOWN and pick
with Z. X picks the last option (usually "NOT NOW"). Used for mission
offers and questions (decisions/0031)."""

from game.config import SCREEN_W, Col
from game.systems.input import Action
from game.ui import font, frames
from game.ui.text import BIG_LINE_H, wrap
from game.ui.textbox import MAX_CHARS, box_top, draw_text_box

from .base import Scene


class ChoiceScene(Scene):
    overlay = True

    def __init__(self, app, question: str, options: list[str], on_choose, speaker: str = "",
                 cancel_index: int | None = None):
        super().__init__(app)
        self.lines = wrap(question, MAX_CHARS)[:3]
        self.options = options
        self.on_choose = on_choose
        self.speaker = speaker
        self.cursor = 0
        self.cancel_index = len(options) - 1 if cancel_index is None else cancel_index

    def update(self) -> None:
        if self.input.pressed(Action.UP):
            self.cursor = (self.cursor - 1) % len(self.options)
        elif self.input.pressed(Action.DOWN):
            self.cursor = (self.cursor + 1) % len(self.options)
        elif self.input.pressed(Action.CONFIRM):
            self._choose(self.cursor)
        elif self.input.pressed(Action.CANCEL):
            self._choose(self.cancel_index)

    def _choose(self, i: int) -> None:
        self.app.scenes.pop()
        self.on_choose(i)

    def draw(self) -> None:
        draw_text_box(self.lines, 10_000, False, self.speaker)
        w = max(font.width(o) for o in self.options) + 26
        h = len(self.options) * BIG_LINE_H + 12
        x, y = SCREEN_W - w - 6, box_top() - h - 4
        frames.box(x, y, w, h)
        for i, opt in enumerate(self.options):
            oy = y + 6 + i * BIG_LINE_H
            font.text(x + 18, oy, opt, Col.BLACK)
            if i == self.cursor:
                frames.cursor(x + 8, oy + 2)
