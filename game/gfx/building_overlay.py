"""The shared house style's finishing touches (decisions/0021), drawn over
the map once when it loads:

- a thin navy outline around every tile building, and a dark eave line
  where its roof meets its front wall
- a maroon mat outside every door
- a name plaque above every building's entrance (its `short_name` in
  content/locations.json), on a doorless landmark that sets a `nameplate`,
  and over a sports field's gate

Drawn buildings (assets/buildings/) carry their own outline in map.png;
they get mats and plaques from here like everyone else, so all plaques
look the same. Pure black is transparent, as everywhere.
"""

from game.config import TILE, Col
from game.world.mapdata import MapData
from game.world.minimap import BUILDING_PARTS, ROOF_COLORS

ROOFS = set(ROOF_COLORS)
WALLS = set(BUILDING_PARTS)
BUILDING_TILES = ROOFS | WALLS
# Plaque lettering (decisions/0036): PixelMplus 10, 5 px per character, so
# names stay readable on the 384 x 288 screen
PLAQUE_FONT = "PixelMplus10-Regular.ttf"
CHAR_W = 5
PLAQUE_H = 11

_plaque_font = None


def plaque_font():
    global _plaque_font
    if _plaque_font is None:
        import pyxel
        from game import config
        _plaque_font = pyxel.Font(str(config.ROOT / "assets" / "fonts" / PLAQUE_FONT), 10)
    return _plaque_font


SMALL_CHAR_W = 4  # Pyxel's built-in font, for a name too long for its wall


def plaque_width(text: str, small: bool = False) -> int:
    return len(text) * (SMALL_CHAR_W if small else CHAR_W) + 5


def fits(text: str, room: int, small: bool = False) -> bool:
    return plaque_width(text, small) <= room - 2


def door_groups(m: MapData) -> dict[str, list[list[tuple[int, int]]]]:
    """Each location's door cells, split into runs of side-by-side doors."""
    by_loc: dict[str, list[tuple[int, int]]] = {}
    for o in m.objects:
        if o.type == "door" and o.location:
            by_loc.setdefault(o.location, []).append((o.x, o.y))
    out = {}
    for loc, cells in by_loc.items():
        groups: list[list[tuple[int, int]]] = []
        for c in sorted(cells, key=lambda c: (c[1], c[0])):
            g = groups[-1] if groups else None
            if g and g[-1][1] == c[1] and g[-1][0] + 1 == c[0]:
                g.append(c)
            else:
                groups.append([c])
        out[loc] = groups
    return out


def tile_building_cells(m: MapData) -> set[tuple[int, int]]:
    drawn = {(x, y) for b in m.buildings for x, y, _ in b.cells()}
    return {(x, y) for y, row in enumerate(m.tiles) for x, t in enumerate(row)
            if t in BUILDING_TILES and (x, y) not in drawn}


def plaque_spot(m: MapData, loc: str, group: list[tuple[int, int]]) -> tuple[int, int, int]:
    """(centre x, top y, room) in map pixels for a door group's plaque;
    `room` is the width of wall it has to fit on."""
    for b in m.buildings:
        # a place can span several drawn buildings (Martyrs' Court's wings):
        # use the one this door group belongs to
        if b.location == loc and b.nameplate and tuple(group[0]) in b.entrances():
            ox, oy = b.origin
            return ox * TILE + b.nameplate[0], oy * TILE + b.nameplate[1], b.size[0] * TILE
    y = group[0][1]
    x0, x1 = group[0][0], group[-1][0]
    cx = (x0 * TILE + (x1 + 1) * TILE) // 2
    above = y - 1
    if 0 <= above < m.height and m.tiles[above][x0] in WALLS:
        left, right = x0, x1                     # the wall row above the doors
        while left - 1 >= 0 and m.tiles[above][left - 1] in WALLS:
            left -= 1
        while right + 1 < m.width and m.tiles[above][right + 1] in WALLS:
            right += 1
        return cx, above * TILE + 4, (right - left + 1) * TILE
    return cx, y * TILE - PLAQUE_H + 1, (x1 - x0 + 3) * TILE


def draw_plaque(target, cx: int, ty: int, text: str, room: int | None = None,
                labels: list | None = None) -> None:
    """A stone name plaque centred at cx. If the name is too long for the
    wall (`room`), it's lettered in Pyxel's smaller built-in font instead.
    With `labels`, only the plaque is drawn and its lettering is added to
    the list as (x, cap top y, text, character width), for the crisp screen
    to letter at full detail each frame (decisions/0039)."""
    small = room is not None and not fits(text, room)
    w = plaque_width(text, small)
    x0 = cx - w // 2
    target.rect(x0, ty, w, PLAQUE_H, Col.STONE_HI)
    target.rectb(x0, ty, w, PLAQUE_H, Col.NAVY)
    if labels is not None:
        cell = SMALL_CHAR_W if small else CHAR_W
        cap = cell * 1.46                        # M PLUS 1 Code's capitals, for a cell this wide
        labels.append((x0 + 3, ty + (PLAQUE_H - cap) / 2, text, cell))
    elif small:
        target.text(x0 + 3, ty + 3, text, Col.NAVY)
    else:
        target.text(x0 + 3, ty, text, Col.NAVY, plaque_font())


