"""Data for the in-game campus map (decisions/0017). Pure Python, no Pyxel:
what colour each tile is on the map, which places get pins, and how the
arrow keys move between pins."""

from dataclasses import dataclass

from game.config import Col

from .directions import Direction
from .locations import Location
from .mapdata import MapData

SCALE = 2  # map pixels per tile

ROOF_COLORS = {
    "roof": Col.DARK_BLUE,         # academic
    "roof_res": Col.ORANGE,        # residence hall
    "roof_other": Col.LIGHT_BLUE,  # other campus building
    "roof_maroon": Col.MAROON,     # Office of Undergraduate Admission
    "modern_roof": Col.ORANGE,     # Campbell (a residence hall)
    "lib_tower": Col.LIGHT_BLUE,   # Walsh Library's tower sits on its roof
}
BUILDING_PARTS = {"wall", "window", "door", "banner",
                  "lib_stone", "glass_arch", "lib_window",
                  "modern_wall", "glass_tower", "glass_door"}

TILE_COLORS = {
    "grass": Col.LIME, "flowers": Col.LIME, "lamp": Col.LIME, "bench": Col.PEACH,
    "sign": Col.LIME, "bike_rack": Col.LIME, "item_card": Col.PEACH, "item_card_road": Col.WHITE, "card_reader": Col.NAVY, "item_package": Col.PEACH, "statue": Col.LIME, "bell": Col.LIME, "shuttle": Col.LIME,
    "path": Col.PEACH, "plaza": Col.PEACH, "booth": Col.PEACH, "pillar": Col.GRAY, "reader_gate": Col.PEACH,
    "road": Col.GRAY, "crosswalk_h": Col.WHITE, "crosswalk_v": Col.WHITE,
    "parking": Col.GRAY, "car": Col.GRAY,
    "tree": Col.GREEN, "tree_purple": Col.GREEN, "hedge": Col.GREEN, "field": Col.GREEN, "dirt": Col.ORANGE,
    "water": Col.CYAN, "grave": Col.GRAY, "dome": Col.WHITE,
    "fence": Col.DARK_BLUE, "offcampus": Col.STONE,
    **ROOF_COLORS,
}

PIN_KINDS = ("transit", "landmark", "building")


def tile_colors(m: MapData) -> list[list[int]]:
    """One colour per tile. Walls, windows and doors take the colour of the
    nearest roof of the same building (above, below or beside them, since
    some buildings face north or east), so each building reads as one
    solid footprint."""
    out = []
    for y, row in enumerate(m.tiles):
        out_row = []
        for x, name in enumerate(row):
            if name in BUILDING_PARTS:
                out_row.append(_building_color(m, x, y))
            else:
                out_row.append(TILE_COLORS[name])
        out.append(out_row)
    return out


def _building_color(m: MapData, x: int, y: int) -> int:
    """Breadth-first search through the building's own wall tiles for a roof."""
    seen = {(x, y)}
    frontier = [(x, y)]
    for _ in range(12):
        nxt = []
        for cx, cy in frontier:
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                nx, ny = cx + dx, cy + dy
                if (nx, ny) in seen or not m.in_bounds(nx, ny):
                    continue
                seen.add((nx, ny))
                t = m.tiles[ny][nx]
                if t in ROOF_COLORS:
                    return ROOF_COLORS[t]
                if t in BUILDING_PARTS:
                    nxt.append((nx, ny))
        frontier = nxt
    return Col.GRAY


@dataclass
class Pin:
    name: str
    x: int
    y: int
    kind: str  # "transit" | "landmark" | "building"
    location: str


def pin_kind(loc: Location) -> str:
    if loc.kind == "transit":
        return "transit"
    if loc.kind == "landmark":
        return "landmark"
    return "building"


def build_pins(m: MapData, locations: dict[str, Location]) -> list[Pin]:
    """Gates and shuttle stops (every one), plus one pin per Campus Guide place."""
    pins: list[Pin] = []
    seen: set[str] = set()
    for obj in m.objects:
        loc = locations.get(obj.location) if obj.location else None
        if loc is None:
            continue
        if loc.kind == "transit":
            if obj.location == "campus_shuttle" or obj.location not in seen:
                pins.append(Pin(loc.name, obj.x, obj.y, "transit", loc.id))
                seen.add(obj.location)
        elif loc.guide and obj.location not in seen:
            pins.append(Pin(loc.name, obj.x, obj.y, pin_kind(loc), loc.id))
            seen.add(obj.location)
    return pins


def next_pin(pins: list[Pin], x: int, y: int, d: Direction) -> int | None:
    """Index of the best pin in direction `d` from (x, y): within about 60
    degrees of that direction, preferring ones close to the straight line."""
    best, best_score = None, None
    for i, p in enumerate(pins):
        dx, dy = p.x - x, p.y - y
        along = dx * d.dx + dy * d.dy
        if along <= 0:
            continue
        across = abs(dx * d.dy) + abs(dy * d.dx)
        if across > 2 * along:
            continue  # more sideways than ahead: not really "in that direction"
        score = along + 2 * across
        if best_score is None or score < best_score:
            best, best_score = i, score
    return best


# --- the detailed campus map (decisions/0032) --------------------------------
DETAIL = 4      # map pixels per tile in the main view: the real art, shrunk 4x
OVERVIEW = 6    # the corner overview shrinks the detailed map 6x more (~0.67 px per tile)


def downsample(raw: bytes, w: int, h: int, k: int, rgb: list[tuple[int, int, int]]) -> bytes:
    """Shrink a palette image `k` times by averaging each k x k block's
    colours and snapping the average to the nearest palette colour. This is
    what makes the map look painted rather than blocky. `raw` holds one
    palette index per pixel, row by row. Returns the smaller image the same
    way. Blocks repeat a lot (lawn, road, roof), so results are cached."""
    ow, oh = w // k, h // k
    out = bytearray(ow * oh)
    cache: dict[bytes, int] = {}
    n = k * k
    for oy in range(oh):
        rows = [raw[(oy * k + j) * w:(oy * k + j) * w + w] for j in range(k)]
        for ox in range(ow):
            x0 = ox * k
            key = b"".join(r[x0:x0 + k] for r in rows)
            v = cache.get(key)
            if v is None:
                r = g = b = 0
                for ci in key:
                    cr, cg, cb = rgb[ci]
                    r += cr; g += cg; b += cb
                r, g, b = r / n, g / n, b / n
                v = min(range(1, len(rgb)),  # never black: black is transparent
                        key=lambda i: (rgb[i][0] - r) ** 2 + (rgb[i][1] - g) ** 2 + (rgb[i][2] - b) ** 2)
                cache[key] = v
            out[oy * ow + ox] = v
    return bytes(out)
