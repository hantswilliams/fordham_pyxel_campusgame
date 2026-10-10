"""In-game campus map (decisions/0017): colours, pins, pin navigation."""

from game import config
from game.config import Col
from game.world.directions import Direction
from game.world.locations import load_locations
from game.world.mapdata import load_map
from game.world.minimap import (BUILDING_PARTS, ROOF_COLORS, TILE_COLORS, Pin, build_pins,
                                next_pin, tile_colors)
from game.world.tiles import TILES

M = load_map(config.START_MAP, config.MAPS_DIR)
LOCATIONS = load_locations(config.LOCATIONS_FILE)


def test_every_tile_has_a_map_colour():
    missing = set(TILES) - set(TILE_COLORS) - BUILDING_PARTS
    assert not missing, f"add these tiles to TILE_COLORS: {sorted(missing)}"


def test_building_walls_take_their_roof_colour():
    colors = tile_colors(M)
    for obj in M.objects:
        if obj.type == "door":
            assert colors[obj.y][obj.x] in ROOF_COLORS.values(), obj.location


def test_admission_is_maroon_on_the_map():
    colors = tile_colors(M)
    door = next(o for o in M.objects if o.location == "admissions")
    assert colors[door.y][door.x] == Col.MAROON


def test_pins_cover_gates_shuttles_and_guide_places():
    pins = build_pins(M, LOCATIONS)
    ids = [p.location for p in pins]
    for gate in ("webster_gate", "main_entrance", "bathgate_gate", "clavius_gate"):
        assert gate in ids
    stops = sum(1 for o in M.objects if o.location == "ram_van")
    assert ids.count("ram_van") == stops >= 6  # every stop gets its own pin
    for loc in LOCATIONS.values():
        if loc.guide:
            assert loc.id in ids, f"Campus Guide place {loc.id} has no pin"
    assert len(ids) == len(set(ids)) + ids.count("ram_van") - 1  # no other duplicates


def test_next_pin_prefers_the_pressed_direction():
    pins = [Pin("A", 10, 10, "building", "a"), Pin("B", 20, 11, "building", "b"),
            Pin("C", 12, 2, "building", "c"), Pin("D", 4, 10, "building", "d")]
    assert pins[next_pin(pins, 10, 10, Direction.RIGHT)].name == "B"
    assert pins[next_pin(pins, 10, 10, Direction.UP)].name == "C"
    assert pins[next_pin(pins, 10, 10, Direction.LEFT)].name == "D"
    assert next_pin(pins, 10, 10, Direction.DOWN) is None


def test_trimmed_map_rows_are_off_campus():
    from game.scenes.campus_map import SKIP_ROWS
    for y in range(SKIP_ROWS):
        assert all(t == "offcampus" for t in M.tiles[y]), f"row {y} has campus on it"
