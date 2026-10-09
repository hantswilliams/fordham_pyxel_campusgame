"""Content checks: run these after editing anything in content/.

They catch the mistakes that are easy to make when hand-editing maps and
JSON: unreachable NPCs, doors with no building card, typos in location ids.
"""

import pytest

from game import config
from game.scenes.card import MAX_CHARS, card_lines
from game.world.directions import Direction
from game.world.locations import load_locations
from game.world.mapdata import load_map

MAP_IDS = sorted(p.stem for p in config.MAPS_DIR.glob("*.txt"))
LOCATIONS = load_locations(config.LOCATIONS_FILE)


@pytest.fixture(scope="module", params=MAP_IDS)
def game_map(request):
    return load_map(request.param, config.MAPS_DIR)


def reachable_from_spawn(m) -> set[tuple[int, int]]:
    """Tiles the player can reach, assuming every guarded gate gets opened.
    Works on a fresh copy so the shared fixture map isn't changed."""
    m = load_map(m.id, config.MAPS_DIR)
    for gate in m.checkpoints():
        m.open_checkpoint(gate.x, gate.y)
    seen = {m.spawn}
    frontier = [m.spawn]
    while frontier:
        x, y = frontier.pop()
        for d in Direction:
            n = (x + d.dx, y + d.dy)
            if n not in seen and not m.is_blocked(*n):
                seen.add(n)
                frontier.append(n)
    return seen


def test_start_map_exists():
    assert config.START_MAP in MAP_IDS


def test_spawn_is_walkable(game_map):
    assert not game_map.is_blocked(*game_map.spawn)


def test_start_greeter_is_through_the_gate():
    """D-0016 Part 2: start outside the Webster Ave gate; an Orientation
    Leader greets you automatically just inside."""
    m = load_map(config.START_MAP, config.MAPS_DIR)
    sx, sy = m.spawn
    ahead = (sx + m.spawn_facing.dx, sy + m.spawn_facing.dy)
    gate = m.object_at(*ahead)
    assert gate and gate.type == "checkpoint", "Bert's ID-check gate should be right in front of the start"
    assert any(o.type == "npc" and o.name == gate.name for o in m.objects), "the guard NPC must exist"
    greeters = [o for o in m.objects if o.type == "npc" and o.auto]
    assert greeters, "expected an auto-greeting Orientation Leader"
    seen = reachable_from_spawn(m)
    for g in greeters:
        assert any((g.x + dx, g.y + dy) in seen for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))


def test_map_edges_are_solid(game_map):
    """Players must never walk off the edge of a map."""
    m = game_map
    for x in range(m.width):
        assert m.is_blocked(x, 0) and m.is_blocked(x, m.height - 1)
    for y in range(m.height):
        assert m.is_blocked(0, y) and m.is_blocked(m.width - 1, y)


def test_every_object_is_reachable(game_map):
    """Each sign/NPC/door needs a walkable neighbour reachable from spawn."""
    seen = reachable_from_spawn(game_map)
    for obj in game_map.objects:
        neighbours = {(obj.x + d.dx, obj.y + d.dy) for d in Direction}
        label = obj.location or obj.name or obj.type
        assert neighbours & seen, f"{label} at {(obj.x, obj.y)} can't be reached"


def test_every_door_tile_has_a_door_object(game_map):
    m = game_map
    for y, row in enumerate(m.tiles):
        for x, name in enumerate(row):
            if name == "door":
                obj = m.object_at(x, y)
                assert obj and obj.type == "door", f"door tile at {(x, y)} has no door object"


def test_door_objects_sit_on_door_tiles(game_map):
    for obj in game_map.objects:
        if obj.type == "door":
            assert game_map.tiles[obj.y][obj.x] == "door", f"{obj.location} door at {(obj.x, obj.y)}"


def test_object_locations_exist(game_map):
    for obj in game_map.objects:
        if obj.location:
            assert obj.location in LOCATIONS, f"unknown location {obj.location!r} at {(obj.x, obj.y)}"


def test_checkpoints_have_guard_lines(game_map):
    for gate in game_map.checkpoints():
        assert gate.name and gate.lines and gate.after_lines, f"checkpoint at {(gate.x, gate.y)}"


def test_npcs_have_dialogue(game_map):
    for obj in game_map.objects:
        if obj.type == "npc":
            assert obj.lines and obj.name, f"NPC at {(obj.x, obj.y)}"


def test_areas_fit_and_spawn_has_one(game_map):
    m = game_map
    for a in m.areas:
        assert a.x >= 0 and a.y >= 0 and a.x + a.w <= m.width and a.y + a.h <= m.height, a.name
    assert m.area_at(*m.spawn) is not None


def test_every_location_is_placed_somewhere():
    """A location nobody can visit is probably a typo or a forgotten object."""
    used = set()
    for map_id in MAP_IDS:
        used |= {o.location for o in load_map(map_id, config.MAPS_DIR).objects if o.location}
    unused = set(LOCATIONS) - used
    assert not unused, f"locations not placed on any map: {sorted(unused)}"


@pytest.mark.parametrize("loc_id", sorted(LOCATIONS))
def test_building_card_fits(loc_id):
    lines = card_lines(LOCATIONS[loc_id])
    assert all(len(s) <= MAX_CHARS for s, _ in lines)
    assert len(lines) <= 16, "card text is very long; trim the blurb"
