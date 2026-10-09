import pyxel

from game import config
from game.gfx.placeholder_art import build_all
from game.scenes.base import SceneManager
from game.scenes.title import TitleScene
from game.systems.input import PyxelInput
from game.world.locations import load_locations


class App:
    def __init__(self, input_source=None, headless: bool = False,
                 start_scene=None):
        pyxel.init(config.SCREEN_W, config.SCREEN_H, title=config.TITLE,
                   fps=config.FPS, headless=headless)
        for index, rgb in config.PALETTE_OVERRIDES.items():
            pyxel.colors[index] = rgb
        build_all()

        self.input = input_source or PyxelInput()
        self.locations = load_locations(config.LOCATIONS_FILE)
        self.scenes = SceneManager()
        self.scenes.push(start_scene(self) if start_scene else TitleScene(self))

    def update(self) -> None:
        self.scenes.update()
        self.input.end_frame()

    def draw(self) -> None:
        self.scenes.draw()

    def run(self) -> None:
        pyxel.run(self.update, self.draw)
