"""First-draft art for Dealy Hall, drawn in code (decisions/0020).

Writes ../map.png (the building on the map) and ../card.png (the picture on
its building card), using only the game's palette (game/config.py).

Once someone retouches the PNGs in a drawing app, don't run this again:
it would overwrite their work. Keep it as a record of how v1 was made.

    uv run python assets/buildings/dealy_hall/options/draft_v1.py
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
OX, OY = (-v for v in META["sprite_offset"])  # footprint (0, 0) in the png


# ---------------------------------------------------------------- helpers
def fieldstone(d, x0, y0, x1, y1):
    """Dealy's dark fieldstone: charcoal with irregular lighter stones."""
    d.rectangle([x0, y0, x1, y1], fill=BRICK_DK)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            h = (x * 73 + y * 151 + (x * y) % 7) % 11
            if h in (0, 4):
                d.point([x, y], fill=BRICK)
            elif h == 7:
                d.point([x, y], fill=NAVY)


def quoin_window(d, x, y, w, h, arched=False):
    """Window with white stone quoins: a white frame with notched edges."""
    d.rectangle([x - 1, y - 1, x + w, y + h], fill=WHITE)
    for qy in range(y, y + h, 3):                  # alternating quoin blocks
        d.point([x - 2, qy], fill=ST_HI)
        d.point([x + w + 1, qy + 1], fill=ST_HI)
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=NAVY)
    if arched:
        d.point([x, y], fill=WHITE)
        d.point([x + w - 1, y], fill=WHITE)
    d.line([x + w // 2, y + 1, x + w // 2, y + h - 1], fill=DBLUE)
    d.point([x + 1, y + 1], fill=LBLUE)


# ---------------------------------------------------------------- map.png
def draw_map() -> Image.Image:
    cols = max(len(r) for r in META["footprint"])
    rows = len(META["footprint"])
    im = Image.new("RGBA", (cols * 16 + OX, rows * 16 + OY), CLEAR)
    d = ImageDraw.Draw(im)

    def R(x0, y0, x1, y1, fill):
        d.rectangle([x0 + OX, y0 + OY, x1 + OX, y1 + OY], fill=fill)

    def roof(x0, y0, x1, y1):
        R(x0, y0, x1, y1, ST)                       # light top storey, seen from above
        R(x0 + 2, y0 + 2, x1 - 2, y1 - 2, ROOF)
        for y in range(y0 + 6, y1 - 2, 6):
            for x in range(x0 + 3, x1 - 2):
                if (x + y) % 5:
                    d.point([x + OX, y + OY], fill=ROOF_SH)

    def south_wall(x0, x1, y0, y1):
        """Dark stone south face: light top storey band, white-trimmed windows,
        arched windows on the ground floor."""
        fieldstone(d, x0 + OX, y0 + OY, x1 + OX, y1 + OY)
        R(x0, y0, x1, y0 + 2, ST_HI)                # light top storey
        for wx in range(x0 + 3, x1 - 4, 7):
            d.point([wx + 2 + OX, y0 + 1 + OY], fill=NAVY)
            quoin_window(d, wx + 1 + OX, y0 + 5 + OY, 3, 3)
            quoin_window(d, wx + 1 + OX, y1 - 6 + OY, 3, 5, arched=True)
        R(x0, y1, x1, y1, ST_DK)

    # roofs: the north-south wing (cols 0-1) and the main block (rows 3-4)
    roof(0, 0, 31, 107)
    roof(32, 48, 95, 63)
    R(30, 48, 33, 63, ROOF)                          # join the two roofs
    R(32, 64, 33, 66, ROOF_SH)                       # shadow where they meet
    # rooftop details
    for vx, vy in ((10, 14), (14, 86), (60, 52), (80, 54)):
        R(vx, vy, vx + 5, vy + 4, GRAY)
        R(vx + 1, vy + 5, vx + 6, vy + 5, ROOF_SH)

    # south walls (what the camera sees)
    south_wall(32, 95, 64, 79)                       # main block
    south_wall(0, 31, 108, 127)                      # south end of the wing
    R(92, 48, 95, 79, BRICK)                         # east end, toward the drive

    # west façade along the wing's west edge: window bays, white quoins
    fieldstone(d, 0 + OX, 0 + OY, 4 + OX, 107 + OY)
    for wy in range(3, 104, 7):
        if not 44 <= wy <= 64:
            R(1, wy, 3, wy + 4, WHITE)
            R(2, wy + 1, 2, wy + 3, NAVY)

    # the columned portico (main entrance), facing west; steps down to the walk
    R(-6, 50, -1, 61, ST_HI)                         # steps
    for sy in range(52, 61, 2):
        R(-6, sy, -1, sy, ST)
    R(0, 46, 9, 65, WHITE)                           # portico: entablature + base
    R(1, 48, 8, 63, ST)
    for cy in (49, 61):                              # two columns, seen from above
        R(1, cy - 1, 3, cy + 1, WHITE)
        d.point([2 + OX, cy + OY], fill=ST_HI)
    R(4, 51, 7, 59, BROWN)                           # arched wooden door
    R(5, 52, 6, 58, NAVY)
    d.point([5 + OX, 55 + OY], fill=YELLOW)
    R(0, 46, 9, 46, ST_DK)

    # dining entrance on the east side of the wing
    R(28, 82, 31, 93, ST_HI)
    R(29, 84, 31, 92, MAROON)
    d.point([30 + OX, 88 + OY], fill=YELLOW)
    R(27, 81, 31, 82, ST_DK)
    return im


# ---------------------------------------------------------------- card.png
CARD_W, CARD_H = 228, 88


def draw_card() -> Image.Image:
    im = Image.new("RGB", (CARD_W, CARD_H), LBLUE)
    d = ImageDraw.Draw(im)
    top, ground = 8, 70

    # light top storey, then the dark fieldstone body
    d.rectangle([4, top, 224, top + 9], fill=ST_HI)
    d.line([4, top, 224, top], fill=ST)
    for wx in range(10, 220, 15):
        d.rectangle([wx, top + 3, wx + 7, top + 7], fill=NAVY)
        d.line([wx + 3, top + 3, wx + 3, top + 7], fill=GRAY)
    fieldstone(d, 0, top + 10, CARD_W - 1, ground)
    d.line([0, top + 10, CARD_W, top + 10], fill=ST_DK)
    d.line([0, top + 40, CARD_W, top + 40], fill=WHITE)          # string course

    bays = [x for x in range(6, 222, 16)]
    portico_x = 64                                                # the entrance bay
    for bx in bays:
        if portico_x - 14 <= bx <= portico_x + 26:
            continue
        quoin_window(d, bx + 3, top + 14, 8, 8, arched=True)     # 3rd floor, arched
        quoin_window(d, bx + 3, top + 28, 8, 8)                  # 2nd floor
        quoin_window(d, bx + 3, top + 44, 8, 14, arched=True)    # tall ground floor
    # the centre bays above the portico: paired windows
    for wx in (portico_x - 2, portico_x + 10, portico_x + 22):
        quoin_window(d, wx, top + 14, 6, 8, arched=True)
        quoin_window(d, wx, top + 28, 6, 8)
    # white trim bands framing the centre bays, as in the photo
    d.line([portico_x - 8, top + 10, portico_x - 8, ground], fill=WHITE)
    d.line([portico_x + 32, top + 10, portico_x + 32, ground], fill=WHITE)

    # the portico: entablature, two columns, arched door
    px0, px1 = portico_x - 4, portico_x + 28
    d.rectangle([px0 - 2, top + 38, px1 + 2, top + 42], fill=WHITE)
    d.line([px0 - 2, top + 42, px1 + 2, top + 42], fill=ST_SH)
    for i in range(px0 + 6, px1 - 4, 3):                          # "DEALY HALL" lettering
        d.point([i, top + 40], fill=ST_SH)
    d.rectangle([px0, top + 43, px1, ground], fill=ST_HI)
    for cx in (px0 + 2, px1 - 4):                                 # columns
        d.rectangle([cx, top + 43, cx + 2, ground], fill=WHITE)
        d.line([cx + 2, top + 43, cx + 2, ground], fill=ST)
    d.rectangle([px0 + 8, top + 50, px1 - 8, ground], fill=BROWN)  # arched door
    d.pieslice([px0 + 8, top + 46, px1 - 8, top + 58], 180, 360, fill=BROWN)
    d.rectangle([px0 + 10, top + 52, px1 - 10, ground], fill=NAVY)
    for gy in range(top + 53, ground, 4):
        d.point([px0 + 12, gy], fill=YELLOW)
        d.point([px1 - 12, gy], fill=YELLOW)

    # steps, path, hedges, lamps, trees
    for i in range(4):
        y = ground + 1 + i * 3
        d.rectangle([px0 - 4 - i * 3, y, px1 + 4 + i * 3, y + 2], fill=ST_HI if i % 2 == 0 else ST)
    d.rectangle([0, ground + 1, CARD_W, CARD_H], fill=GREEN)
    for i in range(4):                                            # redraw steps over the hedge band
        y = ground + 1 + i * 3
        d.rectangle([px0 - 4 - i * 3, y, px1 + 4 + i * 3, y + 2], fill=ST_HI if i % 2 == 0 else ST)
    d.polygon([(px0 - 16, CARD_H), (px0 - 13, ground + 13), (px1 + 13, ground + 13), (px1 + 16, CARD_H)], fill=ST)
    for hx in range(0, CARD_W, 6):                                # hedge tops
        if not px0 - 14 <= hx <= px1 + 14:
            d.ellipse([hx - 2, ground - 3, hx + 5, ground + 4], fill=GREEN)
            d.point([hx + 1, ground - 2], fill=LIME)
    for lx in (34, 168):                                          # lamp posts
        d.line([lx, ground - 22, lx, ground + 6], fill=NAVY)
        d.ellipse([lx - 2, ground - 27, lx + 2, ground - 21], fill=WHITE)
        d.line([lx - 2, ground - 21, lx + 2, ground - 21], fill=NAVY)
    # overhanging branches in the corners, as in the photo
    for cx, cy, r in ((-4, 2, 18), (14, -4, 14), (226, 0, 16), (210, -6, 12)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN)
        d.ellipse([cx - r // 2, cy - r // 2, cx + r // 3, cy + r // 3], fill=LIME)
    # two students walking by
    for sx, shirt in ((140, WHITE), (150, MAROON)):
        d.rectangle([sx, ground - 8, sx + 1, ground - 7], fill=PEACH)
        d.rectangle([sx - 1, ground - 6, sx + 2, ground - 2], fill=shirt)
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
