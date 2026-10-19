"""What lies under every cell, for the finer world art (decisions/0045).

The map's tiles mix ground (grass, walkways, roads) with things standing on
it (trees, benches, signs). The finer art draws the ground across the whole
map first, with rounded lawn corners and kerbs, then stands things on it,
so it needs to know the ground under a sign or a bench too. That comes from
the neighbours: a bench in a plaza stands on paving, a sign on a lawn on
grass.

Pure Python (no Pyxel) so it can be unit-tested; game/gfx/world_art.py
draws it.
"""

from collections import Counter

from .mapdata import MapData

# ground kinds
GRASS, PATH, PLAZA, ROAD, PARKING, OFFCAMPUS = "grass", "path", "plaza", "road", "parking", "offcampus"
PAVED = {PATH, PLAZA}           # meets a lawn with an edging and rounded corners
ASPHALT = {ROAD, PARKING}       # meets anything else with a kerb

# tiles that are ground themselves
GROUND_TILES = {
    "grass": GRASS, "flowers": GRASS, "path": PATH, "plaza": PLAZA,
    "road": ROAD, "crosswalk_h": ROAD, "crosswalk_v": ROAD,
    "parking": PARKING, "offcampus": OFFCAMPUS,
}

# things standing on the ground, and the ground they stand on when the
# neighbours don't say (it's what today's tile art draws under them)
ON_GROUND = {
    "tree": GRASS, "tree_purple": GRASS, "sign": GRASS, "lamp": GRASS, "statue": GRASS,
    "bell": GRASS, "shuttle": GRASS, "grave": GRASS, "dome": GRASS, "fence": GRASS,
    "bike_rack": GRASS, "bench": PATH, "pillar": PATH, "booth": PATH, "reader_gate": PATH,
    "card_reader": PATH, "item_card": PATH, "item_package": PATH, "item_card_road": ROAD,
    "car": PARKING,
}
# ...of which these are drawn in the finer style each frame, not baked into the map
TREES = {"tree", "tree_purple"}

# Everything else (building parts, hedges, water, fields) is drawn whole,
# from today's tile art: it has no ground of its own.

CORNERS = ("nw", "ne", "sw", "se")
_CORNER_DIRS = {"nw": (-1, -1), "ne": (1, -1), "sw": (-1, 1), "se": (1, 1)}
_ORDER = (GRASS, PATH, PLAZA, ROAD, PARKING, OFFCAMPUS)   # breaks ties


def base_tiles(m: MapData) -> list[list[str]]:
    """The map's tiles without the ones that change while you play: a
    mission item shows the tile it lies on, a closed gate the tile it opens
    to. Those are drawn on top each frame instead."""
    tiles = [row[:] for row in m.tiles]
    for (x, y), under in m._under.items():          # mission items put down at runtime
        tiles[y][x] = under
    for o in m.objects:
        if o.type == "checkpoint":
            tiles[o.y][o.x] = o.open_tile
    return tiles


def ground_grid(m: MapData, pictured=()) -> list[list[str | None]]:
    """The ground kind under every cell, [y][x]; None under things drawn
    whole (see base_tiles for the cells that change). Cells under a drawn
    building's picture (`pictured`) get ground too, from their neighbours,
    to show through wherever the picture is see-through (round a fountain)."""
    tiles = base_tiles(m)
    grid: list[list[str | None]] = [[GROUND_TILES.get(t) for t in row] for row in tiles]
    for y, row in enumerate(tiles):
        for x, t in enumerate(row):
            if t in ON_GROUND:
                grid[y][x] = _from_neighbours(grid, x, y, ON_GROUND[t])
    for x, y in sorted(pictured, key=lambda c: (c[1], c[0])):
        if grid[y][x] is None:
            grid[y][x] = _from_neighbours(grid, x, y, GRASS)
    return grid


def _from_neighbours(grid, x: int, y: int, default: str) -> str:
    seen = Counter()
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        g = at(grid, x + dx, y + dy)
        if g is not None and g != OFFCAMPUS:
            seen[g] += 1
    if not seen:
        return default
    best = max(seen.values())
    tied = [g for g in _ORDER if seen[g] == best]
    return default if default in tied else tied[0]


def at(grid, x: int, y: int) -> str | None:
    if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
        return grid[y][x]
    return None