def plaque_spots(m: MapData, locations: dict) -> list[tuple[int, int, str, int | None]]:
    """(centre x, top y, name, room) for every plaque, in map pixels: above
    each entrance, on a doorless landmark that sets a `nameplate`, and over a
    sports field's gate. `room` is the wall it must fit on, if any."""
    out = []
    for loc, groups in door_groups(m).items():
        name = getattr(locations.get(loc), "short_name", "")
        if name:
            for group in groups:
                cx, ty, room = plaque_spot(m, loc, group)
                out.append((cx, ty, name, room))
    for b in m.buildings:
        name = getattr(locations.get(b.location), "short_name", "")
        if not name or b.entrances():
            continue
        ox, oy = b.origin
        if b.nameplate:
            out.append((ox * TILE + b.nameplate[0], oy * TILE + b.nameplate[1], name, None))
        elif b.gate is not None:
            out.append((*gate_plaque_spot(b, name), name, None))
    return out


def mat_spots(m: MapData) -> list[tuple[int, int, str]]:
    """(cell x, cell y, edge) for every door mat: outside each door, and just
    inside a sports field's gate. `edge` is the side of the cell it lies along."""
    out = []
    for groups in door_groups(m).values():
        for group in groups:
            for x, y in group:
                if not m.is_blocked(x, y + 1):
                    out.append((x, y + 1, "top"))
    for b in m.buildings:
        if b.gate is None:
            continue
        dx, dy = {"south": (0, 1), "north": (0, -1), "west": (-1, 0), "east": (1, 0)}[b.gate_faces]
        x, y = b.origin[0] + b.gate[0] + dx, b.origin[1] + b.gate[1] + dy
        if 0 <= x < m.width and 0 <= y < m.height and not m.is_blocked(x, y):
            out.append((x, y, {(0, 1): "top", (0, -1): "bottom", (1, 0): "left", (-1, 0): "right"}[(dx, dy)]))
    return out


def draw_overlay(target, m: MapData, locations: dict, labels: list | None = None) -> None:
    """Draw outlines, eaves, mats and plaques into `target` (a pyxel.Image
    the size of the map, or the screen with the camera set)."""
    cells = tile_building_cells(m)
    for x, y in cells:
        px, py = x * TILE, y * TILE
        e = TILE - 1
        if (x, y - 1) not in cells:
            target.line(px, py, px + e, py, Col.NAVY)
        if (x, y + 1) not in cells:
            target.line(px, py + e, px + e, py + e, Col.NAVY)
        if (x - 1, y) not in cells:
            target.line(px, py, px, py + e, Col.NAVY)
        if (x + 1, y) not in cells:
            target.line(px + e, py, px + e, py + e, Col.NAVY)
        # eave: where a roof meets the front wall below it
        if m.tiles[y][x] in ROOFS and (x, y + 1) in cells and m.tiles[y + 1][x] in WALLS:
            target.line(px, py + e, px + e, py + e, Col.NAVY)
            target.line(px, py + TILE, px + e, py + TILE, Col.ROOF_SH)
    for x, y, edge in mat_spots(m):
        px, py = x * TILE, y * TILE
        if edge in ("top", "bottom"):
            py += 0 if edge == "top" else TILE - 3
            target.rect(px + 2, py, TILE - 4, 3, Col.MAROON)
            target.line(px + 2, py + 1, px + TILE - 3, py + 1, Col.PINK)
        else:
            px += 0 if edge == "left" else TILE - 3
            target.rect(px, py + 2, 3, TILE - 4, Col.MAROON)
            target.line(px + 1, py + 2, px + 1, py + TILE - 3, Col.PINK)
    for cx, ty, name, room in plaque_spots(m, locations):
        draw_plaque(target, cx, ty, name, room, labels)


def gate_plaque_spot(b, name: str) -> tuple[int, int]:
    """(centre x, top y) for the plaque over a field's gate: just above the
    gate, lined up with the side it opens to, kept on the field."""
    ox, oy = b.origin
    gx, gy = ox + b.gate[0], oy + b.gate[1]
    w = plaque_width(name)
    if b.gate_faces == "west":
        cx = gx * TILE + w // 2
    elif b.gate_faces == "east":
        cx = (gx + 1) * TILE - w // 2
    else:
        cx = gx * TILE + TILE // 2
    left, right = ox * TILE, (ox + b.size[0]) * TILE
    cx = min(max(cx, left + w // 2 + 1), right - w // 2 - 1)
    ty = gy * TILE - PLAQUE_H - 1 if b.gate_faces != "north" else (gy + 1) * TILE + 1
    return cx, max(ty, oy * TILE + 1)
