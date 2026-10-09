"""Load a map from a pair of content files:

    content/maps/<name>.txt   - ASCII grid, one character per 16x16 tile
                                (legend in game/world/tiles.py)
    content/maps/<name>.json  - display name, named areas, and objects
                                (signs, NPCs, doors, landmarks) placed by
                                x/y tile coordinates

Pure Python (no Pyxel) so it can be unit-tested.
See decisions/0005-map-authoring.md for why maps are text files for now.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

from .directions import Direction
from .tiles import LEGEND, SPAWN_CHAR, SPAWN_GROUND, TILES

OBJECT_TYPES = {"sign", "npc", "door", "checkpoint"}


class MapError(ValueError):
    pass


@dataclass
class MapObject:
    type: str  # "sign" | "npc" | "door"
    x: int
    y: int
    name: str = ""
    lines: list[str] = field(default_factory=list)
    location: str | None = None  # id in content/locations.json -> building card
    tile: str | None = None  # art drawn at this cell (sign, statue...)
    sprite: int = 0  # character sheet row (npc)
    facing: Direction = Direction.DOWN
    auto: bool = False  # npc starts talking when the player walks up to it
    # checkpoint only: a gate a guard opens after checking your ID
    after_lines: list[str] = field(default_factory=list)
    open_tile: str = "path"


@dataclass
class Area:
    name: str
    x: int
    y: int
    w: int
    h: int

    def contains(self, x: int, y: int) -> bool:
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h


@dataclass
class MapData:
    id: str
    display_name: str
    width: int
    height: int
    tiles: list[list[str]]  # tile names, [y][x]
    objects: list[MapObject]
    spawn: tuple[int, int]
    spawn_facing: Direction = Direction.DOWN
    areas: list[Area] = field(default_factory=list)
    _by_pos: dict = field(default_factory=dict, repr=False)

    def __post_init__(self):
        self._by_pos = {(o.x, o.y): o for o in self.objects}

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def object_at(self, x: int, y: int) -> MapObject | None:
        return self._by_pos.get((x, y))

    def is_blocked(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return True
        if TILES[self.tiles[y][x]].solid:
            return True
        return (x, y) in self._by_pos

    def auto_npc_next_to(self, x: int, y: int, greeted: set) -> tuple[MapObject, Direction] | None:
        """An 'auto' NPC beside (x, y) that hasn't greeted the player yet,
        and the direction from the player to it."""
        for d in Direction:
            obj = self.object_at(x + d.dx, y + d.dy)
            if obj and obj.type == "npc" and obj.auto and (obj.x, obj.y) not in greeted:
                return obj, d
        return None

    def open_checkpoint(self, x: int, y: int) -> bool:
        """Open the checkpoint at (x, y): it stops blocking and its tile
        becomes `open_tile`. Returns False if there's no checkpoint there."""
        obj = self._by_pos.get((x, y))
        if obj is None or obj.type != "checkpoint":
            return False
        del self._by_pos[(x, y)]
        self.objects.remove(obj)
        self.tiles[y][x] = obj.open_tile
        return True

    def checkpoints(self) -> list[MapObject]:
        return [o for o in self.objects if o.type == "checkpoint"]

    def area_at(self, x: int, y: int) -> Area | None:
        """First area (in file order) containing the tile, or None."""
        for area in self.areas:
            if area.contains(x, y):
                return area
        return None


def parse_map(map_id: str, text: str, meta: dict) -> MapData:
    rows = [line.rstrip("\n") for line in text.strip("\n").splitlines()]
    if not rows:
        raise MapError(f"{map_id}: map is empty")
    width = len(rows[0])
    for y, row in enumerate(rows):
        if len(row) != width:
            raise MapError(
                f"{map_id}: row {y} has {len(row)} chars, expected {width}"
            )

    tiles: list[list[str]] = []
    spawn = None
    for y, row in enumerate(rows):
        tile_row = []
        for x, ch in enumerate(row):
            if ch in LEGEND:
                tile_row.append(LEGEND[ch])
            elif ch == SPAWN_CHAR:
                if spawn is not None:
                    raise MapError(f"{map_id}: more than one spawn '@'")
                spawn = (x, y)
                tile_row.append(SPAWN_GROUND)
            else:
                raise MapError(
                    f"{map_id}: unknown character {ch!r} at ({x}, {y}). "
                    "See LEGEND in game/world/tiles.py"
                )
        tiles.append(tile_row)
    if spawn is None:
        raise MapError(f"{map_id}: no player spawn '@'")

    height = len(rows)
    objects = []
    seen: set[tuple[int, int]] = set()
    for i, d in enumerate(meta.get("objects", [])):
        obj = _make_object(map_id, i, d, width, height)
        if (obj.x, obj.y) in seen:
            raise MapError(f"{map_id}: two objects at {(obj.x, obj.y)}")
        seen.add((obj.x, obj.y))
        if obj.tile:
            tiles[obj.y][obj.x] = obj.tile
        objects.append(obj)

    areas = [Area(a["name"], *a["rect"]) for a in meta.get("areas", [])]

    return MapData(
        id=map_id,
        display_name=meta.get("display_name", map_id),
        width=width,
        height=height,
        tiles=tiles,
        objects=objects,
        spawn=spawn,
        spawn_facing=Direction.from_name(meta.get("spawn_facing", "down")),
        areas=areas,
    )


def _make_object(map_id: str, i: int, d: dict, width: int, height: int) -> MapObject:
    where = f"{map_id}: object #{i}"
    kind = d.get("type")
    if kind not in OBJECT_TYPES:
        raise MapError(f"{where} has unknown type {kind!r}")
    try:
        x, y = d["at"]
    except (KeyError, ValueError, TypeError):
        raise MapError(f'{where} needs "at": [x, y]')
    if not (0 <= x < width and 0 <= y < height):
        raise MapError(f"{where} at {(x, y)} is outside the map")
    tile = d.get("tile")
    if tile is not None and tile not in TILES:
        raise MapError(f"{where} uses unknown tile {tile!r}")
    lines = list(d.get("lines", []))
    location = d.get("location")
    if not lines and not location:
        raise MapError(f"{where} at {(x, y)} needs 'lines' or a 'location'")
    return MapObject(
        type=kind,
        x=x,
        y=y,
        name=d.get("name", ""),
        lines=lines,
        location=location,
        tile=tile,
        sprite=d.get("sprite", 0),
        facing=Direction.from_name(d.get("facing", "down")),
        auto=bool(d.get("auto", False)),
        after_lines=list(d.get("after_lines", [])),
        open_tile=d.get("open_tile", "path"),
    )


def load_map(map_id: str, maps_dir: Path) -> MapData:
    text = (maps_dir / f"{map_id}.txt").read_text(encoding="utf-8")
    meta = json.loads((maps_dir / f"{map_id}.json").read_text(encoding="utf-8"))
    return parse_map(map_id, text, meta)
