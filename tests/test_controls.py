"""Button names that follow the device (decisions/0043)."""

import json
import re

import pyxel

from game import config
from game.systems import controls
from game.systems.input import BINDINGS, Action
from game.systems.intro_timeline import load_intro, parse_intro
from game.systems.missions import load_missions


def test_keyboard_names_by_default():
    assert not controls.TOUCH
    assert controls.fmt("Press {confirm}, {back} to skip, {map} map, {menu} missions") == \
        "Press Z, X to skip, M map, TAB missions"


def test_touch_names():
    t = controls.TOUCH_NAMES
    assert controls.fmt("{confirm}: NEXT  {back}: SKIP", t) == "A: NEXT  B: SKIP"
    assert controls.fmt("{move}: PICK A PLACE", t) == "D-PAD: PICK A PLACE"


def test_how_to_play_on_each_device():
    keys = [k for k, _ in load_intro(config.INTRO_FILE).controls_rows]
    assert keys == ["ARROWS/WASD", "Z/SPACE/ENTER", "X", "M", "TAB"]
    raw = config.INTRO_FILE.read_text(encoding="utf-8")
    touch = [k for k, _ in parse_intro(json.loads(controls.fmt(raw, controls.TOUCH_NAMES))).controls_rows]
    assert touch == ["D-PAD", "A", "B", "Y", "X"]


def test_no_placeholder_is_left_unfilled():
    texts = [json.dumps(load_intro(config.INTRO_FILE).__dict__, default=str)]
    texts += [json.dumps(m.__dict__, default=str) for m in load_missions(config.CONTENT_DIR / "missions")]
    for t in texts:
        assert not re.search(r"\{(confirm|back|map|menu|move)[a-z_]*\}", t)


def test_the_big_touch_buttons_open_missions_and_the_map():
    assert pyxel.GAMEPAD1_BUTTON_X in BINDINGS[Action.MENU]        # left button
    assert pyxel.GAMEPAD1_BUTTON_Y in BINDINGS[Action.MAP]         # top button
    assert pyxel.GAMEPAD1_BUTTON_START in BINDINGS[Action.MENU]
    assert pyxel.GAMEPAD1_BUTTON_BACK in BINDINGS[Action.MAP]
