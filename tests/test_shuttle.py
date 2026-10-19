"""The Campus Shuttle (decisions/0044): it drives a loop of the roads, stops at
the six shuttle signs, waits for people in its way, and you can ride it.

The checks that need the game running (riding, the Ram Van) start Pyxel, which
can only happen once per process, so they run in a process of their own."""

import subprocess
import sys
from pathlib import Path

from game import config
from game.world.mapdata import load_map
from game.world.shuttle import (HOLD_FRAMES, ROAD, STOP_FRAMES, Route, Shuttle, eta_text, load_data,
                                timetable)

TILE = config.TILE


def setup():
    m = load_map(config.START_MAP, config.MAPS_DIR)
    data = load_data(config.MAPS_DIR, config.START_MAP)
    return m, data, Route(m, data, TILE)


def drive(sh, frames, blockers=frozenset(), near=False):
    arrivals = []
    for _ in range(frames):
        got = sh.update(set(blockers), near)
        if got is not None:
            arrivals.append(got)
    return arrivals


def test_the_route_stays_on_open_road():
    m, data, r = setup()
    for x, y in r.cells:
        assert m.tiles[y][x] in ROAD, (x, y)
        o = m.object_at(x, y)
        assert o is None or o.type == "item", f"{o.name or o.type} stands on the route at {(x, y)}"
    for a, b in zip(r.points, r.points[1:]):
        assert r._straight(a, b), f"the straight stretch {a} -> {b} leaves the road"
    assert r.points[0] == r.points[-1]                      # a loop


def test_it_covers_the_campus_and_passes_the_main_entrance():
    m, data, r = setup()
    cells = set(r.cells)
    assert len(cells) > 300
    main = next(a for a in m.areas if a.name == "Main Entrance")
    assert any(main.contains(x, y) for x, y in cells)
    north = next(a for a in m.areas if a.name.startswith("McShane"))
    assert any(north.contains(x, y) for x, y in cells)


def test_every_shuttle_sign_is_a_stop():
    m, data, r = setup()
    signs = {(o.x, o.y) for o in m.objects if o.location == "campus_shuttle"}
    assert len(signs) == 6
    assert {s.sign for s in r.stops} == signs
    for s in r.stops:
        x, y = s.alight
        assert not m.is_blocked(x, y) and m.tiles[y][x] not in ROAD
        assert abs(x - s.at[0]) + abs(y - s.at[1]) <= 3       # you step off right by the van


def test_it_drives_the_loop_and_stops_at_every_stop_in_turn():
    m, data, r = setup()
    sh = Shuttle(r, 0)
    loop = timetable(r)[1]
    arrivals = drive(sh, loop + 10)
    assert arrivals == [1, 2, 3, 4, 5, 0]
    assert 60 * config.FPS < loop < 4 * 60 * config.FPS          # one to four minutes round


def test_it_stops_at_a_stop_for_a_few_seconds():
    m, data, r = setup()
    sh = Shuttle(r, 0)
    start = sh.d
    drive(sh, STOP_FRAMES - 1)
    assert sh.d == start and sh.stopped_at is r.stops[0]
    drive(sh, 2)
    assert sh.d != start and sh.stopped_at is None


def test_it_waits_while_you_stand_beside_it_at_a_stop():
    m, data, r = setup()
    sh = Shuttle(r, 0)
    drive(sh, STOP_FRAMES + HOLD_FRAMES - 5, near=True)
    assert sh.stopped_at is r.stops[0]                          # still there
    drive(sh, STOP_FRAMES + 10, near=True)
    assert sh.stopped_at is None                                # but not for ever


def test_it_stops_for_you_and_never_drives_into_you():
    m, data, r = setup()
    sh = Shuttle(r, 0)
    you = r.cell_at(r.stops[1].dist - 60)                    # standing in the road before Alumni Court
    for _ in range(2000):
        sh.update({you})
        assert you not in sh.cells()
    assert sh.waiting and sh.d < r.stops[1].dist
    assert sh.beep >= 0
    drive(sh, 400)                                           # you step aside: it carries on
    assert not sh.waiting


def test_it_says_beep_when_it_stops_for_you():
    m, data, r = setup()
    sh = Shuttle(r, 0)
    drive(sh, STOP_FRAMES + 5)
    ahead = next(iter(sh.ahead()))
    sh.update({ahead})
    assert sh.waiting and sh.beep > 0


def test_it_slows_down_over_crosswalks():
    m, data, r = setup()
    slow = [d for d in range(0, int(r.length), 2) if r.speed_at(d) < r.speed_at(0)]
    assert slow, "the route crosses at least one crosswalk"
    x, y = r.cell_at(slow[0])
    assert m.tiles[y][x].startswith("crosswalk")


