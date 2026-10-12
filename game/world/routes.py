"""Walking directions in plain words, worked out from the map (decisions/0037).

Used by the accessible Rose Hill Campus Guide (tools/build_guide.py), which
describes how to get between places without the game's picture. Pure
Python: no Pyxel.

A route is found on the same grid the player walks: one step per tile,
blocked cells (walls, fences, signs, people) avoided. Turns cost extra, so
the path follows walkways in long straight runs the way a person would,
and the steps read as "Head north for 12 steps" rather than a zigzag.
"""

import heapq
from dataclasses import dataclass, field

from .mapdata import MapData, MapObject

DIRS = {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}
TURN_COST = 4          # a turn costs as much as this many extra steps
SIDE_RANGE = 2         # how far to the side a place can be and still be "passed"
DIAGONALS = {frozenset(("north", "east")): "north-east", frozenset(("north", "west")): "north-west",
             frozenset(("south", "east")): "south-east", frozenset(("south", "west")): "south-west"}
LEFT_OF = {"north": "west", "south": "east", "east": "north", "west": "south"}


@dataclass
class Leg:
    """One instruction: walk `steps` tiles heading `heading`."""
    heading: str
    steps: int
    cells: list[tuple[int, int]] = field(default_factory=list)
    area: str = ""                      # the named area the leg ends in
    passing: list[tuple[str, str]] = field(default_factory=list)  # (place name, "left"/"right")


@dataclass
class Route:
    start: str
    goal: str
    path: list[tuple[int, int]]
    legs: list[Leg]
    arrive_side: str                    # where the goal is at the end: "ahead", "on your left"...

    @property
    def steps(self) -> int:
        return len(self.path) - 1


def place_targets(m: MapData, location: str) -> list[MapObject]:
    """The objects that stand for a place: its doors, else its signs."""
    doors = [o for o in m.objects if o.location == location and o.type == "door"]
    return doors or [o for o in m.objects if o.location == location and o.type == "sign"]


def _walkable(m: MapData, x: int, y: int) -> bool:
    return not m.is_blocked(x, y)


def find_path(m: MapData, start: tuple[int, int], goals: set[tuple[int, int]]) -> list[tuple[int, int]] | None:
    """Fewest-turns-then-shortest walk from `start` to any cell in `goals`."""
    if start in goals:
        return [start]
    best: dict[tuple, int] = {}
    prev: dict[tuple, tuple] = {}
    heap = [(0, start, "")]
    best[(start, "")] = 0
    while heap:
        cost, cell, heading = heapq.heappop(heap)
        if cell in goals:
            path, state = [cell], (cell, heading)
            while state in prev:
                state = prev[state]
                path.append(state[0])
            return path[::-1]
        if cost > best.get((cell, heading), 1 << 30):
            continue
        for name, (dx, dy) in DIRS.items():
            nxt = (cell[0] + dx, cell[1] + dy)
            if not _walkable(m, *nxt):
                continue
            c = cost + 1 + (TURN_COST if heading and name != heading else 0)
            if c < best.get((nxt, name), 1 << 30):
                best[(nxt, name)] = c
                prev[(nxt, name)] = (cell, heading)
                heapq.heappush(heap, (c, nxt, name))
    return None


def _heading(a: tuple[int, int], b: tuple[int, int]) -> str:
    d = (b[0] - a[0], b[1] - a[1])
    return next(n for n, v in DIRS.items() if v == d)


def legs_of(path: list[tuple[int, int]]) -> list[Leg]:
    """Straight runs, with staircases of short alternating runs (a diagonal
    walkway) merged into one north-east / south-west ... leg."""
    runs: list[Leg] = []
    for a, b in zip(path, path[1:]):
        h = _heading(a, b)
        if runs and runs[-1].heading == h:
            runs[-1].steps += 1
            runs[-1].cells.append(b)
        else:
            runs.append(Leg(h, 1, [b]))
    out: list[Leg] = []
    i = 0
    while i < len(runs):
        j = i
        pair = {runs[i].heading}
        # a staircase: alternating headings, each run short
        while (j + 1 < len(runs) and runs[j].steps <= 2 and runs[j + 1].steps <= 2
               and len(pair | {runs[j + 1].heading}) == 2 and runs[j + 1].heading != runs[j].heading
               and frozenset(pair | {runs[j + 1].heading}) in DIAGONALS):
            pair.add(runs[j + 1].heading)
            j += 1
        if j - i >= 2:                                   # at least three runs: call it a diagonal
            cells = [c for r in runs[i:j + 1] for c in r.cells]
            out.append(Leg(DIAGONALS[frozenset(pair)], len(cells), cells))
            i = j + 1
        else:
            out.append(runs[i])
            i += 1
    return out


