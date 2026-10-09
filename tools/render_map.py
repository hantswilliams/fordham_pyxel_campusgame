"""Render a whole map to one PNG, for checking the layout against the real
campus map (decisions/0010) without walking around.

    uv run python tools/render_map.py            # build/map_rose_hill.png
    uv run python tools/render_map.py rose_hill 2  # map id, scale
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pyxel  # noqa: E402

from game import config  # noqa: E402
from game.gfx.placeholder_art import CHAR_IMAGE_BANK, build_all, character_uv  # noqa: E402
from game.scenes.overworld import bake_tilemap  # noqa: E402
from game.world.mapdata import load_map  # noqa: E402

TILE = config.TILE


def main() -> None:
    map_id = sys.argv[1] if len(sys.argv) > 1 else config.START_MAP
    scale = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    pyxel.init(config.SCREEN_W, config.SCREEN_H, headless=True)
    for index, rgb in config.PALETTE_OVERRIDES.items():
        pyxel.colors[index] = rgb
    build_all()

    m = load_map(map_id, config.MAPS_DIR)
    bake_tilemap(m, 0)
    img = pyxel.Image(m.width * TILE, m.height * TILE)
    img.bltm(0, 0, 0, 0, 0, m.width * TILE, m.height * TILE)
    for obj in m.objects:
        if obj.type == "npc":
            u, v = character_uv(obj.sprite, obj.facing, 0)
            img.blt(obj.x * TILE, obj.y * TILE - 2, CHAR_IMAGE_BANK, u, v, TILE, TILE, 0)
    sx, sy = m.spawn
    u, v = character_uv(0, m.spawn_facing, 0)
    img.blt(sx * TILE, sy * TILE - 2, CHAR_IMAGE_BANK, u, v, TILE, TILE, 0)

    out = ROOT / "build" / f"map_{map_id}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out), scale)
    print("saved", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
