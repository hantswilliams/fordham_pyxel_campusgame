"""First drafts (decisions/0024) for the residence-hall batch, in the house
style: Loschert Hall, Alumni Court South, Queen's Court, Faber Hall,
Loyola Hall, Martyrs' Court (main block and west wing), Conley & Salice,
O'Hare Hall, Tierney Hall, Finlay Hall and Walsh Hall.

Each keeps the footprint and south-facing door it already had on the map;
only the art changes.

    uv run python assets/buildings/_style/draw_residence.py
"""

from kit import (BRICK, BRICK_DK, BROWN, CYAN, DBLUE, GRAY, GREEN, LBLUE, LIME, MAROON, NAVY,
                 PBRICK, PBRICK_SH, PEACH, PINK, ROOF, ROOF_SH, ST, ST_DK, ST_HI, ST_SH, WHITE,
                 YELLOW, arched_window, ashlar, battlements, brick, canvas, card, clouds, door,
                 eave, fieldstone, flat_roof, gothic_window, lawn, outline, person,
                 save_building, slope_roof, tree, window)


def rows_of_windows(d, x0, x1, ys, w=7, h=7, gap=4, frame=WHITE, glass=LBLUE, skip=()):
    """Evenly spaced windows across a front, one row per y in `ys`;
    `skip` is a list of (x0, x1) spans to leave clear (doors, towers)."""
    step = w + gap
    n = (x1 - x0 + 1 + gap) // step
    start = x0 + (x1 - x0 + 1 - (n * step - gap)) // 2
    for y in ys:
        for i in range(n):
            x = start + i * step
            if any(a - w < x <= b for a, b in skip):
                continue
            window(d, x, y, w, h, frame=frame, glass=glass)


def front(d, W, top, H, kind, **kw):
    """The front wall from `top` to the bottom edge, with an eave above."""
    eave(d, 0, W - 1, top - 2)
    if kind == "brick":
        brick(d, 0, top, W - 1, H - 1, kw.get("base", PEACH), kw.get("mortar", ST))
    elif kind == "fieldstone":
        fieldstone(d, 0, top, W - 1, H - 1, base=kw.get("base", BRICK_DK),
                   light=kw.get("light", BRICK), dark=kw.get("dark", ROOF_SH))
    elif kind == "ashlar":
        ashlar(d, 0, top, W - 1, H - 1, base=kw.get("base", ST), joint=kw.get("joint", ST_SH))
    else:
        d.rectangle([0, top, W - 1, H - 1], fill=kw.get("base", WHITE))


def door_px(bid_origin_x, door_x):
    return (door_x - bid_origin_x) * 16


# ---------------------------------------------------------------- the 1980s pair
def gabled_glass_bay(d, cx, top, bottom, w=20, gable=10, stone=ST_HI):
    """Loschert and Alumni Court South: a tall glass bay with a pointed
    stone gable, rising above the roof line."""
    x0, x1 = cx - w // 2, cx + w // 2 - 1
    d.polygon([(x0 - 2, top + gable), (cx - 1, top), (cx, top), (x1 + 2, top + gable)], fill=stone)
    d.rectangle([x0 - 2, top + gable, x1 + 2, bottom], fill=stone)
    d.polygon([(x0 + 2, top + gable), (cx - 1, top + 4), (cx, top + 4), (x1 - 2, top + gable)], fill=NAVY)
    d.rectangle([x0 + 1, top + gable, x1 - 1, bottom - 15], fill=NAVY)
    d.rectangle([x0 + 2, top + gable + 1, x1 - 2, bottom - 16], fill=LBLUE)
    for gy in range(top + gable + 6, bottom - 16, 7):
        d.line([x0 + 2, gy, x1 - 2, gy], fill=DBLUE)
    d.line([cx, top + 6, cx, bottom - 16], fill=DBLUE)
    d.line([x0 + 3, top + gable + 2, x0 + 3, bottom - 18], fill=WHITE)


