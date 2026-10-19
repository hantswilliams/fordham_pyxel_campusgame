"""People, the bike and the vans at twice the detail (decisions/0045, step 2).

Drawn in code once, at startup, into one sheet (sheet()):

- people: 32 x 52 frames, 4 ways round x 3 steps, for the same looks
  (sprite numbers) as today's sheet, so maps and missions don't change.
  They stand 22 layout pixels tall, so the head rises into the cell above,
  as in the Game Boy Advance games, with faces, hair highlights and shading
- the player on the bike, both bikes (light blue, and the maroon one from
  the Bike Courier mission), pedalling
- the Campus Shuttle and the Ram Van: side on (64 x 48, facing right),
  from the front and from the back (32 x 48), the same sizes as today's
  vans doubled

Each part is drawn in layout units (2 px each) from the top left, light
from the top left; then one pass outlines everything at once. Right-facing
frames are the left-facing ones flipped.
"""

from __future__ import annotations

from dataclasses import dataclass

import pyxel

from game.config import Art, Col
from game.world.directions import Direction

FRAME_W, FRAME_H = 32, 52
TOP = 5                     # room above a standing person, for a rider's head
ORIGIN = (0, TOP + 14)      # the person's cell's top-left, in a frame (art px)
COLS = 12                   # 4 ways round x 3 steps
VAN_V = 8 * FRAME_H         # the vans' rows, below the people

# Bike and van numbers match game/gfx/placeholder_art.py
BIKE_SPRITE, MAROON_BIKE_SPRITE = 6, 7
SHUTTLE_VAN, RAM_VAN = 0, 1


@dataclass(frozen=True)
class Look:
    skin: str
    hair: str
    shirt: str
    pants: str
    style: str = "short"        # short, long, cap
    bag: bool = False
    lanyard: bool = False
    badge: bool = False
    collar: bool = False


# Same people, in the same order, as placeholder_art.CHARACTERS
LOOKS = [
    Look("SKIN1", "HAIR_BR", "MAROON", "PANTS", bag=True),                    # 0 player
    Look("SKIN2", "HAIR_BK", "SHIRT_W", "KHAKI", lanyard=True),               # 1 orientation leader
    Look("SKIN1", "HAIR_OR", "SHIRT_B", "PANTS", style="long"),               # 2 student
    Look("SKIN1", "HAIR_WH", "BLAZER", "PANTS", collar=True),                 # 3 staff
    Look("SKIN3", "HAIR_BR", "SHIRT_Y", "PANTS"),                             # 4 student
    Look("SKIN2", "HAIR_BK", "GUARD", "PANTS", style="cap", badge=True),      # 5 Public Safety
]


def _c(name: str) -> int:
    return Col.MAROON if name == "MAROON" else getattr(Art, name)


def _shade(name: str) -> int:
    return _c(name + "_SH")


class _Units:
    """Draws in layout units (2 art pixels each) from (ox, oy) on img."""

    def __init__(self, img, ox: int, oy: int):
        self.img, self.ox, self.oy = img, ox, oy

    def _p(self, x: float, y: float) -> tuple[int, int]:
        return round(self.ox + x * 2), round(self.oy + y * 2)

    def rect(self, x0, y0, x1, y1, c) -> None:
        (X0, Y0), (X1, Y1) = self._p(x0, y0), self._p(x1, y1)
        if X1 > X0 and Y1 > Y0:
            self.img.rect(X0, Y0, X1 - X0, Y1 - Y0, c)

    def oval(self, x0, y0, x1, y1, c) -> None:
        (X0, Y0), (X1, Y1) = self._p(x0, y0), self._p(x1, y1)
        if X1 > X0 and Y1 > Y0:
            self.img.elli(X0, Y0, X1 - X0, Y1 - Y0, c)

    def rrect(self, x0, y0, x1, y1, r, c) -> None:
        """A rectangle with corners rounded r units."""
        self.rect(x0 + r, y0, x1 - r, y1, c)
        self.rect(x0, y0 + r, x1, y1 - r, c)
        for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)):
            self.oval(cx - r, cy - r, cx + r, cy + r, c)

    def px(self, x, y, c, w: int = 1, h: int = 1) -> None:
        X, Y = self._p(x, y)
        self.img.rect(X, Y, w, h, c)

    def limb(self, x0, y0, x1, y1, width, c) -> None:
        """A thick line with round ends (arms, legs, tubes), `width` units wide."""
        (X0, Y0), (X1, Y1) = self._p(x0, y0), self._p(x1, y1)
        r = max(0, round(width - 1))         # width units = 2 * width px across
        steps = max(abs(X1 - X0), abs(Y1 - Y0), 1)
        for i in range(steps + 1):
            t = i / steps
            self.img.circ(round(X0 + (X1 - X0) * t), round(Y0 + (Y1 - Y0) * t), r, c)

    def line(self, x0, y0, x1, y1, c) -> None:
        (X0, Y0), (X1, Y1) = self._p(x0, y0), self._p(x1, y1)
        self.img.line(X0, Y0, X1, Y1, c)


