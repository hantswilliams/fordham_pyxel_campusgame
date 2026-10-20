"""Placeholder art for the opening sequence (decisions/0016 Part 2), drawn
with Pyxel shapes each frame. Side views, unlike the top-down campus.
The train is generic on purpose: no transit logos (D-0009).

Each draw function takes `p` (0..1 progress through the scene), `f` (frames
since the scene started) and `length` (scene length in frames)."""

import math

import pyxel

from game.gfx import display
from game.ui import font

from game import config
from game.config import Col
from game.systems.intro_timeline import scroll_offset
from game.ui.textbox import box_top

from .placeholder_art import CHAR_IMAGE_BANK, character_uv
from game.world.directions import Direction

PLAYER = 0
CHAR_SCALE = 2           # people are drawn 2x in the intro (decisions/0019 Part 1)
CHAR_SIZE = 16 * CHAR_SCALE
TRAIN_SCALE = 3          # the train is a close-up, so people are 3x there
# The scenes are laid out for a 256-pixel-wide screen. On a bigger screen
# (the hi-res-screen branch) they're drawn at that size and scaled up to fill
# the width; see present().
ART_W = 256
SCREEN_W = ART_W
ART_SCALE = config.SCREEN_W / ART_W
# the caption box covers everything below this (textbox.box_top), in art pixels
SCENE_BOTTOM = math.ceil(box_top() / ART_SCALE)

_buffer: "pyxel.Image | None" = None


def present(draw, *args) -> None:
    """Draw an intro scene so it fills the screen width. At 256 px wide it's
    drawn as is; on a bigger screen it's drawn at 256 px, copied off the
    screen and scaled up (1.5x on a 384-wide screen)."""
    global _buffer
    if _buffer is None and ART_SCALE != 1:
        _buffer = pyxel.Image(ART_W, SCENE_BOTTOM)
    if ART_SCALE != 1:
        display.art_source(_buffer, ART_SCALE)   # signs are masked against this picture
    draw(*args)
    if ART_SCALE == 1:
        return
    _buffer.blt(0, 0, pyxel.screen, 0, 0, ART_W, SCENE_BOTTOM)
    display.art_source()
    pyxel.cls(Col.NAVY)
    # crisp screen (decisions/0039): scaled 3x in one step, so every pixel
    # is the same size; the words on its signs are drawn over it, crisp
    if display.queue_image(_buffer, ART_W, SCENE_BOTTOM, 0, 0, ART_SCALE):
        display.clear(0, 0, config.SCREEN_W, SCENE_BOTTOM * ART_SCALE)
        # finish the scene now, with its signs, so the boxes and cards drawn
        # next at full detail (decisions/0045) go over all of it
        display.layer()
        return
    # blt scales around the centre of the destination rectangle
    pyxel.blt((config.SCREEN_W - ART_W) / 2, SCENE_BOTTOM * (ART_SCALE - 1) / 2,
              _buffer, 0, 0, ART_W, SCENE_BOTTOM, scale=ART_SCALE)


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


def _label(x: float, y: float, s: str, col: int, bg: int) -> None:
    """Words on a sign of colour `bg`, laid out in Pyxel's 4-pixel font. On
    the crisp screen they're drawn in the reading font at full detail
    (decisions/0039)."""
    if not font.sign(x * ART_SCALE, y * ART_SCALE, s, col, cell=4 * ART_SCALE, bg=bg):
        pyxel.text(x, y, s, col)


