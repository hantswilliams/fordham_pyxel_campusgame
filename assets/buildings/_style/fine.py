"""Drawn buildings at twice the detail (decisions/0045, step 3).

Every building's map.png comes from a drawing script in this folder (or
its own options/draft_v1.py). This runs those same scripts again, through
stand-ins for PIL's Image and ImageDraw that draw at twice the size, and
swaps in finer versions of the shared textures and details: fieldstone,
cut stone, brick, roofs, windows, doors, eaves, trees and cars. So each
building keeps its design, and gets finer stone, slates, window panes and
1 px outlines. The result is map_fine.png, beside map.png, at exactly
twice its size; the game draws it in the finer world (game/gfx/world_art.py).
map.png stays for the campus map and the doubled-up fallback.

    uv run python assets/buildings/_style/fine.py [building ids...]

Everything is addressed in today's pixels; only what's drawn is finer.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from PIL import Image as PILImage
from PIL import ImageDraw as PILDraw

HERE = Path(__file__).resolve().parent
BUILDINGS = HERE.parent
ROOT = BUILDINGS.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
from game import config  # noqa: E402

K = 2
RGB = [((c >> 16) & 255, (c >> 8) & 255, c & 255) for c in config.GAME_COLORS]
(BLACK, NAVY, MAROON, GREEN, BROWN, DBLUE, LBLUE, WHITE, RED, ORANGE, YELLOW,
 LIME, CYAN, GRAY, PINK, PEACH, ST_HI, ST, ST_SH, ST_DK, ROOF, ROOF_SH,
 BRICK, BRICK_DK, PBRICK, PBRICK_SH) = RGB[:26]


def art(name: str):
    return RGB[getattr(config.Art, name)]


def _hash(*vals) -> float:
    x = 2166136261
    for v in vals:
        x = ((x ^ (int(v) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    x ^= x >> 13
    x = (x * 0x5BD1E995) & 0xFFFFFFFF
    x ^= x >> 15
    return x / 2 ** 32


# --- stand-ins for PIL ---------------------------------------------------------

def _box(xy):
    if len(xy) == 2:
        (x0, y0), (x1, y1) = xy
    else:
        x0, y0, x1, y1 = xy
    return x0, y0, x1, y1


def _points(xy):
    if xy and isinstance(xy[0], (tuple, list)):
        return [tuple(p) for p in xy]
    return list(zip(xy[0::2], xy[1::2]))


def _fine_box(x0, y0, x1, y1):
    """Today's inclusive pixel box -> the same area, twice the size."""
    return [x0 * K, y0 * K, x1 * K + K - 1, y1 * K + K - 1]


class FineImage:
    """A picture drawn at twice the size, addressed in today's pixels."""

    def __init__(self, mode="RGBA", size=(1, 1), color=0):
        self.mode = mode
        self.size = (int(size[0]), int(size[1]))
        if color == 0 or color is None:
            color = (0, 0, 0, 0)
        elif len(color) == 3:
            color = tuple(color) + (255,)
        self.fine = PILImage.new("RGBA", (self.size[0] * K, self.size[1] * K), color)

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    def _wrap(self, fine, size):
        out = FineImage(self.mode, size)
        out.fine = fine
        return out

    def crop(self, box):
        x0, y0, x1, y1 = box
        return self._wrap(self.fine.crop((x0 * K, y0 * K, x1 * K, y1 * K)), (x1 - x0, y1 - y0))

    def paste(self, im, box=(0, 0), mask=None):
        self.fine.paste(_fine_of(im), (box[0] * K, box[1] * K), None if mask is None else _fine_of(mask))

    def alpha_composite(self, im, dest=(0, 0)):
        self.fine.alpha_composite(_fine_of(im).convert("RGBA"), (dest[0] * K, dest[1] * K))

    def transpose(self, method):
        turn = method in (PILImage.Transpose.ROTATE_90, PILImage.Transpose.ROTATE_270)
        size = (self.size[1], self.size[0]) if turn else self.size
        return self._wrap(self.fine.transpose(method), size)

    def convert(self, mode):
        return self

    def copy(self):
        return self._wrap(self.fine.copy(), self.size)


def _fine_of(im):
    if isinstance(im, FineImage):
        return im.fine
    return im.resize((im.width * K, im.height * K), PILImage.NEAREST)


