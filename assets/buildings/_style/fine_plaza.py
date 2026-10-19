"""Hand-finished pictures at twice the detail for the fountain plaza
(decisions/0045, step 3): Dealy Hall, Cunniffe House and the Carolyn Dursi
Cunniffe Fountain, in the look of the approved mockup (decisions/images/
0045/B_overworld.png). Each keeps its building's layout (footprint, door,
plaque spot), so only the drawing changes. fine.py uses these instead of
running the building's own script.
"""

from __future__ import annotations

from fine import (BROWN, DBLUE, K, LBLUE, NAVY, ROOF, ROOF_SH, ST, ST_DK, ST_HI, ST_SH, WHITE,
                  YELLOW, FineDraw, FineImage, _panes, art, door, eave, fieldstone, framed_window,
                  pink_brick, slope_roof, stucco)
from kit import meta

SLATE, SLATE_HI = art("SLATE"), art("SLATE_HI")
BRONZE, BRONZE_LT, BRONZE_DK = art("BRONZE"), art("BRONZE_LT"), art("BRONZE_DK")
WATER, WATER_DK, WATER_HI = art("WATER"), art("WATER_DK"), art("WATER_HI")
WIN, WIN_LT, SILL = art("WIN"), art("WIN_LT"), art("SILL")


class U:
    """Draws in today's pixels (fractions allowed) at twice the detail."""

    def __init__(self, d: FineDraw, oy: float = 0):
        self.d, self.oy = d, oy

    def _p(self, x, y):
        return round(x * K), round((y + self.oy) * K)

    def rect(self, x0, y0, x1, y1, c):
        (X0, Y0), (X1, Y1) = self._p(x0, y0), self._p(x1, y1)
        if X1 > X0 and Y1 > Y0:
            self.d.d.rectangle([X0, Y0, X1 - 1, Y1 - 1], fill=c)

    def oval(self, x0, y0, x1, y1, c):
        (X0, Y0), (X1, Y1) = self._p(x0, y0), self._p(x1, y1)
        if X1 > X0 and Y1 > Y0:
            self.d.d.ellipse([X0, Y0, X1 - 1, Y1 - 1], fill=c)

    def poly(self, pts, c):
        self.d.d.polygon([self._p(x, y) for x, y in pts], fill=c)

    def px(self, x, y, c, w=1, h=1):
        X, Y = self._p(x, y)
        self.d.d.rectangle([X, Y, X + w - 1, Y + h - 1], fill=c)


