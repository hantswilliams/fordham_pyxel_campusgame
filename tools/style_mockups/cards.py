"""Dealy Hall's building card in each style (today's: game/scenes/card.py).
Same words as today; the picture is the style's own Dealy Hall drawing."""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import scene as S
import pixel
import smooth
from pixel import P, Pen, outline
from ui_pixel import READ, BOLD, crisp, rbox, wrap

NAME = "DEALY HALL"
KIND = "ACADEMIC BUILDING"
BLURB = ("Academic building of dark stone with white trim, beside Rose Hill Manor "
         "Drive across from Edwards Parade. A Campus Shuttle stop is on the drive by its east end.")
REAL = "The columned main entrance is on the west side, facing Cunniffe House."
INSIDE = ["Classrooms and offices", "Dining"]
DEALY = next(b for b in S.BUILDINGS if b["id"] == "dealy")
KIND_BLUE = (57, 92, 152)


# ------------------------------------------------------------------ pixel
def picture_pixel(s):
    sc = pixel.PixelScene(s)
    Wp, Hp = 228, 88
    p = Pen(Wp, Hp, s)
    bands = [0x8DC3EE, 0xA2CFF2, 0xB8DAF5, 0xCDE6F8, 0xE0F0FB]
    for i, c in enumerate(bands):
        p.rect(0, i * 10, Wp, i * 10 + 10, pixel.rgb(c))
    for cx, cy, w in [(30, 12, 22), (176, 8, 28), (120, 20, 14)]:       # clouds
        p.oval(cx, cy, cx + w, cy + 7, (255, 255, 255))
        p.oval(cx + w * 0.25, cy - 4, cx + w * 0.75, cy + 5, (255, 255, 255))
        p.rect(cx + 2, cy + 5, cx + w - 2, cy + 7, (236, 244, 252))
    for x in range(-6, Wp, 13):                                         # far trees
        p.oval(x, 40 + (x * 7) % 5, x + 18, 62, "leaf_dk")
        p.oval(x + 3, 42 + (x * 7) % 5, x + 13, 54, "leaf")
    p.rect(0, 58, Wp, Hp, "grass")
    for y in range(60, Hp, 8):
        p.rect(0, y, Wp, y + 4, "grass_alt")
    p.poly([(Wp / 2 - 7, 82), (Wp / 2 + 7, 82), (Wp / 2 + 22, Hp), (Wp / 2 - 22, Hp)], "walk")
    pic = p.img
    t = sc.tree_sprite()
    for x in (20, 42, 162, 184):
        pic.alpha_composite(t, (round(x * s), round(54 * s)))
    # the building from the dormers down: its front, as you'd see it walking up
    b = sc.building_sprite(DEALY)
    cut = 26 * s
    b = b.crop((0, cut, b.width, b.height))
    ImageDraw.Draw(b).line([s, 0, b.width - 1 - s, 0], fill=P["out"], width=s)
    ImageDraw.Draw(b).line([s, s, b.width - 1 - s, s], fill=P["slate_hi"], width=s)
    pic.alpha_composite(b, (round((Wp / 2 - 48) * s) - s, round(83 * s) - b.height + s))
    return pic