def loschert():
    im, d, ox, oy = canvas("loschert_hall")
    W, H = im.size
    flat_roof(d, 0, 0, W - 1, 29, rim=ST_HI, fill=ROOF, seam=ROOF_SH, units=((66, 8), (14, 12)))
    front(d, W, 32, H, "brick", base=PEACH, mortar=PBRICK)
    d.rectangle([0, 32, W - 1, 34], fill=ST_HI)                           # stone coping
    rows_of_windows(d, 2, W - 3, (38, 50, 62), w=7, h=8, gap=5, skip=((26, 53),))
    d.rectangle([0, H - 4, W - 1, H - 1], fill=ST)                        # stone base
    cx = door_px(9, 11) + 8 + 4
    gabled_glass_bay(d, cx, 14, H - 1)
    door(d, cx - 7, H - 14, 14, 14, frame=NAVY, glass=True)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def loschert_card():
    im, d = card()
    clouds(d)
    brick(d, 8, 22, 220, 76, PEACH, PBRICK)
    d.rectangle([8, 20, 220, 23], fill=ST_HI)
    for y in (28, 40, 52):
        for x in range(14, 214, 13):
            if not 90 < x < 138:
                window(d, x, y, 8, 9)
    gabled_glass_bay(d, 114, 4, 76, w=36, gable=16)
    door(d, 104, 62, 20, 14, frame=NAVY, glass=True)
    tree(d, 30, 56, 12, ground=76)
    tree(d, 196, 54, 14, ground=76)
    lawn(d, 77)
    d.rectangle([0, 80, 227, 87], fill=ST)                                # Loschert's front steps
    for i, s in enumerate((MAROON, WHITE)):
        person(d, 140 + i * 9, 70, s)
    return im


def alumni_south():
    im, d, ox, oy = canvas("alumni_court_south")
    W, H = im.size
    flat_roof(d, 0, 0, W - 1, 61, rim=ST_HI, fill=ROOF, seam=ROOF_SH, units=((6, 10), (30, 34)))
    front(d, W, 64, H, "brick", base=PEACH, mortar=PBRICK)
    d.rectangle([0, 64, W - 1, 66], fill=ST_HI)
    for y in (70, 82, 94, 106):
        window(d, 3, y, 7, 8)
        window(d, 38, y, 7, 8)
    gabled_glass_bay(d, 24, 46, H - 1, w=18, gable=9)
    door(d, 18, H - 14, 12, 14, frame=NAVY, glass=True)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def alumni_south_card():
    im, d = card()
    clouds(d)
    brick(d, 20, 18, 208, 76, PEACH, PBRICK)
    d.rectangle([20, 16, 208, 19], fill=ST_HI)
    for y in (24, 36, 48, 60):
        for x in range(26, 204, 12):
            if not 98 < x < 132:
                window(d, x, y, 7, 8)
    gabled_glass_bay(d, 114, 2, 76, w=30, gable=14)
    door(d, 106, 62, 16, 14, frame=NAVY, glass=True)
    tree(d, 14, 50, 14, ground=76)
    lawn(d, 77)
    d.rectangle([150, 60, 200, 74], fill=WHITE)                           # the Ram Van at the stop
    d.rectangle([194, 64, 202, 74], fill=WHITE)
    for wx in range(153, 192, 9):
        d.rectangle([wx, 62, wx + 6, 66], fill=NAVY)
    d.rectangle([150, 69, 202, 70], fill=MAROON)
    for wx in (158, 190):
        d.ellipse([wx - 3, 72, wx + 3, 78], fill=NAVY)
    return im


