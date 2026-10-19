"""The walkable campus map: tiles, player, NPCs, signs, doors, area banners."""

import time

import pyxel

from game.gfx import display

from game import config
from game.config import ART_SCALE, SCREEN_H, SCREEN_W, TILE, Col
from game.gfx.building_art import draw_on_map
from game.gfx.building_overlay import draw_overlay
from game.gfx.placeholder_art import (BIKE_SPRITE, CHAR_IMAGE_BANK, MAROON_BIKE_SPRITE, RAM_VAN, SHUTTLE_VAN,
                                      TILE_IMAGE_BANK, character_uv, van_uv)
from game.gfx.world_art import PERSON_SHADOW, VAN_END_SHADOW, VAN_SIDE_SHADOW, blt_up, world_for
from game.systems import controls
from game.systems.bike import Bike
from game.systems.missions import Reaction
from game.systems.input import Action
from game.ui import font
from game.ui.text import BIG_CHAR_W, GROW
from game.world.camera import follow
from game.world.directions import Direction
from game.world.mapdata import MapData, MapObject, load_map
from game.world.movement import GridMover
from game.world.tiles import TILES, slot_to_pixel
from game.world import shuttle as shuttle_mod
from game.world.shuttle import ROAD, Route, Shuttle, eta_text
from game.world.wander import Wanderers

from .campus_map import CampusMapScene
from .card import BuildingCardScene
from .choice import ChoiceScene
from .dialogue import DialogueScene
from .id_check import IdCheckScene
from .menu import MenuScene
from .base import Scene

TILEMAP_INDEX = 0
PLAYER_SPRITE = 0
BANNER_FRAMES = 75  # how long the area-name banner shows on entry
TOAST_FRAMES = 45   # how long 'ON THE BIKE' / 'WALKING' shows
COMPLETE_FRAMES = 90  # the MISSION COMPLETE banner
TRACKER_FRAMES = 120  # the mission bar pops up this long when your next step changes
AUTOSAVE_FRAMES = 150  # save your position every 5 seconds while you move

# Held directions, checked in this order.
DIRECTION_ACTIONS = [
    (Action.UP, Direction.UP),
    (Action.DOWN, Direction.DOWN),
    (Action.LEFT, Direction.LEFT),
    (Action.RIGHT, Direction.RIGHT),
]


