"""Copy drawn buildings' footprints into their map files (decisions/0020).

The game applies assets/buildings/<id>/building.json when it loads a map,
so this isn't needed to play. It keeps content/maps/<map>.txt carrying the
same tiles, which tools that read the bare grid rely on and the tests check.
Run it after changing a footprint:

    uv run python tools/stamp_buildings.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from game import config  # noqa: E402
from game.world.buildings import load_buildings  # noqa: E402
from game.world.tiles import LEGEND  # noqa: E402

CHAR_FOR = {name: ch for ch, name in LEGEND.items()}


def main() -> None:
    for b in load_buildings(config.BUILDINGS_DIR):
        txt = config.MAPS_DIR / f"{b.map_id}.txt"
        rows = [list(r) for r in txt.read_text(encoding="utf-8").splitlines()]
        changed = 0
        for x, y, name in b.cells():
            if rows[y][x] != CHAR_FOR[name]:
                rows[y][x] = CHAR_FOR[name]
                changed += 1
        txt.write_text("\n".join("".join(r) for r in rows) + "\n", encoding="utf-8")

        # hand-placed door objects on its entrances would clash with the
        # doors the building adds itself
        meta_path = config.MAPS_DIR / f"{b.map_id}.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        entrances = {tuple(e) for e in b.entrances()}
        objects = meta.get("objects", [])
        kept = [o for o in objects if not (o.get("type") == "door" and tuple(o["at"]) in entrances)]
        if len(kept) != len(objects):
            meta["objects"] = kept
            meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{b.id}: {changed} cells updated in {txt.name}, "
              f"{len(objects) - len(kept)} door objects removed")


if __name__ == "__main__":
    main()
