"""People who stroll about (decisions/0040), like the townsfolk in a
Pokemon game: an NPC with `"wander": n` in the map takes a step now and
then, staying within n tiles of where it started. Pure logic, no Pyxel.

- It only steps onto open ground: not roads, crosswalks or parking, not in
  front of a door, and never onto or into the player.
- While stepping it holds both cells, so the player can't walk into it,
  and talking to it works from either.
- Each person has their own random generator, seeded from where they
  start, so the same game plays out the same way (tests, screenshots).
- They stand still while the game is paused or a text box is open, since
  only the overworld moves them.
"""

import random

from .directions import Direction
from .mapdata import MapData, MapObject

STEP_SPEED = 1                    # pixels a frame: half the player's walking pace
PAUSE = (45, 150)                 # frames between steps
AVOID = {"road", "crosswalk_h", "crosswalk_v", "parking"}
ENABLED = True                    # tools/capture.py turns this off: its walks are planned on a still map


class Wanderer:
    def __init__(self, obj: MapObject, tile: int):
        self.obj = obj
        self.home = (obj.x, obj.y)
        self.tile = tile
        self.rng = random.Random(obj.x * 1000 + obj.y)
        self.wait = self.rng.randint(*PAUSE)
        self.step: Direction | None = None   # the way it's walking, while it walks
        self.progress = 0
        self.steps = 0

    def can_step(self, m: MapData, x: int, y: int, player: set) -> bool:
        hx, hy = self.home
        r = self.obj.wander
        if abs(x - hx) > r or abs(y - hy) > r or (x, y) in player:
            return False
        if m.is_blocked(x, y) or m.tiles[y][x] in AVOID:
            return False
        above = m.object_at(x, y - 1)
        return not (above and above.type == "door")          # keep doorways clear

    def update(self, m: MapData, player: set) -> None:
        if self.step is not None:
            self.progress += STEP_SPEED
            if self.progress >= self.tile:
                m.end_move(self.obj, self.obj.x + self.step.dx, self.obj.y + self.step.dy)
                self.step, self.progress = None, 0
                self.steps += 1
                self.wait = self.rng.randint(*PAUSE)
            return
        self.wait -= 1
        if self.wait > 0:
            return
        d = self.rng.choice(list(Direction))
        self.obj.facing = d
        self.wait = self.rng.randint(*PAUSE)
        if self.rng.random() < 0.3:                           # sometimes just look around
            return
        x, y = self.obj.x + d.dx, self.obj.y + d.dy
        if self.can_step(m, x, y, player):
            m.begin_move(self.obj, x, y)
            self.step, self.progress = d, 0

    @property
    def pixel_xy(self) -> tuple[int, int]:
        x, y = self.obj.x * self.tile, self.obj.y * self.tile
        if self.step is not None:
            x += self.step.dx * self.progress
            y += self.step.dy * self.progress
        return x, y

    @property
    def frame(self) -> int:
        """0 = standing, 1 = left foot, 2 = right foot (like the player)."""
        if self.step is not None and self.progress < self.tile // 2:
            return 1 + self.steps % 2
        return 0


class Wanderers:
    def __init__(self, m: MapData, tile: int):
        self.map = m
        self.by_obj = {id(o): Wanderer(o, tile) for o in m.objects
                       if o.type == "npc" and o.wander > 0}

    def update(self, player: set) -> None:
        if not ENABLED:
            return
        for w in self.by_obj.values():
            w.update(self.map, player)

    def get(self, obj: MapObject) -> Wanderer | None:
        return self.by_obj.get(id(obj))