# --- people ----------------------------------------------------------------

def _head(u: _Units, L: Look, facing: Direction, hy: float) -> None:
    sk, skd = _c(L.skin), _shade(L.skin)
    hr, hrd, hrl = _c(L.hair), _shade(L.hair), _c(L.hair + "_LT")
    long_hair = L.style == "long"
    if long_hair and facing != Direction.UP:            # hair behind the head and shoulders
        u.rrect(2, 4 + hy, 14, 14 + hy, 2, hrd)
    u.oval(2.5, 0.5 + hy, 13.5, 12 + hy, sk)
    u.oval(9.5, 3 + hy, 13.5, 11.5 + hy, skd)
    u.oval(2.5, 0.5 + hy, 12.5, 11.5 + hy, sk)
    if facing == Direction.DOWN:
        u.oval(2, 0 + hy, 14, 8 + hy, hr)               # hair
        u.rect(2, 3.5 + hy, 3.5, (12 if long_hair else 9) + hy, hr)
        u.rect(12.5, 3.5 + hy, 14, (12 if long_hair else 9) + hy, hrd)
        u.rect(3.5, 5 + hy, 12.5, 6.5 + hy, hr)         # fringe
        u.oval(9.5, 1 + hy, 13.5, 6 + hy, hrd)
        u.rect(4.5, 1.5 + hy, 8, 2.5 + hy, hrl)
        for ex in (5, 9.5):                             # eyes, with a glint
            u.rect(ex, 7 + hy, ex + 1.5, 9.5 + hy, Art.EYE)
            u.px(ex, 7 + hy, Art.SHIRT_W)
        u.rect(7, 10.5 + hy, 9, 11 + hy, skd)           # mouth
    elif facing == Direction.UP:
        u.oval(2, 0 + hy, 14, 12 + hy, hr)
        u.oval(9, 1.5 + hy, 14, 11.5 + hy, hrd)
        if long_hair:
            u.rrect(2.5, 6 + hy, 13.5, 14 + hy, 2, hr)
            u.rect(10, 7 + hy, 13.5, 13.5 + hy, hrd)
        u.rect(4, 2 + hy, 8, 3 + hy, hrl)
        u.rect(3.5, 3 + hy, 5, 6 + hy, hrl)
    else:                                               # facing left (right is the mirror)
        u.oval(2, 0 + hy, 14, 8 + hy, hr)
        u.rect(7.5, 2.5 + hy, 14, (13 if long_hair else 10.5) + hy, hr)
        u.rect(11, 3.5 + hy, 14, (12.5 if long_hair else 10) + hy, hrd)
        u.rect(2.5, 4.5 + hy, 6, 6 + hy, hr)
        u.rect(4.5, 1.5 + hy, 9, 2.5 + hy, hrl)
        u.rect(4, 7 + hy, 5.5, 9.5 + hy, Art.EYE)
        u.px(4, 7 + hy, Art.SHIRT_W)
        u.rect(8.5, 6.5 + hy, 10, 9 + hy, sk)           # ear
        u.rect(9.5, 7 + hy, 10, 8.5 + hy, skd)
        u.rect(2, 8.5 + hy, 2.5, 9.5 + hy, sk)          # nose
    if L.style == "cap":                                # Public Safety's peaked cap
        u.oval(2, -0.5 + hy, 14, 6 + hy, Art.GUARD_SH)
        u.rect(2.5, 3 + hy, 13.5, 5 + hy, Art.GUARD)
        u.rect(3, 0.5 + hy, 7, 1.5 + hy, Art.GUARD)
        if facing == Direction.DOWN:
            u.rect(3, 5 + hy, 13, 6 + hy, Art.EYE)      # the peak
            u.rect(7, 3.5 + hy, 9, 4.5 + hy, Art.BADGE)
        elif facing in (Direction.LEFT, Direction.RIGHT):
            u.rect(1, 4.5 + hy, 5, 5.5 + hy, Art.EYE)


