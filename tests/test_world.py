"""Engine logic tests (movement, camera, text, parser)."""

import pytest

from game.ui.text import wrap
from game.world.camera import follow
from game.world.directions import Direction
from game.world.locations import parse_locations
from game.world.mapdata import MapError, parse_map
from game.world.movement import GridMover

# --- parser errors -----------------------------------------------------------


def test_ragged_rows_rejected():
    with pytest.raises(MapError, match="row 1"):
        parse_map("t", "#@#\n##\n", {})


def test_unknown_character_rejected():
    with pytest.raises(MapError, match="unknown character"):
        parse_map("t", "#@?\n", {})


def test_missing_spawn_rejected():
    with pytest.raises(MapError, match="no player spawn"):
        parse_map("t", "#.#\n", {})


def test_object_outside_map_rejected():
    meta = {"objects": [{"at": [5, 0], "type": "sign", "lines": ["hi"]}]}
    with pytest.raises(MapError, match="outside the map"):
        parse_map("t", "#@.\n", meta)


def test_object_needs_lines_or_location():
    meta = {"objects": [{"at": [2, 0], "type": "sign"}]}
    with pytest.raises(MapError, match="needs 'lines' or a 'location'"):
        parse_map("t", "#@.\n", meta)


def test_two_objects_on_one_tile_rejected():
    o = {"at": [2, 0], "type": "sign", "lines": ["hi"]}
    with pytest.raises(MapError, match="two objects"):
        parse_map("t", "#@.\n", {"objects": [o, dict(o)]})


def test_object_tile_overrides_map_tile_and_blocks():
    meta = {"objects": [{"at": [2, 0], "type": "sign", "tile": "statue", "lines": ["hi"]}]}
    m = parse_map("t", "#@.\n", meta)
    assert m.tiles[0][2] == "statue"
    assert m.is_blocked(2, 0)


def test_area_lookup_uses_first_match():
    meta = {"areas": [{"name": "A", "rect": [0, 0, 2, 1]},
                      {"name": "B", "rect": [0, 0, 3, 1]}]}
    m = parse_map("t", "@..\n", meta)
    assert m.area_at(1, 0).name == "A"
    assert m.area_at(2, 0).name == "B"


def test_bad_location_kind_rejected():
    with pytest.raises(ValueError, match="unknown kind"):
        parse_locations({"x": {"name": "X", "kind": "castle", "blurb": "b"}})


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
    assert follow(50, 50, 256, 192, 128, 96) == (-64, -48)


# --- text ----------------------------------------------------------------------

def test_wrap_respects_width_and_newlines():
    assert wrap("hello there world\nnew", 11) == ["hello there", "world", "new"]
    assert all(len(line) <= 11 for line in wrap("a " * 50, 11))


def test_wrap_splits_long_words():
    assert wrap("abcdefghij", 4) == ["abcd", "efgh", "ij"]


# --- auto-greeting NPCs --------------------------------------------------------

def test_auto_npc_greets_once_from_any_side():
    meta = {"objects": [{"at": [2, 0], "type": "npc", "name": "OL", "lines": ["hi"], "auto": True},
                        {"at": [0, 0], "type": "npc", "name": "Quiet", "lines": ["..."]}]}
    m = parse_map("t", ".@...\n", meta)
    found = m.auto_npc_next_to(1, 0, set())
    assert found is not None
    obj, direction = found
    assert obj.name == "OL" and direction == Direction.RIGHT
    assert m.auto_npc_next_to(1, 0, {(2, 0)}) is None  # already greeted
    assert m.auto_npc_next_to(4, 0, set()) is None      # not adjacent


# --- text box pagination ---------------------------------------------------------

def test_dialogue_pages_fit_the_text_box():
    from game.scenes.dialogue import paginate
    from game.ui.textbox import LINES, MAX_CHARS
    pages = paginate(["word " * 60, "short"])
    assert all(len(p) <= LINES for p in pages)
    assert all(len(line) <= MAX_CHARS for p in pages for line in p)
    assert pages[-1] == ["short"]  # each source line starts a new page
