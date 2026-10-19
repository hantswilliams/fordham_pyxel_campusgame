"""Style C: smooth, illustrated, no visible pixels.

Drawn at 4 px per layout pixel (1536 x 1152), with gradients, soft shadows
and soft outlines, then scaled down to 768 x 576 for smooth edges. Same
scene, same geometry as the pixel styles.
"""

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import scene as S

F = 4                       # hi-res px per unit
W, H = 384 * F, 288 * F
FONTS = Path(__file__).resolve().parents[2] / "build" / "fonts"
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/mplusrounded1c/MPLUSRounded1c-{}.ttf"


def _rounded(weight):
    """M PLUS Rounded 1c (SIL OFL), only for the Style C mockup: fetched
    into build/fonts/ the first time, not part of the game."""
    path = FONTS / f"MPLUSRounded1c-{weight}.ttf"
    if not path.exists():
        import urllib.request
        FONTS.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(FONT_URL.format(weight), path)
    return str(path)


ROUND_MED = _rounded("Medium")
ROUND_BOLD = _rounded("Bold")


def rgb(h):
    return ((h >> 16) & 255, (h >> 8) & 255, h & 255)


C = {k: rgb(v) for k, v in dict(
    grass=0x96CF74, grass_dk=0x86C266, grass_lt=0xA4D883, grass_edge=0xB3E094,
    walk=0xF1E6D3, walk_edge=0xE0D0B5,
    plaza=0xF0EBE2, plaza_line=0xDDD5C7, plaza_alt=0xE9E3D8,
    road=0x858B98, road_line=0x767C89, curb=0xDDE0E6, stripe=0xF7F7F4,
    leaf_hi=0xA6DC72, leaf=0x63B252, leaf_dk=0x3C8546, leaf_out=0x2C6338,
    trunk=0x8A5E3E, trunk_dk=0x6A452C,
    stone_top=0x6F6E7D, stone_bot=0x585766, stone_band=0x7A7988,
    trim=0xF8F6F0, trim_sh=0xDAD6CC,
    slate_lt=0x9CA4B2, slate=0x8089977, slate_dk=0x68707E,
    glass_lt=0xC9E7FF, glass=0x92C6F2, glass_dk=0x5E8FCB,
    win_top=0x2C3757, win_bot=0x4A5F92, win_glint=0xA9BEE8,
    pink=0xD9A091, pink_dk=0xC1857A, cream=0xF7F1E5, cream_sh=0xE4DACA,
    brick=0xB8644F, brick_dk=0x9A4E3D,
    wood=0xA0623F, wood_dk=0x7A4529,
    maroon=0x8A1538, maroon_lt=0xB43C62, maroon_dk=0x5F0B26,
    bronze=0x6B5E54, bronze_lt=0x9A8A7A, bronze_dk=0x483E37,
    water_lt=0xD6EEFF, water=0x8CC4F0, water_dk=0x5E9BD8,
    stone_lt=0xF1ECE3, stone=0xD7D0C3, stone_dk=0xB2A99A,
    sign=0xFFFFFF, post=0x707584,
    skin1=0xF8D5BC, skin1_sh=0xE9B597, skin2=0xD09A73, skin2_sh=0xB27C57,
    skin3=0x93644A, skin3_sh=0x77503A,
    hair_br=0x74492E, hair_br_lt=0xA06B45, hair_bk=0x34303A, hair_bk_lt=0x5C576A,
    hair_or=0xE08B45, hair_or_lt=0xF4B278, hair_wh=0xE9E6E0, hair_wh_lt=0xFFFFFF,
    shirt_w=0xFBFAF7, shirt_w_sh=0xDCD9D1, shirt_b=0x95BFEF, shirt_b_sh=0x759FD3,
    shirt_y=0xF4CF63, shirt_y_sh=0xDCB04A, blazer=0x5E667A, blazer_sh=0x4A5163,
    pants=0x3A4672, pants_sh=0x2C365A, khaki=0xCDB88E, khaki_sh=0xB09B6E,
    shoe=0x2E2E38, eye=0x24212C, bag=0x40508A, ink=0x2A2733,
).items()}
C["slate"] = rgb(0x808997)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def darker(c, k=0.8):
    return tuple(int(v * k) for v in c)


