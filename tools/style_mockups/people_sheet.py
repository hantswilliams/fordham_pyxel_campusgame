"""The finer people, bikes and vans (decisions/0045, step 2) on a strip of
lawn and walkway, twice as big: decisions/images/0045/step2_people.png.

    uv run python tools/style_mockups/people_sheet.py
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

import pyxel  # noqa: E402

from game import config  # noqa: E402

pyxel.init(64, 64, headless=True)
config.apply_palette(pyxel.colors)

from game.gfx import people_art as P  # noqa: E402

sheet = P.sheet()
out = pyxel.Image(sheet.width + 16, sheet.height + 16)
out.cls(config.Art.GRASS)
for row in range(8):                                    # a walkway under each row's feet
    out.rect(0, 8 + row * P.FRAME_H + P.ORIGIN[1] + 26, out.width, 8, config.Art.WALK)
for van in range(2):
    out.rect(0, 8 + P.VAN_V + van * 48 + 30, out.width, 18, config.Art.ROAD)
out.blt(8, 8, sheet, 0, 0, sheet.width, sheet.height, config.Col.BLACK)
out.save(str(REPO / "decisions" / "images" / "0045" / "step2_people.png"), 2)
print("ok")
