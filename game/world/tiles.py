"""Tile definitions: map character -> tile name, art slot, and collision.

Pure data (no Pyxel import) so it can be unit-tested.
Art for each slot is drawn in game/gfx/placeholder_art.py.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TileDef:
    name: str
    slot: int  # index of the 16x16 art slot in image bank 0
    solid: bool


# Every tile, by name.
TILES: dict[str, TileDef] = {
    t.name: t
    for t in [
        TileDef("grass", 0, False),
        TileDef("path", 1, False),
        TileDef("wall", 2, True),
        TileDef("roof", 3, True),
        TileDef("door", 4, True),
        TileDef("window", 5, True),
        TileDef("tree", 6, True),
        TileDef("flowers", 7, False),
        TileDef("hedge", 8, True),
        TileDef("water", 9, True),
        TileDef("bench", 10, True),
        TileDef("sign", 11, True),
        TileDef("banner", 12, True),
        TileDef("lamp", 13, True),
    ]
}

# Characters used in content/maps/*.txt. Digits and letters NOT listed here
# are object ids defined in the map's .json file. '@' is the player spawn.
LEGEND: dict[str, str] = {
    ".": "grass",
    ":": "path",
    "W": "wall",
    "R": "roof",
    "w": "window",
    "B": "banner",
    "T": "tree",
    "*": "flowers",
    "h": "hedge",
    "~": "water",
    "b": "bench",
    "L": "lamp",
}

SPAWN_CHAR = "@"
SPAWN_GROUND = "path"

ARTS_PER_ROW = 256 // 16  # slots per row in a 256px image bank


def slot_to_pixel(slot: int) -> tuple[int, int]:
    """Top-left pixel of an art slot in image bank 0."""
    return (slot % ARTS_PER_ROW) * 16, (slot // ARTS_PER_ROW) * 16
