"""First drafts (decisions/0023) for the athletics batch, in the house
style: Lombardi Memorial Center, McShane Campus Center, Rose Hill Gym,
Moglia Stadium, Jack Coffey Field, Houlihan Park, Murphy Field, Bahoshy
Softball Field and the tennis courts.

    uv run python assets/buildings/_style/draw_athletics.py
"""

from kit import *  # noqa: F401,F403
from kit import (BROWN, CYAN, DBLUE, GRAY, GREEN, LBLUE, LIME, MAROON, NAVY, ORANGE, PEACH,
                 PINK, RED, ROOF, ROOF_SH, ST, ST_DK, ST_HI, ST_SH, WHITE, YELLOW,
                 arched_window, ashlar, battlements, canvas, card, clouds, diamond, door, eave,
                 fieldstone, flat_roof, fordham_f, gothic_window, lawn, light_tower, outline,
                 panels, person, save_building, tree, turf, window, BRICK_DK, slope_roof)


# ---------------------------------------------------------------- buildings
def lombardi():
    """The back of the complex (D-0023 update): two big cream boxes for the
    fieldhouse and pool, white barrel vaults behind McShane, and the
    Lombardi entrance where the building pokes out east of the gym."""
    im, d, ox, oy = canvas("lombardi_center")
    W, H = im.size                                                        # 288 x 112
    # white barrel vaults (behind McShane), running front to back
    for vx in range(0, 128, 16):
        d.rectangle([vx, 4, vx + 15, 92], fill=ST)
        d.rectangle([vx + 2, 4, vx + 13, 92], fill=ST_HI)
        d.rectangle([vx + 5, 4, vx + 10, 92], fill=WHITE)
        d.line([vx, 4, vx, 92], fill=ST_SH)
        d.pieslice([vx, 0, vx + 15, 9], 180, 360, fill=ST_HI)
    d.rectangle([0, 93, 127, H - 1], fill=NAVY)                           # glass link along McShane
    d.rectangle([1, 94, 126, H - 1], fill=LBLUE)
    for gx in range(6, 127, 8):
        d.line([gx, 94, gx, H - 1], fill=WHITE)
    outline(d, 0, 0, 127, H - 1)
    # the two big cream boxes: fieldhouse (with its indoor track) and pool
    flat_roof(d, 128, 0, 207, 79, rim=ST_HI, fill=ST_HI, seam=ST, units=((150, 20),))
    flat_roof(d, 208, 6, W - 1, 79, rim=ST_HI, fill=ST_HI, seam=ST, units=((250, 30),))
    eave(d, 128, W - 1, 80)
    ashlar(d, 128, 82, W - 1, H - 1, base=ST_HI, joint=ST, step=6)
    for px in range(132, W - 2, 12):                                      # tall cream panels
        d.line([px, 82, px, H - 1], fill=ST)
    for wx in range(138, 236, 24):
        d.rectangle([wx, 86, wx + 12, 96], fill=NAVY)
        d.rectangle([wx + 1, 87, wx + 11, 95], fill=LBLUE)
    # the entrance, on the part you can see from the walkway
    d.rectangle([244, 84, 283, H - 1], fill=NAVY)                         # glass entrance bay
    d.rectangle([246, 86, 281, H - 1], fill=LBLUE)
    for gx in range(250, 281, 6):
        d.line([gx, 86, gx, H - 1], fill=DBLUE)
    d.rectangle([240, 82, 243, H - 1], fill=MAROON)                       # banner
    door(d, 258, H - 14, 12, 14, frame=NAVY, glass=True)
    outline(d, 128, 0, W - 1, H - 1)
    d.line([207, 0, 207, 79], fill=NAVY)
    return im


