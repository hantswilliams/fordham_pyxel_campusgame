"""Map raw keys / gamepad buttons to game actions, so scenes never check
raw keys. A scripted source lets tools/tests drive the game without a keyboard."""

from enum import Enum, auto

import pyxel


class Action(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    CONFIRM = auto()
    CANCEL = auto()
    MENU = auto()


BINDINGS: dict[Action, list[int]] = {
    Action.UP: [pyxel.KEY_UP, pyxel.KEY_W, pyxel.GAMEPAD1_BUTTON_DPAD_UP],
    Action.DOWN: [pyxel.KEY_DOWN, pyxel.KEY_S, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN],
    Action.LEFT: [pyxel.KEY_LEFT, pyxel.KEY_A, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT],
    Action.RIGHT: [pyxel.KEY_RIGHT, pyxel.KEY_D, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT],
    Action.CONFIRM: [pyxel.KEY_Z, pyxel.KEY_SPACE, pyxel.KEY_RETURN,
                     pyxel.GAMEPAD1_BUTTON_A],
    Action.CANCEL: [pyxel.KEY_X, pyxel.KEY_BACKSPACE, pyxel.GAMEPAD1_BUTTON_B],
    Action.MENU: [pyxel.KEY_TAB, pyxel.KEY_M, pyxel.GAMEPAD1_BUTTON_START],
}


class PyxelInput:
    def held(self, action: Action) -> bool:
        return any(pyxel.btn(k) for k in BINDINGS[action])

    def pressed(self, action: Action) -> bool:
        return any(pyxel.btnp(k) for k in BINDINGS[action])

    def end_frame(self) -> None:
        pass


class ScriptedInput:
    """Feed a list of per-frame action sets, e.g. for automated screenshots.
    `script[i]` is the set of actions held on frame i; 'pressed' fires on the
    first frame an action appears."""

    def __init__(self, script: list[set[Action]] | None = None):
        self.script = script or []
        self.frame = 0

    def _now(self) -> set[Action]:
        return self.script[self.frame] if self.frame < len(self.script) else set()

    def _prev(self) -> set[Action]:
        if 0 < self.frame <= len(self.script):
            return self.script[self.frame - 1]
        return set()

    def held(self, action: Action) -> bool:
        return action in self._now()

    def pressed(self, action: Action) -> bool:
        return action in self._now() and action not in self._prev()

    def end_frame(self) -> None:
        self.frame += 1