def bake_cell(game_map: MapData, index: int, x: int, y: int) -> None:
    """Re-draw one map cell into the Pyxel tilemap (e.g. a gate that opened)."""
    tm = pyxel.tilemaps[index]
    u, v = slot_to_pixel(TILES[game_map.tiles[y][x]].slot)
    for j in range(2):
        for i in range(2):
            tm.pset(x * 2 + i, y * 2 + j, (u // 8 + i, v // 8 + j))


def bake_tilemap(game_map: MapData, index: int) -> None:
    """Copy a map into a Pyxel tilemap so it draws in one bltm call.
    Each 16px game tile = 2x2 Pyxel 8px tiles."""
    tm = pyxel.tilemaps[index]
    tm.imgsrc = TILE_IMAGE_BANK
    for y, row in enumerate(game_map.tiles):
        for x, name in enumerate(row):
            u, v = slot_to_pixel(TILES[name].slot)
            for j in range(2):
                for i in range(2):
                    tm.pset(x * 2 + i, y * 2 + j, (u // 8 + i, v // 8 + j))


def add_mission_people(game_map: MapData, book) -> None:
    """Put each mission's giver on the map (decisions/0031): a mission file
    says who offers it and where they stand."""
    for g in book.givers():
        x, y = g["at"]
        game_map.add_object(MapObject(
            type="npc", x=x, y=y, name=g["npc"], lines=list(g.get("offer", [])),
            sprite=g.get("sprite", 2), facing=Direction.from_name(g.get("facing", "down"))))


class OverworldScene(Scene):
    def __init__(self, app, map_id: str = config.START_MAP):
        super().__init__(app)
        self.map: MapData = load_map(map_id, config.MAPS_DIR)
        self.progress = app.progress
        self.book = app.missions
        add_mission_people(self.map, self.book)
        sx, sy = self.map.spawn
        facing = self.map.spawn_facing
        if self.progress.gate_open:                 # carrying on from a save
            for gate in self.map.checkpoints():
                self.map.open_checkpoint(gate.x, gate.y)
            if self.progress.position and not self.map.is_blocked(*self.progress.position):
                sx, sy = self.progress.position
                facing = Direction.from_name(self.progress.facing)
        self.player = GridMover(sx, sy, TILE, config.WALK_SPEED, facing)
        area = self.map.area_at(sx, sy)
        self.area_name = area.name if area else self.map.display_name
        self.banner_timer = BANNER_FRAMES
        self.greeted: set[tuple[int, int]] = set()
        if self.progress.gate_open:
            self.greeted = {(o.x, o.y) for o in self.map.objects if o.type == "npc" and o.auto}
        self.bike: Bike = app.bike
        self.player.speed = self.bike.speed
        self.toast = ""
        self.toast_timer = 0
        self.complete_title = ""
        self.complete_timer = 0
        self.tracker_timer = 0
        self._tracker_last = ...  # not looked yet: no pop-up when the scene opens
        self.queue: list[Reaction] = []             # mission messages waiting to be shown
        self.autosave_timer = AUTOSAVE_FRAMES
        self.cam = (0, 0)
        self.queue += self.book.auto_start()        # the First Week Checklist
        self._sync_items(bake=False)
        bake_tilemap(self.map, TILEMAP_INDEX)
        # On the full-size screen the world is drawn at twice the detail
        # (decisions/0045): the whole map once, into one picture.
        started = time.perf_counter()
        self.world = world_for(self.map, app.locations) if display.active else None
        if getattr(app, "perf", False):
            print(f"map picture: {(time.perf_counter() - started) * 1000:.0f} ms")
        # Otherwise the tiles are drawn as they are, with the outlines, eaves,
        # door mats and name plaques (decisions/0021) drawn once into a
        # map-sized image and copied each frame
        self.overlay: pyxel.Image | None = None
        if self.world is None:
            self.overlay = pyxel.Image(self.map.width * TILE, self.map.height * TILE)
            draw_overlay(self.overlay, self.map, app.locations)
        # people who stroll about (decisions/0040)
        self.wanderers = Wanderers(self.map, TILE)
        # the Campus Shuttle, and the Ram Van parked at the garage (decisions/0044)
        self.shuttle: Shuttle | None = None
        self.shuttle_data = shuttle_mod.load_data(config.MAPS_DIR, map_id)
        self.ram_van: tuple[int, int, Direction] | None = None
        if self.shuttle_data and shuttle_mod.ENABLED:
            route = Route(self.map, self.shuttle_data, TILE)
            self.shuttle = Shuttle(route, self.shuttle_data.get("start_stop", 0))
            rv = self.shuttle_data.get("ram_van")
            if rv:
                x, y = rv["at"]
                facing = Direction.from_name(rv.get("facing", "left"))
                self.ram_van = (x, y, facing)
                for cx in (x, x + 1):           # it takes up two cells, side on
                    self.map.add_object(MapObject(type="vehicle", x=cx, y=y, name="Ram Van",
                                                  location=rv.get("location", "ram_van")))
        self.riding_to: int | None = None       # the stop you're riding to
        self.skipping = False
        self.met_driver = False
        self._update_camera()

    # --- update ------------------------------------------------------------
    def update(self) -> None:
        if self.banner_timer > 0:
            self.banner_timer -= 1
        if self.toast_timer > 0:
            self.toast_timer -= 1
        if self.complete_timer > 0:
            self.complete_timer -= 1
        self._watch_tracker()

        p = self.player
        mine = {(p.tile_x, p.tile_y)} | ({p.front_tile} if p.moving else set())
        self.wanderers.update(mine)
        if self.riding_to is not None:
            self._update_ride()
            return
        if self.shuttle:
            self.shuttle.update(mine | self._people_on_road(), self._beside_shuttle())
        if not p.moving and self.queue:
            self._present(self.queue.pop(0))
            return
        self.queue += self.book.tick()              # mission timers
        if not p.moving:
            if self.input.pressed(Action.CONFIRM):
                self._interact()
                return
            if self.input.pressed(Action.CANCEL):
                msg = self.bike.toggle()          # hop on or off (decisions/0030)
                if msg:
                    self.player.speed = self.bike.speed
                    self._show_toast(msg)
                    self._save()
            if self.input.pressed(Action.MAP):
                self._save()
                self.app.scenes.push(CampusMapScene(
                    self.app, self.map, (p.tile_x, p.tile_y), self.area_name))
                return
            if self.input.pressed(Action.MENU):
                self._save()
                self.app.scenes.push(MenuScene(self.app, self.map))
                return
            for action, direction in DIRECTION_ACTIONS:
                if self.input.held(action):
                    if not p.try_move(direction, self._blocked):
                        # walking into a closed gate starts the guard's ID check
                        ahead = self.map.object_at(*p.front_tile)
                        if ahead and ahead.type == "checkpoint":
                            self._start_checkpoint(ahead)
                            return
                    break
        if p.update():
            self._check_area()
            self._check_auto_npc()
            self._check_near()
            self.autosave_timer -= 1
        self.autosave_timer -= 1 if p.moving else 0
        if self.book.changed or self.autosave_timer <= 0:
            self._save()
        self._update_camera()

    # --- the Campus Shuttle (decisions/0044) ----------------------------------------
    def _blocked(self, x: int, y: int) -> bool:
        return self.map.is_blocked(x, y) or bool(self.shuttle and (x, y) in self.shuttle.cells())

    def _people_on_road(self) -> set:
        """Anyone standing on the road, whom the shuttle mustn't drive into."""
        return {(o.x, o.y) for o in self.map.objects
                if o.type == "npc" and self.map.tiles[o.y][o.x] in ROAD}

    def _beside_shuttle(self) -> bool:
        p = self.player
        cells = self.shuttle.cells()
        return any((p.tile_x + d.dx, p.tile_y + d.dy) in cells for d in Direction)

    def _shuttle_door(self) -> None:
        """You pressed confirm at the shuttle: at a stop, get on and pick
        where to go; anywhere else, the driver waves you to a stop."""
        sh = self.shuttle
        here = sh.stopped_at
        if here is None:
            self.app.scenes.push(DialogueScene(self.app, [
                "The shuttle only lets people on and off at its stops, the maroon shuttle signs.",
                "Wait at any stop and hop on when it pulls in."], "Shuttle Driver"))
            return
        stops = sh.route.stops
        cur = stops.index(here)
        dests = [(cur + k) % len(stops) for k in range(1, len(stops))]   # in the order it drives

        def chosen(i):
            if i < len(dests):
                self._board(dests[i])

        def ask():
            self.app.scenes.push(ChoiceScene(self.app, f"{here.name} stop. Where to?",
                                             [stops[i].name.upper() for i in dests] + ["NOT NOW"],
                                             chosen, "Shuttle Driver"))
        if not self.met_driver:
            self.met_driver = True
            self.app.scenes.push(DialogueScene(self.app, shuttle_mod.lines(self.shuttle_data, "driver"),
                                               "Shuttle Driver", on_close=ask))
        else:
            ask()

    def _board(self, dest: int) -> None:
        if self.bike.riding:                    # you get off your bike first
            self.bike.riding = False
            self.player.speed = self.bike.speed
        self.riding_to, self.skipping = dest, False
        self.player.moving = False
        self.player.progress = 0

    def _update_ride(self) -> None:
        """Riding: the van drives on with you aboard and the camera follows it.
        Back skips ahead (the van goes FAST times quicker) to your stop."""
        if not self.skipping and self.input.pressed(Action.CANCEL):
            self.skipping = True
        people = self._people_on_road()
        for _ in range(shuttle_mod.FAST if self.skipping else 1):
            if self.shuttle.update(people) == self.riding_to:
                self._alight()
                break
        self._update_camera()

    def _alight(self) -> None:
        stop = self.shuttle.route.stops[self.riding_to]
        self.riding_to, self.skipping = None, False
        p = self.player
        x, y = stop.alight
        if self._blocked(x, y):                 # someone's standing there: the next free spot
            x, y = min(((cx, cy) for cy in range(y - 3, y + 4) for cx in range(x - 3, x + 4)
                        if self.map.in_bounds(cx, cy) and not self._blocked(cx, cy)
                        and self.map.tiles[cy][cx] not in ROAD),
                       key=lambda c: abs(c[0] - x) + abs(c[1] - y), default=(x, y))
        p.tile_x, p.tile_y = x, y
        vx, vy = stop.at
        dx, dy = x - vx, y - vy
        p.facing = (Direction.RIGHT if dx > 0 else Direction.LEFT) if abs(dx) > abs(dy) else \
            (Direction.DOWN if dy > 0 else Direction.UP)
        self._check_area()
        self._update_camera()
        self.progress.visited.add("campus_shuttle")
        self.app.scenes.push(DialogueScene(self.app, [f"{stop.name}! Have a great day."], "Shuttle Driver"))
        self.queue += self.book.read("campus_shuttle")      # riding counts for the checklist
        self._save()

    def _stop_sign(self, obj) -> None:
        """A shuttle stop's sign says when the shuttle is next due, then shows its card."""
        stops = self.shuttle.route.stops
        stop = next((i for i, s in enumerate(stops) if s.sign == (obj.x, obj.y)), None)

        def card():
            self._open_card(obj.location)
        if stop is None:
            card()
            return
        when = eta_text(self.shuttle.eta(stop), config.FPS)
        self.app.scenes.push(DialogueScene(self.app, [
            f"Campus Shuttle stop: {stops[stop].name}. {when}",
            controls.fmt("When it pulls in, face its door and press {confirm} to ride.")], on_close=card))

    def _open_card(self, location: str) -> None:
        self.app.scenes.push(BuildingCardScene(self.app, self.app.locations[location]))
        self.progress.visited.add(location)
        self.queue += self.book.read(location)

    # --- missions (decisions/0031) -----------------------------------------------------
    def _save(self) -> None:
        pr = self.progress
        if pr.gate_open:
            pr.started = True
            pr.position = (self.player.tile_x, self.player.tile_y)
            pr.facing = self.player.facing.name.lower()
        self.autosave_timer = AUTOSAVE_FRAMES
        self.app.save()
        self._sync_items()

    def _sync_items(self, bake: bool = True) -> None:
        """Mission items appear while their 'find' step is current."""
        want = {(x, y): (tile, item) for x, y, tile, item in self.book.items()}
        for obj in [o for o in self.map.objects if o.type == "item"]:
            if (obj.x, obj.y) not in want:
                self.map.remove_object(obj.x, obj.y)
                if bake:
                    bake_cell(self.map, TILEMAP_INDEX, obj.x, obj.y)
        for (x, y), (tile, item) in want.items():
            here = self.map.object_at(x, y)
            if here is None and (x, y) != (self.player.tile_x, self.player.tile_y):
                self.map.add_object(MapObject(type="item", x=x, y=y, name=item, tile=tile,
                                              lines=["(a mission item)"]))
                if bake:
                    bake_cell(self.map, TILEMAP_INDEX, x, y)

    def _check_near(self) -> None:
        """Standing next to a door or sign counts as 'going to' that place."""
        p = self.player
        seen = set()
        for d in Direction:
            obj = self.map.object_at(p.tile_x + d.dx, p.tile_y + d.dy)
            if obj and obj.location and obj.location not in seen:
                seen.add(obj.location)
                self.queue += self.book.near(obj.location)

    def _present(self, r: Reaction) -> None:
        """Show one mission Reaction: its lines, the reward, then any offer
        or question. Each part waits for the one before."""
        parts = []
        if r.lines:
            parts.append(lambda nxt: self.app.scenes.push(
                DialogueScene(self.app, r.lines, r.speaker, on_close=nxt)))
        if r.completed:
            def banner(nxt, title=r.completed.title):
                self.complete_title, self.complete_timer = title, COMPLETE_FRAMES
                nxt()
            parts.append(banner)
        if r.rewards:
            parts.append(lambda nxt: self.app.scenes.push(
                DialogueScene(self.app, [f"You got: {x}!" for x in r.rewards], on_close=nxt)))
        if r.offer:
            m = r.offer

            def offer(nxt, m=m):
                def chosen(i):
                    if i == 0:
                        self.queue[:0] = self.book.accept(m.id)
                    else:
                        self.queue.insert(0, Reaction(lines=list(m.giver.get("decline_say", ["Okay!"])),
                                                      speaker=m.giver["npc"]))
                    self._save()
                    nxt()
                self.app.scenes.push(ChoiceScene(self.app, f"Help the {m.giver['npc']}? ({m.title})",
                                                 ["YES", "NOT NOW"], chosen, m.giver["npc"]))
            parts.append(offer)
        if r.question:
            q = r.question

            def ask(nxt, q=q):
                def chosen(i):
                    self.queue[:0] = self.book.answer(q["mission"], q["step"], i)
                    self._save()
                    nxt()
                self.app.scenes.push(ChoiceScene(self.app, q["question"], q["options"], chosen,
                                                 r.speaker, cancel_index=len(q["options"]) - 1))
            parts.append(ask)

        def run(i=0):
            if i < len(parts):
                parts[i](lambda: run(i + 1))
            else:
                self._save()
        run()

    def _show_toast(self, text: str) -> None:
        self.toast = text
        self.toast_timer = TOAST_FRAMES

    def _use_bike_rack(self) -> None:
        lines = self.bike.use_rack()
        self.player.speed = self.bike.speed
        self._save()
        self.app.scenes.push(DialogueScene(self.app, lines))

    def _update_camera(self) -> None:
        p = self.player
        x, y = p.pixel_x + TILE / 2, p.pixel_y + TILE / 2
        if self.riding_to is not None:          # on the shuttle: follow the van
            x, y, _, _ = self.shuttle.pos
        self.cam = follow(
            x, y,
            SCREEN_W, SCREEN_H, self.map.width * TILE, self.map.height * TILE,
        )

    def _check_area(self) -> None:
        """Show the area banner when the player walks into a new area."""
        area = self.map.area_at(self.player.tile_x, self.player.tile_y)
        if area and area.name != self.area_name:
            self.area_name = area.name
            self.banner_timer = BANNER_FRAMES

    def _check_auto_npc(self) -> None:
        """NPCs marked "auto" walk-up greet the player once, Pokemon-style."""
        p = self.player
        found = self.map.auto_npc_next_to(p.tile_x, p.tile_y, self.greeted)
        if not found:
            return
        obj, direction = found
        self.greeted.add((obj.x, obj.y))
        p.facing = direction
        obj.facing = direction.opposite
        self.app.scenes.push(DialogueScene(self.app, obj.lines, obj.name))
        self.queue += self.book.talk(obj.name)

    def _start_checkpoint(self, gate) -> None:
        """Guard's lines -> ID tap -> guard's 'all set' lines -> gate opens.
        The guard (an NPC whose name matches the checkpoint's) turns to you."""
        for o in self.map.objects:
            if o.type == "npc" and o.name == gate.name:
                dx, dy = self.player.tile_x - o.x, self.player.tile_y - o.y
                o.facing = (Direction.RIGHT if dx > 0 else Direction.LEFT) if abs(dx) >= abs(dy) \
                    else (Direction.DOWN if dy > 0 else Direction.UP)

        def open_gate():
            self.map.open_checkpoint(gate.x, gate.y)
            bake_cell(self.map, TILEMAP_INDEX, gate.x, gate.y)
            self.progress.gate_open = True
            self._save()
            if gate.after_lines:
                self.app.scenes.push(DialogueScene(self.app, gate.after_lines, gate.name))

        def tap_in():
            self.app.scenes.push(IdCheckScene(self.app, on_done=open_gate))

        self.app.scenes.push(DialogueScene(self.app, gate.lines, gate.name, on_close=tap_in))

    def _interact(self) -> None:
        fx, fy = self.player.front_tile
        if self.shuttle and (fx, fy) in self.shuttle.cells():
            self._shuttle_door()
            return
        obj = self.map.object_at(fx, fy)
        if obj is None:
            return
        if obj.type == "checkpoint":
            self._start_checkpoint(obj)
        elif obj.type == "bike_rack":
            self._use_bike_rack()
        elif obj.type == "item":
            self.queue += self.book.pickup(obj.name)
            self._save()
        elif obj.type == "npc":
            obj.facing = self.player.facing.opposite
            reactions = self.book.talk(obj.name)
            giver = next((g for g in self.book.givers() if g["npc"] == obj.name), None)
            if giver:                               # a mission giver says only mission things
                self.queue += reactions or [Reaction(
                    lines=list(giver.get("idle_say", ["Thanks again for your help!"])), speaker=obj.name)]
            else:
                self.app.scenes.push(DialogueScene(self.app, obj.lines, obj.name))
                self.queue += reactions
        elif obj.location == "campus_shuttle" and self.shuttle:
            self._stop_sign(obj)
        elif obj.location:
            self._open_card(obj.location)
        else:
            self.app.scenes.push(DialogueScene(self.app, obj.lines))

    # --- draw --------------------------------------------------------------
    def draw(self) -> None:
        cx, cy = self.cam
        if self.world is not None:
            self._draw_world_finer(cx, cy)
            display.camera(cx, cy)
        else:
            pyxel.cls(Col.GREEN)
            display.camera(cx, cy)
            self._draw_world_tiles(cx, cy)
        if self.shuttle and self.shuttle.beep:              # it's stopped for you
            vx, vy, _, _ = self.shuttle.pos
            w = font.width("BEEP!") + 6
            bx, by = int(vx - w / 2), int(vy - 34 - GROW)
            pyxel.rect(bx, by, w, 14 + GROW, Col.WHITE)
            pyxel.rectb(bx, by, w, 14 + GROW, Col.NAVY)
            font.text(bx + 3, by + 1, "BEEP!", Col.MAROON)
        # "!" over people with a mission for you, "?" over people a mission is waiting on
        bob = (pyxel.frame_count // 10) % 2
        for obj in self.map.objects:
            if obj.type == "npc":
                mark = self.book.npc_marker(obj.name)
                if mark:
                    ox, oy, _ = self._npc_xy(obj)
                    bx, by = ox + 3, oy - 17 - bob
                    pyxel.rect(bx, by - GROW, 12, 14 + GROW, Col.WHITE)
                    pyxel.rectb(bx, by - GROW, 12, 14 + GROW, Col.NAVY)
                    font.text(bx + 2, by + 1 - GROW, mark, Col.MAROON)
            elif obj.type == "item":                 # a mission item to pick up (decisions/0041)
                bx, by = obj.x * TILE + 3, obj.y * TILE - 15 - bob
                pyxel.rect(bx, by - GROW, 12, 14 + GROW, Col.WHITE)
                pyxel.rectb(bx, by - GROW, 12, 14 + GROW, Col.NAVY)
                font.text(bx + 2, by + 1 - GROW, "!", Col.MAROON)

        display.camera()
        self._draw_hud()

    def _drawables(self) -> list[tuple]:
        """People and vans as (y, x, sprite, facing, frame), to draw back to
        front so lower ones overlap upper ones. The vans (decisions/0044)
        have sprite -1 (the shuttle) and -2 (the Ram Van), and a heading."""
        drawables: list[tuple] = []
        for obj in self.map.objects:
            if obj.type == "npc":
                ox, oy, frame = self._npc_xy(obj)
                drawables.append((oy, ox, obj.sprite, obj.facing, frame))
        p = self.player
        bike_sprite = MAROON_BIKE_SPRITE if "maroon_bike" in self.progress.unlocks else BIKE_SPRITE
        sprite = bike_sprite if self.bike.riding else PLAYER_SPRITE
        frame = p.anim_frame if not self.bike.riding else (p.progress // 4) % 3 if p.moving else 0
        if self.riding_to is None:              # on the shuttle you're inside the van
            drawables.append((p.pixel_y, p.pixel_x, sprite, p.facing, frame))
        if self.shuttle:
            vx, vy, hx, hy = self.shuttle.pos
            drawables.append((vy - TILE / 2, vx, -1, (hx, hy), 0))
        if self.ram_van:
            rx, ry, rf = self.ram_van
            drawables.append((ry * TILE, (rx + 1) * TILE, -2, (rf.dx, rf.dy), 0))
        return drawables

    def _draw_world_tiles(self, cx: int, cy: int) -> None:
        """The world as tiles, at layout size (when the screen isn't doubled)."""
        pyxel.bltm(cx, cy, TILEMAP_INDEX, cx, cy, SCREEN_W, SCREEN_H)
        # drawn buildings go over their footprint tiles (decisions/0020).
        # Characters can't stand on a footprint, so they're always drawn after.
        for b in self.map.buildings:
            draw_on_map(b)
        pyxel.blt(cx, cy, self.overlay, cx, cy, SCREEN_W, SCREEN_H, Col.BLACK)
        for y, x, sprite, facing, frame in sorted(self._drawables(), key=lambda d: d[0]):
            if sprite < 0:
                self._draw_van(SHUTTLE_VAN if sprite == -1 else RAM_VAN, x, y + TILE / 2, *facing)
                continue
            u, v = character_uv(sprite, facing, frame)
            pyxel.blt(x, y - 2, CHAR_IMAGE_BANK, u, v, TILE, TILE, Col.BLACK)

    def _draw_world_finer(self, cx: int, cy: int) -> None:
        """The world at twice the detail (decisions/0045), straight onto the
        full-size screen: the part of the map picture in view, then trees,
        people and vans back to front, each with its shadow. People and vans
        are today's sprites, doubled, until they're redrawn."""
        full = display.full_image()
        k = ART_SCALE
        ox, oy = cx * k, cy * k
        w = self.world
        full.blt(0, 0, w.image, ox, oy, SCREEN_W * k, SCREEN_H * k)
        w.draw_dynamic(full, ox, oy)
        # trees first, so a person level with a tree stands in front of it
        things = [(ty * TILE, tx * TILE, None, tile, 0)
                  for tx, ty, tile in w.visible_trees(cx, cy, SCREEN_W, SCREEN_H)]
        sheet = pyxel.images[CHAR_IMAGE_BANK]
        for y, x, sprite, facing, frame in sorted(things + self._drawables(), key=lambda d: d[0]):
            if sprite is None:
                w.draw_tree(full, x // TILE, y // TILE, facing, ox, oy)
            elif sprite < 0:
                self._draw_van_finer(full, SHUTTLE_VAN if sprite == -1 else RAM_VAN,
                                     x, y + TILE / 2, *facing, ox, oy)
            else:
                w.shadow(full, x * k + 5 - ox, y * k + 25 - oy, PERSON_SHADOW)
                u, v = character_uv(sprite, facing, frame)
                blt_up(full, x * k - ox, (y - 2) * k - oy, sheet, u, v, TILE, TILE, Col.BLACK)

    def _draw_van_finer(self, full, van: int, cx: float, cy: float, hx: float, hy: float,
                        ox: int, oy: int) -> None:
        """_draw_van on the full-size screen, with a shadow."""
        k = ART_SCALE
        sheet = pyxel.images[CHAR_IMAGE_BANK]
        cx, cy = int(cx), int(cy)
        if abs(hx) >= abs(hy) * 0.7:
            u, v, w = van_uv(van, "side")
            self.world.shadow(full, (cx - 16) * k - ox, (cy + 2) * k - oy, VAN_SIDE_SHADOW)
            blt_up(full, (cx - 16) * k - ox, (cy - 16) * k - oy, sheet, u, v, w * (-1 if hx < 0 else 1), 24,
                   Col.BLACK)
        else:
            u, v, w = van_uv(van, "front" if hy > 0 else "back")
            self.world.shadow(full, (cx - 9) * k - ox, (cy + 3) * k - oy, VAN_END_SHADOW)
            blt_up(full, (cx - 8) * k - ox, (cy - 16) * k - oy, sheet, u, v, w, 24, Col.BLACK)

    def _draw_van(self, van: int, cx: float, cy: float, hx: float, hy: float) -> None:
        """A van with its middle at (cx, cy), heading (hx, hy): side on when
        it drives across or at an angle, front or back when it drives down or up."""
        if abs(hx) >= abs(hy) * 0.7:
            u, v, w = van_uv(van, "side")
            flip = -1 if hx < 0 else 1
            pyxel.blt(int(cx - 16), int(cy - 16), CHAR_IMAGE_BANK, u, v, w * flip, 24, Col.BLACK)
        else:
            u, v, w = van_uv(van, "front" if hy > 0 else "back")
            pyxel.blt(int(cx - 8), int(cy - 16), CHAR_IMAGE_BANK, u, v, w, 24, Col.BLACK)

    def _npc_xy(self, obj) -> tuple[int, int, int]:
        """Where to draw a person (map pixels) and their walking frame."""
        w = self.wanderers.get(obj)
        if w is None:
            return obj.x * TILE, obj.y * TILE, 0
        return (*w.pixel_xy, w.frame)

    def _tracker_key(self):
        m = self.book.tracked()
        steps = self.book.current_steps(m) if m else []
        return (m.id, tuple(steps), tuple(sorted(self.book.state(m).done_steps))) if m else None

    def _watch_tracker(self) -> None:
        """The mission bar stays hidden (a clean screen) unless pinned on in
        the TAB menu. It pops up for a few seconds when the next step changes,
        and stays up while a timed step's clock is running."""
        key = self._tracker_key()
        if self._tracker_last is ...:
            self._tracker_last = key
        if key != self._tracker_last:
            self._tracker_last = key
            self.tracker_timer = TRACKER_FRAMES if key else 0
        elif self.tracker_timer > 0:
            self.tracker_timer -= 1

    def _tracker_visible(self) -> bool:
        if self.progress.show_tracker or self.tracker_timer > 0:
            return True
        m = self.book.tracked()
        return bool(m and self.book.state(m).timer is not None)

    def _draw_hud(self) -> None:
        top = 4
        if self.banner_timer > 0:
            top = 26 + GROW
        tracker = self.book.tracker() if self._tracker_visible() else None
        if tracker:
            most = (SCREEN_W - 20) // BIG_CHAR_W
            text = tracker if len(tracker) <= most else tracker[:most - 1] + "."
            w = font.width(text) + 10
            pyxel.rect(4, top, w, 15 + GROW, Col.NAVY)
            pyxel.rectb(4, top, w, 15 + GROW, Col.PEACH)
            font.text(9, top + 1, text, Col.WHITE)
        if self.complete_timer > 0:
            msg = "MISSION COMPLETE!"
            w = font.width(msg) + 20
            x, y = (SCREEN_W - w) // 2, 40
            w = max(w, font.width(self.complete_title) + 20)
            x = (SCREEN_W - w) // 2
            pyxel.rect(x, y, w, 32 + 2 * GROW, Col.MAROON)
            pyxel.rectb(x, y, w, 32 + 2 * GROW, Col.YELLOW)
            pyxel.rectb(x + 2, y + 2, w - 4, 28 + 2 * GROW, Col.WHITE)
            font.centered(y + 3, msg, Col.YELLOW)
            font.centered(y + 16 + GROW, self.complete_title, Col.WHITE)
        if self.riding_to is not None:
            stop = self.shuttle.route.stops[self.riding_to].name.upper()
            msg = f"SHUTTLE TO {stop}" + ("  SKIPPING AHEAD" if self.skipping else controls.fmt("  {back}: SKIP"))
            w = font.width(msg) + 12
            y = SCREEN_H - 22
            pyxel.rect(4, y - GROW, w, 16 + GROW, Col.MAROON)
            pyxel.rectb(4, y - GROW, w, 16 + GROW, Col.WHITE)
            font.text(10, y + 2 - GROW, msg, Col.WHITE)
        elif self.toast_timer > 0:
            w = font.width(self.toast) + 12
            y = SCREEN_H - 22
            pyxel.rect(4, y - GROW, w, 16 + GROW, Col.NAVY)
            pyxel.rectb(4, y - GROW, w, 16 + GROW, Col.WHITE)
            font.text(10, y + 2 - GROW, self.toast, Col.WHITE)
        if self.banner_timer <= 0:
            return
        name = self.area_name
        w = font.width(name) + 16
        # slide in from the top, then hold
        y = min(4, -18 - GROW + (BANNER_FRAMES - self.banner_timer) * 2)
        pyxel.rect(4, y, w, 18 + GROW, Col.MAROON)
        pyxel.rectb(4, y, w, 18 + GROW, Col.WHITE)
        font.text(12, y + 3, name, Col.WHITE)