def lombardi_card():
    im, d = card()
    clouds(d)
    panels(d, 10, 20, 150, 52, base=GRAY, rib=ROOF, step=3)
    ashlar(d, 10, 52, 150, 74, base=ST_HI, joint=ST)
    panels(d, 150, 8, 220, 74, base=ROOF, rib=ROOF_SH, step=4)
    for x0 in range(16, 140, 16):
        window(d, x0, 58, 10, 9)
    d.rectangle([100, 30, 140, 74], fill=NAVY)
    d.rectangle([102, 32, 138, 74], fill=LBLUE)
    for gx in range(106, 138, 6):
        d.line([gx, 32, gx, 74], fill=DBLUE)
    d.rectangle([60, 40, 96, 48], fill=MAROON)                            # sign
    for lx in range(64, 92, 4):
        d.point([lx, 44], fill=WHITE)
    tree(d, 200, 50, 14, ground=74)
    lawn(d, 75)
    for i, s in enumerate((MAROON, WHITE, DBLUE)):
        person(d, 110 + i * 8, 66, s)
    return im


def mcshane():
    """McShane (2021) at the front of the complex: limestone with vertical
    fins, the glass tower, and the glass link to the gym with the main
    entrance (D-0023 update)."""
    im, d, ox, oy = canvas("mcshane_center")
    W, H = im.size                                                        # 160 x 106
    top = oy
    d.rectangle([0, top, 109, top + 9], fill=ST)                          # roof strip
    d.rectangle([2, top + 2, 107, top + 7], fill=ST_HI)
    eave(d, 0, 109, top + 10)
    ashlar(d, 0, top + 12, 109, H - 1, base=ST_HI, joint=ST, step=6)      # limestone
    for fx in range(4, 108, 8):                                           # vertical fins + windows
        d.rectangle([fx, top + 14, fx + 4, H - 14], fill=NAVY)
        d.rectangle([fx + 1, top + 15, fx + 3, H - 15], fill=LBLUE)
        for wy in range(top + 18, H - 16, 9):
            d.point([fx + 2, wy], fill=YELLOW)                            # warm lit rooms
        d.line([fx + 6, top + 12, fx + 6, H - 14], fill=ST_SH)
    d.rectangle([0, H - 13, 109, H - 1], fill=ST)                         # ground floor
    for gx in range(4, 106, 12):
        d.rectangle([gx, H - 11, gx + 8, H - 2], fill=LBLUE)
    outline(d, 0, top, 109, H - 1)
    # the glass tower, rising above the roof
    d.rectangle([110, 0, 143, H - 1], fill=NAVY)
    d.rectangle([112, 2, 141, H - 1], fill=LBLUE)
    for gx in range(116, 141, 5):
        d.line([gx, 2, gx, H - 1], fill=WHITE)
    for gy in range(8, H - 2, 8):
        d.line([112, gy, 141, gy], fill=CYAN)
    # the low glass link to the gym, with the main entrance
    d.rectangle([144, top, W - 1, top + 27], fill=ST)                     # its flat roof
    d.rectangle([146, top + 2, W - 1, top + 25], fill=ST_HI)
    d.line([144, top, W - 1, top], fill=NAVY)
    d.rectangle([144, top + 30, W - 1, H - 1], fill=NAVY)
    d.rectangle([144, top + 32, W - 1, H - 1], fill=LBLUE)
    d.rectangle([144, top + 28, W - 1, top + 31], fill=ST_HI)
    for gx in range(148, W, 5):
        d.line([gx, top + 32, gx, H - 16], fill=WHITE)
    door(d, 146, H - 14, 12, 14, frame=NAVY, glass=True)
    d.line([110, 0, 143, 0], fill=NAVY)
    return im


