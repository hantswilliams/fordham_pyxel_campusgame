"""First-draft art for Campbell Hall, drawn in code (decisions/0020).

Writes ../map.png (the building on the map) and ../card.png (the picture on
its building card), using only the game's palette (game/config.py).

Once someone retouches the PNGs in a drawing app, don't run this again:
it would overwrite their work. Keep it as a record of how v1 was made.

    uv run python assets/buildings/campbell_hall/options/draft_v1.py
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
ROOT = FOLDER.parents[2]
sys.path.insert(0, str(ROOT))

from game.config import palette  # noqa: E402

RGB = [((c >> 16) & 255, (c >> 8) & 255, c & 255) for c in palette()]
(BLACK, NAVY, MAROON, GREEN, BROWN, DBLUE, LBLUE, WHITE, RED, ORANGE, YELLOW,
 LIME, CYAN, GRAY, PINK, PEACH, ST_HI, ST, ST_SH, ST_DK, ROOF, ROOF_SH,
 BRICK, BRICK_DK) = RGB[:24]
CLEAR = (0, 0, 0, 0)  # black = transparent in the game

META = json.loads((FOLDER / "building.json").read_text())


# ---------------------------------------------------------------- helpers
def brick(d, x0, y0, x1, y1):
    """Charcoal brick with faint courses."""
    d.rectangle([x0, y0, x1, y1], fill=BRICK_DK)
    for y in range(y0 + 2, y1, 3):
        for x in range(x0 + (y % 2) * 2, x1, 4):
            d.point([x, y], fill=BRICK)


def window_pair(d, x, y, h=4):
    """Campbell's tall paired windows: white frames, sky-blue glass."""
    d.rectangle([x, y, x + 4, y + h], fill=WHITE)
    d.rectangle([x + 1, y + 1, x + 1, y + h - 1], fill=LBLUE)
    d.rectangle([x + 3, y + 1, x + 3, y + h - 1], fill=LBLUE)


def south_wall(d, x0, x1, y0, y1):
    """A south-facing wall: storeys of paired windows, light trim bands,
    glass at ground level."""
    brick(d, x0, y0, x1, y1)
    d.line([x0, y0, x1, y0], fill=BRICK)                      # parapet edge
    for bx in range(x0 + 2, x1 - 4, 8):
        d.line([bx + 6, y0 + 2, bx + 6, y1 - 6], fill=GRAY)    # light trim band
        for wy in range(y0 + 3, y1 - 8, 6):
            window_pair(d, bx, wy)
    d.rectangle([x0, y1 - 5, x1, y1], fill=NAVY)              # glass ground floor
    for gx in range(x0 + 1, x1, 4):
        d.line([gx, y1 - 4, gx, y1], fill=DBLUE)
    d.line([x0, y1 - 5, x1, y1 - 5], fill=GRAY)


def east_face(d, x0, x1, y0, y1):
    """The east façade, seen steeply from above along the east edge:
    a strip of brick with window bays and light trim."""
    brick(d, x0, y0, x1, y1)
    d.line([x0, y0, x0, y1], fill=BRICK)
    for wy in range(y0 + 2, y1 - 3, 6):
        d.rectangle([x0 + 2, wy, x1 - 1, wy + 3], fill=WHITE)
        d.line([x0 + 3, wy + 1, x1 - 2, wy + 1], fill=LBLUE)
        d.line([x0 + 3, wy + 2, x1 - 2, wy + 2], fill=LBLUE)


def roof(d, x0, y0, x1, y1):
    """Flat roof in stepped segments, dark parapet."""
    d.rectangle([x0, y0, x1, y1], fill=BRICK_DK)              # parapet
    d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 1], fill=ROOF_SH)
    for i, sy in enumerate(range(y0 + 2, y1 - 1, 20)):
        if i % 2:
            d.rectangle([x0 + 2, sy, x1 - 2, min(sy + 19, y1 - 1)], fill=ROOF)
        d.line([x0 + 2, sy, x1 - 2, sy], fill=BRICK_DK)       # step between segments


