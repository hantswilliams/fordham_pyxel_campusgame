"""Today's look for decisions/0045, from the real game: the mockups' camera,
people and line, saved as decisions/images/0045/today_*.png.

    uv run python tools/style_mockups/today.py
"""
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
OUT = REPO / "decisions" / "images" / "0045"
OUT.mkdir(parents=True, exist_ok=True)

import pyxel
from game.app import App
from game.scenes.overworld import OverworldScene
from game.scenes.dialogue import DialogueScene
from game.world.mapdata import MapObject
from game.world.directions import Direction
from game.world import shuttle, wander
import scene as S

wander.ENABLED = False
shuttle.ENABLED = False

def start(app):
    app.progress.gate_open = True
    app.progress.position = (S.PLAYER[0], S.PLAYER[1])
    app.progress.facing = S.PLAYER[2]
    sc = OverworldScene(app)
    sc.map.add_object(MapObject(type="npc", x=36, y=44, name="Leader (mockup)", lines=[S.LINE],
                                sprite=1, facing=Direction.LEFT))
    # the same passers-by as the mockups
    sc.map.add_object(MapObject(type="npc", x=26, y=39, name="Student (mockup)", lines=["Hi"],
                                sprite=4, facing=Direction.UP))
    sc.map.add_object(MapObject(type="npc", x=44, y=41, name="Staff (mockup)", lines=["Hi"],
                                sprite=3, facing=Direction.DOWN))
    sc._update_camera = lambda: setattr(sc, "cam", (int(S.CAM[0] * 16), int(S.CAM[1] * 16)))
    sc._update_camera()
    return sc

app = App(headless=True, start_scene=start)
for _ in range(8):
    app.update(); app.draw()
pyxel.screen.save(str(OUT / "today_overworld.png"), 1)
app.scenes.push(DialogueScene(app, [S.LINE], speaker=S.SPEAKER))
for _ in range(150):
    app.update(); app.draw()
pyxel.screen.save(str(OUT / "today_dialogue.png"), 1)
from game.scenes.card import BuildingCardScene
app.scenes.pop()
app.scenes.push(BuildingCardScene(app, app.locations["dealy_hall"]))
for _ in range(10):
    app.update(); app.draw()
pyxel.screen.save(str(OUT / "today_card.png"), 1)
print("ok")
