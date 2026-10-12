"""The in-game campus map (decisions/0017, redrawn in 0032). Press M to open it.

The main view is the real map art shrunk to 4 px per tile, so buildings,
fields and roads look as they do when you walk round. It glides to follow
the place you've picked. A small overview in the corner shows the whole
campus and the part the main view is showing.

Arrow keys jump between pins, Z opens the selected place's building card,
M or X closes the map."""

import ctypes

import pyxel

from game import config
from game.config import SCREEN_H, SCREEN_W, Col
from game.gfx.map_render import render_world
from game.systems.input import Action
from game.ui import font
from game.ui.text import BIG_CHAR_W
from game.world.directions import Direction
from game.world.mapdata import MapData
from game.world.minimap import DETAIL, OVERVIEW, Pin, build_pins, downsample, next_pin

from .base import Scene
from .card import BuildingCardScene

HEADER_H = 16
FOOTER_H = 30
VIEW_Y = HEADER_H
VIEW_H = SCREEN_H - HEADER_H - FOOTER_H
SKIP_ROWS = 2  # top rows of the campus map are all off-campus; trimmed from the overview
FOLLOW = 0.25  # how quickly the view glides to the selected place (fraction per frame)
DIRECTION_ACTIONS = [(Action.UP, Direction.UP), (Action.DOWN, Direction.DOWN),
                     (Action.LEFT, Direction.LEFT), (Action.RIGHT, Direction.RIGHT)]
PIN_COLORS = {"transit": Col.MAROON, "landmark": Col.PINK, "building": Col.YELLOW}

_cache: dict[str, tuple[pyxel.Image, pyxel.Image]] = {}


def _to_image(data: bytes, w: int, h: int) -> pyxel.Image:
    img = pyxel.Image(w, h)
    try:
        ctypes.memmove(img.data_ptr(), data, w * h)
    except Exception:                    # no direct memory access (e.g. some web builds)
        for y in range(h):
            row = y * w
            for x in range(w):
                img.pset(x, y, data[row + x])
    return img


def _pixels(img: pyxel.Image) -> bytes:
    """Every pixel's colour index, row by row."""
    w, h = img.width, img.height
    try:
        return ctypes.string_at(img.data_ptr(), w * h)
    except Exception:                    # the slow way, if ctypes can't reach the image (D-0034)
        return bytes(img.pget(x, y) for y in range(h) for x in range(w))


