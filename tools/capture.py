"""Run the game headless with scripted input and save screenshots.

    uv run python tools/capture.py            # writes build/screenshots/*.png

Routes are planned automatically on the map, so the script keeps working
when the map changes. Each shot is taken at the end of its segment.
"""

import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pyxel  # noqa: E402

from game import config  # noqa: E402
from game.app import App  # noqa: E402
from game.systems.input import Action, ScriptedInput  # noqa: E402
from game.world.directions import Direction  # noqa: E402
from game.world.mapdata import load_map  # noqa: E402

OUT = ROOT / "build" / "screenshots"
FRAMES_PER_STEP = config.TILE // config.WALK_SPEED
DIR_ACTION = {Direction.UP: Action.UP, Direction.DOWN: Action.DOWN,
              Direction.LEFT: Action.LEFT, Direction.RIGHT: Action.RIGHT}


def wait(frames: int) -> list[set[Action]]:
    return [set() for _ in range(frames)]


def tap(action: Action) -> list[set[Action]]:
    return [{action}, set()]


def read(pages: int, settle: int = 120) -> list[set[Action]]:
    """Open/advance a text box `pages` times, letting each page finish."""
    out = []
    for _ in range(pages):
        out += tap(Action.CONFIRM) + wait(settle)
    return out


class Walker:
    """Plans grid routes with BFS and turns them into held-direction input."""

    def __init__(self, game_map):
        self.m = game_map
        self.pos = game_map.spawn

    def to_face(self, tx: int, ty: int) -> list[set[Action]]:
        """Walk next to object (tx, ty) and face it."""
        goals = {(tx - d.dx, ty - d.dy): d for d in Direction}
        prev = {self.pos: None}
        queue = deque([self.pos])
        end = None
        while queue:
            cur = queue.popleft()
            if cur in goals:
                end = cur
                break
            for d in Direction:
                n = (cur[0] + d.dx, cur[1] + d.dy)
                if n not in prev and not self.m.is_blocked(*n):
                    prev[n] = (cur, d)
                    queue.append(n)
        if end is None:
            raise RuntimeError(f"no route to {(tx, ty)}")
        steps = []
        cur = end
        while prev[cur] is not None:
            cur, d = prev[cur]
            steps.append(d)
        steps.reverse()
        out = []
        for d in steps:
            out += [{DIR_ACTION[d]}] * FRAMES_PER_STEP
        out += [{DIR_ACTION[goals[end]]}, set()]  # turn to face the target
        self.pos = end
        return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    m = load_map(config.START_MAP, config.MAPS_DIR)
    walk = Walker(m)
    door = {}
    for o in m.objects:
        if o.type == "door":
            door.setdefault(o.location, (o.x, o.y))

    sx, sy = m.spawn
    greeter = m.object_at(sx + m.spawn_facing.dx, sy + m.spawn_facing.dy)
    assert greeter and greeter.type == "npc", "expected an NPC in front of the spawn"

    segments = [
        ("01_title", wait(20)),
        ("02_main_entrance", tap(Action.CONFIRM) + wait(30)),
        ("03_orientation_leader", read(1)),
        # finish the conversation, then walk to Keating Hall's door
        ("04_edwards_parade_banner", read(len(greeter.lines))  # advance + close
         + walk.to_face(*door["keating_hall"])),
        ("05_keating_card", tap(Action.CONFIRM) + wait(5)),
        ("06_ohare_card", tap(Action.CONFIRM) + walk.to_face(*door["ohare_hall"])
         + tap(Action.CONFIRM) + wait(5)),
        ("07_ram_statue", tap(Action.CONFIRM) + walk.to_face(39, 42)
         + tap(Action.CONFIRM) + wait(5)),
        ("08_library", tap(Action.CONFIRM) + walk.to_face(*door["walsh_library"]) + wait(2)),
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
