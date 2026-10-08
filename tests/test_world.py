import json

import pytest

from game import config
from game.ui.text import wrap
from game.world.camera import follow
from game.world.directions import Direction
from game.world.mapdata import MapError, load_map, parse_map
from game.world.movement import GridMover
from game.world.tiles import LEGEND, TILES

# --- content validation: every map in content/maps must load cleanly -------

MAP_IDS = sorted(p.stem for p in config.MAPS_DIR.glob("*.txt"))


@pytest.mark.parametrize("map_id", MAP_IDS)
def test_map_loads(map_id):
    m = load_map(map_id, config.MAPS_DIR)
    assert m.width > 0 and m.height > 0
    sx, sy = m.spawn
    assert not m.is_blocked(sx, sy)


@pytest.mark.parametrize("map_id", MAP_IDS)
def test_map_edges_are_solid(map_id):
    """Players should never be able to walk off the edge of a map."""
    m = load_map(map_id, config.MAPS_DIR)
    for x in range(m.width):
        assert m.is_blocked(x, 0) and m.is_blocked(x, m.height - 1)
    for y in range(m.height):
        assert m.is_blocked(0, y) and m.is_blocked(m.width - 1, y)


@pytest.mark.parametrize("map_id", MAP_IDS)
def test_every_object_is_reachable(map_id):
    """Each sign/NPC/door must have a walkable neighbour reachable from spawn."""
    m = load_map(map_id, config.MAPS_DIR)
    seen = {m.spawn}
    frontier = [m.spawn]
    while frontier:
        x, y = frontier.pop()
        for d in Direction:
            n = (x + d.dx, y + d.dy)
            if n not in seen and not m.is_blocked(*n):
                seen.add(n)
                frontier.append(n)
    for obj in m.objects:
        neighbours = {(obj.x + d.dx, obj.y + d.dy) for d in Direction}
        assert neighbours & seen, f"{obj.type} {obj.id!r} at {(obj.x, obj.y)} is unreachable"


@pytest.mark.parametrize("map_id", MAP_IDS)
def test_object_ids_in_json_are_used(map_id):
    meta = json.loads((config.MAPS_DIR / f"{map_id}.json").read_text())
    text = (config.MAPS_DIR / f"{map_id}.txt").read_text()
    for obj_id in meta.get("objects", {}):
        assert obj_id not in LEGEND, f"object id {obj_id!r} clashes with a tile"
        assert obj_id in text, f"object {obj_id!r} is defined but not placed on the map"


def test_legend_points_at_real_tiles():
    for name in LEGEND.values():
        assert name in TILES


# --- parser errors -----------------------------------------------------------

def test_ragged_rows_rejected():
    with pytest.raises(MapError, match="row 1"):
        parse_map("t", "T@T\nTT\n", {})


def test_unknown_character_rejected():
    with pytest.raises(MapError, match="unknown character"):
        parse_map("t", "T@?\n", {})


def test_missing_spawn_rejected():
    with pytest.raises(MapError, match="no player spawn"):
        parse_map("t", "T.T\n", {})


# --- movement ------------------------------------------------------------------

def test_step_takes_tile_over_speed_frames():
    m = GridMover(1, 1, tile=16, speed=2)
    assert m.try_move(Direction.RIGHT, lambda x, y: False)
    frames = 0
    while m.moving:
        m.update()
        frames += 1
    assert frames == 8
    assert (m.tile_x, m.tile_y) == (2, 1)


def test_blocked_move_only_turns():
    m = GridMover(1, 1, tile=16, speed=2)
    assert not m.try_move(Direction.UP, lambda x, y: True)
    assert m.facing == Direction.UP
    assert not m.moving
    assert (m.tile_x, m.tile_y) == (1, 1)


def test_pixel_position_interpolates():
    m = GridMover(0, 0, tile=16, speed=4)
    m.try_move(Direction.DOWN, lambda x, y: False)
    m.update()
    assert (m.pixel_x, m.pixel_y) == (0, 4)


# --- camera --------------------------------------------------------------------

def test_camera_clamps_to_world():
    assert follow(0, 0, 256, 192, 640, 480) == (0, 0)
    assert follow(640, 480, 256, 192, 640, 480) == (640 - 256, 480 - 192)
    assert follow(320, 240, 256, 192, 640, 480) == (192, 144)


def test_camera_centres_small_world():
    cx, cy = follow(50, 50, 256, 192, 128, 96)
    assert (cx, cy) == (-64, -48)


# --- text ----------------------------------------------------------------------

def test_wrap_respects_width_and_newlines():
    lines = wrap("hello there world\nnew", 11)
    assert lines == ["hello there", "world", "new"]
    assert all(len(line) <= 11 for line in wrap("a " * 50, 11))


def test_wrap_splits_long_words():
    assert wrap("abcdefghij", 4) == ["abcd", "efgh", "ij"]
