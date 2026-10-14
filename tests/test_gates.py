"""A Public Safety officer and a card reader at every gate (decisions/0042)."""

from collections import deque

from game import config
from game.world.locations import load_locations
from game.world.mapdata import load_map

OPEN_GATES = {"main_entrance": [(80, 22), (81, 22)],      # the openings in the fence
              "bathgate_gate": [(40, 66), (41, 66)],
              "clavius_gate": [(79, 60), (80, 60)]}


def near(m, cells, pred, d):
    return [o for o in m.objects if pred(o)
            and min(abs(o.x - x) + abs(o.y - y) for x, y in cells) <= d]


def test_every_open_gate_has_an_officer_and_a_card_reader():
    m = load_map(config.START_MAP, config.MAPS_DIR)
    for gate, cells in OPEN_GATES.items():
        officers = near(m, cells, lambda o: o.type == "npc" and o.name == "Public Safety Officer", 3)
        readers = near(m, cells, lambda o: o.tile == "card_reader", 3)
        assert officers, f"{gate} has no officer"
        assert readers and readers[0].lines, f"{gate} has no card reader"
        assert all(o.wander == 0 for o in officers)            # they stay at their gate


def test_the_webster_gate_keeps_its_guard_and_id_check():
    m = load_map(config.START_MAP, config.MAPS_DIR)
    assert any(o.type == "npc" and o.name == "Bert" for o in m.objects)
    assert m.checkpoints()


def test_the_matteo_ricci_booth_is_staffed():
    m = load_map(config.START_MAP, config.MAPS_DIR)
    booths = [(x, y) for y, row in enumerate(m.tiles) for x, t in enumerate(row) if t == "booth"]
    for bx, by in booths:
        assert near(m, [(bx, by)], lambda o: o.type == "npc" and o.name in ("Bert", "Public Safety Officer"), 2)


def test_the_open_gates_can_still_be_walked_through():
    m = load_map(config.START_MAP, config.MAPS_DIR)
    start = m.spawn
    seen, todo = {start}, deque([start])
    for o in m.checkpoints():                       # as if you'd tapped in at Webster
        m.open_checkpoint(o.x, o.y)
    while todo:
        x, y = todo.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and not m.is_blocked(*n):
                seen.add(n)
                todo.append(n)
    for gate, cells in OPEN_GATES.items():
        assert all(c in seen for c in cells), f"can't reach the {gate} opening"


def test_gate_cards_mention_the_officer_and_the_reader():
    locs = load_locations(config.LOCATIONS_FILE)
    for gate in OPEN_GATES:
        text = locs[gate].blurb
        assert "Public Safety officer" in text and "card reader" in text, gate
