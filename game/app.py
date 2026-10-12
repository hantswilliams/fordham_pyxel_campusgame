import sys
from pathlib import Path

import pyxel

from game import config
from game.gfx.placeholder_art import build_all
from game.scenes.base import SceneManager
from game.scenes.title import TitleScene
from game.systems.bike import Bike
from game.systems.input import PyxelInput
from game.systems.missions import MissionBook, load_missions
from game.systems.progress import SaveFile, browser_storage
from game.world.buildings import load_buildings
from game.world.locations import load_locations


class App:
    def __init__(self, input_source=None, headless: bool = False,
                 start_scene=None, save_path="default"):
        # in a web page Esc belongs to the page (decisions/0037): it moves the
        # keyboard out of the game, so it mustn't quit
        quit_key = pyxel.KEY_NONE if sys.platform == "emscripten" else pyxel.KEY_ESCAPE
        pyxel.init(config.SCREEN_W, config.SCREEN_H, title=config.TITLE,
                   fps=config.FPS, quit_key=quit_key, headless=headless)
        config.apply_palette(pyxel.colors)
        build_all()

        self.input = input_source or PyxelInput()
        self.locations = load_locations(config.LOCATIONS_FILE)
        # drawn buildings by location id, for card pictures (decisions/0020)
        # (a place drawn as several buildings uses the one with a card picture)
        self.buildings = {}
        for b in load_buildings(config.BUILDINGS_DIR):
            if b.location not in self.buildings or not self.buildings[b.location].card_png:
                self.buildings[b.location] = b
        # what the game remembers between sessions (decisions/0031). Headless
        # runs (tests, screenshots) keep it in memory unless given a path.
        # In a web page it goes in the browser's local storage (decisions/0034).
        storage = browser_storage() if save_path == "default" and not headless else None
        if save_path == "default":
            save_path = None if headless or storage is not None else \
                Path(pyxel.user_data_dir(*config.SAVE_DIR)) / "save.json"
        self.save_file = SaveFile(save_path, storage)
        self.progress = self.save_file.load()
        self.bike = Bike(self.progress)
        self.missions = MissionBook(
            load_missions(config.CONTENT_DIR / "missions"), self.progress,
            {k: v.name for k, v in self.locations.items()},
            has_bike=lambda: self.progress.has_bike)
        self.scenes = SceneManager()
        self.scenes.push(start_scene(self) if start_scene else TitleScene(self))

    def save(self) -> None:
        self.save_file.save(self.progress)
        self.missions.changed = False

    def new_game(self) -> None:
        """Forget everything and start again from the train."""
        from game.systems.progress import Progress
        self.save_file.delete()
        self.progress.__dict__.update(Progress().__dict__)

    def update(self) -> None:
        self.scenes.update()
        self.input.end_frame()

    def draw(self) -> None:
        self.scenes.draw()

    def run(self) -> None:
        pyxel.run(self.update, self.draw)
