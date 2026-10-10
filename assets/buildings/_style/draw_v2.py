"""House-style drafts (decisions/0021) of the drawn buildings' map.png,
refined from the mockups in this folder. Writes
assets/buildings/<id>/map.png for Walsh Library, Campbell Hall and Dealy
Hall. Name plaques and door mats are not drawn here: the game adds them
(game/gfx/building_overlay.py) so every building's look the same.

Once someone retouches a map.png by hand, don't run this again for it.

    uv run python assets/buildings/_style/draw_v2.py
"""

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
 BRICK, BRICK_DK) = RGB
CLEAR = (0, 0, 0, 0)


# ------------------------------------------------------------- shared kit
def window(d, x, y, w=10, h=7, glass=LBLUE):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=WHITE)
    d.rectangle([x + 1, y + 1, x + w // 2 - 1, y + h - 2], fill=glass)
    d.rectangle([x + w // 2 + 1, y + 1, x + w - 2, y + h - 2], fill=glass)


def door(d, x, y, w, h, frame, leaf=BROWN, glass=False):
    d.rectangle([x - 1, y - 1, x + w, y + h - 1], fill=frame)
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=LBLUE if glass else leaf)
    d.line([x + w // 2, y, x + w // 2, y + h - 1], fill=NAVY if glass else frame)
    if glass:
        d.line([x + 2, y + 1, x + 2, y + h - 3], fill=WHITE)
    else:
        d.point([x + w // 2 - 2, y + h // 2], fill=YELLOW)
        d.point([x + w // 2 + 2, y + h // 2], fill=YELLOW)


def eave(d, x0, x1, y):
    d.line([x0, y, x1, y], fill=NAVY)
    d.line([x0, y + 1, x1, y + 1], fill=ROOF_SH)


def frame(d, w, h):
    d.rectangle([0, 0, w - 1, h - 1], outline=NAVY)


def fieldstone(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=BRICK_DK)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            h = (x * 73 + y * 151 + (x * y) % 7) % 11
            if h in (0, 4):
                d.point([x, y], fill=BRICK)
            elif h == 7:
                d.point([x, y], fill=NAVY)


# ------------------------------------------------------------- buildings
def walsh_library():
    """10 x 8 tiles. Roof (rows 0-5): stone parapet, flat roof, the raised
    tower-block roof at the west, skylights, the slatted tower. Front wall
    (rows 6-7): Fordham stone, piers, glass arches, glass main doors."""
    W, H = 160, 128
    im = Image.new("RGBA", (W, H), CLEAR)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, 93], fill=ST)
    d.rectangle([3, 3, W - 4, 91], fill=ROOF)
    for y in range(12, 90, 10):
        d.line([4, y, W - 5, y], fill=ROOF_SH)
    d.rectangle([3, 3, 60, 54], fill=ST_HI)                 # tower block, a storey up
    d.rectangle([6, 6, 57, 51], fill=ROOF)
    for y in range(14, 50, 10):
        d.line([7, y, 56, y], fill=ROOF_SH)
    d.rectangle([61, 3, 64, 58], fill=ROOF_SH)
    d.rectangle([3, 55, 64, 58], fill=ROOF_SH)
    for sx in (12, 32):                                     # skylights
        d.rectangle([sx, 18, sx + 14, 26], fill=NAVY)
        d.rectangle([sx + 1, 19, sx + 13, 25], fill=LBLUE)
        d.line([sx + 1, 19, sx + 13, 19], fill=WHITE)
    for sx in (74, 128):
        d.rectangle([sx, 66, sx + 18, 72], fill=NAVY)
        d.rectangle([sx + 1, 67, sx + 17, 71], fill=LBLUE)
        d.line([sx + 1, 67, sx + 17, 67], fill=WHITE)
    for ux, uy in ((136, 18), (20, 72)):                    # rooftop units
        d.rectangle([ux + 1, uy + 1, ux + 10, uy + 7], fill=ROOF_SH)
        d.rectangle([ux, uy, ux + 9, uy + 6], fill=GRAY)
        d.line([ux, uy, ux + 9, uy], fill=WHITE)
    # the slatted tower, with its shadow
    tx, ttop, tw, tbase = 100, 8, 22, 70
    d.polygon([(tx + tw, ttop + 10), (tx + tw + 10, ttop + 16), (tx + tw + 10, tbase + 8),
               (tx + 6, tbase + 8)], fill=ROOF_SH)
    d.rectangle([tx - 1, ttop - 3, tx + tw, tbase + 1], fill=NAVY)
    d.rectangle([tx, ttop, tx + tw - 1, tbase], fill=ST_HI)
    d.rectangle([tx + tw - 6, ttop, tx + tw - 1, tbase], fill=ST_SH)
    for sx in range(tx + 3, tx + tw - 3, 3):
        d.line([sx, ttop + 5, sx, ttop + 24], fill=NAVY)
    for y in range(ttop + 30, tbase, 4):
        d.line([tx, y, tx + tw - 7, y], fill=ST)
    d.rectangle([tx, ttop - 2, tx + tw - 1, ttop + 1], fill=ST_DK)
    eave(d, 0, W - 1, 94)
    # front wall
    d.rectangle([0, 96, W - 1, H - 1], fill=ST)
    d.line([0, 96, W - 1, 96], fill=ST_HI)
    for px in range(0, W, 16):
        d.rectangle([px, 96, px + 2, H - 1], fill=ST_HI)
        d.line([px + 3, 97, px + 3, H - 1], fill=ST_SH)
        if px not in (64, 80):
            d.rectangle([px + 5, 104, px + 13, H - 3], fill=NAVY)
            d.pieslice([px + 5, 100, px + 13, 108], 180, 360, fill=NAVY)
            d.line([px + 9, 102, px + 9, H - 3], fill=DBLUE)
            d.line([px + 6, 106, px + 6, 112], fill=LBLUE)
    d.rectangle([64, 97, 95, 107], fill=ST_SH)                # entrance bay, plaque goes here
    door(d, 68, 109, 24, 19, frame=ST_DK, glass=True)
    d.line([0, H - 2, W - 1, H - 2], fill=ST_SH)
    frame(d, W, H)
    return im


def campbell_hall():
    """3 x 10 tiles; tall and narrow, so the front shows almost all the way
    up. Charcoal brick, storeys of paired windows, the glass stair tower,
    glass ground floor under a wood canopy, glass doors."""
    W, H = 48, 160
    im = Image.new("RGBA", (W, H), CLEAR)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, 10], fill=BRICK_DK)
    d.rectangle([2, 2, W - 3, 8], fill=ROOF_SH)
    d.rectangle([6, 3, 14, 7], fill=GRAY)                    # rooftop unit
    eave(d, 0, W - 1, 11)
    d.rectangle([0, 13, W - 1, H - 1], fill=BRICK_DK)
    for y in range(14, H - 22, 3):
        for x in range((y % 2) * 2, W, 4):
            d.point([x, y], fill=BRICK)
    for y in range(16, H - 34, 11):
        for x in (3, 15):
            window(d, x, y, 9, 8)
        d.line([1, y + 9, 26, y + 9], fill=GRAY)              # light trim under each storey
    d.rectangle([27, 3, 42, H - 22], fill=NAVY)              # glass stair tower
    d.rectangle([28, 4, 41, H - 23], fill=LBLUE)
    for gx in range(30, 41, 3):
        d.line([gx, 4, gx, H - 23], fill=DBLUE)
    for gy in range(8, H - 23, 6):
        d.line([28, gy, 41, gy], fill=CYAN)
    d.line([29, 5, 29, H - 24], fill=WHITE)
    d.rectangle([0, H - 21, W - 1, H - 1], fill=NAVY)        # glass ground floor
    for gx in range(2, W, 5):
        d.line([gx, H - 20, gx, H - 1], fill=DBLUE)
    d.rectangle([1, H - 24, W - 2, H - 21], fill=BROWN)      # wood canopy
    d.line([1, H - 21, W - 2, H - 21], fill=NAVY)
    door(d, 18, H - 16, 12, 16, frame=GRAY, glass=True)
    frame(d, W, H)
    return im


def dealy_hall():
    """6 x 5 tiles, one block facing south. Light top storey seen as the
    roof rim, dark fieldstone wall with white-quoined windows, the white
    columned portico with its arched wooden door."""
    W, H = 96, 80
    im = Image.new("RGBA", (W, H), CLEAR)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, 41], fill=ST)
    d.rectangle([3, 3, W - 4, 39], fill=ROOF)
    for y in range(10, 38, 7):
        d.line([4, y, W - 5, y], fill=ROOF_SH)
    for ux, uy in ((10, 8), (74, 20)):
        d.rectangle([ux + 1, uy + 1, ux + 8, uy + 6], fill=ROOF_SH)
        d.rectangle([ux, uy, ux + 7, uy + 5], fill=GRAY)
    eave(d, 0, W - 1, 42)
    fieldstone(d, 0, 44, W - 1, H - 1)
    d.rectangle([0, 44, W - 1, 47], fill=ST_HI)
    for x in list(range(4, 32, 13)) + list(range(66, 92, 13)):
        for y, h in ((51, 8), (63, 14)):
            d.rectangle([x - 2, y - 2, x + 9, y + h + 1], fill=WHITE)
            for qy in range(y - 1, y + h, 3):
                d.point([x - 3, qy], fill=ST_HI)
                d.point([x + 10, qy + 1], fill=ST_HI)
            d.rectangle([x, y, x + 7, y + h - 1], fill=NAVY)
            d.line([x + 4, y, x + 4, y + h - 1], fill=DBLUE)
            d.point([x + 1, y + 1], fill=LBLUE)
    d.rectangle([33, 46, 62, 51], fill=WHITE)                 # portico entablature
    d.line([33, 51, 62, 51], fill=ST_SH)
    d.rectangle([35, 52, 60, H - 1], fill=ST_HI)
    for cx in (36, 57):                                       # columns
        d.rectangle([cx, 52, cx + 2, H - 1], fill=WHITE)
        d.line([cx + 2, 52, cx + 2, H - 1], fill=ST)
    d.pieslice([41, 56, 54, 68], 180, 360, fill=BROWN)        # arched wooden door
    door(d, 42, 62, 12, 18, frame=BROWN, leaf=NAVY)
    frame(d, W, H)
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
    for bid, fn in (("walsh_library", walsh_library), ("campbell_hall", campbell_hall),
                    ("dealy_hall", dealy_hall)):
        save(fn(), BUILDINGS / bid / "map.png")
        print("wrote", bid)
