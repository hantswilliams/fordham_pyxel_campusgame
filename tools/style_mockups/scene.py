"""The one scene every style mockup draws: the Cunniffe Fountain plaza, from
the real map (content/maps/rose_hill.txt cols 23-47, rows 33-51), with the
camera exactly where tools/capture.py's 17ce_fountain_plaza shot has it."""

GRID = [
    "RRR.:...:==========:...::",  # 33
    "WwW.:...:==========:.....",  # 34
    "WDW::::::==:RRRRR==:.::::",  # 35
    "====X======XWwWwW==:::..T",  # 36
    "====X======XwWwWw==::.**.",  # 37
    ":==:::::::::WwWwW==::.**.",  # 38
    ":==::......:wWDWw==::....",  # 39
    ":==:::::::,,,,,,,==::T...",  # 40
    ":==::GGGGG,,,,,,,==::....",  # 41
    ":==::GGGGG,b,~~,b==::....",  # 42
    ":==::WwWwW,,,~~,,YY::T...",  # 43
    ":YY::WwDwW,,,,,,,==::....",  # 44
    ":==::,,,,,,*,,,*,==::....",  # 45
    ":==::..:...RRRRRR==::T...",  # 46
    ":==::..:...RRRRRR==::....",  # 47
    ":==::..:...RRRRRR==::....",  # 48
    ":==::..:...WwWWwW==::T...",  # 49
    ":==::..:...WwDDwW==::.**.",  # 50
    ":==::::::::::::::==::.**.",  # 51
]
X0, Y0 = 23, 33            # map cell of GRID[0][0]
CAM = (23.5, 33.5)         # camera, in map cells (half-tile, as in the game)
VIEW_W, VIEW_H = 24, 18    # cells on screen (384 x 288 layout pixels)

GROUND = {".": "grass", ":": "walk", ",": "plaza", "=": "road", "X": "xwalk_v",
          "Y": "xwalk_h", "*": "flowers", "T": "grass", "b": "plaza", "~": "plaza",
          "R": "walk", "W": "walk", "w": "walk", "D": "walk", "G": "walk"}

# Drawn buildings: origin cell, size in cells, rows of roof (the rest is wall).
BUILDINGS = [
    dict(id="collins", name="COLLINS", x=23, y=30, w=3, h=6, roof=4, kind="collins"),
    dict(id="hughes", name="HUGHES HALL", x=35, y=35, w=5, h=5, roof=1, kind="hughes"),
    dict(id="cunniffe", name="CUNNIFFE", x=28, y=41, w=5, h=4, roof=2, kind="cunniffe"),
    dict(id="dealy", name="DEALY HALL", x=34, y=46, w=6, h=5, roof=3, kind="dealy"),
]
FOUNTAIN = (36, 42)        # 2 x 2 basin

TREES = [(x + X0, y + Y0) for y, row in enumerate(GRID) for x, c in enumerate(row) if c == "T"]
BENCHES = [(34, 42), (39, 42)]
SIGNS = [(42, 38), (29, 46), (33, 50), (38, 40)]          # grey info signposts
SHUTTLE_SIGNS = [(42, 49), (33, 35)]                       # maroon Campus Shuttle stops
RAM_STATUE = (35, 40)
STATUES = [(26, 42)]                                       # Archbishop Hughes

# People: (cell x, cell y, facing, look). The player stands by the fountain;
# an Orientation Leader has stopped to talk.
PLAYER = (35, 44, "right", "player")
PEOPLE = [
    (36, 44, "left", "leader"),
    (42, 46, "left", "student_blue"),
    (26, 39, "up", "student_yellow"),
    (44, 41, "down", "staff"),
]

AREA = "Academic Quad"
SPEAKER = "Orientation Leader"
LINE = ("That's the Cunniffe Fountain. Hughes Hall, right behind it, "
        "is the Gabelli School of Business.")


def cell(x, y):
    """Ground letter at map cell (x, y), or '.' off the grid."""
    gx, gy = x - X0, y - Y0
    if 0 <= gy < len(GRID) and 0 <= gx < len(GRID[0]):
        return GRID[gy][gx]
    return "."


def ground(x, y):
    return GROUND.get(cell(x, y), "grass")
