"""Global game settings. See decisions/0004-screen-and-tile-size.md."""

from pathlib import Path

TITLE = "Fordham Campus Quest"

SCREEN_W = 256
SCREEN_H = 192
FPS = 30

TILE = 16  # one gameplay tile = 16x16 px = 2x2 Pyxel 8x8 tiles
WALK_SPEED = 2  # pixels per frame -> 8 frames per tile (~3.75 tiles/sec)

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
MAPS_DIR = CONTENT_DIR / "maps"
LOCATIONS_FILE = CONTENT_DIR / "locations.json"
INTRO_FILE = CONTENT_DIR / "intro.json"
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


def palette() -> list[int]:
    """The game's full palette as 0xRRGGBB values, index = color number."""
    base = [0x000000, 0x2B335F, 0x7E2072, 0x19959C, 0x8B4852, 0x395C98, 0xA9C1FF,
            0xEEEEEE, 0xD4186C, 0xD38441, 0xE9C35B, 0x70C6A9, 0x7696DE, 0xA3A3A3,
            0xFF9798, 0xEDC7B0]  # Pyxel's default 16
    for index, rgb in PALETTE_OVERRIDES.items():
        base[index] = rgb
    return base + EXTRA_COLORS


def apply_palette(colors) -> None:
    """Set Pyxel's palette (pass pyxel.colors) to the game's palette."""
    colors[:] = palette()
