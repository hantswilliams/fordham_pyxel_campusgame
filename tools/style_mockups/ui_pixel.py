"""Screen furniture for the two pixel styles: plaques, the area banner and the
dialogue box. Frames are drawn on the art image (so in Style A they get the
same chunky pixels as the art); words are drawn afterwards on the full
768 x 576 screen in the game's own fonts, without anti-aliasing, as Pyxel
draws them (M PLUS 1 Code, decisions/0038)."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import scene as S
from pixel import P

REPO = Path(__file__).resolve().parents[2]
READ = str(REPO / "assets/fonts/MPLUS1Code-Medium.ttf")
BOLD = str(REPO / "assets/fonts/MPLUS1Code-Bold.ttf")
SCREEN_W, SCREEN_H = 768, 576


def font(path, size):
    return ImageFont.truetype(path, size)


def crisp(draw):
    draw.fontmode = "1"
    return draw


def rbox(d, x0, y0, x1, y1, r, fill, outline=None, width=1):
    d.rounded_rectangle([x0, y0, x1 - 1, y1 - 1], radius=r, fill=fill, outline=outline, width=width)


def wrap(text, n):
    out, line = [], ""
    for w in text.split():
        if len(line) + len(w) + (1 if line else 0) > n:
            out.append(line)
            line = w
        else:
            line = (line + " " + w) if line else w
    return out + [line]


class PixelUI:
    """s: art pixels per layout pixel (1 = Style A, 2 = Style B)."""

    def __init__(self, s):
        self.s = s
        self.k = 2 // s          # screen pixels per art pixel

    # -------- plaques
    def plaque_size(self, text):
        if self.s == 1:
            return len(text) * 10 + 14, 22, 20       # screen px: w, h, font size
        return len(text) * 8 + 10, 18, 16

    def plaques_frames(self, art, labels):
        d = ImageDraw.Draw(art)
        for text, cx, top, _ in labels:
            w, h, _ = self.plaque_size(text)
            X = round((cx - S.CAM[0]) * 32) - w // 2
            Y = round((top - S.CAM[1]) * 32)
            if Y < 60 and X < 8 + len(S.AREA) * 16 + 40:
                continue
            k = self.k
            x0, y0, x1, y1 = X // k, Y // k, (X + w) // k, (Y + h) // k
            if self.s == 1:
                rbox(d, x0, y0, x1, y1, 1, P["signbd"], P["out"])
                d.line([x0 + 1, y1 - 2, x1 - 2, y1 - 2], fill=P["trim_sh"])
            else:
                rbox(d, x0, y0, x1, y1, 2, P["signbd"], P["out"])
                d.line([x0 + 2, y1 - 2, x1 - 3, y1 - 2], fill=P["trim_sh"])

    def plaques_text(self, screen, labels, hide_below=10**6):
        d = crisp(ImageDraw.Draw(screen))
        for text, cx, top, _ in labels:
            w, h, size = self.plaque_size(text)
            X = round((cx - S.CAM[0]) * 32)
            Y = round((top - S.CAM[1]) * 32)
            if Y + h > hide_below or (Y < 60 and X - w // 2 < 8 + len(S.AREA) * 16 + 40):
                continue        # under the dialogue box or the area banner
            f = font(BOLD, size)
            d.text((X, Y + h // 2 - 1), text, font=f, fill=P["out"], anchor="mm")

    # -------- area banner (top-left)
    def banner_frame(self, art, text):
        d = ImageDraw.Draw(art)
        k = self.k
        w = len(text) * 16 + 32
        x0, y0, x1, y1 = 8 // k, 8 // k, (8 + w) // k, (8 + 44) // k
        if self.s == 1:
            rbox(d, x0, y0, x1, y1, 3, P["maroon"], P["out"])
            d.line([x0 + 2, y0 + 1, x1 - 3, y0 + 1], fill=P["maroon_lt"])
            d.line([x0 + 2, y1 - 2, x1 - 3, y1 - 2], fill=P["maroon_dk"])
        else:
            rbox(d, x0 + 1, y0 + 2, x1 + 1, y1 + 2, 8, P["maroon_dk"])     # drop
            rbox(d, x0, y0, x1, y1, 8, P["maroon"], P["out"], 2)
            d.line([x0 + 6, y0 + 3, x1 - 7, y0 + 3], fill=P["maroon_lt"], width=2)

    def banner_text(self, screen, text):
        d = crisp(ImageDraw.Draw(screen))
        d.text((24, 8 + 22), text, font=font(READ, 32), fill=(255, 255, 255), anchor="lm")

    # -------- dialogue box (bottom)
    BOX = (8, 576 - 8 - 134, 760, 576 - 8)       # screen px

    def dialogue_frame(self, art, speaker):
        d = ImageDraw.Draw(art)
        k = self.k
        x0, y0, x1, y1 = (v // k for v in self.BOX)
        tw = len(speaker) * 16 + 24
        if self.s == 1:
            # FireRed-like: dark rim, light-blue frame, white page
            rbox(d, x0, y0, x1, y1, 4, P["out"])
            rbox(d, x0 + 1, y0 + 1, x1 - 1, y1 - 1, 3, (168, 184, 214))
            rbox(d, x0 + 3, y0 + 3, x1 - 3, y1 - 3, 2, (250, 249, 245))
            d.line([x0 + 4, y1 - 4, x1 - 5, y1 - 4], fill=(226, 228, 236))
            # name tab
            tx0, ty0 = x0 + 6, y0 - 15
            rbox(d, tx0, ty0, tx0 + tw // k, y0 + 2, 3, P["maroon"], P["out"])
            d.line([tx0 + 2, ty0 + 1, tx0 + tw // k - 3, ty0 + 1], fill=P["maroon_lt"])
            # continue arrow
            ax, ay = x1 - 14, y1 - 10
            d.polygon([(ax, ay), (ax + 6, ay), (ax + 3, ay + 3)], fill=P["maroon"])
        else:
            rbox(d, x0, y0 + 4, x1, y1 + 4, 14, (40, 38, 52))               # soft drop
            rbox(d, x0, y0, x1, y1, 14, P["out"])
            rbox(d, x0 + 2, y0 + 2, x1 - 2, y1 - 2, 12, (196, 206, 226))
            rbox(d, x0 + 6, y0 + 6, x1 - 6, y1 - 6, 9, (251, 250, 247))
            # name tab: a maroon pill sitting on the rim
            tx0, ty0 = x0 + 18, y0 - 22
            rbox(d, tx0, ty0, tx0 + tw, y0 + 12, 12, P["out"])
            rbox(d, tx0 + 2, ty0 + 2, tx0 + tw - 2, y0 + 10, 10, P["maroon"])
            d.line([tx0 + 10, ty0 + 4, tx0 + tw - 11, ty0 + 4], fill=P["maroon_lt"], width=2)
            ax, ay = x1 - 30, y1 - 22
            d.polygon([(ax, ay), (ax + 14, ay), (ax + 7, ay + 8)], fill=P["maroon"])

    def dialogue_text(self, screen, speaker, line):
        d = crisp(ImageDraw.Draw(screen))
        x0, y0, x1, y1 = self.BOX
        f = font(READ, 32)
        if self.s == 1:
            d.text((x0 + 12 + 12, y0 - 15), speaker, font=f, fill=(255, 255, 255), anchor="lm")
        else:
            d.text((x0 + 18 + 12, y0 - 5), speaker, font=f, fill=(255, 255, 255), anchor="lm")
        for i, ln in enumerate(wrap(line, 44)):
            d.text((x0 + 22, y0 + 18 + i * 34), ln, font=f, fill=(24, 22, 30), anchor="lt")


def compose(s, art, labels, *, dialogue=True):
    """Art image (384*s x 288*s) + furniture -> 768 x 576 screen."""
    ui = PixelUI(s)
    art = art.copy()
    ui.plaques_frames(art, labels)
    ui.banner_frame(art, S.AREA)
    if dialogue:
        ui.dialogue_frame(art, S.SPEAKER)
    screen = art.convert("RGB").resize((SCREEN_W, SCREEN_H), Image.NEAREST)
    ui.plaques_text(screen, labels, PixelUI.BOX[1] - 24 if dialogue else 10**6)
    ui.banner_text(screen, S.AREA)
    if dialogue:
        ui.dialogue_text(screen, S.SPEAKER, S.LINE)
    return screen
