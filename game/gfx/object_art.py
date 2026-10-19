"""Things on the map at twice the detail (decisions/0045, step 3): signs,
shuttle stops, lamps, benches, statues, the Victory Bell, graves, the
observatory, the guard booth, gate pillars, card readers and the closed
gate, the bike rack, mission items, the campus fence, and the tiles of the
one building still made of tiles (Faculty Memorial Hall).

Drawn in code once, at startup, into one sheet, each 32 x 32 (one cell),
then outlined in one pass like the people (game/gfx/people_art.py). Each
sits in a 36 x 36 slot, so outlines never run into the next one; uv()
gives the cell's top-left. The fence comes in 16 pieces, one for each way
it can join its neighbours (fence_uv), and has no outline, so it stays
light enough to see through.
"""

from __future__ import annotations

import pyxel

from game.config import Art, Col
from game.gfx.people_art import _Units

SLOT = 36
PAD = 2
PER_ROW = 14

# things drawn whole, with an outline (in sheet order)
OBJECTS = ("sign", "shuttle", "lamp", "bench", "statue", "bell", "grave", "dome", "booth",
           "pillar", "card_reader", "reader_gate", "bike_rack", "item_card", "item_card_road",
           "item_package", "ram")
# a statue drawn as something else, by the place it's the sign for
STATUES = {"ram_statue": "ram"}
# building tiles: they fill their cell, and the map overlay outlines the building
TILES = ("roof", "wall", "window", "door")
FENCE_AT = len(OBJECTS) + len(TILES)          # then the 16 fence pieces
N, S, W, E = 1, 2, 4, 8


