"""Shared drawing kit for the house style (decisions/0021): palette names,
textures and details used by every drawn building and landmark. The batch
scripts in this folder import it.

Everything here draws with PIL in the game's exact palette. Pure black is
transparent in the game, so `save` turns transparent pixels black.
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


def canvas(bid):
    """A transparent image the right size for a building's map.png, its
    draw object, and the footprint's top-left in image pixels (ox, oy)."""
    m = meta(bid)
    w = max(len(r) for r in m["footprint"]) * 16
    h = len(m["footprint"]) * 16
    dx, dy = m.get("sprite_offset", [0, 0])
    im = Image.new("RGBA", (w - dx, h - dy), CLEAR)
    return im, ImageDraw.Draw(im), -dx, -dy


def card():
    im = Image.new("RGB", (CARD_W, CARD_H), LBLUE)
    return im, ImageDraw.Draw(im)


def save(im, path):
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = px[x, y]
            px[x, y] = (0, 0, 0, 0) if a < 128 else (r, g, b, 255)
    im.save(path)


def save_building(bid, map_im, card_im=None):
    save(map_im, BUILDINGS / bid / "map.png")
    if card_im is not None:
        save(card_im, BUILDINGS / bid / "card.png")
    print("wrote", bid)


# ---------------------------------------------------------------- textures
def fieldstone(d, x0, y0, x1, y1, base=BRICK_DK, light=BRICK, dark=ROOF_SH):
    """Irregular rubble stone (Dealy, Hughes; light version for the gym)."""
    d.rectangle([x0, y0, x1, y1], fill=base)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            h = (x * 73 + y * 151 + (x * y) % 7) % 11
            if h in (0, 4):
                d.point([x, y], fill=light)
            elif h == 7:
                d.point([x, y], fill=dark)


def ashlar(d, x0, y0, x1, y1, base=ST, joint=ST_SH, step=4):
    """Cut stone in courses with staggered joints."""
    d.rectangle([x0, y0, x1, y1], fill=base)
    for i, y in enumerate(range(y0 + step - 1, y1, step)):
        d.line([x0, y, x1, y], fill=joint)
        for x in range(x0 + (0 if i % 2 else 4), x1, 8):
            d.point([x, y - 2], fill=joint)


def brick(d, x0, y0, x1, y1, base, mortar):
    d.rectangle([x0, y0, x1, y1], fill=base)
    for i, y in enumerate(range(y0 + 2, y1, 3)):
        d.line([x0, y, x1, y], fill=mortar)
        for x in range(x0 + (i % 2) * 3, x1, 6):
            d.point([x, y - 1], fill=mortar)


def panels(d, x0, y0, x1, y1, base=ROOF, rib=ROOF_SH, step=3):
    """Ribbed metal cladding (vertical ribs)."""
    d.rectangle([x0, y0, x1, y1], fill=base)
    for x in range(x0 + 1, x1, step):
        d.line([x, y0, x, y1], fill=rib)


def flat_roof(d, x0, y0, x1, y1, rim=ST, fill=ROOF, seam=ROOF_SH, units=()):
    d.rectangle([x0, y0, x1, y1], fill=rim)
    d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 1], fill=fill)
    for y in range(y0 + 8, y1 - 1, 8):
        d.line([x0 + 3, y, x1 - 3, y], fill=seam)
    for ux, uy in units:
        d.rectangle([ux + 1, uy + 1, ux + 9, uy + 6], fill=seam)
        d.rectangle([ux, uy, ux + 8, uy + 5], fill=GRAY)
        d.line([ux, uy, ux + 8, uy], fill=WHITE)


def slope_roof(d, x0, y0, x1, y1, base, line, highlight):
    """Pitched roof seen from above: horizontal courses, light ridge."""
    d.rectangle([x0, y0, x1, y1], fill=base)
    for i, y in enumerate(range(y0 + 3, y1, 4)):
        d.line([x0, y, x1, y], fill=line)
        for x in range(x0 + (0 if i % 2 else 3), x1, 6):
            d.point([x, y - 2], fill=highlight)
    d.line([x0, y0, x1, y0], fill=highlight)


