"""Drawn buildings (decisions/0020): building.json files load, their
footprints become solid cells and entrances on the map, their pictures are
the right size, and every drawing uses only the game's colors."""

import json
import struct

import pytest

from game import config
from game.world import mapdata
from game.world.buildings import BuildingError, load_buildings, parse_building
from game.world.mapdata import MapError, load_map, parse_map
from game.world.tiles import DOOR_TILES, TILES

BUILDINGS = load_buildings(config.BUILDINGS_DIR)
CARD_SIZE = (228, 88)  # game/scenes/card.py PIC_W, PIC_H


def png_size(path) -> tuple[int, int]:
    with open(path, "rb") as f:
        head = f.read(24)
    assert head[:8] == b"\x89PNG\r\n\x1a\n", f"{path} is not a PNG"
    return struct.unpack(">II", head[16:24])


def minimal(**over) -> dict:
    d = {"name": "Test Hall", "map": "test", "location": "test_hall",
         "origin": [1, 1], "footprint": ["RR", "DW"]}
    d.update(over)
    return d


def test_config_and_mapdata_agree_on_the_folder():
    assert mapdata.BUILDINGS_DIR == config.BUILDINGS_DIR


def test_walsh_library_is_the_pilot():
    ids = [b.id for b in BUILDINGS]
    assert "walsh_library" in ids


def test_landmarks_need_no_entrance():
    b = parse_building(minimal(footprint=["~~", "~~"], landmark=True))
    assert b.landmark and b.entrances() == []


def test_parse_errors():
    with pytest.raises(BuildingError, match="unknown character"):
        parse_building(minimal(footprint=["R?", "DW"]))
    with pytest.raises(BuildingError, match="no entrance"):
        parse_building(minimal(footprint=["RR", "WW"]))
    with pytest.raises(BuildingError, match="status"):
        parse_building(minimal(status="done"))
    with pytest.raises(BuildingError, match="needs 'origin'"):
        d = minimal()
        del d["origin"]
        parse_building(d)


def test_footprint_is_stamped_and_entrances_open_the_card():
    b = parse_building(minimal())
    text = "#####\n#...#\n#...#\n#.@.#\n#####\n"
    m = parse_map("test", text, {}, [b])
    assert m.tiles[1][1] == "roof" and m.is_blocked(1, 1)
    door = m.object_at(1, 2)
    assert door and door.type == "door" and door.location == "test_hall"
    assert m.buildings == [b]
    # buildings for another map are ignored
    assert parse_map("other", text, {}, [b]).tiles[1][1] == "grass"


def test_hand_placed_object_on_an_entrance_is_an_error():
    b = parse_building(minimal())
    text = "#####\n#...#\n#...#\n#.@.#\n#####\n"
    meta = {"objects": [{"at": [1, 2], "type": "door", "location": "test_hall"}]}
    with pytest.raises(MapError, match="entrance"):
        parse_map("test", text, meta, [b])


