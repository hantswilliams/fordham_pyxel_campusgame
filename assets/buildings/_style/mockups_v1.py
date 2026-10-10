"""Mockups for decisions/0021: every door faces south, and one shared
building style taken from research/images/inspiration1-4.png (Pokemon
Gold/Silver towns).

Draws the three drawn buildings (and a typical tile hall) in the proposed
style, each next to how it looks today, and saves a review sheet here.
Run from the repo root after tools/render_map.py, with the game's tile and
character sheets exported to the scratch folder given as the first arg.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from game.config import palette  # noqa: E402

SCRATCH = Path(sys.argv[1])
RGB = [((c >> 16) & 255, (c >> 8) & 255, c & 255) for c in palette()]
(BLACK, NAVY, MAROON, GREEN, BROWN, DBLUE, LBLUE, WHITE, RED, ORANGE, YELLOW,
 LIME, CYAN, GRAY, PINK, PEACH, ST_HI, ST, ST_SH, ST_DK, ROOF, ROOF_SH,
 BRICK, BRICK_DK) = RGB
CLEAR = (0, 0, 0, 0)
TILES = Image.open(SCRATCH / "tiles.png").convert("RGBA")
CHARS = Image.open(SCRATCH / "chars.png").convert("RGBA")
MAP = Image.open(ROOT / "build" / "map_rose_hill.png").convert("RGB")


def tile(name):
    uv = {"grass": (0, 0), "path": (16, 0), "tree": (96, 0), "flowers": (112, 0),
          "lamp": (208, 0), "hedge": (128, 0)}[name]
    return TILES.crop((uv[0], uv[1], uv[0] + 16, uv[1] + 16))


def sprite(u, v):
    s = CHARS.crop((u, v, u + 16, v + 16))
    px = s.load()
    for y in range(16):
        for x in range(16):
            if px[x, y][:3] == (0, 0, 0):
                px[x, y] = CLEAR
    return s


def label(text, col):
    """Pyxel's own 4x6 font, exported by the caller, recolored."""
    im = Image.open(SCRATCH / f"t_{text.replace(' ', '_')}.png").convert("RGBA")
    px = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            px[x, y] = col + (255,) if px[x, y][:3] != (0, 0, 0) else CLEAR
    return im


# ------------------------------------------------------------- shared kit
# The house style: every building is a roof on top and a front wall at the
# bottom (facing south, toward the camera), a 1 px navy outline, a door in
# the bottom row with a mat, two-pane windows, and a gray signpost by the
# door. Each building keeps its own materials and one signature feature.

def outline(d, box):
    x0, y0, x1, y1 = box
    d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], outline=NAVY)


