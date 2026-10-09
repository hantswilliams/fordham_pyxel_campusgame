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

START_MAP = "rose_hill"

# Palette: Pyxel's default 16 colors with four slots swapped:
#   2 purple -> Fordham maroon (approximation; confirm with Fordham brand
#               guidelines, see decisions/0008-art-and-branding.md)
#   3 teal   -> dark leaf green (trees, hedges)
#   4 mauve  -> wood brown (doors, trunks, benches)
#   11 mint  -> grass green
MAROON = 0x860038
PALETTE_OVERRIDES = {2: MAROON, 3: 0x3E7D3A, 4: 0x8F563B, 11: 0x7DBE52}

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