class FineDraw:
    """ImageDraw's calls in today's pixels, drawn twice the size. Shapes come
    out the same; outlines drawn with `outline=` are one fine pixel thick."""

    def __init__(self, im: FineImage):
        self.im = im
        self.d = PILDraw.Draw(im.fine)

    def rectangle(self, xy, fill=None, outline=None, width=1):
        x0, y0, x1, y1 = _box(xy)
        if x1 < x0 or y1 < y0:
            return
        b = _fine_box(x0, y0, x1, y1)
        if fill is not None:
            self.d.rectangle(b, fill=fill)
        if outline is not None:
            self.d.rectangle(b, outline=outline, width=width)

    def line(self, xy, fill=None, width=1):
        pts = _points(xy)
        if len(pts) == 1:
            pts = pts * 2
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            if ax == bx or ay == by:
                self.d.rectangle(_fine_box(min(ax, bx), min(ay, by), max(ax, bx), max(ay, by)), fill=fill)
            else:
                h = (K - 1) / 2
                self.d.line([(ax * K + h, ay * K + h), (bx * K + h, by * K + h)], fill=fill, width=K * width)

    def point(self, xy, fill=None):
        for x, y in _points(xy):
            self.d.rectangle(_fine_box(x, y, x, y), fill=fill)

    def ellipse(self, xy, fill=None, outline=None, width=1):
        self.d.ellipse(_fine_box(*_box(xy)), fill=fill, outline=outline, width=width)

    def pieslice(self, xy, start, end, fill=None, outline=None, width=1):
        self.d.pieslice(_fine_box(*_box(xy)), start, end, fill=fill, outline=outline, width=width)

    def chord(self, xy, start, end, fill=None, outline=None, width=1):
        self.d.chord(_fine_box(*_box(xy)), start, end, fill=fill, outline=outline, width=width)

    def arc(self, xy, start, end, fill=None, width=1):
        self.d.arc(_fine_box(*_box(xy)), start, end, fill=fill, width=K * width)

    def polygon(self, xy, fill=None, outline=None, width=1):
        h = (K - 1) / 2
        self.d.polygon([(x * K + h, y * K + h) for x, y in _points(xy)], fill=fill, outline=outline,
                       width=width)

    # finer drawing, in fine pixels, for the helpers below
    def frect(self, X0, Y0, X1, Y1, c):
        if X1 >= X0 and Y1 >= Y0:
            self.d.rectangle([X0, Y0, X1, Y1], fill=c)


class _ImageModule:
    """Stands in for PIL.Image inside a drawing script."""
    Image = PILImage.Image
    Transpose = PILImage.Transpose
    NEAREST = PILImage.NEAREST

    @staticmethod
    def new(mode, size, color=0):
        return FineImage(mode, size, color)


class _DrawModule:
    """Stands in for PIL.ImageDraw inside a drawing script."""

    @staticmethod
    def Draw(im):
        return FineDraw(im) if isinstance(im, FineImage) else PILDraw.Draw(im)


# --- finer textures ---------------------------------------------------------------

def fieldstone(d, x0, y0, x1, y1, base=BRICK_DK, light=BRICK, dark=ROOF_SH):
    """Rubble stone: irregular stones in courses of dark mortar."""
    X0, Y0, X1, Y1 = _fine_box(x0, y0, x1, y1)
    d.frect(X0, Y0, X1, Y1, base)
    for row, y in enumerate(range(Y0, Y1 + 1, 4)):
        x = X0 - int(_hash(row, y, 1) * 4)
        while x <= X1:
            w = 3 + int(_hash(x, y, 2) * 4)
            t = _hash(x, y, 3)
            c = dark if t < 0.22 else light
            d.frect(max(x, X0), y, min(x + w - 1, X1), min(y + 2, Y1), c)
            if t > 0.85:
                d.frect(max(x, X0), y, min(x + w - 1, X1), y, dark)     # a lighter top edge
            x += w + 1


def fieldstone_v2(d, x0, y0, x1, y1):
    fieldstone(d, x0, y0, x1, y1)