# ---------------------------------------------------------------- Collegiate Gothic
def queens_court():
    im, d, ox, oy = canvas("queens_court")
    W, H = im.size
    # three wings round a garden courtyard, open to the south
    slope_roof(d, 0, 0, W - 1, 61, ROOF, ROOF_SH, GRAY)
    d.rectangle([22, 14, W - 23, 61], fill=LIME)                          # the courtyard
    for x in range(24, W - 23, 5):
        d.point([x, 20 + (x * 7) % 30], fill=GREEN)
    d.line([47, 18, 47, 61], fill=PEACH)                                  # its path
    d.line([48, 18, 48, 61], fill=PEACH)
    d.ellipse([40, 30, 55, 44], fill=GREEN)                               # the statue in its bed
    d.ellipse([43, 33, 52, 41], fill=PINK)
    d.rectangle([46, 27, 49, 38], fill=WHITE)
    d.rectangle([47, 24, 48, 26], fill=WHITE)
    for tx, ty in ((28, 22), (68, 50)):
        d.ellipse([tx - 4, ty - 4, tx + 4, ty + 4], fill=GREEN)
    d.rectangle([22, 14, W - 23, 15], fill=ROOF_SH)
    battlements(d, 0, W - 1, 61, h=3, step=4, fill=ST_SH, top=ST_HI)
    front(d, W, 66, H, "fieldstone", base=ST, light=PEACH, dark=ST_SH)
    for x in (4, 18, 66, 80):                                             # brown-trimmed windows
        window(d, x, 70, 9, 8, frame=BROWN, glass=NAVY)
        arched_window(d, x + 1, 81, 7, 9, frame=BROWN)
    dx = door_px(12, 14)
    d.rectangle([dx - 4, 66, dx + 19, H - 1], fill=ST_HI)                 # stone porch
    battlements(d, dx - 4, dx + 19, 66, h=2, step=3, fill=ST_HI, top=WHITE)
    arched_window(d, dx + 2, 70, 12, 26, frame=ST_SH, glass=BROWN)
    d.line([dx + 8, 76, dx + 8, H - 1], fill=NAVY)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def queens_card():
    im, d = card()
    clouds(d, ((12, 6, 22), (180, 4, 26)))
    fieldstone(d, 6, 18, 222, 72, base=ST, light=PEACH, dark=ST_SH)
    battlements(d, 6, 222, 18, h=3, step=5, fill=ST_SH, top=ST_HI)
    for x in range(14, 214, 20):
        window(d, x, 26, 10, 10, frame=BROWN, glass=NAVY)
        arched_window(d, x + 1, 46, 8, 14, frame=BROWN)
    # the courtyard garden and the white statue
    lawn(d, 72)
    d.ellipse([84, 70, 144, 86], fill=GREEN)
    d.ellipse([94, 73, 134, 83], fill=PINK)
    d.polygon([(109, 76), (113, 52), (114, 52), (118, 76)], fill=WHITE)   # the statue: robe,
    d.ellipse([111, 45, 116, 51], fill=WHITE)                             # head,
    d.line([111, 58, 109, 64], fill=WHITE)                                # and open arms
    d.line([116, 58, 118, 64], fill=WHITE)
    d.line([115, 54, 115, 75], fill=ST_HI)
    d.rectangle([108, 76, 119, 80], fill=ST_HI)
    tree(d, 200, 52, 16, leaf=PINK, hi=WHITE, ground=80)                  # the cherry tree
    tree(d, 28, 56, 12, ground=80)
    return im


def loyola():
    im, d, ox, oy = canvas("loyola_hall")
    W, H = im.size
    slope_roof(d, 0, 0, W - 1, 21, ROOF, ROOF_SH, GRAY)
    front(d, W, 24, H, "ashlar", base=ST, joint=ST_SH)
    battlements(d, 0, W - 1, 24, h=3, step=4, fill=ST_SH, top=ST_HI)
    dx = door_px(28, 31)
    rows_of_windows(d, 2, W - 3, (31, 41, 51), w=7, h=7, gap=5, frame=ST_HI, glass=NAVY,
                    skip=((dx - 6, dx + 21),))
    # the central entrance bay: a taller stone tower with a pointed arch
    d.rectangle([dx - 6, 14, dx + 21, H - 1], fill=ST_HI)
    battlements(d, dx - 6, dx + 21, 14, h=3, step=4, fill=ST_HI, top=WHITE)
    gothic_window(d, dx + 2, 22, 12, 14)
    d.rectangle([dx + 1, 44, dx + 14, H - 1], fill=ST_SH)
    d.pieslice([dx + 1, 38, dx + 14, 50], 180, 360, fill=ST_SH)
    door(d, dx + 3, H - 14, 10, 14, frame=ST_DK, leaf=BROWN)
    outline(d, 0, 0, W - 1, H - 1)
    d.line([dx - 6, 14, dx + 21, 14], fill=NAVY)
    return im


