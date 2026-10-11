"""Placeholder art drawn in code at startup, so the prototype needs no
asset files. Replace with real pixel art in assets/game.pyxres later
(decisions/0008-art-and-branding.md). Slot numbers match game/world/tiles.py."""

import pyxel

from game.config import Col
from game.world.directions import Direction
from game.world.tiles import TILES, slot_to_pixel

TILE_IMAGE_BANK = 0
CHAR_IMAGE_BANK = 1

# Character colour schemes: (shirt, hair, pants, skin). Index = sprite id
# used by NPCs in content/maps/*.json. 0 is the player.
CHARACTERS = [
    (Col.MAROON, Col.BROWN, Col.NAVY, Col.PEACH),      # 0 player
    (Col.WHITE, Col.NAVY, Col.MAROON, Col.BROWN),      # 1 orientation leader
    (Col.LIGHT_BLUE, Col.ORANGE, Col.NAVY, Col.PEACH),  # 2 student
    (Col.GRAY, Col.WHITE, Col.DARK_BLUE, Col.PEACH),   # 3 staff
    (Col.YELLOW, Col.BROWN, Col.DARK_BLUE, Col.BROWN),  # 4 student
    (Col.DARK_BLUE, Col.GRAY, Col.NAVY, Col.BROWN),    # 5 security guard (Bert)
]


def character_uv(sprite: int, facing: Direction, frame: int) -> tuple[int, int]:
    return (facing.sprite_index * 3 + frame) * 16, sprite * 16


# --- tiles -----------------------------------------------------------------

def _grass(img, x, y):
    img.rect(x, y, 16, 16, Col.LIME)
    for px, py in ((2, 3), (10, 1), (6, 9), (13, 11), (3, 13), (9, 5)):
        img.pset(x + px, y + py, Col.GREEN)
        img.pset(x + px + 1, y + py - 1, Col.GREEN)


def _path(img, x, y):
    """Walkway: brick pavers, like the paths in front of Walsh Library."""
    img.rect(x, y, 16, 16, Col.PEACH)
    for row in range(4):
        by = y + row * 4 + 3
        for px in range(0, 16, 2):
            img.pset(x + px, by, Col.GRAY)
        off = 0 if row % 2 == 0 else 4
        for bx in range(off, 16, 8):
            img.pset(x + bx, by - 2, Col.GRAY)


def _wall(img, x, y):
    """Fordham stone front wall (decisions/0021 house style): warm stone in
    courses with staggered joints."""
    img.rect(x, y, 16, 16, Col.STONE)
    for row in range(4):
        by = y + row * 4 + 3
        img.line(x, by, x + 15, by, Col.STONE_SH)
        off = 0 if row % 2 == 0 else 4
        for bx in range(off, 16, 8):
            img.pset(x + bx, by - 2, Col.STONE_SH)
        img.pset(x + off + 2, by - 3, Col.STONE_HI)


