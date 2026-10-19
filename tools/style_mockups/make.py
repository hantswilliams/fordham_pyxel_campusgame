"""Style mockups for decisions/0045: draws Styles A, B and C of the fountain
plaza (overworld, dialogue, Dealy Hall's card) into decisions/images/0045/.
Run tools/style_mockups/today.py first for the real "today" screenshots,
then this, then sheets.py:

    uv run python tools/style_mockups/today.py
    uv run --with numpy python tools/style_mockups/make.py
    uv run --with numpy python tools/style_mockups/sheets.py
"""
from pathlib import Path
from PIL import Image
import pixel, ui_pixel, smooth, cards

OUT = Path(__file__).resolve().parents[2] / "decisions" / "images" / "0045"
OUT.mkdir(parents=True, exist_ok=True)

for s, tag in ((1, "A"), (2, "B")):
    sc = pixel.PixelScene(s)
    art = sc.render()
    ui_pixel.compose(s, art, sc.labels, dialogue=False).save(OUT / f"{tag}_overworld.png")
    ui_pixel.compose(s, art, sc.labels, dialogue=True).save(OUT / f"{tag}_dialogue.png")
    cards.card_pixel(s, art).save(OUT / f"{tag}_card.png")

sc = smooth.SmoothScene()
art = sc.render()
for dlg, name in ((False, "overworld"), (True, "dialogue")):
    smooth.furniture(art.copy(), sc.labels, dlg).convert("RGB").resize((768, 576), Image.LANCZOS).save(OUT / f"C_{name}.png")
cards.card_smooth(art).save(OUT / "C_card.png")
print("ok")
