"""Draw what lies outside the campus fence (decisions/0033): one picture the
size of the map, painted only where the map is off-campus ('#' cells), so
the game shows the streets, the Botanical Garden and the neighbourhood
instead of empty navy squares. You can't walk there: the cells stay
'offcampus' (blocked); this is scenery.

Laid out from research/images/google_map_view.png (as a reference only):
- north-west: the Metro-North tracks and Webster Avenue running up
  diagonally, apartment blocks beyond, Fordham Prep and its field between
  Webster Avenue and the campus fence
- north and east: Southern Boulevard hugging the fence, and beyond it the
  New York Botanical Garden: woods, lawns, paths, the Enid A. Haupt
  Conservatory and its reflecting pool
- south: East Fordham Road, four lanes, with shops and apartment houses
  along both sides, and the street from the south-east gate down to it
- west: Webster Avenue down the left edge to the Webster Avenue gate

    python3 assets/surroundings/draw_surroundings.py   # writes rose_hill.png
"""

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "assets" / "buildings" / "_style"))
from kit import (BRICK, BRICK_DK, BROWN, CAR_COLORS, CLEAR, DBLUE, GRAY, GREEN, LBLUE,  # noqa: E402
                 LIME, MAROON, NAVY, ORANGE, PBRICK, PBRICK_SH, PEACH, PINK, RED, ROOF, ROOF_SH,
                 ST, ST_DK, ST_HI, ST_SH, WHITE, YELLOW, CYAN, car, save)

T = 16
GRID = (ROOT / "content" / "maps" / "rose_hill.txt").read_text().splitlines()
H, W = len(GRID), len(GRID[0])
rng = random.Random(33)

im = Image.new("RGBA", (W * T, H * T), CLEAR)
d = ImageDraw.Draw(im)


def px(p):
    return (round(p[0] * T), round(p[1] * T))


def outside(x, y):
    return 0 <= x < W and 0 <= y < H and GRID[y][x] == "#"


# ---------------------------------------------------------------- roads
SOUTHERN_BLVD = [(32.5, -1.5), (56, 9.6), (81.6, 9.6), (84.6, 21.2), (91, 24.6), (101.5, 31.5)]
WEBSTER_AVE = [(-0.3, 77), (-0.3, 33.5), (22, -1.5)]
FORDHAM_RD = [(101.5, 67.6), (10, 77.6)]
TRACKS = [(-1.5, 25.5), (16.6, -1.5)]
GATE_STREET = [(80.0, 60.5), (80.0, 70.5)]       # from the south-east gate down to Fordham Road
MAIN_GATE_LINK = [(81.5, 22.6), (85.0, 22.6)]    # the main gate out to Southern Boulevard


def band(points, width, fill, caps=True):
    """A thick polyline (in tiles), round at the joins (and the ends, if
    `caps`; a street that stops at a gate is left square)."""
    w = round(width * T)
    pts = [px(p) for p in points]
    d.line(pts, fill=fill, width=w, joint="curve")
    for p in (pts if caps else pts[1:-1]):
        d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=fill)


