"""The walkable campus map: tiles, player, NPCs, signs, doors."""

import pyxel

from game import config
from game.config import SCREEN_H, SCREEN_W, TILE, Col
from game.gfx.placeholder_art import CHAR_IMAGE_BANK, TILE_IMAGE_BANK, character_uv
from game.systems.input import Action
from game.world.camera import follow
from game.world.directions import Direction
from game.world.mapdata import MapData, MapObject, load_map
from game.world.movement import GridMover
from game.world.tiles import TILES, slot_to_pixel

from .dialogue import DialogueScene
from .base import Scene

TILEMAP_INDEX = 0
PLAYER_SPRITE = 0
BANNER_FRAMES = 75  # how long the area-name banner shows on entry

# Held directions, checked in this order.
DIRECTION_ACTIONS = [
    (Action.UP, Direction.UP),
    (Action.DOWN, Direction.DOWN),
    (Action.LEFT, Direction.LEFT),
    (Action.RIGHT, Direction.RIGHT),
]


class OverworldScene(Scene):
    def __init__(self, app, map_id: str = config.START_MAP):
        super().__init__(app)
        self.map: MapData = load_map(map_id, config.MAPS_DIR)
        sx, sy = self.map.spawn
        self.player = GridMover(sx, sy, TILE, config.WALK_SPEED, Direction.UP)
        self.banner_timer = BANNER_FRAMES
        self.cam = (0, 0)
        self._build_tilemap()

    # --- setup -------------------------------------------------------------
    def _build_tilemap(self) -> None:
        """Bake the map into a Pyxel tilemap so it draws in one bltm call.
        Each 16px game tile = 2x2 Pyxel 8px tiles."""
        tm = pyxel.tilemaps[TILEMAP_INDEX]
        tm.imgsrc = TILE_IMAGE_BANK
        for y, row in enumerate(self.map.tiles):
            for x, name in enumerate(row):
                u, v = slot_to_pixel(TILES[name].slot)
                for j in range(2):
                    for i in range(2):
                        tm.pset(x * 2 + i, y * 2 + j, (u // 8 + i, v // 8 + j))

    # --- update ------------------------------------------------------------
    def update(self) -> None:
        if self.banner_timer > 0:
            self.banner_timer -= 1

        p = self.player
        if not p.moving:
            if self.input.pressed(Action.CONFIRM):
                self._interact()
                return
            for action, direction in DIRECTION_ACTIONS:
                if self.input.held(action):
                    p.try_move(direction, self.map.is_blocked)
                    break
        p.update()

        self.cam = follow(
            p.pixel_x + TILE / 2, p.pixel_y + TILE / 2,
            SCREEN_W, SCREEN_H, self.map.width * TILE, self.map.height * TILE,
        )

    def _interact(self) -> None:
        fx, fy = self.player.front_tile
        obj = self.map.object_at(fx, fy)
        if obj is None:
            return
        if obj.type == "npc":
            obj.facing = self.player.facing.opposite
        speaker = obj.name if obj.type == "npc" else ""
        self.app.scenes.push(DialogueScene(self.app, obj.lines, speaker))

    # --- draw --------------------------------------------------------------
    def draw(self) -> None:
        pyxel.cls(Col.GREEN)
        cx, cy = self.cam
        pyxel.camera(cx, cy)
        pyxel.bltm(cx, cy, TILEMAP_INDEX, cx, cy, SCREEN_W, SCREEN_H)

        # Characters, back to front so lower ones overlap upper ones.
        drawables: list[tuple[int, int, int, Direction, int]] = []
        for obj in self.map.objects:
            if obj.type == "npc":
                drawables.append((obj.y * TILE, obj.x * TILE, obj.sprite, obj.facing, 0))
        p = self.player
        drawables.append((p.pixel_y, p.pixel_x, PLAYER_SPRITE, p.facing, p.anim_frame))
        for y, x, sprite, facing, frame in sorted(drawables, key=lambda d: d[0]):
            u, v = character_uv(sprite, facing, frame)
            pyxel.blt(x, y - 2, CHAR_IMAGE_BANK, u, v, TILE, TILE, Col.BLACK)

        pyxel.camera()
        self._draw_hud()

    def _draw_hud(self) -> None:
        if self.banner_timer <= 0:
            return
        name = self.map.display_name
        w = len(name) * 4 + 16
        # slide in from the top, then hold
        y = min(4, -14 + (BANNER_FRAMES - self.banner_timer) * 2)
        pyxel.rect(4, y, w, 14, Col.MAROON)
        pyxel.rectb(4, y, w, 14, Col.WHITE)
        pyxel.text(12, y + 4, name, Col.WHITE)