def loyola_card():
    im, d = card()
    clouds(d)
    ashlar(d, 30, 14, 198, 76, base=ST, joint=ST_SH)
    battlements(d, 30, 198, 14, h=3, step=5, fill=ST_SH, top=ST_HI)
    for y in (22, 36, 50):
        for x in range(38, 192, 14):
            if not 94 < x < 134:
                window(d, x, y, 8, 9, frame=ST_HI, glass=NAVY)
    d.rectangle([96, 2, 132, 76], fill=ST_HI)                             # entrance tower
    battlements(d, 96, 132, 4, h=3, step=4, fill=ST_HI, top=WHITE)
    gothic_window(d, 106, 12, 16, 22)
    d.rectangle([104, 50, 124, 76], fill=ST_SH)
    d.pieslice([104, 42, 124, 60], 180, 360, fill=ST_SH)
    door(d, 108, 58, 12, 18, frame=ST_DK)
    tree(d, 14, 50, 12, ground=76)
    tree(d, 214, 52, 12, ground=76)
    lawn(d, 77)
    return im


def finlay():
    im, d, ox, oy = canvas("finlay_hall")
    W, H = im.size
    # the copper mansard roof, gone green, with dormers
    slope_roof(d, 0, 0, W - 1, 29, GREEN, NAVY, LIME)
    for x in (6, 26, 46):
        d.rectangle([x, 18, x + 10, 29], fill=ST_HI)
        window(d, x + 2, 21, 7, 7, frame=ST_HI, glass=NAVY)
    front(d, W, 32, H, "fieldstone")
    d.rectangle([0, 32, W - 1, 33], fill=ST_HI)
    for x in (36, 50):
        for y in (38, 52):
            window(d, x, y, 8, 9, frame=ST_HI, glass=NAVY)
    dx = door_px(42, 43)
    d.rectangle([dx - 4, 36, dx + 19, H - 1], fill=ST_HI)                 # limestone Gothic portal
    d.polygon([(dx - 4, 46), (dx + 7, 34), (dx + 8, 34), (dx + 19, 46)], fill=ST_HI)
    gothic_window(d, dx + 2, 40, 12, 14)
    d.rectangle([dx + 2, H - 22, dx + 13, H - 1], fill=ST_SH)
    d.pieslice([dx + 2, H - 28, dx + 13, H - 16], 180, 360, fill=ST_SH)
    door(d, dx + 3, H - 14, 10, 14, frame=ST_DK, leaf=BROWN)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def finlay_card():
    im, d = card()
    clouds(d)
    slope_roof(d, 24, 6, 204, 22, GREEN, NAVY, LIME)
    for x in range(36, 196, 24):
        d.rectangle([x, 8, x + 10, 20], fill=ST_HI)
        d.rectangle([x + 2, 11, x + 8, 19], fill=NAVY)
    fieldstone(d, 24, 22, 204, 76)
    d.rectangle([24, 22, 204, 24], fill=ST_HI)
    for y in (30, 46):
        for x in range(32, 198, 14):
            if not 98 < x < 132:
                window(d, x, y, 8, 10, frame=ST_HI, glass=NAVY)
    d.rectangle([100, 26, 130, 76], fill=ST_HI)
    gothic_window(d, 106, 30, 18, 18)
    d.pieslice([104, 52, 126, 72], 180, 360, fill=ST_SH)
    d.rectangle([104, 62, 126, 76], fill=ST_SH)
    door(d, 109, 62, 12, 14, frame=ST_DK)
    for fx in range(30, 90, 8):                                           # the hydrangeas
        d.ellipse([fx, 70, fx + 8, 78], fill=PEACH)
        d.point([fx + 3, 72], fill=WHITE)
    tree(d, 214, 48, 12, ground=78)
    lawn(d, 78)
    return im


