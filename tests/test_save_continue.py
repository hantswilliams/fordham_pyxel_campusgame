"""CONTINUE from a save (decisions/0031): the game comes back where you
left it, with the gate open, your bike, mission people and items. Runs the
real game headless, once."""

import json

from game.systems.input import Action, ScriptedInput


def test_continue_puts_you_back_where_you_were(tmp_path):
    from game.app import App
    from game.scenes.overworld import OverworldScene

    save = tmp_path / "save.json"
    save.write_text(json.dumps({"version": 1, "started": True, "gate_open": True,
                                "position": [20, 63], "facing": "left", "has_bike": True,
                                "missions": {"lost_and_found": {"status": "active", "done_steps": [0]}}}))
    app = App(input_source=ScriptedInput([{Action.CONFIRM}]), headless=True, save_path=save)
    assert app.scenes.top.can_continue                 # the title offers CONTINUE
    app.update()                                       # Z on CONTINUE
    world = app.scenes.top
    assert isinstance(world, OverworldScene)
    assert (world.player.tile_x, world.player.tile_y) == (20, 63)
    assert not world.map.checkpoints()                 # Bert's gate stays open
    assert app.bike.have
    names = {o.name for o in world.map.objects if o.type == "npc"}
    assert {"Worried Student", "Mail Room Staffer", "Athletics Staffer"} <= names
    item = world.map.object_at(47, 31)
    assert item is not None and item.type == "item"   # the lost ID is waiting
    assert "Lost and Found" in app.missions.tracker()

    world._save()
    again = json.loads(save.read_text())
    assert again["position"] == [20, 63] and again["has_bike"]
    assert again["missions"]["first_week"]["status"] == "active"   # the checklist started itself

    # the mission bar is hidden for a clean screen (not pinned, no pop-up on entry)...
    from game.scenes.overworld import TRACKER_FRAMES
    assert not app.progress.show_tracker
    world._watch_tracker()
    assert not world._tracker_visible()
    # ...pops up for a few seconds when the next step changes...
    app.missions.pickup(item.name)
    world._watch_tracker()
    assert world._tracker_visible()
    for _ in range(TRACKER_FRAMES):
        world._watch_tracker()
    assert not world._tracker_visible()
    # ...and stays up when pinned in the TAB menu
    app.progress.show_tracker = True
    assert world._tracker_visible()


class FakeLocalStorage:
    """Stands in for the browser's localStorage (decisions/0034)."""

    def __init__(self):
        self.items = {}

    def getItem(self, key):
        return self.items.get(key)          # like JS: null (None) when missing

    def setItem(self, key, value):
        self.items[key] = str(value)

    def removeItem(self, key):
        self.items.pop(key, None)


def test_web_build_saves_in_browser_local_storage():
    from game.systems.progress import SAVE_KEY, Progress, SaveFile
    store = FakeLocalStorage()
    save = SaveFile(None, store)
    assert not save.exists() and save.load().to_dict() == Progress().to_dict()
    p = Progress(has_bike=True, position=(20, 63), stamps=["lost_and_found"])
    save.save(p)
    assert SAVE_KEY in store.items
    again = SaveFile(None, store)                 # a reload: a new SaveFile, same storage
    assert again.exists()
    assert again.load().to_dict() == p.to_dict()
    store.items[SAVE_KEY] = "{not json"          # a damaged save starts fresh
    assert again.load().to_dict() == Progress().to_dict()
    again.delete()
    assert not again.exists()


def test_desktop_does_not_use_browser_storage():
    from game.systems.progress import browser_storage
    assert browser_storage() is None
