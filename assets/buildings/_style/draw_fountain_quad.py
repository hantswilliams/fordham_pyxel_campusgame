"""First drafts (decisions/0022) for the fountain quad: Cunniffe House,
Hughes Hall and the Carolyn Dursi Cunniffe Fountain, in the house style.
Writes map.png and card.png in each of their folders, using only the
game's palette. Plaques and door mats are added by the game.

Once someone retouches a PNG by hand, don't run this again for it.

    uv run python assets/buildings/_style/draw_fountain_quad.py
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
BUILDINGS = HERE.parent
sys.path.insert(0, str(BUILDINGS.parents[1]))
from game.config import palette  # noqa: E402

RGB = [((c >> 16) & 255, (c >> 8) & 255, c & 255) for c in palette()]
(BLACK, NAVY, MAROON, GREEN, BROWN, DBLUE, LBLUE, WHITE, RED, ORANGE, YELLOW,
 LIME, CYAN, GRAY, PINK, PEACH, ST_HI, ST, ST_SH, ST_DK, ROOF, ROOF_SH,
 BRICK, BRICK_DK, PBRICK, PBRICK_SH) = RGB
CLEAR = (0, 0, 0, 0)
CARD_W, CARD_H = 228, 88


def meta(bid):
    return json.loads((BUILDINGS / bid / "building.json").read_text())


# ---------------------------------------------------------------- textures
def pink_brick(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=PBRICK)
    for i, y in enumerate(range(y0 + 2, y1, 3)):
        d.line([x0, y, x1, y], fill=PBRICK_SH)
        for x in range(x0 + (i % 2) * 3, x1, 6):
            d.point([x, y - 1], fill=PBRICK_SH)


def stucco(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=ST_DK)
    for y in range(y0, y1 + 1, 2):
        for x in range(x0 + (y // 2) % 3, x1 + 1, 5):
            d.point([x, y], fill=ROOF_SH)


def fieldstone(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=BRICK_DK)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            h = (x * 73 + y * 151 + (x * y) % 7) % 11
            if h in (0, 4):
                d.point([x, y], fill=BRICK)
            elif h == 7:
                d.point([x, y], fill=ROOF_SH)


def plaza(d, x0, y0, w, h):
    """The plaza tile's pavers (game/gfx/placeholder_art.py _plaza)."""
    for ty in range(y0, y0 + h, 16):
        for tx in range(x0, x0 + w, 16):
            d.rectangle([tx, ty, tx + 15, ty + 15], fill=ST_HI)
            for row in range(2):
                by = ty + row * 8 + 7
                d.line([tx, by, tx + 15, by], fill=ST)
                off = 0 if row == 0 else 6
                for bx in range(off, 16, 12):
                    d.line([tx + bx, by - 7, tx + bx, by - 1], fill=ST)