def lawn_corners(grid, x: int, y: int) -> list[tuple[str, str]]:
    """The corners of a lawn cell that round off because paving wraps round
    them: (corner, the paving's kind) for each corner whose two side
    neighbours are both walkway or plaza."""
    if at(grid, x, y) != GRASS:
        return []
    out = []
    for c in CORNERS:
        dx, dy = _CORNER_DIRS[c]
        a, b = at(grid, x, y + dy), at(grid, x + dx, y)
        if a in PAVED and b in PAVED:
            out.append((c, a))
    return out


def paving_corners(grid, x: int, y: int) -> list[str]:
    """The corners of a walkway or plaza cell that round off because lawn
    wraps round them: both side neighbours at that corner are lawn. Where
    the paving carries on corner to corner (a walkway drawn as a staircase)
    the corner stays square, and the lawns' corners round off instead, so
    the walkway joins up."""
    if at(grid, x, y) not in PAVED:
        return []
    out = []
    for c in CORNERS:
        dx, dy = _CORNER_DIRS[c]
        if (at(grid, x, y + dy) == GRASS and at(grid, x + dx, y) == GRASS
                and at(grid, x + dx, y + dy) not in PAVED):
            out.append(c)
    return out


def edging(grid, x: int, y: int) -> list[tuple[str, bool, bool]]:
    """Where a walkway or plaza cell gets a darker edging against a lawn:
    (side, cut at its start, cut at its end) for each side that touches a
    lawn. A side is cut short at an end where a rounded corner takes over
    the edging (one of this cell's, or the lawn's). Sides run left to right
    (top, bottom) or top to bottom (left, right)."""
    if at(grid, x, y) not in PAVED:
        return []
    out = []
    for side, (dx, dy) in (("top", (0, -1)), ("bottom", (0, 1)), ("left", (-1, 0)), ("right", (1, 0))):
        if at(grid, x + dx, y + dy) != GRASS:
            continue
        cuts = []
        for end in (-1, 1):
            # the neighbour of this cell, and of the lawn, at this end of the side
            ex, ey = (x + end, y) if dy else (x, y + end)
            mine = at(grid, ex, ey)
            lawns = at(grid, ex + dx, ey + dy)
            cuts.append(mine == GRASS or lawns in PAVED)
        out.append((side, cuts[0], cuts[1]))
    return out


KERBED = PAVED | {GRASS}        # what a road or car park gets a kerb against


def kerbs(grid, x: int, y: int) -> list[tuple[str, bool, bool]]:
    """Where a road or parking cell gets a kerb: (side, cut at its start,
    cut at its end) for each side that meets a walkway, plaza or lawn. As
    with edging(), a side is cut short where a rounded corner takes over."""
    if at(grid, x, y) not in ASPHALT:
        return []
    out = []
    for side, (dx, dy) in (("top", (0, -1)), ("bottom", (0, 1)), ("left", (-1, 0)), ("right", (1, 0))):
        if at(grid, x + dx, y + dy) not in KERBED:
            continue
        cuts = []
        for end in (-1, 1):
            ex, ey = (x + end, y) if dy else (x, y + end)
            mine = at(grid, ex, ey)
            across = at(grid, ex + dx, ey + dy)
            cuts.append((mine in KERBED and across not in ASPHALT) or across in ASPHALT)
        out.append((side, cuts[0], cuts[1]))
    return out


def road_corners(grid, x: int, y: int) -> list[tuple[str, str]]:
    """The corners of a road or parking cell that round off because a
    walkway, plaza or lawn wraps round them: (corner, what wraps round, from
    the cell above or below). Where the road carries on corner to corner (a
    road drawn as a staircase) the corner stays square, so the road joins up."""
    if at(grid, x, y) not in ASPHALT:
        return []
    out = []
    for c in CORNERS:
        dx, dy = _CORNER_DIRS[c]
        a, b = at(grid, x, y + dy), at(grid, x + dx, y)
        if a in KERBED and b in KERBED and at(grid, x + dx, y + dy) not in ASPHALT:
            out.append((c, a))
    return out


def kerb_corners(grid, x: int, y: int) -> list[tuple[str, str]]:
    """The corners of a walkway, plaza or lawn cell that a road wraps round:
    (corner, the asphalt's kind) where both side neighbours at that corner
    are road or parking. The road fills the corner, with its kerb curving."""
    if at(grid, x, y) not in KERBED:
        return []
    out = []
    for c in CORNERS:
        dx, dy = _CORNER_DIRS[c]
        a, b = at(grid, x, y + dy), at(grid, x + dx, y)
        if a in ASPHALT and b in ASPHALT:
            out.append((c, a))
    return out