def card_pixel(s, world):
    """world: the style's overworld art (384s x 288s)."""
    k = 2 // s
    art = world.convert("RGB")
    if s == 1:      # Pyxel dither, as today
        a = np.array(art)
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        a[(xx + yy) % 2 == 0] = pixel.rgb(0x2B335F)
        art = Image.fromarray(a)
    else:           # darkened copy of the world (palette swap to dark shades)
        a = np.array(art).astype(np.float32)
        a = a * 0.38 + np.array([20, 22, 48]) * 0.62 * 0.6
        art = Image.fromarray(a.astype(np.uint8))
    art = art.convert("RGBA")
    d = ImageDraw.Draw(art)
    X0, Y0, X1, Y1 = 6 * s, 6 * s, 378 * s, 282 * s
    HEAD = 20 * s
    if s == 1:
        rbox(d, X0, Y0, X1, Y1, 4, P["out"])
        rbox(d, X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, 3, (168, 184, 214))
        rbox(d, X0 + 3, Y0 + 3, X1 - 3, Y1 - 3, 2, (250, 249, 245))
        d.rectangle([X0 + 3, Y0 + 3, X1 - 4, Y0 + HEAD], fill=P["maroon"])
        d.line([X0 + 4, Y0 + 4, X1 - 5, Y0 + 4], fill=P["maroon_lt"])
    else:
        rbox(d, X0, Y0 + 4, X1, Y1 + 4, 14, (14, 14, 30))
        rbox(d, X0, Y0, X1, Y1, 14, P["out"])
        rbox(d, X0 + 2, Y0 + 2, X1 - 2, Y1 - 2, 12, (196, 206, 226))
        rbox(d, X0 + 6, Y0 + 6, X1 - 6, Y1 - 6, 9, (251, 250, 247))
        rbox(d, X0 + 6, Y0 + 6, X1 - 6, Y0 + HEAD + 10, 9, P["maroon"])
        d.rectangle([X0 + 6, Y0 + HEAD, X1 - 7, Y0 + HEAD + 9], fill=P["maroon"])
        d.line([X0 + 14, Y0 + 9, X1 - 15, Y0 + 9], fill=P["maroon_lt"], width=2)
    # picture
    pic = picture_pixel(s)
    px, py = (384 * s - pic.width) // 2, Y0 + HEAD + 6 * s
    if s == 1:
        d.rectangle([px - 1, py - 1, px + pic.width, py + pic.height], outline=P["out"])
        art.alpha_composite(pic, (px, py))
    else:
        m = Image.new("L", pic.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, pic.width - 1, pic.height - 1], radius=8, fill=255)
        rbox(d, px - 2, py - 2, px + pic.width + 2, py + pic.height + 2, 10, P["out"])
        art.paste(pic, (px, py), m)
    d = ImageDraw.Draw(art)
    # kind tag on the lawn
    if s == 1:
        tw = len(KIND) * 16 // k + 8 * s
        tx, ty = px + 4 * s, py + pic.height - 18 * s
        d.rectangle([tx, ty, tx + tw, ty + 15], fill=KIND_BLUE)
    else:
        tw = len(KIND) * 9 + 20
        tx, ty = px + 8, py + pic.height - 30
        rbox(d, tx, ty, tx + tw, ty + 22, 11, KIND_BLUE, P["out"], 2)
    # footer
    fy = Y1 - 18 * s
    d.line([X0 + 6 * s, fy, X1 - 6 * s, fy], fill=(180, 184, 196), width=s)
    ax, ay = X0 + 12 * s, fy + 7 * s
    d.polygon([(ax, ay), (ax + 8 * s, ay), (ax + 4 * s, ay + 4 * s)], fill=P["maroon"])

    screen = art.convert("RGB").resize((768, 576), Image.NEAREST)
    d = crisp(ImageDraw.Draw(screen))
    f = ImageFont.truetype(READ, 32)
    d.text((X0 * k + 22, (Y0 + HEAD // 2) * k + 3 + (4 if s == 2 else 0)), NAME, font=f, fill=(255, 255, 255), anchor="lm")
    if s == 1:
        d.text((tx * k + 8, ty * k + 15), KIND, font=f, fill=(255, 255, 255), anchor="lm")
    else:
        d.text((tx + tw // 2, ty + 11), KIND, font=ImageFont.truetype(BOLD, 18), fill=(255, 255, 255), anchor="mm")
    lines = [(ln, (24, 22, 30)) for ln in wrap(BLURB, 44)] + [("", None), ("IN REAL LIFE", P["maroon"])] + \
            [(ln, (24, 22, 30)) for ln in wrap(REAL, 44)]
    top = (py + pic.height) * k + 22
    for i, (ln, col) in enumerate(lines[:7]):
        if ln:
            d.text((X0 * k + 22, top + i * 34), ln, font=f, fill=col, anchor="lt")
    d.text((X1 * k - 22, fy * k + 20), "Z: CLOSE", font=f, fill=KIND_BLUE, anchor="rm")
    return screen


# ------------------------------------------------------------------ smooth
def card_smooth(world):
    """world: Style C overworld at hi-res (1536 x 1152)."""
    Z = 2
    F = smooth.F
    bg = world.convert("RGB").filter(ImageFilter.GaussianBlur(10))
    a = np.array(bg).astype(np.float32) * 0.55 + np.array([30, 24, 50]) * 0.45
    img = Image.fromarray(a.astype(np.uint8)).convert("RGBA")
    box = (24 * Z, 18 * Z, 744 * Z, 558 * Z)
    smooth._shadowed(img, box, 28 * Z, blur=16 * Z, offset=(0, 10 * Z), alpha=150)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=28 * Z, fill=(255, 255, 255))
    # picture: full width of the card, rounded
    pw, ph = box[2] - box[0] - 40 * Z, 200 * Z
    px, py = box[0] + 20 * Z, box[1] + 20 * Z
    sp = smooth.SPen(pw / F, ph / F)
    sp.grad("rect", (0, 0, pw / F, ph / F * 0.66), (124, 182, 236), (214, 236, 252))
    for cx, cy, w in [(40, 14, 40), (250, 10, 50), (160, 26, 26)]:
        sp.oval(cx, cy, cx + w, cy + 12, (255, 255, 255))
        sp.oval(cx + w * 0.25, cy - 7, cx + w * 0.75, cy + 8, (255, 255, 255))
    for x in range(-10, int(pw / F), 18):
        sp.ball(x, 62 + (x * 7) % 6, x + 26, 94, "leaf", "leaf", "leaf_dk")
    sp.grad("rect", (0, ph / F * 0.62, pw / F, ph / F), "grass_lt", "grass")
    mid = pw / F / 2
    sp.poly([(mid - 9, 92), (mid + 9, 92), (mid + 34, ph / F), (mid - 34, ph / F)], "walk")
    pic = sp.img
    sc = smooth.SmoothScene()
    t, tn = sc.tree_sprite()
    t2 = t.resize((int(t.width * 1.2), int(t.height * 1.2)), Image.LANCZOS)
    for x in (40, 74, 262, 296):
        pic.alpha_composite(t2, (int(x * F), int(ph - 44 * F)))
    b, n = sc.building_sprite(DEALY)
    b = b.crop((0, n + 24 * F, b.width, b.height))
    ImageDraw.Draw(b).rounded_rectangle([n, 0, b.width - n, 1.2 * F], radius=F, fill=smooth.C["slate_lt"])
    b2 = b.resize((int(b.width * 1.25), int(b.height * 1.25)), Image.LANCZOS)
    pic.alpha_composite(b2, (int(pw / 2 - b2.width / 2), int(ph - 7 * F - b2.height + n)))
    m = Image.new("L", pic.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, pic.width - 1, pic.height - 1], radius=18 * Z, fill=255)
    img.paste(pic, (int(px), int(py)), m)
    d = ImageDraw.Draw(img)
    # title + kind chip
    ft = ImageFont.truetype(smooth.ROUND_BOLD, 34 * Z)
    ty = py + ph + 22 * Z
    d.text((px + 6 * Z, ty), "Dealy Hall", font=ft, fill=smooth.C["ink"], anchor="lt")
    fc = ImageFont.truetype(smooth.ROUND_BOLD, 15 * Z)
    cw = fc.getlength("Academic building") + 24 * Z
    cx0 = px + 6 * Z + ft.getlength("Dealy Hall") + 16 * Z
    d.rounded_rectangle([cx0, ty + 10 * Z, cx0 + cw, ty + 36 * Z], radius=13 * Z, fill=(226, 236, 252))
    d.text((cx0 + cw / 2, ty + 23 * Z), "Academic building", font=fc, fill=KIND_BLUE, anchor="mm")
    # body
    fb = ImageFont.truetype(smooth.ROUND_MED, 22 * Z)
    y = ty + 52 * Z
    for ln in smooth.wrap_px(BLURB, fb, pw - 12 * Z):
        d.text((px + 6 * Z, y), ln, font=fb, fill=(70, 66, 84), anchor="lt")
        y += 30 * Z
    y += 10 * Z
    fh = ImageFont.truetype(smooth.ROUND_BOLD, 15 * Z)
    d.text((px + 6 * Z, y), "INSIDE", font=fh, fill=smooth.C["maroon"], anchor="lt")
    x = px + 80 * Z
    for item in INSIDE:
        w = fh.getlength(item) + 26 * Z
        d.rounded_rectangle([x, y - 6 * Z, x + w, y + 22 * Z], radius=14 * Z, fill=(244, 240, 233))
        d.text((x + w / 2, y + 8 * Z), item, font=fh, fill=smooth.C["ink"], anchor="mm")
        x += w + 10 * Z
    # close button
    bw, bh = 132 * Z, 40 * Z
    bx, by = box[2] - 20 * Z - bw, box[3] - 20 * Z - bh
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=bh / 2, fill=smooth.C["maroon"])
    d.ellipse([bx + 8 * Z, by + 8 * Z, bx + 32 * Z, by + 32 * Z], fill=(255, 255, 255))
    d.text((bx + 20 * Z, by + bh / 2), "Z", font=fh, fill=smooth.C["maroon"], anchor="mm")
    d.text((bx + 80 * Z, by + bh / 2), "Close", font=ImageFont.truetype(smooth.ROUND_BOLD, 19 * Z), fill=(255, 255, 255), anchor="mm")
    fm = ImageFont.truetype(smooth.ROUND_MED, 16 * Z)
    d.text((px + 6 * Z, by + bh / 2), "In real life, the main entrance faces Cunniffe House.", font=fm, fill=(130, 126, 142), anchor="lm")
    return img.convert("RGB").resize((768, 576), Image.LANCZOS)
