"""First drafts (decisions/0025) for the academic batch, in the house style:
University Church, Collins Hall, Thebaud Hall, Freeman Hall, Spellman
Hall, Larkin Hall, Mulcahy Hall and Duane Library (Admission).

Each keeps the footprint and south-facing door it already had on the map.

    uv run python assets/buildings/_style/draw_academic.py
"""

from draw_residence import front, rows_of_windows
from kit import (BROWN, DBLUE, GRAY, GREEN, LBLUE, LIME, MAROON, NAVY, PBRICK, PBRICK_SH,
                 PEACH, ROOF, ROOF_SH, ST, ST_DK, ST_HI, ST_SH, WHITE, YELLOW, arched_window,
                 battlements, brick, canvas, card, clouds, door, fieldstone, flat_roof,
                 gothic_window, lawn, outline, person, save_building, slope_roof, tree, window)


def gothic_tower(d, x0, x1, top, bottom, stone=(ST, ST_HI, ST_SH), pinnacles=True, arch_h=26):
    """A square Gothic tower over a pointed-arch doorway."""
    base, light, dark = stone
    fieldstone(d, x0, top, x1, bottom, base=base, light=light, dark=dark)
    d.rectangle([x0, top, x1, top + 2], fill=light)
    if pinnacles:
        for px in (x0, x1 - 2):
            d.polygon([(px, top), (px + 1, top - 6), (px + 2, top)], fill=light)
    cx = (x0 + x1) // 2
    w = x1 - x0 - 9
    gothic_window(d, cx - w // 2, top + 6, w, max(10, bottom - top - arch_h - 10))
    # the pointed-arch doorway
    dx0, dx1 = cx - 7, cx + 7
    d.rectangle([dx0 - 2, bottom - arch_h + 8, dx1 + 2, bottom], fill=light)
    d.polygon([(dx0 - 2, bottom - arch_h + 8), (cx, bottom - arch_h), (dx1 + 2, bottom - arch_h + 8)], fill=light)
    d.polygon([(dx0, bottom - arch_h + 9), (cx, bottom - arch_h + 3), (dx1, bottom - arch_h + 9)], fill=NAVY)
    d.rectangle([dx0, bottom - arch_h + 9, dx1, bottom - 14], fill=NAVY)
    door(d, dx0 + 1, bottom - 13, dx1 - dx0 - 1, 14, frame=dark, leaf=MAROON)
    outline(d, x0, top, x1, bottom)


# ---------------------------------------------------------------- University Church
def church():
    im, d, ox, oy = canvas("university_church")
    W, H = im.size
    slope_roof(d, 0, 0, W - 1, 45, ROOF_SH, NAVY, ROOF)
    d.line([W // 2, 0, W // 2, 45], fill=ROOF)                            # ridge
    # the octagonal lantern over the crossing
    cx = W // 2
    d.polygon([(cx - 8, 12), (cx - 4, 8), (cx + 4, 8), (cx + 8, 12), (cx + 8, 22),
               (cx - 8, 22)], fill=ST)
    d.rectangle([cx - 6, 14, cx + 5, 20], fill=NAVY)
    for lx in (cx - 4, cx, cx + 4):
        d.line([lx, 14, lx, 20], fill=ST_HI)
    d.polygon([(cx - 8, 12), (cx, 4), (cx + 8, 12)], fill=ROOF)
    d.line([cx, 0, cx, 4], fill=YELLOW)
    front(d, W, 48, H, "fieldstone", base=ST, light=ST_HI, dark=ST_SH)
    for x in (4, 62):
        gothic_window(d, x, 56, 12, 20)
    tx = (18 - 16) * 16
    gothic_tower(d, tx - 4, tx + 19, 26, H - 1)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def church_card():
    im, d = card()
    clouds(d)
    slope_roof(d, 60, 30, 220, 44, ROOF_SH, NAVY, ROOF)
    fieldstone(d, 60, 44, 220, 76, base=ST, light=ST_HI, dark=ST_SH)
    for x in (130, 160, 190):
        gothic_window(d, x, 50, 12, 20)
    d.polygon([(170, 30), (178, 22), (186, 30)], fill=ROOF)                # the lantern
    d.rectangle([172, 24, 184, 32], fill=ST)
    gothic_tower(d, 70, 116, 6, 76, arch_h=34)
    for px in (78, 108):
        d.polygon([(px, 6), (px + 2, -2), (px + 4, 6)], fill=ST_HI)
    tree(d, 26, 48, 18, ground=76)
    lawn(d, 77)
    person(d, 136, 70, NAVY)
    return im


# ---------------------------------------------------------------- Collins Hall
def portico(d, x0, x1, top, bottom, cols=4):
    """White limestone classical front: pediment, columns, arched doors."""
    d.polygon([(x0 - 2, top + 8), ((x0 + x1) // 2, top), (x1 + 2, top + 8)], fill=WHITE)
    d.polygon([(x0 + 3, top + 7), ((x0 + x1) // 2, top + 3), (x1 - 3, top + 7)], fill=ST_HI)
    d.rectangle([x0 - 2, top + 8, x1 + 2, top + 11], fill=WHITE)
    d.rectangle([x0, top + 12, x1, bottom], fill=ST_HI)
    span = (x1 - x0) / (cols - 1)
    for i in range(cols):
        cx = round(x0 + i * span)
        d.rectangle([cx - 1, top + 12, cx + 1, bottom], fill=WHITE)
        d.line([cx + 1, top + 12, cx + 1, bottom], fill=ST)


def collins():
    im, d, ox, oy = canvas("collins_hall")
    W, H = im.size
    slope_roof(d, 0, 0, W - 1, 53, ROOF, ROOF_SH, GRAY)
    front(d, W, 56, H, "brick", base=PBRICK_SH, mortar=BROWN)
    for y in (60, 74):
        window(d, 3, y, 7, 9, frame=WHITE, glass=NAVY)
        window(d, 38, y, 7, 9, frame=WHITE, glass=NAVY)
    portico(d, 13, 34, 52, H - 1)
    d.rectangle([17, H - 16, 30, H - 1], fill=NAVY)
    d.pieslice([17, H - 22, 30, H - 10], 180, 360, fill=NAVY)
    door(d, 18, H - 14, 12, 14, frame=ST, leaf=BROWN)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def collins_card():
    im, d = card()
    clouds(d)
    brick(d, 30, 14, 198, 76, PBRICK_SH, BROWN)
    d.rectangle([30, 12, 198, 15], fill=WHITE)
    for y in (22, 40):
        for x in range(38, 192, 14):
            if not 84 < x < 146:
                window(d, x, y, 8, 11, frame=WHITE, glass=NAVY)
    portico(d, 88, 140, 4, 76, cols=6)
    for ax in (96, 110, 124):                                              # three arched doors
        d.rectangle([ax, 56, ax + 9, 76], fill=BROWN)
        d.pieslice([ax, 51, ax + 9, 61], 180, 360, fill=BROWN)
    tree(d, 14, 52, 12, ground=76)
    tree(d, 214, 50, 12, ground=76)
    lawn(d, 77)
    for i in range(3):
        d.rectangle([86 - i * 4, 76 + i * 2, 142 + i * 4, 77 + i * 2], fill=ST_HI)
    return im


# ---------------------------------------------------------------- Thebaud Hall
def mansard(d, x0, x1, y0, y1, dormers):
    slope_roof(d, x0, y0, x1, y1, GREEN, NAVY, LIME)
    for x in dormers:
        d.polygon([(x - 1, y1 - 10), (x + 5, y1 - 15), (x + 11, y1 - 10)], fill=WHITE)
        d.rectangle([x, y1 - 10, x + 10, y1], fill=WHITE)
        d.rectangle([x + 2, y1 - 8, x + 8, y1 - 1], fill=NAVY)


def thebaud():
    im, d, ox, oy = canvas("thebaud_hall")
    W, H = im.size
    mansard(d, 0, W - 13, oy, oy + 29, (8, 30, 52, 70))
    front(d, W - 12, oy + 32, H, "ashlar", base=ST_HI, joint=ST)
    for x in (6, 22, 62, 76):
        window(d, x, oy + 36, 8, 9, frame=WHITE, glass=NAVY)
        window(d, x, oy + 49, 8, 9, frame=WHITE, glass=NAVY)
    dx = (36 - 34) * 16
    d.rectangle([dx - 2, oy + 34, dx + 17, H - 1], fill=WHITE)
    window(d, dx + 2, oy + 36, 12, 8, frame=WHITE, glass=NAVY)
    door(d, dx + 2, H - 14, 12, 14, frame=ST, leaf=BROWN)
    outline(d, 0, oy, W - 13, H - 1)
    # the old power-plant smokestack beside it
    brick(d, W - 9, 0, W - 2, H - 1, ST_HI, ST)
    d.rectangle([W - 10, 0, W - 1, 2], fill=ST_SH)
    d.rectangle([W - 10, 0, W - 1, H - 1], outline=NAVY)
    return im


def thebaud_card():
    im, d = card()
    clouds(d)
    mansard(d, 30, 180, 14, 36, range(42, 176, 26))
    from kit import ashlar
    ashlar(d, 30, 36, 180, 76, base=ST_HI, joint=ST)
    for x in range(40, 172, 16):
        if not 96 < x < 116:
            window(d, x, 42, 9, 11, frame=WHITE, glass=NAVY)
            window(d, x, 58, 9, 11, frame=WHITE, glass=NAVY)
    door(d, 100, 60, 14, 16, frame=ST, leaf=BROWN)
    brick(d, 196, 0, 210, 76, ST_HI, ST)                                   # the smokestack
    d.rectangle([194, 0, 212, 3], fill=ST_SH)
    tree(d, 14, 54, 12, leaf=WHITE, hi=PEACH, ground=76)                   # the magnolia
    lawn(d, 77)
    return im


# ---------------------------------------------------------------- Freeman, Larkin
GRAY_STONE = dict(base=ST_SH, light=ST, dark=ST_DK)


def freeman():
    im, d, ox, oy = canvas("freeman_hall")
    W, H = im.size
    slope_roof(d, 0, 0, W - 1, 21, ROOF, ROOF_SH, GRAY)
    front(d, W, 24, H, "fieldstone", **GRAY_STONE)
    battlements(d, 0, W - 1, 24, h=3, step=4, fill=ST, top=ST_HI)
    dx = (49 - 46) * 16
    rows_of_windows(d, 2, W - 3, (31, 41, 51), w=7, h=7, gap=5, frame=ST_HI, glass=NAVY,
                    skip=((dx - 4, dx + 19),))
    d.rectangle([dx - 4, 26, dx + 19, H - 1], fill=ST)                    # entrance bay
    d.rectangle([dx + 1, 30, dx + 14, 40], fill=ST_HI)
    window(d, dx + 3, 32, 10, 7, frame=ST_HI, glass=NAVY)
    d.rectangle([dx + 2, H - 16, dx + 13, H - 1], fill=ST_HI)
    door(d, dx + 3, H - 14, 10, 14, frame=ST_DK, leaf=BROWN)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def freeman_card():
    im, d = card()
    clouds(d)
    fieldstone(d, 20, 16, 208, 76, **GRAY_STONE)
    battlements(d, 20, 208, 16, h=3, step=5, fill=ST, top=ST_HI)
    for y in (24, 38, 52):
        for x in range(28, 202, 13):
            if not 98 < x < 128:
                window(d, x, y, 8, 9, frame=ST_HI, glass=NAVY)
    d.rectangle([100, 8, 128, 76], fill=ST)
    battlements(d, 100, 128, 8, h=3, step=4, fill=ST, top=ST_HI)
    gothic_window(d, 106, 16, 16, 20)
    d.rectangle([106, 56, 122, 76], fill=ST_HI)
    door(d, 108, 60, 12, 16, frame=ST_DK)
    lawn(d, 77)
    d.rectangle([0, 80, 227, 82], fill=GREEN)                              # the hedge by the walk
    tree(d, 214, 44, 14, ground=76)
    person(d, 60, 70, MAROON)
    person(d, 70, 70, LBLUE)
    return im


def larkin():
    im, d, ox, oy = canvas("larkin_hall")
    W, H = im.size
    slope_roof(d, 0, 0, W - 1, 21, ROOF, ROOF_SH, GRAY)
    front(d, W, 24, H, "fieldstone", **GRAY_STONE)
    battlements(d, 0, W - 1, 24, h=3, step=4, fill=ST, top=ST_HI)
    for x in (4, 16, 58, 70):
        for y in (31, 45):
            window(d, x, y, 7, 8, frame=ST_HI, glass=NAVY)
    gothic_tower(d, 28, 51, 10, H - 1, stone=(ST_SH, ST, ST_DK), arch_h=24)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def larkin_card():
    im, d = card()
    clouds(d)
    fieldstone(d, 14, 22, 214, 76, **GRAY_STONE)
    battlements(d, 14, 214, 22, h=3, step=5, fill=ST, top=ST_HI)
    for y in (30, 44, 58):
        for x in range(22, 208, 13):
            if not 92 < x < 136:
                window(d, x, y, 8, 9, frame=ST_HI, glass=NAVY)
    gothic_tower(d, 94, 134, 4, 76, stone=(ST_SH, ST, ST_DK), arch_h=30)
    tree(d, 40, 46, 18, ground=76)
    d.line([160, 50, 160, 76], fill=NAVY)                                  # a lamp post
    d.rectangle([158, 46, 162, 50], fill=YELLOW)
    lawn(d, 77)
    return im


# ---------------------------------------------------------------- Spellman, Mulcahy
def spellman():
    im, d, ox, oy = canvas("spellman_hall")
    W, H = im.size
    slope_roof(d, 0, 0, W - 1, 29, ROOF, ROOF_SH, GRAY)
    front(d, W, 32, H, "brick", base=PBRICK_SH, mortar=BROWN)
    battlements(d, 0, W - 1, 32, h=2, step=4, fill=ST_HI, top=WHITE)
    for x in (0, W - 3):
        for y in range(36, H, 6):                                         # stone quoins
            d.rectangle([x, y, x + 2, y + 2], fill=ST_HI)
    for y in (40, 52):
        window(d, 5, y, 7, 9, frame=ST_HI, glass=NAVY)
        window(d, 36, y, 7, 9, frame=ST_HI, glass=NAVY)
    d.rectangle([14, 36, 33, H - 1], fill=ST_HI)
    window(d, 18, 40, 12, 9, frame=ST_HI, glass=NAVY)
    door(d, 18, H - 14, 12, 14, frame=ST, leaf=BROWN)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def spellman_card():
    im, d = card()
    clouds(d)
    brick(d, 60, 16, 180, 76, PBRICK_SH, BROWN)
    battlements(d, 60, 180, 16, h=3, step=5, fill=ST_HI, top=WHITE)
    for y in (24, 40, 56):
        for x in range(68, 176, 16):
            if not 104 < x < 132:
                window(d, x, y, 9, 11, frame=ST_HI, glass=NAVY)
    d.rectangle([106, 20, 132, 76], fill=ST_HI)
    gothic_window(d, 112, 26, 14, 18)                                      # St. Robert Bellarmine Chapel
    door(d, 112, 60, 14, 16, frame=ST, leaf=BROWN)
    tree(d, 30, 50, 16, ground=76)
    tree(d, 202, 54, 14, ground=76)
    lawn(d, 77)
    return im


def mulcahy():
    im, d, ox, oy = canvas("mulcahy_hall")
    W, H = im.size
    flat_roof(d, 0, 0, W - 1, 21, rim=ST_HI, fill=ROOF, seam=ROOF_SH, units=((40, 4), (8, 8)))
    front(d, W, 24, H, "brick", base=BROWN, mortar=PBRICK_SH)
    for px in range(0, W, 10):
        d.rectangle([px, 24, px + 2, H - 1], fill=WHITE)                   # white concrete piers
        d.rectangle([px + 4, 28, px + 7, H - 16], fill=NAVY)               # tall window strips
        d.line([px + 4, 28, px + 4, H - 16], fill=LBLUE)
    d.rectangle([0, 24, W - 1, 26], fill=WHITE)
    d.rectangle([0, H - 14, W - 1, H - 1], fill=ST_DK)
    d.rectangle([10, H - 18, 33, H - 15], fill=WHITE)                      # canopy
    door(d, 16, H - 14, 12, 14, frame=NAVY, glass=True)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def mulcahy_card():
    im, d = card()
    clouds(d)
    brick(d, 50, 6, 178, 76, BROWN, PBRICK_SH)
    for px in range(50, 178, 12):
        d.rectangle([px, 6, px + 3, 76], fill=WHITE)
        d.rectangle([px + 5, 10, px + 9, 66], fill=NAVY)
        d.line([px + 5, 10, px + 5, 66], fill=LBLUE)
    d.rectangle([50, 4, 178, 7], fill=WHITE)
    d.rectangle([50, 66, 178, 76], fill=ST_DK)
    d.rectangle([96, 62, 132, 65], fill=WHITE)
    door(d, 106, 66, 16, 10, frame=NAVY, glass=True)
    tree(d, 22, 44, 18, ground=76)
    tree(d, 204, 46, 16, ground=76)
    lawn(d, 77)
    return im


# ---------------------------------------------------------------- Duane Library (Admission)
def duane():
    im, d, ox, oy = canvas("admissions")
    W, H = im.size
    slope_roof(d, 0, oy, W - 1, oy + 29, ROOF, ROOF_SH, GRAY)
    front(d, W, oy + 32, H, "fieldstone", base=ST, light=ST_HI, dark=ST_SH)
    battlements(d, 0, W - 1, oy + 32, h=3, step=4, fill=ST_SH, top=ST_HI)
    for x in (4, 64):
        gothic_window(d, x, oy + 40, 10, 22)
    gothic_tower(d, 26, 53, 0, H - 1, arch_h=26)
    battlements(d, 26, 53, 2, h=2, step=3, fill=ST, top=ST_HI)
    outline(d, 0, oy, W - 1, H - 1)
    return im


def duane_card():
    im, d = card()
    clouds(d)
    fieldstone(d, 16, 26, 212, 76, base=ST, light=ST_HI, dark=ST_SH)
    battlements(d, 16, 212, 26, h=3, step=5, fill=ST_SH, top=ST_HI)
    for x in range(26, 206, 18):
        if not 84 < x < 140:
            gothic_window(d, x, 36, 10, 26)
    gothic_tower(d, 90, 138, 2, 76, arch_h=30)
    battlements(d, 90, 138, 4, h=2, step=4, fill=ST, top=ST_HI)
    lawn(d, 77)
    d.line([60, 52, 60, 77], fill=NAVY)                                     # lamp post
    d.rectangle([58, 48, 62, 52], fill=YELLOW)
    for i, s in enumerate((MAROON, WHITE, DBLUE)):                         # a campus tour arriving
        person(d, 150 + i * 8, 70, s)
    return im


if __name__ == "__main__":
    save_building("university_church", church(), church_card())
    save_building("collins_hall", collins(), collins_card())
    save_building("thebaud_hall", thebaud(), thebaud_card())
    save_building("freeman_hall", freeman(), freeman_card())
    save_building("larkin_hall", larkin(), larkin_card())
    save_building("spellman_hall", spellman(), spellman_card())
    save_building("mulcahy_hall", mulcahy(), mulcahy_card())
    save_building("admissions", duane(), duane_card())