def _outline(im: FineImage) -> None:
    """A one-pixel navy outline round everything drawn."""
    f = im.fine
    px = f.load()
    w, h = f.size
    solid = [[px[x, y][3] >= 128 for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            if solid[y][x]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and solid[ny][nx]:
                    px[x, y] = NAVY + (255,)
                    break


def _inset_outline(im: FineImage) -> None:
    """The same, but inside the picture's own edge (for pictures that fill
    their whole footprint, so the outline doesn't spill out of it)."""
    f = im.fine
    px = f.load()
    w, h = f.size
    for y in range(h):
        for x in range(w):
            if px[x, y][3] < 128:
                continue
            edge = x in (0, w - 1) or y in (0, h - 1) or any(
                px[x + dx, y + dy][3] < 128 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if edge:
                px[x, y] = NAVY + (255,)


# --- the Carolyn Dursi Cunniffe Fountain --------------------------------------------

def fountain() -> FineImage:
    """Tiered dark-bronze fountain in a round stone basin, the paving round
    it left clear so the plaza shows through."""
    m = meta("cunniffe_fountain")
    oy = -m["sprite_offset"][1]
    im = FineImage("RGBA", (32, 32 + oy))
    u = U(FineDraw(im))
    b = oy                                                   # the basin's footprint starts here
    u.oval(0.5, b + 4, 31.5, b + 31, ST_SH)                  # the basin: rim, then water
    u.oval(0.5, b + 3, 31.5, b + 29, ST)
    u.oval(1.5, b + 3, 30.5, b + 27, ST_HI)
    u.oval(3.5, b + 6, 28.5, b + 27, WATER_DK)
    u.oval(3.5, b + 6, 28.5, b + 25.5, WATER)
    for x, y, w in ((7, b + 13, 5), (19, b + 11, 6), (10, b + 19, 7), (21, b + 18, 4)):
        u.rect(x, y, x + w, y + 0.5, WATER_HI)
    u.rect(13.5, b - 0, 18.5, b + 17, BRONZE)                # pedestal
    u.rect(16.5, b - 0, 18.5, b + 17, BRONZE_DK)
    u.oval(7.5, b + 8, 24.5, b + 14, BRONZE_DK)              # lower bowl, with water in it
    u.oval(7.5, b + 7, 24.5, b + 12, BRONZE)
    u.oval(9.5, b + 7.5, 22.5, b + 10.5, WATER)
    u.rect(14.5, b - 4, 17.5, b + 1, BRONZE)
    u.oval(11, b - 4, 21, b + 1, BRONZE_DK)                  # upper bowl
    u.oval(11, b - 5, 21, b, BRONZE)
    u.oval(12.5, b - 4.5, 19.5, b - 2.5, WATER)
    u.rect(14.5, b - 10, 17.5, b - 3, BRONZE)                # finial
    u.rect(14.5, b - 10, 15.5, b - 3, BRONZE_LT)
    u.rect(15, b - 14, 17, b - 10, WATER_HI)                 # the jet and its spray
    for x, y in ((16, b - 13.5), (13, b - 11), (19, b - 11), (11, b - 8), (21, b - 8),
                 (10, b - 5), (22, b - 5)):
        u.rect(x - 0.5, y, x + 0.5, y + 1.5, WATER_HI)
    for x in (9, 12, 20, 23):                                # falling from the lower bowl
        u.rect(x, b + 11, x + 0.5, b + 14 + (x % 3), WATER_HI)
    _outline(im)
    return im


# --- Dealy Hall ------------------------------------------------------------------------

def dealy() -> FineImage:
    """Dark fieldstone with white-trimmed windows, a hipped slate roof with
    dormers, and the white columned portico round its arched door."""
    W, H, R = 96, 80, 42
    im = FineImage("RGBA", (W, H))
    d = FineDraw(im)
    u = U(d)
    slope_roof(d, 0, 0, W - 1, R - 1, SLATE, ROOF_SH, SLATE_HI)
    u.rect(10, 0, W - 10, 7, ROOF)                           # the back slope, above the ridge
    u.rect(10, 0, W - 10, 1, SLATE_HI)
    u.rect(10, 7, W - 10, 8, ROOF_SH)
    u.poly([(0, R), (0, 0), (10, 0), (10, 8)], ROOF)         # hips at both ends
    u.poly([(W, R), (W, 0), (W - 10, 0), (W - 10, 8)], ROOF_SH)
    for x in (6, W - 15):                                    # dormers, clear of the plaque
        u.poly([(x - 1.5, R - 13), (x + 4.5, R - 18.5), (x + 10.5, R - 13)], ROOF_SH)
        u.rect(x, R - 13, x + 9, R - 3, WHITE)
        u.rect(x + 7, R - 13, x + 9, R - 3, ST_HI)
        u.rect(x + 2, R - 11, x + 7, R - 4, WIN)
        u.rect(x + 2, R - 11, x + 3, R - 7, WIN_LT)
        u.rect(x - 1, R - 3, x + 10, R - 2, ROOF_SH)
    eave(d, 0, W - 1, R)
    fieldstone(d, 0, R + 2, W - 1, H - 1)
    u.rect(0, R + 2, W, R + 4.5, WHITE)                      # the white string course
    u.rect(0, R + 4.5, W, R + 5, ST_SH)
    for x in (4, 17, 66, 79):
        for y, h in ((51, 8), (63, 14)):
            u.rect(x - 1.5, y - 1.5, x + 9.5, y + h + 1, WHITE)          # trim
            for qy in range(y - 1, y + h, 3):                            # quoins
                u.rect(x - 2.5, qy, x - 1.5, qy + 1.5, ST_HI)
                u.rect(x + 9.5, qy + 1, x + 10.5, qy + 2.5, ST_HI)
            X0, Y0 = round(x * K), round(y * K)
            _panes(d, X0, Y0, X0 + 8 * K - 1, Y0 + h * K - 1, WIN)
            u.rect(x - 2, y + h + 1, x + 10, y + h + 1.5, SILL)
    u.rect(33, 46, 63, 51.5, WHITE)                          # portico: entablature, columns
    u.rect(33, 50.5, 63, 51.5, ST_SH)
    u.rect(35, 51.5, 61, H, ST_HI)
    for cx in (36, 57):
        u.rect(cx, 51.5, cx + 3, H, WHITE)
        u.rect(cx + 2, 51.5, cx + 3, H, ST)
        u.rect(cx - 0.5, 51.5, cx + 3.5, 52.5, WHITE)
    u.oval(41, 56, 55, 70, BROWN)                            # the arched wooden door
    door(d, 42, 62, 12, 18, frame=BROWN, leaf=NAVY)
    u.rect(40.5, H - 1, 55.5, H, ST)                         # its step
    _inset_outline(im)
    return im


# --- Cunniffe House -----------------------------------------------------------------

def cunniffe() -> FineImage:
    """Pink-brick wings with slate roofs either side of the taller gray
    centre block, its white top storey and cupola, the arched door."""
    m = meta("cunniffe_house")
    oy = -m["sprite_offset"][1]
    W, H = 80, 64 + oy
    im = FineImage("RGBA", (W, H))
    d = FineDraw(im)
    u = U(d, oy)
    for x0, x1 in ((0, 23), (56, 79)):                      # the wings
        slope_roof(d, x0, oy, x1, oy + 33, SLATE, ROOF_SH, SLATE_HI)
        eave(d, x0, x1, oy + 34)
        u.rect(x0, 35.5, x1 + 1, 38, WHITE)                  # white cornice
        u.rect(x0, 37.5, x1 + 1, 38, ST_SH)
        pink_brick(d, x0, oy + 38, x1, H - 1)
        for wx in range(x0 + 3, x1 - 4, 7):
            framed_window(d, wx, oy + 41, 5, 6, frame=WHITE)
            framed_window(d, wx, oy + 53, 5, 8, frame=WHITE, arched=True)
    u.rect(24, -2, 56, 6, ROOF)                              # the centre block's roof
    u.rect(24, -2, 56, -1, SLATE_HI)
    u.rect(24, 6, 56, 18, WHITE)                             # its white top storey
    u.rect(24, 6, 56, 6.5, ST_HI)
    u.rect(52, 6.5, 56, 18, ST_HI)
    for wx in (28, 38, 48):
        u.rect(wx, 10, wx + 4, 14, WIN)
        u.rect(wx, 10, wx + 1, 12, WIN_LT)
    u.rect(24, 18, 56, 21, ST_HI)                            # dentil cornice
    for x in range(25, 56, 2):
        u.rect(x, 19, x + 1, 20, ST)
    u.rect(24, 20.5, 56, 21, ST_SH)
    stucco(d, 24, oy + 21, 55, H - 1)
    u.rect(53, 21, 56, H - oy, ST_DK)
    for wx in (27, 48):
        framed_window(d, wx, oy + 24, 5, 7)
        framed_window(d, wx, oy + 46, 5, 9)
    u.oval(33, 41, 47, 51, ST_HI)                            # arched door with a fanlight
    u.rect(33, 46, 47, 64, ST_HI)
    u.oval(35, 43, 45, 52, WIN)
    u.rect(35, 47, 45, 64, NAVY)
    u.oval(36, 44, 44, 50, WIN_LT)
    u.rect(39.5, 44, 40.5, 47.5, WIN)
    for gx in range(36, 45, 2):
        u.rect(gx, 48, gx + 0.5, 64, DBLUE)
    for lx in (31, 48):                                      # lamps
        u.rect(lx - 1, 49, lx + 2, 53, YELLOW)
        u.rect(lx - 1, 52, lx + 2, 53, art("BADGE"))
        u.rect(lx, 47.5, lx + 1, 49, NAVY)
    # the cupola: white, with two windows, a slate cap and a green cross
    cx, top = 40, -oy + 3
    u.rect(cx - 8, top + 4, cx + 8, top + 17, WHITE)
    u.rect(cx + 5, top + 4, cx + 8, top + 17, ST_HI)
    u.poly([(cx - 9, top + 4.5), (cx, top + 0.5), (cx + 9, top + 4.5)], ROOF_SH)
    for wx in (cx - 5, cx + 1):
        u.rect(wx, top + 7, wx + 4, top + 15, WIN)
        u.rect(wx, top + 7, wx + 1, top + 11, LBLUE)
    u.rect(cx - 0.5, top - 4, cx + 0.5, top + 1, art("LEAF"))
    u.rect(cx - 1.5, top - 3, cx + 1.5, top - 2, art("LEAF"))
    _inset_outline(im)
    return im


OVERRIDES = {"cunniffe_fountain": fountain, "dealy_hall": dealy, "cunniffe_house": cunniffe}
