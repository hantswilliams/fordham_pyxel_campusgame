"""Bert's ID check at the Webster Ave gate."""

from game.systems.id_check import BEEP_AT, CHOICES, TAP_FRAMES, IdCheck
from game.world.mapdata import parse_map


def test_choose_wraps_between_card_and_phone():
    c = IdCheck()
    c.move(1)
    assert CHOICES[c.choice].startswith("Phone")
    c.move(1)
    assert CHOICES[c.choice].startswith("Fordham ID")


def test_tap_turns_the_light_green_then_grants():
    c = IdCheck()
    c.confirm()
    assert c.state == "tapping" and not c.light_green
    for _ in range(BEEP_AT):
        c.tick()
    assert c.light_green
    for _ in range(TAP_FRAMES):
        c.tick()
    assert c.state == "granted"
    c.confirm()
    assert c.state == "done"


def test_checkpoint_blocks_until_opened():
    meta = {"objects": [{"at": [1, 0], "type": "checkpoint", "name": "Bert", "tile": "reader_gate",
                         "lines": ["ID please"], "after_lines": ["Thanks"]}]}
    m = parse_map("t", "@..\n", meta)
    assert m.is_blocked(1, 0) and m.tiles[0][1] == "reader_gate"
    assert m.open_checkpoint(1, 0)
    assert not m.is_blocked(1, 0) and m.tiles[0][1] == "path"
    assert not m.open_checkpoint(1, 0)  # already open
