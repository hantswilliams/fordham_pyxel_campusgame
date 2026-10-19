"""Crisp text (decisions/0038): the game is drawn at its layout size and
doubled, and the reading font is drawn over it at full size.

Pyxel can only start once per process, and another test starts the game,
so these checks run the game in a process of their own."""

import subprocess
import sys
from pathlib import Path

import pyxel

from game import config
from game.app import App
from game.config import Col
from game.gfx import display
from game.scenes.base import Scene
from game.systems.input import ScriptedInput
from game.ui import font
from game.ui.text import BIG_CHAR_W, BIG_LINE_H


class Art(Scene):
    def draw(self):
        pyxel.cls(Col.WHITE)
        pyxel.pset(10, 10, Col.MAROON)
        font.text(100, 100, "HELLO", Col.NAVY)
        display.camera(50, 0)
        font.text(150, 150, "W", Col.NAVY)      # lands at x = 100 on the screen
        display.camera()


class Cover(Scene):
    overlay = True

    def draw(self):
        pyxel.rect(90, 90, 80, 30, Col.YELLOW)  # over "HELLO"


_app = None


def make(*scenes):
    global _app
    if _app is None:
        _app = App(input_source=ScriptedInput([]), headless=True, display_scale=2,
                   start_scene=scenes[0])
    else:
        _app.scenes.replace(scenes[0](_app))
    for s in scenes[1:]:
        _app.scenes.push(s(_app))
    _app.draw()
    return _app


def colours(x0, y0, w, h):
    return {pyxel.pget(x, y) for x in range(x0, x0 + w) for y in range(y0, y0 + h)}


def check_screen_is_twice_the_layout():
    make(Art)
    assert (pyxel.width, pyxel.height) == (config.SCREEN_W * 2, config.SCREEN_H * 2)


def check_art_is_doubled_exactly():
    make(Art)
    assert colours(20, 20, 2, 2) == {Col.MAROON}
    assert pyxel.pget(19, 20) == Col.WHITE and pyxel.pget(22, 20) == Col.WHITE


def check_text_is_drawn_at_full_size_where_it_was_laid_out():
    make(Art)
    box = colours(200, 200, 5 * BIG_CHAR_W * 2, BIG_LINE_H * 2)
    assert Col.NAVY in box
    assert colours(200 - 40, 200, 30, 30) == {Col.WHITE}         # nothing left of it
    assert Col.NAVY in colours(200, 300, 16, BIG_LINE_H * 2)      # the camera-shifted "W"


def check_an_overlay_covers_the_text_beneath_it():
    make(Art, Cover)
    assert colours(200, 200, 5 * BIG_CHAR_W * 2, 20) == {Col.YELLOW}


class Tall(Scene):
    def draw(self):
        pyxel.cls(Col.WHITE)
        font.text(100, 100, "Hgjy", Col.NAVY)


def check_crisp_font_fits_the_layout():
    make(Tall)
    assert font.crisp().text_width("M") <= BIG_CHAR_W * 2     # one character per 16-pixel cell
    rows = [y for y in range(150, 280) if Col.NAVY in colours(200, y, 6 * BIG_CHAR_W * 2, 1)]
    assert rows and rows[0] >= 200 - 2 and rows[-1] < 200 + BIG_LINE_H * 2, (rows[0], rows[-1])


class Sign(Scene):
    """A maroon sign with words on it, half covered by a box drawn later."""
    def draw(self):
        pyxel.cls(Col.WHITE)
        pyxel.rect(100, 100, 100, 20, Col.MAROON)
        font.sign(104, 104, "FORDHAM ROSE", Col.WHITE, cell=6, bg=Col.MAROON)
        pyxel.rect(150, 90, 60, 40, Col.YELLOW)            # over the right half


def check_signs_are_covered_by_what_is_drawn_over_them():
    make(Sign)
    assert Col.WHITE in colours(208, 208, 80, 24)            # the uncovered words show
    assert colours(300, 200, 100, 40) == {Col.YELLOW}        # the covered half doesn't


class Intro(Scene):
    def draw(self):
        from game.gfx import intro_art

        def art():
            pyxel.cls(Col.LIGHT_BLUE)
            pyxel.pset(10, 10, Col.MAROON)
            pyxel.pset(11, 10, Col.NAVY)
        intro_art.present(art)


def check_intro_art_is_scaled_three_times_in_one_step():
    make(Intro)
    assert colours(30, 30, 3, 3) == {Col.MAROON}              # every art pixel is 3 x 3
    assert colours(33, 30, 3, 3) == {Col.NAVY}
    assert pyxel.pget(29, 30) == Col.LIGHT_BLUE and pyxel.pget(36, 30) == Col.LIGHT_BLUE


class IntroSignUnderACard(Scene):
    """An intro sign, with a card drawn over the scene afterwards."""
    def draw(self):
        from game.gfx import intro_art

        def art():
            pyxel.cls(Col.LIGHT_BLUE)
            pyxel.rect(20, 20, 60, 12, Col.MAROON)
            intro_art._label(22, 23, "FORDHAM", Col.WHITE, Col.MAROON)
        intro_art.present(art)
        pyxel.rect(0, 0, 200, 80, Col.YELLOW)                 # the card, over the sign


def check_a_card_over_the_intro_covers_its_signs():
    make(IntroSignUnderACard)
    assert colours(60, 60, 180, 40) == {Col.YELLOW}


