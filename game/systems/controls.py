"""What the game calls its buttons (decisions/0043).

On a touch screen the web page shows Pyxel's on-screen gamepad, so the game
names its buttons (A, B, X, Y, D-PAD) instead of keyboard keys (Z, X, M,
TAB, ARROWS). Text in the code and content files says {confirm}, {back},
{map}, {menu} or {move} where a button name goes; fmt() fills them in.

    Action          Keyboard          Touch
    confirm         Z                 A   (bottom button)
    back            X                 B   (right button)
    map             M                 Y   (top button)
    menu            TAB               X   (left button)
    move            ARROWS            D-PAD

The game tells which by asking the browser whether the pointer is coarse
(a finger), the same test Pyxel uses to decide to show its gamepad.
"""

import sys

KEYBOARD = {"confirm": "Z", "confirm_all": "Z/SPACE/ENTER", "back": "X", "map": "M",
            "menu": "TAB", "move": "ARROWS", "move_all": "ARROWS/WASD"}
TOUCH_NAMES = {"confirm": "A", "confirm_all": "A", "back": "B", "map": "Y",
               "menu": "X", "move": "D-PAD", "move_all": "D-PAD"}


def _is_touch() -> bool:
    if sys.platform != "emscripten":
        return False
    try:
        import js  # Pyodide's bridge to the browser
        return bool(js.window.matchMedia("(pointer: coarse)").matches)
    except Exception:
        return False


TOUCH = _is_touch()
NAMES = TOUCH_NAMES if TOUCH else KEYBOARD


def key(action: str) -> str:
    """The button name for an action ("confirm", "back", "map", "menu", "move")."""
    return NAMES[action]


def fmt(text: str, names: dict | None = None) -> str:
    """Fill in {confirm}, {back}, {map}, {menu}, {move} with button names."""
    for k, v in (names or NAMES).items():
        text = text.replace("{" + k + "}", v)
    return text
