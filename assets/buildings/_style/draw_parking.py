"""The east side's parking (decisions/0026): the surface lot by the Main
Entrance as a drawn landmark with parked cars, and the Regional Parking
Facility as a drawn building with cars on its top deck, a down ramp,
stair towers and open parking levels on its front.

    uv run python assets/buildings/_style/draw_parking.py
"""

from kit import (CAR_COLORS, DBLUE, GRAY, LBLUE, MAROON, NAVY, ROOF, ROOF_SH, ST, ST_DK,
                 ST_HI, ST_SH, WHITE, YELLOW, canvas, car, card, clouds, door, eave, lawn,
                 meta, outline, p_sign, person, save_building, tree)

ASPHALT, ASPHALT_DK = GRAY, ROOF


# ---------------------------------------------------------------- the surface lot
LOT_ROWS = {  # footprint row -> which way its cars face (toward the aisle)
    0: "down", 3: "up", 4: "down", 7: "up", 8: "down", 11: "up"}


def parking_lot():
    im, d, ox, oy = canvas("parking_lot")
    W, H = im.size                                                        # 128 x 192
    fp = meta("parking_lot")["footprint"]
    d.rectangle([0, 0, W - 1, H - 1], fill=ASPHALT)
    for k in range(60):                                                   # asphalt grit
        d.point([(k * 37) % W, (k * 53) % H], fill=ASPHALT_DK)
    for row, nose in LOT_ROWS.items():
        y0 = row * 16
        for col in range(9):                                              # stall lines
            x = col * 16
            if nose == "down":
                d.line([x, y0, x, y0 + 13], fill=WHITE)
            else:
                d.line([x, y0 + 2, x, y0 + 15], fill=WHITE)
        for col in range(8):
            if fp[row][col] == "c":
                car(d, col * 16 + 4, y0 + 1, CAR_COLORS[(row * 5 + col * 3) % len(CAR_COLORS)], nose)
    for row in (1, 5, 9):                                                 # aisle arrows
        for ax in (40, 88):
            cy = row * 16 + 16
            d.line([ax - 5, cy, ax + 4, cy], fill=WHITE)
            d.line([ax + 2, cy - 2, ax + 4, cy], fill=WHITE)
            d.line([ax + 2, cy + 2, ax + 4, cy], fill=WHITE)
    # the parking sign by the entrance (row 7, first stall)
    d.line([7, 7 * 16 + 6, 7, 7 * 16 + 15], fill=NAVY)
    p_sign(d, 3, 7 * 16 - 2, 9)
    d.rectangle([0, 0, W - 1, H - 1], outline=ST)                         # kerb
    return im


# ---------------------------------------------------------------- the garage
def stair_tower(d, x0, y0, x1, y1):
    """A stair / elevator tower: concrete box, glass front, flat roof."""
    d.rectangle([x0, y0, x1, y1], fill=ST)
    d.rectangle([x0 + 1, y0 + 1, x1 - 1, y0 + 5], fill=ST_HI)              # its roof
    d.rectangle([x0 + 3, y0 + 7, x1 - 3, y1 - 2], fill=LBLUE)              # glass
    for gy in range(y0 + 10, y1 - 2, 5):
        d.line([x0 + 3, gy, x1 - 3, gy], fill=DBLUE)                       # the stairs inside
    d.rectangle([x0, y0, x1, y1], outline=NAVY)


def ramp(d, x0, y0, x1, y1):
    """The down ramp: darker concrete, stripes and arrows pointing down."""
    d.rectangle([x0, y0, x1, y1], fill=ROOF)
    for y in range(y0 + 2, y1, 6):
        d.line([x0 + 1, y, x1 - 1, y], fill=ROOF_SH)                       # grooves
    d.line([x0, y0, x0, y1], fill=YELLOW)                                 # yellow edge lines
    d.line([x1, y0, x1, y1], fill=YELLOW)
    cx = (x0 + x1) // 2
    for ay in range(y0 + 10, y1 - 8, 24):                                 # painted arrows
        d.line([cx, ay, cx, ay + 10], fill=WHITE)
        d.line([cx - 3, ay + 7, cx, ay + 10], fill=WHITE)
        d.line([cx + 3, ay + 7, cx, ay + 10], fill=WHITE)
    d.rectangle([x0, y0, x1, y1], outline=NAVY)


