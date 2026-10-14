"""The TAB menu (decisions/0031): the Mission Log and the Ram Passport.

Everything is drawn in the reading font (PixelMplus, decisions/0018), so
the log is a list plus a short preview of the selected mission; Z opens
that mission's full page (summary, checklist, hint, reward), where Z
tracks or drops it.

Mission Log:   UP/DOWN pick, Z full page, M tracker on/off, LEFT/RIGHT tab
Mission page:  UP/DOWN scroll, Z track/drop, X back
TAB closes the menu from anywhere."""

import math

import pyxel

from game.config import SCREEN_H, SCREEN_W, Col
from game.systems import controls
from game.systems.input import Action
from game.systems.progress import BADGES
from game.ui import font
from game.ui.text import BIG_CHAR_W, GROW, wrap

from .base import Scene
from .choice import ChoiceScene

TABS = ["MISSIONS", "PASSPORT"]
LINE_H = 13 + GROW   # reading-font line spacing in the menu
HEADER_H = 16 + GROW
FOOTER_Y = SCREEN_H - 15 - GROW
ROW_H = 15 + GROW    # one mission per row in the log
LIST_Y = HEADER_H + 3
LIST_ROWS = 4        # rows shown at once; the list scrolls if there are more
TEXT_CHARS = (SCREEN_W - 12) // BIG_CHAR_W   # 40 characters across the screen
BADGE_COLORS = {"academics": Col.DARK_BLUE, "wellness": Col.LIME, "community": Col.MAROON,
                "career": Col.ORANGE, "dining": Col.YELLOW}


