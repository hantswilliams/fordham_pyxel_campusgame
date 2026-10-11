"""What lies outside the campus fence (decisions/0033): streets, the
Botanical Garden and the neighbourhood, painted over the off-campus cells.

assets/surroundings/<map id>.png is a picture the size of the map, clear
everywhere on campus (made by assets/surroundings/draw_surroundings.py).
The off-campus cells stay blocked; this is scenery only.
assets/surroundings/<map id>_labels.json names the streets and places on
green street signs.
"""

import json

import pyxel

from game.config import ROOT, Col

SURROUNDINGS_DIR = ROOT / "assets" / "surroundings"
SIGN_H = 9

_cache: dict[str, "pyxel.Image | None"] = {}


def image(map_id: str) -> "pyxel.Image | None":
    if map_id not in _cache:
        path = SURROUNDINGS_DIR / f"{map_id}.png"
        _cache[map_id] = pyxel.Image.from_image(str(path), include_colors=False) if path.exists() else None
    return _cache[map_id]


def labels(map_id: str) -> list[dict]:
    path = SURROUNDINGS_DIR / f"{map_id}_labels.json"
    return json.loads(path.read_text()) if path.exists() else []


def draw(map_id: str, x: int, y: int, w: int, h: int, target=None) -> None:
    """Copy the part of the scenery at map pixels (x, y, w, h) to the same
    place on `target` (the screen, with the camera set, or a map image)."""
    img = image(map_id)
    if img is not None:
        (target or pyxel).blt(x, y, img, x, y, w, h, Col.BLACK)


def draw_labels(target, map_id: str) -> None:
    """Street-name signs, NYC style: white letters on green."""
    for lab in labels(map_id):
        text = lab["text"]
        w = len(text) * 4 + 5
        cx, cy = round(lab["at"][0] * 16), round(lab["at"][1] * 16)
        x0, y0 = cx - w // 2, cy - SIGN_H // 2
        target.rect(x0, y0, w, SIGN_H, Col.GREEN)
        target.rectb(x0, y0, w, SIGN_H, Col.WHITE)
        target.text(x0 + 3, y0 + 2, text, Col.WHITE)