# ---------------------------------------------------------------- Martyrs' Court
def clock_tower(d, cx, top, bottom, w=22):
    x0, x1 = cx - w // 2, cx + w // 2 - 1
    d.rectangle([x0, top + 10, x1, bottom], fill=ST)
    brick(d, x0 + 1, top + 24, x1 - 1, bottom, ST, ST_SH)
    d.rectangle([x0 - 1, top + 8, x1 + 1, top + 23], fill=ST_HI)          # white stone top
    d.rectangle([x0 + 2, top + 4, x1 - 2, top + 8], fill=ST_HI)
    d.ellipse([cx - 6, top + 10, cx + 5, top + 21], fill=WHITE)           # clock face
    d.ellipse([cx - 6, top + 10, cx + 5, top + 21], outline=NAVY)
    d.line([cx, top + 12, cx, top + 16], fill=NAVY)
    d.line([cx, top + 16, cx + 3, top + 16], fill=NAVY)
    d.line([cx, top, cx, top + 4], fill=ST_HI)                            # cross
    d.line([cx - 2, top + 1, cx + 1, top + 1], fill=ST_HI)
    d.rectangle([x0 - 1, top + 4, x1 + 1, bottom], outline=NAVY)


def martyrs():
    im, d, ox, oy = canvas("martyrs_court")
    W, H = im.size
    flat_roof(d, 0, oy, W - 1, oy + 29, rim=ST_HI, fill=ROOF, seam=ROOF_SH,
              units=((22, oy + 8), (140, oy + 10)))
    front(d, W, oy + 32, H, "brick", base=ST, mortar=ST_SH)
    dx = door_px(12, 17)
    rows_of_windows(d, 2, W - 3, (oy + 36, oy + 47, oy + 58 - 2), w=6, h=7, gap=5,
                    frame=WHITE, glass=NAVY, skip=((dx - 6, dx + 21),))
    clock_tower(d, dx + 8, 0, H - 1, w=26)
    door(d, dx + 2, H - 14, 12, 14, frame=ST_DK, leaf=BROWN)
    d.rectangle([dx - 2, H - 2, dx + 17, H - 1], fill=ST_HI)              # the famous steps
    outline(d, 0, oy, W - 1, H - 1)
    return im


def martyrs_west():
    im, d, ox, oy = canvas("martyrs_court_west")
    W, H = im.size
    flat_roof(d, 0, 0, W - 1, 77, rim=ST_HI, fill=ROOF, seam=ROOF_SH, units=((8, 20),))
    front(d, W, 80, H, "brick", base=ST, mortar=ST_SH)
    for y in (84, 95):
        window(d, 3, y, 6, 7, frame=WHITE, glass=NAVY)
        window(d, 39, y, 6, 7, frame=WHITE, glass=NAVY)
    d.rectangle([14, 82, 33, H - 1], fill=ST_HI)                          # stone entrance surround
    door(d, 18, H - 14, 12, 14, frame=ST_DK, leaf=BROWN)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def martyrs_card():
    im, d = card()
    clouds(d, ((16, 10, 26), (170, 8, 30)))
    brick(d, 4, 30, 224, 72, ST, ST_SH)
    for y in (36, 48, 60):
        for x in range(10, 220, 11):
            if not 96 < x < 134:
                window(d, x, y, 7, 8, frame=WHITE, glass=NAVY)
    clock_tower(d, 114, 0, 72, w=40)
    door(d, 106, 58, 16, 14, frame=ST_DK)
    lawn(d, 73)
    for i in range(3):                                                    # the steps, a hangout
        d.rectangle([96 - i * 4, 72 + i * 2, 132 + i * 4, 73 + i * 2], fill=ST_HI)
    for i, (x, s) in enumerate(((100, MAROON), (110, WHITE), (124, LBLUE))):
        person(d, x, 70 + (i % 2) * 2, s)
    tree(d, 20, 54, 14, ground=74)
    return im