# --------------------------------------------------------------------------
class SPen:
    """Smooth drawing in units on a local RGBA sprite (F px per unit)."""

    def __init__(self, w, h):
        self.img = Image.new("RGBA", (int(w * F), int(h * F)), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    @staticmethod
    def b(x0, y0, x1, y1):
        return [x0 * F, y0 * F, x1 * F - 1, y1 * F - 1]

    def _mask(self):
        return Image.new("L", self.img.size, 0)

    def _fill(self, mask, fill):
        if isinstance(fill, Image.Image):
            src = fill
        else:
            src = Image.new("RGBA", self.img.size, tuple(fill) + (255,))
        self.img.paste(src, (0, 0), mask)

    def rect(self, x0, y0, x1, y1, c, r=0):
        if r:
            self.d.rounded_rectangle(self.b(x0, y0, x1, y1), radius=r * F, fill=C.get(c, c) if isinstance(c, str) else c)
        else:
            self.d.rectangle(self.b(x0, y0, x1, y1), fill=C.get(c, c) if isinstance(c, str) else c)

    def oval(self, x0, y0, x1, y1, c):
        self.d.ellipse(self.b(x0, y0, x1, y1), fill=C[c] if isinstance(c, str) else c)

    def poly(self, pts, c):
        self.d.polygon([(x * F, y * F) for x, y in pts], fill=C[c] if isinstance(c, str) else c)

    def line(self, x0, y0, x1, y1, c, w=1):
        self.d.line([(x0 * F, y0 * F), (x1 * F, y1 * F)], fill=C[c] if isinstance(c, str) else c, width=max(1, int(w * F)))

    def grad(self, shape, box, c0, c1, r=0, horizontal=False, pts=None):
        """Fill a rect / rounded rect / oval / polygon with a linear gradient."""
        c0 = C[c0] if isinstance(c0, str) else c0
        c1 = C[c1] if isinstance(c1, str) else c1
        m = self._mask()
        md = ImageDraw.Draw(m)
        if shape == "rect":
            md.rounded_rectangle(self.b(*box), radius=r * F, fill=255) if r else md.rectangle(self.b(*box), fill=255)
        elif shape == "oval":
            md.ellipse(self.b(*box), fill=255)
        else:
            md.polygon([(x * F, y * F) for x, y in pts], fill=255)
        x0, y0, x1, y1 = [v * F for v in box]
        Wd, Hd = self.img.size
        if horizontal:
            t = np.clip((np.arange(Wd) - x0) / max(1, x1 - x0), 0, 1)[None, :].repeat(Hd, 0)
        else:
            t = np.clip((np.arange(Hd) - y0) / max(1, y1 - y0), 0, 1)[:, None].repeat(Wd, 1)
        g = np.zeros((Hd, Wd, 4), np.uint8)
        for k in range(3):
            g[..., k] = (c0[k] + (c1[k] - c0[k]) * t).astype(np.uint8)
        g[..., 3] = 255
        self._fill(m, Image.fromarray(g))

    def ball(self, x0, y0, x1, y1, c_hi, c_mid, c_lo):
        """An oval lit from the top-left (radial gradient)."""
        c_hi, c_mid, c_lo = (C[c] if isinstance(c, str) else c for c in (c_hi, c_mid, c_lo))
        m = self._mask()
        ImageDraw.Draw(m).ellipse(self.b(x0, y0, x1, y1), fill=255)
        Wd, Hd = self.img.size
        yy, xx = np.mgrid[0:Hd, 0:Wd].astype(np.float32)
        cx, cy = (x0 + (x1 - x0) * 0.32) * F, (y0 + (y1 - y0) * 0.28) * F
        rad = max(x1 - x0, y1 - y0) * F
        t = np.clip(np.hypot(xx - cx, yy - cy) / rad, 0, 1)
        g = np.zeros((Hd, Wd, 4), np.uint8)
        for k in range(3):
            a = np.where(t < 0.45, c_hi[k] + (c_mid[k] - c_hi[k]) * (t / 0.45),
                         c_mid[k] + (c_lo[k] - c_mid[k]) * ((t - 0.45) / 0.55))
            g[..., k] = a.astype(np.uint8)
        g[..., 3] = 255
        self._fill(m, Image.fromarray(g))

    def glaze(self, pts, alpha=60, c=(255, 255, 255)):
        """A translucent highlight polygon (reflections on glass)."""
        lay = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).polygon([(x * F, y * F) for x, y in pts], fill=tuple(c) + (alpha,))
        a = np.array(self.img)
        mask = a[..., 3] > 0
        lay_a = np.array(lay)
        lay_a[~mask, 3] = 0
        self.img = Image.alpha_composite(self.img, Image.fromarray(lay_a))
        self.d = ImageDraw.Draw(self.img)


def soft_outline(img, color, width_units=0.9, alpha=170):
    """A soft, coloured outline round a sprite (instead of black pixel lines)."""
    a = img.split()[3]
    k = int(width_units * F) * 2 + 1
    grown = a.filter(ImageFilter.MaxFilter(k))
    base = Image.new("RGBA", img.size, tuple(color) + (0,))
    base.putalpha(grown.point(lambda v: alpha if v > 0 else 0))
    return Image.alpha_composite(base, img)


def padded(img, units=2):
    n = int(units * F)
    out = Image.new("RGBA", (img.width + 2 * n, img.height + 2 * n), (0, 0, 0, 0))
    out.paste(img, (n, n))
    return out, n