def glass_tower(d, x0, x1, top, base):
    """A glass stair tower rising above the roof."""
    d.rectangle([x0 - 1, top + 3, x1 + 2, base + 3], fill=BRICK_DK)  # shadow on the roof
    d.rectangle([x0, top, x1, base], fill=LBLUE)
    for gx in range(x0 + 2, x1, 3):
        d.line([gx, top, gx, base], fill=NAVY)
    for gy in range(top + 3, base, 5):
        d.line([x0, gy, x1, gy], fill=CYAN)
    d.line([x0 + 1, top + 1, x0 + 1, base - 1], fill=WHITE)  # glint
    d.rectangle([x0 - 1, top - 1, x1 + 1, top + 1], fill=GRAY)  # cap


def rooftop_unit(d, x, y, w, h):
    d.rectangle([x + 1, y + 1, x + w, y + h], fill=BRICK_DK)
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=GRAY)
    d.line([x, y, x + w - 1, y], fill=WHITE)


# ---------------------------------------------------------------- map.png
def draw_map() -> Image.Image:
    cols = max(len(r) for r in META["footprint"])
    rows = len(META["footprint"])
    im = Image.new("RGBA", (cols * 16, rows * 16), CLEAR)
    d = ImageDraw.Draw(im)
    # North part: three tiles wide, its east face set back 2 px.
    # South part: two tiles wide, shifted east; dining entrance at the step.
    roof(d, 0, 0, 39, 55)
    east_face(d, 40, 45, 0, 79)
    roof(d, 16, 56, 41, 133)
    d.rectangle([16, 80, 41, 81], fill=BRICK_DK)              # roof step between the parts
    east_face(d, 42, 47, 80, 133)
    d.line([42, 80, 47, 80], fill=BRICK)
    south_wall(d, 0, 15, 56, 79)                              # north part's exposed south wall
    south_wall(d, 16, 47, 134, 159)                           # south end

    # glass stair towers, taller than the building
    glass_tower(d, 31, 40, 24, 62)
    glass_tower(d, 31, 39, 100, 124)
    rooftop_unit(d, 6, 10, 10, 7)
    rooftop_unit(d, 20, 92, 8, 6)

    # dining entrance on the east side: glass doors under a wood canopy
    d.rectangle([40, 82, 47, 95], fill=NAVY)
    d.rectangle([41, 84, 46, 95], fill=LBLUE)
    d.line([43, 84, 43, 95], fill=NAVY)
    d.line([44, 84, 44, 95], fill=NAVY)
    d.rectangle([36, 80, 47, 82], fill=BROWN)                 # canopy
    d.line([36, 83, 47, 83], fill=BRICK_DK)
    return im


# ---------------------------------------------------------------- card.png
CARD_W, CARD_H = 228, 88


