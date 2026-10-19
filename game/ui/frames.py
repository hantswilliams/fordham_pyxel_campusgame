"""Boxes, tabs and bubbles at full detail (decisions/0045, step 4): rounded
corners, thin rims and a soft drop under each box, as in the approved
mockup. Every function takes layout pixels, like the rest of the drawing,
with the camera applied (display.camera), and draws on the full-size
screen under the layer's own drawing and text (display.queue_full), so the
words and icons a scene draws afterwards go on top.

On a screen that isn't doubled (DISPLAY_SCALE 1: tests and tools) each one
draws a plain version straight away instead.
"""

from __future__ import annotations

import pyxel

from game.config import Art, Col
from game.gfx import display

RIM = Art.OUTLINE


def _rrect(img, x: int, y: int, w: int, h: int, r: int, col: int) -> None:
    """A filled rectangle with corners rounded r pixels (full-size pixels)."""
    r = max(0, min(r, w // 2, h // 2))
    if w <= 0 or h <= 0:
        return
    img.rect(x + r, y, w - 2 * r, h, col)
    img.rect(x, y + r, w, h - 2 * r, col)
    if r:
        for cx, cy in ((x + r, y + r), (x + w - 1 - r, y + r), (x + r, y + h - 1 - r),
                       (x + w - 1 - r, y + h - 1 - r)):
            img.circ(cx, cy, r, col)


def _queue(draw, x: float, y: float) -> bool:
    """Queue draw(image, X, Y) with (X, Y) the full-size spot for layout (x, y)."""
    cx, cy = display._cam
    s = display.scale
    X, Y = round((x - cx) * s), round((y - cy) * s)
    return display.queue_full(lambda full: draw(full, X, Y))


def box(x: float, y: float, w: float, h: float, page: int = Art.UI_PAGE,
        frame: int = Art.UI_FRAME, radius: int = 7, drop: bool = True) -> None:
    """The house box: a soft drop, a dark rim, a light frame, the page."""
    s = display.scale
    W, H, R = round(w * s), round(h * s), radius * 2

    def draw(full, X, Y):
        if drop:
            _rrect(full, X, Y + 4, W, H, R, RIM)
        _rrect(full, X, Y, W, H, R, RIM)
        _rrect(full, X + 2, Y + 2, W - 4, H - 4, R - 2, frame)
        _rrect(full, X + 5, Y + 5, W - 10, H - 10, R - 5, page)
    if not _queue(draw, x, y):
        pyxel.rect(x, y, w, h, page)
        pyxel.rectb(x, y, w, h, Col.NAVY)
        pyxel.rectb(x + 1, y + 1, w - 2, h - 2, frame)


def pill(x: float, y: float, w: float, h: float, fill: int, rim: int | None = RIM,
         shine: int | None = None, radius: int | None = None, drop: int | None = None) -> None:
    """A rounded bar: name tabs, banners, buttons, chips. `shine` is a light
    line along its top, `drop` a darker copy just below it."""
    s = display.scale
    W, H = round(w * s), round(h * s)
    R = min(H // 2, radius * 2) if radius is not None else H // 2

    def draw(full, X, Y):
        if drop is not None:
            _rrect(full, X, Y + 3, W, H, R, drop)
        if rim is not None:
            _rrect(full, X, Y, W, H, R, rim)
            _rrect(full, X + 2, Y + 2, W - 4, H - 4, max(0, R - 2), fill)
        else:
            _rrect(full, X, Y, W, H, R, fill)
        if shine is not None:
            full.rect(X + max(R, 4), Y + 4, W - 2 * max(R, 4), 2, shine)
    if not _queue(draw, x, y):
        pyxel.rect(x, y, w, h, fill)
        if rim is not None:
            pyxel.rectb(x, y, w, h, Col.NAVY)


def header(x: float, y: float, w: float, h: float, fill: int = Col.MAROON, radius: int = 4,
           shine: int | None = Art.MAROON_LT) -> None:
    """A heading band inside a box: rounded at the top, square below."""
    s = display.scale
    W, H, R = round(w * s), round(h * s), radius * 2

    def draw(full, X, Y):
        _rrect(full, X, Y, W, H, R, fill)
        full.rect(X, Y + H - R, W, R, fill)
        if shine is not None:
            full.rect(X + R, Y + 3, W - 2 * R, 2, shine)
    if not _queue(draw, x, y):
        pyxel.rect(x, y, w, h, fill)


def picture(img, w: int, h: int, x: float, y: float, clip=None) -> bool:
    """A full-size picture (w x h full-size pixels) with a dark rounded rim,
    its top-left at layout (x, y), cut to `clip` (layout x, y, w, h) if
    given. False on a screen that isn't doubled (draw today's picture)."""
    s = display.scale
    C = None if clip is None else tuple(round(v * s) for v in clip)

    def draw(full, X, Y):
        if C:
            full.clip(*C)
        _rrect(full, X - 2, Y - 2, w + 4, h + 4, 6, RIM)
        full.blt(X, Y, img, 0, 0, w, h)
        if C:
            full.clip()
    return _queue(draw, x, y)


def disc(cx: float, cy: float, r: float, fill: int, rim: int | None = RIM,
         ring: int | None = None) -> None:
    """A round stamp or badge centred at (cx, cy), radius r layout pixels."""
    s = display.scale
    R = round(r * s)

    def draw(full, X, Y):
        if rim is not None:
            full.circ(X, Y, R, rim)
            full.circ(X, Y, R - 2, fill)
        else:
            full.circ(X, Y, R, fill)
        if ring is not None:
            full.circb(X, Y, R - 6, ring)
            full.circb(X, Y, R - 7, ring)
    if not _queue(draw, cx, cy):
        pyxel.circ(cx, cy, r, fill)
        if rim is not None:
            pyxel.circb(cx, cy, r, Col.NAVY)
        if ring is not None:
            pyxel.circb(cx, cy, r - 3, ring)


def dots(cx: float, cy: float, r: float, col: int, n: int = 16) -> None:
    """A dotted circle: a stamp not yet earned."""
    import math
    s = display.scale
    R = r * s

    def draw(full, X, Y):
        for i in range(n):
            a = 2 * math.pi * i / n
            full.rect(round(X + R * math.cos(a)) - 1, round(Y + R * math.sin(a)) - 1, 2, 2, col)
    if not _queue(draw, cx, cy):
        for i in range(n):
            a = 2 * math.pi * i / n
            pyxel.pset(cx + round(r * math.cos(a)), cy + round(r * math.sin(a)), col)


def art(x: float, y: float, draw) -> bool:
    """Queue a small picture drawn at full detail: draw(u) gets a pen that
    works in layout units (2 full-size pixels each, fractions allowed) from
    (x, y), like people_art's. False on a screen that isn't doubled."""
    from game.gfx.people_art import _Units
    return _queue(lambda full, X, Y: draw(_Units(full, X, Y)), x, y)


def blit(img, u: int, v: int, w: int, h: int, x: float, y: float) -> bool:
    """Queue part of a layout-size picture, doubled, in order with the boxes
    (a map under its pins). False on a screen that isn't doubled."""
    s = display.scale
    return _queue(lambda full, X, Y: full.blt(X + w * (s - 1) / 2, Y + h * (s - 1) / 2, img, u, v, w, h,
                                              scale=s), x, y)


def rect(x: float, y: float, w: float, h: float, col: int) -> None:
    """A plain rectangle, in order with the boxes (a highlight, a rule)."""
    s = display.scale
    W, H = round(w * s), round(h * s)
    if not _queue(lambda full, X, Y: full.rect(X, Y, W, H, col), x, y):
        pyxel.rect(x, y, w, h, col)


def bubble(x: float, y: float, w: float, h: float) -> None:
    """A little white speech bubble with a tail pointing down (the "!" and
    "?" over people's heads, the van's BEEP)."""
    s = display.scale
    W, H = round(w * s), round(h * s)

    def draw(full, X, Y):
        cx = X + W // 2
        full.tri(cx - 5, Y + H - 2, cx + 5, Y + H - 2, cx, Y + H + 5, RIM)
        _rrect(full, X, Y, W, H, 7, RIM)
        _rrect(full, X + 2, Y + 2, W - 4, H - 4, 5, Art.UI_PAGE)
        full.tri(cx - 3, Y + H - 3, cx + 3, Y + H - 3, cx, Y + H + 2, Art.UI_PAGE)
    if not _queue(draw, x, y):
        pyxel.rect(x, y, w, h, Col.WHITE)
        pyxel.rectb(x, y, w, h, Col.NAVY)


def arrow(x: float, y: float, col: int = Col.MAROON, down: bool = True) -> None:
    """A small triangle pointing down (more to read) or up, 8 x 4 layout px."""
    s = display.scale

    def draw(full, X, Y):
        if down:
            full.tri(X, Y, X + 8 * s, Y, X + 4 * s, Y + 4 * s, col)
        else:
            full.tri(X, Y + 4 * s, X + 8 * s, Y + 4 * s, X + 4 * s, Y, col)
    if not _queue(draw, x, y):
        if down:
            pyxel.tri(x, y, x + 8, y, x + 4, y + 4, col)
        else:
            pyxel.tri(x, y + 4, x + 8, y + 4, x + 4, y, col)


def cursor(x: float, y: float, col: int = Col.MAROON) -> None:
    """The choice cursor: a small triangle pointing right, 5 x 8 layout px."""
    s = display.scale
    if not _queue(lambda full, X, Y: full.tri(X, Y, X, Y + 8 * s, X + 5 * s, Y + 4 * s, col), x, y):
        pyxel.tri(x, y, x, y + 8, x + 5, y + 4, col)


def dim(col: int = Col.NAVY) -> None:
    """Dim the whole screen behind a card or menu: a fine checker of `col`."""
    def draw(full, X, Y):
        full.dither(0.5)
        full.rect(0, 0, full.width, full.height, col)
        full.dither(1.0)
    if not _queue(draw, 0, 0):
        pyxel.dither(0.5)
        pyxel.rect(0, 0, pyxel.width, pyxel.height, col)
        pyxel.dither(1.0)
