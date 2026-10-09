"""Placeholder art for the opening sequence (decisions/0016 Part 2), drawn
with Pyxel shapes each frame. Side views, unlike the top-down campus.
The train is generic on purpose: no transit logos (D-0009).

Each draw function takes `p` (0..1 progress through the scene), `f` (frames
since the scene started) and `length` (scene length in frames)."""

import pyxel

from game.config import SCREEN_W, Col
from game.systems.intro_timeline import scroll_offset

from .placeholder_art import CHAR_IMAGE_BANK, character_uv
from game.world.directions import Direction

PLAYER = 0


def _char(x: float, y: float, sprite: int, facing: Direction, frame: int = 0) -> None:
    u, v = character_uv(sprite, facing, frame)
    pyxel.blt(int(x), int(y), CHAR_IMAGE_BANK, u, v, 16, 16, Col.BLACK)


def _walk_frame(f: int) -> int:
    return 1 + (f // 6) % 2


def _centered(y: int, s: str, col: int, cx: int = SCREEN_W // 2) -> None:
    pyxel.text(cx - len(s) * 2, y, s, col)


# --- 1. on the train ---------------------------------------------------------

def _window(wx: int, wy: int, ww: int, wh: int, off: float) -> None:
    pyxel.rect(wx, wy, ww, wh, Col.LIGHT_BLUE)
    pyxel.clip(wx, wy, ww, wh)
    # far skyline (slow)
    base = int(off * 0.5)
    first = base // 22
    for k in range(first - 1, first + ww // 22 + 2):
        bx = wx + k * 22 - base
        h = 12 + (k * 37) % 20
        col = (Col.BROWN, Col.ORANGE, Col.DARK_BLUE, Col.GRAY)[k % 4]
        pyxel.rect(bx, wy + wh - h, 19, h, col)
        for wy2 in range(wy + wh - h + 3, wy + wh - 2, 5):
            for wx2 in range(bx + 3, bx + 17, 5):
                pyxel.pset(wx2, wy2, Col.YELLOW)
    # near trackside poles (fast)
    base2 = int(off)
    for k in range(base2 // 40 - 1, base2 // 40 + ww // 40 + 2):
        px = wx + k * 40 - base2
        pyxel.line(px, wy + 6, px, wy + wh, Col.NAVY)
        pyxel.line(px - 3, wy + 8, px + 3, wy + 8, Col.NAVY)
    pyxel.clip()
    pyxel.rectb(wx - 1, wy - 1, ww + 2, wh + 2, Col.NAVY)
    pyxel.rectb(wx - 2, wy - 2, ww + 4, wh + 4, Col.WHITE)


def draw_train(p: float, f: int, length: int) -> None:
    moving = p < 0.97
    bob = 1 if moving and (f // 8) % 2 else 0
    pyxel.cls(Col.GRAY)
    pyxel.rect(0, 0, SCREEN_W, 20, Col.WHITE)
    pyxel.line(0, 20, SCREEN_W, 20, Col.DARK_BLUE)
    # LED next-stop sign
    pyxel.rect(6, 4, 116, 12, Col.NAVY)   # left, clear of the "Z: NEXT X: SKIP" hint
    if (f // 20) % 4 != 3:
        _centered(7, "NEXT STOP: FORDHAM", Col.ORANGE, cx=64)
    off = scroll_offset(p, length, speed=5.0)
    for wx in (12, 134):
        _window(wx, 28 + bob, 110, 46, off)
    pyxel.rect(0, 80, SCREEN_W, 3, Col.DARK_BLUE)
    pyxel.rect(0, 112, SCREEN_W, 30, Col.BROWN)
    pyxel.line(0, 112, SCREEN_W, 112, Col.NAVY)
    # rows of seats, passengers facing right (direction of travel)
    seats = [(14, 2), (74, None), (134, PLAYER), (194, 3)]
    for sx, who in seats:
        pyxel.rect(sx, 84 + bob, 5, 26, Col.DARK_BLUE)        # seat back
        if who is not None:
            _char(sx + 6, 86 + bob, who, Direction.RIGHT)
        pyxel.rect(sx, 101 + bob, 26, 7, Col.DARK_BLUE)        # cushion
        pyxel.rect(sx + 20, 108 + bob, 3, 4, Col.NAVY)        # leg
    if not moving:
        _centered(64, "FORDHAM", Col.WHITE, cx=189)


# --- 2. Fordham station -------------------------------------------------------

def draw_station(p: float, f: int, length: int) -> None:
    pyxel.cls(Col.LIGHT_BLUE)
    # skyline beyond the station
    for i, (bx, h, col) in enumerate(((130, 40, Col.BROWN), (160, 52, Col.ORANGE),
                                      (196, 34, Col.BROWN), (222, 46, Col.DARK_BLUE))):
        pyxel.rect(bx, 96 - h, 28, h, col)
    # canopy and posts
    pyxel.rect(0, 10, SCREEN_W, 8, Col.GREEN)
    pyxel.line(0, 18, SCREEN_W, 18, Col.NAVY)
    for px in (140, 198, 250):
        pyxel.rect(px, 18, 3, 86, Col.NAVY)
    # station name sign hanging from the canopy
    pyxel.line(166, 18, 166, 26, Col.NAVY)
    pyxel.line(200, 18, 200, 26, Col.NAVY)
    pyxel.rect(154, 26, 58, 13, Col.DARK_BLUE)
    pyxel.rectb(154, 26, 58, 13, Col.WHITE)
    _centered(30, "FORDHAM", Col.WHITE, cx=183)
    # the train, stopped at the platform
    pyxel.rect(-4, 34, 128, 64, Col.WHITE)
    pyxel.rect(-4, 36, 128, 2, Col.GRAY)
    pyxel.rect(-4, 76, 128, 4, Col.DARK_BLUE)
    for wx in (4, 34, 104):
        pyxel.rect(wx, 46, 22, 16, Col.NAVY)
        pyxel.line(wx + 2, 48, wx + 8, 48, Col.LIGHT_BLUE)
    door_open = p > 0.12
    pyxel.rect(66, 42, 30, 56, Col.NAVY if door_open else Col.GRAY)
    if not door_open:
        pyxel.line(81, 42, 81, 97, Col.DARK_BLUE)
        pyxel.rect(70, 48, 8, 14, Col.NAVY)
        pyxel.rect(84, 48, 8, 14, Col.NAVY)
    pyxel.rect(-4, 98, 128, 6, Col.NAVY)
    # platform with the yellow safety edge
    pyxel.rect(0, 104, SCREEN_W, 40, Col.GRAY)
    pyxel.rect(0, 104, SCREEN_W, 2, Col.YELLOW)
    # exit stairs
    pyxel.rect(226, 64, 30, 40, Col.BROWN)
    for sy in range(70, 104, 6):
        pyxel.line(226, sy, 255, sy, Col.NAVY)
    pyxel.rect(228, 52, 24, 9, Col.DARK_BLUE)
    pyxel.text(232, 54, "EXIT", Col.WHITE)
    # people
    _char(170, 90, 4, Direction.LEFT)
    if 0.12 < p <= 0.26:
        _char(73, 82, PLAYER, Direction.DOWN)
    elif p > 0.26:
        t = min(1.0, (p - 0.26) / 0.66)
        x = 73 + (236 - 73) * t
        y = 82 + min(8.0, t * 60)
        if t < 1.0:
            _char(x, y, PLAYER, Direction.RIGHT, _walk_frame(f))


# --- 3. Webster Avenue, outside the gate -------------------------------------

GATE_X = 197  # pedestrian gate opening, between the first two pillars


def _pillar(x: int) -> None:
    pyxel.rect(x, 56, 11, 46, Col.GRAY)
    pyxel.rect(x - 1, 54, 13, 4, Col.WHITE)
    for sy in range(60, 100, 6):
        pyxel.line(x, sy, x + 10, sy, Col.DARK_BLUE)
        pyxel.pset(x + 3 + (sy // 6) % 4, sy + 3, Col.BROWN)


def draw_street(p: float, f: int, length: int) -> None:
    pyxel.cls(Col.LIGHT_BLUE)
    # off-campus apartment buildings (left)
    for bx, w, h, col in ((0, 40, 70, Col.BROWN), (40, 34, 56, Col.ORANGE), (74, 22, 64, Col.BROWN)):
        pyxel.rect(bx, 100 - h, w, h, col)
        for wy in range(100 - h + 6, 94, 10):
            for wx in range(bx + 4, bx + w - 4, 8):
                pyxel.rect(wx, wy, 4, 5, Col.NAVY)
    # campus behind the fence (right): stone building with a tower, trees
    pyxel.rect(200, 22, 56, 50, Col.GRAY)
    pyxel.rect(214, 2, 22, 22, Col.GRAY)
    for tx in range(216, 236, 4):
        pyxel.line(tx, 4, tx, 20, Col.DARK_BLUE)
    for wx in range(204, 254, 9):
        pyxel.rect(wx, 32, 4, 8, Col.NAVY)
        pyxel.rect(wx, 48, 4, 8, Col.NAVY)
    for cx, cy, r in ((112, 56, 16), (138, 50, 18), (170, 58, 15), (192, 60, 12)):
        pyxel.circ(cx, cy, r, Col.GREEN)
        pyxel.circ(cx - 4, cy - 4, r // 3, Col.LIME)
        pyxel.rect(cx - 2, cy + r - 4, 4, 30 - r, Col.BROWN)
    # guard booth (green roof) behind the fence
    pyxel.rect(150, 74, 22, 26, Col.WHITE)
    pyxel.rect(154, 78, 14, 8, Col.LIGHT_BLUE)
    pyxel.tri(147, 74, 175, 74, 161, 64, Col.GREEN)
    # iron fence
    pyxel.line(96, 72, SCREEN_W, 72, Col.NAVY)
    pyxel.line(96, 96, SCREEN_W, 96, Col.NAVY)
    for fx in range(96, SCREEN_W, 4):
        if not (GATE_X - 1 < fx < GATE_X + 12):  # keep the pedestrian gate open
            pyxel.line(fx, 68, fx, 100, Col.NAVY)
    # maroon Fordham sign on the fence
    pyxel.rect(100, 76, 44, 18, Col.MAROON)
    pyxel.rectb(100, 76, 44, 18, Col.WHITE)
    _centered(79, "FORDHAM", Col.WHITE, cx=122)
    _centered(87, "ROSE HILL", Col.PEACH, cx=122)
    # stone pillars: pedestrian gate between the first two, vehicle gate after
    for px in (186, GATE_X + 12, 244):
        _pillar(px)
    # sidewalk (tan, like walkways in the game) and road (gray)
    pyxel.rect(0, 100, SCREEN_W, 18, Col.PEACH)
    for sx in range(0, SCREEN_W, 16):
        pyxel.line(sx, 100, sx, 117, Col.GRAY)
    pyxel.rect(0, 118, SCREEN_W, 2, Col.WHITE)
    pyxel.rect(0, 120, SCREEN_W, 24, Col.GRAY)
    for dx in range(0, SCREEN_W, 24):
        pyxel.rect(dx + 4, 129, 12, 2, Col.YELLOW)
    # a maroon Ram Van drives past
    if 0.2 < p < 0.6:
        vx = SCREEN_W - (p - 0.2) / 0.4 * (SCREEN_W + 50)
        pyxel.rect(vx, 112, 44, 16, Col.MAROON)
        pyxel.rect(vx + 4, 115, 10, 6, Col.LIGHT_BLUE)
        pyxel.rect(vx + 18, 115, 22, 6, Col.LIGHT_BLUE)
        pyxel.circ(vx + 9, 128, 3, Col.NAVY)
        pyxel.circ(vx + 35, 128, 3, Col.NAVY)
    # Bert, the guard, waits by the gate to check IDs
    _char(GATE_X + 26, 88, 5, Direction.LEFT)
    # the player walks to the gate, then turns to face it
    t = min(1.0, p / 0.7)
    x = -16 + (GATE_X - 2 + 16) * t
    if t < 1.0:
        _char(x, 88, PLAYER, Direction.RIGHT, _walk_frame(f))
    else:
        _char(x, 88, PLAYER, Direction.UP)


SCENE_ART = {"train": draw_train, "station": draw_station, "street": draw_street}
