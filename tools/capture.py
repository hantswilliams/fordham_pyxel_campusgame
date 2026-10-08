"""Run the game headless with scripted input and save screenshots.

    uv run python tools/capture.py            # writes build/screenshots/*.png

Useful for checking art/layout changes without playing, and for sharing
progress. Each shot is (name, frames_to_run, actions_held).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pyxel  # noqa: E402

from game.app import App  # noqa: E402
from game.systems.input import Action, ScriptedInput  # noqa: E402

OUT = ROOT / "build" / "screenshots"


def hold(action: Action | None, frames: int) -> list[set[Action]]:
    return [{action} if action else set() for _ in range(frames)]


def tap(action: Action) -> list[set[Action]]:
    return [{action}, set()]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # Script: title -> start -> walk north to the Orientation Leader and talk.
    segments = [
        ("01_title", hold(None, 20)),
        ("02_arrival", tap(Action.CONFIRM) + hold(None, 30)),
        ("03_walk_north", hold(Action.UP, 8 * 14) + hold(None, 4)),
        # step right once, then press right again (blocked, so just turns)
        ("04_talk", hold(Action.RIGHT, 8) + hold(None, 2) + tap(Action.RIGHT)
         + tap(Action.CONFIRM) + hold(None, 60)),
        ("05_next_line", tap(Action.CONFIRM) + hold(None, 60)),
        # finish the conversation, step back onto the path, walk to Keating Hall
        ("06_keating_door", tap(Action.CONFIRM) + hold(None, 60) + tap(Action.CONFIRM)
         + hold(Action.LEFT, 8) + hold(Action.UP, 8 * 6) + tap(Action.CONFIRM)
         + hold(None, 60)),
    ]
    script: list[set[Action]] = []
    shot_at: dict[int, str] = {}
    for name, frames in segments:
        script += frames
        shot_at[len(script)] = name

    app = App(input_source=ScriptedInput(script), headless=True)
    for frame in range(1, len(script) + 1):
        app.update()
        app.draw()
        if frame in shot_at:
            path = OUT / f"{shot_at[frame]}.png"
            pyxel.screen.save(str(path), 3)
            print("saved", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
