"""The TAB menu (decisions/0031): the Mission Log and the Ram Passport.
LEFT/RIGHT switch tabs, UP/DOWN pick a mission, Z tracks or drops it,
M turns the on-screen tracker on or off, TAB or X closes."""

import math

import pyxel

from game.config import SCREEN_H, SCREEN_W, Col
from game.systems.input import Action
from game.systems.progress import BADGES
from game.ui import font
from game.ui.text import wrap

from .base import Scene
from .choice import ChoiceScene

TABS = ["MISSIONS", "PASSPORT"]
LIST_W = 92
BADGE_COLORS = {"academics": Col.DARK_BLUE, "wellness": Col.LIME, "community": Col.MAROON,
                "career": Col.ORANGE, "dining": Col.YELLOW}


class MenuScene(Scene):
    def __init__(self, app, game_map=None):
        super().__init__(app)
        self.map = game_map
        self.tab = 0
        self.cursor = 0
        self.book = app.missions
        self.progress = app.progress

    # --- which missions to list ---------------------------------------------------
    def _listed(self):
        """Active first, then ones you can start, then finished ones."""
        order = {"active": 0, "available": 1, "done": 2}
        ms = [self.book.missions[i] for i in self.book.order]
        return sorted(ms, key=lambda m: (order[self.book.state(m).status], self.book.order.index(m.id)))

    def update(self) -> None:
        if self.input.pressed(Action.MENU) or self.input.pressed(Action.CANCEL):
            self.app.scenes.pop()
            return
        if self.input.pressed(Action.LEFT) or self.input.pressed(Action.RIGHT):
            self.tab = 1 - self.tab
            return
        if self.input.pressed(Action.MAP):
            self.progress.show_tracker = not self.progress.show_tracker
            self.app.save()
            return
        if self.tab != 0:
            return
        listed = self._listed()
        if self.input.pressed(Action.UP):
            self.cursor = (self.cursor - 1) % len(listed)
        elif self.input.pressed(Action.DOWN):
            self.cursor = (self.cursor + 1) % len(listed)
        elif self.input.pressed(Action.CONFIRM):
            m = listed[self.cursor]
            if self.book.state(m).status != "active":
                return
            options = ["TRACK", "DROP", "BACK"] if m.optional else ["TRACK", "BACK"]

            def chosen(i, m=m, options=options):
                if options[i] == "TRACK":
                    self.progress.tracked = m.id
                elif options[i] == "DROP":
                    self.book.drop(m.id)
                self.app.save()
            self.app.scenes.push(ChoiceScene(self.app, f"{m.title}: what would you like to do?",
                                             options, chosen))

    # --- drawing --------------------------------------------------------------------------
    def draw(self) -> None:
        pyxel.cls(Col.WHITE)
        pyxel.rect(0, 0, SCREEN_W, 16, Col.MAROON)
        x = 6
        for i, name in enumerate(TABS):
            w = font.width(name) + 10
            if i == self.tab:
                pyxel.rect(x - 4, 1, w, 15, Col.WHITE)
                font.text(x + 1, 2, name, Col.MAROON)
            else:
                font.text(x + 1, 2, name, Col.PEACH)
            x += w + 6
        pyxel.text(SCREEN_W - 54, 6, "TAB: CLOSE", Col.WHITE)
        if self.tab == 0:
            self._draw_missions()
        else:
            self._draw_passport()

    def _status_icon(self, m) -> tuple[str, int]:
        st = self.book.state(m).status
        if st == "done":
            return "OK", Col.GREEN
        if st == "active":
            return ">", Col.MAROON
        return "!", Col.ORANGE

    def _draw_missions(self) -> None:
        listed = self._listed()
        self.cursor = min(self.cursor, len(listed) - 1)
        tracked = self.book.tracked()
        for i, m in enumerate(listed):
            y = 22 + i * 16
            if i == self.cursor:
                pyxel.rect(2, y - 2, LIST_W, 15, Col.LIGHT_BLUE)
            icon, col = self._status_icon(m)
            pyxel.text(6, y + 3, icon, col)
            title = m.title if len(m.title) <= 19 else m.title[:18] + "."
            pyxel.text(16, y + 3, title, Col.BLACK)
            if tracked is m:
                pyxel.text(LIST_W - 6, y + 3, "*", Col.MAROON)
        pyxel.line(LIST_W + 4, 18, LIST_W + 4, SCREEN_H - 16, Col.GRAY)
        self._draw_detail(listed[self.cursor], LIST_W + 10)
        y = SCREEN_H - 12
        pyxel.rect(0, y - 2, SCREEN_W, 14, Col.NAVY)
        tr = "ON" if self.progress.show_tracker else "OFF"
        pyxel.text(4, y + 2, f"Z: TRACK/DROP   M: TRACKER {tr}   LEFT/RIGHT: PASSPORT", Col.WHITE)

    def _draw_detail(self, m, x: int) -> None:
        w_chars = (SCREEN_W - x - 4) // 4
        st = self.book.state(m)
        font.text(x, 20, m.title, Col.MAROON)
        y = 36
        for line in wrap(m.summary, w_chars)[:4]:
            pyxel.text(x, y, line, Col.BLACK)
            y += 7
        y += 3
        if st.status == "available":
            where = ""
            if m.giver and self.map is not None:
                area = self.map.area_at(*m.giver["at"])
                where = f" ({area.name})" if area else ""
            msg = f"Look for the {m.giver['npc']}{where}: they'll have a ! over their head." \
                if m.giver else "This starts on its own."
            if not self.book.requirements_met(m) and "bike" in m.requires:
                msg += " You'll need a bike."
            for line in wrap(msg, w_chars):
                pyxel.text(x, y, line, Col.DARK_BLUE)
                y += 7
            return
        current = self.book.current_steps(m)
        for i, s in enumerate(m.steps):
            if y > SCREEN_H - 34:
                pyxel.text(x, y, "...", Col.GRAY)
                break
            done = i in st.done_steps
            mark, col = ("[x]", Col.GREEN) if done else (("[ ]", Col.MAROON) if i in current else ("[ ]", Col.GRAY))
            pyxel.text(x, y, mark, col)
            label = self.book.step_text(m, i)
            for j, line in enumerate(wrap(label, w_chars - 4)[:2]):
                pyxel.text(x + 14, y + j * 7, line, Col.BLACK if not done else Col.GRAY)
            y += 7 * min(2, len(wrap(label, w_chars - 4))) + 2
        if st.status == "active" and current:
            hint = m.steps[current[0]].get("hint")
            if hint:
                hy = SCREEN_H - 32
                for j, line in enumerate(wrap("Hint: " + hint, w_chars)[:2]):
                    pyxel.text(x, hy + j * 7, line, Col.DARK_BLUE)
        elif st.status == "done":
            pyxel.text(x, SCREEN_H - 26, "Finished! Stamp earned.", Col.GREEN)

    def _draw_passport(self) -> None:
        font.text(8, 20, "RAM PASSPORT", Col.MAROON)
        missions = [self.book.missions[i] for i in self.book.order]
        n = len(missions)
        cols = min(n, 4)
        cw = (SCREEN_W - 16) // cols
        for i, m in enumerate(missions):
            cx = 8 + (i % cols) * cw + cw // 2
            cy = 58 + (i // cols) * 48
            stamp = m.reward.get("stamp")
            earned = stamp in self.progress.stamps
            if earned:
                pyxel.circ(cx, cy, 16, Col.MAROON)
                pyxel.circb(cx, cy, 16, Col.NAVY)
                pyxel.circb(cx, cy, 13, Col.PEACH)
                initials = "".join(w[0] for w in m.reward.get("stamp_name", m.title).split()[:2]).upper()
                pyxel.text(cx - len(initials) * 2 + 1, cy - 2, initials, Col.WHITE)
            else:
                for a in range(0, 360, 30):
                    pyxel.pset(cx + round(16 * math.cos(math.radians(a))),
                               cy + round(16 * math.sin(math.radians(a))), Col.GRAY)
                pyxel.text(cx - 1, cy - 2, "?", Col.GRAY)
            name = m.reward.get("stamp_name", m.title)
            pyxel.text(cx - len(name) * 2, cy + 20, name, Col.BLACK if earned else Col.GRAY)
        # badges (decisions/0003)
        by = 130
        pyxel.text(8, by - 10, "BADGES", Col.MAROON)
        bw = (SCREEN_W - 16) // len(BADGES)
        for i, b in enumerate(BADGES):
            cx = 8 + i * bw + bw // 2
            got = b in self.progress.badges
            pyxel.circ(cx, by + 6, 6, BADGE_COLORS[b] if got else Col.WHITE)
            pyxel.circb(cx, by + 6, 6, Col.NAVY if got else Col.GRAY)
            pyxel.text(cx - 1, by + 4, b[0].upper(), Col.WHITE if got else Col.GRAY)
            pyxel.text(cx - len(b) * 2, by + 15, b.upper(), Col.BLACK if got else Col.GRAY)
        y = SCREEN_H - 12
        pyxel.rect(0, y - 2, SCREEN_W, 14, Col.NAVY)
        got, total = len(self.progress.stamps), n
        msg = f"STAMPS {got}/{total}"
        if "maroon_bike" in self.progress.unlocks:
            msg += "   MAROON BIKE UNLOCKED"
        if got >= total:
            msg = "PASSPORT COMPLETE! WELCOME TO FORDHAM"
        pyxel.text(4, y + 2, msg, Col.WHITE)
