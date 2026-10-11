"""Draw a whole map at full size (tiles, drawn buildings, outlines and
plaques) into one image. Used by the in-game campus map (decisions/0032)
and by tools/render_map.py."""

import pyxel

from game.config import TILE
from game.gfx.building_art import draw_on_map
from game.gfx.building_overlay import draw_overlay
from game.world.mapdata import MapData

SCRATCH_TILEMAP = 7  # a spare Pyxel tilemap; the overworld uses 0


def render_world(m: MapData, locations, tilemap_index: int = SCRATCH_TILEMAP) -> pyxel.Image:
    from game.scenes.overworld import bake_tilemap  # avoid an import cycle
    bake_tilemap(m, tilemap_index)
    w, h = m.width * TILE, m.height * TILE
    img = pyxel.Image(w, h)
    img.bltm(0, 0, tilemap_index, 0, 0, w, h)
    for b in m.buildings:
        draw_on_map(b, img)
    draw_overlay(img, m, locations)
    return img
