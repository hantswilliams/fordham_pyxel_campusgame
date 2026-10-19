"""Global game settings. See decisions/0004-screen-and-tile-size.md."""

from pathlib import Path

TITLE = "Fordham Campus Quest"

SCREEN_W = 384
SCREEN_H = 288
# Crisp text (decisions/0038): the real screen is this many times bigger.
# The game is laid out and drawn at SCREEN_W x SCREEN_H and doubled; only
# the reading-font text uses the extra pixels (game/gfx/display.py).
DISPLAY_SCALE = 2
FPS = 30

TILE = 16  # one gameplay tile = 16x16 px = 2x2 Pyxel 8x8 tiles
WALK_SPEED = 2  # pixels per frame -> 8 frames per tile (~3.75 tiles/sec)
BIKE_SPEED = 4  # on the bike (decisions/0030): twice as fast, still divides TILE

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
MAPS_DIR = CONTENT_DIR / "maps"
LOCATIONS_FILE = CONTENT_DIR / "locations.json"
INTRO_FILE = CONTENT_DIR / "intro.json"
SAVE_DIR = ("fordham", "campus_quest")  # pyxel.user_data_dir(vendor, app): where the save lives
BUILDINGS_DIR = ROOT / "assets" / "buildings"  # drawn buildings, decisions/0020

START_MAP = "rose_hill"

# Palette: Pyxel's default 16 colors with four slots swapped:
#   2 purple -> Fordham maroon (approximation; confirm with Fordham brand
#               guidelines, see decisions/0008-art-and-branding.md)
#   3 teal   -> dark leaf green (trees, hedges)
#   4 mauve  -> wood brown (doors, trunks, benches)
#   11 mint  -> grass green
MAROON = 0x860038
PALETTE_OVERRIDES = {2: MAROON, 3: 0x3E7D3A, 4: 0x8F563B, 11: 0x7DBE52}

# Extra "Fordham stone" colors added after the 16 (decisions/0020 Part 4):
# warm stone shades for Fordham's stone buildings, two roof grays, and two
# charcoal bricks for the newer residence halls.
# Keep this list short; every drawing uses only these colors plus the 16.
# assets/buildings/palette.hex holds the same colors for drawing apps.
EXTRA_COLORS = [
    0xE4DDD0,  # 16 stone highlight
    0xC6BDAE,  # 17 stone
    0x9C9386,  # 18 stone shadow
    0x6F685E,  # 19 dark stone trim
    0x8C929C,  # 20 roof
    0x6A707A,  # 21 roof shadow
    0x55535C,  # 22 charcoal brick (Campbell Hall)
    0x3B3A42,  # 23 dark charcoal brick
    0xC98A7C,  # 24 pink brick (Cunniffe House wings, decisions/0022)
    0xA5675E,  # 25 pink brick shadow
]

# Named color indices so the rest of the code never uses magic numbers.
class Col:
    BLACK = 0
    NAVY = 1
    MAROON = 2
    GREEN = 3  # dark leaf green (overridden)
    BROWN = 4  # wood brown (overridden)
    DARK_BLUE = 5
    LIGHT_BLUE = 6
    WHITE = 7
    RED = 8
    ORANGE = 9
    YELLOW = 10
    LIME = 11  # grass green (overridden)
    CYAN = 12
    GRAY = 13
    PINK = 14
    PEACH = 15
    # extra colors (EXTRA_COLORS above)
    STONE_HI = 16
    STONE = 17
    STONE_SH = 18
    STONE_DK = 19
    ROOF = 20
    ROOF_SH = 21
    BRICK = 22
    BRICK_DK = 23
    PINK_BRICK = 24
    PINK_BRICK_SH = 25


def palette() -> list[int]:
    """The 16 colors plus the extra colors, as 0xRRGGBB values, index =
    color number: what drawn buildings may use (assets/buildings/palette.hex)."""
    base = [0x000000, 0x2B335F, 0x7E2072, 0x19959C, 0x8B4852, 0x395C98, 0xA9C1FF,
            0xEEEEEE, 0xD4186C, 0xD38441, 0xE9C35B, 0x70C6A9, 0x7696DE, 0xA3A3A3,
            0xFF9798, 0xEDC7B0]  # Pyxel's default 16
    for index, rgb in PALETTE_OVERRIDES.items():
        base[index] = rgb
    return base + EXTRA_COLORS


