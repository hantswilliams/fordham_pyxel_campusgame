"""The Rose Hill Campus Guide (decisions/0037): the accessible version of
the game, generated from the same content. These tests keep it complete and
correct as the game changes; tools/check_accessibility.cjs runs axe-core on
the built pages in the GitHub workflow."""

import re
import sys
from pathlib import Path

import pytest

from game import config
from game.world.mapdata import load_map
from game.world.routes import Leg, Route, legs_of, sentences

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import build_guide  # noqa: E402


@pytest.fixture(scope="module")
def guide(tmp_path_factory):
    return build_guide.build(tmp_path_factory.mktemp("guide"))


def text(path: Path) -> str:
    return path.read_text()


def test_every_place_has_a_page(guide):
    for loc_id, loc in guide.locations.items():
        page = guide.out / "places" / f"{build_guide.slug(loc_id)}.html"
        assert page.exists(), loc_id
        assert loc.blurb.replace("'", "&#x27;") in text(page) or build_guide.esc(loc.blurb) in text(page)


def test_every_page_has_the_basics(guide):
    for page in guide.pages:
        t = text(page)
        assert '<html lang="en">' in t, page
        assert re.search(r"<title>[^<]+ – Rose Hill Campus Guide</title>", t), page
        assert t.count("<h1>") == 1, f"{page}: one main heading"
        assert 'class="skip" href="#main"' in t and 'id="main"' in t, page
        assert "<nav" in t and "<main" in t and "<footer" in t, page


def test_headings_never_skip_a_level(guide):
    for page in guide.pages:
        levels = [int(n) for n in re.findall(r"<h([1-6])[ >]", text(page))]
        for a, b in zip(levels, levels[1:]):
            assert b <= a + 1, f"{page}: h{a} followed by h{b}"


def test_every_picture_has_text(guide):
    for page in guide.pages:
        for img in re.findall(r"<img [^>]*>", text(page)):
            alt = re.search(r'alt="([^"]*)"', img)
            assert alt and alt.group(1).strip(), f"{page}: {img}"


def test_every_mission_step_is_in_the_guide(guide):
    t = text(guide.out / "missions.html")
    for m in guide.missions:
        assert f'id="{m.id}"' in t
        for i in range(len(m.steps)):
            assert f'data-step="{m.id}:{i}"' in t, f"{m.id} step {i}"
            first = guide.book.step_text(m, i).split()[0]
            assert first in t


def test_every_place_can_be_reached_from_both_entrances(guide):
    for loc_id, loc in guide.locations.items():
        if loc.kind == "transit" or not build_guide.place_targets(guide.map, loc_id):
            continue
        t = text(guide.out / "places" / f"{build_guide.slug(loc_id)}.html")
        assert "aren't available" not in t, f"no directions to {loc_id}"
        assert t.count("<ol>") >= 2, f"{loc_id}: directions from both entrances"


def test_directions_follow_walkable_ground(guide):
    m = load_map(config.START_MAP, config.MAPS_DIR)
    assert guide.routes_checked
    for route, start, to in guide.routes_checked:
        path = route.path
        for a, b in zip(path, path[1:]):
            assert abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1, (start, to)
            assert not m.is_blocked(*b), f"{start} to {to} walks through {b}"
        assert sum(leg.steps for leg in route.legs) == route.steps


def test_game_keys_are_kept_out_of_mission_hints():
    assert build_guide.no_controls("It's east. Press X to hop on your bike.") == "It's east."


def luminance(hex_colour: str) -> float:
    rgb = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def test_colours_pass_wcag_contrast():
    v = dict(re.findall(r"--([a-z]+):\s*(#[0-9a-fA-F]{6})", build_guide.CSS))
    for fg in ("ink", "maroon", "muted"):                      # text: 4.5:1 (1.4.3)
        assert contrast(v[fg], v["paper"]) >= 4.5, fg
    assert contrast(v["maroon"], v["band"]) >= 4.5              # site name and links in the header
    assert contrast(v["muted"], v["band"]) >= 4.5
    for ui in ("focus", "line"):                                # focus ring, borders: 3:1 (1.4.11)
        assert contrast(v[ui], v["paper"]) >= 3, ui


def test_staircase_walks_read_as_one_diagonal():
    path = [(0, 10)]
    for i in range(4):                                         # north, east, north, east...
        x, y = path[-1]
        path.append((x, y - 1))
        path.append((x + 1, y - 1))
    legs = legs_of(path)
    assert [leg.heading for leg in legs] == ["north-east"] and legs[0].steps == 8


def test_a_single_first_step_is_folded_into_the_next():
    route = Route("A", "B", [(0, 0)] * 6, [Leg("east", 1, [(1, 0)]), Leg("north", 4, [(1, -4)])], "on your left")
    assert sentences(route)[0] == "Take one step east, then head north for 4 steps."


def test_game_page_opens_the_guide_in_a_new_tab_and_says_so():
    import build_web
    link = re.search(r'<a id="fcq-guide"[^>]*>.*?</a>', build_web.A11Y, re.S).group(0)
    assert 'target="_blank"' in link and 'rel="noopener"' in link
    assert "opens in a new tab" in link


def test_game_page_shows_when_the_game_is_paused():
    import build_web
    page = build_web.A11Y
    assert 'id="fcq-resume"' in page and "Game paused" in page
    assert 'aria-live="polite"' in page                        # the bar's status is announced
    assert "visibilitychange" in page                          # coming back to the tab