# --------------------------------------------------------------------------
class SmoothScene:
    def __init__(self):
        self.img = Image.new("RGBA", (W, H), C["grass"] + (255,))
        self.shadow = Image.new("L", (W, H), 0)
        self.labels = []
        self.adding_shadows = True

    def X(self, cx):
        return (cx - S.CAM[0]) * 16 * F

    def Y(self, cy):
        return (cy - S.CAM[1]) * 16 * F

    def paste(self, sprite, x, y, pad_px=0):
        x, y = int(x) - pad_px, int(y) - pad_px
        cx0, cy0 = max(0, -x), max(0, -y)
        crop = sprite.crop((cx0, cy0, sprite.width, sprite.height))
        self.img.alpha_composite(crop, (x + cx0, y + cy0))

    def shade(self, shape, box_or_pts, cell):
        if not self.adding_shadows:
            return
        d = ImageDraw.Draw(self.shadow)
        ox, oy = self.X(cell[0]), self.Y(cell[1])
        if shape == "oval":
            x0, y0, x1, y1 = box_or_pts
            d.ellipse([ox + x0 * F, oy + y0 * F, ox + x1 * F, oy + y1 * F], fill=255)
        else:
            d.polygon([(ox + x * F, oy + y * F) for x, y in box_or_pts], fill=255)

    # ------------------------------------------------------------------ ground
    def ground(self):
        T = 16 * F
        x0, y0 = math.floor(S.CAM[0]) - 1, math.floor(S.CAM[1]) - 1
        nx, ny = S.VIEW_W + 3, S.VIEW_H + 3
        kinds = ["grass", "walk", "plaza", "road", "xwalk_v", "xwalk_h", "flowers"]
        grid = np.array([[kinds.index(S.ground(x0 + i, y0 + j)) for i in range(nx)] for j in range(ny)], np.uint8)
        mat = np.kron(grid, np.ones((T, T), np.uint8))
        ox, oy = int(self.X(x0)), int(self.Y(y0))
        Hh, Ww = mat.shape
        paved = (mat >= 1) & (mat <= 5)
        m = np.array(Image.fromarray((paved * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5 * F))) >= 128
        mat = np.where(m & ~paved, 1, mat)
        mat = np.where(~m & paved, np.where(mat == 6, 6, 0), mat)
        lawn = (mat == 0) | (mat == 6)
        yy, xx = np.mgrid[0:Hh, 0:Ww]
        gx, gy = (xx + ox) / F, (yy + oy) / F        # unit coords
        out = np.zeros((Hh, Ww, 3), np.float32)

        # lawn: soft noise + gentle mowing stripes
        rng = np.random.default_rng(4)
        noise = Image.fromarray((rng.random((ny * 2, nx * 2)) * 255).astype(np.uint8)).resize((Ww, Hh), Image.BICUBIC)
        noise = (np.array(noise) / 255.0 - 0.5)
        stripes = ((((gx + gy * 0.0) / 32.0) % 1.0) < 0.5).astype(np.float32)
        base = np.array(C["grass"], np.float32)
        alt = np.array(C["grass_lt"], np.float32)
        for k in range(3):
            out[..., k] = base[k] + (alt[k] - base[k]) * stripes * 0.55 + noise * 10
        # paved materials
        def put(mask, col):
            out[mask] = np.array(C[col], np.float32)

        walk = mat == 1
        plaza = mat == 2
        road = (mat >= 3) & (mat <= 5)
        put(walk, "walk")
        put(plaza, "plaza")
        # plaza slabs: per-slab tint + thin joints every 8 units
        sx, sy = (gx // 8).astype(int), (gy // 8).astype(int)
        alt_slab = ((sx * 7 + sy * 13) % 5 == 0) & plaza
        put(alt_slab, "plaza_alt")
        joint = plaza & (((gx % 8) < 0.5) | ((gy % 8) < 0.5))
        put(joint, "plaza_line")
        # road with a soft curb
        put(road, "road")
        road_img = Image.fromarray((road * 255).astype(np.uint8))
        near_road = np.array(road_img.filter(ImageFilter.MaxFilter(int(2.5 * F) * 2 + 1))) > 0
        put(~road & near_road & (walk | plaza), "curb")
        near_paved = np.array(Image.fromarray(((~road) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(int(0.8 * F) * 2 + 1))) > 0
        put(road & near_paved, "road_line")
        # crosswalk bars with round ends
        lxu, lyu = gx % 16, gy % 16
        xv = (mat == 4) & ((lxu % 5.33) > 1.6) & ((lxu % 5.33) < 4.4) & (lyu > -1)
        xh = (mat == 5) & ((lyu % 5.33) > 1.6) & ((lyu % 5.33) < 4.4)
        put(xv | xh, "stripe")

        # lawn edge: a soft light kerb on the lawn, a soft shade on the paving
        lawn_img = Image.fromarray((lawn * 255).astype(np.uint8))
        grow = np.array(lawn_img.filter(ImageFilter.MaxFilter(int(1.2 * F) * 2 + 1))) > 0
        shrink = np.array(lawn_img.filter(ImageFilter.MinFilter(int(1.0 * F) * 2 + 1))) > 0
        edge_on_lawn = lawn & ~shrink
        edge_on_paving = ~lawn & grow
        out[edge_on_lawn] = out[edge_on_lawn] * 0.5 + np.array(C["grass_edge"]) * 0.5
        out[edge_on_paving] = out[edge_on_paving] * 0.93

        img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")
        self.img.paste(img, (ox, oy))
        for j in range(ny):
            for i in range(nx):
                if S.cell(x0 + i, y0 + j) == "*":
                    self.flowers(x0 + i, y0 + j)

    def flowers(self, cx, cy):
        p = SPen(16, 16)
        for k, (x, y) in enumerate([(3, 4), (11, 3), (7, 8), (12, 10), (3, 12), (9, 13)]):
            p.oval(x - 2.6, y - 1.2, x + 2.6, y + 2.6, mix(C["grass"], C["leaf_dk"], 0.45))
        cols = [C["maroon_lt"], (255, 255, 255), C["shirt_y"], (246, 160, 180)]
        spots = [(4, 4), (11, 3.5), (7.5, 8), (12.5, 10), (3.5, 11.5), (9, 12.5)]
        for k, (x, y) in enumerate(spots):
            c = cols[(k * 3 + int(cx + cy)) % 4]
            for a in range(5):
                ang = a * 2 * math.pi / 5
                px, py = x + math.cos(ang) * 1.3, y + math.sin(ang) * 1.3
                p.oval(px - 1.1, py - 1.1, px + 1.1, py + 1.1, c)
            p.oval(x - 0.7, y - 0.7, x + 0.7, y + 0.7, C["shirt_y"] if c != C["shirt_y"] else (255, 255, 255))
        self.paste(p.img, self.X(cx), self.Y(cy))

    def apply_shadow(self):
        m = np.array(self.shadow.filter(ImageFilter.GaussianBlur(2.2 * F))).astype(np.float32) / 255.0
        a = np.array(self.img).astype(np.float32)
        tint = np.array([0.62, 0.66, 0.84])
        for k in range(3):
            a[..., k] *= 1 - m * (1 - tint[k]) * 0.95
        self.img = Image.fromarray(a.astype(np.uint8))

    # ------------------------------------------------------------------- trees
    def tree(self, cx, cy):
        img, n = self.tree_sprite()
        self.shade("oval", (-3, 9, 23, 19), (cx, cy))
        self.paste(img, self.X(cx) - 6 * F, self.Y(cy) - 15 * F, n)

    def tree_sprite(self):
        p = SPen(28, 32)
        p.grad("rect", (12, 18, 16, 30), "trunk", "trunk_dk", r=1.5, horizontal=True)
        lumps = [(14, 13, 10.5), (7.5, 16, 6.5), (20.5, 16, 6.5), (14, 6.5, 7.5), (8.5, 9.5, 6.5), (19.5, 9.5, 6.5)]
        for x, y, r in lumps:
            p.oval(x - r, y - r, x + r, y + r, "leaf_dk")
        for x, y, r in sorted(lumps, key=lambda l: -l[1]):
            p.ball(x - r * 0.95, y - r * 0.98, x + r * 0.9, y + r * 0.85, "leaf_hi", "leaf", "leaf_dk")
        img, n = padded(p.img)
        return soft_outline(img, C["leaf_out"], 0.7, 150), n

    # ---------------------------------------------------------------- objects
    def bench(self, cx, cy):
        p = SPen(16, 16)
        p.rect(2.5, 11, 3.5, 14.5, "post")
        p.rect(12.5, 11, 13.5, 14.5, "post")
        p.grad("rect", (1, 4.5, 15, 7.5), "wood", "wood_dk", r=1)
        p.grad("rect", (1, 8.5, 15, 11.5), "wood", "wood_dk", r=1)
        img, n = padded(p.img)
        img = soft_outline(img, C["ink"], 0.5, 120)
        self.shade("oval", (1, 10, 17, 16), (cx, cy))
        self.paste(img, self.X(cx), self.Y(cy), n)

    def signpost(self, cx, cy, maroon=False):
        p = SPen(16, 22)
        p.rect(7.2, 12, 8.8, 21, "post", r=0.7)
        if maroon:
            p.grad("rect", (2, 3.5, 14, 14), "maroon_lt", "maroon", r=3)
            p.rect(4.5, 6.5, 11.5, 11, (255, 255, 255), r=1.5)
            p.rect(5.5, 7.3, 10.5, 8.8, "maroon", r=0.6)
            p.oval(5, 10.3, 7, 12.3, (255, 255, 255))
            p.oval(9, 10.3, 11, 12.3, (255, 255, 255))
        else:
            p.rect(2, 4.5, 14, 13.5, "sign", r=2.5)
            for k, y in enumerate((7, 9, 11)):
                p.rect(4.5, y - 0.4, 11.5 - (k == 2) * 3, y + 0.4, "post", r=0.4)
        img, n = padded(p.img)
        img = soft_outline(img, C["ink"], 0.55, 130)
        self.shade("oval", (4, 12, 16, 17), (cx, cy))
        self.paste(img, self.X(cx), self.Y(cy) - 6 * F, n)

    def statue(self, cx, cy):
        p = SPen(16, 26)
        p.grad("rect", (3, 17, 13, 24), "stone_lt", "stone_dk", r=1, horizontal=True)
        p.ball(5.8, 1.8, 10.2, 6.2, "bronze_lt", "bronze", "bronze_dk")
        p.grad("rect", (5, 6, 11, 16), "bronze_lt", "bronze_dk", r=2.5, horizontal=True)
        img, n = padded(p.img)
        img = soft_outline(img, C["ink"], 0.55, 130)
        self.shade("oval", (3, 19, 18, 26), (cx, cy - 0.5))
        self.paste(img, self.X(cx), self.Y(cy) - 9 * F, n)

    def ram(self, cx, cy):
        p = SPen(18, 24)
        p.grad("rect", (2, 14, 16, 22), "stone_lt", "stone_dk", r=1, horizontal=True)
        p.rect(5, 10.5, 6.5, 14.5, "bronze_dk", r=0.6)
        p.rect(12, 10.5, 13.5, 14.5, "bronze_dk", r=0.6)
        p.ball(4, 5.5, 15.5, 13, "bronze_lt", "bronze", "bronze_dk")
        p.ball(1.5, 3, 7.5, 9, "bronze_lt", "bronze", "bronze_dk")
        p.oval(3, 1.5, 8.5, 7, "bronze_lt")
        p.oval(4.5, 3, 7, 5.5, "bronze_dk")
        img, n = padded(p.img)
        img = soft_outline(img, C["ink"], 0.55, 130)
        self.shade("oval", (2, 17, 20, 24), (cx, cy - 0.5))
        self.paste(img, self.X(cx), self.Y(cy) - 7 * F, n)

    def fountain(self, cx, cy):
        p = SPen(36, 46)
        p.grad("oval", (1, 17, 35, 44), "stone_lt", "stone_dk")
        p.oval(4, 20, 32, 40, "water_dk")
        p.ball(4.5, 20.5, 31.5, 39, "water_lt", "water", "water_dk")
        for x, y, w in [(8, 27, 5), (22, 25, 6), (11, 33, 7), (24, 32, 4)]:
            p.rect(x, y, x + w, y + 0.6, (255, 255, 255, 200), r=0.3)
        p.grad("rect", (15, 14, 21, 31), "bronze_lt", "bronze_dk", r=1, horizontal=True)
        p.grad("oval", (9, 21, 27, 28), "bronze_lt", "bronze_dk", horizontal=True)
        p.oval(11, 21.5, 25, 24.8, "water")
        p.grad("oval", (13, 10, 23, 15), "bronze_lt", "bronze_dk", horizontal=True)
        p.oval(14.5, 10.5, 21.5, 12.8, "water")
        p.grad("rect", (16.5, 4, 19.5, 11), "bronze_lt", "bronze_dk", r=1, horizontal=True)
        p.rect(17.2, 0, 18.8, 5, "water_lt", r=0.8)
        for x, y in [(18, 0.5), (15, 3), (21, 3), (13, 6), (23, 6), (12, 9.5), (24, 9.5)]:
            p.oval(x - 0.7, y - 0.7, x + 0.7, y + 0.9, "water_lt")
        img, n = padded(p.img)
        img = soft_outline(img, C["ink"], 0.6, 110)
        self.shade("oval", (3, 19, 39, 47), (cx, cy - 1))
        self.paste(img, self.X(cx), self.Y(cy) - 14 * F, n)

    # -------------------------------------------------------------- buildings
    def building_sprite(self, b):
        Wb, Hb = b["w"] * 16, b["h"] * 16
        top = 14 if b["kind"] == "cunniffe" else 0
        p = SPen(Wb, Hb + top)
        getattr(self, "_b_" + b["kind"])(p, b, Wb, Hb, top)
        img, n = padded(p.img)
        return soft_outline(img, C["ink"], 0.6, 140), n

    def building(self, b):
        Wb, Hb = b["w"] * 16, b["h"] * 16
        top = 14 if b["kind"] == "cunniffe" else 0
        img, n = self.building_sprite(b)
        self.shade("poly", [(Wb, 2), (Wb + 7, 7), (Wb + 7, Hb + 3), (5, Hb + 3), (1, Hb), (Wb, Hb)], (b["x"], b["y"]))
        self.paste(img, self.X(b["x"]), self.Y(b["y"]) - top * F, n)

    def _roof(self, p, x0, y0, x1, y1):
        p.grad("rect", (x0, y0, x1, y1), "slate_lt", "slate_dk")
        y = y0 + 4
        while y < y1 - 2:
            p.rect(x0, y, x1, y + 0.35, mix(C["slate"], C["slate_dk"], 0.6))
            y += 4
        p.rect(x0, y1 - 1.2, x1, y1, "slate_dk")

    def _wall(self, p, x0, y0, x1, y1, top="stone_top", bot="stone_bot", bands=True):
        p.grad("rect", (x0, y0, x1, y1), top, bot)
        if bands:
            y = y0 + 15
            while y < y1 - 4:
                p.rect(x0, y, x1, y + 0.5, mix(C[top], C["stone_band"], 0.8))
                y += 14.5

    def _window(self, p, x, y, w, h, arched=True):
        if arched:
            p.rect(x - 1, y + w / 2, x + w + 1, y + h + 1, "trim")
            p.oval(x - 1, y - 1, x + w + 1, y + w + 1, "trim")
            p.grad("rect", (x, y + w / 2, x + w, y + h), "win_top", "win_bot")
            p.grad("oval", (x, y, x + w, y + w), "win_top", "win_top")
        else:
            p.rect(x - 1, y - 1, x + w + 1, y + h + 1, "trim", r=0.6)
            p.grad("rect", (x, y, x + w, y + h), "win_top", "win_bot", r=0.4)
        p.rect(x - 1.5, y + h + 0.4, x + w + 1.5, y + h + 1.4, "trim_sh", r=0.4)
        p.rect(x + w / 2 - 0.25, y + (w / 2 if arched else 0), x + w / 2 + 0.25, y + h, "trim")
        p.poly([(x + 0.6, y + h * 0.75), (x + w * 0.55, y + (w / 3 if arched else 0.5)),
                (x + w * 0.8, y + (w / 3 if arched else 0.5)), (x + 0.6, y + h)], mix(C["win_bot"], C["win_glint"], 0.45))

    def _b_hughes(self, p, b, Wb, Hb, top):
        p.grad("rect", (0, 0, Wb, 16), "glass_lt", "glass_dk")
        for x in range(8, Wb, 8):
            p.rect(x - 0.25, 0, x + 0.25, 15, (238, 248, 255))
        p.glaze([(10, 0), (22, 0), (12, 15), (0, 15)], 70)
        p.glaze([(40, 0), (46, 0), (36, 15), (30, 15)], 55)
        self._wall(p, 0, 16, Wb, Hb)
        p.rect(0, 15.5, Wb, 18, "trim")
        p.rect(0, 18, Wb, 18.8, "trim_sh")
        for r in range(4):
            for c in range(6):
                if r == 3 and c in (2, 3):
                    continue
                cxw = 5 + c * (Wb - 10) / 5
                self._window(p, cxw - 3, 22 + r * 14.5, 6, 9 if r < 3 else 8)
        p.grad("rect", (Wb / 2 - 11, Hb - 18.5, Wb / 2 + 11, Hb - 14.5), "glass_lt", "glass", r=1.2)
        p.grad("rect", (Wb / 2 - 7, Hb - 14, Wb / 2 + 7, Hb), "glass", "glass_dk")
        p.rect(Wb / 2 - 0.3, Hb - 14, Wb / 2 + 0.3, Hb, "glass_dk")
        p.glaze([(Wb / 2 - 6, Hb - 14), (Wb / 2 - 3, Hb - 14), (Wb / 2 - 6, Hb - 6)], 90)
        p.rect(Wb / 2 - 9, Hb - 1.6, Wb / 2 + 9, Hb, "stone_lt", r=0.6)
        self.labels.append((b["name"], b["x"] + b["w"] / 2, b["y"] + 1.25))

    def _b_dealy(self, p, b, Wb, Hb, top):
        R = b["roof"] * 16
        self._roof(p, 0, 0, Wb, R)
        p.grad("rect", (10, 0, Wb - 10, 7.5), "slate_lt", "slate", r=0)
        p.rect(10, 7.2, Wb - 10, 8, "slate_dk")
        p.poly([(0, R), (0, 0.5), (10, 0.5), (10, 8)], mix(C["slate_lt"], C["slate"], 0.3))
        p.poly([(Wb, R), (Wb, 0.5), (Wb - 10, 0.5), (Wb - 10, 8)], "slate_dk")
        for x in (9, 24, Wb - 33, Wb - 18):
            p.poly([(x - 1.5, R - 13), (x + 4.5, R - 18.5), (x + 10.5, R - 13)], "slate_dk")
            p.rect(x, R - 13, x + 9, R - 2.5, "trim", r=0.5)
            p.grad("rect", (x + 2, R - 11, x + 7, R - 4), "win_top", "win_bot", r=0.4)
        self._wall(p, 0, R, Wb, Hb, bands=False)
        p.rect(0, R - 0.5, Wb, R + 2, "trim")
        for r in range(2):
            for c in range(8):
                if c in (3, 4):
                    continue
                self._window(p, 4 + c * 11.5, R + 5 + r * 13, 6, 8, arched=False)
        px0, px1 = Wb / 2 - 13, Wb / 2 + 13
        p.grad("rect", (px0, R + 3, px1, Hb), "trim", "trim_sh")
        p.poly([(px0 - 2, R + 4), (Wb / 2, R - 3.5), (px1 + 2, R + 4)], "trim")
        p.poly([(px0 + 3, R + 3), (Wb / 2, R - 0.5), (px1 - 3, R + 3)], "trim_sh")
        for x in (px0 + 1, px0 + 5, px1 - 7, px1 - 3):
            p.grad("rect", (x, R + 5, x + 2.2, Hb - 1), "trim", "trim_sh", r=0.6, horizontal=True)
        p.grad("rect", (Wb / 2 - 5, Hb - 13, Wb / 2 + 5, Hb), "wood", "wood_dk")
        p.grad("oval", (Wb / 2 - 5, Hb - 18, Wb / 2 + 5, Hb - 8), "wood", "wood")
        p.rect(Wb / 2 - 0.3, Hb - 15, Wb / 2 + 0.3, Hb, "wood_dk")
        p.rect(px0 - 1, Hb - 1.6, px1 + 1, Hb, "stone_lt", r=0.5)
        self.labels.append((b["name"], b["x"] + b["w"] / 2, b["y"] + 1.3))

    def _b_cunniffe(self, p, b, Wb, Hb, top):
        R = top + b["roof"] * 16
        mid0, mid1 = Wb / 2 - 15, Wb / 2 + 15
        self._roof(p, 0, top + 4, mid0 + 2, R)
        self._roof(p, mid1 - 2, top + 4, Wb, R)
        p.grad("rect", (0, R, mid0, Hb + top), "pink", "pink_dk")
        p.grad("rect", (mid1, R, Wb, Hb + top), "pink", "pink_dk")
        for x in (3, 13, mid1 + 3, mid1 + 13):
            self._window(p, x, R + 4, 6, 9, arched=False)
            self._window(p, x, R + 18, 6, 9, arched=False)
        p.poly([(mid0 - 2, R), (mid0 + 6, top + 4), (mid1 - 6, top + 4), (mid1 + 2, R)], "slate")
        p.poly([(mid0 + 6, top + 4), (mid1 - 6, top + 4), (mid1 - 3, top + 9), (mid0 + 3, top + 9)], "slate_lt")
        p.poly([(Wb / 2 + 4, top + 4), (mid1 - 6, top + 4), (mid1 + 2, R), (Wb / 2 + 6, R)], "slate_dk")
        p.grad("rect", (Wb / 2 - 5, top - 4, Wb / 2 + 5, top + 8), "trim", "trim_sh", horizontal=True)
        p.grad("rect", (Wb / 2 - 3, top - 2, Wb / 2 + 1, top + 4), "glass", "glass_dk", r=1.5)
        p.poly([(Wb / 2 - 6.5, top - 4), (Wb / 2, top - 10.5), (Wb / 2 + 6.5, top - 4)], "slate_dk")
        p.rect(Wb / 2 - 0.4, top - 14, Wb / 2 + 0.4, top - 9, "bronze_lt")
        p.rect(Wb / 2 - 2, top - 12.6, Wb / 2 + 2, top - 11.8, "bronze_lt")
        p.grad("rect", (mid0, R, mid1, Hb + top), "cream", "cream_sh", horizontal=True)
        p.rect(mid0, R - 0.5, mid1, R + 2, "trim")
        for x in (mid0 + 3, mid1 - 9):
            self._window(p, x, R + 4, 6, 10, arched=False)
            self._window(p, x, R + 18, 6, 10, arched=False)
        p.grad("oval", (Wb / 2 - 4, Hb + top - 16, Wb / 2 + 4, Hb + top - 8), "glass", "glass_dk")
        p.grad("rect", (Wb / 2 - 4, Hb + top - 12, Wb / 2 + 4, Hb + top), "pants", "pants_sh")
        p.rect(Wb / 2 - 6, Hb + top - 17, Wb / 2 - 5, Hb + top, "trim")
        p.rect(Wb / 2 + 5, Hb + top - 17, Wb / 2 + 6, Hb + top, "trim")
        p.rect(mid0 - 1, Hb + top - 1.6, mid1 + 1, Hb + top, "stone_lt", r=0.5)
        self.labels.append((b["name"], b["x"] + b["w"] / 2, b["y"] + 2.1))

    def _b_collins(self, p, b, Wb, Hb, top):
        R = b["roof"] * 16
        self._roof(p, 0, 0, Wb, R)
        p.grad("rect", (0, R, Wb, Hb), "brick", "brick_dk")
        p.rect(0, R - 0.5, Wb, R + 2, "trim")
        p.grad("rect", (Wb / 2 - 12, R + 2, Wb / 2 + 12, Hb), "trim", "trim_sh")
        for x in (Wb / 2 - 11, Wb / 2 - 6, Wb / 2 + 3, Wb / 2 + 8):
            p.grad("rect", (x, R + 4, x + 3, Hb - 1), "trim", "trim_sh", r=0.6, horizontal=True)
        p.grad("rect", (Wb / 2 - 3, Hb - 12, Wb / 2 + 3, Hb), "wood", "wood_dk")
        p.grad("oval", (Wb / 2 - 3, Hb - 15, Wb / 2 + 3, Hb - 9), "wood", "wood")
        for x in (2, Wb - 8):
            self._window(p, x, R + 6, 6, 10, arched=False)
        self.labels.append((b["name"], b["x"] + b["w"] / 2, b["y"] + 4.15))

    # ------------------------------------------------------------------ people
    LOOKS = {
        "player": dict(skin="skin1", hair="hair_br", shirt="maroon", pants="pants", bag=True),
        "leader": dict(skin="skin2", hair="hair_bk", shirt="shirt_w", pants="khaki", lanyard=True),
        "student_blue": dict(skin="skin1", hair="hair_or", shirt="shirt_b", pants="pants"),
        "student_yellow": dict(skin="skin3", hair="hair_bk", shirt="shirt_y", pants="pants"),
        "staff": dict(skin="skin1", hair="hair_wh", shirt="blazer", pants="pants"),
    }

    def person(self, cx, cy, facing, look):
        L = self.LOOKS[look]
        p = SPen(16, 23)
        sk, hr, sh, pt = L["skin"], L["hair"], L["shirt"], L["pants"]
        shd = sh + "_sh" if sh + "_sh" in C else "maroon_dk"
        sh_lt = "maroon_lt" if sh == "maroon" else sh
        side = facing in ("left", "right")
        if not side:
            p.rect(5, 16.5, 7.6, 21.5, pt, r=1)
            p.rect(8.4, 16.5, 11, 21.5, pt + "_sh", r=1)
            p.rect(4.4, 20.2, 7.8, 22.6, "shoe", r=1.1)
            p.rect(8.2, 20.2, 11.6, 22.6, "shoe", r=1.1)
            p.grad("rect", (2.4, 12, 4.8, 18), sh_lt, shd, r=1.2)
            p.grad("rect", (11.2, 12, 13.6, 18), shd, shd, r=1.2)
            p.oval(2.4, 16.6, 4.8, 19, sk)
            p.oval(11.2, 16.6, 13.6, 19, sk + "_sh")
            p.grad("rect", (4, 11.2, 12, 18.2), sh_lt, shd, r=2.6, horizontal=True)
        else:
            p.rect(5.6, 16.5, 9.4, 21.5, pt, r=1.2)
            p.rect(4, 20.2, 8.4, 22.6, "shoe", r=1.1)
            p.rect(7.4, 20.6, 10.8, 22.6, "shoe", r=1.1)
            if L.get("bag"):
                p.grad("rect", (8.6, 11.8, 12.8, 17.4), "bag", darker(C["bag"], 0.75), r=1.4)
            p.grad("rect", (4.4, 11.2, 10.6, 18.2), sh_lt, shd, r=2.6, horizontal=True)
            p.grad("rect", (5.8, 12.4, 8.2, 17.2), shd, shd, r=1.2)
            p.oval(5.8, 16, 8.2, 18.4, sk)
        if L.get("bag") and facing == "down":
            p.rect(4.6, 11.4, 5.6, 16, "bag", r=0.4)
            p.rect(10.4, 11.4, 11.4, 16, "bag", r=0.4)
        if L.get("lanyard"):
            if facing == "down":
                p.line(6.5, 11.5, 8, 14.5, "maroon", 0.8)
                p.line(9.5, 11.5, 8, 14.5, "maroon", 0.8)
                p.rect(6.6, 14.4, 9.4, 16.6, (255, 255, 255), r=0.5)
            elif side:
                p.line(5.5, 11.6, 5.6, 14.6, "maroon", 0.8)
                p.rect(4.4, 14.4, 6.8, 16.6, (255, 255, 255), r=0.5)
        # head
        p.ball(2.4, 0.4, 13.6, 12, sk, sk, sk + "_sh")
        hl = hr + "_lt"
        if facing == "down":
            p.ball(1.8, -0.2, 14.2, 8.4, hl, hr, darker(C[hr], 0.8))
            p.rect(1.8, 3.4, 3.6, 9.4, hr, r=0.9)
            p.rect(12.4, 3.4, 14.2, 9.4, darker(C[hr], 0.85), r=0.9)
            p.poly([(3.2, 4.4), (12.8, 4.4), (12.4, 6.6), (8, 6.0), (6, 6.8), (3.6, 6.4)], hr)
            for ex in (5.4, 10.6):
                p.oval(ex - 0.9, 7.2, ex + 0.9, 9.8, "eye")
                p.oval(ex - 0.5, 7.5, ex + 0.1, 8.2, (255, 255, 255))
            p.oval(3.6, 9.6, 5.4, 10.6, (240, 150, 140, 255))
            p.oval(10.6, 9.6, 12.4, 10.6, (240, 150, 140, 255))
        elif facing == "up":
            p.ball(1.8, -0.2, 14.2, 12.2, hl, hr, darker(C[hr], 0.8))
        else:
            p.ball(1.8, -0.2, 14.2, 8.4, hl, hr, darker(C[hr], 0.8))
            p.grad("rect", (7.4, 2.4, 14.2, 10.8), hr, darker(C[hr], 0.8), r=2.4, horizontal=True)
            p.poly([(2.4, 4.4), (7.6, 4.0), (6.4, 6.2), (2.8, 6.4)], hr)
            p.oval(3.4, 7.2, 5.2, 9.8, "eye")
            p.oval(3.7, 7.5, 4.3, 8.2, (255, 255, 255))
            p.oval(8.4, 6.6, 10.4, 9.2, sk)
            p.oval(3.0, 9.6, 4.8, 10.6, (240, 150, 140, 255))
        img, n = padded(p.img)
        img = soft_outline(img, C["ink"], 0.55, 190)
        if facing == "right":
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        self.shade("oval", (2.5, 13, 14.5, 17), (cx, cy))
        self.paste(img, self.X(cx), self.Y(cy) - 7 * F, n)

    # ----------------------------------------------------------------- compose
    def render(self):
        self.ground()
        items = []
        for b in S.BUILDINGS:
            items.append((b["y"] + b["h"], 0, lambda b=b: self.building(b)))
        for x, y in S.TREES:
            items.append((y + 1, 1, lambda x=x, y=y: self.tree(x, y)))
        for x, y in S.BENCHES:
            items.append((y + 0.8, 1, lambda x=x, y=y: self.bench(x, y)))
        for x, y in S.SIGNS:
            items.append((y + 0.9, 1, lambda x=x, y=y: self.signpost(x, y)))
        for x, y in S.SHUTTLE_SIGNS:
            items.append((y + 0.9, 1, lambda x=x, y=y: self.signpost(x, y, True)))
        for x, y in S.STATUES:
            items.append((y + 0.9, 1, lambda x=x, y=y: self.statue(x, y)))
        rx, ry = S.RAM_STATUE
        items.append((ry + 0.9, 1, lambda: self.ram(rx, ry)))
        fx, fy = S.FOUNTAIN
        items.append((fy + 2, 1, lambda: self.fountain(fx, fy)))
        for x, y, f, look in [S.PLAYER] + S.PEOPLE:
            items.append((y + 1, 2, lambda x=x, y=y, f=f, look=look: self.person(x, y, f, look)))
        items.sort(key=lambda t: (t[0], t[1]))
        ground = self.img.copy()
        for _, _, fn in items:          # pass 1: collect shadows
            fn()
        self.img = ground
        self.apply_shadow()
        self.adding_shadows = False
        self.labels = []
        for _, _, fn in items:          # pass 2: draw
            fn()
        return self.img


# --------------------------------------------------------------------------
# Screen furniture, drawn at hi-res too, then everything is scaled down.

def _shadowed(base, box, r, blur=10, offset=(0, 8), alpha=70):
    sh = Image.new("L", base.size, 0)
    x0, y0, x1, y1 = box
    ImageDraw.Draw(sh).rounded_rectangle([x0 + offset[0], y0 + offset[1], x1 + offset[0], y1 + offset[1]], radius=r, fill=alpha)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    dark = Image.new("RGBA", base.size, (30, 26, 50, 0))
    dark.putalpha(sh)
    base.alpha_composite(dark)


def wrap_px(text, f, max_w):
    out, line = [], ""
    for w in text.split():
        t = (line + " " + w) if line else w
        if f.getlength(t) > max_w and line:
            out.append(line)
            line = w
        else:
            line = t
    return out + [line]


def furniture(img, labels, dialogue=True):
    Z = 2                     # hi-res px per final screen px
    d = ImageDraw.Draw(img)
    box_top = (576 - 8 - 136) * Z
    # plaques: white rounded labels with a soft shadow
    fb = ImageFont.truetype(ROUND_BOLD, 15 * Z)
    for text, cx, top in labels:
        X = (cx - S.CAM[0]) * 32 * Z
        Y = (top - S.CAM[1]) * 32 * Z
        w = fb.getlength(text) + 16 * Z
        h = 21 * Z
        if dialogue and Y + h > box_top - 30 * Z:
            continue
        if Y < 60 * Z and X - w / 2 < 280 * Z:
            continue
        box = (X - w / 2, Y, X + w / 2, Y + h)
        _shadowed(img, box, h / 2, blur=4 * Z, offset=(0, 2 * Z), alpha=90)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle(box, radius=h / 2, fill=(255, 255, 255))
        d.text((X, Y + h / 2), text, font=fb, fill=C["ink"], anchor="mm")
    # area banner: maroon pill with a location pin
    f = ImageFont.truetype(ROUND_BOLD, 26 * Z)
    tw = f.getlength(S.AREA)
    box = (12 * Z, 12 * Z, 12 * Z + tw + 64 * Z, 12 * Z + 44 * Z)
    _shadowed(img, box, 22 * Z, blur=8 * Z, offset=(0, 4 * Z), alpha=110)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=22 * Z, fill=C["maroon"])
    px, py = box[0] + 24 * Z, box[1] + 22 * Z
    d.ellipse([px - 8 * Z, py - 12 * Z, px + 8 * Z, py + 4 * Z], fill=(255, 255, 255))
    d.polygon([(px - 7 * Z, py - 1 * Z), (px + 7 * Z, py - 1 * Z), (px, py + 11 * Z)], fill=(255, 255, 255))
    d.ellipse([px - 3.5 * Z, py - 7.5 * Z, px + 3.5 * Z, py - 0.5 * Z], fill=C["maroon"])
    d.text((box[0] + 42 * Z, py), S.AREA, font=f, fill=(255, 255, 255), anchor="lm")
    if not dialogue:
        return img
    # dialogue card
    box = (10 * Z, box_top, 758 * Z, (576 - 10) * Z)
    _shadowed(img, box, 22 * Z, blur=12 * Z, offset=(0, 6 * Z), alpha=120)
    card = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle(box, radius=22 * Z, fill=(255, 255, 255, 246), outline=(222, 220, 232, 255), width=Z)
    img.alpha_composite(card)
    d = ImageDraw.Draw(img)
    fn = ImageFont.truetype(ROUND_BOLD, 22 * Z)
    nw = fn.getlength(S.SPEAKER) + 36 * Z
    nb = (box[0] + 22 * Z, box[1] - 20 * Z, box[0] + 22 * Z + nw, box[1] + 16 * Z)
    _shadowed(img, nb, 18 * Z, blur=4 * Z, offset=(0, 2 * Z), alpha=90)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(nb, radius=18 * Z, fill=C["maroon"])
    d.text(((nb[0] + nb[2]) / 2, (nb[1] + nb[3]) / 2), S.SPEAKER, font=fn, fill=(255, 255, 255), anchor="mm")
    ft = ImageFont.truetype(ROUND_MED, 29 * Z)
    lines = wrap_px(S.LINE, ft, (box[2] - box[0]) - 64 * Z)
    for i, ln in enumerate(lines):
        d.text((box[0] + 30 * Z, box[1] + 30 * Z + i * 38 * Z), ln, font=ft, fill=C["ink"], anchor="lt")
    ax, ay = box[2] - 38 * Z, box[3] - 30 * Z
    d.ellipse([ax - 13 * Z, ay - 13 * Z, ax + 13 * Z, ay + 13 * Z], fill=C["maroon"])
    d.polygon([(ax - 6 * Z, ay - 3 * Z), (ax + 6 * Z, ay - 3 * Z), (ax, ay + 5 * Z)], fill=(255, 255, 255))
    return img


def compose(dialogue=True):
    sc = SmoothScene()
    art = sc.render()
    art = furniture(art, sc.labels, dialogue)
    return art.convert("RGB").resize((768, 576), Image.LANCZOS)
