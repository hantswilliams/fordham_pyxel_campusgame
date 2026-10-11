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
    item = world.map.object_at(47, 33)
    assert item is not None and item.type == "item"   # the lost ID is waiting
    assert "Lost and Found" in app.missions.tracker()

    world._save()
    again = json.loads(save.read_text())
    assert again["position"] == [20, 63] and again["has_bike"]
    assert again["missions"]["first_week"]["status"] == "active"   # the checklist started itself