def garage():
    im, d, ox, oy = canvas("regional_parking")
    W, H = im.size                                                        # 144 x 160
    deck_bottom = 109
    # the top deck
    d.rectangle([0, 0, W - 1, deck_bottom], fill=ST)                       # parapet
    d.rectangle([3, 3, W - 4, deck_bottom - 3], fill=ASPHALT)
    for k in range(50):
        d.point([4 + (k * 41) % (W - 8), 4 + (k * 29) % (deck_bottom - 8)], fill=ROOF)
    # stalls: a row along the north wall, a double row in the middle,
    # a row along the south wall
    rows = ((5, "down"), (46, "up"), (61, "down"), (93, "up"))
    for r, (y0, nose) in enumerate(rows):
        for i, x in enumerate(range(26, 108, 12)):
            d.line([x - 2, y0, x - 2, y0 + 14], fill=WHITE)
            if (r * 3 + i * 2) % 5 != 0:                                  # most stalls taken
                car(d, x + 1, y0 + 1, CAR_COLORS[(r * 7 + i * 5) % len(CAR_COLORS)], nose)
        d.line([108, y0, 108, y0 + 14], fill=WHITE)
    for ly in (34, 82):                                                   # light poles
        for lx in (40, 88):
            d.ellipse([lx - 2, ly - 2, lx + 2, ly + 2], fill=NAVY)
            d.point([lx, ly], fill=YELLOW)
    ramp(d, 114, 6, W - 6, deck_bottom - 6)                               # down to the lower levels
    stair_tower(d, 4, 4, 21, 27)                                          # NW stair / elevator
    eave(d, 0, W - 1, deck_bottom + 1)
    # the front: open parking levels with cars inside, over the ground floor
    front_top = deck_bottom + 3
    d.rectangle([0, front_top, W - 1, H - 1], fill=ST_HI)
    for ly in (front_top + 3, front_top + 18):                            # two open levels
        d.rectangle([24, ly, W - 4, ly + 10], fill=NAVY)
        for i, cx in enumerate(range(30, W - 12, 15)):                    # cars seen side-on
            if (i + ly) % 3:
                col = CAR_COLORS[(i * 3 + ly) % len(CAR_COLORS)]
                d.rectangle([cx, ly + 5, cx + 11, ly + 9], fill=col)
                d.rectangle([cx + 2, ly + 2, cx + 8, ly + 5], fill=col)
                d.rectangle([cx + 3, ly + 3, cx + 7, ly + 4], fill=LBLUE)
        d.line([24, ly + 11, W - 4, ly + 11], fill=ST)                     # concrete spandrel
    # ground floor: pedestrian doors and the car entrance with its barrier
    gy = H - 15
    d.rectangle([0, gy - 1, W - 1, gy - 1], fill=ST)
    d.rectangle([44, gy, 83, H - 1], fill=ST)
    door(d, 50, H - 14, 12, 14, frame=NAVY, glass=True)
    door(d, 66, H - 14, 12, 14, frame=NAVY, glass=True)
    d.rectangle([96, gy, W - 6, H - 1], fill=NAVY)                         # car entrance
    for bx in range(98, W - 10, 4):                                       # striped barrier arm
        d.line([bx, H - 8, bx + 1, H - 8], fill=YELLOW)
        d.line([bx + 2, H - 8, bx + 3, H - 8], fill=WHITE)
    d.rectangle([W - 10, H - 11, W - 7, H - 1], fill=ST_DK)                # ticket post
    p_sign(d, 106, gy - 12, 11)
    # the stair tower at the front corner
    stair_tower(d, 2, front_top - 8, 21, H - 1)
    door(d, 7, H - 12, 10, 12, frame=NAVY, glass=True)
    outline(d, 0, 0, W - 1, H - 1)
    return im


def garage_card():
    im, d = card()
    clouds(d)
    d.rectangle([30, 10, 210, 76], fill=ST_HI)
    for ly in (16, 32, 48):
        d.rectangle([48, ly, 206, ly + 11], fill=NAVY)
        for i, cx in enumerate(range(52, 200, 17)):
            if (i + ly) % 3:
                col = CAR_COLORS[(i * 5 + ly) % len(CAR_COLORS)]
                d.rectangle([cx, ly + 5, cx + 13, ly + 10], fill=col)
                d.rectangle([cx + 3, ly + 2, cx + 10, ly + 5], fill=col)
                d.rectangle([cx + 4, ly + 3, cx + 9, ly + 4], fill=LBLUE)
        d.line([48, ly + 12, 206, ly + 12], fill=ST)
    d.rectangle([30, 4, 48, 76], fill=ST)                                 # glass stair tower
    d.rectangle([33, 8, 45, 76], fill=LBLUE)
    for gy in range(12, 76, 6):
        d.line([33, gy, 45, gy], fill=DBLUE)
    d.rectangle([150, 62, 206, 76], fill=NAVY)                            # car entrance and barrier
    for bx in range(152, 196, 6):
        d.line([bx, 68, bx + 2, 68], fill=YELLOW)
        d.line([bx + 3, 68, bx + 5, 68], fill=WHITE)
    p_sign(d, 170, 50, 11)
    door(d, 90, 62, 14, 14, frame=NAVY, glass=True)
    lawn(d, 77)
    # the Ram Van at its stop out front
    d.rectangle([110, 70, 146, 82], fill=WHITE)
    for wx in range(113, 140, 8):
        d.rectangle([wx, 72, wx + 5, 75], fill=NAVY)
    d.rectangle([110, 77, 146, 78], fill=MAROON)
    for wx in (116, 140):
        d.ellipse([wx - 3, 80, wx + 3, 86], fill=NAVY)
    person(d, 100, 72, MAROON)
    tree(d, 14, 52, 12, ground=77)
    tree(d, 220, 56, 10, ground=77)
    return im


if __name__ == "__main__":
    save_building("parking_lot", parking_lot())
    save_building("regional_parking", garage(), garage_card())
