"""Load a map from a pair of content files:

    content/maps/<name>.txt   - ASCII grid, one character per 16x16 tile
    content/maps/<name>.json  - display name + objects (signs, NPCs, doors)

Pure Python (no Pyxel) so it can be unit-tested.
See decisions/0005-map-authoring.md for why maps are text files for now.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

from .directions import Direction
from .tiles import LEGEND, SPAWN_CHAR, SPAWN_GROUND, TILES

OBJECT_TYPES = {"sign", "npc", "door"}


class MapError(ValueError):
    pass


@dataclass
class MapObject:
    id: str
    type: str  # "sign" | "npc" | "door"
    x: int
    y: int
    name: str = ""
    lines: list[str] = field(default_factory=list)
    tile: str | None = None  # tile art drawn at this cell (sign, door)
    ground: str = "path"  # tile drawn underneath (npc)
    sprite: int = 0  # character sheet row (npc)
    facing: Direction = Direction.DOWN


@dataclass
class MapData:
    id: str
    display_name: str
    width: int
    height: int
    tiles: list[list[str]]  # tile names, [y][x]
    objects: list[MapObject]
    spawn: tuple[int, int]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def object_at(self, x: int, y: int) -> MapObject | None:
        for obj in self.objects:
            if obj.x == x and obj.y == y:
                return obj
        return None

    def is_blocked(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return True
        if TILES[self.tiles[y][x]].solid:
            return True
        return self.object_at(x, y) is not None


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

    object_defs: dict = meta.get("objects", {})
    tiles: list[list[str]] = []
    objects: list[MapObject] = []
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
            elif ch in object_defs:
                obj = _make_object(map_id, ch, object_defs[ch], x, y)
                objects.append(obj)
                tile_row.append(obj.tile or obj.ground)
            else:
                raise MapError(
                    f"{map_id}: unknown character {ch!r} at ({x}, {y}). "
                    "Add it to the legend or define it under 'objects' in the .json"
                )
        tiles.append(tile_row)

    if spawn is None:
        raise MapError(f"{map_id}: no player spawn '@'")

    return MapData(
        id=map_id,
        display_name=meta.get("display_name", map_id),
        width=width,
        height=len(rows),
        tiles=tiles,
        objects=objects,
        spawn=spawn,
    )


def _make_object(map_id: str, ch: str, d: dict, x: int, y: int) -> MapObject:
    kind = d.get("type")
    if kind not in OBJECT_TYPES:
        raise MapError(f"{map_id}: object {ch!r} has unknown type {kind!r}")
    tile = d.get("tile")
    ground = d.get("ground", "path")
    for t in (tile, ground):
        if t is not None and t not in TILES:
            raise MapError(f"{map_id}: object {ch!r} uses unknown tile {t!r}")
    lines = d.get("lines", [])
    if not lines:
        raise MapError(f"{map_id}: object {ch!r} has no 'lines' to show")
    return MapObject(
        id=ch,
        type=kind,
        x=x,
        y=y,
        name=d.get("name", ""),
        lines=list(lines),
        tile=tile,
        ground=ground,
        sprite=d.get("sprite", 0),
        facing=Direction.from_name(d.get("facing", "down")),
    )


def load_map(map_id: str, maps_dir: Path) -> MapData:
    text = (maps_dir / f"{map_id}.txt").read_text(encoding="utf-8")
    meta = json.loads((maps_dir / f"{map_id}.json").read_text(encoding="utf-8"))
    return parse_map(map_id, text, meta)