def check_plaque_names_are_lettered_at_full_detail():
    from game.gfx.building_overlay import CHAR_W, SMALL_CHAR_W, draw_overlay
    from game.world.locations import load_locations
    from game.world.mapdata import load_map
    m = load_map(config.START_MAP, config.MAPS_DIR)
    labels = []
    draw_overlay(pyxel.Image(m.width * 16, m.height * 16), m,
                 load_locations(config.LOCATIONS_FILE), labels)
    assert len(labels) > 30
    assert {cell for *_, cell in labels} <= {CHAR_W, SMALL_CHAR_W}


def check_the_world_is_drawn_at_twice_the_detail():
    """The finer world (decisions/0045): the campus in its new colours, with
    shadows, and details a single screen pixel wide, so it isn't doubled."""
    from game.config import SHADOW_OF, Art
    from game.scenes.overworld import OverworldScene
    make(OverworldScene)
    counts = {}
    for y in range(0, pyxel.height, 2):
        for x in range(0, pyxel.width, 2):
            c = pyxel.pget(x, y)
            counts[c] = counts.get(c, 0) + 1
    total = sum(counts.values())
    assert counts.get(Art.GRASS, 0) > total * 0.05
    assert counts.get(Art.WALK, 0) > total * 0.02
    assert counts.get(SHADOW_OF[Art.GRASS], 0) + counts.get(SHADOW_OF[Art.WALK], 0) > 0
    assert counts.get(Col.LIME, 0) < total * 0.01               # today's grass is gone
    # a grass tuft's pixels: some stand alone, one screen pixel wide
    single = 0
    for y in range(pyxel.height):
        for x in range(1, pyxel.width - 1):
            if pyxel.pget(x, y) == Art.GRASS_TUFT and pyxel.pget(x - 1, y) != Art.GRASS_TUFT \
                    and pyxel.pget(x + 1, y) != Art.GRASS_TUFT:
                single += 1
                if single > 5:
                    return
    raise AssertionError("no detail finer than doubled pixels")


def check_people_bikes_and_vans_are_drawn_in_full_detail():
    """The finer people (decisions/0045, step 2): every frame drawn, outlined,
    inside its frame, right the mirror of left, steps different from standing."""
    from game.config import Art
    from game.gfx import people_art as P
    from game.world.directions import Direction
    make(Art_)
    sheet = P.sheet()

    def frame(sprite, d, f):
        u, v = P.frame_uv(sprite, d, f)
        return [[sheet.pget(u + x, v + y) for x in range(P.FRAME_W)] for y in range(P.FRAME_H)]

    for sprite in range(P.MAROON_BIKE_SPRITE + 1):
        for d in Direction:
            frames = [frame(sprite, d, f) for f in range(3)]
            for px in frames:
                seen = {c for row in px for c in row}
                assert Art.OUTLINE in seen and len(seen) > 6, (sprite, d)
                assert set(px[-1]) == {Col.BLACK}, (sprite, d)        # room below the feet
                assert {row[0] for row in px} | {row[-1] for row in px} == {Col.BLACK}, (sprite, d)
            assert frames[1] != frames[0] and frames[2] != frames[0], (sprite, d)
        for f in range(3):
            left, right = frame(sprite, Direction.LEFT, f), frame(sprite, Direction.RIGHT, f)
            assert right == [row[::-1] for row in left]
    for van, body in ((P.SHUTTLE_VAN, Art.VAN), (P.RAM_VAN, Col.MAROON)):
        for view in ("side", "front", "back"):
            u, v, w, h = P.van_uv(van, view)
            seen = {sheet.pget(u + x, v + y) for x in range(w) for y in range(h)}
            assert body in seen and Art.TYRE in seen, (van, view)
    # and the campus uses them
    from game.scenes.overworld import OverworldScene
    make(OverworldScene)
    on_screen = {pyxel.pget(x, y) for x in range(0, pyxel.width, 2) for y in range(0, pyxel.height, 2)}
    assert {Art.SKIN1, Art.OUTLINE} <= on_screen


def check_things_on_the_map_are_drawn_in_full_detail():
    """Signs, benches, the fence and the like (decisions/0045, step 3): each
    drawn and outlined in its cell, nothing spilling into the next slot."""
    from game.config import Art
    from game.gfx import object_art as O
    make(Art_)
    sheet = O.sheet()

    def seen(u, v, w, h):
        return {sheet.pget(u + x, v + y) for x in range(w) for y in range(h)}

    for name in O.OBJECTS:
        u, v = O.uv(name)
        inside = seen(u, v, 32, 32)
        assert Art.OUTLINE in inside and len(inside) > 4, name
        for margin in ((u - O.PAD, v - O.PAD, O.SLOT, O.PAD - 1), (u - O.PAD, v + 33, O.SLOT, O.PAD - 1)):
            assert seen(*margin) == {Col.BLACK}, name
    for name in O.TILES:
        assert Col.BLACK not in seen(*O.uv(name), 32, 32), name         # building tiles fill their cell
    for joins in range(16):
        assert Art.IRON in seen(*O.fence_uv(joins), 32, 32), joins


Art_ = Art                      # a plain scene, for checks that only need Pyxel started


def test_crisp_display():
    root = Path(__file__).resolve().parent.parent
    run = subprocess.run([sys.executable, "-m", "tests.test_display"], cwd=root,
                         capture_output=True, text=True, timeout=120)
    assert run.returncode == 0, run.stdout + run.stderr[-2000:]


if __name__ == "__main__":
    failed = 0
    for name, check in list(globals().items()):
        if name.startswith("check_"):
            try:
                check()
            except AssertionError as e:
                failed += 1
                print(f"FAILED {name}: {e}")
    sys.exit(1 if failed else 0)
