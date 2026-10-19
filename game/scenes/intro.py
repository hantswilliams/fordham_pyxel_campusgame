"""Opening sequence: arrive by Metro-North, walk to the Webster Avenue gate,
learn the controls, then start the game outside the gate (decisions/0016)."""

import pyxel

from game import config
from game.config import SCREEN_H, SCREEN_W, Col
from game.gfx.intro_art import SCENE_ART, present_scene
from game.systems import controls
from game.systems.input import Action
from game.systems.intro_timeline import IntroData, IntroTimeline, load_intro
from game.ui import font, frames
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
        present_scene(SCENE_ART[tl.beat.scene], tl.scene_progress, tl.scene_frame, tl.scene_length)
        draw_text_box(wrap(tl.beat.caption, MAX_CHARS), tl.revealed_chars, tl.caption_complete)
        hint = controls.fmt("{confirm}: NEXT  {back}: SKIP")
        hw = font.width(hint) + 14
        frames.pill(SCREEN_W - hw - 4, 3, hw, 15 + GROW, Col.NAVY, radius=4, shine=Col.DARK_BLUE)
        font.text(SCREEN_W - hw + 3, 4, hint, Col.WHITE)


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
        present_scene(SCENE_ART["street"], 1.0, pyxel.frame_count, 1)
        frames.dim()
        x, y, w, h = 6, 6, SCREEN_W - 12, SCREEN_H - 12
        frames.box(x, y, w, h, radius=8)
        frames.header(x + 2.5, y + 2.5, w - 5, 16 + GROW)
        font.centered(y + 4, self.data.controls_title, Col.WHITE)

        row_y = y + 26 + GROW
        action_x = x + 24 + max(font.width(k) for k, _ in self.data.controls_rows)
        for keys, action in self.data.controls_rows:
            frames.pill(x + 8, row_y - 1, font.width(keys) + 10, 14 + GROW, Col.DARK_BLUE, radius=3,
                        shine=Col.LIGHT_BLUE)
            font.text(x + 13, row_y, keys, Col.WHITE)
            font.text(action_x, row_y, action, Col.BLACK)
            row_y += 18 + GROW

        if self.data.tip:
            for i, line in enumerate(wrap(self.data.tip, (w - 16) // BIG_CHAR_W)):
                font.text(x + 8, row_y + 2 + i * BIG_LINE_H, line, Col.MAROON)
        if self.data.prompt and (pyxel.frame_count // 15) % 2 == 0:
            font.centered(y + h - 16, self.data.prompt, Col.DARK_BLUE)
