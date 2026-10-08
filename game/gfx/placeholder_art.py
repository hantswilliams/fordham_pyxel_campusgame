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
    img.rect(x, y, 16, 16, Col.PEACH)
    for px, py in ((3, 2), (11, 6), (6, 12), (14, 14), (1, 9)):
        img.pset(x + px, y + py, Col.GRAY)


def _wall(img, x, y):
    img.rect(x, y, 16, 16, Col.GRAY)
    for row in range(4):
        by = y + row * 4
        img.line(x, by, x + 15, by, Col.DARK_BLUE)
        off = 0 if row % 2 == 0 else 4
        for bx in range(off, 16, 8):
            img.line(x + bx, by, x + bx, by + 3, Col.DARK_BLUE)
        img.line(x + off + 1, by + 1, x + off + 5, by + 1, Col.WHITE)


def _roof(img, x, y):
    img.rect(x, y, 16, 16, Col.DARK_BLUE)
    for row in range(0, 16, 4):
        img.line(x, y + row + 3, x + 15, y + row + 3, Col.NAVY)
        off = 0 if (row // 4) % 2 == 0 else 3
        for bx in range(off, 16, 6):
            img.pset(x + bx, y + row + 1, Col.LIGHT_BLUE)


def _door(img, x, y):
    _wall(img, x, y)
    img.rect(x + 3, y + 5, 10, 11, Col.BROWN)
    img.circ(x + 8, y + 6, 5, Col.BROWN)
    img.rect(x + 3, y + 6, 10, 10, Col.BROWN)
    img.line(x + 8, y + 2, x + 8, y + 15, Col.NAVY)
    img.pset(x + 6, y + 10, Col.YELLOW)
    img.pset(x + 10, y + 10, Col.YELLOW)


def _window(img, x, y):
    _wall(img, x, y)
    img.rect(x + 4, y + 4, 8, 10, Col.NAVY)
    img.tri(x + 4, y + 4, x + 11, y + 4, x + 8, y + 1, Col.NAVY)
    img.rect(x + 5, y + 5, 6, 8, Col.LIGHT_BLUE)
    img.line(x + 8, y + 3, x + 8, y + 13, Col.NAVY)
    img.line(x + 5, y + 9, x + 10, y + 9, Col.NAVY)
    img.pset(x + 6, y + 6, Col.WHITE)


def _tree(img, x, y):
    _grass(img, x, y)
    img.rect(x + 6, y + 10, 4, 6, Col.BROWN)
    img.circ(x + 8, y + 7, 7, Col.NAVY)
    img.circ(x + 8, y + 7, 6, Col.GREEN)
    for px, py in ((5, 4), (9, 3), (11, 7), (6, 8), (8, 6)):
        img.pset(x + px, y + py, Col.LIME)


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
    _grass(img, x, y)
    img.rect(x + 7, y + 9, 2, 7, Col.BROWN)
    img.rect(x + 1, y + 2, 14, 8, Col.NAVY)
    img.rect(x + 2, y + 3, 12, 6, Col.BROWN)
    img.line(x + 4, y + 5, x + 11, y + 5, Col.PEACH)
    img.line(x + 4, y + 7, x + 9, y + 7, Col.PEACH)


def _banner(img, x, y):
    _wall(img, x, y)
    img.rect(x + 4, y + 1, 8, 12, Col.MAROON)
    img.tri(x + 4, y + 13, x + 11, y + 13, x + 8, y + 10, Col.GRAY)
    img.line(x + 4, y + 1, x + 11, y + 1, Col.YELLOW)
    img.line(x + 6, y + 5, x + 9, y + 5, Col.WHITE)
    img.line(x + 7, y + 4, x + 7, y + 8, Col.WHITE)


def _lamp(img, x, y):
    _grass(img, x, y)
    img.rect(x + 7, y + 5, 2, 11, Col.NAVY)
    img.rect(x + 5, y + 1, 6, 4, Col.YELLOW)
    img.rectb(x + 5, y + 1, 6, 4, Col.NAVY)
    img.rect(x + 5, y + 14, 6, 2, Col.NAVY)


TILE_ART = {
    "grass": _grass, "path": _path, "wall": _wall, "roof": _roof,
    "door": _door, "window": _window, "tree": _tree, "flowers": _flowers,
    "hedge": _hedge, "water": _water, "bench": _bench, "sign": _sign,
    "banner": _banner, "lamp": _lamp,
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