def ashlar(d, x0, y0, x1, y1, base=ST, joint=ST_SH, step=4):
    """Cut stone in courses with staggered joints, a light edge on each."""
    X0, Y0, X1, Y1 = _fine_box(x0, y0, x1, y1)
    d.frect(X0, Y0, X1, Y1, base)
    pitch = step * K
    for i, y in enumerate(range(Y0, Y1 + 1, pitch)):
        if y + pitch - 1 <= Y1:
            d.frect(X0, y + pitch - 1, X1, y + pitch - 1, joint)
        if base != ST_HI:
            d.frect(X0, y, X1, y, ST_HI)
        for x in range(X0 + (8 if i % 2 else 0), X1, 16):
            d.frect(x, y, x, min(y + pitch - 2, Y1), joint)


def brick(d, x0, y0, x1, y1, base, mortar):
    X0, Y0, X1, Y1 = _fine_box(x0, y0, x1, y1)
    d.frect(X0, Y0, X1, Y1, base)
    for i, y in enumerate(range(Y0 + 3, Y1 + 1, 4)):
        d.frect(X0, y, X1, y, mortar)
        for x in range(X0 + (i % 2) * 4, X1 + 1, 8):
            d.frect(x, y - 3, x, y - 1, mortar)


def pink_brick(d, x0, y0, x1, y1):
    brick(d, x0, y0, x1, y1, PBRICK, PBRICK_SH)


