"""The scenery outside the fence (decisions/0033) covers only off-campus
cells, matches the map's size, and its street signs sit off campus."""

import json

import pytest

from game import config

PIL = pytest.importorskip("PIL.Image")
DIR = config.ROOT / "assets" / "surroundings"


def grid():
    return (config.MAPS_DIR / "rose_hill.txt").read_text().splitlines()


def test_scenery_is_the_size_of_the_map_and_clear_on_campus():
    g = grid()
    im = PIL.open(DIR / "rose_hill.png").convert("RGBA")
    assert im.size == (len(g[0]) * config.TILE, len(g) * config.TILE)
    px = im.load()
    for y, row in enumerate(g):
        for x, ch in enumerate(row):
            cx, cy = x * config.TILE + 8, y * config.TILE + 8
            if ch == "#":
                assert px[cx, cy][3] == 255, f"off-campus cell {(x, y)} has no scenery"
            else:
                assert px[cx, cy][3] == 0, f"scenery drawn over campus cell {(x, y)}"


def test_street_signs_are_off_campus():
    g = grid()
    for lab in json.loads((DIR / "rose_hill_labels.json").read_text()):
        x, y = int(lab["at"][0]), int(lab["at"][1])
        assert g[y][x] == "#", f"{lab['text']} sign at {(x, y)} is on campus"
