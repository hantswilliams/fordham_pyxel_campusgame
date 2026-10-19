import math

import pyxel

from game import config
from game.gfx import display
from game.config import SCREEN_H, SCREEN_W, Art, Col
from game.systems.input import Action
from game.ui import font, frames
from game.ui.text import TEXT_H

from .base import Scene
from .intro import IntroScene


_title_cache: dict[str, pyxel.Image] = {}


def _big_title(y: int, s: str) -> None:
    """Draw `s` at twice the reading font's size, centred, with a shadow."""
    if display.active:                  # crisp text (decisions/0038): drawn at full size
        x = (SCREEN_W - font.width(s) * 2) / 2
        font.text(x + 1, y + 1, s, Col.NAVY, size=2)
        font.text(x, y, s, Col.WHITE, size=2)
        return
    if s not in _title_cache:
        img = pyxel.Image(font.width(s) + 2, TEXT_H + 2)
        img.cls(Col.BLACK)
        img.text(1, font.TEXT_DY, s, Col.NAVY, font.font())
        img.text(0, font.TEXT_DY, s, Col.WHITE, font.font())
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
        self.world = None                    # the campus behind the title (decisions/0045)

    def _backdrop(self) -> bool:
        """The campus in its finer look, panning slowly across Edwards Parade
        and Keating Hall. The map picture is made here once and kept for the
        walk. False when the screen isn't doubled."""
        if not display.active:
            return False
        if self.world is None:
            from game.gfx.world_art import world_for
            from game.world.mapdata import load_map
            self.world = world_for(load_map(config.START_MAP, config.MAPS_DIR), self.app.locations)
        w = self.world
        t = (1 - math.cos(pyxel.frame_count / 300)) / 2          # 0..1 and back, slowly
        cx, cy = int((44 + 14 * t) * config.TILE), 34 * config.TILE
        X, Y = cx * config.ART_SCALE, cy * config.ART_SCALE

        def draw(full):
            full.blt(0, 0, w.image, X, Y, full.width, full.height)
            for tx, ty, tile in w.visible_trees(cx, cy, SCREEN_W, SCREEN_H):
                w.draw_tree(full, tx, ty, tile, X, Y)
        return display.queue_full(draw)

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
        dy = (SCREEN_H - 192) // 2      # laid out for 192 px tall; centred on a taller screen
        if self._backdrop():
            frames.pill(40, dy + 12, SCREEN_W - 80, 160, Col.MAROON, radius=8, shine=Art.MAROON_LT,
                        drop=Art.OUTLINE)
        else:
            pyxel.cls(Col.MAROON)
            # simple gothic-arch frame
            pyxel.rectb(16, 16, SCREEN_W - 32, SCREEN_H - 32, Col.WHITE)
            pyxel.rectb(19, 19, SCREEN_W - 38, SCREEN_H - 38, Col.WHITE)

        font.centered(dy + 24, "WELCOME TO", Col.PEACH)
        # big title: the reading font drawn at 2x, with a navy shadow
        _big_title(dy + 56, "FORDHAM")
        _big_title(dy + 92, "CAMPUS QUEST")

        if self.can_continue:
            for i, label in enumerate(("CONTINUE", "NEW GAME")):
                y = dy + 132 + i * 20
                col = Col.YELLOW if i == self.cursor else Col.PEACH
                font.centered(y, label, col)
                if i == self.cursor and (pyxel.frame_count // 15) % 2 == 0:
                    w = font.width(label)
                    x = (SCREEN_W - w) // 2 - 12
                    pyxel.tri(x, y + 2, x, y + 10, x + 5, y + 6, Col.YELLOW)
        elif (pyxel.frame_count // 15) % 2 == 0:
            font.centered(dy + 136, "PRESS Z / ENTER TO START", Col.YELLOW)

        if display.active:
            note = "PROTOTYPE"
            frames.pill((SCREEN_W - len(note) * 4) // 2 - 6, dy + 178, len(note) * 4 + 12, 10, Art.OUTLINE,
                        rim=None, radius=3)
            centered_text(dy + 180, note, Col.GRAY)
        else:
            centered_text(dy + 176, "PROTOTYPE - PLACEHOLDER ART", Col.GRAY)
