"""The world at twice the detail (decisions/0045).

The game still plays on 16 px cells; this is only how it looks. When a map
loads, the whole of it is drawn once into one picture with 32 px cells:

1. the ground: lawns with soft patches and grass tufts, walkways, stone
   plazas, roads with kerbs and crosswalks, parking; a darker edging where
   paving meets a lawn, with rounded corners (game/world/ground.py says
   which)
2. shadows, falling down and to the right from buildings, trees and the
   things standing on the ground: one darker shade of whatever they land on
3. drawn buildings at full detail (their map_fine.png, from
   assets/buildings/_style/fine.py); today's building tiles and objects,
   doubled (until they're redrawn)
4. the outlines, mats and plaques (game/gfx/building_overlay.py), doubled,
   with the plaques' names lettered at full detail

Each frame the overworld copies the part on screen and draws the rest over
it at full size: trees in the new style, sorted with the people so a crown
covers whoever stands behind it; mission items and closed gates, which come
and go; people and vans, with shadows cut to shape each frame.

Pyxel can't blend colours, so a shadow is cut to shape with two scratch
pictures (Shadows): one copies with every colour swapped for its shade
(config.SHADOW_OF), the other turns a caster into a stencil.
"""

from __future__ import annotations

import math

import pyxel

from game.config import ART_SCALE, SHADOW_OF, TILE, Art, Col
from game.gfx.building_art import fine_image, map_image
from game.gfx.building_overlay import BUILDING_TILES, draw_overlay
from game.gfx.placeholder_art import TILE_IMAGE_BANK, object_tiles
from game.ui import font
from game.world import ground as G
from game.world.mapdata import MapData
from game.world.tiles import TILES, slot_to_pixel

K = ART_SCALE
CELL = TILE * K                 # 32 art pixels to a cell
RADIUS = 10                     # rounded lawn corners
ROAD_RADIUS = 12                # rounded road corners
BUILDING_SHADOW = (12, 6)       # how far a shadow falls, right and down (art pixels)
LOW_SHADOW = (4, 4)             # hedges
OBJECT_SHADOW = (4, 3)          # signs, lamps, benches

# where things are on the atlas (one 256 x 256 picture, made once)
TUFTS_V, FLOWERS_U, STRIPES_U = 0, 128, 192
PLAZA_V, ROAD_U, PARK_U = 32, 96, 160
CORNER_V = 64                   # corner pieces: rows 64, 80 and 96, 16 px apart
TREE_V = 112
TREE_W, TREE_H = 56, 64
TREE_ORIGIN = (12, 30)          # the tree's cell's top-left, in the tree picture
SHADOW_U = 128
TREE_SHADOW = (SHADOW_U, 112, 48, 18)
PERSON_SHADOW = (SHADOW_U, 132, 24, 9)
VAN_SIDE_SHADOW = (SHADOW_U, 144, 64, 14)
VAN_END_SHADOW = (SHADOW_U, 160, 36, 12)


def _strip(img, px: int, py: int, side: str, inset: int, width: int, cut0: bool, cut1: bool,
           r: int, col: int) -> None:
    """A band `width` px wide along one side of the cell at (px, py),
    starting `inset` px in from that side (negative: out into the next
    cell), cut r px short at either end."""
    a0, a1 = (r if cut0 else 0), CELL - (r if cut1 else 0)
    if side in ("top", "bottom"):
        y = py + inset if side == "top" else py + CELL - inset - width
        img.rect(px + a0, y, a1 - a0, width, col)
    else:
        x = px + inset if side == "left" else px + CELL - inset - width
        img.rect(x, py + a0, width, a1 - a0, col)