def _side(heading: str, dx: int, dy: int) -> str | None:
    """'left' or 'right' of someone walking `heading`, for an offset (dx, dy)."""
    hx, hy = DIRS.get(heading, (0, 0))
    if (hx, hy) == (0, 0):
        return None
    cross = hx * dy - hy * dx          # screen coordinates: y grows downward
    if cross < 0:
        return "left"
    if cross > 0:
        return "right"
    return None


def _main_heading(leg: Leg) -> str:
    return leg.heading if leg.heading in DIRS else leg.heading.split("-")[0]


def describe(m: MapData, path: list[tuple[int, int]], names: dict[str, str],
             goal: MapObject, start_name: str, goal_name: str) -> Route:
    legs = legs_of(path)
    mentioned = {goal.location}
    sx, sy = path[0]
    for o in m.objects:                 # don't point out where you're starting from
        if o.location and abs(o.x - sx) + abs(o.y - sy) <= 3:
            mentioned.add(o.location)
    places = [o for o in m.objects if o.location and o.type in ("door", "sign") and o.location in names]
    for leg in legs:
        area = m.area_at(*leg.cells[-1])
        leg.area = area.name if area else ""
        h = _main_heading(leg)
        for cx, cy in leg.cells:
            for o in places:
                if o.location in mentioned:
                    continue
                dx, dy = o.x - cx, o.y - cy
                along = abs(dx) if h in ("east", "west") else abs(dy)
                side_dist = abs(dy) if h in ("east", "west") else abs(dx)
                if along == 0 and 1 <= side_dist <= SIDE_RANGE:
                    side = _side(h, dx, dy)
                    if side:
                        leg.passing.append((names[o.location], side))
                        mentioned.add(o.location)
    end = path[-1]
    last = _main_heading(legs[-1]) if legs else "north"
    dx, dy = goal.x - end[0], goal.y - end[1]
    if (dx, dy) == DIRS[last]:
        arrive = "straight ahead"
    else:
        side = _side(last, dx, dy)
        arrive = f"on your {side}" if side else "behind you"
    return Route(start_name, goal_name, path, legs, arrive)


def route_to(m: MapData, start: tuple[int, int], location: str, names: dict[str, str],
             start_name: str) -> Route | None:
    """Directions from `start` to the nearest door (or sign) of `location`."""
    targets = place_targets(m, location)
    goals: dict[tuple[int, int], MapObject] = {}
    for o in targets:
        for dx, dy in DIRS.values():
            c = (o.x + dx, o.y + dy)
            if _walkable(m, *c):
                goals.setdefault(c, o)
    if not goals:
        return None
    path = find_path(m, start, set(goals))
    if path is None:
        return None
    return describe(m, path, names, goals[path[-1]], start_name, names.get(location, location))


def sentences(route: Route) -> list[str]:
    """The route as numbered-list sentences."""
    out = []
    area = None
    lead = ""
    for i, leg in enumerate(route.legs):
        if leg.steps == 1 and i + 1 < len(route.legs) and not leg.passing:
            lead = f"Take one step {leg.heading}, then h"     # folded into the next instruction
            continue
        s = f"{lead or 'H'}ead {leg.heading} for {leg.steps} step{'s' if leg.steps != 1 else ''}"
        lead = ""
        if leg.passing:
            bits = [f"{name} on your {side}" for name, side in leg.passing[:2]]
            s += ", passing " + " and ".join(bits)
        if leg.area and leg.area != area and i > 0:
            s += f", into {leg.area}"
        area = leg.area or area
        out.append(s + ".")
    out.append(f"{route.goal} is {route.arrive_side}.")
    return out