def birch(d, x, ground, h, r):
    """Birch tree: white trunk with dark marks, light leafy crown."""
    d.line([x, ground - h, x, ground], fill=WHITE)
    d.line([x + 1, ground - h + 4, x + 1, ground], fill=WHITE)
    for y in range(ground - h + 6, ground, 5):
        d.point([x, y], fill=NAVY)
    cy = ground - h
    d.ellipse([x - r, cy - r, x + r, cy + r // 2], fill=GREEN)
    d.ellipse([x - r + 3, cy - r + 1, x + r // 2, cy], fill=LIME)


def card_block(d, x0, x1, top, ground, bay=10):
    """Six storeys of charcoal brick with paired windows and trim bands,
    glass shopfronts at ground level, a stepped parapet."""
    brick(d, x0, top, x1, ground)
    for i, bx in enumerate(range(x0, x1, bay * 2)):            # stepped roofline
        step = 2 if i % 2 else 0
        d.rectangle([bx, top - 3 + step, min(bx + bay * 2 - 1, x1), top], fill=BRICK_DK)
    for bx in range(x0 + 3, x1 - 5, bay):
        d.line([bx + 7, top + 3, bx + 7, ground - 12], fill=GRAY)
        for wy in range(top + 3, ground - 13, 7):
            window_pair(d, bx, wy, h=5)
    d.rectangle([x0, ground - 10, x1, ground], fill=NAVY)      # glass ground floor
    for gx in range(x0 + 2, x1, 7):
        d.line([gx, ground - 10, gx, ground], fill=GRAY)
    d.line([x0, ground - 11, x1, ground - 11], fill=GRAY)


def person(d, x, y, shirt):
    d.rectangle([x, y, x + 1, y + 1], fill=PEACH)
    d.rectangle([x - 1, y + 2, x + 2, y + 5], fill=shirt)
    d.line([x, y + 6, x, y + 7], fill=NAVY)
    d.line([x + 1, y + 6, x + 1, y + 7], fill=NAVY)


def draw_card() -> Image.Image:
    im = Image.new("RGB", (CARD_W, CARD_H), LBLUE)
    d = ImageDraw.Draw(im)
    ground = 64
    for cx, cy, w in ((150, 14, 30), (196, 8, 22)):
        d.ellipse([cx, cy, cx + w, cy + 7], fill=WHITE)
        d.ellipse([cx + w // 4, cy - 3, cx + w * 3 // 4, cy + 4], fill=WHITE)

    # right: the north part, set back (a little smaller and higher)
    card_block(d, 118, 226, 26, ground - 2)
    glass_tower(d, 160, 168, 22, ground - 2)
    # left: the south part, closer, with the tall glass stair tower
    card_block(d, 2, 108, 16, ground)
    glass_tower(d, 86, 104, 2, ground)
    # dining entrance and its wood canopy between the two
    d.rectangle([108, 44, 120, ground], fill=BRICK_DK)
    d.rectangle([104, 46, 126, 48], fill=BROWN)
    d.rectangle([110, 50, 118, ground], fill=LBLUE)
    d.line([114, 50, 114, ground], fill=NAVY)

    # plaza, wide steps down to the walkway, lawn
    d.rectangle([0, ground + 1, CARD_W, CARD_H], fill=LIME)
    d.rectangle([0, ground + 1, CARD_W, ground + 4], fill=ST)     # plaza
    for i in range(4):                                             # steps
        y = ground + 5 + i * 3
        d.rectangle([92 + i * 2, y, 190 + i * 6, y + 1], fill=ST_HI)
        d.line([92 + i * 2, y + 2, 190 + i * 6, y + 2], fill=ST_SH)
    d.polygon([(100, CARD_H), (124, ground + 17), (196, ground + 17), (228, CARD_H)], fill=ST)
    for x in range(0, 90, 6):
        d.point([x, ground + 10 + (x * 7) % 9], fill=GREEN)
    d.line([186, ground + 5, 200, ground + 17], fill=GRAY)         # handrail
    # outdoor tables and chairs on the plaza
    for tx in (16, 34, 52, 70):
        d.line([tx, ground - 2, tx, ground + 3], fill=NAVY)
        d.line([tx - 3, ground - 2, tx + 3, ground - 2], fill=NAVY)
    # birch trees
    for x, h, r in ((60, 30, 9), (78, 36, 10), (130, 26, 9), (182, 30, 12), (206, 34, 13), (222, 28, 10)):
        birch(d, x, ground + 2, h, r)
    # students outside the dining hall
    for i, shirt in enumerate((MAROON, RED, WHITE, DBLUE, ORANGE, MAROON)):
        person(d, 128 + i * 6, ground - 6, shirt)
    return im


def to_game_png(im: Image.Image, path: Path) -> None:
    """Save with fully transparent pixels as pure black (the game's
    transparent color) and everything else opaque."""
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = px[x, y]
            px[x, y] = (0, 0, 0, 0) if a < 128 else (r, g, b, 255)
    im.save(path)


if __name__ == "__main__":
    to_game_png(draw_map(), FOLDER / "map.png")
    to_game_png(draw_card(), FOLDER / "card.png")
    print("wrote", FOLDER / "map.png", "and", FOLDER / "card.png")
