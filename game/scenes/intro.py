"""Opening sequence: arrive by Metro-North, walk to the Webster Avenue gate,
learn the controls, then start the game outside the gate (decisions/0016)."""

import pyxel

from game import config
from game.config import SCREEN_H, SCREEN_W, Col
from game.gfx.intro_art import SCENE_ART
from game.systems.input import Action
from game.systems.intro_timeline import IntroData, IntroTimeline, load_intro
from game.ui.text import CHAR_W, LINE_H, wrap

from .base import Scene

BOX_MARGIN = 6
BOX_H = 44
PAD = 8
MAX_CHARS = (SCREEN_W - 2 * BOX_MARGIN - 2 * PAD) // CHAR_W


def draw_caption(text: str, revealed: int, complete: bool) -> None:
    x, y = BOX_MARGIN, SCREEN_H - BOX_H - BOX_MARGIN
    w = SCREEN_W - 2 * BOX_MARGIN
    pyxel.rect(x, y, w, BOX_H, Col.WHITE)
    pyxel.rectb(x, y, w, BOX_H, Col.NAVY)
    pyxel.rectb(x + 2, y + 2, w - 4, BOX_H - 4, Col.MAROON)
    remaining = revealed
    for i, line in enumerate(wrap(text, MAX_CHARS)):
        pyxel.text(x + PAD, y + PAD + 1 + i * (LINE_H + 2), line[:max(0, remaining)], Col.NAVY)
        remaining -= len(line)
    if complete and (pyxel.frame_count // 8) % 2 == 0:
        ax, ay = x + w - 12, y + BOX_H - 9
        pyxel.tri(ax, ay, ax + 6, ay, ax + 3, ay + 3, Col.MAROON)


class IntroScene(Scene):
    def __init__(self, app, data: IntroData | None = None):
        super().__init__(app)
        self.data = data or load_intro(config.INTRO_FILE)
        self.timeline = IntroTimeline(self.data.beats)

    def update(self) -> None:
        tl = self.timeline
        if self.input.pressed(Action.CANCEL):
            tl.skip()
        elif self.input.pressed(Action.CONFIRM):
            tl.confirm()
        else:
            tl.tick()
        if tl.done:
            self.app.scenes.replace(ControlsScene(self.app, self.data))

    def draw(self) -> None:
        tl = self.timeline
        SCENE_ART[tl.beat.scene](tl.scene_progress, tl.scene_frame, tl.scene_length)
        draw_caption(tl.beat.caption, tl.revealed_chars, tl.caption_complete)
        hint = "Z: NEXT   X: SKIP"
        pyxel.rect(SCREEN_W - len(hint) * CHAR_W - 8, 2, len(hint) * CHAR_W + 6, 9, Col.NAVY)
        pyxel.text(SCREEN_W - len(hint) * CHAR_W - 5, 4, hint, Col.WHITE)


class ControlsScene(Scene):
    """'How to play' card over the gate. Z starts the game outside the gate."""

    def __init__(self, app, data: IntroData):
        super().__init__(app)
        self.data = data

    def update(self) -> None:
        if self.input.pressed(Action.CONFIRM):
            from .overworld import OverworldScene  # avoid an import cycle
            self.app.scenes.replace(OverworldScene(self.app))

    def draw(self) -> None:
        SCENE_ART["street"](1.0, pyxel.frame_count, 1)
        pyxel.dither(0.6)
        pyxel.rect(0, 0, SCREEN_W, SCREEN_H, Col.NAVY)
        pyxel.dither(1.0)

        x, y, w, h = 20, 22, SCREEN_W - 40, SCREEN_H - 44
        pyxel.rect(x, y, w, h, Col.WHITE)
        pyxel.rectb(x, y, w, h, Col.NAVY)
        pyxel.rect(x, y, w, 16, Col.MAROON)
        title = self.data.controls_title
        pyxel.text(x + (w - len(title) * CHAR_W) // 2, y + 5, title, Col.WHITE)

        row_y = y + 26
        for keys, action in self.data.controls_rows:
            pyxel.rect(x + 10, row_y - 2, len(keys) * CHAR_W + 6, 9, Col.DARK_BLUE)
            pyxel.text(x + 13, row_y, keys, Col.WHITE)
            pyxel.text(x + 96, row_y, action, Col.NAVY)
            row_y += 16

        if self.data.tip:
            for i, line in enumerate(wrap(self.data.tip, (w - 20) // CHAR_W)):
                pyxel.text(x + 10, row_y + 4 + i * (LINE_H + 1), line, Col.MAROON)
        if self.data.prompt and (pyxel.frame_count // 15) % 2 == 0:
            p = self.data.prompt
            pyxel.text(x + (w - len(p) * CHAR_W) // 2, y + h - 12, p, Col.DARK_BLUE)
