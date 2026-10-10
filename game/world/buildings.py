"""Buildings drawn as whole pictures instead of tiles (decisions/0020).

Each building with its own folder in assets/buildings/<id>/ has:

    building.json   where it sits on which map, its footprint (which cells
                    are solid, which are entrances), which way it faces,
                    its review status
    map.png         the picture drawn over the map (optional: without it,
                    the footprint's tiles show instead)
    card.png        the picture on its building card (optional)

The footprint is the source of truth for what you bump into and which
spots open the building card. It is written with the same characters as
the map files (legend in game/world/tiles.py); ' ' leaves the map's own
cell alone. Every entrance-type cell (DOOR_TILES) becomes a door object
that opens the building's card.

Pure Python (no Pyxel) so it can be unit-tested; game/gfx/building_art.py
loads the pictures.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

from .tiles import DOOR_TILES, LEGEND

STATUSES = ("draft", "in review", "approved")
FACINGS = ("north", "south", "east", "west")


class BuildingError(ValueError):
    pass


@dataclass
class BuildingAsset:
    id: str
    name: str
    map_id: str
    location: str  # id in content/locations.json
    origin: tuple[int, int]  # map tile of the footprint's top-left cell
    footprint: list[str]
    faces: str = "south"
    status: str = "draft"
    # where map.png's top-left goes, in pixels from the footprint's top-left
    # (negative y lets a tower rise above the footprint)
    sprite_offset: tuple[int, int] = (0, 0)
    folder: Path | None = None
    notes: dict = field(default_factory=dict)

    @property
    def map_png(self) -> Path | None:
        p = self.folder / "map.png" if self.folder else None
        return p if p and p.exists() else None

    @property
    def card_png(self) -> Path | None:
        p = self.folder / "card.png" if self.folder else None
        return p if p and p.exists() else None

    def cells(self):
        """(map x, map y, tile name) for every footprint cell that isn't ' '."""
        ox, oy = self.origin
        for j, row in enumerate(self.footprint):
            for i, ch in enumerate(row):
                if ch != " ":
                    yield ox + i, oy + j, LEGEND[ch]

    def entrances(self) -> list[tuple[int, int]]:
        return [(x, y) for x, y, t in self.cells() if t in DOOR_TILES]

    @property
    def size(self) -> tuple[int, int]:
        """Footprint size in tiles (width, height)."""
        return max(len(r) for r in self.footprint), len(self.footprint)


def parse_building(d: dict, folder: Path | None = None) -> BuildingAsset:
    bid = d.get("id") or (folder.name if folder else "?")
    where = f"building {bid!r}"
    for key in ("name", "map", "location", "origin", "footprint"):
        if key not in d:
            raise BuildingError(f"{where}: building.json needs {key!r}")
    rows = d["footprint"]
    if not rows or not all(isinstance(r, str) for r in rows):
        raise BuildingError(f"{where}: 'footprint' must be a list of strings")
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != " " and ch not in LEGEND:
                raise BuildingError(
                    f"{where}: footprint row {j} has unknown character {ch!r} "
                    f"at column {i}. Use the map legend (game/world/tiles.py)")
    status = d.get("status", "draft")
    if status not in STATUSES:
        raise BuildingError(f"{where}: status must be one of {STATUSES}")
    faces = d.get("faces", "south")
    if faces not in FACINGS:
        raise BuildingError(f"{where}: faces must be one of {FACINGS}")
    b = BuildingAsset(
        id=bid,
        name=d["name"],
        map_id=d["map"],
        location=d["location"],
        origin=tuple(d["origin"]),
        footprint=list(rows),
        faces=faces,
        status=status,
        sprite_offset=tuple(d.get("sprite_offset", (0, 0))),
        folder=folder,
        notes={k: v for k, v in d.items() if k.startswith("_")},
    )
    if not b.entrances():
        raise BuildingError(f"{where}: footprint has no entrance (e.g. 'A' or 'D')")
    return b


def load_buildings(buildings_dir: Path, map_id: str | None = None) -> list[BuildingAsset]:
    """Every assets/buildings/<id>/building.json (for one map, if given)."""
    out = []
    if not buildings_dir.is_dir():
        return out
    for path in sorted(buildings_dir.glob("*/building.json")):
        b = parse_building(json.loads(path.read_text(encoding="utf-8")), path.parent)
        if map_id is None or b.map_id == map_id:
            out.append(b)
    return out