def offset(points, dist):
    """The polyline moved sideways by `dist` tiles (left of travel is +)."""
    out = []
    for i, (x, y) in enumerate(points):
        a = points[max(i - 1, 0)]
        b = points[min(i + 1, len(points) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1
        out.append((x - dy / n * dist, y + dx / n * dist))
    return out


def dashes(points, fill, on=6, off=6, width=1):
    """A dashed line along a polyline, in pixels."""
    for a, b in zip(points, points[1:]):
        (x0, y0), (x1, y1) = px(a), px(b)
        n = math.hypot(x1 - x0, y1 - y0)
        k = 0.0
        while k < n:
            e = min(k + on, n)
            d.line([(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n),
                    (x0 + (x1 - x0) * e / n, y0 + (y1 - y0) * e / n)], fill=fill, width=width)
            k += on + off


def avenue(points, lanes=2, cars=0, seed=0, caps=True):
    """A city street: concrete sidewalks, asphalt, lane markings, traffic."""
    width = lanes * 1.0 + 0.4
    band(points, width + 1.4, ST_HI, caps)               # sidewalks
    band(points, width + 0.3, ST_SH, caps)               # curbs
    band(points, width, ROOF, caps)                      # asphalt
    if lanes >= 4:                                       # double yellow down the middle
        for off in (-0.06, 0.06):
            d.line([px(p) for p in offset(points, off)], fill=YELLOW, width=1)
        for off in (-1.0, 1.0):
            dashes(offset(points, off), WHITE)
    else:
        dashes(points, YELLOW, on=8, off=5)
    r = random.Random(seed)
    for _ in range(cars):                                # traffic, keeping to the right
        i = r.randrange(len(points) - 1)
        t = r.random()
        a, b = points[i], points[i + 1]
        side = r.choice((-1, 1)) * (0.5 if lanes < 4 else r.choice((0.5, 1.5)))
        (cx, cy), = offset([(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), b], side)[:1]
        horiz = abs(b[0] - a[0]) > abs(b[1] - a[1])
        car_at(cx * T, cy * T, r.choice(CAR_COLORS), horiz, side > 0)


def car_at(cx, cy, body, horiz, flip):
    """A car centred at (cx, cy) px, turned to run along the street."""
    c = Image.new("RGBA", (9, 14), CLEAR)
    car(ImageDraw.Draw(c), 0, 0, body, "down" if flip else "up")
    if horiz:
        c = c.transpose(Image.Transpose.ROTATE_90 if flip else Image.Transpose.ROTATE_270)
    im.alpha_composite(c, (round(cx - c.width / 2), round(cy - c.height / 2)))


# ---------------------------------------------------------------- ground
# the Botanical Garden north and east of Southern Boulevard; the city elsewhere
d.rectangle([0, 0, W * T, H * T], fill=ST_HI)
for x in range(0, W * T, 8):                             # the city: concrete paving
    d.line([x, 0, x, H * T], fill=ST)
for y in range(0, H * T, 8):
    d.line([0, y, W * T, y], fill=ST)
nybg = SOUTHERN_BLVD + [(101.5, -1.5)]
d.polygon([px(p) for p in nybg], fill=LIME)
d.polygon([px(p) for p in [(99.2, 31), (101, 31), (101, 61), (99.2, 61)]], fill=LIME)  # Bronx Park, east edge
for _ in range(2600):                                    # mown-grass texture
    x, y = rng.randrange(W * T), rng.randrange(H * T)
    if im.getpixel((x, y))[:3] == LIME:
        d.point([x, y], fill=GREEN)


def block_paving(x0, y0, x1, y1):
    """Concrete with joints, for sidewalks and plazas (tile coords)."""
    d.rectangle([x0 * T, y0 * T, x1 * T - 1, y1 * T - 1], fill=ST_HI)
    for x in range(int(x0 * T), int(x1 * T), 8):
        d.line([x, y0 * T, x, y1 * T - 1], fill=ST)
    for y in range(int(y0 * T), int(y1 * T), 8):
        d.line([x0 * T, y, x1 * T - 1, y], fill=ST)


# ---------------------------------------------------------------- city buildings
def apartment(x0, y0, x1, y1, wall=BRICK, roof=ROOF_SH, tower=None, awnings=None):
    """A city building in the house 3/4 view (tile coords, may be fractional):
    a flat roof with a parapet, then the front wall with windows. NYC
    touches: a wooden water tower, and shop awnings on the ground floor."""
    X0, Y0, X1, Y1 = round(x0 * T), round(y0 * T), round(x1 * T) - 1, round(y1 * T) - 1
    wall_h = min(18, max(10, (Y1 - Y0) // 3))
    roof_y1 = Y1 - wall_h
    d.rectangle([X0, Y0, X1, roof_y1], fill=roof)
    d.rectangle([X0 + 2, Y0 + 2, X1 - 2, roof_y1 - 1], fill=ROOF if roof != ROOF else ROOF_SH)
    for yy in range(Y0 + 7, roof_y1 - 2, 7):
        d.line([X0 + 3, yy, X1 - 3, yy], fill=roof)
    d.rectangle([X0, roof_y1 + 1, X1, Y1], fill=wall)
    d.line([X0, roof_y1 + 1, X1, roof_y1 + 1], fill=NAVY)
    for wy in range(roof_y1 + 3, Y1 - 4, 6):            # windows
        for wx in range(X0 + 3, X1 - 3, 6):
            d.rectangle([wx, wy, wx + 2, wy + 3], fill=LBLUE)
            d.point([wx, wy], fill=WHITE)
    if awnings:                                          # shopfronts along the street
        for i, ax in enumerate(range(X0 + 2, X1 - 8, 12)):
            col = awnings[i % len(awnings)]
            d.rectangle([ax, Y1 - 5, ax + 9, Y1 - 3], fill=col)
            d.line([ax, Y1 - 3, ax + 9, Y1 - 3], fill=NAVY)
            d.rectangle([ax + 1, Y1 - 2, ax + 8, Y1], fill=LBLUE)
    if tower:                                            # a water tower on the roof
        tx, ty = round(tower[0] * T), round(tower[1] * T)
        d.rectangle([tx - 1, ty + 7, tx + 8, ty + 9], fill=NAVY)
        d.rectangle([tx, ty, tx + 7, ty + 7], fill=BROWN)
        d.line([tx + 2, ty + 1, tx + 2, ty + 6], fill=ORANGE)
        d.line([tx + 5, ty + 1, tx + 5, ty + 6], fill=ORANGE)
        d.polygon([(tx - 1, ty), (tx + 8, ty), (tx + 3, ty - 4)], fill=ST_DK)
    d.rectangle([X0, Y0, X1, Y1], outline=NAVY)


def street_tree(x, y, r=6):
    cx, cy = round(x * T), round(y * T)
    d.ellipse([cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1], fill=NAVY)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN)
    d.ellipse([cx - r + 2, cy - r + 1, cx + r // 3, cy - 1], fill=LIME)


def woods(poly, count, rmin=6, rmax=11, seed=1):
    """Dense tree canopy inside a polygon (tile coords)."""
    r_ = random.Random(seed)
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    mask = Image.new("1", (W * T, H * T), 0)
    ImageDraw.Draw(mask).polygon([px(p) for p in poly], fill=1)
    placed = 0
    tries = 0
    while placed < count and tries < count * 20:
        tries += 1
        x = r_.uniform(min(xs), max(xs)) * T
        y = r_.uniform(min(ys), max(ys)) * T
        if not (0 <= x < W * T and 0 <= y < H * T) or not mask.getpixel((int(x), int(y))):
            continue
        r = r_.randint(rmin, rmax)
        leaf = r_.choice((GREEN, GREEN, GREEN, LIME if r_.random() < 0.15 else GREEN))
        d.ellipse([x - r - 1, y - r - 1, x + r + 1, y + r + 1], fill=NAVY)
        d.ellipse([x - r, y - r, x + r, y + r], fill=leaf)
        d.ellipse([x - r + 2, y - r + 2, x + r // 3, y - r // 3], fill=LIME)
        if r_.random() < 0.08:                             # an autumn tree here and there
            d.ellipse([x - r + 1, y - r + 1, x + r - 1, y + r - 1], fill=ORANGE)
            d.ellipse([x - r + 3, y - r + 2, x, y - 2], fill=YELLOW)
        placed += 1


def garden_path(points, width=0.7):
    band(points, width + 0.15, ST_SH)
    band(points, width, PEACH)


# ---------------------------------------------------------------- north-west: tracks, Webster Avenue, Fordham Prep
# apartment blocks west of the tracks
for (x0, y0, x1, y1, tw) in ((0, 0, 5.5, 4.2, (2, 0.6)), (6.5, 0, 11.6, 3.2, None),
                             (0, 5.2, 3.4, 10.0, (1, 5.8)), (0, 11, 2.2, 15.5, None),
                             (12.8, -0.5, 15.6, 1.8, None)):
    apartment(x0, y0, x1, y1, wall=rng.choice((BRICK, PBRICK, BRICK_DK)), tower=tw)
# Metro-North's Harlem Line: a gravel cutting with two tracks, and a train
band(TRACKS, 2.6, ST_SH)
band(TRACKS, 2.2, ST_DK)
for off in (-0.5, 0.5):
    rails = offset(TRACKS, off)
    for k in range(0, 60):                               # sleepers
        t = k / 60
        (x0, y0), (x1, y1) = rails[0], rails[1]
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        nx, ny = 0.818 * 0.32, 0.575 * 0.32
        d.line([px((cx - nx, cy - ny)), px((cx + nx, cy + ny))], fill=BROWN, width=2)
    for r_off in (-0.18, 0.18):
        d.line([px(p) for p in offset(rails, r_off)], fill=GRAY, width=1)
# a Metro-North train (silver, with the blue and red stripe) on the near track
train = offset(TRACKS, 0.5)
(tx0, ty0), (tx1, ty1) = train
for car_i in range(3):
    t0, t1 = 0.30 + car_i * 0.105, 0.30 + car_i * 0.105 + 0.095
    a = (tx0 + (tx1 - tx0) * t0, ty0 + (ty1 - ty0) * t0)
    b = (tx0 + (tx1 - tx0) * t1, ty0 + (ty1 - ty0) * t1)
    d.line([px(a), px(b)], fill=NAVY, width=13)
    d.line([px(a), px(b)], fill=ST_HI, width=11)
    d.line([px(a), px(b)], fill=WHITE, width=5)
    d.line([px(offset([a, b], 0.22)[0]), px(offset([a, b], 0.22)[1])], fill=DBLUE, width=1)
    d.line([px(offset([a, b], -0.22)[0]), px(offset([a, b], -0.22)[1])], fill=RED, width=1)
avenue(WEBSTER_AVE, lanes=4, cars=9, seed=4)
# Fordham Prep, between Webster Avenue and the campus fence, with Prep Field
d.polygon([px(p) for p in [(14.2, 2.6), (23.9, 2.6), (23.9, 18.9), (9.0, 18.9)]], fill=LIME)
apartment(15.2, 3.4, 23.6, 8.6, wall=PBRICK, roof=ROOF_SH)
for wx in range(int(16.0 * T), int(23.0 * T), 20):      # Prep's stone trim
    d.line([wx, int(7.6 * T), wx, int(8.5 * T)], fill=ST_HI)
x0, y0, x1, y1 = (round(v * T) for v in (13.4, 10.0, 23.6, 18.4))
d.rectangle([x0, y0, x1, y1], fill=GREEN)
for i, sx in enumerate(range(x0, x1, 12)):
    if i % 2:
        d.rectangle([sx, y0, min(sx + 11, x1), y1], fill=LIME)
d.rectangle([x0 + 4, y0 + 4, x1 - 4, y1 - 4], outline=WHITE)
d.line([(x0 + x1) // 2, y0 + 4, (x0 + x1) // 2, y1 - 4], fill=WHITE)
d.ellipse([(x0 + x1) // 2 - 10, (y0 + y1) // 2 - 10, (x0 + x1) // 2 + 10, (y0 + y1) // 2 + 10], outline=WHITE)
d.rectangle([x0, y0, x1, y1], outline=NAVY)
for k in range(6):
    street_tree(13.0 + k * 1.9, 9.3, 5)
woods([(24, -1), (33, -1), (34.5, 0.6), (24, 2.2)], 18, 5, 8, seed=9)   # trees north of the Murphy road
# the west edge: Webster Avenue down to the gate; trees along the sidewalk
for y in range(36, 73, 4):
    street_tree(1.35, y + 0.5, 5)

# ---------------------------------------------------------------- north and east: Southern Boulevard and the Botanical Garden
woods([(33, -1.5), (101.5, -1.5), (101.5, 31.5), (91, 24.6), (84.6, 21.2), (81.6, 9.6), (56, 9.6)],
      520, 6, 12, seed=2)
# the Enid A. Haupt Conservatory: a glass palace with a central dome, two wings
# reaching south round the reflecting pool, on an open lawn
d.polygon([px(p) for p in [(55.5, -1.5), (80.5, -1.5), (80.5, 8.2), (55.5, 8.2)]], fill=LIME)
for _ in range(220):
    x, y = rng.uniform(55.5, 80.5) * T, rng.uniform(-1, 8) * T
    if 0 <= y:
        d.point([x, y], fill=GREEN)
garden_path([(57.5, 7.6), (78.5, 7.6)], 0.8)
garden_path([(68.0, 7.6), (68.0, 4.6)], 1.2)
pool = [round(v * T) for v in (63.6, 3.6, 72.4, 6.3)]
d.rectangle([pool[0] - 2, pool[1] - 2, pool[2] + 2, pool[3] + 2], fill=ST_HI)
d.rectangle(pool, fill=DBLUE)
d.rectangle([pool[0] + 2, pool[1] + 2, pool[2] - 2, pool[3] - 2], fill=CYAN)
for k in range(5):
    d.line([pool[0] + 6 + k * 26, pool[1] + 8, pool[0] + 14 + k * 26, pool[1] + 8], fill=LBLUE)


def glasshouse(x0, y0, x1, y1):
    X0, Y0, X1, Y1 = (round(v * T) for v in (x0, y0, x1, y1))
    d.rectangle([X0, Y0, X1, Y1], fill=WHITE)
    d.rectangle([X0 + 2, Y0 + 2, X1 - 2, Y1 - 2], fill=LBLUE)
    for x in range(X0 + 4, X1 - 2, 4):
        d.line([x, Y0 + 2, x, Y1 - 2], fill=WHITE)
    d.line([X0 + 2, (Y0 + Y1) // 2, X1 - 2, (Y0 + Y1) // 2], fill=WHITE)
    d.rectangle([X0, Y0, X1, Y1], outline=NAVY)


glasshouse(58.0, 0.4, 78.0, 2.6)          # the long back range
glasshouse(58.0, 2.4, 61.4, 6.8)          # west wing
glasshouse(74.6, 2.4, 78.0, 6.8)          # east wing
cx, cy, r = round(68.0 * T), round(1.6 * T), 30   # the Palm Dome
d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], fill=NAVY)
d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE)
d.ellipse([cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3], fill=LBLUE)
for k in range(0, 360, 30):
    a = math.radians(k)
    d.line([cx, cy, cx + (r - 3) * math.cos(a), cy + (r - 3) * math.sin(a)], fill=WHITE)
for rr in (10, 20):
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=WHITE)
d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=WHITE)
d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=CYAN)
# winding garden paths through the woods
garden_path([(84, 0), (88, 6), (86.5, 12), (90, 18), (97, 22), (101, 25)])
garden_path([(42, -1), (46, 2.2), (52, 3.5), (55.5, 5)])
garden_path([(88, 6), (95, 8), (101, 7)])
# a pond in the woods
d.ellipse([round(92 * T), round(11.5 * T), round(97.5 * T), round(15 * T)], fill=DBLUE)
d.ellipse([round(92.3 * T), round(11.8 * T), round(97.2 * T), round(14.7 * T)], fill=CYAN)
woods([(99.2, 31), (101, 31), (101, 61), (99.2, 61)], 26, 5, 8, seed=7)  # Bronx Park, east edge
avenue(SOUTHERN_BLVD, lanes=4, cars=12, seed=2)
avenue(MAIN_GATE_LINK, lanes=2, caps=False)

# ---------------------------------------------------------------- south: East Fordham Road
# buildings on the campus side, between the fence and the road
for (x0, y0, x1, y1, tw, aw) in (
        (63.4, 61.2, 70.6, 66.0, (64.5, 61.8), (RED, YELLOW, DBLUE)),
        (71.0, 61.2, 78.4, 65.6, None, (MAROON, ORANGE, LIME)),
        (94.4, 61.2, 100.5, 65.8, (98.2, 61.7), (RED, DBLUE))):
    block_paving(x0 - 0.3, y0 - 0.3, x1 + 0.3, y1 + 1.8)
    apartment(x0, y0, x1, y1, wall=rng.choice((BRICK, PBRICK, PBRICK_SH)), tower=tw, awnings=aw)
block_paving(81.6, 61, 84, 68.5)
for y in (62.2, 64.6, 67.0):
    street_tree(82.8, y, 5)
block_paving(28, 66.8, 64, 70)                         # the north sidewalk of Fordham Road
block_paving(84, 66.8, 94.4, 70)
for x in range(30, 63, 3):
    street_tree(x + 0.5, 67.7, 5)
for x in range(85, 94, 3):
    street_tree(x + 0.5, 67.7, 5)
avenue(GATE_STREET, lanes=2, cars=1, seed=6, caps=False)
avenue(FORDHAM_RD, lanes=4, cars=16, seed=3)
# a Select Bus Service bus on each big road, and people out walking
def bus(cx, cy, angle_deg, stripe=RED):
    b = Image.new("RGBA", (34, 12), CLEAR)
    bd = ImageDraw.Draw(b)
    bd.rectangle([0, 0, 33, 11], fill=NAVY)
    bd.rectangle([1, 1, 32, 10], fill=WHITE)
    bd.rectangle([1, 4, 32, 7], fill=DBLUE)
    bd.line([1, 8, 32, 8], fill=stripe)
    bd.rectangle([29, 2, 32, 9], fill=LBLUE)                 # windscreen
    for x in (8, 18):                                        # roof vents
        bd.rectangle([x, 2, x + 3, 3], fill=ST)
    b = b.rotate(angle_deg, resample=Image.Resampling.NEAREST, expand=True)
    im.alpha_composite(b, (round(cx * T - b.width / 2), round(cy * T - b.height / 2)))


def walker(x, y, shirt):
    X, Y = round(x * T), round(y * T)
    d.rectangle([X, Y, X + 1, Y + 1], fill=PEACH)
    d.rectangle([X - 1, Y + 2, X + 2, Y + 5], fill=shirt)
    d.point([X, Y + 6], fill=NAVY)
    d.point([X + 1, Y + 6], fill=NAVY)


fr_angle = math.degrees(math.atan2(10, 91.5))                  # Fordham Road climbs to the east
bus(55.0, 67.6 + (101.5 - 55.0) * 10 / 91.5 + 0.55, -fr_angle + 180)
bus(70.0, 10.15, 0, stripe=MAROON)
for _ in range(26):
    x = rng.uniform(29, 63)
    walker(x, rng.uniform(67.3, 69.6), rng.choice((RED, DBLUE, MAROON, YELLOW, LIME, WHITE, ORANGE)))
for x, y in ((58.6, 7.9), (64.0, 7.4), (73.5, 7.8), (68.3, 5.4), (86.5, 9.0), (89.2, 16.5)):
    walker(x, y, rng.choice((RED, DBLUE, YELLOW, WHITE)))

# shops and apartment houses on the far side of Fordham Road
fx = 12.0
while fx < 100:
    w = rng.uniform(3.2, 6.0)
    y_road = 67.6 + (101.5 - (fx + w / 2)) * 10 / 91.5   # the road's centre here
    top = y_road + 3.1
    if top < H:
        apartment(fx, top, fx + w - 0.3, top + 4.5, wall=rng.choice((BRICK, PBRICK, BRICK_DK, PBRICK_SH)),
                  roof=rng.choice((ROOF_SH, ROOF_SH, ST_DK)), tower=(fx + 1.0, top + 1.0) if rng.random() < 0.3 else None)
        # their shopfronts face the road: awnings along the near edge
        X0, X1, Y = round(fx * T) + 2, round((fx + w - 0.3) * T) - 3, round(top * T)
        for i, ax in enumerate(range(X0, X1 - 9, 12)):
            d.rectangle([ax, Y - 3, ax + 9, Y], fill=(RED, YELLOW, DBLUE, MAROON, ORANGE, LIME)[(i + int(fx)) % 6])
            d.line([ax, Y - 3, ax + 9, Y - 3], fill=NAVY)
    fx += w

# ---------------------------------------------------------------- keep it off the campus
px_ = im.load()
for y in range(H):
    for x in range(W):
        if not outside(x, y):
            for yy in range(y * T, y * T + T):
                for xx in range(x * T, x * T + T):
                    px_[xx, yy] = CLEAR
save(im, HERE / "rose_hill.png")
print("wrote", HERE / "rose_hill.png")
