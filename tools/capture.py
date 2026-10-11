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
from game.scenes.dialogue import paginate  # noqa: E402
from game.systems.bike import TAKE_LINES  # noqa: E402
from game.systems.missions import MissionBook, load_missions  # noqa: E402
from game.systems.progress import Progress  # noqa: E402
from game.scenes.overworld import add_mission_people  # noqa: E402
from game.world.locations import load_locations  # noqa: E402
from game.world.mapdata import MapObject  # noqa: E402
from game.systems.input import Action, ScriptedInput  # noqa: E402
from game.world.directions import Direction  # noqa: E402
from game.world.mapdata import load_map  # noqa: E402

OUT = ROOT / "build" / "screenshots"
FRAMES_PER_STEP = config.TILE // config.WALK_SPEED
BIKE_FRAMES_PER_STEP = config.TILE // config.BIKE_SPEED
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


def pages(n: int) -> list[set[Action]]:
    """Let each of n text-box pages finish typing, then press Z."""
    out = []
    for _ in range(n):
        out += wait(75) + tap(Action.CONFIRM)
    return out


def drain(reactions) -> list[set[Action]]:
    """Click through the mission messages (decisions/0031) that a step of the
    script sets off, page by page, as the game shows them."""
    out = []
    for r in reactions:
        pages = len(paginate(r.lines)) if r.lines else 0
        pages += len(paginate([f"You got: {x}!" for x in r.rewards])) if r.rewards else 0
        for _ in range(pages):
            out += wait(75) + tap(Action.CONFIRM)
    return out + wait(4)