# ---------------------------------------------------------------- details
def framed_window(d, x, y, w, h, frame=ST_HI, arched=False):
    """Window with a cream stone surround (Cunniffe) or white trim (Hughes)."""
    d.rectangle([x - 1, y - 1, x + w, y + h], fill=frame)
    if arched:
        d.pieslice([x - 1, y - 3, x + w, y + 4], 180, 360, fill=frame)
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=NAVY)
    if arched:
        d.pieslice([x, y - 2, x + w - 1, y + 3], 180, 360, fill=NAVY)
    d.line([x + w // 2, y, x + w // 2, y + h - 1], fill=WHITE if frame != WHITE else LBLUE)
    if w >= 5:
        d.rectangle([x + 1, y + 1, x + w // 2 - 1, y + h - 2], fill=LBLUE)
        d.rectangle([x + w // 2 + 1, y + 1, x + w - 2, y + h - 2], fill=LBLUE)


def cupola(d, cx, top, w, h):
    """White octagonal cupola with two windows and a green cross."""
    x0 = cx - w // 2
    d.rectangle([x0 - 1, top + 3, x0 + w, top + h + 1], fill=NAVY)
    d.rectangle([x0, top + 4, x0 + w - 1, top + h], fill=WHITE)
    d.rectangle([x0 + w - 3, top + 4, x0 + w - 1, top + h], fill=ST_HI)   # shaded facet
    d.rectangle([x0 - 1, top + 2, x0 + w, top + 4], fill=ST_DK)            # roof cap
    for wx in (x0 + 3, x0 + w - 7):
        d.rectangle([wx, top + 7, wx + 3, top + h - 2], fill=LBLUE)
        d.line([wx, top + 7, wx + 3, top + 7], fill=NAVY)
    d.line([cx, top - 3, cx, top + 2], fill=GREEN)                          # the cross
    d.line([cx - 1, top - 2, cx + 1, top - 2], fill=GREEN)


# ---------------------------------------------------------------- Cunniffe
def cunniffe_map():
    m = meta("cunniffe_house")
    OY = -m["sprite_offset"][1]
    W, H = 96, 64 + OY
    im = Image.new("RGBA", (W, H), CLEAR)
    d = ImageDraw.Draw(im)
    y = lambda v: v + OY                                                    # noqa: E731
    # pink-brick wings: low roofs, then walls with white trim
    for x0, x1 in ((0, 31), (64, 95)):
        d.rectangle([x0, y(0), x1, y(33)], fill=ROOF_SH)
        for ry in range(y(4), y(33), 6):
            d.line([x0 + 2, ry, x1 - 2, ry], fill=ROOF)
        d.line([x0, y(34), x1, y(34)], fill=NAVY)                         # eave
        d.rectangle([x0, y(35), x1, y(37)], fill=WHITE)                    # white cornice
        pink_brick(d, x0, y(38), x1, y(63))
        for wx in range(x0 + 4, x1 - 4, 9):
            framed_window(d, wx, y(41), 5, 6, frame=WHITE)
            framed_window(d, wx, y(53), 5, 8, frame=WHITE, arched=True)
    # centre block: taller, gray stucco, white top storey and dentil cornice
    d.rectangle([32, y(-2), 63, y(5)], fill=ROOF)
    d.rectangle([32, y(6), 63, y(17)], fill=WHITE)                         # top storey
    d.line([32, y(6), 63, y(6)], fill=ST_HI)
    for wx in (36, 46, 56):
        d.rectangle([wx, y(10), wx + 3, y(13)], fill=NAVY)
        d.point([wx, y(10)], fill=LBLUE)
    d.rectangle([32, y(18), 63, y(20)], fill=ST_HI)                        # dentil cornice
    for dx in range(33, 63, 2):
        d.point([dx, y(19)], fill=ST)
    stucco(d, 32, y(21), 63, y(63))
    for wx in (34, 57):
        framed_window(d, wx, y(24), 5, 7)
        framed_window(d, wx, y(46), 5, 9)
    # the arched front door with its iron grille, and two lanterns
    d.rectangle([41, y(45), 54, y(63)], fill=ST_HI)
    d.pieslice([41, y(41), 54, y(50)], 180, 360, fill=ST_HI)
    d.rectangle([43, y(47), 52, y(63)], fill=NAVY)
    d.pieslice([43, y(43), 52, y(51)], 180, 360, fill=NAVY)
    for gx in range(44, 52, 2):
        d.line([gx, y(46), gx, y(63)], fill=DBLUE)
    for lx in (39, 56):
        d.rectangle([lx - 1, y(49), lx + 1, y(52)], fill=YELLOW)
        d.point([lx, y(48)], fill=NAVY)
    # cupola on the roof
    cupola(d, 48, 3, 16, 16)
    # outline: wings and centre block
    d.rectangle([0, y(0), W - 1, H - 1], outline=NAVY)
    d.line([32, y(-2), 32, y(0)], fill=NAVY)
    d.line([63, y(-2), 63, y(0)], fill=NAVY)
    d.line([32, y(-2), 63, y(-2)], fill=NAVY)
    return im


def cunniffe_card():
    im = Image.new("RGB", (CARD_W, CARD_H), LBLUE)
    d = ImageDraw.Draw(im)
    ground = 72
    for cx, cy, w in ((150, 10, 26), (196, 18, 20)):
        d.ellipse([cx, cy, cx + w, cy + 6], fill=WHITE)
    # bare trees behind
    for tx in (14, 214):
        d.line([tx, 10, tx, ground], fill=BROWN)
        for i in range(5):
            d.line([tx, 20 + i * 8, tx + (-1) ** i * (14 - i * 2), 12 + i * 8], fill=BROWN)
    # wings
    for x0, x1 in ((6, 64), (164, 222)):
        d.rectangle([x0, 34, x1, 37], fill=WHITE)
        pink_brick(d, x0, 38, x1, ground)
        for wx in range(x0 + 6, x1 - 6, 14):
            framed_window(d, wx, 42, 7, 9, frame=WHITE)
            framed_window(d, wx, 58, 7, 11, frame=WHITE, arched=True)
    # centre block
    d.rectangle([64, 16, 164, 31], fill=WHITE)
    for wx in range(72, 160, 18):
        d.rectangle([wx, 21, wx + 6, 25], fill=NAVY)
        d.point([wx, 21], fill=LBLUE)
    d.rectangle([62, 31, 166, 34], fill=ST_HI)
    for dx in range(63, 166, 2):
        d.point([dx, 32], fill=ST)
    stucco(d, 64, 35, 164, ground)
    for wx in (72, 92, 130, 150):
        framed_window(d, wx, 40, 7, 11)
        framed_window(d, wx, 56, 7, 12)
    d.rectangle([107, 52, 121, ground], fill=ST_HI)
    d.pieslice([107, 47, 121, 58], 180, 360, fill=ST_HI)
    d.rectangle([109, 54, 119, ground], fill=NAVY)
    d.pieslice([109, 49, 119, 58], 180, 360, fill=NAVY)
    for gx in range(110, 119, 2):
        d.line([gx, 52, gx, ground], fill=DBLUE)
    cupola(d, 114, 2, 22, 14)
    # hedges, lamp post, lawn
    d.rectangle([0, ground - 4, CARD_W, ground + 2], fill=GREEN)
    for hx in range(0, CARD_W, 7):
        d.point([hx + 2, ground - 3], fill=LIME)
    d.rectangle([0, ground + 3, CARD_W, CARD_H], fill=LIME)
    for x in range(0, CARD_W, 6):
        d.point([x, ground + 8 + (x * 7) % 6], fill=GREEN)
    d.line([40, ground - 22, 40, ground + 6], fill=NAVY)
    d.ellipse([37, ground - 28, 43, ground - 21], fill=NAVY)
    d.rectangle([39, ground - 26, 41, ground - 23], fill=YELLOW)
    return im


# ---------------------------------------------------------------- Hughes
def hughes_map():
    W, H = 80, 80
    im = Image.new("RGBA", (W, H), CLEAR)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, 13], fill=CYAN)                             # sloped glass roof
    for gx in range(2, W, 4):
        d.line([gx, 1, gx, 12], fill=DBLUE)
    d.line([0, 1, W - 1, 1], fill=WHITE)
    d.line([0, 7, W - 1, 7], fill=LBLUE)
    d.rectangle([0, 14, W - 1, 16], fill=WHITE)                            # white cornice
    d.line([0, 17, W - 1, 17], fill=ST_SH)
    fieldstone(d, 0, 18, W - 1, H - 1)
    for row_y in (21, 35):
        for wx in (4, 19, 34, 49, 64):
            framed_window(d, wx, row_y, 9, 9, frame=WHITE, arched=True)
    for wx in (4, 66):
        framed_window(d, wx, 49, 9, 9, frame=WHITE, arched=True)
    d.rectangle([0, 61, W - 1, 62], fill=WHITE)                            # string course
    for wx in (4, 66):
        framed_window(d, wx, 66, 9, 10, frame=WHITE)
    # glass entrance under the teal glass canopy
    d.rectangle([29, 66, 50, H - 1], fill=NAVY)
    d.rectangle([30, 67, 49, H - 1], fill=LBLUE)
    for gx in range(33, 49, 5):
        d.line([gx, 67, gx, H - 1], fill=DBLUE)
    d.line([31, 68, 31, H - 2], fill=WHITE)
    d.rectangle([24, 62, 55, 65], fill=CYAN)
    d.line([24, 62, 55, 62], fill=WHITE)
    d.line([24, 66, 55, 66], fill=NAVY)
    d.rectangle([0, 0, W - 1, H - 1], outline=NAVY)
    return im


def hughes_card():
    im = Image.new("RGB", (CARD_W, CARD_H), LBLUE)
    d = ImageDraw.Draw(im)
    ground = 74
    d.polygon([(20, 14), (34, 4), (194, 4), (208, 14)], fill=CYAN)        # glass roof
    for gx in range(36, 194, 6):
        d.line([gx, 5, gx - 2, 13], fill=DBLUE)
    d.line([34, 4, 194, 4], fill=WHITE)
    d.rectangle([16, 14, 212, 17], fill=WHITE)
    d.line([16, 18, 212, 18], fill=ST_SH)
    fieldstone(d, 18, 19, 210, ground)
    for row_y in (22, 36, 50):
        for wx in range(24, 204, 18):
            if row_y == 50 and 84 <= wx <= 132:
                continue
            framed_window(d, wx, row_y, 8, 9, frame=WHITE, arched=True)
    d.rectangle([18, 62, 210, 63], fill=WHITE)
    for wx in (26, 46, 66, 150, 170, 190):
        framed_window(d, wx, 66, 8, 7, frame=WHITE)
    # entrance, canopy, lettering
    d.rectangle([96, 64, 132, ground], fill=NAVY)
    d.rectangle([97, 65, 131, ground], fill=LBLUE)
    for gx in range(101, 131, 6):
        d.line([gx, 65, gx, ground], fill=DBLUE)
    d.rectangle([88, 59, 140, 62], fill=CYAN)
    d.line([88, 59, 140, 59], fill=WHITE)
    for lx in range(100, 129, 4):                                          # HUGHES HALL letters
        d.rectangle([lx, 55, lx + 2, 57], fill=GRAY)
    # Ram statue on its plinth, hedges, a young tree, lawn
    d.rectangle([30, ground - 2, 52, ground + 3], fill=ST)
    d.ellipse([33, ground - 12, 47, ground - 3], fill=DBLUE)              # body
    d.rectangle([35, ground - 4, 36, ground - 1], fill=DBLUE)
    d.rectangle([44, ground - 4, 45, ground - 1], fill=DBLUE)
    d.ellipse([44, ground - 17, 51, ground - 10], fill=DBLUE)             # head
    d.arc([46, ground - 19, 53, ground - 12], 270, 180, fill=GRAY)        # curled horn
    d.rectangle([56, ground - 3, CARD_W, ground + 2], fill=GREEN)
    d.rectangle([0, ground - 3, 28, ground + 2], fill=GREEN)
    d.rectangle([0, ground + 3, CARD_W, CARD_H], fill=LIME)
    d.line([170, 34, 170, ground], fill=BROWN)
    d.ellipse([158, 24, 182, 50], fill=GREEN)
    d.ellipse([162, 27, 172, 38], fill=LIME)
    return im


# ---------------------------------------------------------------- fountain
def fountain_map():
    m = meta("cunniffe_fountain")
    OY = -m["sprite_offset"][1]
    W, H = 32, 32 + OY
    im = Image.new("RGBA", (W, H), CLEAR)
    d = ImageDraw.Draw(im)
    plaza(d, 0, OY, 32, 32)                                                # paving round the basin
    d.ellipse([0, OY + 4, 31, OY + 30], fill=NAVY)                         # basin rim
    d.ellipse([1, OY + 5, 30, OY + 29], fill=ST)
    d.ellipse([3, OY + 7, 28, OY + 27], fill=CYAN)                         # water
    for wx, wy in ((6, OY + 15), (20, OY + 20), (10, OY + 23), (22, OY + 11)):
        d.line([wx, wy, wx + 3, wy], fill=LBLUE)
    d.arc([1, OY + 5, 30, OY + 29], 180, 360, fill=ST_HI)
    # the tiered bronze fountain
    d.rectangle([14, OY + 6, 17, OY + 22], fill=DBLUE)                     # column
    d.ellipse([12, OY + 19, 19, OY + 24], fill=NAVY)                       # base
    d.ellipse([5, OY + 4, 26, OY + 10], fill=NAVY)                         # lower bowl
    d.ellipse([6, OY + 4, 25, OY + 8], fill=DBLUE)
    d.line([7, OY + 5, 24, OY + 5], fill=GRAY)
    d.rectangle([14, 6, 17, OY + 5], fill=DBLUE)
    d.ellipse([9, 6, 22, 11], fill=NAVY)                                   # upper bowl
    d.line([10, 7, 21, 7], fill=GRAY)
    d.rectangle([15, 1, 16, 6], fill=DBLUE)                                # finial
    d.point([15, 0], fill=GRAY)
    # falling water
    for sx in (8, 23):
        for sy in range(OY + 10, OY + 17, 2):
            d.point([sx, sy], fill=WHITE)
    for sx in (10, 21):
        for sy in range(12, OY + 4, 2):
            d.point([sx, sy], fill=LBLUE)
    d.point([15, 0], fill=WHITE)
    return im


def fountain_card():
    im = Image.new("RGB", (CARD_W, CARD_H), ST_DK)
    d = ImageDraw.Draw(im)
    stucco(d, 0, 0, 160, 64)                                               # Cunniffe behind
    pink_brick(d, 160, 0, CARD_W - 1, 64)
    for wx in (14, 50, 110, 140):
        framed_window(d, wx, 6, 9, 14)
        framed_window(d, wx, 34, 9, 18)
    framed_window(d, 186, 30, 9, 20, frame=WHITE, arched=True)
    d.rectangle([76, 34, 94, 64], fill=ST_HI)                              # the front door
    d.rectangle([78, 36, 92, 64], fill=NAVY)
    for gx in range(79, 92, 2):
        d.line([gx, 36, gx, 64], fill=DBLUE)
    # trees framing it
    for cx, cy, r in ((14, 30, 22), (214, 22, 26)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN)
        d.ellipse([cx - r + 6, cy - r + 4, cx, cy - 4], fill=LIME)
    # hedges with mums, benches, paving
    d.rectangle([0, 58, CARD_W, 68], fill=GREEN)
    for mx in (34, 44, 150, 162, 172):
        d.ellipse([mx, 60, mx + 8, 67], fill=YELLOW)
    d.rectangle([0, 69, CARD_W, CARD_H], fill=ST_HI)
    for y in range(72, CARD_H, 5):
        d.line([0, y, CARD_W, y], fill=ST)
    for bx in (6, 196):
        d.rectangle([bx, 62, bx + 22, 64], fill=BROWN)
        d.rectangle([bx, 66, bx + 22, 68], fill=BROWN)
        d.line([bx + 2, 68, bx + 2, 72], fill=NAVY)
        d.line([bx + 20, 68, bx + 20, 72], fill=NAVY)
    # the fountain: basin, tiers, column, finial, water
    cx = 114
    d.ellipse([cx - 50, 70, cx + 50, 86], fill=NAVY)
    d.ellipse([cx - 48, 70, cx + 48, 82], fill=DBLUE)
    d.rectangle([cx - 4, 34, cx + 4, 76], fill=NAVY)
    d.ellipse([cx - 28, 40, cx + 28, 50], fill=NAVY)
    d.ellipse([cx - 26, 40, cx + 26, 46], fill=DBLUE)
    d.line([cx - 24, 42, cx + 24, 42], fill=GRAY)
    d.rectangle([cx - 3, 12, cx + 3, 40], fill=NAVY)
    d.ellipse([cx - 16, 14, cx + 16, 21], fill=NAVY)
    d.line([cx - 14, 16, cx + 14, 16], fill=GRAY)
    d.rectangle([cx - 1, 2, cx + 1, 14], fill=NAVY)
    d.ellipse([cx - 3, 0, cx + 3, 4], fill=GRAY)
    for sx in (cx - 26, cx + 26):
        for sy in range(48, 74, 3):
            d.point([sx, sy], fill=WHITE)
    for sx in (cx - 15, cx + 15):
        for sy in range(20, 42, 3):
            d.point([sx, sy], fill=LBLUE)
    return im


def save(im, path):
    im = im.convert("RGBA")
    px = im.load()
    for yy in range(im.size[1]):
        for xx in range(im.size[0]):
            r, g, b, a = px[xx, yy]
            px[xx, yy] = (0, 0, 0, 0) if a < 128 else (r, g, b, 255)
    im.save(path)


if __name__ == "__main__":
    for bid, mp, card in (("cunniffe_house", cunniffe_map, cunniffe_card),
                          ("hughes_hall", hughes_map, hughes_card),
                          ("cunniffe_fountain", fountain_map, fountain_card)):
        save(mp(), BUILDINGS / bid / "map.png")
        save(card(), BUILDINGS / bid / "card.png")
        print("wrote", bid)
