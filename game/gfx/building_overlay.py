"""The shared house style's finishing touches (decisions/0021), drawn over
the map once when it loads:

- a thin navy outline around every tile building, and a dark eave line
  where its roof meets its front wall
- a maroon mat outside every door
- a name plaque above every building's entrance (its `short_name` in
  content/locations.json)

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
CHAR_W = 4      # Pyxel's built-in font: 4 px per character
PLAQUE_H = 9


def plaque_width(text: str) -> int:
    return len(text) * CHAR_W + 5


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
        if b.location == loc and b.nameplate:
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


def draw_plaque(target, cx: int, ty: int, text: str) -> None:
    w = plaque_width(text)
    x0 = cx - w // 2
    target.rect(x0, ty, w, PLAQUE_H, Col.STONE_HI)
    target.rectb(x0, ty, w, PLAQUE_H, Col.NAVY)
    target.text(x0 + 3, ty + 2, text, Col.NAVY)


def draw_overlay(target, m: MapData, locations: dict) -> None:
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

    for loc, groups in door_groups(m).items():
        for group in groups:
            for x, y in group:                   # a mat outside each door
                if not m.is_blocked(x, y + 1):
                    px, py = x * TILE, (y + 1) * TILE
                    target.rect(px + 2, py, TILE - 4, 3, Col.MAROON)
                    target.line(px + 2, py + 1, px + TILE - 3, py + 1, Col.PINK)
            name = getattr(locations.get(loc), "short_name", "")
            if name:
                cx, ty, _ = plaque_spot(m, loc, group)
                draw_plaque(target, cx, ty, name)
