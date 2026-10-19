"""Pictures for drawn buildings (decisions/0020): map.png drawn over the
map, card.png shown on the building card.

Pure black (0, 0, 0) is transparent, as for the character sprites; use navy
for dark lines. The palette must be set (config.apply_palette) before
loading, so each pixel snaps to its exact game color.
"""

import pyxel

from game.config import TILE, Col
from game.world.buildings import BuildingAsset

TRANSPARENT = Col.BLACK

_cache: dict[str, "pyxel.Image | None"] = {}


def _load(path) -> "pyxel.Image | None":
    if path is None:
        return None
    key = str(path)
    if key not in _cache:
        _cache[key] = pyxel.Image.from_image(key, include_colors=False)
    return _cache[key]


_maps: dict = {}


def map_image(b: BuildingAsset) -> "pyxel.Image | None":
    # drawn every frame: look the file up once per building, not every
    # frame (checking that map.png exists cost about 0.7 ms a frame)
    if b.folder not in _maps:
        _maps[b.folder] = _load(b.map_png)
    return _maps[b.folder]


_fine: dict = {}


def fine_image(b: BuildingAsset) -> "pyxel.Image | None":
    """map_fine.png: the picture at twice the detail (decisions/0045)."""
    if b.folder not in _fine:
        _fine[b.folder] = _load(b.map_fine_png)
    return _fine[b.folder]


def card_image(b: BuildingAsset) -> "pyxel.Image | None":
    return _load(b.card_png)


def card_fine_image(b: BuildingAsset) -> "pyxel.Image | None":
    """card_fine.png: the card picture at twice the detail (decisions/0045)."""
    return _load(b.card_fine_png)


def draw_on_map(b: BuildingAsset, target=None) -> bool:
    """Draw the building's map.png at its place (in map pixels). Draws to the
    screen, or into `target` (a pyxel.Image). False if it has no map.png."""
    img = map_image(b)
    if img is None:
        return False
    ox, oy = b.origin
    dx, dy = b.sprite_offset
    x, y = ox * TILE + dx, oy * TILE + dy
    (target or pyxel).blt(x, y, img, 0, 0, img.width, img.height, TRANSPARENT)
    return True


def clear_cache() -> None:
    _cache.clear()