# The finer art (decisions/0045): the world drawn at twice the detail. Its
# colors come after the ones above, so drawn buildings keep their numbers.
ART_SCALE = 2           # art pixels per layout pixel: a 16 px cell is drawn 32 px wide
ART_COLORS = {
    # lawns
    "GRASS": 0x8BC765, "GRASS_ALT": 0x82BE5E, "GRASS_TUFT": 0x6AA84E, "GRASS_HI": 0xA9DA7E,
    # walkways and plazas, with the darker edging where they meet a lawn
    "WALK": 0xEAD8B7, "WALK_EDGE": 0xCDB690,
    "PLAZA": 0xE6DFD2, "PLAZA_ALT": 0xDCD4C5, "PLAZA_GROUT": 0xC4BBAB, "PLAZA_HI": 0xF2EDE4,
    # roads, kerbs, crosswalks and parking
    "ROAD": 0x80838B, "ROAD_DK": 0x6A6D75, "CURB": 0xCED1D6, "CURB_DK": 0x5C5F67,
    "STRIPE": 0xF2F2EE, "PARK": 0x8A8D95, "PARK_LINE": 0xE6E6E0,
    # flower beds
    "FLOWER_RED": 0xAD3563, "FLOWER_YELLOW": 0xF0C95A, "FLOWER_WHITE": 0xF7F5EE,
    "FLOWER_PINK": 0xDCA597,
    # trees, and the copper beech's purple leaves
    "LEAF_OUT": 0x23502D, "LEAF_DK": 0x2F6B36, "LEAF": 0x438A3F, "LEAF_LT": 0x5FA64A,
    "LEAF_HI": 0x88C55C, "TRUNK": 0x6E4A2E, "TRUNK_DK": 0x4D3220,
    "BEECH_OUT": 0x3A1B30, "BEECH_DK": 0x5A2A48, "BEECH": 0x7A3A5E, "BEECH_LT": 0x9A5578,
    "BEECH_HI": 0xBC7C96,
    # people (game/gfx/people_art.py): an outline, skin, hair, clothes
    "OUTLINE": 0x2B2A35, "EYE": 0x1E1C26, "SHOE": 0x2A2A33,
    "SKIN1": 0xF6CDB0, "SKIN1_SH": 0xDDA88A, "SKIN2": 0xC68B62, "SKIN2_SH": 0xA16C48,
    "SKIN3": 0x8A5A3C, "SKIN3_SH": 0x6C432B,
    "HAIR_BR": 0x6B4329, "HAIR_BR_SH": 0x4C2E1C, "HAIR_BR_LT": 0x94633F,
    "HAIR_BK": 0x2E2A30, "HAIR_BK_SH": 0x1C191E, "HAIR_BK_LT": 0x4F4B5E,
    "HAIR_OR": 0xD9823F, "HAIR_OR_SH": 0xA95F2A, "HAIR_OR_LT": 0xF0A866,
    "HAIR_WH": 0xE4E1DA, "HAIR_WH_SH": 0xB7B3AA, "HAIR_WH_LT": 0xFAF9F5,
    "MAROON_SH": 0x5C0026, "MAROON_LT": 0xA8305E,
    "SHIRT_W": 0xF7F6F2, "SHIRT_W_SH": 0xD3D0C8, "SHIRT_B": 0x8FB8EA, "SHIRT_B_SH": 0x6C93C9,
    "SHIRT_Y": 0xEFC85C, "SHIRT_Y_SH": 0xCFA23C, "BLAZER": 0x5B6274, "BLAZER_SH": 0x434958,
    "GUARD": 0x34477A, "GUARD_SH": 0x26355E, "BADGE": 0xE8C766,
    "PANTS": 0x34406A, "PANTS_SH": 0x252E50, "KHAKI": 0xC9B48A, "KHAKI_SH": 0xA8935F,
    "BAG": 0x3C4A7A, "BAG_LT": 0x55689A,
    # the bike and the vans
    "BIKE": 0x7FB3E6, "BIKE_SH": 0x5A8CC4, "METAL": 0xB9BCC4, "TYRE": 0x26252D, "HUB": 0x9EA2AA,
    "VAN": 0xF4F4F0, "VAN_SH": 0xD4D5D8, "VAN_GLASS": 0x6D8FC0, "VAN_GLASS_HI": 0xBCD6F2,
    "VAN_GLASS_DK": 0x3F5A86, "BUMPER": 0x6F737D, "HEADLIGHT": 0xFBE7A0, "TAILLIGHT": 0xD93A3A,
    # buildings' windows at full detail (assets/buildings/_style/fine.py)
    "PANE_DK": 0x8DA6EA, "PANE_HI": 0xE2EBFF, "SILL": 0xC9C4BA,
    # hand-finished buildings (assets/buildings/_style/fine_plaza.py): slate, bronze, water
    "SLATE": 0x737A86, "SLATE_HI": 0xA9AFB9, "WIN": 0x30395A, "WIN_LT": 0x5A6DA0,
    "BRONZE": 0x5D5148, "BRONZE_LT": 0x857566, "BRONZE_DK": 0x3E352F,
    "WATER": 0x7CB6E8, "WATER_DK": 0x5A92CF, "WATER_HI": 0xCDE8FF,
    # signs, benches, fences and the like (game/gfx/object_art.py)
    "SIGN_BD": 0xF6F4EE, "POST": 0x6B6E78, "POST_DK": 0x4D5058,
    "WOOD_LT": 0xB07650, "WOOD_DK": 0x663B27, "IRON": 0x34363F, "IRON_HI": 0x6C7280,
    "CARD_BOX": 0xC98F55, "CARD_BOX_SH": 0x9E6C3B,
    # boxes, cards and menus (game/ui/frames.py)
    "UI_FRAME": 0xC4CEE2, "UI_PAGE": 0xFBFAF7, "UI_LINE": 0xDCDBE3, "UI_HILITE": 0xDCE6F8,
    # never drawn: marks "not this" while shadows are cut to shape (game/gfx/world_art.py)
    "MASK": 0xFF01FD,
}