@pytest.mark.parametrize("b", BUILDINGS, ids=lambda b: b.id)
def test_building_is_on_the_map_with_its_doors(b):
    m = load_map(b.map_id, config.MAPS_DIR)
    if b.landmark:
        # a landmark has no door; a sign on one of its cells, or a signpost
        # right beside it (Moglia Stadium), opens its card
        cells = {(x, y) for x, y, _ in b.cells()}
        near = cells | {(x + dx, y + dy) for x, y in cells
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
        assert any(o.type == "sign" and o.location == b.location and (o.x, o.y) in near
                   for o in m.objects), f"{b.id}: needs a sign on or beside one of its cells"
    else:
        assert b.location in {o.location for o in m.objects if o.type == "door"}
    for x, y, name in b.cells():
        assert m.tiles[y][x] == name
    for x, y in b.entrances():
        assert m.tiles[y][x] in DOOR_TILES
        assert m.object_at(x, y).location == b.location
    # the bare grid (without building.json) carries the same tiles, so the
    # map file and the building can't drift apart
    bare = load_map(b.map_id, config.MAPS_DIR, buildings_dir=None)
    for x, y, name in b.cells():
        assert bare.tiles[y][x] == name, f"{b.id}: map file differs at {(x, y)}; run tools/stamp_buildings.py"


@pytest.mark.parametrize("b", BUILDINGS, ids=lambda b: b.id)
def test_pictures_have_the_right_size(b):
    w, h = b.size
    dx, dy = b.sprite_offset
    if b.map_png:
        assert png_size(b.map_png) == (w * config.TILE - dx, h * config.TILE - dy), (
            f"{b.id}/map.png should cover the footprint plus the sprite offset")
    if b.card_png:
        assert png_size(b.card_png) == CARD_SIZE


def test_palette_file_matches_the_game():
    lines = (config.BUILDINGS_DIR / "palette.hex").read_text().split()
    assert [int(s, 16) for s in lines] == config.palette()


@pytest.mark.parametrize("b", BUILDINGS, ids=lambda b: b.id)
def test_pictures_use_only_game_colors(b):
    Image = pytest.importorskip("PIL.Image")
    allowed = {((c >> 16) & 255, (c >> 8) & 255, c & 255) for c in config.palette()}
    for path in (b.map_png, b.card_png):
        if path is None:
            continue
        im = Image.open(path).convert("RGBA")
        bad = {px[:3] for _, px in im.getcolors(1 << 20) if px[3] >= 128 and px[:3] not in allowed}
        assert not bad, f"{path.name} uses colors outside palette.hex: {sorted(bad)[:5]}"


@pytest.mark.parametrize("b", [b for b in BUILDINGS if b.map_png], ids=lambda b: b.id)
def test_every_picture_has_a_finer_one_twice_the_size(b):
    """The finer world (decisions/0045) draws map_fine.png, made from the
    same script as map.png by assets/buildings/_style/fine.py."""
    assert b.map_fine_png, f"{b.id} has no map_fine.png: run assets/buildings/_style/fine.py {b.id}"
    w, h = png_size(b.map_png)
    assert png_size(b.map_fine_png) == (w * 2, h * 2)


@pytest.mark.parametrize("b", [b for b in BUILDINGS if b.map_fine_png], ids=lambda b: b.id)
def test_finer_pictures_use_only_game_colors(b):
    Image = pytest.importorskip("PIL.Image")
    allowed = {((c >> 16) & 255, (c >> 8) & 255, c & 255) for c in config.GAME_COLORS}
    im = Image.open(b.map_fine_png).convert("RGBA")
    bad = {px[:3] for _, px in im.getcolors(1 << 20) if px[3] >= 128 and px[:3] not in allowed}
    assert not bad, f"{b.id}/map_fine.png uses colors outside the game's palette: {sorted(bad)[:5]}"


@pytest.mark.parametrize("b", [b for b in BUILDINGS if b.card_png], ids=lambda b: b.id)
def test_every_card_picture_has_a_finer_one(b):
    """The building card's picture at twice the detail (decisions/0045)."""
    assert b.card_fine_png, f"{b.id} has no card_fine.png: run assets/buildings/_style/fine.py {b.id}"
    assert png_size(b.card_fine_png) == (CARD_SIZE[0] * 2, CARD_SIZE[1] * 2)
    Image = pytest.importorskip("PIL.Image")
    allowed = {((c >> 16) & 255, (c >> 8) & 255, c & 255) for c in config.GAME_COLORS}
    im = Image.open(b.card_fine_png).convert("RGBA")
    bad = {px[:3] for _, px in im.getcolors(1 << 20) if px[3] >= 128 and px[:3] not in allowed}
    assert not bad, f"{b.id}/card_fine.png uses colors outside the game's palette: {sorted(bad)[:5]}"


def test_every_drawn_building_has_a_script_for_its_finer_picture():
    import sys
    sys.path.insert(0, str(config.BUILDINGS_DIR / "_style"))
    from fine import SOURCES
    assert {b.id for b in BUILDINGS if b.map_png} <= set(SOURCES)


def test_extra_colors_are_few():
    """D-0020 Part 4: a short list of extra colors; D-0022 raised the cap
    from 8 to 10 for Cunniffe's pink brick. More needs a decision."""
    assert len(config.EXTRA_COLORS) <= 10
    assert len(config.palette()) == 16 + len(config.EXTRA_COLORS)


def test_a_place_drawn_as_several_buildings_has_one_card_picture():
    """Martyrs' Court is two drawn buildings (decisions/0024); its card uses
    the main block's picture, and each wing gets its own name plaque."""
    from collections import defaultdict
    by_loc = defaultdict(list)
    for b in load_buildings(config.BUILDINGS_DIR):
        by_loc[b.location].append(b)
    for loc, bs in by_loc.items():
        if len(bs) > 1:
            assert sum(1 for b in bs if b.card_png) == 1, loc
            assert all(b.nameplate for b in bs), loc


@pytest.mark.parametrize("b", [b for b in BUILDINGS if b.gate is not None], ids=lambda b: b.id)
def test_gate_opens_the_card_from_the_path_in_front(b):
    """A sports field's gate (decisions/0023) is where you go in: reading it
    opens the card, and you can stand right in front of it."""
    m = load_map(b.map_id, config.MAPS_DIR)
    gx, gy = b.origin[0] + b.gate[0], b.origin[1] + b.gate[1]
    o = m.object_at(gx, gy)
    assert o is not None and o.location == b.location, f"{b.id}: no sign on its gate"
    dx, dy = {"south": (0, 1), "north": (0, -1), "west": (-1, 0), "east": (1, 0)}[b.gate_faces]
    assert not m.is_blocked(gx + dx, gy + dy), f"{b.id}: can't stand in front of the gate"