def mcshane_card():
    im, d = card()
    clouds(d, ((20, 8, 24), (120, 4, 20)))
    ashlar(d, 6, 14, 150, 76, base=ST_HI, joint=ST, step=6)
    for fx in range(10, 146, 9):
        d.rectangle([fx, 18, fx + 4, 70], fill=NAVY)
        d.rectangle([fx + 1, 19, fx + 3, 69], fill=YELLOW if (fx // 9) % 3 else LBLUE)
        d.line([fx + 6, 14, fx + 6, 70], fill=ST_SH)
    d.rectangle([150, 2, 196, 76], fill=NAVY)                             # glass tower
    d.rectangle([152, 4, 194, 76], fill=LBLUE)
    for gx in range(156, 194, 5):
        d.line([gx, 4, gx, 76], fill=WHITE)
    d.rectangle([196, 34, 208, 76], fill=NAVY)                            # glass link to the gym
    d.rectangle([197, 36, 207, 76], fill=YELLOW)
    fieldstone(d, 208, 30, 227, 76, base=ST_SH, light=ST, dark=ST_DK)       # the gym's Gothic end
    d.polygon([(208, 30), (227, 12), (227, 30)], fill=ROOF_SH)
    gothic_window(d, 216, 40, 10, 18)
    lawn(d, 77)
    for i, s in enumerate((MAROON, LBLUE, WHITE)):
        person(d, 120 + i * 9, 68, s)
    return im


def gym():
    """Rose Hill Gym (1925), the old Gothic end of the complex: a big slate
    roof with its ridge running back from the front, a raised clerestory
    along the ridge, and the fieldstone gable front (D-0023 update)."""
    im, d, ox, oy = canvas("rose_hill_gym")
    W, H = im.size                                                        # 112 x 102
    cx = W // 2
    roof_bottom = oy + 46
    # the two slopes of the big pitched roof, ridge down the middle
    slope_left, slope_right = ROOF_SH, ROOF
    d.rectangle([2, 0, cx - 1, roof_bottom], fill=slope_left)
    d.rectangle([cx, 0, W - 3, roof_bottom], fill=slope_right)
    for x in range(6, W - 4, 6):                                          # slate courses
        d.line([x, 0, x, roof_bottom], fill=NAVY if x < cx else ROOF_SH)
    # the raised clerestory monitor along the ridge
    d.rectangle([cx - 12, 0, cx + 11, roof_bottom - 6], fill=ST_DK)
    d.rectangle([cx - 10, 2, cx + 9, roof_bottom - 8], fill=ROOF)
    d.line([cx, 2, cx, roof_bottom - 8], fill=GRAY)
    d.rectangle([cx - 12, 4, cx - 11, roof_bottom - 8], fill=LBLUE)       # its glass sides
    d.rectangle([cx + 10, 4, cx + 11, roof_bottom - 8], fill=LBLUE)
    outline(d, 2, 0, W - 3, roof_bottom)
    # dark fieldstone front with the pointed gable over the entrance
    front_top = roof_bottom + 2
    fieldstone(d, 0, front_top, W - 1, H - 1, base=ST_SH, light=ST, dark=ST_DK)
    d.polygon([(cx - 30, front_top + 2), (cx, front_top - 18), (cx + 29, front_top + 2)], fill=ST_SH)
    d.polygon([(cx - 26, front_top + 2), (cx, front_top - 14), (cx + 25, front_top + 2)], fill=ST_DK)
    d.line([cx - 30, front_top + 2, cx, front_top - 18], fill=ST_HI)       # stone coping
    d.line([cx, front_top - 18, cx + 29, front_top + 2], fill=ST_HI)
    d.line([cx, front_top - 24, cx, front_top - 18], fill=ST_HI)           # stone cross
    d.line([cx - 2, front_top - 22, cx + 2, front_top - 22], fill=ST_HI)
    gothic_window(d, cx - 13, front_top - 6, 26, 24)                      # the great window, lit
    for gy in range(front_top + 8, front_top + 17, 3):
        d.line([cx - 12, gy, cx + 11, gy], fill=YELLOW)
    for x0 in (8, 22, 82, 96):                                            # side windows
        arched_window(d, x0, front_top + 8, 7, 11, frame=ST_HI, glass=NAVY)
    d.rectangle([0, front_top, 3, H - 1], fill=ST_SH)                     # corner buttresses
    d.rectangle([W - 4, front_top, W - 1, H - 1], fill=ST_SH)
    for dx in (cx - 18, cx - 6, cx + 6):                                  # three wooden doors
        door(d, dx, H - 14, 10, 14, frame=ST_SH, leaf=BROWN)
    outline(d, 0, front_top, W - 1, H - 1)
    return im


def gym_card():
    im, d = card()
    clouds(d)
    d.rectangle([110, 8, 220, 40], fill=ST_DK)                             # arched roof behind
    d.pieslice([110, 0, 220, 20], 180, 360, fill=ST_DK)
    d.rectangle([112, 22, 218, 36], fill=LBLUE)
    for gx in range(114, 218, 5):
        d.line([gx, 22, gx, 36], fill=WHITE)
    fieldstone(d, 20, 34, 220, 76, base=ST, light=ST_HI, dark=ST_SH)
    battlements(d, 20, 220, 34, h=3, step=4, fill=ST_SH, top=ST_HI)
    d.rectangle([70, 14, 130, 76], fill=ST_HI)                             # the great arch
    d.polygon([(70, 24), (100, 4), (130, 24)], fill=ST_HI)
    gothic_window(d, 80, 18, 40, 30)
    for dx in (82, 95, 108):
        door(d, dx, 56, 10, 20, frame=ST_SH)
    for x0 in (30, 46, 150, 170, 190):
        window(d, x0, 44, 9, 11, frame=ST_HI)
    # the Victory Bell on its little pagoda roof
    d.rectangle([40, 52, 52, 76], fill=ST_SH)
    d.polygon([(36, 52), (46, 44), (56, 52)], fill=NAVY)
    d.ellipse([42, 54, 50, 62], fill=YELLOW)
    lawn(d, 77)
    for i in range(4):
        d.rectangle([84 - i * 4, 76 + i * 2, 116 + i * 4, 77 + i * 2], fill=ST_HI)
    return im


# ---------------------------------------------------------------- landmarks
def moglia():
    im, d, ox, oy = canvas("moglia_stadium")
    W, H = im.size
    # aluminum bleachers stepping down toward the field (south)
    for i, y in enumerate(range(14, H, 3)):
        d.rectangle([0, y, W - 1, y + 2], fill=GRAY if i % 2 else WHITE)
    d.rectangle([56, 18, 103, H - 1], fill=MAROON)                         # maroon seat section
    for y in range(19, H, 3):
        d.line([56, y, 103, y], fill=PINK)
    for ax in range(8, W, 30):                                             # aisles
        d.line([ax, 14, ax, H - 1], fill=ROOF_SH)
    # the press box on top, with FORDHAM along the front
    d.rectangle([40, 0, 119, 13], fill=WHITE)
    d.rectangle([40, 0, 119, 2], fill=GRAY)
    d.rectangle([44, 4, 115, 7], fill=NAVY)
    d.rectangle([48, 9, 111, 12], fill=MAROON)
    for lx in range(52, 108, 8):
        d.rectangle([lx, 10, lx + 3, 11], fill=WHITE)
    for tx in (4, W - 6):
        light_tower(d, tx, 2, 10)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def moglia_card():
    im, d = card()
    clouds(d)
    d.rectangle([60, 6, 200, 30], fill=WHITE)                              # press box
    d.rectangle([64, 10, 196, 18], fill=NAVY)
    d.rectangle([70, 21, 190, 28], fill=WHITE)
    for i, lx in enumerate(range(78, 182, 14)):                            # F O R D H A M
        d.rectangle([lx, 22, lx + 8, 27], fill=MAROON)
    for i, y in enumerate(range(32, 80, 4)):
        d.polygon([(0, y + 10), (228, y - 6), (228, y - 3), (0, y + 13)], fill=GRAY if i % 2 else WHITE)
    d.polygon([(120, 52), (228, 44), (228, 76), (150, 82)], fill=MAROON)   # maroon seats
    for y in range(50, 84, 4):
        d.line([120, y + 4, 228, y - 4], fill=PINK)
    light_tower(d, 20, 4, 40)
    return im


def jack_coffey():
    im, d, ox, oy = canvas("jack_coffey_field")
    W, H = im.size
    d.rectangle([0, 0, W - 1, H - 1], fill=GREEN)                          # surround
    x0, x1, y0, y1 = 10, W - 11, 8, H - 9
    turf(d, x0, y0, x1, y1, stripe=17)
    d.rectangle([x0, y0, x0 + 17, y1], fill=MAROON)                        # end zones
    d.rectangle([x1 - 17, y0, x1, y1], fill=MAROON)
    for zx in (x0 + 8, x1 - 8):
        for zy in range(y0 + 12, y1 - 10, 8):
            d.point([zx, zy], fill=WHITE)
    d.rectangle([x0, y0, x1, y1], outline=WHITE)
    for yx in range(x0 + 17, x1 - 16, 17):                                 # yard lines
        d.line([yx, y0, yx, y1], fill=WHITE)
        for hy in (y0 + 28, y1 - 28):
            d.point([yx + 8, hy], fill=WHITE)
    fordham_f(d, W // 2, H // 2, 8)
    for gx in (x0 - 4, x1 + 4):                                            # goal posts
        d.line([gx, H // 2 - 8, gx, H // 2 + 8], fill=YELLOW)
        d.line([gx - 3 if gx < W // 2 else gx + 3, H // 2, gx, H // 2], fill=YELLOW)
    for tx, ty in ((3, 2), (W - 5, 2), (3, H - 14), (W - 5, H - 14)):
        light_tower(d, tx, ty, 10)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def jack_coffey_card():
    im, d = card()
    clouds(d)
    d.rectangle([40, 14, 140, 24], fill=WHITE)                             # stands across the field
    d.rectangle([44, 16, 136, 19], fill=NAVY)
    for i, y in enumerate(range(24, 44, 3)):
        d.rectangle([20, y, 200, y + 2], fill=GRAY if i % 2 else WHITE)
    d.rectangle([150, 26, 200, 43], fill=MAROON)
    light_tower(d, 12, 2, 40)
    light_tower(d, 214, 2, 40)
    turf(d, 0, 44, 227, 87, stripe=12, vertical=False)
    for x in range(10, 228, 36):
        d.line([x, 44, x - 20, 87], fill=WHITE)
    d.line([0, 50, 227, 50], fill=WHITE)
    d.rectangle([0, 76, 30, 87], fill=WHITE)                               # soccer goal
    d.rectangle([2, 78, 28, 87], fill=GREEN)
    for i, s in enumerate((MAROON, MAROON, WHITE, MAROON)):
        person(d, 90 + i * 22, 60 + (i % 2) * 6, s)
    return im


def houlihan():
    im, d, ox, oy = canvas("houlihan_park")
    W, H = im.size
    diamond(d, 0, 0, W, H, infield=PEACH, base_path=ST_HI, track=BROWN)
    d.rectangle([W // 2 - 24, H - 5, W // 2 + 24, H - 1], fill=GRAY)      # grandstand behind home
    d.rectangle([W // 2 - 12, 2, W // 2 + 12, 9], fill=NAVY)              # scoreboard
    d.rectangle([W // 2 - 10, 4, W // 2 + 10, 7], fill=YELLOW)
    for tx in (4, W - 6):
        light_tower(d, tx, 3, 10)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def murphy():
    im, d, ox, oy = canvas("murphy_field")
    W, H = im.size
    d.rectangle([0, 0, W - 1, H - 1], fill=GREEN)
    x0, x1, y0, y1 = 8, W - 9, 6, H - 22
    turf(d, x0, y0, x1, y1, stripe=16)
    d.rectangle([x0, y0, x1, y1], outline=WHITE)
    d.line([W // 2, y0, W // 2, y1], fill=WHITE)
    d.ellipse([W // 2 - 14, (y0 + y1) // 2 - 14, W // 2 + 14, (y0 + y1) // 2 + 14], outline=WHITE)
    for gx, sgn in ((x0, 1), (x1, -1)):                                     # penalty boxes + goals
        d.rectangle([min(gx, gx + sgn * 20), (y0 + y1) // 2 - 18,
                     max(gx, gx + sgn * 20), (y0 + y1) // 2 + 18], outline=WHITE)
        d.line([gx - sgn * 3, (y0 + y1) // 2 - 6, gx - sgn * 3, (y0 + y1) // 2 + 6], fill=WHITE)
    fordham_f(d, W // 2, (y0 + y1) // 2, 6)
    for tx, ty in ((2, 2), (W - 4, 2)):
        light_tower(d, tx, ty, 10)
    # the stone MURPHY FIELD archway at the south edge, with its iron gates
    ax0, ax1 = W // 2 - 26, W // 2 + 26
    fieldstone(d, ax0, H - 20, ax0 + 9, H - 1, base=ST_SH, light=ST, dark=ST_DK)
    fieldstone(d, ax1 - 9, H - 20, ax1, H - 1, base=ST_SH, light=ST, dark=ST_DK)
    d.rectangle([ax0, H - 22, ax1, H - 16], fill=ST_HI)
    d.arc([ax0 + 8, H - 26, ax1 - 8, H - 10], 180, 360, fill=ST_HI)
    for lx in range(ax0 + 12, ax1 - 10, 4):                                 # "MURPHY FIELD"
        d.point([lx, H - 19], fill=NAVY)
    for gx in range(ax0 + 11, ax1 - 9, 3):                                  # iron gates
        d.line([gx, H - 15, gx, H - 1], fill=NAVY)
    d.rectangle([0, H - 21, ax0 - 1, H - 18], fill=NAVY)                    # fence along the field
    d.rectangle([ax1 + 1, H - 21, W - 1, H - 18], fill=NAVY)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def murphy_card():
    im, d = card()
    clouds(d)
    turf(d, 0, 40, 227, 87, stripe=10, vertical=False)
    light_tower(d, 200, 4, 40)
    for fx in range(0, 228, 6):                                             # iron fence
        d.line([fx, 44, fx, 74], fill=NAVY)
    d.line([0, 44, 227, 44], fill=NAVY)
    fieldstone(d, 70, 14, 90, 80, base=ST_SH, light=ST, dark=ST_DK)        # stone archway
    fieldstone(d, 138, 14, 158, 80, base=ST_SH, light=ST, dark=ST_DK)
    d.rectangle([70, 8, 158, 22], fill=ST_SH)
    d.pieslice([90, 18, 138, 50], 180, 360, fill=LBLUE)
    d.arc([86, 6, 142, 40], 180, 360, fill=ST_HI)
    for i, lx in enumerate(range(94, 136, 4)):                              # MURPHY FIELD letters
        d.rectangle([lx, 10, lx + 2, 13], fill=ST_HI)
    for gx in range(92, 138, 4):
        d.line([gx, 34, gx, 80], fill=NAVY)
    d.rectangle([110, 56, 118, 62], fill=ST_DK)                              # the bust on its plinth
    d.rectangle([108, 63, 120, 80], fill=ST_HI)
    lawn(d, 80)
    return im


def bahoshy():
    im, d, ox, oy = canvas("bahoshy_field")
    W, H = im.size
    diamond(d, 0, 0, W, H, infield=ORANGE, base_path=PEACH, track=RED)
    d.rectangle([4, H - 8, 28, H - 4], fill=NAVY)                            # dugouts
    d.rectangle([W - 29, H - 8, W - 5, H - 4], fill=NAVY)
    light_tower(d, W - 5, 3, 10)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def tennis():
    im, d, ox, oy = canvas("tennis_courts")
    W, H = im.size
    d.rectangle([0, 0, W - 1, H - 1], fill=GREEN)
    for cy in range(3):
        for cx in range(2):
            x0, y0 = 3 + cx * 30, 3 + cy * 31
            d.rectangle([x0, y0, x0 + 27, y0 + 28], fill=DBLUE)
            d.rectangle([x0 + 4, y0 + 3, x0 + 23, y0 + 25], outline=WHITE)
            d.line([x0 + 4, y0 + 14, x0 + 23, y0 + 14], fill=NAVY)           # net
            d.line([x0 + 13, y0 + 7, x0 + 13, y0 + 21], fill=WHITE)
    for fx in range(0, W, 3):                                                # fence
        d.point([fx, 0], fill=NAVY)
        d.point([fx, H - 1], fill=NAVY)
    outline(d, 0, 0, W - 1, H - 1)
    return im


if __name__ == "__main__":
    save_building("lombardi_center", lombardi(), lombardi_card())
    save_building("mcshane_center", mcshane(), mcshane_card())
    save_building("rose_hill_gym", gym(), gym_card())
    save_building("moglia_stadium", moglia(), moglia_card())
    save_building("jack_coffey_field", jack_coffey(), jack_coffey_card())
    save_building("houlihan_park", houlihan())
    save_building("murphy_field", murphy(), murphy_card())
    save_building("bahoshy_field", bahoshy())
    save_building("tennis_courts", tennis())