def _slot(i: int) -> tuple[int, int]:
    return (i % PER_ROW) * SLOT + PAD, (i // PER_ROW) * SLOT + PAD


def uv(name: str) -> tuple[int, int] | None:
    """Top-left of a thing's 32 x 32 cell on the sheet, or None."""
    if name in OBJECTS:
        return _slot(OBJECTS.index(name))
    if name in TILES:
        return _slot(len(OBJECTS) + TILES.index(name))
    return None


def fence_uv(joins: int) -> tuple[int, int]:
    """The fence piece that joins N / S / W / E (bits) to its neighbours."""
    return _slot(FENCE_AT + joins)


# --- the things ----------------------------------------------------------------------

def _post(u: _Units, top: float) -> None:
    u.rect(7, top, 9, 16, Art.POST)
    u.rect(8, top, 9, 16, Art.POST_DK)


def _sign(u: _Units) -> None:
    """The gray information sign by a door or a landmark."""
    _post(u, 11)
    u.rrect(2, 3, 14, 12, 1, Art.SIGN_BD)
    u.rect(2, 10.5, 14, 12, Art.SILL)
    for k, y in enumerate((5, 7, 9)):
        u.rect(4, y, 12 - (k == 2) * 3, y + 0.5, Art.POST)


def _shuttle(u: _Units) -> None:
    """A maroon Campus Shuttle stop: a white bus on a maroon board."""
    _post(u, 11.5)
    u.rrect(2, 1.5, 14, 12, 1.5, Col.MAROON)
    u.rect(3, 2.5, 13, 3.5, Art.MAROON_LT)
    u.rect(4.5, 4.5, 11.5, 9, Art.SIGN_BD)
    u.rect(5.5, 5.5, 10.5, 7, Col.MAROON)
    u.rect(5, 9, 6.5, 10, Art.SIGN_BD)
    u.rect(9.5, 9, 11, 10, Art.SIGN_BD)


def _lamp(u: _Units) -> None:
    """A black lamp post with a lantern."""
    u.rect(7.25, 4.5, 8.75, 15, Art.IRON)
    u.rect(6, 14.5, 10, 16, Art.IRON)
    u.rect(5.5, 1, 10.5, 5, Art.IRON)
    u.rect(6.5, 2, 9.5, 4.5, Art.HEADLIGHT)
    u.rect(6.5, 2, 7.5, 4.5, Art.SIGN_BD)
    u.rect(5, 0.5, 11, 1.5, Art.IRON)


def _bench(u: _Units) -> None:
    """A wooden bench with iron legs."""
    u.rect(1, 5, 15, 7, Art.WOOD_LT)
    u.rect(1, 7, 15, 8, Art.WOOD_DK)
    u.rect(1, 9, 15, 11, Col.BROWN)
    u.rect(1, 10.5, 15, 11, Art.WOOD_DK)
    for x in (2, 13):
        u.rect(x, 11, x + 1, 14.5, Art.IRON)


def _statue(u: _Units) -> None:
    """A bronze figure on a stone plinth."""
    u.rect(3, 10, 13, 16, Col.STONE)
    u.rect(3, 10, 13, 11.5, Col.STONE_HI)
    u.rect(10.5, 11.5, 13, 16, Col.STONE_SH)
    u.rect(4.5, 8.5, 11.5, 10, Col.STONE_SH)
    u.oval(6, 0.5, 10, 4.5, Art.BRONZE)
    u.rrect(5, 4.5, 11, 9, 1.5, Art.BRONZE)
    u.rect(4, 5, 5.5, 8.5, Art.BRONZE)
    u.rect(9, 5, 11, 9, Art.BRONZE_DK)
    u.rect(6, 1, 7.5, 2.5, Art.BRONZE_LT)
    u.rect(5.5, 5, 6.5, 8.5, Art.BRONZE_LT)


def _ram(u: _Units) -> None:
    """The bronze Ram on its plinth, by the fountain."""
    u.rect(2, 10, 15, 16, Col.STONE)
    u.rect(2, 10, 15, 11.5, Col.STONE_HI)
    u.rect(12, 11.5, 15, 16, Col.STONE_SH)
    u.rect(5, 7.5, 6.5, 10.5, Art.BRONZE_DK)              # legs
    u.rect(11, 7.5, 12.5, 10.5, Art.BRONZE_DK)
    u.oval(4, 3, 14.5, 9, Art.BRONZE)                     # body, facing left
    u.oval(9, 3.5, 14.5, 9, Art.BRONZE_DK)
    u.oval(1.5, 1, 6.5, 6.5, Art.BRONZE)                  # head
    u.oval(3, 0, 7.5, 4.5, Art.BRONZE_LT)                 # the curled horn
    u.oval(4.5, 1.2, 6.2, 3, Art.BRONZE_DK)
    u.rect(5, 4, 10, 5, Art.BRONZE_LT)                    # light along its back
    u.px(2.5, 3.5, Art.BRONZE_DK)


def _bell(u: _Units) -> None:
    """The Victory Bell in its frame."""
    for x in (1.5, 12.5):
        u.rect(x, 2, x + 2, 16, Art.WOOD_LT)
        u.rect(x + 1.2, 2, x + 2, 16, Art.WOOD_DK)
    u.rect(1, 1.5, 15, 3.5, Col.BROWN)
    u.rect(1, 1.5, 15, 2, Art.WOOD_LT)
    u.rect(7.5, 3.5, 8.5, 5, Art.IRON)
    u.oval(5, 4.5, 11, 10, Art.BADGE)
    u.rect(4.5, 8, 11.5, 11, Art.BADGE)
    u.rect(4, 10.5, 12, 12, Col.ORANGE)
    u.rect(9, 5.5, 11.5, 11, Col.ORANGE)
    u.rect(6, 5.5, 7, 9, Art.HEADLIGHT)
    u.rect(7.5, 11.5, 8.5, 13, Art.IRON)


def _grave(u: _Units) -> None:
    """Two headstones in the Jesuit cemetery."""
    for x, y in ((1.5, 3.5), (8.5, 6.5)):
        u.rect(x, y + 2, x + 6, y + 9, Col.STONE)
        u.oval(x, y, x + 6, y + 5, Col.STONE)
        u.rect(x + 4.5, y + 2, x + 6, y + 9, Col.STONE_SH)
        u.rect(x + 2.5, y + 2, x + 3.5, y + 6.5, Col.STONE_DK)
        u.rect(x + 1.5, y + 3, x + 4.5, y + 4, Col.STONE_DK)
        u.rect(x - 0.5, y + 8.5, x + 6.5, y + 9.5, Col.STONE_SH)


def _dome(u: _Units) -> None:
    """The Seismic Observatory: a small white house under a metal dome."""
    u.rect(2.5, 8, 13.5, 15.5, Art.VAN)
    u.rect(11, 8, 13.5, 15.5, Art.VAN_SH)
    u.oval(3, 2.5, 13, 12.5, Art.METAL)
    u.oval(3, 2.5, 11, 10, Art.SIGN_BD)
    u.rect(7.5, 2.5, 8.5, 8, Art.HUB)
    u.rect(2.5, 8, 13.5, 9, Art.HUB)
    u.rect(6.5, 11, 9.5, 15.5, Col.BROWN)


def _booth(u: _Units) -> None:
    """The guard booth at a gate."""
    u.rect(2.5, 6, 13.5, 15.5, Art.VAN)
    u.rect(11, 6, 13.5, 15.5, Art.VAN_SH)
    u.rect(3.5, 8, 12.5, 11, Art.VAN_GLASS)
    u.rect(3.5, 8, 12.5, 9, Art.VAN_GLASS_DK)
    u.rect(4.5, 9, 5, 10.5, Art.VAN_GLASS_HI)
    u.rect(6.5, 12, 9.5, 15.5, Col.BROWN)
    u.rect(1.5, 3, 14.5, 6.5, Art.GUARD)
    u.rect(1.5, 3, 14.5, 4, Art.SHIRT_B_SH)
    u.rect(1.5, 6, 14.5, 6.5, Art.GUARD_SH)


def _pillar(u: _Units) -> None:
    """A stone gate pillar with a cap."""
    u.rect(3, 2, 13, 16, Col.STONE)
    u.rect(10.5, 2, 13, 16, Col.STONE_SH)
    for y in (5, 9, 13):
        u.rect(3, y, 13, y + 0.5, Col.STONE_SH)
    u.rect(2, 0.5, 14, 3, Col.STONE_HI)
    u.rect(2, 2.5, 14, 3, Col.STONE_SH)


def _card_reader(u: _Units) -> None:
    """An ID card reader on a post (decisions/0042), its light green."""
    u.rect(7, 8, 9, 15, Art.IRON)
    u.rect(5.5, 14.5, 10.5, 15.5, Art.IRON)
    u.rrect(4, 1.5, 12, 8.5, 1, Art.POST_DK)
    u.rect(5, 2.5, 11, 4, Col.MAROON)
    u.rect(6, 5.5, 10, 6, Art.IRON)
    u.rect(9.5, 6.5, 10.5, 7.5, Art.GRASS)


def _reader_gate(u: _Units) -> None:
    """The closed pedestrian gate with its reader showing red."""
    for x in range(1, 12, 2):
        u.rect(x, 1.5, x + 0.5, 15.5, Art.IRON)
        u.rect(x, 1, x + 0.5, 1.5, Art.IRON_HI)
    for y in (3, 12):
        u.rect(0, y, 12, y + 1, Art.IRON)
    u.rect(13.5, 6, 14.5, 16, Art.POST)
    u.rrect(12, 2.5, 16, 7, 0.5, Art.POST_DK)
    u.rect(13, 3.5, 15, 4.5, Art.TAILLIGHT)


def _bike_rack(u: _Units) -> None:
    """A metal hoop on a concrete pad, a maroon bike parked against it."""
    u.rect(0, 14, 16, 16, Col.STONE)
    u.rect(0, 14, 16, 14.5, Col.STONE_HI)
    u.rect(1, 3, 15, 4, Art.METAL)
    u.rect(1, 3, 2, 14, Art.METAL)
    u.rect(14, 3, 15, 14, Art.METAL)
    for wx in (4, 12):
        u.oval(wx - 3, 8, wx + 3, 14, Art.TYRE)
        u.oval(wx - 2.2, 8.8, wx + 2.2, 13.2, Art.METAL)
        u.oval(wx - 1.6, 9.4, wx + 1.6, 12.6, 0)
        u.rect(wx - 0.4, 10.6, wx + 0.4, 11.4, Art.HUB)
    u.limb(4, 11, 8, 11, 0.5, Col.MAROON)
    u.limb(4, 11, 6, 7.5, 0.5, Col.MAROON)
    u.limb(6, 7.5, 8, 11, 0.5, Col.MAROON)
    u.limb(6, 7.5, 11, 7.5, 0.5, Col.MAROON)
    u.limb(8, 11, 11, 7.5, 0.5, Col.MAROON)
    u.limb(11, 7.5, 12, 11, 0.5, Art.MAROON_SH)
    u.rect(5, 6, 7.5, 7, Art.SHOE)
    u.rect(10.5, 5.5, 12.5, 6.5, Art.SHOE)


def _sparkle(u: _Units) -> None:
    for x, y in ((3, 2), (12.5, 1.5), (8, 3.5)):
        u.rect(x, y, x + 0.5, y + 0.5, Art.HEADLIGHT)
    u.rect(12.5, 0.5, 13, 3, Art.SIGN_BD)
    u.rect(11.5, 1.5, 14, 2, Art.SIGN_BD)


def _item_card(u: _Units) -> None:
    """A dropped Fordham ID card, sparkling."""
    u.rect(3.5, 7, 13, 13, Art.SIGN_BD)
    u.rect(4.5, 8, 12, 9.5, Col.MAROON)
    u.rect(4.5, 10, 6.5, 12, Art.SKIN1)
    u.rect(7.5, 10.5, 11.5, 11, Art.POST)
    u.rect(7.5, 11.5, 10, 12, Art.POST)
    _sparkle(u)


def _item_package(u: _Units) -> None:
    """A cardboard package, sparkling."""
    u.rect(3, 6, 13, 14, Art.CARD_BOX)
    u.rect(10.5, 6, 13, 14, Art.CARD_BOX_SH)
    u.rect(3, 6, 13, 7, Art.WOOD_LT)
    u.rect(7.5, 6, 8.5, 14, Art.WALK)
    u.rect(9, 9.5, 12, 11.5, Art.SIGN_BD)
    _sparkle(u)


# --- Faculty Memorial Hall's tiles -------------------------------------------------

def _roof(img, x: int, y: int) -> None:
    """Slate courses, as on the hand-finished roofs."""
    img.rect(x, y, 32, 32, Art.SLATE)
    for i, ry in enumerate(range(y + 6, y + 32, 7)):
        img.rect(x, ry, 32, 1, Col.ROOF_SH)
        for sx in range(x + (6 if i % 2 else 0), x + 32, 12):
            img.rect(sx, ry - 6, 1, 6, Col.ROOF_SH)
            if (sx * 7 + ry) % 5 == 0:
                img.rect(sx + 1, ry - 6, 9, 1, Art.SLATE_HI)


def _wall(img, x: int, y: int) -> None:
    """Fordham stone in courses, each with a light edge."""
    img.rect(x, y, 32, 32, Col.STONE)
    for i, ry in enumerate(range(y, y + 32, 8)):
        img.rect(x, ry, 32, 1, Col.STONE_HI)
        img.rect(x, ry + 7, 32, 1, Col.STONE_SH)
        for sx in range(x + (8 if i % 2 else 0), x + 32, 16):
            img.rect(sx, ry + 1, 1, 6, Col.STONE_SH)


def _window(img, x: int, y: int) -> None:
    _wall(img, x, y)
    img.rect(x + 7, y + 5, 18, 21, Col.WHITE)
    img.rect(x + 8, y + 6, 16, 18, Col.LIGHT_BLUE)
    img.rect(x + 8, y + 6, 16, 5, Art.PANE_DK)
    img.rect(x + 15, y + 6, 2, 18, Col.WHITE)
    img.rect(x + 9, y + 7, 1, 3, Art.PANE_HI)
    img.rect(x + 6, y + 25, 20, 1, Art.SILL)


def _door(img, x: int, y: int) -> None:
    _wall(img, x, y)
    img.rect(x + 6, y + 6, 20, 26, Col.STONE_DK)
    img.rect(x + 8, y + 8, 16, 24, Col.BROWN)
    img.rect(x + 15, y + 8, 2, 24, Col.NAVY)
    for px in (x + 10, x + 18):
        img.rectb(px, y + 10, 4, 8, Art.WOOD_DK)
        img.rectb(px, y + 21, 4, 8, Art.WOOD_DK)
    img.rect(x + 13, y + 19, 1, 2, Col.YELLOW)
    img.rect(x + 18, y + 19, 1, 2, Col.YELLOW)


# --- the campus fence ----------------------------------------------------------------

def _fence(img, x: int, y: int, joins: int) -> None:
    """Black iron railings, light enough to see through: side on where the
    fence runs across, end on (a slim rail with posts) where it runs up
    and down, a post where it turns or ends."""
    across = bool(joins & (W | E)) or not joins & (N | S)
    if across:
        x0 = x if joins & W else x + 14
        x1 = x + 32 if joins & E else x + 18
        for ry in (y + 10, y + 24):                      # rails
            img.rect(x0, ry, x1 - x0, 1, Art.IRON)
        for px in range(x0 + 1, x1, 3):                  # pickets, each with a lit point
            img.rect(px, y + 7, 1, 20, Art.IRON)
            img.pset(px, y + 6, Art.IRON_HI)
    if joins & (N | S):
        y0 = y if joins & N else y + 14
        y1 = y + 32 if joins & S else y + 18
        img.rect(x + 15, y0, 2, y1 - y0, Art.IRON)       # the railing, end on
        img.rect(x + 15, y0, 1, y1 - y0, Art.IRON_HI)
        for py in range(y0 + 4, y1, 8):                  # pickets seen from the end
            img.rect(x + 14, py, 4, 2, Art.IRON)
            img.pset(x + 15, py, Art.IRON_HI)
    if across and joins & (N | S) or not joins:          # a post where it turns or stands alone
        img.rect(x + 14, y + 5, 4, 23, Art.IRON)
        img.rect(x + 14, y + 5, 1, 23, Art.IRON_HI)
        img.rect(x + 13, y + 4, 6, 2, Art.IRON)


# --- the sheet --------------------------------------------------------------------

DRAW = {
    "sign": _sign, "shuttle": _shuttle, "lamp": _lamp, "bench": _bench, "statue": _statue,
    "bell": _bell, "grave": _grave, "dome": _dome, "booth": _booth, "pillar": _pillar,
    "card_reader": _card_reader, "reader_gate": _reader_gate, "bike_rack": _bike_rack,
    "item_card": _item_card, "item_card_road": _item_card, "item_package": _item_package,
    "ram": _ram,
}
TILE_DRAW = {"roof": _roof, "wall": _wall, "window": _window, "door": _door}

_sheet: pyxel.Image | None = None


def sheet() -> pyxel.Image:
    global _sheet
    if _sheet is None:
        _sheet = _build()
    return _sheet


def _build() -> pyxel.Image:
    rows = -(-(FENCE_AT + 16) // PER_ROW)
    flat = pyxel.Image(PER_ROW * SLOT, rows * SLOT)
    flat.cls(Col.BLACK)
    for name, fn in DRAW.items():
        fn(_Units(flat, *uv(name)))
    # one outline round each thing, as for the people; slots keep them apart
    out = pyxel.Image(flat.width, flat.height)
    out.cls(Col.BLACK)
    for c in range(1, len(pyxel.colors)):
        out.pal(c, Art.OUTLINE)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        out.blt(dx, dy, flat, 0, 0, flat.width, flat.height, Col.BLACK)
    out.pal()
    out.blt(0, 0, flat, 0, 0, flat.width, flat.height, Col.BLACK)
    for name, fn in TILE_DRAW.items():                    # building tiles: no outline of their own
        fn(out, *uv(name))
    for j in range(16):                                   # nor the fence, so you see through it
        _fence(out, *fence_uv(j), j)
    return out