# ---------------------------------------------------------------- modern halls
def conley_salice():
    im, d, ox, oy = canvas("conley_salice")
    W, H = im.size
    flat_roof(d, 0, 0, W - 1, 93, rim=ST, fill=ROOF, seam=ROOF_SH, units=((8, 14), (26, 60)))
    d.line([0, 46, W - 1, 46], fill=NAVY)                                 # where Conley meets Salice
    d.line([0, 47, W - 1, 47], fill=ST)
    front(d, W, 96, H, "brick", base=BRICK, mortar=BRICK_DK)
    for y in (100, 111):
        window(d, 3, y, 8, 8, frame=ST_HI)
        window(d, 37, y, 8, 8, frame=ST_HI)
    d.rectangle([14, 96, 33, H - 1], fill=NAVY)                           # glass stair tower
    d.rectangle([15, 97, 32, H - 1], fill=LBLUE)
    for gy in range(101, H - 14, 6):
        d.line([15, gy, 32, gy], fill=CYAN)
    d.rectangle([0, H - 4, W - 1, H - 1], fill=ST)                        # cast-stone base
    door(d, 18, H - 14, 12, 14, frame=NAVY, glass=True)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def conley_card():
    im, d = card()
    clouds(d)
    for bx, bw, name in ((10, 96, 0), (122, 96, 1)):                     # Conley and Salice
        brick(d, bx, 10, bx + bw, 76, BRICK, BRICK_DK)
        for y in range(16, 66, 10):
            for x in range(bx + 6, bx + bw - 6, 12):
                if not bx + 38 < x < bx + 58:
                    window(d, x, y, 8, 7, frame=ST_HI)
        d.rectangle([bx + 40, 4, bx + 56, 76], fill=NAVY)
        d.rectangle([bx + 42, 6, bx + 54, 76], fill=LBLUE)
        for gy in range(10, 76, 6):
            d.line([bx + 42, gy, bx + 54, gy], fill=CYAN)
        d.rectangle([bx, 70, bx + bw, 76], fill=ST)
    lawn(d, 77)
    d.rectangle([106, 30, 122, 87], fill=ST_HI)                           # the walk between them
    tree(d, 114, 52, 8, ground=80)
    return im


def ohare():
    im, d, ox, oy = canvas("ohare_hall")
    W, H = im.size
    # three wings, seen from above as a flat roof shaped like an E
    d.rectangle([0, 0, W - 1, 45], fill=LIME)
    for x0, x1 in ((0, 31), (56, 87), (112, 143)):
        flat_roof(d, x0, 0, x1, 45, rim=ST_HI, fill=ROOF, seam=ROOF_SH)
    flat_roof(d, 0, 22, W - 1, 45, rim=ST_HI, fill=ROOF, seam=ROOF_SH,
              units=((40, 30), (96, 30)))
    for tx in (44, 100):
        d.ellipse([tx - 6, 4, tx + 6, 16], fill=GREEN)
    front(d, W, 48, H, "fieldstone")
    for px in range(0, W, 24):                                            # limestone piers
        d.rectangle([px, 48, px + 2, H - 1], fill=ST_HI)
    d.rectangle([0, 48, W - 1, 50], fill=ST_HI)
    rows_of_windows(d, 4, W - 5, (54, 66, 78, 90), w=8, h=8, gap=4, frame=ST_HI, glass=LBLUE,
                    skip=((44, 67), (92, 115)))
    for door_x in (80, 83):
        dx = door_px(77, door_x)
        d.rectangle([dx - 2, 52, dx + 17, H - 1], fill=ST_HI)
        window(d, dx + 2, 56, 12, 10, frame=ST_HI, glass=LBLUE)
        window(d, dx + 2, 70, 12, 10, frame=ST_HI, glass=LBLUE)
        door(d, dx + 2, H - 14, 12, 14, frame=NAVY, glass=True)
    outline(d, 0, 22, W - 1, H - 1)
    for x0, x1 in ((0, 31), (56, 87), (112, 143)):
        outline(d, x0, 0, x1, 24)
    return im


