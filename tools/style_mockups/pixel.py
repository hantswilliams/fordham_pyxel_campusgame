"""Clean pixel-art renderer for the style mockups.

One art direction drawn at two densities:
  s = 1  ->  16 px tiles, shown doubled (Style A: today's pixel size, cleaned up)
  s = 2  ->  32 px tiles, shown 1:1    (Style B: twice the detail, half-size pixels)

Everything is drawn in "units" (layout pixels, 16 per map cell) and rendered
at s pixels per unit with no anti-aliasing, so it stays true pixel art.
"""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import scene as S


def rgb(h):
    return ((h >> 16) & 255, (h >> 8) & 255, h & 255)


P = {k: rgb(v) for k, v in dict(
    # ground
    grass=0x8BC765, grass_alt=0x82BE5E, grass_tuft=0x6AA84E, grass_hi=0xA9DA7E,
    walk=0xEAD8B7, walk_edge=0xCDB690, walk_hi=0xF5E9D0,
    plaza=0xE6DFD2, plaza_alt=0xDCD4C5, plaza_grout=0xC4BBAB, plaza_hi=0xF2EDE4,
    road=0x80838B, road_dk=0x6A6D75, curb=0xCED1D6, curb_dk=0x5C5F67, stripe=0xF2F2EE,
    soil=0x7A5A3C,
    # trees
    leaf_out=0x23502D, leaf_dk=0x2F6B36, leaf=0x438A3F, leaf_lt=0x5FA64A, leaf_hi=0x88C55C,
    trunk=0x6E4A2E, trunk_dk=0x4D3220,
    # buildings
    out=0x2B2A35,
    fs=0x5E5D68, fs_lt=0x74737E, fs_dk=0x4A4954, fs_mortar=0x41404A,
    trim=0xF3F1EA, trim_sh=0xCFCBC0,
    slate=0x737A86, slate_lt=0x8E95A1, slate_dk=0x5A606B, slate_hi=0xA9AFB9,
    glass_hi=0xD9EEFF, glass=0x9CCBF2, glass_md=0x6FA3DA, glass_dk=0x46699F,
    win=0x30395A, win_lt=0x55689A, win_hi=0x8EA3D1,
    pink=0xC98A7C, pink_dk=0xA5675E, pink_lt=0xDCA597,
    cream=0xF1EBDC, cream_sh=0xD8CEBA,
    brick=0xA85A47, brick_dk=0x854232, brick_lt=0xC07360,
    wood=0x8F563B, wood_dk=0x663B27, wood_lt=0xB07650,
    maroon=0x860038, maroon_dk=0x5C0026, maroon_lt=0xAD3563,
    bronze=0x5D5148, bronze_lt=0x857566, bronze_dk=0x3E352F,
    water=0x7CB6E8, water_dk=0x5A92CF, water_hi=0xCDE8FF,
    stone=0xC9C2B5, stone_lt=0xE2DCD1, stone_dk=0x9E9688,
    signbd=0xF6F4EE, post=0x6B6E78, post_dk=0x4D5058,
    # people
    skin1=0xF6CDB0, skin1_sh=0xDDA88A, skin2=0xC68B62, skin2_sh=0xA16C48,
    skin3=0x8A5A3C, skin3_sh=0x6C432B,
    hair_br=0x6B4329, hair_br_sh=0x4C2E1C, hair_br_lt=0x94633F, hair_bk=0x2E2A30, hair_bk_sh=0x1C191E, hair_bk_lt=0x4F4B5E,
    hair_or=0xD9823F, hair_or_sh=0xA95F2A, hair_or_lt=0xF0A866, hair_wh=0xE4E1DA, hair_wh_sh=0xB7B3AA, hair_wh_lt=0xFAF9F5,
    shirt_w=0xF7F6F2, shirt_w_sh=0xD3D0C8, shirt_b=0x8FB8EA, shirt_b_sh=0x6C93C9,
    shirt_y=0xF0C95A, shirt_y_sh=0xCFA23C, blazer=0x5B6274, blazer_sh=0x434958,
    pants=0x34406A, pants_sh=0x252E50, khaki=0xC9B48A, khaki_sh=0xA8935F,
    shoe=0x2A2A33, eye=0x1E1C26, bag=0x3C4A7A,
).items()}

SHADOW_TINT = (0.70, 0.73, 0.86)   # ground under a shadow: a darker, cooler shade