def _person(img, ox: int, oy: int, L: Look, facing: Direction, frame: int) -> None:
    """One frame of a person on foot; frame 1 and 2 are the two steps."""
    u = _Units(img, ox, oy)
    sk, skd = _c(L.skin), _shade(L.skin)
    sh, shd = _c(L.shirt), _shade(L.shirt)
    pt, ptd = _c(L.pants), _shade(L.pants)
    side = facing in (Direction.LEFT, Direction.RIGHT)
    by = -0.5 if frame else 0                           # a little bob on each step
    # legs and shoes
    if not side:
        lift = (1 if frame == 1 else 0, 1 if frame == 2 else 0)
        for (x0, x1, dark), up in zip(((5, 7.5, False), (8.5, 11, True)), lift):
            u.rect(x0, 17 + by, x1, 21 - up, pt)
            if dark:
                u.rect(x0 + 1, 17 + by, x1, 21 - up, ptd)
            u.rect(x0 - 0.5 if not dark else x0, 20.5 - up, x1 + (0.5 if dark else 0), 22.5 - up, Art.SHOE)
    else:
        near, far = {0: (0, 0), 1: (-1.5, 1.5), 2: (1.5, -1.5)}[frame]
        u.rect(6 + far, 17 + by, 8.5 + far, 21, ptd)    # far leg
        u.rect(5 + far, 20.5, 8.5 + far, 22.5, Art.SHOE)
        u.rect(7 + near, 17 + by, 9.5 + near, 21, pt)   # near leg
        u.rect(6 + near, 21, 9.5 + near, 22.5, Art.SHOE)
    # body and arms
    if not side:
        swing = {0: 0, 1: 0.5, 2: -0.5}[frame]
        u.rrect(4, 11.5 + by, 12, 18 + by, 2, sh)
        u.rect(10, 12.5 + by, 12, 18 + by, shd)
        u.rect(2.5, 12 + by + swing, 4.5, 16.5 + by + swing, sh)
        u.rect(11.5, 12 + by - swing, 13.5, 16.5 + by - swing, shd)
        u.rect(2.5, 16.5 + by + swing, 4.5, 18 + by + swing, sk)
        u.rect(11.5, 16.5 + by - swing, 13.5, 18 + by - swing, skd)
        if L.collar and facing == Direction.DOWN:
            u.rect(7, 11.5 + by, 9, 13.5 + by, Art.SHIRT_W)
        if L.badge and facing == Direction.DOWN:
            u.rect(5, 13 + by, 6.5, 14.5 + by, Art.BADGE)
        if L.bag and facing == Direction.DOWN:          # backpack straps
            u.rect(4.5, 11.5 + by, 5.5, 16 + by, Art.BAG)
            u.rect(10.5, 11.5 + by, 11.5, 16 + by, Art.BAG)
        if L.bag and facing == Direction.UP:
            u.rrect(4.5, 12 + by, 11.5, 17.5 + by, 1.5, Art.BAG)
            u.rect(5.5, 13 + by, 10.5, 14 + by, Art.BAG_LT)
        if L.lanyard and facing == Direction.DOWN:
            u.rect(6.5, 11.5 + by, 9.5, 12.5 + by, Col.MAROON)
            u.rect(7.5, 12.5 + by, 8.5, 14.5 + by, Col.MAROON)
            u.rect(6.5, 14.5 + by, 9.5, 16.5 + by, Art.SHIRT_W)
            u.rect(7, 15 + by, 9, 15.5 + by, Col.MAROON)
    else:
        swing = {0: 0, 1: 1, 2: -1}[frame]              # the near arm swings against the near leg
        u.rrect(4.5, 11.5 + by, 10.5, 18 + by, 2, sh)
        u.rect(9, 12 + by, 10.5, 18 + by, shd)
        if L.bag:
            u.rrect(9, 12 + by, 12.5, 17 + by, 1, Art.BAG)
            u.rect(9.5, 12.5 + by, 10.5, 16.5 + by, Art.BAG_LT)
        if L.lanyard:
            u.rect(5, 12 + by, 6.5, 14.5 + by, Col.MAROON)
            u.rect(4.5, 14.5 + by, 6.5, 16.5 + by, Art.SHIRT_W)
        if L.badge:
            u.rect(4.5, 13 + by, 5.5, 14.5 + by, Art.BADGE)
        u.rect(6 + swing, 12.5 + by, 8 + swing, 16.5 + by, shd)
        u.rect(6 + swing, 16.5 + by, 8 + swing, 18 + by, sk)
    _head(u, L, facing, by)


