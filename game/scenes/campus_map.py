"""The in-game campus map (decisions/0017). Press M to open it.

Arrow keys jump between pins, Z opens the selected place's building card,
M or X closes the map."""

import pyxel

from game.config import SCREEN_H, SCREEN_W, Col
from game.systems.input import Action
from game.ui import font
from game.ui.text import BIG_CHAR_W
from game.world.directions import Direction
from game.world.mapdata import MapData
from game.world.minimap import SCALE, Pin, build_pins, next_pin, tile_colors

from .base import Scene
from .card import BuildingCardScene

MAP_X, MAP_Y = 4, 18
FOOTER_H = 26
SKIP_ROWS = 2  # top rows of the campus map are all off-campus; trimmed to fit
DIRECTION_ACTIONS = [(Action.UP, Direction.UP), (Action.DOWN, Direction.DOWN),
                     (Action.LEFT, Direction.LEFT), (Action.RIGHT, Direction.RIGHT)]
PIN_COLORS = {"transit": Col.MAROON, "landmark": Col.PINK, "building": Col.YELLOW}

_image_cache: dict[str, pyxel.Image] = {}


def map_image(m: MapData) -> pyxel.Image:
    """Draw the whole campus once at 2 px per tile, then reuse it."""
    if m.id not in _image_cache:
        img = pyxel.Image(m.width * SCALE, m.height * SCALE)
        for y, row in enumerate(tile_colors(m)):
            for x, col in enumerate(row):
                img.rect(x * SCALE, y * SCALE, SCALE, SCALE, col)
        _image_cache[m.id] = img
    return _image_cache[m.id]


def _screen_xy(x: int, y: int) -> tuple[int, int]:
    """Screen position of the centre of tile (x, y) on the map."""
    return MAP_X + x * SCALE + SCALE // 2, MAP_Y + (y - SKIP_ROWS) * SCALE + SCALE // 2


class CampusMapScene(Scene):
    def __init__(self, app, game_map: MapData, player_xy: tuple[int, int], area_name: str):
        super().__init__(app)
        self.map = game_map
        self.player_xy = player_xy
        self.area_name = area_name
        self.pins: list[Pin] = build_pins(game_map, app.locations)
        self.selected: int | None = None
        self.image = map_image(game_map)

    def update(self) -> None:
        if self.input.pressed(Action.MAP) or self.input.pressed(Action.CANCEL):
            self.app.scenes.pop()
            return
        for action, d in DIRECTION_ACTIONS:
            if self.input.pressed(action):
                if self.selected is None:
                    fx, fy = self.player_xy
                else:
                    fx, fy = self.pins[self.selected].x, self.pins[self.selected].y
                found = next_pin(self.pins, fx, fy, d)
                if found is not None:
                    self.selected = found
                return
        if self.input.pressed(Action.CONFIRM) and self.selected is not None:
            loc = self.app.locations[self.pins[self.selected].location]
            self.app.scenes.push(BuildingCardScene(self.app, loc))

    # --- drawing ---------------------------------------------------------------
    def draw(self) -> None:
        pyxel.cls(Col.NAVY)
        pyxel.rect(0, 0, SCREEN_W, 16, Col.MAROON)
        font.text(6, 2, "ROSE HILL CAMPUS MAP", Col.WHITE)
        font.text(SCREEN_W - 6 - font.width("M: CLOSE"), 2, "M: CLOSE", Col.PEACH)

        w, h = self.image.width, self.image.height - SKIP_ROWS * SCALE
        pyxel.blt(MAP_X, MAP_Y, self.image, 0, SKIP_ROWS * SCALE, w, h)
        pyxel.rectb(MAP_X - 1, MAP_Y - 1, w + 2, h + 2, Col.WHITE)

        blink = (pyxel.frame_count // 8) % 2 == 0
        for i, pin in enumerate(self.pins):
            if i != self.selected:
                self._draw_pin(pin, selected=False, blink=blink)
        if self.selected is not None:
            self._draw_pin(self.pins[self.selected], selected=True, blink=blink)
        self._draw_player(blink)
        self._draw_legend(MAP_X + w + 6, MAP_Y)
        self._draw_footer()

    def _draw_pin(self, pin: Pin, selected: bool, blink: bool) -> None:
        cx, cy = _screen_xy(pin.x, pin.y)
        col = PIN_COLORS[pin.kind]
        if selected:
            pyxel.rect(cx - 2, cy - 2, 5, 5, col)
            pyxel.rectb(cx - 3, cy - 3, 7, 7, Col.WHITE if blink else Col.NAVY)
        else:
            pyxel.rect(cx - 1, cy - 1, 3, 3, col)
            pyxel.rectb(cx - 2, cy - 2, 5, 5, Col.NAVY)

    def _draw_player(self, blink: bool) -> None:
        cx, cy = _screen_xy(*self.player_xy)
        pyxel.circb(cx, cy, 4 if blink else 3, Col.WHITE)
        pyxel.circ(cx, cy, 1, Col.MAROON)

    def _draw_legend(self, x: int, y: int) -> None:
        rows = [
            ("ROAD", Col.GRAY, "box"), ("WALKWAY", Col.PEACH, "box"),
            ("ACADEMIC", Col.DARK_BLUE, "box"), ("RESIDENCE", Col.ORANGE, "box"),
            ("CAMPUS", Col.LIGHT_BLUE, "box"), ("ADMISSION", Col.MAROON, "box"),
            ("", 0, None),
            ("PLACE", PIN_COLORS["building"], "pin"), ("LANDMARK", PIN_COLORS["landmark"], "pin"),
            ("GATE/RAM", PIN_COLORS["transit"], "pin"), ("YOU", Col.WHITE, "you"),
        ]
        for i, (label, col, kind) in enumerate(rows):
            ry = y + i * 10
            if kind == "box":
                pyxel.rect(x, ry, 6, 5, col)
            elif kind == "pin":
                pyxel.rect(x + 1, ry + 1, 3, 3, col)
                pyxel.rectb(x, ry, 5, 5, Col.WHITE)
            elif kind == "you":
                pyxel.circb(x + 2, ry + 2, 3, col)
            if label:
                pyxel.text(x + 9, ry, label, Col.WHITE)

    def _draw_footer(self) -> None:
        y = SCREEN_H - FOOTER_H
        pyxel.rect(0, y, SCREEN_W, FOOTER_H, Col.WHITE)
        pyxel.line(0, y, SCREEN_W, y, Col.NAVY)
        max_chars = (SCREEN_W - 12) // BIG_CHAR_W
        if self.selected is None:
            font.text(6, y + 2, f"You are here: {self.area_name}"[:max_chars], Col.BLACK)
            pyxel.text(6, y + 17, "ARROWS: PICK A PLACE", Col.DARK_BLUE)
        else:
            pin = self.pins[self.selected]
            font.text(6, y + 2, pin.name[:max_chars], Col.MAROON)
            pyxel.text(6, y + 17, "Z: DETAILS   ARROWS: NEXT PLACE", Col.DARK_BLUE)