def test_the_signs_say_when_it_is_next_due():
    m, data, r = setup()
    sh = Shuttle(r, 0)
    assert sh.eta(0) == 0                                    # it's here now
    drive(sh, STOP_FRAMES + 1)
    for stop in (1, 3, 0):
        probe = Shuttle(r, 0)
        probe.d, probe.dwell, probe.at_stop = sh.d, sh.dwell, sh.at_stop
        want = probe.eta(stop)
        frames = 0
        while True:
            frames += 1
            if probe.update(set()) == stop:
                break
        assert abs(frames - want) <= max(3, want // 200), (stop, frames, want)   # within a second or so


def test_eta_text_reads_naturally():
    assert eta_text(0) == "It's here now!"
    assert eta_text(30 * 12) == "Next shuttle: about 10 seconds."
    assert eta_text(30 * 40) == "Next shuttle: about 40 seconds."
    assert eta_text(30 * 70) == "Next shuttle: about 1 minute."
    assert eta_text(30 * 150) == "Next shuttle: about 2 minutes."


def test_the_ram_van_waits_by_the_garage_off_the_route():
    m, data, r = setup()
    x, y = data["ram_van"]["at"]
    for c in ((x, y), (x + 1, y)):
        assert not m.is_blocked(*c) and m.tiles[c[1]][c[0]] not in ROAD
        assert c not in set(r.cells)
    driver = next(o for o in m.objects if o.name == "Ram Van Driver")
    assert abs(driver.x - x) + abs(driver.y - y) <= 2
    assert any(o.location == "ram_van" for o in m.objects)       # its sign


# --- in the game -----------------------------------------------------------------------------
_app = None


def game():
    """A fresh campus to play on (Pyxel itself starts only once)."""
    global _app
    from game.app import App
    from game.scenes.overworld import OverworldScene
    from game.systems.input import ScriptedInput
    if _app is None:
        _app = App(input_source=ScriptedInput([]), headless=True, start_scene=OverworldScene)
    else:
        _app.scenes.replace(OverworldScene(_app))
    return _app, _app.scenes.top


def check_riding_takes_you_to_your_stop_and_counts_for_the_checklist():
    app, ow = game()
    ow.progress.gate_open = True
    sh = ow.shuttle
    assert sh.stopped_at is sh.route.stops[0]
    ow._board(1)                                             # to Alumni Court
    for _ in range(3000):
        ow.update()
        if ow.riding_to is None:
            break
    assert ow.riding_to is None
    p = ow.player
    assert (p.tile_x, p.tile_y) == sh.route.stops[1].alight
    st = ow.book.state(next(m for m in ow.book.active() if m.id == "first_week"))
    assert "campus_shuttle" in sum(st.collected.values(), [])


def check_skipping_ahead_gets_there_much_sooner():
    app, ow = game()
    ow._board(3)
    ow.skipping = True
    frames = 0
    while ow.riding_to is not None and frames < 2000:
        ow.update()
        frames += 1
    assert ow.riding_to is None and frames < ow.shuttle.eta(3) // 4 + 400


def check_you_cannot_walk_into_the_van():
    app, ow = game()
    for c in ow.shuttle.cells():
        assert ow._blocked(*c)
    x, y = ow.ram_van[:2]
    assert ow._blocked(x, y) and ow._blocked(x + 1, y)


def check_you_get_off_your_bike_to_board():
    app, ow = game()
    ow.bike.have = ow.bike.riding = True
    ow._board(2)
    assert not ow.bike.riding and ow.player.speed == config.WALK_SPEED


def check_the_vans_are_drawn():
    import pyxel
    from game.gfx.placeholder_art import CHAR_IMAGE_BANK, RAM_VAN, SHUTTLE_VAN, van_uv
    app, ow = game()
    img = pyxel.images[CHAR_IMAGE_BANK]
    for van in (SHUTTLE_VAN, RAM_VAN):
        u, v, w = van_uv(van, "side")
        assert any(img.pget(u + i, v + 12) != 0 for i in range(w))
    ow.draw()                                                # draws without trouble


def test_riding_in_the_game():
    root = Path(__file__).resolve().parent.parent
    run = subprocess.run([sys.executable, "-m", "tests.test_shuttle"], cwd=root,
                         capture_output=True, text=True, timeout=180)
    assert run.returncode == 0, run.stdout + run.stderr[-3000:]


if __name__ == "__main__":
    failed = 0
    for name, check in list(globals().items()):
        if name.startswith("check_"):
            try:
                check()
            except Exception as e:
                failed += 1
                import traceback
                traceback.print_exc()
                print(f"FAILED {name}: {e!r}")
    sys.exit(1 if failed else 0)
