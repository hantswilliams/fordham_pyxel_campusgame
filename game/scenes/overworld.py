"""The walkable campus map: tiles, player, NPCs, signs, doors, area banners."""

import pyxel

from game import config
from game.config import SCREEN_H, SCREEN_W, TILE, Col
from game.gfx.building_art import draw_on_map
from game.gfx.building_overlay import draw_overlay
from game.gfx.placeholder_art import BIKE_SPRITE, CHAR_IMAGE_BANK, TILE_IMAGE_BANK, character_uv
from game.systems.bike import Bike
from game.systems.input import Action
from game.ui import font
from game.world.camera import follow
from game.world.directions import Direction
from game.world.mapdata import MapData, MapObject, load_map
from game.world.movement import GridMover
from game.world.tiles import TILES, slot_to_pixel

from .campus_map import CampusMapScene
from .card import BuildingCardScene
from .dialogue import DialogueScene
from .id_check import IdCheckScene
from .base import Scene

TILEMAP_INDEX = 0
PLAYER_SPRITE = 0
BANNER_FRAMES = 75  # how long the area-name banner shows on entry
TOAST_FRAMES = 45   # how long 'ON THE BIKE' / 'WALKING' shows

# Held directions, checked in this order.
DIRECTION_ACTIONS = [
    (Action.UP, Direction.UP),
    (Action.DOWN, Direction.DOWN),
    (Action.LEFT, Direction.LEFT),
    (Action.RIGHT, Direction.RIGHT),
]