def stucco(d, x0, y0, x1, y1):
    X0, Y0, X1, Y1 = _fine_box(x0, y0, x1, y1)
    d.frect(X0, Y0, X1, Y1, ST_DK)
    for y in range(Y0, Y1 + 1, 3):
        for x in range(X0 + (y // 3) % 4, X1 + 1, 7):
            d.frect(x, y, x, y, ROOF_SH)


def tan_stone(d, x0, y0, x1, y1, band=0):
    """Keating's tan fieldstone, in finer blocks with thin light mortar."""
    X0, Y0, X1, Y1 = _fine_box(x0, y0, x1, y1)
    d.frect(X0, Y0, X1, Y1, ST)
    for row, y in enumerate(range(Y0, Y1 + 1, 5)):
        x = X0 - (row % 2) * 4
        while x <= X1:
            w = 5 + int(_hash(x, y, 4) * 4)
            h = _hash(x, y, 5)
            c = ST_DK if h < 0.18 else (ST if h < 0.45 else ST_SH)
            d.frect(max(x, X0), y, min(x + w - 1, X1), min(y + 3, Y1), c)
            x += w + 1
    if band:
        for y in range(y0 + band, y1, band):
            d.frect(X0, y * K, X1, y * K + 1, ST_HI)


def panels(d, x0, y0, x1, y1, base=ROOF, rib=ROOF_SH, step=3):
    X0, Y0, X1, Y1 = _fine_box(x0, y0, x1, y1)
    d.frect(X0, Y0, X1, Y1, base)
    for x in range(X0 + 2, X1, step + 1):
        d.frect(x, Y0, x, Y1, rib)


def flat_roof(d, x0, y0, x1, y1, rim=ST, fill=ROOF, seam=ROOF_SH, units=()):
    X0, Y0, X1, Y1 = _fine_box(x0, y0, x1, y1)
    d.frect(X0, Y0, X1, Y1, rim)
    d.frect(X0, Y0, X1, Y0, ST_HI)
    d.frect(X0 + 3, Y0 + 3, X1 - 3, Y1 - 2, fill)
    for y in range(Y0 + 12, Y1 - 3, 12):
        d.frect(X0 + 4, y, X1 - 4, y, seam)
    for x in range(X0 + 20, X1 - 4, 24):
        d.frect(x, Y0 + 4, x, Y1 - 3, seam)
    for ux, uy in units:                                 # rooftop units
        UX, UY = ux * K, uy * K
        d.frect(UX + 2, UY + 2, UX + 18, UY + 13, seam)
        d.frect(UX, UY, UX + 16, UY + 11, GRAY)
        d.frect(UX, UY, UX + 16, UY, WHITE)
        for gx in range(UX + 3, UX + 14, 3):
            d.frect(gx, UY + 3, gx, UY + 8, ROOF_SH)


def slope_roof(d, x0, y0, x1, y1, base, line, highlight):
    """A pitched roof from above: slates in courses, a light ridge."""
    X0, Y0, X1, Y1 = _fine_box(x0, y0, x1, y1)
    d.frect(X0, Y0, X1, Y1, base)
    for i, y in enumerate(range(Y0 + 6, Y1 + 1, 7)):
        d.frect(X0, y, X1, y, line)
        for x in range(X0 + (6 if i % 2 else 0), X1 + 1, 12):
            d.frect(x, y - 6, x, y - 1, line)
            if _hash(x, y, 6) < 0.3:
                d.frect(x + 1, y - 6, min(x + 10, X1), y - 6, highlight)
    d.frect(X0, Y0, X1, Y0 + 1, highlight)


def plaza(d, x0, y0, w, h):
    """The fountain's plaza: left clear, so the world's paving shows round it."""


def eave(d, x0, x1, y):
    X0, _, X1, _ = _fine_box(x0, 0, x1, 0)
    d.frect(X0, y * K, X1, y * K, NAVY)
    d.frect(X0, y * K + 1, X1, y * K + 3, ROOF_SH)


# --- finer details -------------------------------------------------------------------

def _panes(d, X0, Y0, X1, Y1, glass, split=True):
    """Glass from (X0, Y0) to (X1, Y1) in fine pixels: a darker top, a glint,
    and a fine mullion down the middle."""
    dark = art("PANE_DK") if glass == LBLUE else (DBLUE if glass == NAVY else glass)
    hi = art("PANE_HI") if glass == LBLUE else (LBLUE if glass == NAVY else WHITE)
    d.frect(X0, Y0, X1, Y1, glass)
    d.frect(X0, Y0, X1, Y0 + max(0, (Y1 - Y0) // 3 - 1), dark)
    if split and X1 - X0 >= 5:
        mx = (X0 + X1) // 2
        d.frect(mx, Y0, mx, Y1, WHITE if glass != WHITE else ST_SH)
        d.frect(X0 + 1, Y0 + 1, X0 + 1, min(Y0 + 3, Y1 - 1), hi)
        d.frect(mx + 2, Y0 + 1, mx + 2, min(Y0 + 2, Y1 - 1), hi)
    else:
        d.frect(X0 + 1, Y0 + 1, X0 + 1, min(Y0 + 3, Y1 - 1), hi)


def window(d, x, y, w=8, h=8, frame=WHITE, glass=LBLUE):
    """The house-style window: a fine frame, two panes, a sill."""
    X0, Y0, X1, Y1 = _fine_box(x, y, x + w - 1, y + h - 1)
    d.frect(X0, Y0, X1, Y1, frame)
    _panes(d, X0 + 1, Y0 + 1, X1 - 1, Y1 - 2, glass, w >= 5)
    d.frect(X0, Y1, X1, Y1, art("SILL") if frame == WHITE else frame)


def window_v2(d, x, y, w=10, h=7, glass=LBLUE):
    window(d, x, y, w, h, WHITE, glass)


def window_keating(d, x, y, w=8, h=8):
    window(d, x, y, w, h, WHITE, LBLUE)


def arched_window(d, x, y, w, h, frame=WHITE, glass=NAVY):
    X0, X1 = (x - 1) * K, (x + w) * K + K - 1
    top, bottom = (y - 1) * K, (y + h) * K + K - 1
    r = (X1 - X0 + 1) // 2
    d.d.pieslice([X0, top, X1, top + 2 * r], 180, 360, fill=frame)
    d.frect(X0, top + r, X1, bottom, frame)
    d.d.pieslice([X0 + 1, top + 1, X1 - 1, top + 2 * r - 1], 180, 360, fill=glass)
    _panes(d, X0 + 1, top + r, X1 - 1, bottom - 1, glass)
    d.d.pieslice([X0 + 1, top + 1, X1 - 1, top + 2 * r - 1], 180, 270,
                 fill=DBLUE if glass == NAVY else art("PANE_DK"))


def gothic_window(d, x, y, w, h, frame=ST_HI, tracery=True):
    """Pointed-arch window with fine white tracery."""
    mid = y + w // 2
    d.rectangle([x - 1, mid - 1, x + w, y + h], fill=frame)
    d.polygon([(x - 1, mid), (x + w // 2, y - 2), (x + w, mid)], fill=frame)
    X0, X1 = x * K, (x + w - 1) * K + K - 1
    YM, Y1 = mid * K, (y + h - 1) * K + K - 1
    cx = (X0 + X1) / 2
    d.d.polygon([(X0, YM), (cx, y * K - 1), (X1, YM)], fill=NAVY)
    d.frect(X0, YM, X1, Y1, NAVY)
    d.frect(X0, YM, X1, YM + (Y1 - YM) // 3, DBLUE)
    if tracery:
        for mx in range(X0 + 3, X1 - 1, 4):
            d.frect(mx, YM - 1, mx, Y1, WHITE)
        d.frect(X0, YM + 6, X1, YM + 6, WHITE)
        d.frect(round(cx), y * K + 3, round(cx), YM - 1, WHITE)


def framed_window(d, x, y, w, h, frame=ST_HI, arched=False):
    """A window with a stone surround (Cunniffe) or white trim (Hughes)."""
    X0, Y0, X1, Y1 = (x - 1) * K, (y - 1) * K, (x + w) * K + K - 1, (y + h) * K + K - 1
    d.frect(X0, Y0, X1, Y1, frame)
    if arched:
        d.d.pieslice([X0, (y - 3) * K, X1, (y + 4) * K + 1], 180, 360, fill=frame)
        d.d.pieslice([X0 + 2, (y - 3) * K + 2, X1 - 2, (y + 4) * K - 1], 180, 360, fill=NAVY)
    _panes(d, X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, LBLUE if w >= 5 else NAVY)
    d.frect(X0 - 1, Y1 + 1, X1 + 1, Y1 + 1, art("SILL"))


def door(d, x, y, w, h, frame=ST_DK, leaf=BROWN, glass=False):
    """Double doors in a frame: panelled wood with brass knobs, or glass."""
    X0, Y0, X1, Y1 = (x - 1) * K, (y - 1) * K, (x + w) * K + K - 1, (y + h - 1) * K + K - 1
    d.frect(X0, Y0, X1, Y1, frame)
    IX0, IY0, IX1 = X0 + 2, Y0 + 2, X1 - 2
    mx = (IX0 + IX1) // 2
    if glass:
        _panes(d, IX0, IY0, IX1, Y1, LBLUE)
        d.frect(mx, IY0, mx, Y1, NAVY)
        return
    d.frect(IX0, IY0, IX1, Y1, leaf)
    d.frect(mx, IY0, mx, Y1, NAVY)
    shade = {BROWN: art("TRUNK_DK"), MAROON: art("MAROON_SH")}.get(leaf, NAVY)
    for a, b in ((IX0 + 2, mx - 2), (mx + 2, IX1 - 2)):     # recessed panels
        if b - a >= 2:
            for top, bot in ((IY0 + 2, (IY0 + Y1) // 2 - 1), ((IY0 + Y1) // 2 + 2, Y1 - 3)):
                if bot > top:
                    d.d.rectangle([a, top, b, bot], outline=shade)
    ky = (IY0 + Y1) // 2
    d.frect(mx - 2, ky, mx - 2, ky + 1, YELLOW)
    d.frect(mx + 2, ky, mx + 2, ky + 1, YELLOW)


def door_v2(d, x, y, w, h, frame, leaf=BROWN, glass=False):
    door(d, x, y, w, h, frame, leaf, glass)


def tree(d, cx, cy, r, leaf=GREEN, hi=LIME, trunk=BROWN, ground=None):
    """A small tree in the finer style (courtyards, forecourts)."""
    CX, CY, R = cx * K + 1, cy * K + 1, r * K
    if ground is not None:
        d.frect(CX - 1, CY, CX + 1, ground * K + 1, art("TRUNK"))
    out, dk, mid, lt = (art("LEAF_OUT"), art("LEAF_DK"), art("LEAF"), art("LEAF_LT"))
    if leaf == MAROON:
        out, dk, mid, lt = (art("BEECH_OUT"), art("BEECH_DK"), art("BEECH"), art("BEECH_LT"))
    d.d.ellipse([CX - R - 1, CY - R - 1, CX + R + 1, CY + R + 1], fill=out)
    d.d.ellipse([CX - R, CY - R, CX + R, CY + R], fill=dk)
    s = max(1, R // 6)
    d.d.ellipse([CX - R + s, CY - R, CX + R - 2 * s, CY + R - 3 * s], fill=mid)
    d.d.ellipse([CX - R + 3 * s, CY - R + 2 * s, CX, CY - s], fill=lt)


def car(d, x, y, body, nose="up"):
    """A parked car from above (9 x 14 today's pixels), with a cab, glass and lights."""
    X0, Y0, X1, Y1 = _fine_box(x, y, x + 8, y + 13)
    roof = {RED: MAROON, MAROON: NAVY, WHITE: ST_HI, GRAY: ROOF_SH, DBLUE: NAVY, YELLOW: ORANGE,
            ST_DK: BRICK_DK, LBLUE: CYAN, GREEN: NAVY, ST_HI: ST}.get(body, body)
    d.d.rounded_rectangle([X0, Y0, X1, Y1], radius=3, fill=NAVY)
    d.d.rounded_rectangle([X0 + 1, Y0 + 1, X1 - 1, Y1 - 1], radius=2, fill=body)
    up = nose == "up"
    wy0 = Y0 + 6 if up else Y1 - 9                       # windscreen
    d.frect(X0 + 2, wy0, X1 - 2, wy0 + 3, art("VAN_GLASS"))
    d.frect(X0 + 3, wy0, X0 + 3, wy0 + 1, art("VAN_GLASS_HI"))
    ry0 = Y1 - 7 if up else Y0 + 4                       # rear window
    d.frect(X0 + 2, ry0, X1 - 2, ry0 + 2, art("VAN_GLASS_DK"))
    top = min(wy0, ry0) + 4
    d.frect(X0 + 3, top, X1 - 3, max(wy0, ry0) - 1, roof)   # the roof between
    ly = Y0 + 1 if up else Y1 - 2
    for lx in (X0 + 2, X1 - 3):
        d.frect(lx, ly, lx + 1, ly + 1, art("HEADLIGHT"))


# names a script may use, and the finer drawing that replaces each
SWAPS = {
    "fieldstone": fieldstone, "ashlar": ashlar, "brick": brick, "pink_brick": pink_brick,
    "stucco": stucco, "tan_stone": tan_stone, "panels": panels, "flat_roof": flat_roof,
    "slope_roof": slope_roof, "plaza": plaza, "eave": eave, "window": window,
    "arched_window": arched_window, "gothic_window": gothic_window, "framed_window": framed_window,
    "door": door, "tree": tree, "car": car,
}
# where a script's own helper takes different arguments from the kit's
PER_SCRIPT = {
    "draw_v2": {"window": window_v2, "door": door_v2, "fieldstone": fieldstone_v2},
    "keating": {"window": window_keating},
}


# --- running the scripts -----------------------------------------------------------

def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(f"fine_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _patch(mod, script: str) -> None:
    swaps = {**SWAPS, **PER_SCRIPT.get(script, {})}
    for attr in list(vars(mod)):
        if attr == "Image":
            setattr(mod, attr, _ImageModule)
        elif attr == "ImageDraw":
            setattr(mod, attr, _DrawModule)
        elif attr in swaps and callable(getattr(mod, attr)):
            setattr(mod, attr, swaps[attr])


_kit = None
_mods: dict[str, object] = {}


def _script(script: str):
    """A drawing script, loaded with the stand-ins in place (and the kit)."""
    global _kit
    if _kit is None:
        import kit
        _kit = kit
        _patch(kit, "kit")
    if script not in _mods:
        path = BUILDINGS / "keating_hall" / "options" / "draft_v1.py" if script == "keating" \
            else HERE / f"{script}.py"
        mod = _load(script, path)
        _patch(mod, script)
        _mods[script] = mod
    return _mods[script]


# building id -> (script, how to draw its map picture)
SOURCES = {
    "walsh_library": ("draw_v2", lambda m: m.walsh_library()),
    "campbell_hall": ("draw_v2", lambda m: m.campbell_hall()),
    "dealy_hall": ("draw_v2", lambda m: m.dealy_hall()),
    "cunniffe_house": ("draw_fountain_quad", lambda m: m.cunniffe_map()),
    "hughes_hall": ("draw_fountain_quad", lambda m: m.hughes_map()),
    "cunniffe_fountain": ("draw_fountain_quad", lambda m: m.fountain_map()),
    "keating_hall": ("keating", lambda m: m.draw_map()),
    "lombardi_center": ("draw_athletics", lambda m: m.lombardi()),
    "mcshane_center": ("draw_athletics", lambda m: m.mcshane()),
    "rose_hill_gym": ("draw_athletics", lambda m: m.gym()),
    "moglia_stadium": ("draw_athletics", lambda m: m.gated("moglia_stadium", m.moglia())),
    "jack_coffey_field": ("draw_athletics", lambda m: m.gated("jack_coffey_field", m.jack_coffey())),
    "houlihan_park": ("draw_athletics", lambda m: m.gated("houlihan_park", m.houlihan())),
    "murphy_field": ("draw_athletics", lambda m: m.murphy()),
    "bahoshy_field": ("draw_athletics", lambda m: m.gated("bahoshy_field", m.bahoshy())),
    "tennis_courts": ("draw_athletics", lambda m: m.gated("tennis_courts", m.tennis())),
    "loschert_hall": ("draw_residence", lambda m: m.loschert()),
    "alumni_court_south": ("draw_residence", lambda m: m.alumni_south()),
    "queens_court": ("draw_residence", lambda m: m.queens_court()),
    "faber_hall": ("draw_residence", lambda m: m.faber()),
    "loyola_hall": ("draw_residence", lambda m: m.loyola()),
    "martyrs_court": ("draw_residence", lambda m: m.martyrs()),
    "martyrs_court_west": ("draw_residence", lambda m: m.martyrs_west()),
    "conley_salice": ("draw_residence", lambda m: m.conley_salice()),
    "ohare_hall": ("draw_residence", lambda m: m.ohare()),
    "tierney_hall": ("draw_residence", lambda m: m.tierney()),
    "finlay_hall": ("draw_residence", lambda m: m.finlay()),
    "walsh_hall": ("draw_residence", lambda m: m.walsh_hall()),
    "university_church": ("draw_academic", lambda m: m.church()),
    "collins_hall": ("draw_academic", lambda m: m.collins()),
    "thebaud_hall": ("draw_academic", lambda m: m.thebaud()),
    "freeman_hall": ("draw_academic", lambda m: m.freeman()),
    "larkin_hall": ("draw_academic", lambda m: m.larkin()),
    "spellman_hall": ("draw_academic", lambda m: m.spellman()),
    "mulcahy_hall": ("draw_academic", lambda m: m.mulcahy()),
    "admissions": ("draw_academic", lambda m: m.duane()),
    "parking_lot": ("draw_parking", lambda m: m.parking_lot()),
    "regional_parking": ("draw_parking", lambda m: m.garage()),
}

# today's walkway and lawn colours inside pictures -> the finer world's
REMAP = {LIME: art("GRASS"), GREEN: art("GRASS_TUFT"), PEACH: art("WALK")}


def finish(im: PILImage.Image) -> PILImage.Image:
    """Snap transparency, use the finer world's lawn and walkway colours, and
    thin a two-pixel navy outline round the building to one pixel."""
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    solid = [[px[x, y][3] >= 128 for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            if not solid[y][x]:
                px[x, y] = (0, 0, 0, 0)
                continue
            c = px[x, y][:3]
            if c in REMAP:
                px[x, y] = REMAP[c] + (255,)
    navy = NAVY + (255,)
    for y in range(h):
        for x in range(w):
            if px[x, y] != navy:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ox, oy = x - dx, y - dy                  # outside, opposite the way in
                if 0 <= ox < w and 0 <= oy < h and solid[oy][ox]:
                    continue
                ix, iy, jx, jy = x + dx, y + dy, x + 2 * dx, y + 2 * dy
                if (0 <= jx < w and 0 <= jy < h and px[ix, iy] == navy and solid[jy][jx]
                        and px[jx, jy] != navy):
                    px[ix, iy] = px[jx, jy]
    return im


def draw(bid: str) -> PILImage.Image:
    from fine_plaza import OVERRIDES                    # hand-finished ones (it imports this)
    if bid in OVERRIDES:
        return finish(OVERRIDES[bid]().fine)
    script, fn = SOURCES[bid]
    picture = fn(_script(script))
    return finish(picture.fine)


def main(ids) -> None:
    allowed = set(RGB)
    for bid in ids or SOURCES:
        im = draw(bid)
        bad = {c[:3] for _, c in im.getcolors(1 << 20) if c[3] and c[:3] not in allowed}
        if bad:
            raise SystemExit(f"{bid}: colours outside the game's palette: {sorted(bad)[:5]}")
        im.save(BUILDINGS / bid / "map_fine.png")
        print("wrote", bid, im.size)


if __name__ == "__main__":
    main(sys.argv[1:])