def ohare_card():
    im, d = card()
    clouds(d)
    fieldstone(d, 4, 12, 224, 76)
    for px in range(4, 224, 20):
        d.rectangle([px, 12, px + 2, 76], fill=ST_HI)
    d.rectangle([4, 10, 224, 13], fill=ST_HI)
    for y in (18, 30, 42, 54):
        for x in range(10, 220, 10):
            if (x - 4) % 20 < 14 and not 100 < x < 128:
                window(d, x, y, 7, 8, frame=ST_HI)
    d.rectangle([100, 4, 128, 76], fill=ST_HI)                            # the stone tower bay
    for y in (10, 26, 42):
        window(d, 106, y, 16, 12, frame=ST_HI)
    door(d, 106, 60, 16, 16, frame=NAVY, glass=True)
    lawn(d, 77)
    d.rectangle([150, 70, 172, 72], fill=BROWN)                           # a bench, as in the photo
    person(d, 60, 68, MAROON)
    tree(d, 210, 56, 12, ground=77)
    return im


def tierney():
    im, d, ox, oy = canvas("tierney_hall")
    W, H = im.size
    flat_roof(d, 0, 0, W - 1, 29, rim=ST_HI, fill=ROOF, seam=ROOF_SH, units=((60, 8),))
    front(d, W, 32, H, "panel", base=WHITE)
    for x in range(0, W, 12):                                             # panel joints
        d.line([x, 32, x, H - 1], fill=ST_HI)
    d.rectangle([0, 32, 17, H - 1], fill=BRICK)                           # the dark brick end
    brick(d, 0, 32, 17, H - 1, BRICK, BRICK_DK)
    for x in range(22, W - 4, 13):
        if not 44 < x < 66:
            window(d, x, 36, 10, 8, frame=GRAY, glass=LBLUE)
            window(d, x, 48, 10, 8, frame=GRAY, glass=LBLUE)
    dx = door_px(76, 78)
    d.rectangle([dx - 2, 34, dx + 17, H - 1], fill=GRAY)                  # glass stair bay
    d.rectangle([dx, 36, dx + 15, H - 15], fill=LBLUE)
    d.line([dx + 7, 36, dx + 7, H - 15], fill=WHITE)
    door(d, dx + 2, H - 14, 12, 14, frame=NAVY, glass=True)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def tierney_card():
    im, d = card()
    clouds(d)
    d.rectangle([40, 20, 210, 76], fill=WHITE)
    for x in range(40, 210, 14):
        d.line([x, 20, x, 76], fill=ST_HI)
    brick(d, 20, 20, 44, 76, BRICK, BRICK_DK)
    for y in (26, 42, 58):
        for x in range(52, 204, 18):
            window(d, x, y, 13, 10, frame=GRAY)
    d.rectangle([20, 18, 210, 20], fill=ST)
    door(d, 120, 62, 14, 14, frame=NAVY, glass=True)
    tree(d, 200, 44, 16, ground=76)
    lawn(d, 77)
    d.rectangle([0, 80, 227, 87], fill=GRAY)                              # the drive
    return im