def bake_cell(game_map: MapData, index: int, x: int, y: int) -> None:
    """Re-draw one map cell into the Pyxel tilemap (e.g. a gate that opened)."""
    tm = pyxel.tilemaps[index]
    u, v = slot_to_pixel(TILES[game_map.tiles[y][x]].slot)
    for j in range(2):
        for i in range(2):
            tm.pset(x * 2 + i, y * 2 + j, (u // 8 + i, v // 8 + j))


def bake_tilemap(game_map: MapData, index: int) -> None:
    """Copy a map into a Pyxel tilemap so it draws in one bltm call.
    Each 16px game tile = 2x2 Pyxel 8px tiles."""
    tm = pyxel.tilemaps[index]
    tm.imgsrc = TILE_IMAGE_BANK
    for y, row in enumerate(game_map.tiles):
        for x, name in enumerate(row):
            u, v = slot_to_pixel(TILES[name].slot)
            for j in range(2):
                for i in range(2):
                    tm.pset(x * 2 + i, y * 2 + j, (u // 8 + i, v // 8 + j))


class OverworldScene(Scene):
    def __init__(self, app, map_id: str = config.START_MAP):
        super().__init__(app)
        self.map: MapData = load_map(map_id, config.MAPS_DIR)
        sx, sy = self.map.spawn
        self.player = GridMover(sx, sy, TILE, config.WALK_SPEED,
                                self.map.spawn_facing)
        area = self.map.area_at(sx, sy)
        self.area_name = area.name if area else self.map.display_name
        self.banner_timer = BANNER_FRAMES
        self.greeted: set[tuple[int, int]] = set()
        # the bike lives on the app, so it survives leaving the overworld
        if not hasattr(app, "bike"):
            app.bike = Bike()
        self.bike: Bike = app.bike
        self.player.speed = self.bike.speed
        self.toast = ""
        self.toast_timer = 0
        self.cam = (0, 0)
        bake_tilemap(self.map, TILEMAP_INDEX)
        # outlines, eaves, door mats and name plaques (decisions/0021),
        # drawn once into a map-sized image and copied each frame
        self.overlay = pyxel.Image(self.map.width * TILE, self.map.height * TILE)
        draw_overlay(self.overlay, self.map, app.locations)
        self._update_camera()

    # --- update ------------------------------------------------------------
    def update(self) -> None:
        if self.banner_timer > 0:
            self.banner_timer -= 1
        if self.toast_timer > 0:
            self.toast_timer -= 1

        p = self.player
        if not p.moving:
            if self.input.pressed(Action.CONFIRM):
                self._interact()
                return
            if self.input.pressed(Action.CANCEL):
                msg = self.bike.toggle()          # hop on or off (decisions/0030)
                if msg:
                    self.player.speed = self.bike.speed
                    self._show_toast(msg)
            if self.input.pressed(Action.MAP):
                self.app.scenes.push(CampusMapScene(
                    self.app, self.map, (p.tile_x, p.tile_y), self.area_name))
                return
            for action, direction in DIRECTION_ACTIONS:
                if self.input.held(action):
                    if not p.try_move(direction, self.map.is_blocked):
                        # walking into a closed gate starts the guard's ID check
                        ahead = self.map.object_at(*p.front_tile)
                        if ahead and ahead.type == "checkpoint":
                            self._start_checkpoint(ahead)
                            return
                    break
        if p.update():
            self._check_area()
            self._check_auto_npc()
        self._update_camera()

    def _show_toast(self, text: str) -> None:
        self.toast = text
        self.toast_timer = TOAST_FRAMES

    def _use_bike_rack(self) -> None:
        lines = self.bike.use_rack()
        self.player.speed = self.bike.speed
        self.app.scenes.push(DialogueScene(self.app, lines))

    def _update_camera(self) -> None:
        p = self.player
        self.cam = follow(
            p.pixel_x + TILE / 2, p.pixel_y + TILE / 2,
            SCREEN_W, SCREEN_H, self.map.width * TILE, self.map.height * TILE,
        )

    def _check_area(self) -> None:
        """Show the area banner when the player walks into a new area."""
        area = self.map.area_at(self.player.tile_x, self.player.tile_y)
        if area and area.name != self.area_name:
            self.area_name = area.name
            self.banner_timer = BANNER_FRAMES

    def _check_auto_npc(self) -> None:
        """NPCs marked "auto" walk-up greet the player once, Pokemon-style."""
        p = self.player
        found = self.map.auto_npc_next_to(p.tile_x, p.tile_y, self.greeted)
        if not found:
            return
        obj, direction = found
        self.greeted.add((obj.x, obj.y))
        p.facing = direction
        obj.facing = direction.opposite
        self.app.scenes.push(DialogueScene(self.app, obj.lines, obj.name))

    def _start_checkpoint(self, gate) -> None:
        """Guard's lines -> ID tap -> guard's 'all set' lines -> gate opens.
        The guard (an NPC whose name matches the checkpoint's) turns to you."""
        for o in self.map.objects:
            if o.type == "npc" and o.name == gate.name:
                dx, dy = self.player.tile_x - o.x, self.player.tile_y - o.y
                o.facing = (Direction.RIGHT if dx > 0 else Direction.LEFT) if abs(dx) >= abs(dy) \
                    else (Direction.DOWN if dy > 0 else Direction.UP)

        def open_gate():
            self.map.open_checkpoint(gate.x, gate.y)
            bake_cell(self.map, TILEMAP_INDEX, gate.x, gate.y)
            if gate.after_lines:
                self.app.scenes.push(DialogueScene(self.app, gate.after_lines, gate.name))

        def tap_in():
            self.app.scenes.push(IdCheckScene(self.app, on_done=open_gate))

        self.app.scenes.push(DialogueScene(self.app, gate.lines, gate.name, on_close=tap_in))

    def _interact(self) -> None:
        fx, fy = self.player.front_tile
        obj = self.map.object_at(fx, fy)
        if obj is None:
            return
        if obj.type == "checkpoint":
            self._start_checkpoint(obj)
        elif obj.type == "bike_rack":
            self._use_bike_rack()
        elif obj.type == "npc":
            obj.facing = self.player.facing.opposite
            self.app.scenes.push(DialogueScene(self.app, obj.lines, obj.name))
        elif obj.location:
            self.app.scenes.push(
                BuildingCardScene(self.app, self.app.locations[obj.location]))
        else:
            self.app.scenes.push(DialogueScene(self.app, obj.lines))

    # --- draw --------------------------------------------------------------
    def draw(self) -> None:
        pyxel.cls(Col.GREEN)
        cx, cy = self.cam
        pyxel.camera(cx, cy)
        pyxel.bltm(cx, cy, TILEMAP_INDEX, cx, cy, SCREEN_W, SCREEN_H)
        # drawn buildings go over their footprint tiles (decisions/0020).
        # Characters can't stand on a footprint, so they're always drawn after.
        for b in self.map.buildings:
            draw_on_map(b)
        pyxel.blt(cx, cy, self.overlay, cx, cy, SCREEN_W, SCREEN_H, Col.BLACK)

        # Characters, back to front so lower ones overlap upper ones.
        drawables: list[tuple[int, int, int, Direction, int]] = []
        for obj in self.map.objects:
            if obj.type == "npc":
                drawables.append((obj.y * TILE, obj.x * TILE, obj.sprite, obj.facing, 0))
        p = self.player
        sprite = BIKE_SPRITE if self.bike.riding else PLAYER_SPRITE
        frame = p.anim_frame if not self.bike.riding else (p.progress // 4) % 3 if p.moving else 0
        drawables.append((p.pixel_y, p.pixel_x, sprite, p.facing, frame))
        for y, x, sprite, facing, frame in sorted(drawables, key=lambda d: d[0]):
            u, v = character_uv(sprite, facing, frame)
            pyxel.blt(x, y - 2, CHAR_IMAGE_BANK, u, v, TILE, TILE, Col.BLACK)

        pyxel.camera()
        self._draw_hud()

    def _draw_hud(self) -> None:
        if self.toast_timer > 0:
            w = font.width(self.toast) + 12
            y = SCREEN_H - 22
            pyxel.rect(4, y, w, 16, Col.NAVY)
            pyxel.rectb(4, y, w, 16, Col.WHITE)
            font.text(10, y + 2, self.toast, Col.WHITE)
        if self.banner_timer <= 0:
            return
        name = self.area_name
        w = font.width(name) + 16
        # slide in from the top, then hold
        y = min(4, -18 + (BANNER_FRAMES - self.banner_timer) * 2)
        pyxel.rect(4, y, w, 18, Col.MAROON)
        pyxel.rectb(4, y, w, 18, Col.WHITE)
        font.text(12, y + 3, name, Col.WHITE)