def window(d, x, y, w=10, h=7, glass=LBLUE):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=WHITE)
    d.rectangle([x + 1, y + 1, x + w // 2 - 1, y + h - 2], fill=glass)
    d.rectangle([x + w // 2 + 1, y + 1, x + w - 2, y + h - 2], fill=glass)
    d.line([x + 1, y + 1, x + 2, y + 1], fill=WHITE)


def door(d, x, y, w=10, h=13, frame=ST_DK, leaf=BROWN, glass=False):
    d.rectangle([x - 1, y - 1, x + w, y + h - 1], fill=frame)
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=LBLUE if glass else leaf)
    d.line([x + w // 2, y, x + w // 2, y + h - 1], fill=NAVY if glass else frame)
    if not glass:
        d.point([x + w // 2 - 2, y + h // 2], fill=YELLOW)
        d.point([x + w // 2 + 2, y + h // 2], fill=YELLOW)


def mat(d, x, y, w=12):
    d.rectangle([x, y, x + w - 1, y + 2], fill=MAROON)
    d.line([x, y + 1, x + w - 1, y + 1], fill=PINK)


def signpost(d, x, y):
    """Gray metal sign on two legs, as in the inspiration images (14 x 13)."""
    d.rectangle([x + 2, y + 9, x + 3, y + 12], fill=NAVY)
    d.rectangle([x + 10, y + 9, x + 11, y + 12], fill=NAVY)
    d.rectangle([x, y, x + 13, y + 9], fill=NAVY)
    d.rectangle([x + 1, y + 1, x + 12, y + 8], fill=WHITE)
    d.rectangle([x + 2, y + 2, x + 11, y + 7], fill=GRAY)
    for ly in (3, 5):
        d.line([x + 3, y + ly, x + 10, y + ly], fill=WHITE)


def nameplate(im, d, text, cx, y, bg=ST_HI, fg=NAVY):
    lab = label(text, fg)
    w = lab.size[0] + 4
    d.rectangle([cx - w // 2, y, cx - w // 2 + w - 1, y + 7], fill=bg)
    d.rectangle([cx - w // 2 - 1, y - 1, cx - w // 2 + w, y + 8], outline=NAVY)
    im.paste(lab, (cx - w // 2 + 2, y + 1), lab)


def eave(d, x0, x1, y):
    """Bottom edge of a roof: dark line plus a soft shadow on the wall."""
    d.line([x0, y, x1, y], fill=NAVY)
    d.line([x0, y + 1, x1, y + 1], fill=ST_DK)


# ------------------------------------------------------------- buildings
def walsh_library():
    """10 x 8 tiles (one row shorter, so a walkway can run along its south
    side). Signature: the slatted tower and the row of glass arches."""
    W, H = 160, 128
    im = Image.new("RGBA", (W, H), CLEAR)
    d = ImageDraw.Draw(im)
    # roof: stone parapet, flat membrane, skylights; the tower block is taller
    d.rectangle([0, 0, W - 1, 93], fill=ST)
    d.rectangle([3, 3, W - 4, 91], fill=ROOF)
    for y in range(12, 90, 10):
        d.line([4, y, W - 5, y], fill=ROOF_SH)
    d.rectangle([3, 3, 60, 54], fill=ST_HI)          # tower block roof, a storey up
    d.rectangle([6, 6, 57, 51], fill=ROOF)
    d.rectangle([61, 3, 64, 58], fill=ROOF_SH)        # its shadow
    d.rectangle([3, 55, 64, 58], fill=ROOF_SH)
    for sx in (12, 32):
        d.rectangle([sx, 18, sx + 14, 26], fill=NAVY)
        d.rectangle([sx + 1, 19, sx + 13, 25], fill=LBLUE)
    for sx in (74, 128):
        d.rectangle([sx, 66, sx + 18, 72], fill=NAVY)
        d.rectangle([sx + 1, 67, sx + 17, 71], fill=LBLUE)
    # the tower: stone, open slats at the top, crown, shadow
    tx, ttop, tw, tbase = 100, 8, 22, 70
    d.polygon([(tx + tw, ttop + 10), (tx + tw + 10, ttop + 16), (tx + tw + 10, tbase + 8),
               (tx + 6, tbase + 8)], fill=ROOF_SH)
    d.rectangle([tx, ttop, tx + tw - 1, tbase], fill=ST_HI)
    d.rectangle([tx + tw - 6, ttop, tx + tw - 1, tbase], fill=ST_SH)
    for sx in range(tx + 3, tx + tw - 3, 3):
        d.line([sx, ttop + 5, sx, ttop + 24], fill=NAVY)
    d.rectangle([tx - 1, ttop - 2, tx + tw, ttop + 1], fill=ST_DK)
    outline(d, (tx, ttop - 2, tx + tw - 1, tbase))
    eave(d, 0, W - 1, 94)
    # front wall (south): stone, piers, cornice, glass arches; main doors centred
    d.rectangle([0, 96, W - 1, H - 1], fill=ST)
    d.line([0, 96, W - 1, 96], fill=ST_HI)
    for px in range(0, W, 16):
        d.rectangle([px, 96, px + 2, H - 1], fill=ST_HI)
        d.line([px + 3, 97, px + 3, H - 1], fill=ST_SH)
        if px not in (64, 80):
            d.rectangle([px + 5, 104, px + 13, H - 3], fill=NAVY)       # glass arch
            d.pieslice([px + 5, 100, px + 13, 108], 180, 360, fill=NAVY)
            d.line([px + 9, 102, px + 9, H - 3], fill=DBLUE)
            d.line([px + 6, 106, px + 6, 112], fill=LBLUE)
    d.rectangle([66, 99, 93, 104], fill=ST_SH)                          # entrance canopy
    nameplate(im, d, "WALSH LIBRARY", 80, 98)
    door(d, 68, 108, 24, 19, frame=ST_DK, glass=True)
    d.line([0, H - 1, W - 1, H - 1], fill=ST_DK)
    outline(d, (0, 0, W - 1, H - 1))
    return im, (68, H)            # where the door's bottom-left meets the ground


def campbell_hall():
    """3 x 10 tiles; tall and narrow like the dark tower in inspiration3.
    Signature: the glass stair tower and charcoal brick."""
    W, H = 48, 160
    im = Image.new("RGBA", (W, H), CLEAR)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, 10], fill=BRICK_DK)                      # roof strip
    d.rectangle([2, 2, W - 3, 8], fill=ROOF_SH)
    eave(d, 0, W - 1, 11)
    d.rectangle([0, 12, W - 1, H - 1], fill=BRICK_DK)                  # tall façade
    for y in range(14, H - 22, 3):
        for x in range((y % 2) * 2, W, 4):
            d.point([x, y], fill=BRICK)
    for row, y in enumerate(range(16, H - 26, 11)):                     # storeys of windows
        for x in (3, 15):
            window(d, x, y, 9, 8)
    d.rectangle([28, 4, 41, H - 22], fill=LBLUE)                       # glass stair tower
    for gx in range(30, 41, 3):
        d.line([gx, 4, gx, H - 22], fill=NAVY)
    for gy in range(8, H - 22, 6):
        d.line([28, gy, 41, gy], fill=CYAN)
    d.line([29, 5, 29, H - 23], fill=WHITE)
    outline(d, (28, 4, 41, H - 22))
    d.rectangle([0, H - 21, W - 1, H - 1], fill=NAVY)                  # glass ground floor
    for gx in range(2, W, 5):
        d.line([gx, H - 20, gx, H - 1], fill=DBLUE)
    d.rectangle([2, H - 24, W - 3, H - 21], fill=BROWN)                 # wood canopy
    nameplate(im, d, "CAMPBELL", 24, H - 33, bg=WHITE)
    door(d, 18, H - 16, 12, 16, frame=GRAY, glass=True)
    outline(d, (0, 0, W - 1, H - 1))
    return im, (18, H)


def dealy_hall():
    """6 x 5 tiles: simplified from the T to one block facing south.
    Signature: dark fieldstone, white quoins, the columned portico."""
    W, H = 96, 80
    im = Image.new("RGBA", (W, H), CLEAR)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, 41], fill=ST)                            # light top storey
    d.rectangle([3, 3, W - 4, 39], fill=ROOF)
    for y in range(10, 38, 7):
        d.line([4, y, W - 5, y], fill=ROOF_SH)
    eave(d, 0, W - 1, 42)
    d.rectangle([0, 44, W - 1, H - 1], fill=BRICK_DK)                  # fieldstone wall
    for y in range(44, H):
        for x in range(W):
            h = (x * 73 + y * 151 + (x * y) % 7) % 11
            if h in (0, 4):
                d.point([x, y], fill=BRICK)
    d.rectangle([0, 44, W - 1, 47], fill=ST_HI)                        # light band
    for x in list(range(4, 32, 13)) + list(range(66, 92, 13)):
        for y, h in ((50, 8), (62, 14)):
            d.rectangle([x - 2, y - 2, x + 9, y + h + 1], fill=WHITE)  # quoins
            for qy in range(y - 1, y + h, 3):
                d.point([x - 3, qy], fill=ST_HI)
                d.point([x + 10, qy + 1], fill=ST_HI)
            d.rectangle([x, y, x + 7, y + h - 1], fill=NAVY)
            d.line([x + 4, y, x + 4, y + h - 1], fill=DBLUE)
    # portico: white columns and pediment, arched wooden door
    d.rectangle([34, 46, 61, 51], fill=WHITE)
    d.line([34, 51, 61, 51], fill=ST_SH)
    d.rectangle([36, 52, 59, H - 1], fill=ST_HI)
    for cx in (37, 56):
        d.rectangle([cx, 52, cx + 2, H - 1], fill=WHITE)
        d.line([cx + 2, 52, cx + 2, H - 1], fill=ST)
    nameplate(im, d, "DEALY HALL", 48, 36, bg=WHITE)
    d.pieslice([41, 56, 54, 68], 180, 360, fill=BROWN)
    door(d, 42, 62, 12, 18, frame=BROWN, leaf=NAVY)
    outline(d, (0, 0, W - 1, H - 1))
    return im, (42, H)


def typical_hall():
    """A typical tile building (Hughes Hall, 5 x 3 tiles) in the same style:
    slate roof, Fordham stone wall, centred door, signpost."""
    W, H = 80, 48
    im = Image.new("RGBA", (W, H), CLEAR)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, 25], fill=DBLUE)
    d.line([0, 0, W - 1, 0], fill=CYAN)
    for y in range(4, 24, 4):
        for x in range((y // 4 % 2) * 4, W, 8):
            d.line([x, y, x + 5, y], fill=NAVY)
    eave(d, 0, W - 1, 26)
    d.rectangle([0, 28, W - 1, H - 1], fill=ST)
    for y in range(31, H - 1, 4):
        d.line([0, y, W - 1, y], fill=ST_SH)
    for x in (6, 20, 50, 64):
        window(d, x, 33)
    nameplate(im, d, "HUGHES HALL", 40, 18, bg=ST_HI)
    door(d, 35, 35, 10, 13)
    outline(d, (0, 0, W - 1, H - 1))
    return im, (35, H)


# ------------------------------------------------------------- scenes
def scene(build, size_tiles, today_box):
    """256 x 192 scene: lawn, trees, a path to the door, the signpost and
    the player at the mat; plus today's in-game crop for comparison."""
    bim, (dx, dy) = build
    bw, bh = bim.size
    sc = Image.new("RGBA", (256, 192), CLEAR)
    for y in range(0, 192, 16):
        for x in range(0, 256, 16):
            sc.paste(tile("grass"), (x, y))
    bx = (256 - bw) // 2 // 16 * 16
    by = max(0, (192 - 32 - bh) // 16 * 16)
    if by >= 16:
        for x in range(0, 256, 16):
            sc.paste(tile("tree"), (x, 0), tile("tree"))
    door_x = bx + dx
    for y in range(by + bh, 192, 16):                                  # path to the door
        sc.paste(tile("path"), (door_x // 16 * 16, y))
        sc.paste(tile("path"), (door_x // 16 * 16 + 16, y))
    for x in range(0, 256, 16):
        sc.paste(tile("path"), (x, 176))
    sc.paste(bim, (bx, by), bim)
    d = ImageDraw.Draw(sc)
    mat(d, door_x, by + bh)
    signpost(d, door_x - 22, by + bh + 2)
    player = sprite(48, 0)                                             # facing up
    sc.paste(player, (door_x // 16 * 16, by + bh + 2), player)
    today = MAP.crop(today_box).resize((256, 192), Image.NEAREST) if today_box else None
    return sc.convert("RGB"), today


FONT = ImageFont.truetype(str(ROOT / "assets/fonts/PixelMplus12-Regular.ttf"), 20)


def sheet(rows, out):
    cell_w, cell_h = 512, 384
    pad, head = 16, 34
    W = cell_w * 2 + pad * 3
    H = (cell_h + head + pad) * len(rows) + pad + 40
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.text((pad, 10), "TODAY", font=FONT, fill=(0, 0, 0))
    d.text((pad * 2 + cell_w, 10), "PROPOSED: doors face south, shared style", font=FONT, fill=(0, 0, 0))
    y = 44
    for name, today, prop in rows:
        d.text((pad, y), name, font=FONT, fill=(134, 0, 56))
        if today is not None:
            im.paste(today.resize((cell_w, cell_h), Image.NEAREST), (pad, y + head))
        im.paste(prop.resize((cell_w, cell_h), Image.NEAREST), (pad * 2 + cell_w, y + head))
        y += cell_h + head + pad
    im.save(out)


if __name__ == "__main__":
    T = 16
    rows = []
    for name, build, box in (
        ("Walsh Library", walsh_library(), (2 * T, 58 * T, 2 * T + 256, 58 * T + 192)),
        ("Campbell Hall", campbell_hall(), (0, 50 * T, 256, 50 * T + 192)),
        ("Dealy Hall", dealy_hall(), (26 * T, 40 * T, 26 * T + 256, 40 * T + 192)),
        ("A typical tile hall (Hughes)", typical_hall(), (26 * T, 33 * T, 26 * T + 256, 33 * T + 192)),
    ):
        prop, today = scene(build, None, box)
        key = "hughes" if "Hughes" in name else name.split()[0].lower()
        prop.save(HERE / f"proposed_{key}.png")
        rows.append((name, today, prop))
    sheet(rows, HERE / "style_mockups.png")
    print("saved", HERE / "style_mockups.png")
