"""Text box overlay with a typewriter effect. Confirm reveals the full page,
then advances; after the last page the overlay closes."""

from game.systems.input import Action
from game.ui.text import wrap
from game.ui.textbox import LINES, MAX_CHARS, draw_text_box

from .base import Scene

CHARS_PER_FRAME = 2


def paginate(lines: list[str], max_chars: int = MAX_CHARS, per_page: int = LINES) -> list[list[str]]:
    """Wrap each source line and split it into pages of `per_page` lines.
    Each source line always starts a new page."""
    pages: list[list[str]] = []
    for line in lines:
        wrapped = wrap(line, max_chars)
        for i in range(0, len(wrapped), per_page):
            pages.append(wrapped[i:i + per_page])
    return pages


class DialogueScene(Scene):
    overlay = True

    def __init__(self, app, lines: list[str], speaker: str = "",
                 on_close=None):
        super().__init__(app)
        self.speaker = speaker
        self.on_close = on_close
        self.pages = paginate(lines)
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
        if self.page >= len(self.pages):
            return
        draw_text_box(self.pages[self.page], self.revealed,
                      self.revealed >= self._page_len, self.speaker)
