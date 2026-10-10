"""Campus locations (buildings, landmarks, transit) from content/locations.json.

These feed the building cards now and the Campus Guide in M3
(decisions/0006, 0014). Pure Python, no Pyxel.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

KINDS = {
    "academic": "ACADEMIC BUILDING",
    "residence": "RESIDENCE HALL",
    "campus": "CAMPUS BUILDING",
    "athletics": "ATHLETICS",
    "landmark": "LANDMARK",
    "transit": "GETTING AROUND",
}


@dataclass
class Location:
    id: str
    name: str
    kind: str
    blurb: str
    inside: list[str] = field(default_factory=list)
    url: str = ""
    guide: bool = False  # appears in the Campus Guide (D-0014)
    short_name: str = ""  # on the building's name plaque (D-0021)
    real_entrance: str = ""  # where the entrance really is, if the map differs (D-0021)

    @property
    def kind_label(self) -> str:
        return KINDS[self.kind]


def parse_locations(data: dict) -> dict[str, Location]:
    out = {}
    for loc_id, d in data.items():
        if loc_id.startswith("_"):
            continue  # comments / metadata
        kind = d.get("kind")
        if kind not in KINDS:
            raise ValueError(f"location {loc_id!r}: unknown kind {kind!r}")
        if not d.get("name") or not d.get("blurb"):
            raise ValueError(f"location {loc_id!r}: needs 'name' and 'blurb'")
        out[loc_id] = Location(
            id=loc_id,
            name=d["name"],
            kind=kind,
            blurb=d["blurb"],
            inside=list(d.get("inside", [])),
            url=d.get("url", ""),
            guide=bool(d.get("guide", False)),
            short_name=d.get("short_name", ""),
            real_entrance=d.get("real_entrance", ""),
        )
    return out


def load_locations(path: Path) -> dict[str, Location]:
    return parse_locations(json.loads(path.read_text(encoding="utf-8")))