class MenuScene(Scene):
    def __init__(self, app, game_map=None):
        super().__init__(app)
        self.map = game_map
        self.tab = 0
        self.cursor = 0
        self.top = 0              # first row shown in the log
        self.page = None          # the mission whose full page is open
        self.scroll = 0
        self.book = app.missions
        self.progress = app.progress

    # --- which missions to list ---------------------------------------------------
    def _listed(self):
        """Active first, then ones you can start, then finished ones."""
        order = {"active": 0, "available": 1, "done": 2}
        ms = [self.book.missions[i] for i in self.book.order]
        return sorted(ms, key=lambda m: (order[self.book.state(m).status], self.book.order.index(m.id)))

    def update(self) -> None:
        if self.input.pressed(Action.MENU):
            self.app.scenes.pop()
            return
        if self.page is not None:
            self._update_page()
            return
        if self.input.pressed(Action.CANCEL):
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
            self.page = listed[self.cursor]
            self.scroll = 0

    def _update_page(self) -> None:
        m = self.page
        if self.input.pressed(Action.CANCEL):
            self.page = None
            return
        most = max(0, len(self._page_lines(m)) - self._page_rows())
        if self.input.pressed(Action.UP):
            self.scroll = max(0, self.scroll - 1)
        elif self.input.pressed(Action.DOWN):
            self.scroll = min(most, self.scroll + 1)
        elif self.input.pressed(Action.CONFIRM) and self.book.state(m).status == "active":
            options = ["TRACK", "DROP", "BACK"] if m.optional else ["TRACK", "BACK"]

            def chosen(i, m=m, options=options):
                if options[i] == "TRACK":
                    self.progress.tracked = m.id
                elif options[i] == "DROP":
                    self.book.drop(m.id)
                    self.page = None
                self.app.save()
            self.app.scenes.push(ChoiceScene(self.app, f"{m.title}: what would you like to do?",
                                             options, chosen))

    # --- what to say about a mission ----------------------------------------------
    def _where(self, m) -> str:
        where = ""
        if m.giver and self.map is not None:
            area = self.map.area_at(*m.giver["at"])
            where = f" ({area.name})" if area else ""
        msg = f"Look for the {m.giver['npc']}{where}: they'll have a ! over their head." \
            if m.giver else "This starts on its own."
        if not self.book.requirements_met(m) and "bike" in m.requires:
            msg += " You'll need a bike."
        return msg

    def _hint(self, m) -> str | None:
        current = self.book.current_steps(m)
        if self.book.state(m).status == "active" and current:
            return m.steps[current[0]].get("hint")
        return None

    def _reward(self, m) -> str:
        r = m.reward
        parts = []
        if r.get("stamp"):
            parts.append(f"{r.get('stamp_name', m.title)} stamp")
        if r.get("badge"):
            parts.append(f"{r['badge'].title()} badge")
        if r.get("unlock"):
            parts.append(r.get("unlock_name", r["unlock"]))
        return ", ".join(parts)

    def _page_lines(self, m) -> list[tuple[int, str, int]]:
        """The full page as (indent px, text, colour) lines."""
        st = self.book.state(m)
        out = [(0, line, Col.BLACK) for line in wrap(m.summary, TEXT_CHARS)]
        out.append((0, "", Col.BLACK))
        if st.status == "available":
            out += [(0, line, Col.DARK_BLUE) for line in wrap(self._where(m), TEXT_CHARS)]
        else:
            current = self.book.current_steps(m)
            for i in range(len(m.steps)):
                done = i in st.done_steps
                mark = "[x]" if done else "[ ]"
                col = Col.GRAY if done else (Col.MAROON if i in current else Col.BLACK)
                for j, line in enumerate(wrap(self.book.step_text(m, i), TEXT_CHARS - 4)):
                    out.append((0, f"{mark} {line}" if j == 0 else f"    {line}", col))
            hint = self._hint(m)
            if hint:
                out.append((0, "", Col.BLACK))
                out += [(0, line, Col.DARK_BLUE) for line in wrap("Hint: " + hint, TEXT_CHARS)]
        reward = self._reward(m)
        if reward:
            out.append((0, "", Col.BLACK))
            label = "Earned: " if st.status == "done" else "Reward: "
            out += [(0, line, Col.GREEN if st.status == "done" else Col.MAROON)
                    for line in wrap(label + reward, TEXT_CHARS)]
        return out

    @staticmethod
    def _page_rows() -> int:
        return (FOOTER_Y - (HEADER_H + 4)) // LINE_H

    # --- drawing --------------------------------------------------------------------------
    def draw(self) -> None:
        pyxel.cls(Col.WHITE)
        if self.page is not None:
            self._draw_page(self.page)
            return
        pyxel.rect(0, 0, SCREEN_W, HEADER_H, Col.MAROON)
        x = 6
        for i, name in enumerate(TABS):
            w = font.width(name) + 10
            if i == self.tab:
                pyxel.rect(x - 4, 1, w, HEADER_H - 1, Col.WHITE)
                font.text(x + 1, 2, name, Col.MAROON)
            else:
                font.text(x + 1, 2, name, Col.PEACH)
            x += w + 6
        close = f"{controls.key('menu')}: CLOSE"
        font.text(SCREEN_W - 6 - font.width(close), 2, close, Col.WHITE)
        if self.tab == 0:
            self._draw_missions()
        else:
            self._draw_passport()

    def _footer(self, msg: str) -> None:
        pyxel.rect(0, FOOTER_Y, SCREEN_W, SCREEN_H - FOOTER_Y, Col.NAVY)
        font.text(6, FOOTER_Y + 1, msg, Col.WHITE)

    def _status(self, m) -> tuple[str, int]:
        """What the row says on the right: NEW, steps done, or DONE."""
        st = self.book.state(m)
        if st.status == "done":
            return "DONE", Col.GREEN
        if st.status == "active":
            return f"{len(st.done_steps)}/{len(m.steps)}", Col.MAROON
        return "NEW", Col.ORANGE

    def _draw_icon(self, x: int, y: int, m) -> None:
        """A tick for done, an arrow for in progress, a ! for not started."""
        st = self.book.state(m).status
        if st == "done":
            pyxel.line(x, y + 4, x + 2, y + 6, Col.GREEN)
            pyxel.line(x, y + 5, x + 2, y + 7, Col.GREEN)
            pyxel.line(x + 2, y + 6, x + 7, y + 1, Col.GREEN)
            pyxel.line(x + 2, y + 7, x + 7, y + 2, Col.GREEN)
        elif st == "active":
            pyxel.tri(x + 1, y, x + 1, y + 8, x + 6, y + 4, Col.MAROON)
        else:
            pyxel.rect(x + 3, y, 2, 6, Col.ORANGE)
            pyxel.rect(x + 3, y + 7, 2, 2, Col.ORANGE)

    def _draw_missions(self) -> None:
        listed = self._listed()
        self.cursor = min(self.cursor, len(listed) - 1)
        if self.cursor < self.top:
            self.top = self.cursor
        elif self.cursor >= self.top + LIST_ROWS:
            self.top = self.cursor - LIST_ROWS + 1
        tracked = self.book.tracked()
        for row, m in enumerate(listed[self.top:self.top + LIST_ROWS]):
            i = self.top + row
            y = LIST_Y + row * ROW_H
            if i == self.cursor:
                pyxel.rect(2, y - 1, SCREEN_W - 4, ROW_H, Col.LIGHT_BLUE)
            self._draw_icon(6, y + 3 + GROW // 2, m)
            status, col = self._status(m)
            sx = SCREEN_W - 8 - font.width(status)
            room = (sx - 22 - 14) // BIG_CHAR_W
            title = m.title if len(m.title) <= room else m.title[:room - 1] + "."
            font.text(20, y + 1, title, Col.BLACK)
            font.text(sx, y + 1, status, col)
            if tracked is m:   # a little maroon flag for the tracked mission
                fx = sx - 12
                pyxel.line(fx, y + 2, fx, y + 11, Col.NAVY)
                pyxel.tri(fx + 1, y + 2, fx + 1, y + 7, fx + 6, y + 4, Col.MAROON)
        if self.top > 0:
            pyxel.tri(SCREEN_W // 2 - 3, LIST_Y - 1, SCREEN_W // 2 + 3, LIST_Y - 1, SCREEN_W // 2, LIST_Y - 4, Col.GRAY)
        sep = LIST_Y + LIST_ROWS * ROW_H + 1
        if self.top + LIST_ROWS < len(listed):
            pyxel.tri(SCREEN_W // 2 - 3, sep - 2, SCREEN_W // 2 + 3, sep - 2, SCREEN_W // 2, sep + 1, Col.GRAY)
        pyxel.line(6, sep, SCREEN_W - 7, sep, Col.GRAY)
        self._draw_preview(listed[self.cursor], sep + 3)
        tr = "PINNED" if self.progress.show_tracker else "AUTO"
        self._footer(controls.fmt(f"{{confirm}}: OPEN  {{map}}: BAR {tr}  LEFT/RIGHT: TAB"))

    def _draw_preview(self, m, y: int) -> None:
        """What to do next for the selected mission; the full page has the rest."""
        st = self.book.state(m)
        lines: list[tuple[str, int]] = []
        if st.status == "available":
            lines = [(t, Col.BLACK) for t in wrap(m.summary, TEXT_CHARS)]
        elif st.status == "done":
            lines = [("Finished!", Col.GREEN)]
            if self._reward(m):
                lines += [(t, Col.GREEN) for t in wrap("Earned: " + self._reward(m), TEXT_CHARS)]
        else:
            current = self.book.current_steps(m)
            if len(current) == 1:
                lines = [(t, Col.MAROON) for t in wrap("Next: " + self.book.step_text(m, current[0]), TEXT_CHARS)]
            elif current:
                lines = [(f"Still to do ({len(current)}):", Col.MAROON)]
                lines += [(t, Col.BLACK) for i in current for t in
                          wrap("- " + self.book.step_text(m, i), TEXT_CHARS)]
            hint = self._hint(m)
            if hint:
                lines += [(t, Col.DARK_BLUE) for t in wrap("Hint: " + hint, TEXT_CHARS)]
        rows = (FOOTER_Y - y) // LINE_H
        if len(lines) > rows:   # too long for the preview: Z shows it all
            lines = lines[:rows]
            text, col = lines[-1]
            lines[-1] = (text[:TEXT_CHARS - 4].rstrip() + " ...", col)
        for j, (text, col) in enumerate(lines):
            font.text(6, y + j * LINE_H, text, col)

    def _draw_page(self, m) -> None:
        st = self.book.state(m)
        pyxel.rect(0, 0, SCREEN_W, HEADER_H, Col.MAROON)
        font.text(6, 2, m.title, Col.WHITE)
        tag = {"active": "IN PROGRESS", "available": "NOT STARTED", "done": "DONE"}[st.status]
        font.text(SCREEN_W - 6 - font.width(tag), 2, tag, Col.PEACH)
        if self.book.tracked() is m:
            fx = SCREEN_W - 18 - font.width(tag)
            pyxel.line(fx, 3, fx, 12, Col.WHITE)
            pyxel.tri(fx + 1, 3, fx + 1, 8, fx + 6, 5, Col.YELLOW)
        lines = self._page_lines(m)
        rows = self._page_rows()
        self.scroll = min(self.scroll, max(0, len(lines) - rows))
        y0 = HEADER_H + 4
        for j, (indent, text, col) in enumerate(lines[self.scroll:self.scroll + rows]):
            font.text(6 + indent, y0 + j * LINE_H, text, col)
        cx = SCREEN_W - 8
        if self.scroll > 0:
            pyxel.tri(cx - 3, y0 + 4, cx + 3, y0 + 4, cx, y0, Col.MAROON)
        if self.scroll + rows < len(lines):
            yb = FOOTER_Y - 6
            pyxel.tri(cx - 3, yb, cx + 3, yb, cx, yb + 4, Col.MAROON)
        if st.status == "active":
            act = "TRACK/DROP" if m.optional else "TRACK"
            self._footer(controls.fmt(f"{{confirm}}: {act}  UP/DOWN: SCROLL  {{back}}: BACK"))
        else:
            self._footer(controls.fmt("UP/DOWN: SCROLL  {back}: BACK"))

    def _draw_passport(self) -> None:
        font.text(8, HEADER_H + 3, "RAM PASSPORT", Col.MAROON)
        missions = [self.book.missions[i] for i in self.book.order]
        n = len(missions)
        cols = min(n, 4)
        cw = (SCREEN_W - 16) // cols
        for i, m in enumerate(missions):
            cx = 8 + (i % cols) * cw + cw // 2
            cy = 56 + (i // cols) * 56
            stamp = m.reward.get("stamp")
            earned = stamp in self.progress.stamps
            if earned:
                pyxel.circ(cx, cy, 16, Col.MAROON)
                pyxel.circb(cx, cy, 16, Col.NAVY)
                pyxel.circb(cx, cy, 13, Col.PEACH)
                words = [w for w in m.reward.get("stamp_name", m.title).split()
                         if w.lower() not in ("and", "of", "the", "a")]
                initials = "".join(w[0] for w in words[:2]).upper()
                font.text(cx - font.width(initials) // 2, cy - 6 - GROW // 2, initials, Col.WHITE)
            else:
                for a in range(0, 360, 30):
                    pyxel.pset(cx + round(16 * math.cos(math.radians(a))),
                               cy + round(16 * math.sin(math.radians(a))), Col.GRAY)
                font.text(cx - 4, cy - 6 - GROW // 2, "?", Col.GRAY)
            name = m.reward.get("stamp_name", m.title)
            for j, line in enumerate(wrap(name, (cw - 2) // BIG_CHAR_W)[:2]):
                font.text(cx - font.width(line) // 2, cy + 19 + j * (12 + GROW), line, Col.BLACK if earned else Col.GRAY)
        # badges (decisions/0003): three to a row, a coloured disc then the name
        by = 120
        font.text(8, by, "BADGES", Col.MAROON)
        bw = (SCREEN_W - 16) // 3
        for i, b in enumerate(BADGES):
            x = 10 + (i % 3) * bw
            y = by + 15 + (i // 3) * 14
            got = b in self.progress.badges
            pyxel.circ(x + 5, y + 6, 5, BADGE_COLORS[b] if got else Col.WHITE)
            pyxel.circb(x + 5, y + 6, 5, Col.NAVY if got else Col.GRAY)
            font.text(x + 14, y, b.title(), Col.BLACK if got else Col.GRAY)
        got, total = len(self.progress.stamps), n
        msg = f"STAMPS {got}/{total}"
        if "maroon_bike" in self.progress.unlocks:
            msg += "   MAROON BIKE UNLOCKED"
        if got >= total:
            msg = "PASSPORT COMPLETE! WELCOME TO FORDHAM"
        self._footer(msg)
