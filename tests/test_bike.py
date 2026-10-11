"""The bike (decisions/0030): borrow it at the rack by Walsh Library, hop on
and off with X, ride twice as fast."""

from game import config
from game.systems.bike import RETURN_LINES, TAKE_LINES, Bike
from game.world.mapdata import load_map
from game.world.movement import GridMover
from game.world.directions import Direction


def test_bike_speed_is_double_and_fits_the_grid():
    assert config.BIKE_SPEED == 2 * config.WALK_SPEED
    assert config.TILE % config.BIKE_SPEED == 0     # steps still end on a tile


def test_no_bike_until_you_borrow_one():
    b = Bike()
    assert b.toggle() is None and not b.riding
    assert b.speed == config.WALK_SPEED


def test_rack_lends_a_bike_and_takes_it_back():
    b = Bike()
    assert b.use_rack() == TAKE_LINES
    assert b.have and b.riding and b.speed == config.BIKE_SPEED
    assert b.toggle() == "WALKING" and b.speed == config.WALK_SPEED
    assert b.toggle() == "ON THE BIKE" and b.speed == config.BIKE_SPEED
    assert b.use_rack() == RETURN_LINES
    assert not b.have and not b.riding and b.toggle() is None


def test_a_bike_step_takes_half_the_frames():
    walker = GridMover(0, 0, config.TILE, config.WALK_SPEED, Direction.RIGHT)
    rider = GridMover(0, 0, config.TILE, config.BIKE_SPEED, Direction.RIGHT)
    free = lambda x, y: False  # noqa: E731
    walker.try_move(Direction.RIGHT, free)
    rider.try_move(Direction.RIGHT, free)
    frames = {"walk": 0, "ride": 0}
    while walker.moving:
        walker.update(); frames["walk"] += 1
    while rider.moving:
        rider.update(); frames["ride"] += 1
    assert frames["ride"] * 2 == frames["walk"]


def test_bike_rack_by_the_library_near_the_start():
    m = load_map(config.START_MAP, config.MAPS_DIR)
    racks = [o for o in m.objects if o.type == "bike_rack"]
    assert racks, "the map needs a bike rack"
    lib = next(o for o in m.objects if o.type == "door" and o.location == "walsh_library")
    sx, sy = m.spawn
    for r in racks:
        assert abs(r.x - lib.x) + abs(r.y - lib.y) <= 10      # outside the library
        assert abs(r.x - sx) + abs(r.y - sy) <= 20            # near the start
        assert m.is_blocked(r.x, r.y)                         # you face it, not walk on it