class Walker:
    """Plans grid routes with BFS and turns them into held-direction input."""

    def __init__(self, game_map):
        self.m = game_map
        self.pos = game_map.spawn

    def to_face(self, tx: int, ty: int, frames: int = FRAMES_PER_STEP) -> list[set[Action]]:
        """Walk (or ride: pass the bike's frames per step) next to object
        (tx, ty) and face it."""
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
            out += [{DIR_ACTION[d]}] * frames
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

    # the game's missions, run alongside the script so it knows what pops up
    progress = Progress()
    book = MissionBook(load_missions(config.CONTENT_DIR / "missions"), progress,
                       {k: v.name for k, v in load_locations(config.LOCATIONS_FILE).items()},
                       has_bike=lambda: progress.has_bike)
    add_mission_people(m, book)
    book.auto_start()
    fountain = next((o.x, o.y) for o in m.objects if o.location == "cunniffe_fountain")
    greeter = next(o for o in m.objects if o.type == "npc" and o.auto)
    gate_steps = abs(m.spawn[1] - (greeter.y + 1))  # walk up through the gate
    gate = next(o for o in m.objects if o.type == "checkpoint")  # Bert's ID check

    segments = [
        ("01_title", wait(20)),
        # opening sequence (content/intro.json): train 270f, station 210f, street 450f
        ("02_train", tap(Action.CONFIRM) + wait(88)),
        ("03_train_arrives", wait(177)),
        ("04_station_doors", wait(60)),
        ("05_station_walk_out", wait(80)),
        ("06_street_ram_van", wait(230)),
        ("07_street_at_gate", wait(250)),
        ("08_controls", wait(60)),
        ("09_webster_ave_start", tap(Action.CONFIRM) + wait(20)),
        # Bert's ID check: walking into the closed gate starts it
        ("10_bert_asks_for_id", [{Action.UP}] + wait(150)),
        ("11_id_choose", read(len(paginate(gate.lines)))),
        ("12_id_phone_beep", tap(Action.CONFIRM) + wait(38)),      # phone is the first choice
        ("13_access_granted", wait(20)),
        ("14_bert_all_set", tap(Action.CONFIRM) + wait(150)),
        # through the gate: welcome banner, then the Orientation Leader
        ("15_through_gate_welcome", read(len(paginate(gate.after_lines)))
         + [{Action.UP}] * (FRAMES_PER_STEP * gate_steps) + wait(120)),
        ("16_route_to_parade", tap(Action.CONFIRM) + wait(10) + tap(Action.CONFIRM) + wait(150)),
    ]
    # close the rest of the welcome, then explore from just inside the gate
    walk.pos = (greeter.x, greeter.y + 1)
    segments += [
        # Walsh Library's north entrance, seen from the walkway (D-0019)
        ("17_walsh_library_front", read(len(paginate(greeter.lines)) - 1)
         + drain(book.talk(greeter.name)) + walk.to_face(*door["walsh_library"]) + wait(4)),
        ("17b_walsh_library_card", tap(Action.CONFIRM) + wait(5)),
    ]
    # the bike rack outside the library (decisions/0030): borrow a bike, ride, hop off
    rack = next(o for o in m.objects if o.type == "bike_rack")
    segments += [
        ("17ba_bike_rack", tap(Action.CONFIRM) + drain(book.read("walsh_library"))
         + walk.to_face(rack.x, rack.y)
         + tap(Action.CONFIRM) + wait(120)),
        ("17bb_riding", read(len(paginate(TAKE_LINES)) - 1) + tap(Action.CONFIRM) + wait(4)
         + walk.to_face(*door["larkin_hall"], frames=BIKE_FRAMES_PER_STEP) + wait(4)),
        ("17bc_hop_off", wait(BIKE_FRAMES_PER_STEP) + tap(Action.CANCEL) + wait(6)),
        ("17c_campbell_entrance", walk.to_face(*door["campbell_hall"]) + wait(4)),
        ("17cb_campbell_card", tap(Action.CONFIRM) + wait(5)),
        # Dealy Hall's columned entrance faces west, toward Cunniffe House
        ("17cc_dealy_portico", tap(Action.CONFIRM) + drain(book.read("campbell_hall"))
         + walk.to_face(*door["dealy_hall"]) + wait(4)),
        ("17cd_dealy_card", tap(Action.CONFIRM) + wait(5)),
        # the fountain quad (decisions/0022): the fountain, then Hughes Hall
        ("17ce_fountain_plaza", tap(Action.CONFIRM) + drain(book.read("dealy_hall"))
         + walk.to_face(*fountain) + wait(4)),
        ("17cf_fountain_card", tap(Action.CONFIRM) + wait(5)),
        ("17cg_hughes_card", tap(Action.CONFIRM) + drain(book.read("cunniffe_fountain"))
         + walk.to_face(*door["hughes_hall"]) + tap(Action.CONFIRM) + wait(5)),
        ("17d_keating_card", tap(Action.CONFIRM) + drain(book.read("hughes_hall"))
         + walk.to_face(*door["keating_hall"]) + tap(Action.CONFIRM) + wait(5)),
        ("18_ohare_card", tap(Action.CONFIRM) + drain(book.read("keating_hall"))
         + walk.to_face(*door["ohare_hall"]) + tap(Action.CONFIRM) + wait(5)),
        # campus map (decisions/0017): open, pick a place, open its card
        ("19_campus_map", tap(Action.CONFIRM) + drain(book.read("ohare_hall")) + tap(Action.MAP) + wait(10)),
        ("20_map_pin", tap(Action.LEFT) + wait(2) + tap(Action.LEFT) + wait(6)),
        ("21_map_card", tap(Action.CONFIRM) + wait(5)),
    ]
    # a mission (decisions/0031): Lost and Found, from the "!" to the stamp
    lost = book.missions["lost_and_found"]
    giver = lost.giver
    item = next(st for st in lost.steps if st["do"] == "find")
    segments += [
        ("22_mission_giver", tap(Action.CONFIRM) + wait(4) + tap(Action.MAP) + wait(4)
         + walk.to_face(*giver["at"]) + wait(4)),
        ("23_mission_offer", tap(Action.CONFIRM) + pages(len(paginate(giver["offer"]))) + wait(10)),
    ]
    accepted = book.accept("lost_and_found")
    m.add_object(MapObject(type="item", x=item["at"][0], y=item["at"][1], name=item["item"],
                           tile=item["tile"], lines=["item"]))
    segments += [
        ("24_mission_tracker", tap(Action.CONFIRM) + drain(accepted) + wait(10)),
        ("25_mission_found_item", walk.to_face(*item["at"]) + tap(Action.CONFIRM) + wait(60)),
    ]
    found = book.pickup(item["item"])
    m.remove_object(*item["at"])
    segments += [
        ("26_mission_log", wait(15) + tap(Action.CONFIRM) + drain(found[1:]) + wait(4) + tap(Action.MENU) + wait(6)),
        ("26b_mission_page", tap(Action.CONFIRM) + wait(6)),
        ("27_ram_passport", tap(Action.CANCEL) + wait(2) + tap(Action.RIGHT) + wait(6)),
        ("28_mission_map_pin", tap(Action.MENU) + wait(4) + tap(Action.MAP) + wait(12)),
    ]
    done = book.near("thebaud_hall")
    segments += [
        # arriving at Thebaud: the step's line, then the finish line, then the banner and rewards
        ("29_mission_complete", tap(Action.MAP) + wait(4) + walk.to_face(*door["thebaud_hall"])
         + pages(len(paginate(done[0].lines)) + len(paginate(done[1].lines))) + wait(20)),
        ("30_passport_stamp", pages(len(paginate([f"You got: {x}!" for x in done[1].rewards])))
         + wait(10) + tap(Action.MENU) + wait(4) + tap(Action.RIGHT) + wait(6)),
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