def h32(*a):
    """Small deterministic hash -> [0, 1)."""
    x = 2166136261
    for v in a:
        x = ((x ^ (int(v) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    x ^= x >> 13
    x = (x * 0x5BD1E995) & 0xFFFFFFFF
    x ^= x >> 15
    return x / 2**32


class Pen:
    """Draws in units onto an RGBA image at s pixels per unit, no anti-aliasing."""

    def __init__(self, w_units, h_units, s):
        self.s = s
        self.img = Image.new("RGBA", (round(w_units * s), round(h_units * s)), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def _b(self, x0, y0, x1, y1):
        s = self.s
        return [round(x0 * s), round(y0 * s), round(x1 * s) - 1, round(y1 * s) - 1]

    def rect(self, x0, y0, x1, y1, c):
        b = self._b(x0, y0, x1, y1)
        if b[2] >= b[0] and b[3] >= b[1]:
            self.d.rectangle(b, fill=P[c] if isinstance(c, str) else c)

    def oval(self, x0, y0, x1, y1, c):
        b = self._b(x0, y0, x1, y1)
        if b[2] >= b[0] and b[3] >= b[1]:
            self.d.ellipse(b, fill=P[c] if isinstance(c, str) else c)

    def rrect(self, x0, y0, x1, y1, r, c):
        b = self._b(x0, y0, x1, y1)
        if b[2] >= b[0] and b[3] >= b[1]:
            self.d.rounded_rectangle(b, radius=max(0, round(r * self.s)), fill=P[c] if isinstance(c, str) else c)

    def poly(self, pts, c):
        self.d.polygon([(round(x * self.s), round(y * self.s)) for x, y in pts],
                       fill=P[c] if isinstance(c, str) else c)

    def px(self, x, y, c, w=1, h=1):
        """A block of whole *pixels* at unit position (x, y)."""
        X, Y = round(x * self.s), round(y * self.s)
        self.d.rectangle([X, Y, X + w - 1, Y + h - 1], fill=P[c] if isinstance(c, str) else c)


def outline(img, color=None, darken=0.5, diagonal=False):
    """Selective outline: every empty pixel touching a filled one gets that
    neighbour's colour darkened (or a fixed colour)."""
    a = np.array(img)
    alpha = a[..., 3] > 0
    out = a.copy()
    shifts = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    if diagonal:
        shifts += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    edge = np.zeros_like(alpha)
    for dy, dx in shifts:
        nb = np.roll(np.roll(alpha, dy, 0), dx, 1)
        rgbn = np.roll(np.roll(a, dy, 0), dx, 1)
        new = nb & ~alpha & ~edge
        if color is None:
            out[new, :3] = (rgbn[new, :3] * darken).astype(np.uint8)
        else:
            out[new, :3] = color
        out[new, 3] = 255
        edge |= new
    return Image.fromarray(out)


def pad(img, n):
    out = Image.new("RGBA", (img.width + 2 * n, img.height + 2 * n), (0, 0, 0, 0))
    out.paste(img, (n, n))
    return out


# ----------------------------------------------------------------------------

class PixelScene:
    def __init__(self, s):
        self.s = s
        self.T = 16 * s
        self.W, self.H = 384 * s, 288 * s
        self.img = Image.new("RGBA", (self.W, self.H), P["grass"] + (255,))
        self.shadow = Image.new("L", (self.W, self.H), 0)
        self.labels = []   # (text, cx, top, kind) in screen units, drawn crisp later

    # map cell -> pixel in this image
    def X(self, cx):
        return round((cx - S.CAM[0]) * self.T)

    def Y(self, cy):
        return round((cy - S.CAM[1]) * self.T)

    # ------------------------------------------------------------------ ground
    def ground(self):
        s, T = self.s, self.T
        x0, y0 = math.floor(S.CAM[0]) - 1, math.floor(S.CAM[1]) - 1
        nx, ny = S.VIEW_W + 3, S.VIEW_H + 3
        kinds = ["grass", "walk", "plaza", "road", "xwalk_v", "xwalk_h", "flowers"]
        grid = np.zeros((ny, nx), np.uint8)
        for j in range(ny):
            for i in range(nx):
                grid[j, i] = kinds.index(S.ground(x0 + i, y0 + j))
        mat = np.kron(grid, np.ones((T, T), np.uint8))
        ox, oy = self.X(x0), self.Y(y0)
        Hh, Ww = mat.shape

        # round the corners where paving meets lawn
        paved = (mat >= 1) & (mat <= 5)
        m = Image.fromarray((paved * 255).astype(np.uint8))
        r = 2.4 * s
        m = np.array(m.filter(ImageFilter.GaussianBlur(r))) >= 128
        lawn_kind = np.where(mat == 6, 6, 0)
        # cells that became paved take "walk"; cells that became lawn take grass/flowers
        mat = np.where(m & ~paved, 1, mat)
        mat = np.where(~m & paved, lawn_kind, mat)

        yy, xx = np.mgrid[0:Hh, 0:Ww]
        U = s  # pixels per unit
        out = np.zeros((Hh, Ww, 3), np.uint8)

        def put(mask, c):
            out[mask] = P[c]

        # lawn: soft patches + tufts
        lawn = (mat == 0) | (mat == 6)
        put(lawn, "grass")
        # low-frequency patches
        ux, uy = (xx + ox) / (U * 16.0), (yy + oy) / (U * 16.0)
        n = (np.sin(ux * 1.7 + np.sin(uy * 1.3) * 1.5) + np.sin(uy * 2.1 + ux * 0.6)) * 0.5
        put(lawn & (n > 0.45), "grass_alt")
        # tufts: little "v"s on a jittered grid, 3 per cell
        tuft = np.zeros_like(lawn)
        for j in range(ny):
            for i in range(nx):
                for k in range(3):
                    hx, hy = h32(x0 + i, y0 + j, k, 1), h32(x0 + i, y0 + j, k, 2)
                    px_, py_ = int((i * 16 + 2 + hx * 11) * U), int((j * 16 + 3 + hy * 10) * U)
                    pts = [(0, 0), (2, 0), (1, -1)] if s == 1 else \
                          [(0, 0), (1, 1), (2, 1), (3, 1), (4, 0), (1, 0), (3, 0), (2, -1), (2, 0), (0, -1), (4, -1)]
                    for dx, dy in pts:
                        X_, Y_ = px_ + dx, py_ + dy + (2 if s == 2 else 1)
                        if 0 <= X_ < Ww and 0 <= Y_ < Hh:
                            tuft[Y_, X_] = True
        put(lawn & tuft, "grass_tuft")

        # walkway: fill, then a 1-unit darker lip against the lawn
        walk = mat == 1
        put(walk, "walk")
        lawnb = Image.fromarray((lawn * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * U + 1))
        near_lawn = np.array(lawnb) > 0
        put(walk & near_lawn, "walk_edge")

        # plaza: square pavers, 8 units, running bond
        plaza = mat == 2
        put(plaza, "plaza")
        uxp, uyp = (xx + ox) // U, (yy + oy) // U
        row = uyp // 8
        colp = (uxp + (row % 2) * 4) // 8
        alt = np.vectorize(lambda a, b: h32(a, b, 7) < 0.3)(colp, row) if False else \
            ((colp * 7 + row * 13) % 5 == 0)
        put(plaza & alt, "plaza_alt")
        grout = ((uyp % 8) == 7) | (((uxp + (row % 2) * 4) % 8) == 7)
        if s == 2:
            grout_px = (((yy + oy) % (8 * U)) == 8 * U - 1) | ((((xx + ox) + (row % 2) * 4 * U) % (8 * U)) == 8 * U - 1)
            put(plaza & grout_px, "plaza_grout")
            hi = (((yy + oy) % (8 * U)) == 0) | ((((xx + ox) + (row % 2) * 4 * U) % (8 * U)) == 0)
            put(plaza & hi & ~grout_px, "plaza_hi")
        else:
            put(plaza & grout, "plaza_grout")
        put(plaza & near_lawn, "walk_edge")

        # road + curbs
        road = (mat >= 3) & (mat <= 5)
        put(road, "road")
        # sparse fine grain (very low contrast)
        grain = ((xx * 73 + yy * 151 + (xx * yy) % 97) % 61) == 0
        put(road & grain, "road_dk")
        notroad = Image.fromarray(((~road) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * U + 1))
        put(road & (np.array(notroad) > 0), "curb_dk")
        roadb = np.array(Image.fromarray((road * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(4 * U + 1))) > 0
        put(~road & roadb & (walk | plaza), "curb")
        # crosswalk stripes
        lx, ly = (xx + ox) % (16 * U), (yy + oy) % (16 * U)
        xv = (mat == 4) & ((lx // U) % 6 >= 2) & ((lx // U) % 6 < 5)
        xh = (mat == 5) & ((ly // U) % 6 >= 2) & ((ly // U) % 6 < 5)
        put(xv | xh, "stripe")

        img = Image.fromarray(out).convert("RGBA")
        self.img.paste(img, (ox, oy))

        # flower beds on '*' cells (drawn as sprites so they sit on the lawn)
        for j in range(ny):
            for i in range(nx):
                if S.cell(x0 + i, y0 + j) == "*":
                    self.flowers(x0 + i, y0 + j)

    def flowers(self, cx, cy):
        p = Pen(16, 16, self.s)
        cols = [("maroon_lt", "trim"), ("shirt_y", "trim"), ("trim", "shirt_y"), ("pink_lt", "trim")]
        spots = [(3, 3), (10, 2), (6, 8), (13, 9), (2, 12), (9, 13)]
        for k, (x, y) in enumerate(spots):
            petal, mid = cols[int(h32(cx, cy, k) * 4)]
            p.rect(x, y + 2, x + 1, y + 4, "leaf")
            if self.s == 2:
                p.rect(x - 1, y, x + 2, y + 2, petal)
                p.rect(x - 0.5, y - 0.5, x + 1.5, y + 2.5, petal)
                p.px(x, y + 0.5, mid, 2, 2)
            else:
                p.rect(x - 1, y, x + 2, y + 2, petal)
                p.px(x, y, mid)
        self.paste(p.img, self.X(cx), self.Y(cy))

    # ----------------------------------------------------------------- helpers
    def paste(self, sprite, x, y):
        self.img.alpha_composite(sprite, (int(x), int(y))) if x >= 0 and y >= 0 else self._paste_clip(sprite, x, y)

    def _paste_clip(self, sprite, x, y):
        x, y = int(x), int(y)
        cx0, cy0 = max(0, -x), max(0, -y)
        if cx0 >= sprite.width or cy0 >= sprite.height:
            return
        crop = sprite.crop((cx0, cy0, sprite.width, sprite.height))
        self.img.alpha_composite(crop, (x + cx0, y + cy0))

    def shade(self, shape, pts_units, origin_cell):
        """Add a shadow shape (ellipse box or polygon, in units relative to a cell)."""
        d = ImageDraw.Draw(self.shadow)
        ox, oy = self.X(origin_cell[0]), self.Y(origin_cell[1])
        s = self.s
        if shape == "oval":
            x0, y0, x1, y1 = pts_units
            d.ellipse([ox + x0 * s, oy + y0 * s, ox + x1 * s - 1, oy + y1 * s - 1], fill=255)
        else:
            d.polygon([(ox + x * s, oy + y * s) for x, y in pts_units], fill=255)

    def apply_shadow(self):
        a = np.array(self.img).astype(np.float32)
        m = np.array(self.shadow) > 0
        for k in range(3):
            a[..., k] = np.where(m, a[..., k] * SHADOW_TINT[k], a[..., k])
        self.img = Image.fromarray(a.astype(np.uint8))
        self.shadow = Image.new("L", (self.W, self.H), 0)

    # ------------------------------------------------------------------- trees
    def tree(self, cx, cy):
        img = self.tree_sprite()
        self.shade("oval", (-2, 9, 22, 18), (cx, cy))
        self.paste(img, self.X(cx) - 5 * self.s - 1, self.Y(cy) - 14 * self.s - 1)

    def tree_sprite(self):
        p = Pen(26, 30, self.s)
        # trunk
        p.rect(11, 19, 15, 28, "trunk")
        p.rect(13.5, 19, 15, 28, "trunk_dk")
        lumps = [(13, 12, 10), (7, 15, 6), (19, 15, 6), (13, 6, 7), (8, 9, 6), (18, 9, 6)]
        for x, y, r in lumps:
            p.oval(x - r, y - r, x + r, y + r, "leaf_dk")
        for x, y, r in lumps:
            rr = r * 0.82
            p.oval(x - rr - r * 0.12, y - rr - r * 0.16, x + rr - r * 0.12, y + rr - r * 0.16, "leaf")
        for x, y, r in lumps:
            rr = r * 0.5
            p.oval(x - rr - r * 0.3, y - rr - r * 0.36, x + rr - r * 0.3, y + rr - r * 0.36, "leaf_lt")
        for x, y, r in lumps[3:]:
            rr = r * 0.22
            p.oval(x - rr - r * 0.42, y - rr - r * 0.5, x + rr - r * 0.42, y + rr - r * 0.5, "leaf_hi")
        return outline(p.img, P["leaf_out"])

    # ---------------------------------------------------------------- objects
    def bench(self, cx, cy):
        p = Pen(16, 16, self.s)
        p.rect(1, 6, 15, 8, "wood_dk")
        p.rect(1, 5, 15, 7, "wood_lt")
        p.rect(1, 9, 15, 11, "wood")
        p.rect(1, 10, 15, 11, "wood_dk") if self.s == 2 else None
        p.rect(2, 11, 3, 14, "post_dk")
        p.rect(13, 11, 14, 14, "post_dk")
        img = outline(p.img, P["out"])
        self.shade("oval", (1, 11, 17, 16), (cx, cy))
        self.paste(img, self.X(cx) - 1, self.Y(cy) - 1)

    def signpost(self, cx, cy, maroon=False):
        p = Pen(16, 22, self.s)
        p.rect(7, 13, 9, 21, "post")
        p.rect(8, 13, 9, 21, "post_dk")
        if maroon:
            p.rrect(2, 4, 14, 14, 1.5, "maroon")
            p.rect(3, 5, 13, 6, "maroon_lt")
            # little bus
            p.rect(4.5, 7, 11.5, 11.5, "trim")
            p.rect(5.5, 8, 10.5, 9.5, "maroon")
            p.rect(5, 11.5, 6.5, 12.5, "trim")
            p.rect(9.5, 11.5, 11, 12.5, "trim")
        else:
            p.rrect(2, 5, 14, 14, 1, "signbd")
            p.rect(2, 12.5, 14, 14, "trim_sh")
            for k, y in enumerate((7, 9, 11) if self.s == 2 else (7, 9.5)):
                p.rect(4, y, 12 - (k == 2) * 3, y + (0.5 if self.s == 2 else 1), "post")
        img = outline(p.img, P["out"])
        self.shade("oval", (4, 12.5, 15, 17), (cx, cy))
        self.paste(img, self.X(cx) - 1, self.Y(cy) - 6 * self.s - 1)

    def statue(self, cx, cy):
        p = Pen(16, 26, self.s)
        p.rect(3, 17, 13, 24, "stone")
        p.rect(3, 17, 13, 18.5, "stone_lt")
        p.rect(10.5, 18.5, 13, 24, "stone_dk")
        p.rect(4.5, 15.5, 11.5, 17, "stone_dk")
        # bronze figure
        p.oval(6, 2, 10, 6, "bronze")
        p.rrect(5, 6, 11, 15.5, 1.5, "bronze")
        p.rect(4, 7, 5.5, 12, "bronze")
        p.rect(9, 6.5, 11, 15.5, "bronze_dk")
        p.rect(6, 2.5, 7.5, 4, "bronze_lt")
        p.rect(5.5, 7, 6.5, 13, "bronze_lt")
        img = outline(p.img, P["out"])
        self.shade("oval", (3, 19, 18, 26), (cx, cy - 0.5))
        self.paste(img, self.X(cx) - 1, self.Y(cy) - 9 * self.s - 1)

    def fountain(self, cx, cy):
        s = self.s
        p = Pen(36, 46, s)
        # basin: stone rim ellipse, water inside
        p.oval(1, 18, 35, 44, "stone_dk")
        p.oval(1, 17, 35, 42, "stone")
        p.oval(2, 17, 34, 39, "stone_lt")
        p.oval(4, 20, 32, 40, "water_dk")
        p.oval(4, 20, 32, 38, "water")
        # ripples
        for k, (x, y, w) in enumerate([(8, 27, 5), (22, 25, 6), (11, 33, 7), (24, 32, 4)]):
            p.rect(x, y, x + w, y + (0.5 if s == 2 else 1), "water_hi")
        # pedestal + tiers (bronze)
        p.rect(15, 14, 21, 31, "bronze")
        p.rect(18.5, 14, 21, 31, "bronze_dk")
        p.oval(9, 22, 27, 28, "bronze_dk")
        p.oval(9, 21, 27, 26, "bronze")
        p.oval(11, 21.5, 25, 24.5, "water")
        p.oval(13, 11, 23, 15, "bronze_dk")
        p.oval(13, 10, 23, 14, "bronze")
        p.oval(14.5, 10.5, 21.5, 12.5, "water")
        p.rect(16.5, 4, 19.5, 11, "bronze")
        p.rect(16.5, 4, 17.5, 11, "bronze_lt")
        # spray
        for x, y in [(18, 1), (15, 3), (21, 3), (13, 6), (23, 6), (12, 9), (24, 9)]:
            p.rect(x - 0.5, y, x + 0.5 + (0.5 if s == 1 else 0), y + 1.5, "water_hi")
        p.rect(17, 0, 19, 4, "water_hi")
        for x in (10, 13, 23, 26):
            p.rect(x, 25, x + 1, 27 + (x % 3), "water_hi")
        img = outline(p.img, P["out"])
        self.shade("oval", (3, 19, 39, 47), (cx, cy - 1))
        self.paste(img, self.X(cx) - s, self.Y(cy) - 14 * s - s)

    # -------------------------------------------------------------- buildings
    def building_sprite(self, b):
        s = self.s
        W, H = b["w"] * 16, b["h"] * 16
        top = 14 if b["kind"] == "cunniffe" else 0
        p = Pen(W, H + top, s)
        getattr(self, "_b_" + b["kind"])(p, b, W, H, top)
        return outline(pad(p.img, s), P["out"])

    def building(self, b):
        s = self.s
        W, H = b["w"] * 16, b["h"] * 16
        top = 14 if b["kind"] == "cunniffe" else 0
        img = self.building_sprite(b)
        # drop shadow: right side and a little below
        x, y = b["x"], b["y"]
        self.shade("poly", [(W, 3), (W + 6, 7), (W + 6, H + 3), (6, H + 3), (2, H), (W, H)], (x, y))
        self.paste(img, self.X(x) - s, self.Y(y) - top * s - s)

    def _roof(self, p, x0, y0, x1, y1, kind="slate"):
        s = self.s
        if kind == "glass":
            p.rect(x0, y0, x1, y1, "glass_md")
            p.rect(x0, y0, x1, y0 + 1, "glass_hi")
            step = 8
            x = x0 + 4
            while x < x1 - 2:
                p.rect(x, y0 + 1, x + 0.5 if s == 2 else x + 1, y1 - 1, "glass_dk")
                p.rect(x + (0.5 if s == 2 else 1), y0 + 1, x + (1 if s == 2 else 2), y1 - 1, "glass_hi") if s == 2 else None
                x += step
            p.rect(x0, y1 - 2, x1, y1, "slate_dk")
            return
        p.rect(x0, y0, x1, y1, "slate")
        # shingle courses
        y, k = y0 + 3, 0
        while y < y1 - 1:
            p.rect(x0, y, x1, y + (0.5 if s == 2 else 1), "slate_dk")
            if s == 2:
                off = 3 if k % 2 else 0
                xx = x0 + off
                while xx < x1:
                    p.rect(xx, y - 3, xx + 0.5, y, "slate_dk")
                    xx += 6
            y += 3.5 if s == 2 else 4
            k += 1
        p.rect(x0, y0, x1, y0 + 1.5, "slate_hi")
        p.rect(x0, y1 - 1.5, x1, y1, "slate_dk")

    def _stone_wall(self, p, x0, y0, x1, y1, base="fs"):
        s = self.s
        p.rect(x0, y0, x1, y1, base)
        if s == 1:
            # a regular, quiet block pattern
            for yy in range(int(y0) + 2, int(y1), 4):
                for xx in range(int(x0) + ((yy // 4) % 2) * 3, int(x1) - 1, 6):
                    p.rect(xx, yy, xx + 3, yy + 1, base + "_lt")
            return
        y, k = y0 + 0.5, 0
        while y < y1:
            x = x0 + (2.5 if k % 2 else 0)
            while x < x1:
                w = 4 + (h32(x * 3, y * 5, 3) > 0.5) * 2
                t = h32(x, y, 9)
                c = base + "_lt" if t < 0.33 else (base + "_dk" if t > 0.8 else base)
                p.rect(x + 0.5, y + 0.5, min(x + w, x1), min(y + 3, y1), c)
                x += w
            y += 3
            k += 1

    def _brick_wall(self, p, x0, y0, x1, y1, base):
        s = self.s
        p.rect(x0, y0, x1, y1, base)
        if s == 2:
            y, k = y0 + 1.5, 0
            while y < y1:
                p.rect(x0, y, x1, y + 0.5, base + "_dk")
                x = x0 + (2 if k % 2 else 0)
                while x < x1:
                    p.rect(x, y - 1.5, x + 0.5, y, base + "_dk")
                    x += 4
                y += 2
                k += 1
        else:
            for yy in range(int(y0) + 2, int(y1), 3):
                p.rect(x0, yy, x1, yy + 1, base + "_dk")

    def _window(self, p, x, y, w, h, kind="arched", frame="trim", glass="win"):
        s = self.s
        # frame
        if kind == "arched":
            p.rect(x - 1, y + w / 2, x + w + 1, y + h + 1, frame)
            p.oval(x - 1, y - 1, x + w + 1, y + w + 1, frame)
            p.rect(x, y + w / 2, x + w, y + h, glass)
            p.oval(x, y, x + w, y + w, glass)
        else:
            p.rect(x - 1, y - 1, x + w + 1, y + h + 1, frame)
            p.rect(x, y, x + w, y + h, glass)
        # sill
        p.rect(x - 1.5, y + h + 0.5, x + w + 1.5, y + h + 1.5, "trim_sh" if frame == "trim" else frame)
        # reflections + mullion
        g_lt = glass + "_lt" if glass + "_lt" in P else "glass"
        if s == 2:
            p.rect(x + w / 2 - 0.25, y + (w / 2 if kind == "arched" else 0), x + w / 2 + 0.25, y + h, frame)
            p.rect(x, y + h * 0.55, x + w, y + h * 0.55 + 0.5, frame)
            p.rect(x + 0.5, y + (w / 2 if kind == "arched" else 0.5), x + 1, y + h * 0.45, g_lt)
            p.px(x + 0.5, y + h - 1.5, "win_hi" if glass == "win" else "glass_hi")
        else:
            p.px(x, y + (w / 2 if kind == "arched" else 0), g_lt)

    def _b_hughes(self, p, b, W, H, top):
        s = self.s
        self._roof(p, 0, 0, W, 16, "glass")
        self._stone_wall(p, 0, 16, W, H)
        p.rect(0, 16, W, 18, "trim")              # cornice
        p.rect(0, 18, W, 18.5 if s == 2 else 19, "trim_sh")
        p.rect(0, 16, 2, H, "fs_lt")              # quoins
        p.rect(W - 2, 16, W, H, "fs_dk")
        cols = 6
        for r in range(4):
            for c in range(cols):
                cx = 5 + c * (W - 10) / (cols - 1)
                if r == 3 and c in (2, 3):
                    continue
                self._window(p, cx - 3, 22 + r * 14.5, 6, 9 if r < 3 else 8, "arched")
        # glass canopy entrance
        p.rect(W / 2 - 10, H - 18, W / 2 + 10, H - 15, "glass")
        p.rect(W / 2 - 10, H - 15, W / 2 + 10, H - 14, "glass_dk")
        p.rect(W / 2 - 7, H - 14, W / 2 + 7, H, "glass_md")
        p.rect(W / 2 - 0.5, H - 14, W / 2 + 0.5, H, "glass_dk")
        p.rect(W / 2 - 6, H - 13, W / 2 - 4, H - 2, "glass_hi")
        p.rect(W / 2 + 1, H - 13, W / 2 + 2, H - 2, "glass_hi")
        p.rect(W / 2 - 9, H - 1.5, W / 2 + 9, H, "stone_lt")
        self.labels.append((b["name"], b["x"] + b["w"] / 2, b["y"] + 1.25, "plaque"))

    def _b_dealy(self, p, b, W, H, top):
        s = self.s
        R = b["roof"] * 16
        self._roof(p, 0, 0, W, R)
        # hipped: a lighter back slope above the ridge, hips at both ends
        p.rect(10, 0, W - 10, 7, "slate_lt")
        p.rect(10, 0, W - 10, 1.5, "slate_hi")
        p.rect(10, 7, W - 10, 8, "slate_dk")
        p.poly([(0, R), (0, 1), (10, 1), (10, 8)], "slate_lt")
        p.poly([(W, R), (W, 1), (W - 10, 1), (W - 10, 8)], "slate_dk")
        # dormers with white frames, in pairs either side of the pediment
        for x in (9, 24, W - 33, W - 18):
            p.poly([(x - 1.5, R - 13), (x + 4.5, R - 18), (x + 10.5, R - 13)], "slate_dk")
            p.rect(x, R - 13, x + 9, R - 3, "trim")
            p.rect(x + 7, R - 13, x + 9, R - 3, "trim_sh")
            p.rect(x + 2, R - 11, x + 7, R - 4, "win")
            p.rect(x + 2, R - 11, x + 3, R - 7, "win_lt")
            p.rect(x - 1, R - 3, x + 10, R - 2, "slate_dk")
        self._stone_wall(p, 0, R, W, H)
        p.rect(0, R, W, R + 2, "trim")
        p.rect(0, R + 2, W, R + 2.5 if s == 2 else R + 3, "trim_sh")
        for r in range(2):
            for c in range(8):
                x = 4 + c * 11.5
                if c in (3, 4) and r == 1:
                    continue
                if c in (3, 4):
                    continue
                self._window(p, x, R + 5 + r * 13, 6, 8, "square")
        # white portico with an arched wooden door
        px0, px1 = W / 2 - 13, W / 2 + 13
        p.rect(px0, R + 3, px1, H, "trim")
        p.poly([(px0 - 2, R + 4), (W / 2, R - 3), (px1 + 2, R + 4)], "trim")
        p.poly([(px0 + 3, R + 3), (W / 2, R - 0.5), (px1 - 3, R + 3)], "trim_sh")
        for x in (px0 + 1, px0 + 5, px1 - 7, px1 - 3):
            p.rect(x, R + 5, x + 2, H - 1, "trim_sh" if s == 1 else "trim")
            if s == 2:
                p.rect(x + 1.5, R + 5, x + 2, H - 1, "trim_sh")
        p.rect(W / 2 - 5, H - 13, W / 2 + 5, H, "wood")
        p.oval(W / 2 - 5, H - 18, W / 2 + 5, H - 8, "wood")
        p.rect(W / 2 - 0.5, H - 15, W / 2 + 0.5, H, "wood_dk")
        p.rect(W / 2 - 4, H - 12, W / 2 - 3, H - 1, "wood_lt")
        p.rect(px0 - 1, H - 1.5, px1 + 1, H, "stone_lt")
        self.labels.append((b["name"], b["x"] + b["w"] / 2, b["y"] + 1.3, "plaque"))

    def _b_cunniffe(self, p, b, W, H, top):
        s = self.s
        R = top + b["roof"] * 16          # wall starts here
        mid0, mid1 = W / 2 - 15, W / 2 + 15
        # wings: slate roofs, pink brick
        self._roof(p, 0, top + 4, mid0 + 2, R)
        self._roof(p, mid1 - 2, top + 4, W, R)
        self._brick_wall(p, 0, R, mid0, H + top, "pink")
        self._brick_wall(p, mid1, R, W, H + top, "pink")
        for x in (3, 13, mid1 + 3, mid1 + 13):
            self._window(p, x, R + 4, 6, 9, "square", "trim", "win")
            self._window(p, x, R + 18, 6, 9, "square", "trim", "win")
        # centre block: cream, hipped roof, cupola
        p.poly([(mid0 - 2, R), (mid0 + 6, top + 4), (mid1 - 6, top + 4), (mid1 + 2, R)], "slate")
        p.poly([(mid0 + 6, top + 4), (mid1 - 6, top + 4), (mid1 - 3, top + 9), (mid0 + 3, top + 9)], "slate_hi")
        p.poly([(W / 2 + 4, top + 4), (mid1 - 6, top + 4), (mid1 + 2, R), (W / 2 + 6, R)], "slate_dk")
        # cupola
        p.rect(W / 2 - 5, top - 4, W / 2 + 5, top + 8, "trim")
        p.rect(W / 2 + 2, top - 4, W / 2 + 5, top + 8, "trim_sh")
        p.rect(W / 2 - 3, top - 2, W / 2 + 1, top + 4, "glass_md")
        p.poly([(W / 2 - 6, top - 4), (W / 2, top - 10), (W / 2 + 6, top - 4)], "slate_dk")
        p.rect(W / 2 - 0.5, top - 14, W / 2 + 0.5, top - 9, "bronze_lt")
        p.rect(W / 2 - 2, top - 12.5, W / 2 + 2, top - 12 + (0 if s == 2 else 0.5), "bronze_lt")
        p.rect(mid0, R, mid1, H + top, "cream")
        p.rect(mid1 - 3, R, mid1, H + top, "cream_sh")
        p.rect(mid0, R, mid1, R + 2, "trim")
        for x in (mid0 + 3, mid1 - 9):
            self._window(p, x, R + 4, 6, 10, "square", "trim", "win")
            self._window(p, x, R + 18, 6, 10, "square", "trim", "win")
        # door with fanlight
        p.rect(W / 2 - 4, H + top - 12, W / 2 + 4, H + top, "pants")
        p.oval(W / 2 - 4, H + top - 16, W / 2 + 4, H + top - 8, "glass_md")
        p.rect(W / 2 - 4, H + top - 12, W / 2 + 4, H + top, "pants")
        p.rect(W / 2 - 0.5, H + top - 12, W / 2 + 0.5, H + top, "pants_sh")
        p.rect(W / 2 - 6, H + top - 17, W / 2 - 5, H + top, "trim")
        p.rect(W / 2 + 5, H + top - 17, W / 2 + 6, H + top, "trim")
        p.rect(mid0 - 1, H + top - 1.5, mid1 + 1, H + top, "stone_lt")
        self.labels.append((b["name"], b["x"] + b["w"] / 2, b["y"] + 2.1, "plaque"))

    def _b_collins(self, p, b, W, H, top):
        R = b["roof"] * 16
        self._roof(p, 0, 0, W, R)
        self._brick_wall(p, 0, R, W, H, "brick")
        p.rect(0, R, W, R + 2, "trim")
        p.rect(W / 2 - 12, R + 2, W / 2 + 12, H, "trim")
        for x in (W / 2 - 11, W / 2 - 6, W / 2 + 3, W / 2 + 8):
            p.rect(x, R + 4, x + 3, H - 1, "trim_sh")
            p.rect(x, R + 4, x + 1.5, H - 1, "trim")
        p.rect(W / 2 - 3, H - 12, W / 2 + 3, H, "wood")
        p.oval(W / 2 - 3, H - 15, W / 2 + 3, H - 9, "wood")
        p.rect(W / 2 - 0.5, H - 12, W / 2 + 0.5, H, "wood_dk")
        for x in (2, W - 8):
            self._window(p, x, R + 6, 6, 10, "square")
        self.labels.append((b["name"], b["x"] + b["w"] / 2, b["y"] + 4.15, "plaque"))

    # ------------------------------------------------------------------ people
    LOOKS = {
        "player": dict(skin="skin1", hair="hair_br", shirt="maroon", pants="pants", bag=True),
        "leader": dict(skin="skin2", hair="hair_bk", shirt="shirt_w", pants="khaki", lanyard=True),
        "student_blue": dict(skin="skin1", hair="hair_or", shirt="shirt_b", pants="pants"),
        "student_yellow": dict(skin="skin3", hair="hair_bk", shirt="shirt_y", pants="pants"),
        "staff": dict(skin="skin1", hair="hair_wh", shirt="blazer", pants="pants"),
    }

    def person(self, cx, cy, facing, look):
        """A chibi figure 22 units tall: feet on the cell's bottom, head
        rising 7 units into the cell above (GBA proportions)."""
        L = self.LOOKS[look]
        s = self.s
        p = Pen(16, 23, s)
        sk, hr, sh, pt = L["skin"], L["hair"], L["shirt"], L["pants"]
        shd = sh + "_sh" if sh + "_sh" in P else sh + "_dk"
        hl = hr + "_lt"
        side = facing in ("left", "right")
        # legs + shoes
        if not side:
            p.rect(5, 17, 7.5, 21, pt)
            p.rect(8.5, 17, 11, 21, pt)
            p.rect(9.5, 17, 11, 21, pt + "_sh")
            p.rect(4.5, 20.5, 7.5, 22.5, "shoe")
            p.rect(8.5, 20.5, 11.5, 22.5, "shoe")
        else:
            p.rect(5.5, 17, 9.5, 21, pt)
            p.rect(8, 17, 9.5, 21, pt + "_sh")
            p.rect(4, 20.5, 8, 22.5, "shoe")
            p.rect(7.5, 21, 10.5, 22.5, "shoe")
        # body
        if not side:
            p.rrect(4, 11.5, 12, 18, 2, sh)
            p.rect(10, 12.5, 12, 18, shd)
            p.rect(2.5, 12, 4.5, 16.5, sh)          # arms
            p.rect(11.5, 12, 13.5, 16.5, shd)
            p.rect(2.5, 16.5, 4.5, 18, sk)
            p.rect(11.5, 16.5, 13.5, 18, sk + "_sh")
        else:
            p.rrect(4.5, 11.5, 10.5, 18, 2, sh)
            p.rect(9, 12, 10.5, 18, shd)
            if L.get("bag"):
                p.rrect(9, 12, 12.5, 17, 1, "bag")
                p.rect(9.5, 12.5, 10.5, 16.5, "win_lt")
            p.rect(6, 12.5, 8, 16.5, shd)          # near arm
            p.rect(6, 16.5, 8, 18, sk)
        if L.get("bag") and facing == "down":
            p.rect(4.5, 11.5, 5.5, 16, "bag")
            p.rect(10.5, 11.5, 11.5, 16, "bag")
        if L.get("bag") and facing == "up":
            p.rrect(4.5, 12, 11.5, 17.5, 1.5, "bag")
            p.rect(5.5, 13, 10.5, 14, "win_lt")
        if L.get("lanyard"):
            if facing == "down":
                p.rect(6.5, 11.5, 9.5, 12.5, "maroon")
                p.rect(7.5, 12.5, 8.5, 14.5, "maroon")
                p.rect(6.5, 14.5, 9.5, 16.5, "trim")
                p.rect(7, 15, 9, 15.5, "maroon")
            elif side:
                p.rect(5, 12, 6.5, 14.5, "maroon")
                p.rect(4.5, 14.5, 6.5, 16.5, "trim")
        # head
        p.oval(2.5, 0.5, 13.5, 12, sk)
        p.oval(9.5, 3, 13.5, 11.5, sk + "_sh")
        p.oval(2.5, 0.5, 12.5, 11.5, sk)
        if facing == "down":
            p.oval(2, 0, 14, 8, hr)                       # hair cap
            p.rect(2, 3.5, 3.5, 9, hr)
            p.rect(12.5, 3.5, 14, 9, hr + "_sh")
            p.rect(3.5, 5, 12.5, 6.5, hr)                 # fringe
            p.oval(9.5, 1, 13.5, 6, hr + "_sh")
            p.rect(4.5, 1.5, 8, 2.5, hl) if s == 2 else p.px(5, 1.5, hl, 2, 1)
            if s == 2:
                for ex in (5, 9.5):
                    p.rect(ex, 7, ex + 1.5, 9.5, "eye")
                    p.px(ex, 7, "trim")
                p.rect(7, 10.5, 9, 11, sk + "_sh")
            else:
                p.px(5, 7.5, "eye", 1, 2)
                p.px(10, 7.5, "eye", 1, 2)
        elif facing == "up":
            p.oval(2, 0, 14, 12, hr)
            p.oval(9, 1.5, 14, 11.5, hr + "_sh")
            p.rect(4, 2, 8, 3, hl) if s == 2 else p.px(5, 2, hl, 2, 1)
            p.rect(3.5, 3, 5, 6, hl) if s == 2 else None
        else:  # facing left (right is the mirror)
            p.oval(2, 0, 14, 8, hr)
            p.rect(7.5, 2.5, 14, 10.5, hr)
            p.rect(11, 3.5, 14, 10, hr + "_sh")
            p.rect(2.5, 4.5, 6, 6, hr)
            p.rect(4.5, 1.5, 9, 2.5, hl) if s == 2 else p.px(5, 1.5, hl, 2, 1)
            if s == 2:
                p.rect(4, 7, 5.5, 9.5, "eye")
                p.px(4, 7, "trim")
                p.rect(8.5, 6.5, 10, 9, sk)      # ear
                p.rect(9.5, 7, 10, 8.5, sk + "_sh")
                p.rect(2, 8.5, 2.5, 9.5, sk)     # nose
            else:
                p.px(4, 7.5, "eye", 1, 2)
        img = outline(p.img, P["out"])
        if facing == "right":
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        self.shade("oval", (2.5, 12.5, 14.5, 17), (cx, cy))
        self.paste(img, self.X(cx) - s, self.Y(cy) - 7 * s - s)

    def ram(self, cx, cy):
        """The bronze Ram on its plinth."""
        p = Pen(18, 24, self.s)
        p.rect(2, 14, 16, 22, "stone")
        p.rect(2, 14, 16, 15.5, "stone_lt")
        p.rect(13, 15.5, 16, 22, "stone_dk")
        # body, facing left
        p.oval(4, 6, 15, 13, "bronze")
        p.oval(9, 6.5, 15, 13, "bronze_dk")
        p.rect(5, 11, 6.5, 14.5, "bronze_dk")      # legs
        p.rect(12, 11, 13.5, 14.5, "bronze_dk")
        p.oval(1.5, 3, 7, 8.5, "bronze")           # head
        p.oval(3, 1.5, 8, 6.5, "bronze_lt")        # curled horn
        p.oval(4.5, 3, 6.5, 5, "bronze_dk")
        p.rect(5, 7, 10, 8, "bronze_lt")           # back highlight
        p.px(2.5, 5, "bronze_dk")
        img = outline(p.img, P["out"])
        self.shade("oval", (2, 17, 20, 24), (cx, cy - 0.5))
        self.paste(img, self.X(cx) - self.s, self.Y(cy) - 7 * self.s - self.s)

    # ----------------------------------------------------------------- compose
    def render(self):
        self.ground()
        # depth-sorted objects
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
        # shadows go down first (they fall on the ground only)
        self._shadow_only = True
        saved = self.img.copy()
        for _, _, fn in items:
            fn()
        self.img = saved
        self.apply_shadow()
        # then the objects themselves (re-run without adding shadows)
        self.labels = []
        shade = self.shade
        self.shade = lambda *a, **k: None
        for _, _, fn in items:
            fn()
        self.shade = shade
        return self.img
