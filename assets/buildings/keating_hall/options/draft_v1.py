"""First-draft art for Keating Hall, in the shared house style
(decisions/0020, 0021). Writes ../map.png and ../card.png using only the
game's palette. Name plaque and door mats are added by the game.

Once someone retouches the PNGs in a drawing app, don't run this again.

    uv run python assets/buildings/keating_hall/options/draft_v1.py
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
sys.path.insert(0, str(FOLDER.parents[2]))
from game.config import palette  # noqa: E402

RGB = [((c >> 16) & 255, (c >> 8) & 255, c & 255) for c in palette()]
(BLACK, NAVY, MAROON, GREEN, BROWN, DBLUE, LBLUE, WHITE, RED, ORANGE, YELLOW,
 LIME, CYAN, GRAY, PINK, PEACH, ST_HI, ST, ST_SH, ST_DK, ROOF, ROOF_SH,
 BRICK, BRICK_DK, PBRICK, PBRICK_SH) = RGB
CLEAR = (0, 0, 0, 0)
META = json.loads((FOLDER / "building.json").read_text())
OY = -META["sprite_offset"][1]          # footprint y 0 is image y OY


# ---------------------------------------------------------------- helpers
def tan_stone(d, x0, y0, x1, y1, band=0):
    """Keating's warm tan fieldstone: blocks of mixed tan and brown-gray
    in light mortar, with pale limestone bands every `band` px (the
    tower's striped look)."""
    d.rectangle([x0, y0, x1, y1], fill=ST)                    # mortar
    for row, y in enumerate(range(y0, y1 + 1, 4)):
        off = (row % 2) * 3
        for x in range(x0 - off, x1 + 1, 6):
            h = (x * 7 + y * 13 + row) % 9
            col = ST_DK if h == 0 else (ST if h in (3, 6) else ST_SH)
            d.rectangle([max(x, x0), y, min(x + 4, x1), min(y + 2, y1)], fill=col)
    if band:
        for y in range(y0 + band, y1, band):
            d.line([x0, y, x1, y], fill=ST_HI)


def battlements(d, x0, x1, y, h=3, step=4, fill=ST, top=ST_HI):
    """Crenellated parapet: merlons rising above y."""
    d.rectangle([x0, y, x1, y + 2], fill=fill)
    for x in range(x0, x1 + 1, step * 2):
        d.rectangle([x, y - h, min(x + step - 1, x1), y], fill=fill)
        d.line([x, y - h, min(x + step - 1, x1), y - h], fill=top)


def window(d, x, y, w=8, h=8):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=WHITE)
    d.rectangle([x + 1, y + 1, x + w // 2 - 1, y + h - 2], fill=LBLUE)
    d.rectangle([x + w // 2 + 1, y + 1, x + w - 2, y + h - 2], fill=LBLUE)


def gothic_window(d, x, y, w, h, tracery=True):
    """Pointed-arch window with white tracery."""
    d.rectangle([x - 1, y + w // 2 - 1, x + w, y + h], fill=ST_HI)
    d.polygon([(x - 1, y + w // 2), (x + w // 2, y - 2), (x + w, y + w // 2)], fill=ST_HI)
    d.rectangle([x, y + w // 2, x + w - 1, y + h - 1], fill=NAVY)
    d.polygon([(x, y + w // 2), (x + (w - 1) / 2, y), (x + w - 1, y + w // 2)], fill=NAVY)
    if tracery:
        for mx in range(x + 2, x + w - 1, 3):
            d.line([mx, y + w // 2 - 1, mx, y + h - 1], fill=WHITE)
        d.line([x, y + w // 2 + 3, x + w - 1, y + w // 2 + 3], fill=WHITE)
        d.point([x + w // 2, y + 2], fill=WHITE)


def banner(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + 1], fill=ST_HI)
    d.rectangle([x, y + 2, x + w - 1, y + h - 1], fill=MAROON)
    d.polygon([(x, y + h), (x + w - 1, y + h), (x + w // 2, y + h - 3)], fill=ST_SH)
    d.rectangle([x + w // 2 - 1, y + 7, x + w // 2, y + 9], fill=WHITE)
    d.line([x + 1, y + 3, x + 1, y + h - 3], fill=PINK)


# ---------------------------------------------------------------- map.png
def draw_map() -> Image.Image:
    W = len(META["footprint"][0]) * 16                    # 160
    H = len(META["footprint"]) * 16 + OY                  # 112 + 10
    im = Image.new("RGBA", (W, H), CLEAR)
    d = ImageDraw.Draw(im)
    wall_top = OY + 58                                    # front wall from here down
    tx0, tx1 = 60, 99                                     # the tower

    # roof of the wings: flat, stone-edged, with the parapet along the front
    d.rectangle([0, OY, W - 1, wall_top - 1], fill=ST)
    d.rectangle([3, OY + 3, W - 4, wall_top - 7], fill=ROOF)
    for y in range(OY + 10, wall_top - 8, 8):
        d.line([4, y, W - 5, y], fill=ROOF_SH)
    for ux, uy in ((18, OY + 12), (128, OY + 20)):
        d.rectangle([ux + 1, uy + 1, ux + 10, uy + 6], fill=ROOF_SH)
        d.rectangle([ux, uy, ux + 9, uy + 5], fill=GRAY)
    d.rectangle([3, wall_top - 6, W - 4, wall_top - 1], fill=ROOF_SH)   # parapet shadow
    battlements(d, 0, W - 1, wall_top - 3)

    # front wall
    tan_stone(d, 0, wall_top, W - 1, H - 1)
    d.line([0, wall_top, W - 1, wall_top], fill=ST_HI)
    d.line([0, wall_top + 32, W - 1, wall_top + 32], fill=ST_HI)          # string course
    for x0, x1 in ((5, 42), (122, 159)):
        for bx in range(x0, x1 - 6, 10):
            window(d, bx, wall_top + 6, 7, 8)
            window(d, bx, wall_top + 20, 7, 8)
            gothic_window(d, bx, wall_top + 37, 7, 14)
    # buttresses at the wing ends and beside the tower
    for bx in (0, 51, 105, W - 4):
        d.rectangle([bx, wall_top - 2, bx + 3, H - 1], fill=ST)
        d.line([bx + 3, wall_top, bx + 3, H - 1], fill=ST_DK)
    # maroon banners beside the tower
    banner(d, 42, wall_top + 2, 6, 26)
    banner(d, 112, wall_top + 2, 6, 26)
    # corner turrets on the wings
    for cx in (0, W - 12):
        tan_stone(d, cx, wall_top - 18, cx + 11, wall_top + 4)
        battlements(d, cx, cx + 11, wall_top - 18, h=3, step=3)
        d.rectangle([cx, wall_top - 18, cx + 11, wall_top + 4], outline=NAVY)

    # the tower: banded stone from the ground to above the roof
    d.polygon([(tx1 + 1, OY + 4), (tx1 + 9, OY + 10), (tx1 + 9, wall_top - 4),
               (tx1 + 1, wall_top - 4)], fill=ROOF_SH)                  # its shadow on the roof
    tan_stone(d, tx0, 6, tx1, H - 1, band=6)
    for px in (tx0, tx1 - 6):                                           # corner turrets
        tan_stone(d, px, 0, px + 6, wall_top, band=5)
        d.rectangle([px - 1, 0, px + 7, 2], fill=ST_HI)
        d.rectangle([px, 0, px + 6, wall_top], outline=NAVY)
    battlements(d, tx0 + 7, tx1 - 7, 7, h=3, step=3)
    gothic_window(d, 72, 14, 16, 30)                                    # the great tracery window
    d.ellipse([75, 46, 84, 55], fill=ST_HI)                             # carved crest
    d.ellipse([77, 48, 82, 53], fill=ST)
    gothic_window(d, 70, wall_top + 2, 20, 12)                          # window above the entrance
    # the pointed-arch entrance (the plaque goes just above it)
    d.rectangle([69, wall_top + 26, 90, H - 1], fill=ST_HI)
    d.polygon([(69, wall_top + 30), (79.5, wall_top + 22), (90, wall_top + 30)], fill=ST_HI)
    d.rectangle([71, wall_top + 30, 88, H - 1], fill=NAVY)
    d.polygon([(71, wall_top + 30), (79.5, wall_top + 24), (88, wall_top + 30)], fill=NAVY)
    d.rectangle([75, wall_top + 40, 84, H - 1], fill=BROWN)              # the doors inside
    d.line([79, wall_top + 40, 79, H - 1], fill=NAVY)

    # outline: wings, then the tower over them
    d.rectangle([0, OY, W - 1, H - 1], outline=NAVY)
    d.line([tx0 - 1, 6, tx0 - 1, H - 1], fill=NAVY)
    d.line([tx1 + 1, 6, tx1 + 1, H - 1], fill=NAVY)
    return im


# ---------------------------------------------------------------- card.png
CARD_W, CARD_H = 228, 88


def draw_card() -> Image.Image:
    im = Image.new("RGB", (CARD_W, CARD_H), LBLUE)
    d = ImageDraw.Draw(im)
    ground = 70
    for cx, cy, w in ((20, 10, 26), (176, 14, 30)):
        d.ellipse([cx, cy, cx + w, cy + 6], fill=WHITE)
        d.ellipse([cx + w // 4, cy - 3, cx + w * 3 // 4, cy + 4], fill=WHITE)
    # wings with crenellated parapets and corner turrets
    tan_stone(d, 18, 30, 210, ground)
    battlements(d, 18, 210, 30, h=3, step=4)
    for tx in (18, 198):
        tan_stone(d, tx, 22, tx + 12, ground)
        battlements(d, tx, tx + 12, 22, h=3, step=3)
    d.line([18, 54, 210, 54], fill=ST_HI)
    for x0, x1 in ((22, 92), (136, 206)):
        for bx in range(x0, x1 - 6, 11):
            window(d, bx, 35, 8, 7)
            window(d, bx, 44, 8, 7)
            gothic_window(d, bx, 57, 8, 11)
    banner(d, 94, 34, 6, 26)
    banner(d, 128, 34, 6, 26)
    # the tower
    tan_stone(d, 100, 6, 127, ground, band=5)
    for px in (100, 122):
        tan_stone(d, px, 0, px + 5, 40, band=4)
        d.rectangle([px - 1, 0, px + 6, 1], fill=ST_HI)
    battlements(d, 106, 121, 6, h=2, step=3)
    gothic_window(d, 108, 10, 12, 20)
    d.ellipse([110, 33, 117, 40], fill=ST_HI)
    gothic_window(d, 106, 42, 16, 9)
    d.rectangle([107, 55, 120, ground], fill=ST_HI)
    d.polygon([(107, 58), (113.5, 52), (120, 58)], fill=ST_HI)
    d.rectangle([109, 58, 118, ground], fill=NAVY)
    d.polygon([(109, 58), (113.5, 54), (118, 58)], fill=NAVY)
    # steps, wood rail fence, lawn, trees, students
    for i in range(4):
        y = ground + 1 + i * 2
        d.rectangle([98 - i * 6, y, 129 + i * 6, y + 1], fill=ST_HI if i % 2 == 0 else ST)
    d.rectangle([0, ground + 9, CARD_W, CARD_H], fill=LIME)
    d.rectangle([0, ground + 1, 97 - 18, ground + 8], fill=GREEN)        # hedges
    d.rectangle([129 + 18, ground + 1, CARD_W, ground + 8], fill=GREEN)
    d.line([0, ground + 10, CARD_W, ground + 10], fill=BROWN)            # rail fence
    for fx in range(4, CARD_W, 14):
        d.line([fx, ground + 8, fx, ground + 12], fill=BROWN)
    for x in range(0, CARD_W, 6):
        d.point([x, ground + 15 + (x * 7) % 4], fill=GREEN)
    for cx, cy, r, col in ((6, 30, 16, ORANGE), (18, 44, 10, GREEN), (222, 28, 15, GREEN),
                           (210, 44, 10, ORANGE)):
        d.line([cx, cy, cx, ground + 8], fill=BROWN)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        d.ellipse([cx - r + 3, cy - r + 2, cx, cy - 2], fill=YELLOW if col == ORANGE else LIME)
    for sx, shirt in ((60, MAROON), (66, WHITE), (150, RED), (172, DBLUE), (112, MAROON)):
        y = ground + 13 if sx != 112 else ground - 1
        d.rectangle([sx, y - 6, sx + 1, y - 5], fill=PEACH)
        d.rectangle([sx - 1, y - 4, sx + 2, y], fill=shirt)
    return im


def save(im: Image.Image, path: Path) -> None:
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = px[x, y]
            px[x, y] = (0, 0, 0, 0) if a < 128 else (r, g, b, 255)
    im.save(path)


if __name__ == "__main__":
    save(draw_map(), FOLDER / "map.png")
    save(draw_card(), FOLDER / "card.png")
    print("wrote map.png and card.png")
