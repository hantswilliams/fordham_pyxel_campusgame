"""Crisp text (decisions/0038): the screen has twice as many pixels as the
game's layout, and only the text uses them.

The game is still laid out and drawn at 384 x 288 (config.SCREEN_W/H): every
scene draws as before, into the top-left corner of a 768 x 576 Pyxel screen.
At the end of each layer that picture is doubled into a full-size image, and
the reading-font text is drawn over it at full size, so letters get four
times the pixels while the art looks exactly as it did.

Text calls (game/ui/font.py) are queued while a layer draws, with the camera
offset and clip rectangle in force when they were made, and drawn when the
layer is doubled. Each scene in the stack is a layer, so a menu or card drawn
over the world also covers the world's text.

With config.DISPLAY_SCALE = 1 nothing here is used and text is drawn
straight onto the 384 x 288 screen (tests and tools that read the screen).
"""

from __future__ import annotations

import pyxel

from game import config

W, H = config.SCREEN_W, config.SCREEN_H
KEY_RGB = 0xFF00FE          # never drawn by the game: marks "nothing drawn here" in a layer

active = False
scale = 1
_key = 0
_final: pyxel.Image | None = None
_layer: pyxel.Image | None = None
_cam = (0, 0)
_clip: tuple[int, int, int, int] | None = None
_texts: list[tuple] = []


def setup(display_scale: int) -> None:
    """Call once after pyxel.init (screen = W*scale x H*scale) and the palette."""
    global active, scale, _key, _final, _layer
    scale = display_scale
    active = scale > 1
    if not active:
        return
    pyxel.colors.append(KEY_RGB)
    _key = len(pyxel.colors) - 1
    _final = pyxel.Image(W * scale, H * scale)
    _layer = pyxel.Image(W, H)


def camera(x: float = 0, y: float = 0) -> None:
    """pyxel.camera, remembered so queued text lands in the right place."""
    global _cam
    _cam = (x, y)
    pyxel.camera(x, y)


def clip(x: float | None = None, y: float = 0, w: float = 0, h: float = 0) -> None:
    """pyxel.clip, remembered so queued text is clipped the same way."""
    global _clip
    if x is None:
        _clip = None
        pyxel.clip()
    else:
        _clip = (x, y, w, h)
        pyxel.clip(x, y, w, h)


def queue_text(x: float, y: float, s: str, col: int, font, cell: int, dy: int) -> bool:
    """Queue `s` for drawing at full size. (x, y) is in layout pixels; each
    character takes `cell` screen pixels. Returns False when not active."""
    if not active:
        return False
    _texts.append((x - _cam[0], y - _cam[1], s, col, font, cell, dy, _clip))
    return True


def begin() -> None:
    global _cam, _clip
    if not active:
        return
    _cam, _clip = (0, 0), None
    _texts.clear()
    _final.cls(config.Col.BLACK)
    pyxel.camera()
    pyxel.clip()
    pyxel.rect(0, 0, W, H, _key)


def layer() -> None:
    """Finish the layer drawn so far, before an overlay draws over it. With
    no text waiting the overlay can simply draw over it, which saves doubling
    the picture twice (the costly part, about 4 ms)."""
    if active and _texts:
        _flush()


def _flush() -> None:
    """Double the layer onto the full-size image, draw its text over it, and
    clear the drawing area for the next layer."""
    global _cam, _clip
    pyxel.camera()
    pyxel.clip()
    pyxel.dither(1.0)
    _layer.blt(0, 0, pyxel.screen, 0, 0, W, H)
    # blt scales around the centre of the destination rectangle
    _final.blt(W * (scale - 1) / 2, H * (scale - 1) / 2, _layer, 0, 0, W, H, _key, scale=scale)
    for x, y, s, col, font, cell, dy, rect in _texts:
        if rect:
            cx, cy, cw, ch = rect
            _final.clip(cx * scale, cy * scale, cw * scale, ch * scale)
        px, py = round(x * scale), round(y * scale) + dy
        for i, c in enumerate(s):
            if c != " ":
                _final.text(px + i * cell, py, c, col, font)
        if rect:
            _final.clip()
    _texts.clear()
    _cam, _clip = (0, 0), None
    pyxel.rect(0, 0, W, H, _key)


def end() -> None:
    """Finish the frame: put the full-size image on the screen."""
    if not active:
        return
    _flush()
    pyxel.blt(0, 0, _final, 0, 0, W * scale, H * scale)
