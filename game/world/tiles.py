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
        TileDef("roof", 3, True),          # academic building (slate)
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
        TileDef("roof_res", 14, True),     # residence hall (terracotta)
        TileDef("roof_other", 15, True),   # library, church, campus center...
        TileDef("roof_maroon", 16, True),  # Office of Undergraduate Admission
        TileDef("field", 17, True),        # athletic turf (fenced)
        TileDef("dirt", 18, True),         # baseball infield
        TileDef("fence", 19, True),        # campus boundary
        TileDef("offcampus", 20, True),    # outside the campus
        TileDef("parking", 21, False),
        TileDef("statue", 22, True),
        TileDef("bell", 23, True),
        TileDef("shuttle", 24, True),      # Ram Van shuttle stop sign
        TileDef("pillar", 25, True),       # gate pillar
        TileDef("grave", 26, True),
        TileDef("dome", 27, True),         # Seismic Observatory
        TileDef("road", 28, False),        # campus road (asphalt), see decisions/0016
        TileDef("crosswalk_h", 29, False), # crosswalk on a road running left-right
        TileDef("crosswalk_v", 30, False), # crosswalk on a road running up-down
        TileDef("booth", 31, True),        # guard booth at a gate
        TileDef("reader_gate", 32, True),  # closed pedestrian gate with an ID card reader
        # Walsh Library, facing north onto Walsh Lawn (decisions/0019)
        TileDef("lib_stone", 33, True),    # light stone façade with piers
        TileDef("glass_arch", 34, True),   # tall glass entrance arch (a door)
        TileDef("lib_window", 35, True),   # stone with upper-floor windows
        TileDef("lib_tower", 36, True),    # the slatted stone tower
        # Campbell Hall, the newer residence hall (decisions/0019)
        TileDef("modern_roof", 37, True),
        TileDef("modern_wall", 38, True),  # dark brick with tall windows
        TileDef("glass_tower", 39, True),  # glass stair tower
        TileDef("glass_door", 40, True),   # glass entrance (a door)
        TileDef("plaza", 41, False),       # stone-paved plaza, e.g. round the Cunniffe Fountain (decisions/0022)
        TileDef("car", 42, True),          # a parked car in a parking stall
        TileDef("tree_purple", 43, True),  # copper beech: dark purple leaves (southwest corner)
        TileDef("bike_rack", 44, True),    # bike rack with bikes in it (decisions/0030)
        TileDef("item_card", 45, True),    # a mission item: a dropped ID card, sparkling (decisions/0031)
        TileDef("item_package", 46, True), # a mission item: a package (decisions/0031)
        TileDef("item_card_road", 47, True),  # the dropped ID card, lying on a road (decisions/0041)
    ]
}

# Characters used in content/maps/*.txt. '@' is the player spawn.
# Signs, NPCs, landmarks and door destinations are placed by coordinates in
# the map's .json file (like a Tiled object layer, see decisions/0005).
LEGEND: dict[str, str] = {
    ".": "grass",
    ":": "path",          # walkway / sidewalk
    "=": "road",
    "X": "crosswalk_h",
    "Y": "crosswalk_v",
    "*": "flowers",
    "P": "parking",
    "W": "wall",
    "w": "window",
    "D": "door",
    "B": "banner",
    "R": "roof",
    "O": "roof_res",
    "G": "roof_other",
    "M": "roof_maroon",
    "T": "tree",
    "h": "hedge",
    "~": "water",
    "b": "bench",
    "L": "lamp",
    "F": "field",
    "d": "dirt",
    "|": "fence",
    "#": "offcampus",
    "I": "pillar",
    "+": "grave",
    "K": "booth",
    "S": "lib_stone",
    "A": "glass_arch",
    "s": "lib_window",
    "t": "lib_tower",
    "Q": "modern_roof",
    "q": "modern_wall",
    "g": "glass_tower",
    "J": "glass_door",
    ",": "plaza",
    "c": "car",
    "V": "tree_purple",
}

# Tiles that are building entrances: each one needs a door object (with a
# location) so pressing Z on it opens the building card.
DOOR_TILES = {"door", "glass_arch", "glass_door"}

SPAWN_CHAR = "@"
SPAWN_GROUND = "path"

ARTS_PER_ROW = 256 // 16  # slots per row in a 256px image bank


def slot_to_pixel(slot: int) -> tuple[int, int]:
    """Top-left pixel of an art slot in image bank 0."""
    return (slot % ARTS_PER_ROW) * 16, (slot // ARTS_PER_ROW) * 16
