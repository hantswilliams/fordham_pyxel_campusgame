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
}
BUILDING_PARTS = {"wall", "window", "door", "banner"}

TILE_COLORS = {
    "grass": Col.LIME, "flowers": Col.LIME, "lamp": Col.LIME, "bench": Col.PEACH,
    "sign": Col.LIME, "statue": Col.LIME, "bell": Col.LIME, "shuttle": Col.LIME,
    "path": Col.PEACH, "booth": Col.PEACH, "pillar": Col.GRAY,
    "road": Col.GRAY, "crosswalk_h": Col.WHITE, "crosswalk_v": Col.WHITE,
    "parking": Col.GRAY,
    "tree": Col.GREEN, "hedge": Col.GREEN, "field": Col.GREEN, "dirt": Col.ORANGE,
    "water": Col.CYAN, "grave": Col.GRAY, "dome": Col.WHITE,
    "fence": Col.DARK_BLUE, "offcampus": Col.NAVY,
    **ROOF_COLORS,
}

PIN_KINDS = ("transit", "landmark", "building")


def tile_colors(m: MapData) -> list[list[int]]:
    """One colour per tile. Walls, windows and doors take the colour of the
    roof above them, so each building reads as one solid footprint."""
    out = []
    for y, row in enumerate(m.tiles):
        out_row = []
        for x, name in enumerate(row):
            if name in BUILDING_PARTS:
                col = Col.GRAY
                for yy in range(y - 1, max(-1, y - 12), -1):
                    above = m.tiles[yy][x]
                    if above in ROOF_COLORS:
                        col = ROOF_COLORS[above]
                        break
                    if above not in BUILDING_PARTS:
                        break
                out_row.append(col)
            else:
                out_row.append(TILE_COLORS[name])
        out.append(out_row)
    return out


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
            if obj.location == "ram_van" or obj.location not in seen:
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
