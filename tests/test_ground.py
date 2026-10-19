"""The ground under every cell, for the finer world art (decisions/0045):
what stands on what, where lawns and roads round their corners, where the
edging and kerbs go."""

from game import config
from game.config import Art
from game.world import ground as G
from game.world.mapdata import MapObject, parse_map


def make(text: str, objects=()):
    return parse_map("t", text, {"objects": list(objects)})


def sign(x, y, tile="sign"):
    return {"type": "sign", "at": [x, y], "tile": tile, "lines": ["Hi"]}


def test_things_stand_on_the_ground_around_them():
    m = make("""
,,,..
,b,.@
,,,..
""", [sign(4, 0)])
    grid = G.ground_grid(m)
    assert grid[1][1] == G.PLAZA                 # a bench in a plaza stands on paving
    assert grid[0][4] == G.GRASS                 # a sign on a lawn on grass
    assert grid[1][4] == G.PATH                  # the spawn is a walkway


def test_buildings_have_no_ground_of_their_own():
    grid = G.ground_grid(make("RR@\nWD."))
    assert grid[0][0] is None and grid[1][1] is None


def test_cells_that_change_get_the_ground_they_have_without_the_change():
    m = make("""
:::
:@:
""", [{"type": "checkpoint", "at": [0, 0], "tile": "reader_gate", "open_tile": "path",
       "name": "Bert", "lines": ["ID?"]}])
    m.add_object(MapObject(type="item", x=2, y=0, name="ID card", tile="item_card", lines=["!"]))
    tiles = G.base_tiles(m)
    assert tiles[0][0] == "path" and tiles[0][2] == "path"   # the gate open, the item gone
    assert m.tiles[0][0] == "reader_gate"                     # the map itself is unchanged


def test_a_lawn_rounds_its_corner_where_paving_wraps_round_it():
    grid = G.ground_grid(make("""
:::
:..
:.@
"""))
    assert G.lawn_corners(grid, 1, 1) == [("nw", G.PATH)]
    assert G.lawn_corners(grid, 2, 1) == []


def test_a_walkway_rounds_its_corners_where_lawn_wraps_round_it():
    grid = G.ground_grid(make("""
...
.@.
...
"""))
    assert G.paving_corners(grid, 1, 1) == ["nw", "ne", "sw", "se"]


def test_a_staircase_walkway_joins_up_corner_to_corner():
    grid = G.ground_grid(make("""
:..
.@.
..:
"""))
    assert G.paving_corners(grid, 0, 0) == []                # stays square toward the next step
    assert ("sw", G.PATH) in G.lawn_corners(grid, 1, 0)      # the lawn gives way instead
    assert ("ne", G.PATH) in G.lawn_corners(grid, 0, 1)


def test_edging_runs_along_lawns_and_stops_short_at_rounded_corners():
    grid = G.ground_grid(make("""
.....
.:@:.
"""))
    def top(x):
        return [e for e in G.edging(grid, x, 1) if e[0] == "top"]
    # the walkway's top side meets the lawn all along; its two end cells'
    # outer corners are rounded, so the edging stops short there
    assert top(2) == [("top", False, False)]
    assert top(1) == [("top", True, False)]
    assert top(3) == [("top", False, True)]


def test_roads_get_kerbs_against_walkways_and_lawns_but_not_buildings():
    grid = G.ground_grid(make("""
:@:
===
R.R
"""))
    assert [k[0] for k in G.kerbs(grid, 1, 1)] == ["top", "bottom"]
    assert [k[0] for k in G.kerbs(grid, 0, 1)] == ["top"]


def test_a_staircase_road_joins_up_corner_to_corner():
    grid = G.ground_grid(make("""
=::
:=:
:@=
"""))
    # the middle step's outer corners bend round; toward the next step it stays square
    assert G.road_corners(grid, 1, 1) == [("ne", G.PATH), ("sw", G.PATH)]
    # the road fills the walkways' corners between the steps, its kerb curving
    assert G.kerb_corners(grid, 1, 0) == [("sw", G.ROAD)]
    assert G.kerb_corners(grid, 0, 1) == [("ne", G.ROAD)]


def test_the_real_map_has_ground_under_every_walkable_cell():
    from game.world.mapdata import load_map
    from game.world.tiles import TILES
    m = load_map(config.START_MAP, config.MAPS_DIR)
    grid = G.ground_grid(m)
    for y, row in enumerate(G.base_tiles(m)):
        for x, t in enumerate(row):
            if not TILES[t].solid:
                assert grid[y][x] is not None, (x, y, t)


def test_the_palette_fits_pyxel_and_keeps_the_building_colours():
    colours = config.GAME_COLORS
    assert len(set(colours)) == len(colours)
    assert len(colours) + 1 <= 255                         # + the crisp screen's key colour
    assert colours[:len(config.palette())] == config.palette()   # drawn buildings keep their numbers
    assert config.Art.GRASS == len(config.palette())


def test_every_ground_colour_has_a_darker_shadow():
    def lum(i):
        c = config.GAME_COLORS[i]
        return ((c >> 16) & 255) * 0.3 + ((c >> 8) & 255) * 0.59 + (c & 255) * 0.11
    for c in (Art.GRASS, Art.GRASS_TUFT, Art.WALK, Art.WALK_EDGE, Art.PLAZA, Art.ROAD, Art.CURB,
              Art.STRIPE, Art.PARK, config.Col.STONE, config.Col.MAROON):
        s = config.SHADOW_OF[c]
        assert s != c and lum(s) < lum(c)
        assert s not in config.SHADOW_OF                    # a shadow never darkens twice