def _hash(*vals: int) -> float:
    """A repeatable 0..1 for a cell, so the lawn looks the same every time."""
    x = 2166136261
    for v in vals:
        x = ((x ^ (v & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    x ^= x >> 13
    x = (x * 0x5BD1E995) & 0xFFFFFFFF
    x ^= x >> 15
    return x / 2 ** 32


def blt_up(dst, x: float, y: float, src, u: int, v: int, w: int, h: int,
           colkey: int | None = None, k: int = K) -> None:
    """Copy (u, v, w, h) of src into dst with its top-left at (x, y), k times
    bigger. A negative w flips it. (Pyxel scales round the middle of the
    destination, so this puts the corner where it's asked for.)"""
    if k == 1:
        dst.blt(x, y, src, u, v, w, h, colkey)
    else:
        dst.blt(x + abs(w) * (k - 1) / 2, y + h * (k - 1) / 2, src, u, v, w, h, colkey, scale=k)


class Shadows:
    """Cuts shadows to shape. Pyxel can't blend colours, so a shadow is
    made from two scratch pictures, set up once: `dark` copies with every
    colour swapped for its shade, `stencil` turns a caster into a stencil."""

    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.dark = pyxel.Image(w, h)
        for c, s in SHADOW_OF.items():
            self.dark.pal(c, s)
        self.stencil = pyxel.Image(w, h)
        for c in range(1, len(pyxel.colors)):
            if c != Art.MASK:
                self.stencil.pal(c, Col.WHITE)

    def rect(self, dst, x: int, y: int, w: int, h: int) -> None:
        """A rectangular shadow."""
        self.dark.blt(0, 0, dst, x, y, w, h)
        dst.blt(x, y, self.dark, 0, 0, w, h)

    def cast(self, dst, x: float, y: float, src, u: int, v: int, w: int, h: int, k: int = 1) -> None:
        """A shadow the shape of (u, v, w, h) of src (anything not black),
        k times bigger, with its top-left at (x, y) on dst."""
        x, y = int(x), int(y)
        sw, sh = w * k, h * k
        if sw > self.w or sh > self.h:
            return
        self.stencil.rect(0, 0, sw, sh, Art.MASK)
        blt_up(self.stencil, 0, 0, src, u, v, w, h, Col.BLACK, k)
        self.dark.blt(0, 0, dst, x, y, sw, sh)
        self.dark.blt(0, 0, self.stencil, 0, 0, sw, sh, Col.WHITE)
        dst.blt(x, y, self.dark, 0, 0, sw, sh, Art.MASK)


# --- the atlas: tiles and pieces for the ground, trees, shadow shapes -------

_atlas: pyxel.Image | None = None


def atlas() -> pyxel.Image:
    global _atlas
    if _atlas is None:
        _atlas = pyxel.Image(256, 256)
        _atlas.cls(Col.BLACK)
        _draw_atlas(_atlas)
    return _atlas


def _draw_atlas(a) -> None:
    # grass tufts (on black: drawn over the lawn), four ways round
    tuft = ((0, 0), (1, 1), (2, 1), (3, 1), (4, 0), (1, 0), (3, 0), (2, -1), (2, 0), (0, -1), (4, -1))
    for var in range(4):
        for t in range(3):
            tx = var * 32 + 3 + int(_hash(var, t, 1) * 23)
            ty = 6 + t * 9 + int(_hash(var, t, 2) * 4)
            for dx, dy in tuft:
                a.pset(tx + dx, ty + dy, Art.GRASS_TUFT)
            a.pset(tx + 2, ty - 2, Art.GRASS_HI)
    # flowers, two ways round
    petals = (Art.FLOWER_RED, Art.FLOWER_YELLOW, Art.FLOWER_WHITE, Art.FLOWER_PINK)
    spots = ((6, 6), (20, 4), (12, 16), (26, 18), (4, 24), (18, 26))
    for var in range(2):
        u = FLOWERS_U + var * 32
        for i, (x, y) in enumerate(spots):
            x, y = (x + var * 3) % 28 + 2, (y + var * 5) % 26 + 2
            petal = petals[(i + var * 2) % 4]
            mid = Art.FLOWER_YELLOW if petal != Art.FLOWER_YELLOW else Art.FLOWER_WHITE
            a.rect(u + x, y + 4, 2, 4, Art.LEAF)
            a.rect(u + x - 2, y, 6, 4, petal)
            a.rect(u + x - 1, y - 1, 4, 6, petal)
            a.rect(u + x, y + 1, 2, 2, mid)
    # crosswalk stripes: across a left-right road (bars upright), and up-down
    for s in (3, 13, 23):
        a.rect(STRIPES_U + s, 0, 6, 32, Art.STRIPE)
        a.rect(STRIPES_U + 32, s, 32, 6, Art.STRIPE)
    # plaza: square slabs in a running bond, three ways round
    for var in range(3):
        u = var * 32
        for y in range(32):
            row = y // 16
            for x in range(32):
                xs = (x + row * 8) % 32
                slab = (xs // 16, row)
                c = Art.PLAZA_ALT if _hash(var, *slab, 3) < 0.3 else Art.PLAZA
                if y % 16 == 15 or xs % 16 == 15:
                    c = Art.PLAZA_GROUT
                elif y % 16 == 0 or xs % 16 == 0:
                    c = Art.PLAZA_HI
                a.pset(u + x, PLAZA_V + y, c)
    # road: asphalt with a sparse grain, two ways round; parking with a stall line
    for var in range(2):
        u = ROAD_U + var * 32
        a.rect(u, PLAZA_V, 32, 32, Art.ROAD)
        for i in range(7):
            a.pset(u + int(_hash(var, i, 4) * 32), PLAZA_V + int(_hash(var, i, 5) * 32), Art.ROAD_DK)
    a.rect(PARK_U, PLAZA_V, 32, 32, Art.PARK)
    a.rect(PARK_U, PLAZA_V + 2, 2, 28, Art.PARK_LINE)
    for i in range(5):
        a.pset(PARK_U + 4 + int(_hash(9, i, 4) * 27), PLAZA_V + int(_hash(9, i, 5) * 32), Art.ROAD_DK)
    _draw_corners(a)
    _draw_tree(a, 0, TREE_V, (Art.LEAF_OUT, Art.LEAF_DK, Art.LEAF, Art.LEAF_LT, Art.LEAF_HI))
    _draw_tree(a, 64, TREE_V, (Art.BEECH_OUT, Art.BEECH_DK, Art.BEECH, Art.BEECH_LT, Art.BEECH_HI))
    for u, v, w, h in (TREE_SHADOW, PERSON_SHADOW, VAN_SIDE_SHADOW, VAN_END_SHADOW):
        a.elli(u, v, w, h, Col.WHITE)


# Corner pieces, drawn once for the north-west corner and mirrored. Each
# is (size, how far it reaches past the cell's corner, colours by distance
# from the middle of the rounding): 0 leaves the picture alone.
#   path / plaza: a lawn's corner with paving wrapped round it
#   lawn:         a walkway's or plaza's corner with lawn wrapped round it
#   into_road / into_park: a walkway's, plaza's or lawn's corner a road
#                 wraps round; the kerb curves with it
#   out_walk / out_plaza / out_grass: a road's corner with something
#                 else wrapped round it
CORNER_KINDS = ("path", "plaza", "lawn", "into_road", "into_park",
                "out_walk", "out_plaza", "out_grass")
_FILL = {"path": Art.WALK, "plaza": Art.PLAZA, "into_road": Art.ROAD, "into_park": Art.PARK,
         "out_walk": Art.WALK, "out_plaza": Art.PLAZA, "out_grass": Art.GRASS}


def _corner_size(kind: str) -> tuple[int, int]:
    """(size, reach past the cell's corner) of a corner piece."""
    if kind == "lawn":
        return RADIUS, 0
    if kind in ("path", "plaza"):
        return RADIUS + 2, 2
    return (ROAD_RADIUS + 2, 2) if kind.startswith("into") else (ROAD_RADIUS + 4, 4)


def _corner_colour(kind: str, d: float, inside: bool) -> int:
    """The colour at distance d from the rounding's middle; `inside` is
    whether the pixel is in the cell itself (not the reach past it)."""
    r, rr = RADIUS, ROAD_RADIUS
    fill = _FILL.get(kind, 0) if inside else 0
    if kind == "lawn":
        return 0 if d <= r - 2 else Art.WALK_EDGE if d <= r else Art.GRASS
    if kind in ("path", "plaza"):
        return 0 if d <= r else Art.WALK_EDGE if d <= r + 2 else fill
    if kind.startswith("into"):
        if d <= rr - 4:
            return 0
        return (Art.CURB if inside else 0) if d <= rr else Art.CURB_DK if d <= rr + 2 else fill
    return 0 if d <= rr - 2 else Art.CURB_DK if d <= rr else Art.CURB if d <= rr + 4 else fill


def _draw_corners(a) -> None:
    for k, kind in enumerate(CORNER_KINDS):
        n, reach = _corner_size(kind)
        r = RADIUS if kind in ("path", "plaza", "lawn") else ROAD_RADIUS
        for o, corner in enumerate(G.CORNERS):
            u, v = ((k * 4 + o) % 16) * 16, CORNER_V + (k * 4 + o) // 16 * 16
            for j in range(n):
                for i in range(n):
                    si = n - 1 - i if corner in ("ne", "se") else i
                    sj = n - 1 - j if corner in ("sw", "se") else j
                    ax, ay = si - reach + 0.5, sj - reach + 0.5     # from the cell's corner
                    c = _corner_colour(kind, math.hypot(ax - r, ay - r), ax >= 0 and ay >= 0)
                    if c:
                        a.pset(u + i, v + j, c)


def _corner_at(img, px: int, py: int, kind: str, corner: str) -> None:
    """Put a corner piece on the cell whose top-left is (px, py)."""
    k = CORNER_KINDS.index(kind) * 4 + G.CORNERS.index(corner)
    u, v = (k % 16) * 16, CORNER_V + k // 16 * 16
    n, reach = _corner_size(kind)
    x = px - reach if corner in ("nw", "sw") else px + CELL - (n - reach)
    y = py - reach if corner in ("nw", "ne") else py + CELL - (n - reach)
    img.blt(x, y, atlas(), u, v, n, n, Col.BLACK)


def _draw_tree(a, u: int, v: int, leaves) -> None:
    """A round, lumpy crown lit from the top left, on a short trunk."""
    out, dark, mid, light, hi = leaves
    px, py = u + 2, v + 2                     # room for the outline
    a.rect(px + 21, py + 37, 10, 20, out)     # trunk and its outline
    a.rect(px + 22, py + 38, 8, 18, Art.TRUNK)
    a.rect(px + 27, py + 38, 3, 18, Art.TRUNK_DK)
    lumps = ((13, 12, 10), (7, 15, 6), (19, 15, 6), (13, 6, 7), (8, 9, 6), (18, 9, 6))
    for x, y, r in lumps:
        a.circ(px + 2 * x, py + 2 * y, 2 * r + 1, out)
    for x, y, r in lumps:
        a.circ(px + 2 * x, py + 2 * y, 2 * r, dark)
    for x, y, r in lumps:
        a.circ(round(px + 2 * (x - 0.12 * r)), round(py + 2 * (y - 0.16 * r)), round(1.64 * r), mid)
    for x, y, r in lumps:
        a.circ(round(px + 2 * (x - 0.3 * r)), round(py + 2 * (y - 0.36 * r)), round(r), light)
    for x, y, r in lumps[3:]:
        a.circ(round(px + 2 * (x - 0.42 * r)), round(py + 2 * (y - 0.5 * r)), round(0.44 * r), hi)


# --- the map picture ---------------------------------------------------------

class WorldArt:
    def __init__(self, m: MapData, locations):
        self.map = m
        self.tiles = G.base_tiles(m)
        self.grid = G.ground_grid(m, self._drawn_cells())
        self.trees = [(x, y, t) for y, row in enumerate(self.tiles) for x, t in enumerate(row)
                      if t in G.TREES]
        self.image = pyxel.Image(m.width * CELL, m.height * CELL)
        self.shadows = Shadows(128, 64)           # for people and vans, each frame
        self._draw_ground()
        self._draw_shadows()
        self._draw_things()
        self._draw_overlay(locations)

    # 1. the ground
    def _draw_ground(self) -> None:
        img, grid, tiles, a = self.image, self.grid, self.tiles, atlas()
        h, w = len(grid), len(grid[0])
        img.cls(Art.GRASS)
        for y in range(h):                        # soft patches across the lawns
            for x in range(w):
                if grid[y][x] == G.GRASS and _hash(x, y, 1) < 0.14:
                    pw, ph = 40 + int(_hash(x, y, 2) * 36), 18 + int(_hash(x, y, 3) * 16)
                    img.elli(x * CELL + 16 - pw // 2, y * CELL + 16 - ph // 2, pw, ph, Art.GRASS_ALT)
        for y in range(h):
            for x in range(w):
                g, t = grid[y][x], tiles[y][x]
                px, py = x * CELL, y * CELL
                if g == G.GRASS:
                    img.blt(px, py, a, int(_hash(x, y, 4) * 4) * 32, TUFTS_V, CELL, CELL, Col.BLACK)
                    if t == "flowers":
                        img.blt(px, py, a, FLOWERS_U + (x + y) % 2 * 32, 0, CELL, CELL, Col.BLACK)
                elif g == G.PATH:
                    img.rect(px, py, CELL, CELL, Art.WALK)
                elif g == G.PLAZA:
                    img.blt(px, py, a, int(_hash(x, y, 5) * 3) * 32, PLAZA_V, CELL, CELL)
                elif g == G.ROAD:
                    img.blt(px, py, a, ROAD_U + (x * 7 + y * 3) % 2 * 32, PLAZA_V, CELL, CELL)
                    if t == "crosswalk_h":            # a crossing over a left-right road
                        img.blt(px, py, a, STRIPES_U, 0, CELL, CELL, Col.BLACK)
                    elif t == "crosswalk_v":
                        img.blt(px, py, a, STRIPES_U + 32, 0, CELL, CELL, Col.BLACK)
                elif g == G.PARKING:
                    img.blt(px, py, a, PARK_U, PLAZA_V, CELL, CELL)
                elif g == G.OFFCAMPUS:
                    img.rect(px, py, CELL, CELL, Col.STONE)
        for y in range(h):                        # edging and kerbs
            for x in range(w):
                px, py = x * CELL, y * CELL
                for side, cut0, cut1 in G.edging(grid, x, y):
                    _strip(img, px, py, side, 0, 2, cut0, cut1, RADIUS, Art.WALK_EDGE)
                for side, cut0, cut1 in G.kerbs(grid, x, y):
                    _strip(img, px, py, side, 0, 2, cut0, cut1, ROAD_RADIUS, Art.CURB_DK)
                    _strip(img, px, py, side, -4, 4, cut0, cut1, ROAD_RADIUS, Art.CURB)
        for y in range(h):                        # rounded corners
            for x in range(w):
                px, py = x * CELL, y * CELL
                for corner, paving in G.lawn_corners(grid, x, y):
                    _corner_at(img, px, py, paving, corner)
                for corner in G.paving_corners(grid, x, y):
                    _corner_at(img, px, py, "lawn", corner)
                for corner, asphalt in G.kerb_corners(grid, x, y):
                    _corner_at(img, px, py, "into_park" if asphalt == G.PARKING else "into_road", corner)
                for corner, other in G.road_corners(grid, x, y):
                    _corner_at(img, px, py, {G.PATH: "out_walk", G.PLAZA: "out_plaza"}.get(other, "out_grass"),
                               corner)

    def _drawn_cells(self) -> set[tuple[int, int]]:
        """Cells covered by a drawn building's picture."""
        return {(x, y) for b in self.map.buildings if _picture(b)[0] is not None
                for x, y, _ in b.cells()}

    # 2. shadows
    def _draw_shadows(self) -> None:
        img, tiles, objs = self.image, self.tiles, object_tiles()
        pictures = [_picture(b) for b in self.map.buildings]
        big = (max([p.width * k for p, k in pictures if p] + [128]),
               max([p.height * k for p, k in pictures if p] + [128]))
        sh = Shadows(*big)
        drawn = self._drawn_cells()
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                px, py = x * CELL, y * CELL
                if (x, y) in drawn:
                    continue
                if t in BUILDING_TILES:
                    sh.rect(img, px + BUILDING_SHADOW[0], py + BUILDING_SHADOW[1], CELL, CELL)
                elif t == "hedge":
                    sh.rect(img, px + LOW_SHADOW[0], py + LOW_SHADOW[1], CELL, CELL)
                elif t in G.TREES:
                    u, v, w, h = TREE_SHADOW
                    sh.cast(img, px - 4, py + 18, atlas(), u, v, w, h)
                elif t in G.ON_GROUND:
                    u, v = slot_to_pixel(TILES[t].slot)
                    sh.cast(img, px + OBJECT_SHADOW[0], py + OBJECT_SHADOW[1], objs, u, v, TILE, TILE, K)
        for b, (pic, k) in zip(self.map.buildings, pictures):
            # buildings cast a building's shadow, a landmark drawn at full
            # detail (the fountain, with the paving round it left clear) a low
            # one; fields lie flat, and today's landmark pictures have their
            # paving drawn in, so they'd cast a square shadow
            if pic is None:
                continue
            if _is_building(b):
                dx, dy = BUILDING_SHADOW
            elif b.landmark and k == 1:
                dx, dy = LOW_SHADOW
            else:
                continue
            ox, oy = b.origin
            sx, sy = b.sprite_offset
            sh.cast(img, (ox * TILE + sx) * K + dx, (oy * TILE + sy) * K + dy, pic, 0, 0,
                    pic.width, pic.height, k)

    # 3. buildings and objects, today's art doubled
    def _draw_things(self) -> None:
        img, tiles, objs = self.image, self.tiles, object_tiles()
        bank = pyxel.images[TILE_IMAGE_BANK]
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                u, v = slot_to_pixel(TILES[t].slot)
                if self.grid[y][x] is None:
                    blt_up(img, x * CELL, y * CELL, bank, u, v, TILE, TILE)
                elif t in G.ON_GROUND and t not in G.TREES:
                    blt_up(img, x * CELL, y * CELL, objs, u, v, TILE, TILE, Col.BLACK)
        for b in self.map.buildings:
            pic, k = _picture(b)
            if pic is not None:
                ox, oy = b.origin
                sx, sy = b.sprite_offset
                blt_up(img, (ox * TILE + sx) * K, (oy * TILE + sy) * K, pic, 0, 0,
                       pic.width, pic.height, Col.BLACK, k)

    # 4. outlines, mats and plaques
    def _draw_overlay(self, locations) -> None:
        m = self.map
        overlay = pyxel.Image(m.width * TILE, m.height * TILE)
        overlay.cls(Col.BLACK)
        labels: list = []
        draw_overlay(overlay, m, locations, labels)
        blt_up(self.image, 0, 0, overlay, 0, 0, overlay.width, overlay.height, Col.BLACK)
        for x, y, name, cell in labels:
            font.letter(self.image, x * K, y * K, name, Col.NAVY, cell * K)

    # --- each frame --------------------------------------------------------
    def visible_trees(self, cx: int, cy: int, w: int, h: int):
        """(x, y, tile) for the trees in or near the view (cx, cy, w, h), in map pixels."""
        x0, x1 = (cx - CELL) // TILE, (cx + w + CELL) // TILE
        y0, y1 = (cy - TILE) // TILE, (cy + h + 2 * TILE) // TILE
        return [t for t in self.trees if x0 <= t[0] <= x1 and y0 <= t[1] <= y1]

    def draw_tree(self, dst, x: int, y: int, tile: str, ox: int, oy: int) -> None:
        """A tree on cell (x, y); (ox, oy) is the screen's top-left on the map picture."""
        u = 0 if tile == "tree" else 64
        dst.blt(x * CELL - TREE_ORIGIN[0] - ox, y * CELL - TREE_ORIGIN[1] - oy, atlas(), u, TREE_V,
                TREE_W, TREE_H, Col.BLACK)

    def draw_dynamic(self, dst, ox: int, oy: int) -> None:
        """Mission items and closed gates: their tiles come and go, so they're
        drawn on the ground each frame rather than baked into the picture."""
        objs = object_tiles()
        for o in self.map.objects:
            if o.tile and o.type in ("item", "checkpoint"):
                u, v = slot_to_pixel(TILES[o.tile].slot)
                blt_up(dst, o.x * CELL - ox, o.y * CELL - oy, objs, u, v, TILE, TILE, Col.BLACK)

    def shadow(self, dst, x: float, y: float, shape) -> None:
        """A shadow shape from the atlas (PERSON_SHADOW...) at (x, y) on dst."""
        u, v, w, h = shape
        self.shadows.cast(dst, x, y, atlas(), u, v, w, h)


def _picture(b):
    """(picture, how much to scale it): map_fine.png as it is, or today's
    map.png doubled, or (None, 0)."""
    fine = fine_image(b)
    if fine is not None:
        return fine, 1
    pic = map_image(b)
    return (pic, K) if pic is not None else (None, 0)


def _is_building(b) -> bool:
    """A drawn building, rather than a field or a flat landmark."""
    flat = set("FdPc~.:,*=XY")
    return any(ch not in flat for row in b.footprint for ch in row if ch != " ")


_cache: dict[str, WorldArt] = {}


def world_for(m: MapData, locations) -> WorldArt:
    """The map picture, made once per map and kept: only the cells that
    change while you play (mission items, gates) differ between visits, and
    those are drawn each frame."""
    art = _cache.get(m.id)
    if art is None:
        art = _cache[m.id] = WorldArt(m, locations)
    art.map = m                 # a new game loads the map afresh
    return art