# ---------------------------------------------------------------- details
def eave(d, x0, x1, y):
    """Where the roof meets the front wall."""
    d.line([x0, y, x1, y], fill=NAVY)
    d.line([x0, y + 1, x1, y + 1], fill=ROOF_SH)


def window(d, x, y, w=8, h=8, frame=WHITE, glass=LBLUE):
    """The house-style two-pane window."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=frame)
    if w >= 5:
        d.rectangle([x + 1, y + 1, x + w // 2 - 1, y + h - 2], fill=glass)
        d.rectangle([x + w // 2 + 1, y + 1, x + w - 2, y + h - 2], fill=glass)
    else:
        d.rectangle([x + 1, y + 1, x + w - 2, y + h - 2], fill=glass)


def arched_window(d, x, y, w, h, frame=WHITE, glass=NAVY):
    d.rectangle([x - 1, y + w // 2, x + w, y + h], fill=frame)
    d.pieslice([x - 1, y - 1, x + w, y + w], 180, 360, fill=frame)
    d.rectangle([x, y + w // 2, x + w - 1, y + h - 1], fill=glass)
    d.pieslice([x, y, x + w - 1, y + w - 1], 180, 360, fill=glass)
    d.line([x + w // 2, y + 1, x + w // 2, y + h - 1], fill=DBLUE if glass == NAVY else WHITE)
    d.point([x + 1, y + w // 2], fill=LBLUE)


def gothic_window(d, x, y, w, h, frame=ST_HI):
    """Pointed-arch window with white tracery."""
    d.rectangle([x - 1, y + w // 2 - 1, x + w, y + h], fill=frame)
    d.polygon([(x - 1, y + w // 2), (x + w // 2, y - 2), (x + w, y + w // 2)], fill=frame)
    d.rectangle([x, y + w // 2, x + w - 1, y + h - 1], fill=NAVY)
    d.polygon([(x, y + w // 2), (x + (w - 1) / 2, y), (x + w - 1, y + w // 2)], fill=NAVY)
    for mx in range(x + 2, x + w - 1, 3):
        d.line([mx, y + w // 2 - 1, mx, y + h - 1], fill=WHITE)
    d.line([x, y + w // 2 + 3, x + w - 1, y + w // 2 + 3], fill=WHITE)


def door(d, x, y, w, h, frame=ST_DK, leaf=BROWN, glass=False):
    d.rectangle([x - 1, y - 1, x + w, y + h - 1], fill=frame)
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=LBLUE if glass else leaf)
    d.line([x + w // 2, y, x + w // 2, y + h - 1], fill=NAVY if glass else frame)
    if glass:
        d.line([x + 2, y + 1, x + 2, y + h - 3], fill=WHITE)
    else:
        d.point([x + w // 2 - 2, y + h // 2], fill=YELLOW)
        d.point([x + w // 2 + 2, y + h // 2], fill=YELLOW)


def battlements(d, x0, x1, y, h=3, step=4, fill=ST, top=ST_HI):
    d.rectangle([x0, y, x1, y + 2], fill=fill)
    for x in range(x0, x1 + 1, step * 2):
        d.rectangle([x, y - h, min(x + step - 1, x1), y], fill=fill)
        d.line([x, y - h, min(x + step - 1, x1), y - h], fill=top)


def outline(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], outline=NAVY)


def tree(d, cx, cy, r, leaf=GREEN, hi=LIME, trunk=BROWN, ground=None):
    if ground is not None:
        d.line([cx, cy, cx, ground], fill=trunk)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=leaf)
    d.ellipse([cx - r + 3, cy - r + 2, cx + r // 3, cy - 1], fill=hi)


def lawn(d, y, w=CARD_W, h=CARD_H):
    d.rectangle([0, y, w, h], fill=LIME)
    for x in range(0, w, 6):
        d.point([x, y + 4 + (x * 7) % max(1, h - y - 6)], fill=GREEN)


def clouds(d, spots=((24, 10, 26), (160, 14, 30))):
    for cx, cy, w in spots:
        d.ellipse([cx, cy, cx + w, cy + 6], fill=WHITE)
        d.ellipse([cx + w // 4, cy - 3, cx + w * 3 // 4, cy + 4], fill=WHITE)


def person(d, x, y, shirt):
    d.rectangle([x, y, x + 1, y + 1], fill=PEACH)
    d.rectangle([x - 1, y + 2, x + 2, y + 5], fill=shirt)
    d.line([x, y + 6, x, y + 7], fill=NAVY)
    d.line([x + 1, y + 6, x + 1, y + 7], fill=NAVY)


# ---------------------------------------------------------------- fields
def turf(d, x0, y0, x1, y1, stripe=16, vertical=True):
    """Mown / FieldTurf stripes."""
    d.rectangle([x0, y0, x1, y1], fill=GREEN)
    if vertical:
        for i, x in enumerate(range(x0, x1 + 1, stripe)):
            if i % 2:
                d.rectangle([x, y0, min(x + stripe - 1, x1), y1], fill=LIME)
    else:
        for i, y in enumerate(range(y0, y1 + 1, stripe)):
            if i % 2:
                d.rectangle([x0, y, x1, min(y + stripe - 1, y1)], fill=LIME)


def fordham_f(d, cx, cy, s=6, col=MAROON, edge=WHITE):
    """A small maroon 'F' logo for midfield / outfield."""
    d.ellipse([cx - s - 2, cy - s - 2, cx + s + 2, cy + s + 2], fill=edge)
    d.ellipse([cx - s, cy - s, cx + s, cy + s], fill=col)
    d.rectangle([cx - 2, cy - s + 2, cx - 1, cy + s - 2], fill=WHITE)
    d.line([cx - 2, cy - s + 2, cx + 3, cy - s + 2], fill=WHITE)
    d.line([cx - 2, cy, cx + 2, cy], fill=WHITE)


def light_tower(d, x, y, h):
    d.line([x, y, x, y + h], fill=NAVY)
    d.rectangle([x - 3, y - 3, x + 3, y], fill=NAVY)
    for lx in range(x - 2, x + 3, 2):
        d.point([lx, y - 2], fill=YELLOW)


def diamond(d, x0, y0, w, h, infield=ORANGE, base_path=PEACH, track=MAROON, logo=True):
    """A baseball/softball field seen from above, home plate at the bottom
    centre, outfield fence curving round the top."""
    cx, home = x0 + w // 2, y0 + h - 8
    d.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], fill=GREEN)
    r = min(w // 2 - 2, h - 10)
    d.pieslice([cx - r, home - r, cx + r, home + r], 225, 315, fill=track)       # warning track
    d.pieslice([cx - r + 4, home - r + 4, cx + r - 4, home + r - 4], 225, 315, fill=LIME)
    for i in range(0, r - 4, 8):                                                  # mowing arcs
        d.arc([cx - i, home - i, cx + i, home + i], 225, 315, fill=GREEN)
    s = r // 3
    d.polygon([(cx, home), (cx - s, home - s), (cx, home - 2 * s), (cx + s, home - s)], fill=infield)
    d.polygon([(cx, home - 3), (cx - s + 4, home - s), (cx, home - 2 * s + 4), (cx + s - 4, home - s)], fill=LIME)
    d.ellipse([cx - 2, home - s - 2, cx + 2, home - s + 2], fill=base_path)       # mound
    for bx, by in ((cx, home), (cx - s, home - s), (cx, home - 2 * s), (cx + s, home - s)):
        d.rectangle([bx - 1, by - 1, bx + 1, by + 1], fill=WHITE)
    d.line([cx, home, cx - r + 6, home - r + 6], fill=WHITE)                      # foul lines
    d.line([cx, home, cx + r - 6, home - r + 6], fill=WHITE)
    d.arc([cx - r, home - r, cx + r, home + r], 225, 315, fill=NAVY)              # fence
    if logo:
        fordham_f(d, cx, home - r // 2 - s // 2, 4)
    return cx, home