def _roof(img, x, y):
    """Slate roof for academic buildings."""
    img.rect(x, y, 16, 16, Col.DARK_BLUE)
    for row in range(0, 16, 4):
        img.line(x, y + row + 3, x + 15, y + row + 3, Col.NAVY)
        off = 0 if (row // 4) % 2 == 0 else 4
        for bx in range(off, 16, 8):
            img.line(x + bx, y + row, x + bx + 4, y + row, Col.CYAN)


def _door(img, x, y):
    """Wooden door in the bottom of a stone wall; the mat outside is drawn
    on the path by game/gfx/building_overlay.py."""
    _wall(img, x, y)
    img.rect(x + 2, y + 2, 12, 14, Col.STONE_DK)
    img.rect(x + 3, y + 3, 10, 13, Col.BROWN)
    img.line(x + 8, y + 3, x + 8, y + 15, Col.STONE_DK)
    img.line(x + 4, y + 4, x + 6, y + 4, Col.ORANGE)
    img.pset(x + 6, y + 10, Col.YELLOW)
    img.pset(x + 10, y + 10, Col.YELLOW)


def _window(img, x, y):
    """Two-pane window: white frame, light blue glass (the house style)."""
    _wall(img, x, y)
    img.rect(x + 2, y + 4, 12, 9, Col.WHITE)
    img.rect(x + 3, y + 5, 4, 7, Col.LIGHT_BLUE)
    img.rect(x + 9, y + 5, 4, 7, Col.LIGHT_BLUE)
    img.line(x + 3, y + 5, x + 4, y + 5, Col.WHITE)
    img.line(x + 2, y + 13, x + 13, y + 13, Col.STONE_SH)


def _tree(img, x, y):
    _grass(img, x, y)
    img.rect(x + 6, y + 10, 4, 6, Col.BROWN)
    img.circ(x + 8, y + 7, 7, Col.NAVY)
    img.circ(x + 8, y + 7, 6, Col.GREEN)
    for px, py in ((5, 4), (9, 3), (11, 7), (6, 8), (8, 6)):
        img.pset(x + px, y + py, Col.LIME)


def _tree_purple(img, x, y):
    """A copper beech: a broad crown of dark purple leaves."""
    _grass(img, x, y)
    img.rect(x + 6, y + 11, 4, 5, Col.BROWN)
    img.circ(x + 8, y + 7, 7, Col.NAVY)
    img.circ(x + 8, y + 7, 6, Col.MAROON)
    for px, py in ((5, 4), (9, 3), (11, 7), (6, 8), (8, 5)):
        img.pset(x + px, y + py, Col.PINK_BRICK_SH)


def _flowers(img, x, y):
    _grass(img, x, y)
    for (px, py), col in zip(
        ((2, 2), (9, 3), (5, 8), (12, 9), (3, 12), (10, 13)),
        (Col.RED, Col.YELLOW, Col.PINK, Col.WHITE, Col.YELLOW, Col.RED),
    ):
        img.rect(x + px, y + py, 2, 2, col)


def _hedge(img, x, y):
    img.rect(x, y, 16, 16, Col.GREEN)
    img.rect(x, y + 13, 16, 3, Col.NAVY)
    for px in range(0, 16, 3):
        img.pset(x + px, y + 2, Col.LIME)
        img.pset(x + px + 1, y + 6, Col.LIME)
        img.pset(x + px, y + 10, Col.LIME)


def _water(img, x, y):
    img.rect(x, y, 16, 16, Col.CYAN)
    img.line(x + 2, y + 4, x + 6, y + 4, Col.WHITE)
    img.line(x + 9, y + 10, x + 13, y + 10, Col.WHITE)
    img.line(x + 4, y + 13, x + 7, y + 13, Col.LIGHT_BLUE)


def _bench(img, x, y):
    _path(img, x, y)
    img.rect(x + 1, y + 3, 14, 3, Col.BROWN)
    img.rect(x + 1, y + 7, 14, 4, Col.BROWN)
    img.line(x + 1, y + 10, x + 14, y + 10, Col.NAVY)
    img.rect(x + 2, y + 11, 2, 4, Col.NAVY)
    img.rect(x + 12, y + 11, 2, 4, Col.NAVY)


def _sign(img, x, y):
    """Gray metal signpost on two legs, as in the inspiration images
    (decisions/0021). Used beside every door and at landmarks."""
    _grass(img, x, y)
    img.rect(x + 3, y + 11, 2, 5, Col.NAVY)
    img.rect(x + 11, y + 11, 2, 5, Col.NAVY)
    img.rect(x + 1, y + 1, 14, 11, Col.NAVY)
    img.rect(x + 2, y + 2, 12, 9, Col.WHITE)
    img.rect(x + 3, y + 3, 10, 7, Col.GRAY)
    img.line(x + 4, y + 5, x + 11, y + 5, Col.WHITE)
    img.line(x + 4, y + 7, x + 9, y + 7, Col.WHITE)


def _banner(img, x, y):
    _wall(img, x, y)
    img.rect(x + 4, y + 1, 8, 12, Col.MAROON)
    img.tri(x + 4, y + 13, x + 11, y + 13, x + 8, y + 10, Col.STONE)
    img.line(x + 4, y + 1, x + 11, y + 1, Col.YELLOW)
    img.line(x + 6, y + 5, x + 9, y + 5, Col.WHITE)
    img.line(x + 7, y + 4, x + 7, y + 8, Col.WHITE)


def _lamp(img, x, y):
    _grass(img, x, y)
    img.rect(x + 7, y + 5, 2, 11, Col.NAVY)
    img.rect(x + 5, y + 1, 6, 4, Col.YELLOW)
    img.rectb(x + 5, y + 1, 6, 4, Col.NAVY)
    img.rect(x + 5, y + 14, 6, 2, Col.NAVY)


def _roof_colored(base, line, highlight):
    """Roof variants; colour tells the player what kind of building it is."""
    def draw(img, x, y):
        img.rect(x, y, 16, 16, base)
        for row in range(0, 16, 4):
            img.line(x, y + row + 3, x + 15, y + row + 3, line)
            off = 0 if (row // 4) % 2 == 0 else 3
            for bx in range(off, 16, 6):
                img.pset(x + bx, y + row + 1, highlight)
    return draw


def _field(img, x, y):
    for sx in range(0, 16, 4):
        img.rect(x + sx, y, 4, 16, Col.GREEN if (sx // 4) % 2 == 0 else Col.LIME)


def _dirt(img, x, y):
    img.rect(x, y, 16, 16, Col.ORANGE)
    for px, py in ((2, 3), (11, 2), (6, 10), (13, 12), (4, 14)):
        img.pset(x + px, y + py, Col.BROWN)


def _fence(img, x, y):
    _grass(img, x, y)
    img.line(x, y + 5, x + 15, y + 5, Col.NAVY)
    img.line(x, y + 11, x + 15, y + 11, Col.NAVY)
    for px in range(1, 16, 4):
        img.line(x + px, y + 3, x + px, y + 13, Col.NAVY)
        img.pset(x + px, y + 2, Col.NAVY)


def _offcampus(img, x, y):
    img.rect(x, y, 16, 16, Col.NAVY)
    img.line(x, y + 7, x + 15, y + 7, Col.DARK_BLUE)
    img.line(x + 7, y, x + 7, y + 15, Col.DARK_BLUE)


def _parking(img, x, y):
    img.rect(x, y, 16, 16, Col.GRAY)
    img.rect(x, y + 1, 1, 14, Col.WHITE)
    img.pset(x + 9, y + 5, Col.DARK_BLUE)
    img.pset(x + 4, y + 12, Col.DARK_BLUE)


def _statue(img, x, y):
    _grass(img, x, y)
    img.rect(x + 3, y + 11, 10, 5, Col.GRAY)
    img.line(x + 3, y + 11, x + 12, y + 11, Col.WHITE)
    img.circ(x + 8, y + 3, 2, Col.DARK_BLUE)
    img.rect(x + 6, y + 5, 5, 6, Col.DARK_BLUE)
    img.pset(x + 7, y + 6, Col.LIGHT_BLUE)


def _bell(img, x, y):
    _grass(img, x, y)
    img.rect(x + 2, y + 2, 2, 14, Col.BROWN)
    img.rect(x + 12, y + 2, 2, 14, Col.BROWN)
    img.rect(x + 2, y + 2, 12, 2, Col.BROWN)
    img.rect(x + 5, y + 5, 6, 6, Col.YELLOW)
    img.rect(x + 4, y + 10, 8, 2, Col.YELLOW)
    img.pset(x + 8, y + 12, Col.ORANGE)
    img.pset(x + 6, y + 6, Col.WHITE)


def _shuttle(img, x, y):
    _grass(img, x, y)
    img.rect(x + 7, y + 9, 2, 7, Col.NAVY)
    img.rect(x + 2, y + 1, 12, 9, Col.MAROON)
    img.rect(x + 4, y + 3, 8, 4, Col.WHITE)
    img.line(x + 5, y + 4, x + 10, y + 4, Col.LIGHT_BLUE)
    img.pset(x + 5, y + 7, Col.WHITE)
    img.pset(x + 10, y + 7, Col.WHITE)


def _pillar(img, x, y):
    _path(img, x, y)
    img.rect(x + 3, y + 2, 10, 14, Col.GRAY)
    img.rect(x + 2, y, 12, 3, Col.WHITE)
    img.line(x + 11, y + 3, x + 11, y + 15, Col.DARK_BLUE)
    img.line(x + 5, y + 8, x + 9, y + 8, Col.DARK_BLUE)


def _grave(img, x, y):
    _grass(img, x, y)
    for gx, gy in ((2, 4), (9, 7)):
        img.rect(x + gx, y + gy + 2, 5, 6, Col.GRAY)
        img.circ(x + gx + 2, y + gy + 2, 2, Col.GRAY)
        img.line(x + gx + 2, y + gy + 2, x + gx + 2, y + gy + 5, Col.DARK_BLUE)
        img.line(x + gx + 1, y + gy + 3, x + gx + 3, y + gy + 3, Col.DARK_BLUE)


def _dome(img, x, y):
    _grass(img, x, y)
    img.rect(x + 3, y + 8, 10, 7, Col.WHITE)
    img.rectb(x + 3, y + 8, 10, 7, Col.GRAY)
    img.circ(x + 8, y + 8, 5, Col.LIGHT_BLUE)
    img.rect(x + 3, y + 9, 10, 1, Col.GRAY)
    img.line(x + 8, y + 3, x + 8, y + 8, Col.NAVY)
    img.rect(x + 7, y + 11, 2, 4, Col.BROWN)


def _road(img, x, y):
    """Asphalt campus road. Deliberately darker and cooler than walkways."""
    img.rect(x, y, 16, 16, Col.GRAY)
    for px, py in ((2, 3), (9, 1), (13, 7), (5, 10), (11, 13), (1, 14), (7, 6)):
        img.pset(x + px, y + py, Col.DARK_BLUE)
    for px, py in ((4, 5), (12, 11)):
        img.pset(x + px, y + py, Col.WHITE)


def _crosswalk(vertical_stripes: bool):
    def draw(img, x, y):
        _road(img, x, y)
        for s in range(1, 16, 5):
            if vertical_stripes:
                img.rect(x + s, y, 3, 16, Col.WHITE)
            else:
                img.rect(x, y + s, 16, 3, Col.WHITE)
    return draw


def _booth(img, x, y):
    """Guard booth, from the Webster Avenue gate photo."""
    _path(img, x, y)
    img.rect(x + 3, y + 6, 10, 9, Col.WHITE)
    img.rectb(x + 3, y + 6, 10, 9, Col.GRAY)
    img.rect(x + 5, y + 8, 6, 3, Col.LIGHT_BLUE)
    img.tri(x + 1, y + 6, x + 14, y + 6, x + 8, y + 1, Col.GREEN)
    img.line(x + 1, y + 6, x + 14, y + 6, Col.NAVY)
    img.rect(x + 7, y + 12, 2, 3, Col.BROWN)


def _reader_gate(img, x, y):
    """Closed pedestrian gate (iron bars) with an ID card reader on a post.
    Opens to a plain walkway once the guard has checked your ID."""
    _path(img, x, y)
    for bx in range(1, 12, 3):
        img.line(x + bx, y + 2, x + bx, y + 15, Col.NAVY)
    img.line(x, y + 3, x + 11, y + 3, Col.NAVY)
    img.line(x, y + 12, x + 11, y + 12, Col.NAVY)
    img.rect(x + 13, y + 6, 2, 10, Col.GRAY)            # reader post
    img.rect(x + 12, y + 3, 4, 5, Col.NAVY)             # reader
    img.pset(x + 13, y + 4, Col.RED)                    # red light: locked
    img.pset(x + 14, y + 4, Col.RED)


# --- Walsh Library (from research/images/Walsh-1078_lookingSouth.jpg) ----------

def _lib_stone(img, x, y):
    img.rect(x, y, 16, 16, Col.WHITE)
    for row in range(0, 16, 4):
        img.line(x, y + row + 3, x + 15, y + row + 3, Col.GRAY)
        off = 2 if (row // 4) % 2 == 0 else 6
        for bx in range(off, 16, 8):
            img.line(x + bx, y + row, x + bx, y + row + 3, Col.GRAY)
    img.rect(x, y, 2, 16, Col.GRAY)          # stone piers
    img.rect(x + 14, y, 2, 16, Col.GRAY)


def _glass_arch(img, x, y):
    _lib_stone(img, x, y)
    img.rect(x + 3, y + 4, 10, 12, Col.NAVY)
    img.circ(x + 8, y + 4, 5, Col.NAVY)
    img.rect(x + 3, y + 5, 10, 11, Col.NAVY)
    img.line(x + 8, y + 1, x + 8, y + 15, Col.DARK_BLUE)
    img.line(x + 3, y + 9, x + 12, y + 9, Col.DARK_BLUE)
    img.line(x + 5, y + 3, x + 5, y + 7, Col.LIGHT_BLUE)   # reflection


def _lib_window(img, x, y):
    _lib_stone(img, x, y)
    for wx in (3, 9):
        img.rect(x + wx, y + 3, 4, 8, Col.NAVY)
        img.line(x + wx, y + 7, x + wx + 3, y + 7, Col.DARK_BLUE)
        img.line(x + wx - 1, y + 11, x + wx + 4, y + 11, Col.GRAY)


def _lib_tower(img, x, y):
    _roof_colored(Col.GRAY, Col.DARK_BLUE, Col.WHITE)(img, x, y)
    img.rect(x + 2, y, 12, 16, Col.WHITE)
    img.rectb(x + 2, y, 12, 16, Col.GRAY)
    for sx in range(4, 13, 2):
        img.line(x + sx, y + 2, x + sx, y + 11, Col.NAVY)     # the tower's slats
    img.rect(x + 2, y + 12, 12, 4, Col.GRAY)


# --- Campbell Hall (from research/images/campbell_dorms_facingWest.png) ------

def _modern_roof(img, x, y):
    """Flat gray panel roof: reads as 'modern', distinct from the slate
    (academic), orange (residence) and pale gray (campus) roofs."""
    img.rect(x, y, 16, 16, Col.GRAY)
    for g in range(0, 16, 8):
        img.line(x, y + g, x + 15, y + g, Col.NAVY)
        img.line(x + g, y, x + g, y + 15, Col.NAVY)
    img.rect(x + 3, y + 3, 2, 2, Col.DARK_BLUE)     # rooftop vents
    img.rect(x + 11, y + 11, 2, 2, Col.DARK_BLUE)


def _modern_wall(img, x, y):
    img.rect(x, y, 16, 16, Col.NAVY)
    for row in range(0, 16, 4):
        img.line(x, y + row, x + 15, y + row, Col.DARK_BLUE)
    for wx in (2, 7, 12):
        img.rect(x + wx, y + 2, 2, 11, Col.LIGHT_BLUE)       # tall narrow windows
        img.pset(x + wx, y + 3, Col.WHITE)


def _glass_tower(img, x, y):
    img.rect(x, y, 16, 16, Col.LIGHT_BLUE)
    for gx in range(0, 16, 4):
        img.line(x + gx, y, x + gx, y + 15, Col.WHITE)
    for gy in range(0, 16, 5):
        img.line(x, y + gy, x + 15, y + gy, Col.WHITE)
    img.line(x + 1, y + 1, x + 3, y + 3, Col.CYAN)


def _glass_door(img, x, y):
    _modern_wall(img, x, y)
    img.rect(x + 2, y + 2, 12, 2, Col.GRAY)                  # canopy
    img.rect(x + 3, y + 4, 10, 12, Col.CYAN)
    img.rectb(x + 3, y + 4, 10, 12, Col.WHITE)
    img.line(x + 8, y + 4, x + 8, y + 15, Col.WHITE)


def _plaza(img, x, y):
    """Stone pavers: larger, paler slabs than the walkways."""
    img.rect(x, y, 16, 16, Col.STONE_HI)
    for row in range(2):
        by = y + row * 8 + 7
        img.line(x, by, x + 15, by, Col.STONE)
        off = 0 if row == 0 else 6
        for bx in range(off, 16, 12):
            img.line(x + bx, by - 7, x + bx, by - 1, Col.STONE)
    img.pset(x + 3, y + 3, Col.STONE)
    img.pset(x + 11, y + 12, Col.STONE)


def _car(img, x, y):
    """A parked car seen from above, in a parking stall."""
    _parking(img, x, y)
    img.rect(x + 4, y + 2, 9, 13, Col.NAVY)
    img.rect(x + 5, y + 2, 7, 12, Col.RED)
    img.rect(x + 5, y + 4, 7, 2, Col.LIGHT_BLUE)       # windscreen
    img.rect(x + 5, y + 11, 7, 1, Col.LIGHT_BLUE)      # rear window
    img.rect(x + 6, y + 6, 5, 5, Col.MAROON)           # roof


TILE_ART = {
    "grass": _grass, "path": _path, "wall": _wall, "roof": _roof,
    "door": _door, "window": _window, "tree": _tree, "tree_purple": _tree_purple, "flowers": _flowers,
    "hedge": _hedge, "water": _water, "bench": _bench, "sign": _sign,
    "banner": _banner, "lamp": _lamp,
    "roof_res": _roof_colored(Col.ORANGE, Col.BROWN, Col.PEACH),
    "roof_other": _roof_colored(Col.GRAY, Col.DARK_BLUE, Col.WHITE),
    "roof_maroon": _roof_colored(Col.MAROON, Col.NAVY, Col.PINK),
    "field": _field, "dirt": _dirt, "fence": _fence, "offcampus": _offcampus,
    "parking": _parking, "statue": _statue, "bell": _bell, "shuttle": _shuttle,
    "pillar": _pillar, "grave": _grave, "dome": _dome,
    "road": _road, "crosswalk_h": _crosswalk(True), "crosswalk_v": _crosswalk(False),
    "booth": _booth, "reader_gate": _reader_gate,
    "lib_stone": _lib_stone, "glass_arch": _glass_arch, "lib_window": _lib_window,
    "lib_tower": _lib_tower, "modern_roof": _modern_roof, "modern_wall": _modern_wall,
    "glass_tower": _glass_tower, "glass_door": _glass_door,
    "plaza": _plaza, "car": _car,
}


def build_tiles() -> None:
    img = pyxel.images[TILE_IMAGE_BANK]
    for name, tile in TILES.items():
        x, y = slot_to_pixel(tile.slot)
        TILE_ART[name](img, x, y)


# --- characters ------------------------------------------------------------

def _character(img, ox, oy, facing: Direction, frame: int, colors) -> None:
    shirt, hair, pants, skin = colors
    d = facing
    # head
    img.rect(ox + 4, oy + 1, 8, 8, Col.NAVY)
    img.rect(ox + 5, oy + 2, 6, 6, skin)
    img.rect(ox + 4, oy + 1, 8, 3, hair)
    if d == Direction.UP:
        img.rect(ox + 5, oy + 2, 6, 6, hair)
    elif d == Direction.LEFT:
        img.rect(ox + 8, oy + 2, 3, 4, hair)
        img.pset(ox + 6, oy + 5, Col.NAVY)
    elif d == Direction.RIGHT:
        img.rect(ox + 5, oy + 2, 3, 4, hair)
        img.pset(ox + 9, oy + 5, Col.NAVY)
    else:
        img.pset(ox + 6, oy + 5, Col.NAVY)
        img.pset(ox + 9, oy + 5, Col.NAVY)
    # body + arms
    img.rect(ox + 4, oy + 9, 8, 4, shirt)
    img.rect(ox + 3, oy + 9, 1, 3, shirt)
    img.rect(ox + 12, oy + 9, 1, 3, shirt)
    img.pset(ox + 3, oy + 12, skin)
    img.pset(ox + 12, oy + 12, skin)
    # legs: frame 0 standing, 1 left foot forward, 2 right foot forward
    left_len = 2 if frame == 2 else 3
    right_len = 2 if frame == 1 else 3
    img.rect(ox + 5, oy + 13, 2, left_len - 1, pants)
    img.rect(ox + 5, oy + 12 + left_len, 2, 1, Col.NAVY)
    img.rect(ox + 9, oy + 13, 2, right_len - 1, pants)
    img.rect(ox + 9, oy + 12 + right_len, 2, 1, Col.NAVY)


def build_characters() -> None:
    img = pyxel.images[CHAR_IMAGE_BANK]
    for sprite, colors in enumerate(CHARACTERS):
        for d in Direction:
            for frame in range(3):
                u, v = character_uv(sprite, d, frame)
                _character(img, u, v, d, frame, colors)


def build_all() -> None:
    build_tiles()
    build_characters()