class Art:
    """Color numbers for the finer art, by the names in ART_COLORS."""


for _i, _name in enumerate(ART_COLORS):
    setattr(Art, _name, len(EXTRA_COLORS) + 16 + _i)

# Shadows (decisions/0045) are one darker, cooler shade of whatever they
# fall on. Every color the map picture can hold has its shade here.
SHADOW_TINT = (0.70, 0.73, 0.86)
_SHADED = [i for i in range(1, 16 + len(EXTRA_COLORS))] + [
    getattr(Art, n) for n in ("GRASS", "GRASS_ALT", "GRASS_TUFT", "GRASS_HI", "WALK", "WALK_EDGE",
                              "PLAZA", "PLAZA_ALT", "PLAZA_GROUT", "PLAZA_HI", "ROAD", "ROAD_DK",
                              "CURB", "CURB_DK", "STRIPE", "PARK", "PARK_LINE", "FLOWER_RED",
                              "FLOWER_YELLOW", "FLOWER_WHITE", "FLOWER_PINK", "LEAF")]


def _shade(rgb: int) -> int:
    r, g, b = (rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255
    t = SHADOW_TINT
    return (round(r * t[0]) << 16) | (round(g * t[1]) << 8) | round(b * t[2])


def _with_shadows() -> tuple[list[int], dict[int, int]]:
    colors = palette() + list(ART_COLORS.values())
    shadow = {}
    for i in _SHADED:
        rgb = _shade(colors[i])
        if rgb not in colors:
            colors.append(rgb)
        shadow[i] = colors.index(rgb)
    return colors, shadow


GAME_COLORS, SHADOW_OF = _with_shadows()


def apply_palette(colors) -> None:
    """Set Pyxel's palette (pass pyxel.colors) to the game's palette: the
    building colors, the finer art's colors and their shadows."""
    colors[:] = GAME_COLORS
