"""Comparison sheets: an overview grid and pixel close-ups."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import smooth

OUT = Path(__file__).resolve().parents[2] / "decisions" / "images" / "0045"
FB = smooth.ROUND_BOLD
FM = smooth.ROUND_MED
INK, MUTED, BG = (42, 39, 51), (110, 106, 122), (247, 245, 241)
COLS = [("today", "Today", "Gold/Silver-style 16 px tiles, 2x"),
        ("A", "A. Tidied", "same pixel size, cleaned up"),
        ("B", "B. Finer pixels", "twice the detail, half-size pixels"),
        ("C", "C. Smooth", "no visible pixels")]
SHOTS = ["overworld", "dialogue", "card"]


def src(tag, shot):
    return OUT / f"{tag}_{shot}.png"


def overview():
    w, h, gap, head = 384, 288, 16, 70
    sheet = Image.new("RGB", (4 * w + 5 * gap, head + 3 * (h + gap) + gap), BG)
    d = ImageDraw.Draw(sheet)
    for i, (tag, title, sub) in enumerate(COLS):
        x = gap + i * (w + gap)
        d.text((x, 18), title, font=ImageFont.truetype(FB, 22), fill=INK)
        d.text((x, 46), sub, font=ImageFont.truetype(FM, 14), fill=MUTED)
        for j, shot in enumerate(SHOTS):
            im = Image.open(src(tag, shot)).convert("RGB").resize((w, h), Image.LANCZOS)
            sheet.paste(im, (x, head + j * (h + gap)))
    sheet.save(OUT / "overview.png")


def closeups():
    box = (330, 196, 530, 372)       # the fountain, the two people, Hughes's door
    z = 3
    w, h = (box[2] - box[0]) * z, (box[3] - box[1]) * z
    gap, head = 20, 64
    sheet = Image.new("RGB", (2 * w + 3 * gap, 2 * (h + head) + 2 * gap), BG)
    d = ImageDraw.Draw(sheet)
    for i, (tag, title, sub) in enumerate(COLS):
        x = gap + (i % 2) * (w + gap)
        y = gap + (i // 2) * (h + head + gap)
        d.text((x, y + 4), title, font=ImageFont.truetype(FB, 24), fill=INK)
        d.text((x, y + 36), sub + "  (3x close-up)", font=ImageFont.truetype(FM, 15), fill=MUTED)
        im = Image.open(src(tag, "overworld")).convert("RGB").crop(box)
        im = im.resize((w, h), Image.NEAREST if tag != "C" else Image.LANCZOS)
        sheet.paste(im, (x, y + head))
    sheet.save(OUT / "closeups.png")


overview()
closeups()
print("ok")