def _centered(y: int, s: str, col: int, bg: int, cx: int = SCREEN_W // 2) -> None:
    _label(cx - len(s) * 2, y, s, col, bg)


# --- the finer intro (decisions/0045) ----------------------------------------
# The scenes are drawn straight onto a full-size picture with a Pen that
# works in the scenes' own units (256 across), so every shape comes out
# sharp, and people are drawn at close-up size from the same drawing as on
# campus (people_art.close_up), not blown up from small sprites.

from . import people_art  # noqa: E402
from game.config import Art  # noqa: E402


class Pen:
    """Draws in the intro's units (k pixels each) on img."""

    def __init__(self, img, k: float):
        self.img, self.k = img, k

    def _v(self, v: float) -> int:
        return round(v * self.k)

    def rect(self, x, y, w, h, c) -> None:
        X0, Y0, X1, Y1 = self._v(x), self._v(y), self._v(x + w), self._v(y + h)
        if X1 > X0 and Y1 > Y0:
            self.img.rect(X0, Y0, X1 - X0, Y1 - Y0, c)

    def rrect(self, x, y, w, h, r, c) -> None:
        X0, Y0, X1, Y1 = self._v(x), self._v(y), self._v(x + w), self._v(y + h)
        R = max(0, min(self._v(r), (X1 - X0) // 2, (Y1 - Y0) // 2))
        if X1 <= X0 or Y1 <= Y0:
            return
        self.img.rect(X0 + R, Y0, X1 - X0 - 2 * R, Y1 - Y0, c)
        self.img.rect(X0, Y0 + R, X1 - X0, Y1 - Y0 - 2 * R, c)
        for cx, cy in ((X0 + R, Y0 + R), (X1 - 1 - R, Y0 + R), (X0 + R, Y1 - 1 - R), (X1 - 1 - R, Y1 - 1 - R)):
            self.img.circ(cx, cy, R, c)

    def edge(self, x, y, w, h, c, t: int = 1) -> None:
        """A t-pixel border just inside (x, y, w, h)."""
        X0, Y0, X1, Y1 = self._v(x), self._v(y), self._v(x + w), self._v(y + h)
        self.img.rect(X0, Y0, X1 - X0, t, c)
        self.img.rect(X0, Y1 - t, X1 - X0, t, c)
        self.img.rect(X0, Y0, t, Y1 - Y0, c)
        self.img.rect(X1 - t, Y0, t, Y1 - Y0, c)

    def hline(self, x0, x1, y, c, t: int = 2) -> None:
        self.img.rect(self._v(x0), self._v(y), self._v(x1) - self._v(x0), t, c)

    def vline(self, x, y0, y1, c, t: int = 2) -> None:
        self.img.rect(self._v(x), self._v(y0), t, self._v(y1) - self._v(y0), c)

    def circ(self, cx, cy, r, c) -> None:
        self.img.circ(self._v(cx), self._v(cy), round(r * self.k), c)

    def tri(self, x0, y0, x1, y1, x2, y2, c) -> None:
        self.img.tri(self._v(x0), self._v(y0), self._v(x1), self._v(y1), self._v(x2), self._v(y2), c)

    def dot(self, x, y, c, size: int = 2) -> None:
        self.img.rect(self._v(x), self._v(y), size, size, c)

    def clip(self, x=None, y=0, w=0, h=0) -> None:
        if x is None:
            self.img.clip()
        else:
            self.img.clip(self._v(x), self._v(y), self._v(x + w) - self._v(x), self._v(y + h) - self._v(y))

    def label(self, x, y, s, col, cell: float = 4) -> None:
        """Words on a sign, lettered sharp (cell units a character)."""
        font.letter(self.img, x * self.k, y * self.k, s, col, cell * self.k)

    def centered(self, y, s, col, cx: float = SCREEN_W / 2) -> None:
        self.label(cx - len(s) * 2, y, s, col)

    def person(self, x, y, sprite: int, facing: Direction, frame: int = 0,
               scale: int = CHAR_SCALE) -> None:
        """Someone standing where a 16-pixel sprite `scale` times bigger had
        its top-left at (x, y): feet on the same spot, head a little higher."""
        kp = scale * self.k
        img = people_art.close_up(sprite, facing, frame, kp)
        X = self._v(x) - people_art.CLOSE_PAD
        Y = self._v(y + 16 * scale) - round(22.5 * kp) - people_art.CLOSE_PAD
        self.img.blt(X, Y, img, 0, 0, img.width, img.height, Col.BLACK)

    def tree(self, cx, cy, r) -> None:
        """A round, lumpy tree lit from the top left, as on campus."""
        self.rect(cx - 1.5, cy + r * 0.6, 3, 30 - r, Art.TRUNK)
        self.rect(cx + 0.3, cy + r * 0.6, 1.2, 30 - r, Art.TRUNK_DK)
        lumps = ((0, 0, 1.0), (-0.45, 0.25, 0.6), (0.45, 0.25, 0.6), (0, -0.4, 0.7))
        for dx, dy, f in lumps:
            self.img.circ(self._v(cx + dx * r), self._v(cy + dy * r), round(r * f * self.k) + 1, Art.LEAF_OUT)
        for dx, dy, f in lumps:
            self.circ(cx + dx * r, cy + dy * r, r * f, Art.LEAF_DK)
        for dx, dy, f in lumps:
            self.circ(cx + dx * r - r * f * 0.12, cy + dy * r - r * f * 0.16, r * f * 0.8, Art.LEAF)
        for dx, dy, f in lumps:
            self.circ(cx + dx * r - r * f * 0.3, cy + dy * r - r * f * 0.35, r * f * 0.42, Art.LEAF_LT)


_scene: pyxel.Image | None = None


def present_scene(draw, *args) -> None:
    """Draw an intro scene, draw(pen, *args), filling the screen above the
    caption box: at full detail on the crisp screen (decisions/0045),
    otherwise straight onto the screen at 1.5x."""
    global _scene
    if not display.active:
        pyxel.cls(Col.NAVY)
        draw(Pen(pyxel.screen, ART_SCALE), *args)
        pyxel.clip()
        return
    k = ART_SCALE * display.scale
    if _scene is None:
        _scene = pyxel.Image(round(ART_W * k), round(SCENE_BOTTOM * k))
    _scene.cls(Col.NAVY)
    draw(Pen(_scene, k), *args)
    _scene.clip()
    pyxel.cls(Col.NAVY)
    display.queue_image(_scene, _scene.width, _scene.height, 0, 0, 1 / display.scale)
    display.clear(0, 0, config.SCREEN_W, SCENE_BOTTOM * ART_SCALE)
    display.layer()           # finished now, so boxes and cards drawn next go over it


# --- 1. on the train ---------------------------------------------------------

def _window(pen: Pen, wx: float, wy: float, ww: float, wh: float, off: float) -> None:
    """A carriage window with the Bronx sliding past: a slow skyline, fast poles."""
    pen.rect(wx, wy, ww, wh, Col.LIGHT_BLUE)
    pen.rect(wx, wy + wh * 0.55, ww, wh * 0.45, Art.PANE_HI)
    pen.clip(wx, wy, ww, wh)
    base = int(off * 0.5)
    first = base // 22
    for k in range(first - 1, first + int(ww) // 22 + 2):
        bx = wx + k * 22 - base
        h = 12 + (k * 37) % 20
        col = (Col.BROWN, Col.ORANGE, Col.DARK_BLUE, Col.GRAY)[k % 4]
        pen.rect(bx, wy + wh - h, 19, h, col)
        pen.rect(bx + 15, wy + wh - h, 4, h, Art.OUTLINE if col == Col.DARK_BLUE else Art.WOOD_DK)
        pen.rect(bx, wy + wh - h, 19, 1, Art.PANE_HI)
        for wy2 in range(int(wy + wh - h + 3), int(wy + wh - 2), 5):
            for wx2 in range(int(bx + 3), int(bx + 15), 4):
                if (wx2 * 7 + wy2 * 3 + k) % 5:
                    pen.rect(wx2, wy2, 1.6, 2, Col.YELLOW)
    base2 = int(off)
    for k in range(base2 // 40 - 1, base2 // 40 + int(ww) // 40 + 2):
        px = wx + k * 40 - base2
        pen.vline(px, wy + 6, wy + wh, Art.IRON, 3)
        pen.hline(px - 3, px + 4, wy + 8, Art.IRON, 2)
    pen.clip()
    pen.edge(wx - 2, wy - 2, ww + 4, wh + 4, Art.UI_PAGE, 5)      # the frame, and a dark edge
    pen.edge(wx - 2, wy - 2, ww + 4, wh + 4, Art.OUTLINE, 1)
    pen.edge(wx, wy, ww, wh, Art.POST, 1)


def draw_train(pen: Pen, p: float, f: int, length: int) -> None:
    """Close-up inside the carriage: passengers at 3x fill their seats, heads
    level with the windows. Everything sits above the caption box."""
    moving = p < 0.97
    bob = 1 if moving and (f // 8) % 2 else 0
    pen.rect(0, 0, SCREEN_W, SCENE_BOTTOM, Art.CURB)                 # the carriage wall
    pen.rect(0, 69, SCREEN_W, 41, Col.GRAY)
    pen.rect(0, 0, SCREEN_W, 18, Art.UI_PAGE)                         # ceiling, with its lights
    for lx in (14, 140):
        pen.rrect(lx, 13, 102, 3, 1, Art.PANE_HI)
    pen.hline(0, SCREEN_W, 18, Col.DARK_BLUE, 2)
    pen.rrect(6, 2.5, 116, 13, 2, Art.OUTLINE)                        # the LED next-stop sign
    pen.rect(7.5, 4, 113, 10, Art.WIN)
    if (f // 20) % 4 != 3:
        pen.centered(6.3, "NEXT STOP: FORDHAM", Col.ORANGE, cx=64)
    off = scroll_offset(p, length, speed=5.0)
    for wx in (8, 132):
        _window(pen, wx, 30 + bob, 116, 34, off)
    pen.rect(0, 67, SCREEN_W, 2, Col.DARK_BLUE)                       # window sill
    pen.hline(0, SCREEN_W, 67, Col.LIGHT_BLUE, 1)
    pen.rect(0, 110, SCREEN_W, SCENE_BOTTOM - 110, Col.BROWN)          # floor, in planks
    for py in range(114, SCENE_BOTTOM, 6):
        pen.hline(0, SCREEN_W, py, Art.WOOD_DK, 1)
    pen.hline(0, SCREEN_W, 110, Art.OUTLINE, 2)
    seats = [(2, 2), (66, None), (130, PLAYER), (194, 3)]                # passengers face the way we're going
    for sx, who in seats:
        pen.rrect(sx, 56 + bob, 8, 50, 2, Col.DARK_BLUE)               # seat back and headrest
        pen.rect(sx + 1.5, 59 + bob, 1.5, 44, Col.LIGHT_BLUE)
        pen.rrect(sx - 0.5, 51.5 + bob, 11, 7, 2.5, Col.DARK_BLUE)
        pen.rect(sx + 1, 52.5 + bob, 7, 1, Col.LIGHT_BLUE)
        if who is not None:
            pen.person(sx + 8, 50 + bob, who, Direction.RIGHT, scale=TRAIN_SCALE)
        pen.rrect(sx, 89 + bob, 58, 11, 3, Col.DARK_BLUE)               # cushion, over the legs
        pen.hline(sx + 3, sx + 55, 90 + bob, Col.LIGHT_BLUE, 2)
        pen.rect(sx + 48, 100 + bob, 5, 10, Art.IRON)                   # leg
    if not moving:                                     # the platform sign, through the window
        pen.rrect(170, 36, 40, 13, 1.5, Art.UI_PAGE)
        pen.rect(171, 37, 38, 11, Col.DARK_BLUE)
        pen.centered(40, "FORDHAM", Col.WHITE, cx=190)


# --- 2. Fordham station -------------------------------------------------------

def draw_station(pen: Pen, p: float, f: int, length: int) -> None:
    pen.rect(0, 0, SCREEN_W, SCENE_BOTTOM, Col.LIGHT_BLUE)
    pen.rect(0, 60, SCREEN_W, 44, Art.PANE_HI)
    for i, (bx, h, col) in enumerate(((130, 40, Col.BROWN), (160, 52, Col.ORANGE),
                                      (196, 34, Col.BROWN), (222, 46, Col.DARK_BLUE))):
        pen.rect(bx, 96 - h, 28, h, col)                              # the skyline beyond
        pen.rect(bx + 22, 96 - h, 6, h, Art.WOOD_DK if col != Col.DARK_BLUE else Art.OUTLINE)
        for wy in range(100 - h, 92, 6):
            for wx in range(bx + 3, bx + 20, 5):
                pen.rect(wx, wy, 2, 3, Art.WIN if (wx + wy) % 3 else Col.YELLOW)
    pen.rect(0, 9, SCREEN_W, 9, Art.LEAF_DK)                          # canopy and its posts
    pen.rect(0, 9, SCREEN_W, 2, Art.LEAF)
    pen.hline(0, SCREEN_W, 18, Art.OUTLINE, 2)
    for px in (140, 198, 250):
        pen.rect(px, 18, 3, 86, Art.IRON)
        pen.rect(px, 18, 1, 86, Art.IRON_HI)
    pen.vline(166, 18, 26, Art.IRON, 2)                               # the station's name sign
    pen.vline(200, 18, 26, Art.IRON, 2)
    pen.rrect(153, 25, 60, 15, 2, Art.UI_PAGE)
    pen.rect(154.5, 26.5, 57, 12, Col.DARK_BLUE)
    pen.centered(30, "FORDHAM", Col.WHITE, cx=183)
    # the train, stopped at the platform (doors sized for 2x people)
    pen.rect(-4, 28, 130, 70, Art.VAN)
    pen.rect(-4, 28, 130, 4, Art.VAN_SH)
    pen.rect(-4, 78, 130, 5, Col.DARK_BLUE)
    pen.hline(-4, 126, 83, Col.LIGHT_BLUE, 2)
    for wx in (4, 32, 102):
        pen.rrect(wx - 1, 39, 24, 20, 1.5, Art.OUTLINE)
        pen.rect(wx, 40, 22, 18, Art.VAN_GLASS)
        pen.rect(wx, 40, 22, 6, Art.VAN_GLASS_DK)
        pen.tri(wx + 2, 56, wx + 9, 42, wx + 12, 42, Art.VAN_GLASS_HI)
    door_open = p > 0.12
    pen.rrect(59, 33, 40, 66, 1.5, Art.OUTLINE)
    if door_open:
        pen.rect(60, 34, 38, 64, Art.WIN)
        pen.rect(60, 34, 38, 10, Art.OUTLINE)
    else:
        pen.rect(60, 34, 38, 64, Art.VAN_SH)
        pen.vline(79, 34, 98, Art.OUTLINE, 2)
        for dx in (64, 84):
            pen.rect(dx, 42, 10, 16, Art.VAN_GLASS)
            pen.rect(dx, 42, 10, 5, Art.VAN_GLASS_DK)
    pen.rect(-4, 98, 130, 6, Art.OUTLINE)
    pen.rect(0, 104, SCREEN_W, SCENE_BOTTOM - 104, Col.GRAY)            # the platform
    for tx in range(0, SCREEN_W, 16):
        pen.vline(tx, 108, SCENE_BOTTOM, Art.POST, 1)
    pen.rect(0, 104, SCREEN_W, 3, Col.YELLOW)                          # its yellow safety edge
    for tx in range(0, SCREEN_W, 4):
        pen.dot(tx + 1, 105, Col.ORANGE, 2)
    pen.rect(226, 64, 30, 40, Col.BROWN)                               # exit stairs
    for sy in range(70, 104, 6):
        pen.hline(226, 256, sy, Art.WOOD_DK, 2)
        pen.hline(226, 256, sy - 5, Art.WOOD_LT, 1)
    pen.rrect(227, 51, 26, 11, 1.5, Art.UI_PAGE)
    pen.rect(228, 52, 24, 9, Col.DARK_BLUE)
    pen.label(232, 54, "EXIT", Col.WHITE)
    pen.person(160, 72, 4, Direction.LEFT)                             # people, feet on the platform
    if 0.12 < p <= 0.26:
        pen.person(63, 64, PLAYER, Direction.DOWN)                      # in the doorway
    elif p > 0.26:
        t = min(1.0, (p - 0.26) / 0.66)
        x = 63 + (236 - 63) * t
        y = 64 + min(8.0, t * 60)                                      # step down onto the platform
        if t < 1.0:
            pen.person(x, y, PLAYER, Direction.RIGHT, _walk_frame(f))


# --- 3. Webster Avenue, outside the gate -------------------------------------

GATE_X = 192  # pedestrian gate opening (20 px), between the first two pillars
GATE_W = 20
SIDEWALK_Y = 84   # top of the sidewalk; people stand on it
ROAD_Y = 102      # top of the road; the caption box starts at SCENE_BOTTOM
FEET_Y = 98       # where people's feet touch the sidewalk


def _pillar(pen: Pen, x: float) -> None:
    """A stone gate pillar, in courses, with a cap."""
    pen.rect(x - 0.5, 40, 12, 46, Art.OUTLINE)
    pen.rect(x, 40, 11, 46, Col.STONE)
    pen.rect(x + 8, 40, 3, 46, Col.STONE_SH)
    for sy in range(44, 84, 5):
        pen.hline(x, x + 11, sy, Col.STONE_SH, 1)
        bx = x + 3 + (sy // 5) % 2 * 4
        pen.vline(bx, sy, sy + 5, Col.STONE_SH, 1)
    pen.rrect(x - 1.5, 37, 14, 4.5, 1, Art.OUTLINE)
    pen.rect(x - 1, 37.5, 13, 3.5, Col.STONE_HI)


def _ram_van(pen: Pen, x: float) -> None:
    """Fordham's maroon Ram Van, side on, wheels on the road: about 1.4x as
    tall as a person and 3.5x as long."""
    top, bottom = 72, 120
    pen.rrect(x - 0.5, top - 0.5, 117, bottom - top + 1, 6, Art.OUTLINE)
    pen.rrect(x, top, 116, bottom - top, 5.5, Col.MAROON)
    pen.rrect(x + 2, top + 1, 112, 3, 1.5, Art.MAROON_LT)              # light along the roof
    pen.rect(x, bottom - 12, 116, 6, Art.MAROON_SH)
    for wx in range(int(x) + 30, int(x) + 106, 16):                   # passenger windows
        pen.rrect(wx, top + 8, 13, 14, 1.5, Art.VAN_GLASS)
        pen.rect(wx, top + 8, 13, 5, Art.VAN_GLASS_DK)
        pen.tri(wx + 1.5, top + 20, wx + 6, top + 9.5, wx + 8, top + 9.5, Art.VAN_GLASS_HI)
    pen.rrect(x + 2, top + 8, 18, 18, 2, Art.VAN_GLASS)                # windscreen (the front's on the left)
    pen.tri(x + 4, top + 24, x + 10, top + 10, x + 13, top + 10, Art.VAN_GLASS_HI)
    pen.rect(x + 22, top + 8, 6, 34, Art.WIN)                          # door
    pen.vline(x + 25, top + 8, top + 42, Art.OUTLINE, 2)
    pen.rect(x, top + 28, 116, 3, Art.VAN)                             # stripe and lettering
    pen.label(x + 50, top + 32, "RAM VAN", Col.WHITE)
    pen.rect(x - 0.5, bottom - 7, 4, 3, Art.HEADLIGHT)
    pen.rect(x + 112.5, bottom - 8, 4, 4, Art.TAILLIGHT)
    for wx in (x + 20, x + 92):                                        # wheels
        pen.circ(wx, bottom, 7.5, Art.OUTLINE)
        pen.circ(wx, bottom, 7, Art.TYRE)
        pen.circ(wx, bottom, 3.3, Art.HUB)
        pen.circ(wx, bottom, 1.2, Art.TYRE)


def draw_street(pen: Pen, p: float, f: int, length: int) -> None:
    pen.rect(0, 0, SCREEN_W, SCENE_BOTTOM, Col.LIGHT_BLUE)
    pen.rect(0, 50, SCREEN_W, 40, Art.PANE_HI)
    # off-campus apartment buildings (left)
    for bx, w, h, col, dk in ((0, 40, 74, Col.BROWN, Art.WOOD_DK), (40, 34, 60, Col.ORANGE, Art.CARD_BOX_SH),
                              (74, 22, 68, Col.BROWN, Art.WOOD_DK)):
        pen.rect(bx, SIDEWALK_Y - h, w, h, col)
        pen.rect(bx + w - 3, SIDEWALK_Y - h, 3, h, dk)
        pen.rect(bx, SIDEWALK_Y - h, w, 2, Art.OUTLINE)
        for wy in range(SIDEWALK_Y - h + 6, SIDEWALK_Y - 6, 10):
            for wx in range(bx + 4, bx + w - 4, 8):
                pen.rect(wx - 0.5, wy - 0.5, 5, 6, Art.SIGN_BD)
                pen.rect(wx, wy, 4, 5, Art.WIN)
                pen.rect(wx, wy, 1.3, 2.5, Art.WIN_LT)
    # the campus behind the fence (right): a stone building with a tower, trees
    pen.rect(200, 22, 56, 40, Col.STONE)
    pen.rect(200, 22, 56, 2, Col.STONE_HI)
    pen.rect(214, 4, 22, 20, Col.STONE)
    pen.rect(231, 4, 5, 20, Col.STONE_SH)
    for bx in range(214, 236, 4):
        pen.rect(bx, 1.5, 2, 3, Col.STONE)                             # battlements
    for tx in range(217, 234, 4):
        pen.vline(tx, 7, 20, Art.WIN, 2)
    for wx in range(204, 254, 9):
        pen.rect(wx - 0.5, 29.5, 5, 9, Col.STONE_HI)
        pen.rect(wx, 30, 4, 8, Art.WIN)
        pen.tri(wx, 30, wx + 4, 30, wx + 2, 27.5, Col.STONE_HI)
    for cx, cy, r in ((112, 42, 16), (138, 36, 18), (170, 44, 15), (192, 46, 12)):
        pen.tree(cx, cy, r)
    # the guard booth behind the fence
    pen.rect(150, 58, 22, 26, Art.VAN)
    pen.rect(167, 58, 5, 26, Art.VAN_SH)
    pen.rect(154, 62, 14, 8, Art.VAN_GLASS)
    pen.rect(154, 62, 14, 3, Art.VAN_GLASS_DK)
    pen.tri(146, 58.5, 176, 58.5, 161, 47.5, Art.OUTLINE)
    pen.tri(147.5, 58, 174.5, 58, 161, 49, Art.LEAF_DK)
    pen.hline(147, 175, 58, Art.OUTLINE, 2)
    # iron railings, with the pedestrian gate open
    pen.hline(96, SCREEN_W, 56, Art.IRON, 2)
    pen.hline(96, SCREEN_W, 80, Art.IRON, 2)
    for fx in range(96, SCREEN_W, 3):
        if not (GATE_X - 1 < fx < GATE_X + GATE_W):
            pen.vline(fx, 53, SIDEWALK_Y, Art.IRON, 2)
            pen.dot(fx, 52, Art.IRON_HI, 2)
    # the maroon Fordham sign on the fence, high enough that the Ram Van
    # passing in front doesn't hide it (decisions/0039)
    pen.rrect(99, 49, 46, 23, 2, Art.UI_PAGE)
    pen.rrect(100.5, 50.5, 43, 20, 1.5, Col.MAROON)
    pen.centered(53, "FORDHAM", Col.WHITE, cx=122)
    pen.centered(62, "ROSE HILL", Col.PEACH, cx=122)
    for px in (GATE_X - 11, GATE_X + GATE_W, 244):                      # stone pillars
        _pillar(pen, px)
    # the sidewalk (tan, like walkways in the game), the kerb and the road
    pen.rect(0, SIDEWALK_Y, SCREEN_W, ROAD_Y - SIDEWALK_Y - 2, Art.WALK)
    for sx in range(0, SCREEN_W, 16):
        pen.vline(sx, SIDEWALK_Y, ROAD_Y - 3, Art.WALK_EDGE, 2)
    pen.hline(0, SCREEN_W, SIDEWALK_Y, Art.WALK_EDGE, 2)
    pen.rect(0, ROAD_Y - 3, SCREEN_W, 3, Art.CURB)
    pen.hline(0, SCREEN_W, ROAD_Y, Art.CURB_DK, 2)
    pen.rect(0, ROAD_Y, SCREEN_W, SCENE_BOTTOM - ROAD_Y, Art.ROAD)
    for dx in range(0, SCREEN_W, 24):
        pen.rect(dx + 4, 124, 12, 2, Col.YELLOW)
    # Bert, the guard, waits by the gate to check IDs (feet on the sidewalk)
    pen.person(GATE_X + GATE_W + 4, FEET_Y - CHAR_SIZE, 5, Direction.LEFT)
    # the player walks to the gate, then turns to face it
    t = min(1.0, p / 0.7)
    stop_x = GATE_X + GATE_W / 2 - CHAR_SIZE / 2
    x = -CHAR_SIZE + (stop_x + CHAR_SIZE) * t
    if t < 1.0:
        pen.person(x, FEET_Y - CHAR_SIZE, PLAYER, Direction.RIGHT, _walk_frame(f))
    else:
        pen.person(x, FEET_Y - CHAR_SIZE, PLAYER, Direction.UP)
    # a maroon Ram Van drives past on the near side of the road, in front
    # of the people on the sidewalk
    if 0.2 < p < 0.6:
        _ram_van(pen, SCREEN_W - (p - 0.2) / 0.4 * (SCREEN_W + 130))


SCENE_ART = {"train": draw_train, "station": draw_station, "street": draw_street}