def map_images(m: MapData, locations) -> tuple[pyxel.Image, pyxel.Image]:
    """(detailed map at 4 px per tile, small overview), made once per map:
    render the whole map at full size, then shrink it with colour
    averaging so it reads like a painted map rather than blocks."""
    if m.id not in _cache:
        full = render_world(m, locations)
        w, h = full.width, full.height
        raw = _pixels(full)
        rgb = [((c >> 16) & 255, (c >> 8) & 255, c & 255) for c in config.palette()]
        k = config.TILE // DETAIL
        detail = downsample(raw, w, h, k, rgb)
        dw, dh = w // k, h // k
        small = downsample(detail, dw, dh, OVERVIEW, rgb)
        _cache[m.id] = (_to_image(detail, dw, dh),
                        _to_image(small, dw // OVERVIEW, dh // OVERVIEW))
    return _cache[m.id]


class CampusMapScene(Scene):
    def __init__(self, app, game_map: MapData, player_xy: tuple[int, int], area_name: str):
        super().__init__(app)
        self.map = game_map
        self.player_xy = player_xy
        self.area_name = area_name
        self.pins: list[Pin] = build_pins(game_map, app.locations)
        self.selected: int | None = None
        self.image, self.overview = map_images(game_map, app.locations)
        self.goals = self._mission_goals(app)
        self.cam_x, self.cam_y = self._target()

    def _mission_goals(self, app) -> list[tuple[int, int]]:
        """Where the tracked mission wants you next (decisions/0031)."""
        book = getattr(app, "missions", None)
        if book is None:
            return []
        out = []
        for t in book.targets():
            if "at" in t:
                out.append(tuple(t["at"]))
                continue
            for o in self.map.objects:
                if ("location" in t and o.location == t["location"] and o.type in ("door", "sign")) or \
                        ("npc" in t and o.type == "npc" and o.name == t["npc"]):
                    out.append((o.x, o.y))
                    break
        return out

    # --- where the view looks -----------------------------------------------------
    def _focus(self) -> tuple[int, int]:
        if self.selected is None:
            return self.player_xy
        p = self.pins[self.selected]
        return p.x, p.y

    def _target(self) -> tuple[float, float]:
        fx, fy = self._focus()
        tx = fx * DETAIL + DETAIL / 2 - SCREEN_W / 2
        ty = fy * DETAIL + DETAIL / 2 - VIEW_H / 2
        return (min(max(tx, 0), self.image.width - SCREEN_W),
                min(max(ty, 0), self.image.height - VIEW_H))

    def _screen_xy(self, x: int, y: int) -> tuple[int, int]:
        """Screen position of the centre of tile (x, y) in the main view."""
        return (round(x * DETAIL + DETAIL // 2 - self.cam_x),
                round(VIEW_Y + y * DETAIL + DETAIL // 2 - self.cam_y))

    # --- update ---------------------------------------------------------------------
    def update(self) -> None:
        tx, ty = self._target()
        self.cam_x += (tx - self.cam_x) * FOLLOW
        self.cam_y += (ty - self.cam_y) * FOLLOW
        if abs(tx - self.cam_x) < 0.5:
            self.cam_x = tx
        if abs(ty - self.cam_y) < 0.5:
            self.cam_y = ty

        if self.input.pressed(Action.MAP) or self.input.pressed(Action.CANCEL):
            self.app.scenes.pop()
            return
        for action, d in DIRECTION_ACTIONS:
            if self.input.pressed(action):
                fx, fy = self._focus()
                found = next_pin(self.pins, fx, fy, d)
                if found is not None:
                    self.selected = found
                return
        if self.input.pressed(Action.CONFIRM) and self.selected is not None:
            loc = self.app.locations[self.pins[self.selected].location]
            self.app.scenes.push(BuildingCardScene(self.app, loc))

    # --- drawing ----------------------------------------------------------------------
    def draw(self) -> None:
        pyxel.cls(Col.NAVY)
        pyxel.blt(0, VIEW_Y, self.image, round(self.cam_x), round(self.cam_y), SCREEN_W, VIEW_H)

        blink = (pyxel.frame_count // 8) % 2 == 0
        pyxel.clip(0, VIEW_Y, SCREEN_W, VIEW_H)
        for i, pin in enumerate(self.pins):
            if i != self.selected:
                self._draw_pin(pin, selected=False, blink=blink)
        self._draw_player(blink)
        for gx, gy in self.goals:
            cx, cy = self._screen_xy(gx, gy)
            pyxel.rect(cx - 4, cy - 16, 9, 14, Col.WHITE)
            pyxel.rectb(cx - 4, cy - 16, 9, 14, Col.MAROON)
            font.text(cx - 3, cy - 15, "!", Col.MAROON)
            pyxel.pset(cx, cy - 1, Col.MAROON)
        if self.selected is not None:
            self._draw_pin(self.pins[self.selected], selected=True, blink=blink)
        pyxel.clip()

        self._draw_overview(blink)
        self._draw_header()
        self._draw_footer()

    def _draw_header(self) -> None:
        pyxel.rect(0, 0, SCREEN_W, HEADER_H, Col.MAROON)
        font.text(6, 2, "ROSE HILL CAMPUS MAP", Col.WHITE)
        font.text(SCREEN_W - 6 - font.width("M: CLOSE"), 2, "M: CLOSE", Col.PEACH)

    def _draw_pin(self, pin: Pin, selected: bool, blink: bool) -> None:
        cx, cy = self._screen_xy(pin.x, pin.y)
        col = PIN_COLORS[pin.kind]
        if not selected:
            pyxel.rect(cx - 1, cy - 1, 3, 3, col)        # small, so the buildings show
            pyxel.rectb(cx - 2, cy - 2, 5, 5, Col.NAVY)
            return
        # a map pin with the place's name on a tag above it
        pyxel.tri(cx - 3, cy - 6, cx + 3, cy - 6, cx, cy, col)
        pyxel.circ(cx, cy - 8, 4, col)
        pyxel.circb(cx, cy - 8, 4, Col.WHITE if blink else Col.NAVY)
        pyxel.pset(cx, cy - 8, Col.WHITE)
        name = pin.name
        tw = font.width(name) + 8
        tx = min(max(cx - tw // 2, 2), SCREEN_W - tw - 2)
        ty = max(cy - 30, VIEW_Y + 2)
        pyxel.rect(tx, ty, tw, 15, Col.WHITE)
        pyxel.rectb(tx, ty, tw, 15, Col.NAVY)
        font.text(tx + 4, ty + 1, name, Col.NAVY)

    def _draw_player(self, blink: bool) -> None:
        cx, cy = self._screen_xy(*self.player_xy)
        pyxel.circ(cx, cy, 3, Col.MAROON)
        pyxel.circb(cx, cy, 5 if blink else 4, Col.WHITE)

    def _draw_overview(self, blink: bool) -> None:
        """The whole campus, small, in the top-right corner, with a yellow box
        round the part the main view is showing."""
        ov = self.overview
        skip = SKIP_ROWS * DETAIL // OVERVIEW
        w, h = ov.width, ov.height - skip
        x0, y0 = SCREEN_W - w - 4, VIEW_Y + 4
        pyxel.rect(x0 - 2, y0 - 2, w + 4, h + 4, Col.NAVY)
        pyxel.blt(x0, y0, ov, 0, skip, w, h)
        pyxel.rectb(x0 - 1, y0 - 1, w + 2, h + 2, Col.WHITE)
        pyxel.clip(x0, y0, w, h)
        pyxel.rectb(x0 + round(self.cam_x / OVERVIEW), y0 + round(self.cam_y / OVERVIEW) - skip,
                    SCREEN_W // OVERVIEW, VIEW_H // OVERVIEW, Col.YELLOW)
        for gx, gy in self.goals:
            pyxel.rect(x0 + gx * DETAIL // OVERVIEW - 1, y0 + gy * DETAIL // OVERVIEW - skip - 1, 3, 3,
                       Col.WHITE if blink else Col.MAROON)
        px, py = self.player_xy
        pyxel.rect(x0 + px * DETAIL // OVERVIEW - 1, y0 + py * DETAIL // OVERVIEW - skip - 1, 3, 3,
                   Col.MAROON if blink else Col.WHITE)
        pyxel.clip()
        self._draw_key(x0 - 2, y0 + h + 2, w + 4)

    def _draw_key(self, x: int, y: int, w: int) -> None:
        """What the pin colours mean, in a panel under the overview."""
        rows = (("Place", "building"), ("Landmark", "landmark"), ("Gate/Ram", "transit"))
        w = max(w, 14 + max(font.width(r[0]) for r in rows) + 4)
        x = min(x, SCREEN_W - w - 2)
        h = len(rows) * 12 + 4
        pyxel.rect(x, y, w, h, Col.WHITE)
        pyxel.rectb(x, y, w, h, Col.NAVY)
        for i, (label, kind) in enumerate(rows):
            ry = y + 2 + i * 12
            pyxel.rectb(x + 3, ry + 3, 7, 7, Col.NAVY)
            pyxel.rect(x + 4, ry + 4, 5, 5, PIN_COLORS[kind])
            font.text(x + 13, ry, label, Col.DARK_BLUE)

    def _draw_footer(self) -> None:
        y = SCREEN_H - FOOTER_H
        pyxel.rect(0, y, SCREEN_W, FOOTER_H, Col.WHITE)
        pyxel.line(0, y, SCREEN_W, y, Col.NAVY)
        max_chars = (SCREEN_W - 12) // BIG_CHAR_W
        if self.selected is None:
            font.text(6, y + 2, f"You are here: {self.area_name}"[:max_chars], Col.BLACK)
            font.text(6, y + 15, "ARROWS: PICK A PLACE", Col.DARK_BLUE)
        else:
            pin = self.pins[self.selected]
            font.text(6, y + 2, pin.name[:max_chars], Col.MAROON)
            font.text(6, y + 15, "Z: DETAILS  ARROWS: NEXT", Col.DARK_BLUE)
