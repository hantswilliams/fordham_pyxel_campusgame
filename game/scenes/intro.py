"""Opening sequence: arrive by Metro-North, walk to the Webster Avenue gate,
learn the controls, then start the game outside the gate (decisions/0016)."""

import pyxel

from game import config
from game.config import SCREEN_H, SCREEN_W, Col
from game.gfx.intro_art import SCENE_ART, present
from game.systems import controls
from game.systems.input import Action
from game.systems.intro_timeline import IntroData, IntroTimeline, load_intro
from game.ui import font
from game.ui.text import BIG_CHAR_W, BIG_LINE_H, GROW, wrap
from game.ui.textbox import MAX_CHARS, draw_text_box

from .base import Scene

__all__ = ["IntroScene", "ControlsScene", "MAX_CHARS"]


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
        present(SCENE_ART[tl.beat.scene], tl.scene_progress, tl.scene_frame, tl.scene_length)
        draw_text_box(wrap(tl.beat.caption, MAX_CHARS), tl.revealed_chars, tl.caption_complete)
        hint = controls.fmt("{confirm}: NEXT  {back}: SKIP")
        hw = font.width(hint) + 8
        pyxel.rect(SCREEN_W - hw - 2, 2, hw, 15 + GROW, Col.NAVY)
        font.text(SCREEN_W - hw + 2, 3, hint, Col.WHITE)


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
        present(SCENE_ART["street"], 1.0, pyxel.frame_count, 1)
        pyxel.dither(0.6)
        pyxel.rect(0, 0, SCREEN_W, SCREEN_H, Col.NAVY)
        pyxel.dither(1.0)

        x, y, w, h = 6, 6, SCREEN_W - 12, SCREEN_H - 12
        pyxel.rect(x, y, w, h, Col.WHITE)
        pyxel.rectb(x, y, w, h, Col.NAVY)
        pyxel.rectb(x + 1, y + 1, w - 2, h - 2, Col.NAVY)
        pyxel.rect(x + 2, y + 2, w - 4, 16 + GROW, Col.MAROON)
        font.centered(y + 4, self.data.controls_title, Col.WHITE)

        row_y = y + 26 + GROW
        action_x = x + 24 + max(font.width(k) for k, _ in self.data.controls_rows)
        for keys, action in self.data.controls_rows:
            pyxel.rect(x + 8, row_y - 1, font.width(keys) + 8, 14 + GROW, Col.DARK_BLUE)
            font.text(x + 12, row_y, keys, Col.WHITE)
            font.text(action_x, row_y, action, Col.BLACK)
            row_y += 18 + GROW

        if self.data.tip:
            for i, line in enumerate(wrap(self.data.tip, (w - 16) // BIG_CHAR_W)):
                font.text(x + 8, row_y + 2 + i * BIG_LINE_H, line, Col.MAROON)
        if self.data.prompt and (pyxel.frame_count // 15) % 2 == 0:
            font.centered(y + h - 16, self.data.prompt, Col.DARK_BLUE)
