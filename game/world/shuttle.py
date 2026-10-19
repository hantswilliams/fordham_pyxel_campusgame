"""The Campus Shuttle (decisions/0044): a white minivan that drives one loop
of the campus roads, stopping at the six maroon shuttle-stop signs. You can
ride it from stop to stop. A maroon Ram Van, the service to Lincoln Center,
stays parked at the garage. Pure logic, no Pyxel.

The route is a list of road cells in the map's JSON ("shuttle"). Between
them the van takes the shortest way along the road, and staircase-shaped
roads are straightened into diagonals so it glides along them rather than
zig-zagging. It drives like a careful campus driver:

- it stops at each stop for a few seconds, and waits there a little longer
  while you're standing beside it
- it stops for you (or anyone) on the road just ahead, and says "BEEP"
- it slows down over crosswalks
- the road cells under it are taken, so you can't walk through it
- it stands still while a text box or menu is open (only the overworld
  moves it), and in screenshot runs (ENABLED = False) there is no shuttle
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass

from game.systems import controls

from .directions import Direction
from .mapdata import MapData

SPEED = 2                  # pixels a frame: walking pace (the bike is twice as fast)
CROSSWALK_SPEED = 1        # over the stripes
STOP_FRAMES = 150          # 5 seconds at each stop
HOLD_FRAMES = 450          # waits up to 15 seconds more while you're beside it at a stop
FAST = 8                   # how much faster a ride goes when you skip ahead
LENGTH = 24                # the stretch of road the van takes up, in pixels
LOOK = 32                  # how far ahead it checks for people
ROAD = {"road", "crosswalk_h", "crosswalk_v", "item_card_road"}
CROSSWALK = {"crosswalk_h", "crosswalk_v"}
ENABLED = True             # tools/capture.py turns this off


@dataclass
class Stop:
    name: str
    where: str                 # the road it's on, for the stop's card and the Guide
    sign: tuple[int, int]      # the maroon sign
    at: tuple[int, int]        # the road cell the van stops on
    dist: float = 0.0          # how far round the loop that is, in pixels
    alight: tuple[int, int] = (0, 0)   # where you step off


class Route:
    """The loop as a polyline in map pixels (cell centres), with the stops on it."""

    def __init__(self, m: MapData, data: dict, tile: int):
        self.map, self.tile = m, tile
        self.stops = [Stop(s["name"], s.get("where", ""), tuple(s["sign"]), tuple(s["at"]))
                      for s in data["stops"]]
        cells = route_cells(m, [tuple(c) for c in data["route"]])
        keep = {s.at for s in self.stops} | {tuple(c) for c in data["route"]}
        self.cells = cells
        self.points = self._straighten(cells, keep)
        self.cum = [0.0]
        for (x0, y0), (x1, y1) in zip(self.points, self.points[1:]):
            self.cum.append(self.cum[-1] + math.hypot(x1 - x0, y1 - y0))
        self.length = self.cum[-1]
        for s in self.stops:
            i = self.points.index(self._centre(s.at)) if self._centre(s.at) in self.points else None
            if i is None:
                raise ValueError(f"shuttle stop {s.name!r} at {s.at} isn't on the route")
            s.dist = self.cum[i]
            s.alight = self._alight(s)
        self.stops.sort(key=lambda s: s.dist)

    # --- building ----------------------------------------------------------------------
    def _centre(self, c: tuple[int, int]) -> tuple[float, float]:
        return c[0] * self.tile + self.tile / 2, c[1] * self.tile + self.tile / 2

    def _on_road(self, x: float, y: float) -> bool:
        cx, cy = int(x // self.tile), int(y // self.tile)
        return self.map.in_bounds(cx, cy) and self.map.tiles[cy][cx] in ROAD

    def _straight(self, a, b) -> bool:
        """Can the van drive straight from a to b without leaving the road?"""
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) // 2))
        return all(self._on_road(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
                   for k in range(n + 1))

    def _straighten(self, cells, keep) -> list[tuple[float, float]]:
        """Pull the cell path tight: from each corner, drive straight to the
        furthest cell still reachable on road. Stops and route points stay."""
        pts = [self._centre(c) for c in cells]
        out = [pts[0]]
        i = 0
        while i < len(pts) - 1:
            j = i + 1
            while j + 1 < len(pts) and cells[j] not in keep and self._straight(pts[i], pts[j + 1]):
                j += 1
            out.append(pts[j])
            i = j
        return out

    def _alight(self, s: Stop) -> tuple[int, int]:
        """Where you step off: the open sidewalk cell nearest the van's door,
        towards the stop's sign."""
        m = self.map
        ax, ay = s.at
        best = None
        for y in range(ay - 3, ay + 4):
            for x in range(ax - 3, ax + 4):
                if not m.in_bounds(x, y) or m.is_blocked(x, y) or m.tiles[y][x] in ROAD:
                    continue
                key = (abs(x - ax) + abs(y - ay), abs(x - s.sign[0]) + abs(y - s.sign[1]))
                if best is None or key < best[0]:
                    best = (key, (x, y))
        if best is None:
            raise ValueError(f"shuttle stop {s.name!r}: no free sidewalk beside it")
        return best[1]

    # --- reading -----------------------------------------------------------------------
    def at(self, d: float) -> tuple[float, float, float, float]:
        """Where the van's centre is d pixels round the loop, and its heading."""
        d %= self.length
        lo, hi = 0, len(self.cum) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.cum[mid] <= d:
                lo = mid
            else:
                hi = mid
        (x0, y0), (x1, y1) = self.points[lo], self.points[hi]
        seg = self.cum[hi] - self.cum[lo] or 1
        t = (d - self.cum[lo]) / seg
        return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, (x1 - x0) / seg, (y1 - y0) / seg

    def cell_at(self, d: float) -> tuple[int, int]:
        x, y, _, _ = self.at(d)
        return int(x // self.tile), int(y // self.tile)

    def speed_at(self, d: float) -> int:
        x, y = self.cell_at(d)
        return CROSSWALK_SPEED if self.map.tiles[y][x] in CROSSWALK else SPEED

    def frames_between(self, d0: float, d1: float) -> int:
        """Driving time from d0 to d1 (going forward round the loop), not counting stops."""
        gap = (d1 - d0) % self.length
        frames, done = 0, 0.0
        while done < gap:
            done += self.speed_at(d0 + done)
            frames += 1
        return frames


class Shuttle:
    """The van on its route. `update(blockers, near)` each overworld frame:
    `blockers` are the cells of people it mustn't drive into (you, and anyone
    on the road), `near` whether you're standing beside it."""

    def __init__(self, route: Route, start_stop: int = 0):
        self.route = route
        self.d = route.stops[start_stop % len(route.stops)].dist
        self.dwell = STOP_FRAMES
        self.hold = HOLD_FRAMES
        self.at_stop: int | None = start_stop % len(route.stops)
        self.waiting = False           # stopped for someone in the road
        self.beep = 0                  # frames left to show "BEEP"

    # where it is
    @property
    def pos(self) -> tuple[float, float, float, float]:
        return self.route.at(self.d)

    def cells(self) -> set[tuple[int, int]]:
        """The road cells it takes up."""
        r = self.route
        return {r.cell_at(self.d + s) for s in range(-LENGTH // 2, LENGTH // 2 + 1, 4)}

    def ahead(self) -> set[tuple[int, int]]:
        r = self.route
        return {r.cell_at(self.d + s) for s in range(LENGTH // 2 + 4, LENGTH // 2 + LOOK + 1, 4)} - self.cells()

    @property
    def stopped_at(self) -> Stop | None:
        """The stop it's standing at, doors open, or None while it drives."""
        return self.route.stops[self.at_stop] if self.at_stop is not None and self.dwell > 0 else None

    # driving
    def update(self, blockers: set, near: bool = False) -> int | None:
        """One frame. Returns the index of a stop it has just pulled in to."""
        if self.beep:
            self.beep -= 1
        if self.dwell > 0:
            if near and self.hold > 0:          # you're right by the door: the driver waits
                self.hold -= 1
            else:
                self.dwell -= 1
            if self.dwell > 0:
                return None
            self.at_stop = None
        if self.ahead() & blockers:
            if not self.waiting:
                self.beep = 45
            self.waiting = True
            return None
        self.waiting = False
        r = self.route
        nxt = self.next_stop()
        step = r.speed_at(self.d)
        to_stop = (r.stops[nxt].dist - self.d) % r.length
        if 0 < to_stop <= step:
            self.d = r.stops[nxt].dist
            self.at_stop, self.dwell, self.hold = nxt, STOP_FRAMES, HOLD_FRAMES
            return nxt
        self.d = (self.d + step) % r.length
        return None

    def next_stop(self) -> int:
        """The next stop it'll pull in to (not the one it's standing at)."""
        r = self.route
        best, gap = 0, None
        for i, s in enumerate(r.stops):
            g = (s.dist - self.d) % r.length
            if g == 0:
                continue
            if gap is None or g < gap:
                best, gap = i, g
        return best

    def eta(self, stop: int) -> int:
        """Frames until it reaches `stop`, with the usual waits at the stops before it."""
        if self.at_stop == stop and self.dwell > 0:
            return 0
        r = self.route
        frames = self.dwell if self.dwell > 0 else 0
        i = self.next_stop()
        d = self.d
        while True:
            frames += r.frames_between(d, r.stops[i].dist)
            if i == stop:
                return frames
            frames += STOP_FRAMES
            d = r.stops[i].dist
            i = (i + 1) % len(r.stops)


def timetable(route: Route) -> tuple[list[tuple[Stop, int]], int]:
    """Each stop with the frames it takes to get there from the first stop
    (stopping at the ones between), and the time for the whole loop."""
    out, frames = [], 0
    stops = route.stops
    for i, s in enumerate(stops):
        if i:
            frames += STOP_FRAMES + route.frames_between(stops[i - 1].dist, s.dist)
        out.append((s, frames))
    loop = frames + STOP_FRAMES + route.frames_between(stops[-1].dist, stops[0].dist + route.length)
    return out, loop


def eta_text(frames: int, fps: int = 30) -> str:
    """'about 40 seconds', 'about 2 minutes'."""
    if frames <= 0:
        return "It's here now!"
    s = frames / fps
    if s < 50:
        return f"Next shuttle: about {max(5, round(s / 5) * 5)} seconds."
    mins = max(1, round(s / 60))
    return f"Next shuttle: about {mins} minute{'s' if mins > 1 else ''}."


def route_cells(m: MapData, waypoints: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """The loop as road cells: the shortest way along the road between each
    pair of waypoints, back round to the first. Cells with people or signs
    on them are avoided (mission items on the road are fine)."""
    def free(c):
        x, y = c
        if not m.in_bounds(x, y) or m.tiles[y][x] not in ROAD:
            return False
        o = m.object_at(x, y)
        return o is None or o.type == "item"

    for w in waypoints:
        if not free(w):
            raise ValueError(f"shuttle route point {w} isn't open road")
    loop = list(waypoints) + [waypoints[0]]
    out = [loop[0]]
    for a, b in zip(loop, loop[1:]):
        prev = {a: None}
        q = deque([a])
        while q:
            u = q.popleft()
            if u == b:
                break
            for d in Direction:
                v = (u[0] + d.dx, u[1] + d.dy)
                if v not in prev and free(v):
                    prev[v] = u
                    q.append(v)
        if b not in prev:
            raise ValueError(f"shuttle route: no road from {a} to {b}")
        leg = [b]
        while leg[-1] != a:
            leg.append(prev[leg[-1]])
        out += leg[::-1][1:]
    return out


def load_data(maps_dir, map_id: str) -> dict | None:
    """The "shuttle" part of a map's JSON, or None if the map has no shuttle."""
    import json
    path = maps_dir / f"{map_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8")).get("shuttle")


def lines(data: dict, key: str) -> list[str]:
    """Some of the shuttle's lines from the map's JSON, with button names filled in."""
    return [controls.fmt(s) for s in data.get(key, [])]