# --- the player on the bike ---------------------------------------------------

def _rider(img, ox: int, oy: int, facing: Direction, frame: int, bike: int, bike_sh: int) -> None:
    """The player riding, pedals turning with `frame`. Side on, the bike is
    drawn facing left; front and back, its wheel is end-on under the rider.
    The rider sits higher than someone standing, so their head uses the
    room above (TOP)."""
    u = _Units(img, ox, oy)
    L = LOOKS[0]
    sk = _c(L.skin)
    sh, shd = _c(L.shirt), _shade(L.shirt)
    pt, ptd = _c(L.pants), _shade(L.pants)
    if facing in (Direction.LEFT, Direction.RIGHT):
        cx, cy = 8, 19.2                                # the crank, turning a third each step
        crank = [(0, 1.6), (1.4, -0.8), (-1.4, -0.8)][frame]
        near = (cx + crank[0], cy + crank[1])
        far = (cx - crank[0], cy - crank[1])
        hip = (9.8, 14.6)

        def leg(pedal, col):
            kx = (hip[0] + pedal[0]) / 2 - 2
            ky = (hip[1] + pedal[1]) / 2 - 0.8
            u.limb(hip[0], hip[1], kx, ky, 1.2, col)
            u.limb(kx, ky, pedal[0], pedal[1] - 0.6, 1.0, col)
            u.rect(pedal[0] - 1, pedal[1] - 0.6, pedal[0] + 1, pedal[1] + 0.6, Art.SHOE)

        leg(far, ptd)                                   # the far leg, behind the bike
        for wx in (4, 12):                              # wheels, with spokes you can see through
            u.oval(wx - 3, 16.2, wx + 3, 22.2, Art.TYRE)
            u.oval(wx - 2.2, 17, wx + 2.2, 21.4, Art.METAL)
            u.oval(wx - 1.7, 17.5, wx + 1.7, 20.9, 0)
            u.line(wx - 1.7, 19.2, wx + 1.7, 19.2, Art.METAL)
            u.line(wx, 17.5, wx, 20.9, Art.METAL)
            u.oval(wx - 0.5, 18.7, wx + 0.5, 19.7, Art.HUB)
        u.limb(12, 19.2, cx, cy, 0.5, bike_sh)          # chain stay
        u.limb(cx, cy, 10.5, 15.2, 0.6, bike)           # seat tube
        u.limb(10.5, 15.2, 12, 19.2, 0.5, bike_sh)      # seat stay
        u.limb(cx, cy, 5, 14.8, 0.6, bike)              # down tube
        u.limb(5, 14.8, 10.5, 15.2, 0.6, bike)          # top tube
        u.limb(5, 14.8, 4, 19.2, 0.6, bike_sh)          # fork
        u.limb(5, 14.8, 5, 12.8, 0.5, Art.HUB)          # stem
        u.rect(3.5, 12.3, 5.5, 13.3, Art.SHOE)          # handlebar grip
        u.rect(9.2, 14.2, 12.4, 15.2, Art.SHOE)         # saddle
        u.rrect(6.5, 8.6, 11.5, 15, 2, sh)              # the rider, leaning in
        u.rect(10, 9.2, 11.5, 15, shd)
        u.rrect(9.6, 9, 12.6, 14, 1, Art.BAG)
        u.rect(10.1, 9.5, 11.1, 13.5, Art.BAG_LT)
        u.limb(8, 10.6, 5, 12.6, 1, shd)                # arm to the handlebars
        u.oval(4.2, 12, 5.8, 13.6, sk)
        leg(near, pt)                                   # the near leg, over the bike
        _head(_Units(img, ox - 1, oy - 4), L, Direction.LEFT, 0)
        return
    # front (riding down) or back (riding up)
    down = facing == Direction.DOWN
    lift = 1 if frame == 1 else 0, 1 if frame == 2 else 0
    u.rrect(7, 16.2, 9, 22.4, 0.8, Art.TYRE)            # the wheel, end-on
    u.rect(7.5, 17.2 + frame, 8.5, 18.2 + frame, Art.HUB)   # its spokes turning
    for (x0, x1), up, col in zip(((4.2, 6.6), (9.4, 11.8)), lift, (pt, ptd)):   # legs, on the pedals
        u.rect(x0, 14.5, x1, 19.5 - up, col)
        u.rect(x0 - 0.4, 19 - up, x1 + 0.4, 20.4 - up, Art.SHOE)
    u.rrect(4, 9, 12, 15.5, 2, sh)                      # body, sitting up
    u.rect(10, 10, 12, 15.5, shd)
    if down:
        u.rect(4.5, 9, 5.5, 13.5, Art.BAG)
        u.rect(10.5, 9, 11.5, 13.5, Art.BAG)
    else:
        u.rrect(4.5, 9.5, 11.5, 15, 1.5, Art.BAG)
        u.rect(5.5, 10.5, 10.5, 11.5, Art.BAG_LT)
    u.rect(6.6, 15.2, 9.4, 16.4, bike)                  # mudguard and fork, in the bike's colour
    u.rect(6.6, 16.4, 7.1, 18.4, bike_sh)
    u.rect(8.9, 16.4, 9.4, 18.4, bike_sh)
    u.rect(7.4, 14.4, 8.6, 15.4, Art.HEADLIGHT if down else Art.TAILLIGHT)
    u.rect(1.5, 14.6, 14.5, 15.4, Art.METAL)            # handlebars, wider than the rider
    u.rect(1, 14.2, 2.6, 16, Art.SHOE)
    u.rect(13.4, 14.2, 15, 16, Art.SHOE)
    u.limb(4.4, 11, 2, 14.6, 0.9, sh)                   # arms down to the grips
    u.limb(11.6, 11, 14, 14.6, 0.9, shd)
    u.oval(1.2, 13.6, 2.8, 15.2, sk)
    u.oval(13.2, 13.6, 14.8, 15.2, sk)
    _head(_Units(img, ox, oy - 4), L, facing, 0)


