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
CHAR_SCALE = 2           # people are drawn 2x in the intro (decisions/0019 Part 1)
CHAR_SIZE = 16 * CHAR_SCALE
TRAIN_SCALE = 3          # the train is a close-up, so people are 3x there
SCENE_BOTTOM = 130       # the caption box covers everything below this (textbox.box_top)


def _char(x: float, y: float, sprite: int, facing: Direction, frame: int = 0,
          scale: int = CHAR_SCALE) -> None:
    """Draw a character with its top-left at (x, y), 16*scale pixels square.
    Pyxel scales around the centre of the source rectangle, hence the offset."""
    u, v = character_uv(sprite, facing, frame)
    off = (16 * scale - 16) / 2
    pyxel.blt(int(x + off), int(y + off), CHAR_IMAGE_BANK, u, v, 16, 16, Col.BLACK,
              scale=scale)


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
    """Close-up inside the carriage: passengers at 3x fill their seats, heads
    level with the windows. Everything sits above the caption box."""
    moving = p < 0.97
    bob = 1 if moving and (f // 8) % 2 else 0
    pyxel.cls(Col.GRAY)
    pyxel.rect(0, 0, SCREEN_W, 18, Col.WHITE)
    pyxel.line(0, 18, SCREEN_W, 18, Col.DARK_BLUE)
    # LED next-stop sign
    pyxel.rect(6, 3, 116, 12, Col.NAVY)   # left, clear of the "Z: NEXT X: SKIP" hint
    if (f // 20) % 4 != 3:
        _centered(6, "NEXT STOP: FORDHAM", Col.ORANGE, cx=64)
    off = scroll_offset(p, length, speed=5.0)
    for wx in (8, 132):
        _window(wx, 30 + bob, 116, 34, off)
    pyxel.rect(0, 67, SCREEN_W, 2, Col.DARK_BLUE)            # window sill
    pyxel.rect(0, 110, SCREEN_W, SCENE_BOTTOM - 110, Col.BROWN)  # floor
    pyxel.line(0, 110, SCREEN_W, 110, Col.NAVY)
    # four seats, passengers facing right (direction of travel)
    seats = [(2, 2), (66, None), (130, PLAYER), (194, 3)]
    for sx, who in seats:
        pyxel.rect(sx, 56 + bob, 8, 50, Col.DARK_BLUE)       # seat back
        pyxel.rect(sx + 1, 58 + bob, 2, 46, Col.LIGHT_BLUE)  # highlight
        pyxel.rect(sx, 52 + bob, 10, 6, Col.DARK_BLUE)       # headrest
        if who is not None:
            _char(sx + 8, 50 + bob, who, Direction.RIGHT, scale=TRAIN_SCALE)
        pyxel.rect(sx, 90 + bob, 58, 10, Col.DARK_BLUE)      # cushion, over the legs
        pyxel.line(sx, 90 + bob, sx + 57, 90 + bob, Col.LIGHT_BLUE)
        pyxel.rect(sx + 48, 100 + bob, 5, 10, Col.NAVY)       # leg
    if not moving:
        _centered(40, "FORDHAM", Col.WHITE, cx=190)


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
    # the train, stopped at the platform (doors sized for 2x people)
    pyxel.rect(-4, 28, 130, 70, Col.WHITE)
    pyxel.rect(-4, 30, 130, 2, Col.GRAY)
    pyxel.rect(-4, 80, 130, 4, Col.DARK_BLUE)
    for wx in (4, 32, 102):
        pyxel.rect(wx, 40, 22, 18, Col.NAVY)
        pyxel.line(wx + 2, 42, wx + 8, 42, Col.LIGHT_BLUE)
    door_open = p > 0.12
    pyxel.rect(60, 34, 38, 64, Col.NAVY if door_open else Col.GRAY)
    if not door_open:
        pyxel.line(79, 34, 79, 97, Col.DARK_BLUE)
        pyxel.rect(64, 42, 10, 16, Col.NAVY)
        pyxel.rect(84, 42, 10, 16, Col.NAVY)
    pyxel.rect(-4, 98, 130, 6, Col.NAVY)
    # platform with the yellow safety edge
    pyxel.rect(0, 104, SCREEN_W, 40, Col.GRAY)
    pyxel.rect(0, 104, SCREEN_W, 2, Col.YELLOW)
    # exit stairs
    pyxel.rect(226, 64, 30, 40, Col.BROWN)
    for sy in range(70, 104, 6):
        pyxel.line(226, sy, 255, sy, Col.NAVY)
    pyxel.rect(228, 52, 24, 9, Col.DARK_BLUE)
    pyxel.text(232, 54, "EXIT", Col.WHITE)
    # people (feet on the platform at y = 104)
    _char(160, 72, 4, Direction.LEFT)
    if 0.12 < p <= 0.26:
        _char(63, 64, PLAYER, Direction.DOWN)                 # in the doorway
    elif p > 0.26:
        t = min(1.0, (p - 0.26) / 0.66)
        x = 63 + (236 - 63) * t
        y = 64 + min(8.0, t * 60)                              # step down onto the platform
        if t < 1.0:
            _char(x, y, PLAYER, Direction.RIGHT, _walk_frame(f))


# --- 3. Webster Avenue, outside the gate -------------------------------------

GATE_X = 192  # pedestrian gate opening (20 px), between the first two pillars
GATE_W = 20
SIDEWALK_Y = 84   # top of the sidewalk; people stand on it
ROAD_Y = 102      # top of the road; the caption box starts at SCENE_BOTTOM
FEET_Y = 98       # where people's feet touch the sidewalk


def _pillar(x: int) -> None:
    pyxel.rect(x, 40, 11, 46, Col.GRAY)
    pyxel.rect(x - 1, 38, 13, 4, Col.WHITE)
    for sy in range(44, 84, 6):
        pyxel.line(x, sy, x + 10, sy, Col.DARK_BLUE)
        pyxel.pset(x + 3 + (sy // 6) % 4, sy + 3, Col.BROWN)


def _ram_van(x: float) -> None:
    """Fordham's maroon shuttle bus, side view, wheels on the road.
    About 1.4x as tall as a person and 3.5x as long."""
    x = int(x)
    top, bottom = 72, 120
    pyxel.rect(x + 2, top, 112, bottom - top, Col.MAROON)          # body
    pyxel.rect(x, top + 4, 116, bottom - top - 8, Col.MAROON)
    pyxel.rect(x + 2, top, 112, 3, Col.PINK)                       # roof highlight
    for wx in range(x + 30, x + 106, 16):                          # passenger windows
        pyxel.rect(wx, top + 8, 13, 14, Col.LIGHT_BLUE)
        pyxel.line(wx + 1, top + 9, wx + 4, top + 9, Col.WHITE)
    pyxel.rect(x + 2, top + 8, 18, 18, Col.LIGHT_BLUE)              # windshield (front, left)
    pyxel.rect(x + 22, top + 8, 6, 34, Col.NAVY)                   # door
    pyxel.line(x + 25, top + 8, x + 25, top + 41, Col.DARK_BLUE)
    pyxel.rect(x, top + 28, 116, 3, Col.WHITE)                     # stripe
    pyxel.text(x + 50, top + 32, "RAM VAN", Col.WHITE)
    pyxel.rect(x, bottom - 6, 4, 3, Col.YELLOW)                    # headlight
    for wx in (x + 20, x + 92):                                    # wheels
        pyxel.circ(wx, bottom, 7, Col.NAVY)
        pyxel.circ(wx, bottom, 3, Col.GRAY)


def draw_street(p: float, f: int, length: int) -> None:
    pyxel.cls(Col.LIGHT_BLUE)
    # off-campus apartment buildings (left)
    for bx, w, h, col in ((0, 40, 74, Col.BROWN), (40, 34, 60, Col.ORANGE), (74, 22, 68, Col.BROWN)):
        pyxel.rect(bx, SIDEWALK_Y - h, w, h, col)
        for wy in range(SIDEWALK_Y - h + 6, SIDEWALK_Y - 6, 10):
            for wx in range(bx + 4, bx + w - 4, 8):
                pyxel.rect(wx, wy, 4, 5, Col.NAVY)
    # campus behind the fence (right): stone building with a tower, trees
    pyxel.rect(200, 22, 56, 40, Col.GRAY)
    pyxel.rect(214, 4, 22, 20, Col.GRAY)
    for tx in range(216, 236, 4):
        pyxel.line(tx, 6, tx, 20, Col.DARK_BLUE)
    for wx in range(204, 254, 9):
        pyxel.rect(wx, 30, 4, 8, Col.NAVY)
    for cx, cy, r in ((112, 42, 16), (138, 36, 18), (170, 44, 15), (192, 46, 12)):
        pyxel.circ(cx, cy, r, Col.GREEN)
        pyxel.circ(cx - 4, cy - 4, r // 3, Col.LIME)
        pyxel.rect(cx - 2, cy + r - 4, 4, 30 - r, Col.BROWN)
    # guard booth (green roof) behind the fence
    pyxel.rect(150, 58, 22, 26, Col.WHITE)
    pyxel.rect(154, 62, 14, 8, Col.LIGHT_BLUE)
    pyxel.tri(147, 58, 175, 58, 161, 48, Col.GREEN)
    # iron fence
    pyxel.line(96, 56, SCREEN_W, 56, Col.NAVY)
    pyxel.line(96, 80, SCREEN_W, 80, Col.NAVY)
    for fx in range(96, SCREEN_W, 4):
        if not (GATE_X - 1 < fx < GATE_X + GATE_W):  # keep the pedestrian gate open
            pyxel.line(fx, 52, fx, SIDEWALK_Y, Col.NAVY)
    # maroon Fordham sign on the fence
    pyxel.rect(100, 60, 44, 18, Col.MAROON)
    pyxel.rectb(100, 60, 44, 18, Col.WHITE)
    _centered(63, "FORDHAM", Col.WHITE, cx=122)
    _centered(71, "ROSE HILL", Col.PEACH, cx=122)
    # stone pillars: pedestrian gate between the first two, vehicle gate after
    for px in (GATE_X - 11, GATE_X + GATE_W, 244):
        _pillar(px)
    # sidewalk (tan, like walkways in the game) and road (gray)
    pyxel.rect(0, SIDEWALK_Y, SCREEN_W, ROAD_Y - SIDEWALK_Y - 2, Col.PEACH)
    for sx in range(0, SCREEN_W, 16):
        pyxel.line(sx, SIDEWALK_Y, sx, ROAD_Y - 3, Col.GRAY)
    pyxel.rect(0, ROAD_Y - 2, SCREEN_W, 2, Col.WHITE)             # curb
    pyxel.rect(0, ROAD_Y, SCREEN_W, SCENE_BOTTOM - ROAD_Y, Col.GRAY)
    for dx in range(0, SCREEN_W, 24):
        pyxel.rect(dx + 4, 124, 12, 2, Col.YELLOW)
    # Bert, the guard, waits by the gate to check IDs (feet on the sidewalk)
    _char(GATE_X + GATE_W + 4, FEET_Y - CHAR_SIZE, 5, Direction.LEFT)
    # the player walks to the gate, then turns to face it
    t = min(1.0, p / 0.7)
    stop_x = GATE_X + GATE_W / 2 - CHAR_SIZE / 2
    x = -CHAR_SIZE + (stop_x + CHAR_SIZE) * t
    if t < 1.0:
        _char(x, FEET_Y - CHAR_SIZE, PLAYER, Direction.RIGHT, _walk_frame(f))
    else:
        _char(x, FEET_Y - CHAR_SIZE, PLAYER, Direction.UP)
    # a maroon Ram Van drives past on the near side of the road, in front
    # of the people on the sidewalk
    if 0.2 < p < 0.6:
        _ram_van(SCREEN_W - (p - 0.2) / 0.4 * (SCREEN_W + 130))


SCENE_ART = {"train": draw_train, "station": draw_station, "street": draw_street}