def walsh_hall():
    im, d, ox, oy = canvas("walsh_hall")
    W, H = im.size
    # thirteen storeys: a small roof, and the tall front shows most of it
    flat_roof(d, 0, 0, W - 1, 13, rim=ST, fill=ROOF, seam=ROOF_SH, units=((30, 3),))
    front(d, W, 16, H, "brick", base=BROWN, mortar=PBRICK_SH)
    for px in range(0, W, 10):                                            # the vertical piers
        d.rectangle([px, 16, px + 1, H - 1], fill=PBRICK)
    for y in range(19, H - 16, 6):
        for x in range(3, W - 2, 10):
            d.rectangle([x, y, x + 5, y + 3], fill=NAVY)
            d.line([x, y, x + 5, y], fill=LBLUE)
    dx = door_px(52, 54)
    d.rectangle([0, H - 14, W - 1, H - 1], fill=ST_DK)                    # ground-floor lobby
    d.rectangle([2, H - 12, W - 3, H - 4], fill=LBLUE)
    d.rectangle([dx - 4, H - 18, dx + 19, H - 15], fill=ST_HI)            # canopy
    door(d, dx + 2, H - 14, 12, 14, frame=NAVY, glass=True)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def walsh_hall_card():
    im, d = card()
    clouds(d, ((10, 8, 24), (176, 12, 30)))
    brick(d, 84, 0, 144, 76, BROWN, PBRICK_SH)
    for px in range(84, 144, 8):
        d.rectangle([px, 0, px + 1, 76], fill=PBRICK)
    for y in range(2, 66, 5):
        for x in range(87, 142, 8):
            d.rectangle([x, y, x + 4, y + 2], fill=NAVY)
    d.rectangle([84, 66, 144, 76], fill=ST_DK)
    d.rectangle([86, 68, 142, 76], fill=LBLUE)
    door(d, 108, 66, 12, 10, frame=NAVY, glass=True)
    tree(d, 40, 50, 16, ground=76)
    tree(d, 190, 54, 14, ground=76)
    lawn(d, 77)
    d.rectangle([0, 80, 227, 87], fill=GRAY)                              # East 191st Street side
    return im


def faber():
    im, d, ox, oy = canvas("faber_hall")
    W, H = im.size
    flat_roof(d, 0, 0, W - 1, 21, rim=ST_HI, fill=ROOF, seam=ROOF_SH, units=((20, 6),))
    front(d, W, 24, H, "brick", base=ST_HI, mortar=ST)
    for y in (28, 38, 48, 58):
        d.line([0, y + 8, W - 1, y + 8], fill=ST)                         # horizontal bands
        window(d, 3, y, 8, 7, frame=WHITE, glass=NAVY)
        window(d, 37, y, 8, 7, frame=WHITE, glass=NAVY)
    d.rectangle([14, 26, 33, H - 1], fill=ST)                             # stair bay with slots
    for y in range(30, H - 16, 6):
        d.rectangle([22, y, 25, y + 3], fill=NAVY)
    door(d, 18, H - 14, 12, 14, frame=ST_DK, glass=True)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def faber_card():
    im, d = card()
    clouds(d)
    brick(d, 60, 4, 168, 76, ST_HI, ST)
    for y in range(8, 70, 9):
        d.line([60, y + 7, 168, y + 7], fill=ST)
        for x in range(66, 164, 14):
            if not 104 < x < 124:
                window(d, x, y, 9, 6, frame=WHITE, glass=NAVY)
    d.rectangle([106, 4, 122, 76], fill=ST)
    door(d, 108, 62, 12, 14, frame=ST_DK, glass=True)
    ashlar(d, 168, 30, 222, 76, base=ST, joint=ST_SH)                     # Loyola next door
    battlements(d, 168, 222, 30, fill=ST_SH)
    tree(d, 30, 50, 16, ground=76)
    lawn(d, 77)
    return im


if __name__ == "__main__":
    save_building("loschert_hall", loschert(), loschert_card())
    save_building("alumni_court_south", alumni_south(), alumni_south_card())
    save_building("queens_court", queens_court(), queens_card())
    save_building("faber_hall", faber(), faber_card())
    save_building("loyola_hall", loyola(), loyola_card())
    save_building("martyrs_court", martyrs(), martyrs_card())
    save_building("martyrs_court_west", martyrs_west())
    save_building("conley_salice", conley_salice(), conley_card())
    save_building("ohare_hall", ohare(), ohare_card())
    save_building("tierney_hall", tierney(), tierney_card())
    save_building("finlay_hall", finlay(), finlay_card())
    save_building("walsh_hall", walsh_hall(), walsh_hall_card())
