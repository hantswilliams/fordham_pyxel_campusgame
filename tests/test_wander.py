"""People who stroll about (decisions/0040)."""

from game import config
from game.world.mapdata import load_map
from game.world.wander import AVOID, Wanderers

TILE = config.TILE


def run(frames=6000, player=(7, 71)):
    m = load_map(config.START_MAP, config.MAPS_DIR)
    ws = Wanderers(m, TILE)
    seen = {id(w): set() for w in ws.by_obj.values()}
    for _ in range(frames):
        ws.update({player})
        for w in ws.by_obj.values():
            seen[id(w)].add((w.obj.x, w.obj.y))
            assert m.object_at(w.obj.x, w.obj.y) is w.obj         # it holds its own cell
    return m, ws, seen


def test_some_people_wander_and_the_guides_stay_put():
    m = load_map(config.START_MAP, config.MAPS_DIR)
    ws = Wanderers(m, TILE)
    names = {w.obj.name for w in ws.by_obj.values()}
    assert {"Commuter", "First-Year", "Junior"} <= names
    assert not names & {"Orientation Leader", "Bert", "Staff Member"}


def test_they_stay_near_home_on_open_ground():
    m, ws, seen = run()
    for w in ws.by_obj.values():
        cells = seen[id(w)]
        assert len(cells) > 1, f"{w.obj.name} never moved"
        hx, hy = w.home
        for x, y in cells:
            assert abs(x - hx) <= w.obj.wander and abs(y - hy) <= w.obj.wander
            assert m.tiles[y][x] not in AVOID
            above = m.object_at(x, y - 1)
            assert not (above and above.type == "door"), f"{w.obj.name} blocked a door"


def test_they_never_walk_into_the_player():
    m, ws, seen = run(player=(7, 70))                     # beside the Commuter's spot
    assert all((7, 70) not in cells for cells in seen.values())


def test_a_person_mid_step_blocks_both_cells():
    m = load_map(config.START_MAP, config.MAPS_DIR)
    ws = Wanderers(m, TILE)
    for _ in range(3000):
        ws.update(set())
        w = next((w for w in ws.by_obj.values() if w.step), None)
        if w:
            to = (w.obj.x + w.step.dx, w.obj.y + w.step.dy)
            assert m.is_blocked(w.obj.x, w.obj.y) and m.is_blocked(*to)
            assert m.object_at(*to) is w.obj                     # you can talk to it there
            return
    raise AssertionError("nobody took a step")


def test_the_same_game_plays_out_the_same_way():
    a = [(w.obj.x, w.obj.y) for w in run(2000)[1].by_obj.values()]
    b = [(w.obj.x, w.obj.y) for w in run(2000)[1].by_obj.values()]
    assert a == b
