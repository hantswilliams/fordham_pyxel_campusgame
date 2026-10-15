"""Missions (decisions/0031): every mission file is valid, and the engine
runs the step types, timers, rewards and the checklist."""

import json

from game import config
from game.systems.missions import FPS, MissionBook, load_missions, validate, _mission_from_dict
from game.systems.progress import Progress, SaveFile
from game.world.locations import load_locations
from game.world.mapdata import load_map

MISSIONS_DIR = config.CONTENT_DIR / "missions"


def _world():
    m = load_map(config.START_MAP, config.MAPS_DIR)
    locs = load_locations(config.LOCATIONS_FILE)
    npcs = {o.name for o in m.objects if o.type == "npc"}
    taken = {(o.x, o.y) for o in m.objects}

    def is_free(x, y):
        return m.in_bounds(x, y) and not m.is_blocked(x, y) and (x, y) not in taken
    return m, locs, npcs, is_free


def test_every_mission_file_is_valid():
    missions = load_missions(MISSIONS_DIR)
    assert missions, "no missions found"
    _, locs, npcs, is_free = _world()
    assert validate(missions, locs, npcs, is_free) == []


def test_the_checklist_is_the_one_required_mission_and_comes_first():
    missions = load_missions(MISSIONS_DIR)
    required = [m for m in missions if not m.optional]
    assert [m.id for m in required] == ["first_week"]
    assert missions[0].id == "first_week" and missions[0].any_order


def test_givers_and_items_are_reachable():
    from tests.test_content import reachable_from_spawn
    m, _, _, _ = _world()
    seen = reachable_from_spawn(m)
    for mission in load_missions(MISSIONS_DIR):
        spots = [tuple(mission.giver["at"])] if mission.giver else []
        spots += [tuple(s["at"]) for s in mission.steps if s["do"] == "find"]
        for spot in spots:
            assert spot in seen, f"{mission.id}: {spot} can't be reached"


def test_template_is_skipped_but_parses():
    d = json.loads((MISSIONS_DIR / "_TEMPLATE.json").read_text())
    assert _mission_from_dict(d, "_TEMPLATE.json").steps
    assert "my_mission" not in {m.id for m in load_missions(MISSIONS_DIR)}


def _book(progress=None, bike=False):
    p = progress or Progress()
    return MissionBook(load_missions(MISSIONS_DIR), p, has_bike=lambda: bike), p


def test_lost_and_found_from_offer_to_stamp():
    book, p = _book()
    assert book.npc_marker("Worried Student") == "!"
    offer = book.talk("Worried Student")
    assert offer[0].offer and offer[0].offer.id == "lost_and_found"
    book.accept("lost_and_found")
    assert book.items() == [(47, 31, "item_card_road", "lost_id")]
    assert "lost ID" in book.tracker()
    book.pickup("lost_id")
    assert book.items() == []
    done = book.near("thebaud_hall")
    assert done[-1].completed and done[-1].completed.id == "lost_and_found"
    assert "lost_and_found" in p.stamps and "wellness" in p.badges
    assert book.npc_marker("Worried Student") is None


def test_bike_courier_needs_a_bike_and_runs_against_the_clock():
    book, p = _book(bike=False)
    assert not book.talk("Mail Room Staffer")[0].offer          # "borrow a bike first"
    book, p = _book(bike=True)
    book.accept("bike_courier")
    book.pickup("package")
    assert p.mission("bike_courier").timer == 15 * FPS
    fail = book.tick(15 * FPS)
    assert "Out of time" in fail[0].lines[0]
    assert book.items(), "the package goes back to McShane"
    book.pickup("package")
    book.tick(5 * FPS)
    done = book.near("ohare_hall")
    assert done[-1].completed and "maroon_bike" in p.unlocks


def test_game_day_collect_then_two_questions():
    book, p = _book()
    book.accept("game_day")
    book.read("victory_bell")
    assert "(1/3)" in book.tracker()
    book.read("moglia_stadium"); book.read("rose_hill_gym")
    q = [r for r in book.talk("Athletics Staffer") if r.question]
    assert q and q[0].question["question"].startswith("Since what year")
    wrong = book.answer("game_day", q[0].question["step"], 1)
    assert "Not quite" in wrong[0].lines[0]
    right = book.answer("game_day", q[0].question["step"], 0)
    nxt = [r for r in right if r.question]
    assert nxt, "the second question follows straight away"
    done = book.answer("game_day", nxt[0].question["step"], 1)
    assert done[-1].completed and "game_day" in p.stamps


def test_checklist_starts_itself_and_takes_any_order():
    book, p = _book()
    book.auto_start()
    assert p.mission("first_week").status == "active"
    book.read("thebaud_hall")
    book.read("hughes_hall"); book.read("dealy_hall")
    book.talk("Orientation Leader")
    assert {"academics", "community"} <= p.badges
    for loc in ("mcshane_center", "walsh_library", "ohare_hall", "campus_shuttle"):
        book.read(loc)
    done = book.read("webster_gate")
    assert done[-1].completed and done[-1].completed.id == "first_week"


def test_progress_survives_a_save_and_load(tmp_path):
    book, p = _book()
    book.accept("game_day"); book.read("victory_bell")
    p.position, p.has_bike, p.visited = (10, 20), True, {"walsh_library"}
    save = SaveFile(tmp_path / "save.json")
    save.save(p)
    q = save.load()
    assert q.to_dict() == p.to_dict()
    book2 = MissionBook(load_missions(MISSIONS_DIR), q)
    assert "(1/3)" in book2.tracker()


def test_a_damaged_save_starts_fresh(tmp_path):
    path = tmp_path / "save.json"
    path.write_text("{not json")
    assert SaveFile(path).load().to_dict() == Progress().to_dict()


def test_mission_bar_is_off_unless_pinned():
    from game.systems.progress import Progress
    assert Progress().show_tracker is False
    assert Progress.from_dict({"show_tracker": True}).show_tracker is False   # old saves: clean screen
    p = Progress(show_tracker=True)
    assert Progress.from_dict(p.to_dict()).show_tracker is True
