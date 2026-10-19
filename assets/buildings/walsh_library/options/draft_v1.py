"""First-draft art for Walsh Library, drawn in code (decisions/0020).

Writes ../map.png (the building on the map) and ../card.png (the picture on
its building card), using only the game's palette (game/config.py).

Once someone retouches the PNGs in a drawing app, don't run this again:
it would overwrite their work. Keep it as a record of how v1 was made.

    uv run python assets/buildings/walsh_library/options/draft_v1.py
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
 LIME, CYAN, GRAY, PINK, PEACH, ST_HI, ST, ST_SH, ST_DK, ROOF, ROOF_SH) = RGB[:22]
CLEAR = (0, 0, 0, 0)  # black = transparent in the game

META = json.loads((FOLDER / "building.json").read_text())
OFF_X, OFF_Y = (-v for v in META["sprite_offset"])  # footprint (0,0) in the png


# ---------------------------------------------------------------- helpers
def glass_arch(d, x, y, w, h):
    """Tall dark glass arch with mullions and a glint (top-left at x, y)."""
    r = w // 2
    d.rectangle([x, y + r, x + w - 1, y + h - 1], fill=NAVY)
    d.pieslice([x, y, x + w - 1, y + w - 1], 180, 360, fill=NAVY)
    d.line([x + r, y + 2, x + r, y + h - 1], fill=DBLUE)
    d.line([x, y + r + 3, x + w - 1, y + r + 3], fill=DBLUE)
    d.line([x + 1, y + r + 1, x + 1, y + r + 5], fill=LBLUE)


def window(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=NAVY)
    d.line([x + w // 2, y, x + w // 2, y + h - 1], fill=DBLUE)
    d.point([x, y], fill=LBLUE)
    d.line([x - 1, y + h, x + w, y + h], fill=ST_HI)  # sill


def coursing(d, x0, y0, x1, y1, line=ST_SH, step=4):
    """Ashlar stone courses: a faint line every `step` rows, staggered joints."""
    for i, y in enumerate(range(y0 + step - 1, y1, step)):
        d.line([x0, y, x1, y], fill=line)
        for x in range(x0 + (0 if i % 2 else 4), x1, 8):
            d.point([x, y - 1], fill=line)


# ---------------------------------------------------------------- map.png
FACADE_H = 32  # two storeys: windows above, tall glass arches below


def facade(d, x0, x1, y0):
    """North façade from x0 to x1 (exclusive), top at y0; one bay per tile."""
    d.rectangle([x0, y0, x1 - 1, y0 + FACADE_H - 1], fill=ST)
    coursing(d, x0, y0 + 4, x1 - 1, y0 + 12)
    d.line([x0, y0, x1 - 1, y0], fill=ST_DK)               # parapet top
    d.line([x0, y0 + 1, x1 - 1, y0 + 1], fill=ST_HI)
    d.line([x0, y0 + 3, x1 - 1, y0 + 3], fill=ST_SH)       # under the cornice
    d.line([x0, y0 + 12, x1 - 1, y0 + 12], fill=ST_HI)     # string course
    d.rectangle([x0, y0 + 13, x1 - 1, y0 + FACADE_H - 2], fill=ST_SH)
    for bx in range(x0, x1, 16):
        window(d, bx + 5, y0 + 5, 8, 5)
        glass_arch(d, bx + 4, y0 + 13, 10, 18)
        # stone pier, full height, with a cap rising above the parapet
        d.rectangle([bx, y0 - 3, bx + 2, y0 + FACADE_H - 2], fill=ST_HI)
        d.line([bx + 3, y0 + 2, bx + 3, y0 + FACADE_H - 2], fill=ST_SH)
        d.line([bx, y0 - 3, bx + 2, y0 - 3], fill=ST_DK)
    # end piers
    d.rectangle([x1 - 3, y0 - 3, x1 - 1, y0 + FACADE_H - 2], fill=ST_HI)
    d.line([x1 - 3, y0 - 3, x1 - 1, y0 - 3], fill=ST_DK)
    d.line([x1 - 1, y0, x1 - 1, y0 + FACADE_H - 2], fill=ST_SH)
    d.line([x0, y0 + FACADE_H - 1, x1 - 1, y0 + FACADE_H - 1], fill=ST_DK)  # base


def tower(d, x, top, w, base):
    """The slatted stone tower, standing on the roof."""
    shade = 6
    # shadow on the roof, cast to the south-east
    d.polygon([(x + w, top + 18), (x + w + 12, top + 26), (x + w + 12, base + 8),
               (x + 8, base + 8), (x, base)], fill=ROOF_SH)
    d.rectangle([x, top, x + w - 1, base], fill=ST_HI)
    d.rectangle([x + w - shade, top, x + w - 1, base], fill=ST_SH)
    coursing(d, x, top + 26, x + w - 1, base, line=ST)
    # open slatted top: dark gaps between stone fins
    for sx in range(x + 3, x + w - 3, 3):
        d.line([sx, top + 5, sx, top + 22], fill=NAVY)
    d.line([x, top + 23, x + w - 1, top + 23], fill=ST_DK)
    # corner piers and crown
    for px in (x, x + w - 3):
        d.rectangle([px, top - 3, px + 2, top + 24], fill=ST_HI if px == x else ST_SH)
    d.rectangle([x - 1, top - 1, x + w, top + 1], fill=ST_DK)
    d.line([x - 1, base, x + w, base], fill=ST_DK)
    d.rectangle([x - 1, top - 4, x + 3, top - 2], fill=ST_DK)
    d.rectangle([x + w - 4, top - 4, x + w, top - 2], fill=ST_DK)


def skylight(d, x, y, w, h):
    d.rectangle([x - 1, y - 1, x + w, y + h], fill=ST_DK)
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=LBLUE)
    for gx in range(x + 3, x + w - 1, 4):
        d.line([gx, y, gx, y + h - 1], fill=CYAN)
    d.line([x, y, x + w - 1, y], fill=WHITE)


def rooftop_unit(d, x, y, w, h):
    d.rectangle([x + 2, y + 2, x + w + 1, y + h + 1], fill=ROOF_SH)
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=GRAY)
    d.line([x, y, x + w - 1, y], fill=WHITE)
    for gx in range(x + 2, x + w - 1, 3):
        d.line([gx, y + 2, gx, y + h - 2], fill=ROOF)


def draw_map() -> Image.Image:
    cols = max(len(r) for r in META["footprint"])
    rows = len(META["footprint"])
    im = Image.new("RGBA", (cols * 16 + OFF_X, rows * 16 + OFF_Y), CLEAR)
    d = ImageDraw.Draw(im)

    def P(pts):
        return [(px + OFF_X, py + OFF_Y) for px, py in pts]

    W, H = cols * 16, rows * 16  # 160 x 144
    # whole outline: tower block (cols 0-3) from row 0, wing from row 1,
    # angled south-east end; the roof fills everything behind the façades
    outline = [(0, 0), (64, 0), (64, 16), (W, 16), (W, 112), (128, H), (0, H)]
    d.polygon(P(outline), fill=ST_DK)
    roof = [(2, 30), (62, 30), (62, 46), (W - 2, 46), (W - 2, 112), (127, H - 2), (2, H - 2)]
    d.polygon(P(roof), fill=ST)  # parapet
    inner = [(5, 32), (64, 32), (64, 48), (W - 5, 48), (W - 5, 111), (126, H - 5), (5, H - 5)]
    d.polygon(P(inner), fill=ROOF)
    # roof membrane seams
    for y in range(56, H - 6, 12):
        for x in range(6, W - 6):
            if im.getpixel((x + OFF_X, y + OFF_Y)) == ROOF + (255,):
                d.point((x + OFF_X, y + OFF_Y), fill=ROOF_SH)

    # the tower block is taller: its roof is lighter and throws a shadow
    d.rectangle(P([(5, 32), (60, 70)]), fill=ROOF)
    d.rectangle(P([(5, 71), (60, 72)]), fill=ST)
    d.rectangle(P([(61, 48), (63, 72)]), fill=ST)
    d.rectangle(P([(64, 48), (69, 76)]), fill=ROOF_SH)   # shadow to the east
    d.rectangle(P([(5, 73), (63, 77)]), fill=ROOF_SH)    # shadow to the south
    d.rectangle(P([(8, 36), (57, 67)]), fill=ROOF)
    skylight(d, *P([(14, 44)])[0], 36, 8)
    skylight(d, *P([(14, 56)])[0], 36, 6)

    # skylights over the reading rooms, rooftop units
    for sx in (22, 46, 70):
        skylight(d, *P([(sx, 96)])[0], 16, 7)
    rooftop_unit(d, *P([(136, 56)])[0], 12, 9)
    rooftop_unit(d, *P([(132, 92)])[0], 10, 8)
    rooftop_unit(d, *P([(20, 118)])[0], 9, 7)

    tower(d, *P([(96, 54)])[0], 22, 104 + OFF_Y)

    # the two north façades facing Walsh Lawn
    facade(d, 0 + OFF_X, 64 + OFF_X, 0 + OFF_Y)
    facade(d, 64 + OFF_X, W + OFF_X, 16 + OFF_Y)
    return im


# ---------------------------------------------------------------- card.png
CARD_W, CARD_H = 228, 88


def tree(d, cx, cy, r):
    d.rectangle([cx - 1, cy, cx + 1, cy + r + 3], fill=BROWN)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN)
    d.ellipse([cx - r + 2, cy - r + 1, cx + r // 2, cy + r // 3], fill=LIME)
    d.ellipse([cx - r + 4, cy - r + 3, cx + r // 3, cy - 1], fill=GREEN)


def cypress(d, cx, base, h):
    d.polygon([(cx, base - h), (cx - 3, base - 3), (cx - 2, base), (cx + 2, base),
               (cx + 3, base - 3)], fill=GREEN)
    d.line([cx - 1, base - h + 4, cx - 1, base - 3], fill=LIME)


def card_wall(d, x0, x1, top, ground, storeys, arch_row=False, bay=12):
    """A stone section: parapet with pier caps, rows of windows, and either
    windows or tall glass arches at ground level."""
    d.rectangle([x0, top, x1, ground], fill=ST)
    coursing(d, x0, top + 4, x1, ground, step=3)
    d.rectangle([x0, top - 6, x1, top - 1], fill=NAVY)            # glass penthouse behind the parapet
    d.line([x0, top - 6, x1, top - 6], fill=DBLUE)
    d.line([x0, top, x1, top], fill=ST_DK)
    d.line([x0, top + 1, x1, top + 1], fill=ST_HI)
    for bx in range(x0, x1 - 3, bay):
        d.rectangle([bx, top - 9, bx + 2, ground], fill=ST_HI)     # pier, cap above the roofline
        d.line([bx + 3, top + 2, bx + 3, ground], fill=ST_SH)
        d.line([bx, top - 9, bx + 2, top - 9], fill=ST_DK)
        for s in range(storeys):
            wy = top + 4 + s * 10
            window(d, bx + 5, wy, 5, 6)
        if arch_row:
            glass_arch(d, bx + 4, ground - 22, 7, 22)
    d.rectangle([x1 - 2, top - 9, x1, ground], fill=ST_HI)
    d.line([x1 - 2, top - 9, x1, top - 9], fill=ST_DK)


def draw_card() -> Image.Image:
    im = Image.new("RGB", (CARD_W, CARD_H), LBLUE)
    d = ImageDraw.Draw(im)
    ground = 66
    # sky: a few clouds
    for cx, cy, w in ((30, 10, 22), (170, 6, 28), (205, 16, 16)):
        d.ellipse([cx, cy, cx + w, cy + 6], fill=WHITE)
        d.ellipse([cx + w // 4, cy - 3, cx + w * 3 // 4, cy + 4], fill=WHITE)
    # trees at the edges, behind the building
    tree(d, 6, 34, 12)
    tree(d, 222, 30, 14)
    tree(d, 214, 46, 9)

    # the slatted tower behind the centre block
    tx, ttop, tw = 104, 6, 22
    d.rectangle([tx, ttop, tx + tw - 1, 40], fill=ST_HI)
    d.rectangle([tx + tw - 5, ttop, tx + tw - 1, 40], fill=ST_SH)
    for sx in range(tx + 3, tx + tw - 3, 3):
        d.line([sx, ttop + 5, sx, ttop + 20], fill=LBLUE)          # sky through the slats
        d.line([sx + 1, ttop + 5, sx + 1, ttop + 20], fill=NAVY)
    d.rectangle([tx - 1, ttop - 1, tx + tw, ttop + 1], fill=ST_DK)
    d.rectangle([tx - 1, ttop - 4, tx + 3, ttop - 2], fill=ST_DK)
    d.rectangle([tx + tw - 4, ttop - 4, tx + tw, ttop - 2], fill=ST_DK)
    d.line([tx, ttop + 21, tx + tw - 1, ttop + 21], fill=ST_DK)

    # left wing (east), three storeys of windows
    card_wall(d, 4, 64, 30, ground, 3)
    # centre: the curved front with tall glass arches (the entrances)
    card_wall(d, 60, 172, 34, ground, 1, arch_row=True, bay=14)
    # right section (west) steps forward: a little lower on the page
    card_wall(d, 168, 224, 30, ground + 2, 3)
    d.line([168, 30, 168, ground + 2], fill=ST_DK)
    d.line([64, 30, 64, ground], fill=ST_SH)

    # lawn, path, steps
    d.rectangle([0, ground + 1, CARD_W, CARD_H], fill=LIME)
    d.rectangle([0, ground + 3, CARD_W, ground + 3], fill=GREEN)
    for x in range(0, CARD_W, 5):
        d.point([x, ground + 8 + (x * 7) % 9], fill=GREEN)
        d.point([x + 2, ground + 14 + (x * 5) % 7], fill=GREEN)
    d.rectangle([62, ground, 170, ground + 2], fill=ST_HI)          # entrance steps
    d.line([62, ground + 2, 170, ground + 2], fill=ST_SH)
    for cx in (22, 44, 186, 206):
        cypress(d, cx, ground + 2, 16)
    for lx in (58, 176):                                             # lamp posts
        d.line([lx, ground - 12, lx, ground + 2], fill=NAVY)
        d.rectangle([lx - 1, ground - 15, lx + 1, ground - 12], fill=YELLOW)
    # a student walking up, for scale
    sx, sy = 140, ground + 6
    d.rectangle([sx, sy - 13, sx + 3, sy - 10], fill=PEACH)
    d.rectangle([sx, sy - 14, sx + 3, sy - 13], fill=BROWN)
    d.rectangle([sx - 1, sy - 9, sx + 4, sy - 3], fill=MAROON)
    d.rectangle([sx, sy - 2, sx + 1, sy], fill=NAVY)
    d.rectangle([sx + 2, sy - 2, sx + 3, sy], fill=NAVY)
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