# --- the vans ------------------------------------------------------------------

def van_uv(van: int, view: str) -> tuple[int, int, int, int]:
    """(u, v, w, h) of a van picture: view is "side" (facing right), "front"
    or "back". Same sizes as today's vans, doubled."""
    v = VAN_V + van * 48
    return {"side": (0, v, 64, 48), "front": (64, v, 32, 48), "back": (96, v, 32, 48)}[view]


def _van_colours(van: int) -> tuple[int, int, int]:
    """body, its shade, the stripe"""
    if van == SHUTTLE_VAN:
        return Art.VAN, Art.VAN_SH, Col.MAROON
    return Col.MAROON, Art.MAROON_SH, Art.VAN


def _van_side(img, u: int, v: int, van: int) -> None:
    body, shade, stripe = _van_colours(van)
    for wx in (15, 49):                                 # wheel arches
        img.circ(u + wx, v + 39, 9, Art.OUTLINE)
    img.rect(u + 2, v + 14, 46, 26, body)               # the body: roof, then the sloping front
    img.tri(u + 46, v + 14, u + 46, v + 26, u + 56, v + 26, body)
    img.rect(u + 46, v + 26, 15, 14, body)
    img.rect(u + 4, v + 12, 41, 3, body)
    img.rect(u + 2, v + 35, 59, 5, shade)
    img.rect(u + 4, v + 12, 41, 2, Art.VAN_SH if van == SHUTTLE_VAN else Art.MAROON_LT)
    for x in (6, 19, 32):                               # side windows
        img.rect(u + x, v + 16, 11, 9, Art.VAN_GLASS_DK)
        img.rect(u + x + 1, v + 17, 9, 7, Art.VAN_GLASS)
        img.line(u + x + 2, v + 22, u + x + 6, v + 17, Art.VAN_GLASS_HI)
    img.tri(u + 46, v + 16, u + 46, v + 25, u + 54, v + 25, Art.VAN_GLASS_DK)   # windscreen
    img.tri(u + 47, v + 18, u + 47, v + 24, u + 52, v + 24, Art.VAN_GLASS)
    img.rect(u + 31, v + 15, 1, 20, shade)              # the sliding door
    img.rect(u + 2, v + 28, 59, 3, stripe)
    img.rect(u + 49, v + 22, 2, 3, Art.OUTLINE)         # mirror
    img.rect(u + 58, v + 28, 3, 3, Art.HEADLIGHT)
    img.rect(u + 2, v + 27, 2, 5, Art.TAILLIGHT)
    img.rect(u + 57, v + 36, 5, 3, Art.BUMPER)
    img.rect(u + 1, v + 36, 4, 3, Art.BUMPER)
    for wx in (15, 49):
        img.circ(u + wx, v + 40, 7, Art.TYRE)
        img.circ(u + wx, v + 40, 3, Art.HUB)
        img.pset(u + wx, v + 40, Art.TYRE)


def _van_end(img, u: int, v: int, van: int, front: bool) -> None:
    body, shade, stripe = _van_colours(van)
    img.rect(u + 4, v + 40, 5, 7, Art.TYRE)             # tyres
    img.rect(u + 23, v + 40, 5, 7, Art.TYRE)
    img.rect(u + 3, v + 10, 26, 32, body)
    img.rect(u + 5, v + 8, 22, 3, body)
    img.rect(u + 5, v + 8, 22, 2, Art.VAN_SH if van == SHUTTLE_VAN else Art.MAROON_LT)
    img.rect(u + 24, v + 10, 5, 32, shade)              # the shaded side
    img.rect(u + 5, v + 13, 22, 11, Art.VAN_GLASS_DK)   # windscreen or rear window
    img.rect(u + 6, v + 14, 20, 9, Art.VAN_GLASS)
    img.line(u + 8, v + 21, u + 13, v + 15, Art.VAN_GLASS_HI)
    img.rect(u + 3, v + 28, 26, 3, stripe)
    img.rect(u + 3, v + 38, 26, 4, Art.BUMPER)
    lamp = Art.HEADLIGHT if front else Art.TAILLIGHT
    img.rect(u + 5, v + 32, 4, 3 if front else 5, lamp)
    img.rect(u + 23, v + 32, 4, 3 if front else 5, lamp)
    if front:
        img.rect(u + 12, v + 33, 8, 4, Art.BUMPER)      # grille
        img.rect(u + 1, v + 18, 2, 3, Art.OUTLINE)      # mirrors
        img.rect(u + 29, v + 18, 2, 3, Art.OUTLINE)
    else:
        img.rect(u + 13, v + 33, 6, 3, Art.VAN)         # number plate


# --- the sheet -------------------------------------------------------------------

def frame_uv(sprite: int, facing: Direction, frame: int) -> tuple[int, int]:
    """Top-left of a person's frame on the sheet (same numbering as
    placeholder_art.character_uv)."""
    return (facing.sprite_index * 3 + frame) * FRAME_W, sprite * FRAME_H


_sheet: pyxel.Image | None = None


def sheet() -> pyxel.Image:
    global _sheet
    if _sheet is None:
        _sheet = _build()
    return _sheet


def _build() -> pyxel.Image:
    flat = pyxel.Image(COLS * FRAME_W, VAN_V + 2 * 48)
    flat.cls(Col.BLACK)
    left, right = Direction.LEFT, Direction.RIGHT
    for sprite, look in enumerate(LOOKS):
        for d in (Direction.DOWN, Direction.UP, left):
            for f in range(3):
                u, v = frame_uv(sprite, d, f)
                _person(flat, u, v + TOP, look, d, f)
    for sprite, (bike, bike_sh) in ((BIKE_SPRITE, (Art.BIKE, Art.BIKE_SH)),
                                     (MAROON_BIKE_SPRITE, (Col.MAROON, Art.MAROON_SH))):
        for d in (Direction.DOWN, Direction.UP, left):
            for f in range(3):
                u, v = frame_uv(sprite, d, f)
                _rider(flat, u, v + TOP, d, f, bike, bike_sh)
    one = pyxel.Image(FRAME_W, FRAME_H)                 # (Pyxel can't copy a picture onto itself)
    for sprite in range(MAROON_BIKE_SPRITE + 1):        # facing right: facing left, flipped
        for f in range(3):
            lu, lv = frame_uv(sprite, left, f)
            ru, rv = frame_uv(sprite, right, f)
            one.blt(0, 0, flat, lu, lv, FRAME_W, FRAME_H)
            flat.blt(ru, rv, one, 0, 0, -FRAME_W, FRAME_H)
    for van in (SHUTTLE_VAN, RAM_VAN):
        u, v, _, _ = van_uv(van, "side")
        _van_side(flat, u, v, van)
        u, v, _, _ = van_uv(van, "front")
        _van_end(flat, u, v, van, True)
        u, v, _, _ = van_uv(van, "back")
        _van_end(flat, u, v, van, False)
    # one outline round everything: the drawing shifted a pixel each way in
    # the outline colour, then the drawing itself on top
    out = pyxel.Image(flat.width, flat.height)
    out.cls(Col.BLACK)
    for c in range(1, len(pyxel.colors)):
        out.pal(c, Art.OUTLINE)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        out.blt(dx, dy, flat, 0, 0, flat.width, flat.height, Col.BLACK)
    out.pal()
    out.blt(0, 0, flat, 0, 0, flat.width, flat.height, Col.BLACK)
    return out
