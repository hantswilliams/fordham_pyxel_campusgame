"""Missions (decisions/0031): optional side quests, plus the First Week
Checklist as the one required mission. Each mission is a JSON file in
content/missions/ (copy _TEMPLATE.json). This module loads and checks those
files and runs them. Pure logic, no Pyxel: the overworld reports what the
player did (talked to someone, opened a card, stood by a door, picked
something up, answered a question) and gets back Reactions to show.

Step types ("do"):
  talk     talk to a person                         {"npc"}
  go_to    walk up to a place's door or sign        {"location"}
  read     open a place's card                      {"location"}
  find     pick up an item placed on the map        {"item", "name", "at", "tile"}
  answer   answer a person's multiple-choice question {"npc", "question", "options", "correct"}
  ride     get to a place, optionally against the clock {"location", "seconds", "restart_from"}
  collect  do `need` of a set of targets, any order {"need", "targets": [{"location", "do"}]}
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from game.systems import controls

from .progress import BADGES, MissionState, Progress

STEP_TYPES = {"talk", "go_to", "read", "find", "answer", "ride", "collect"}
FPS = 30
ITEM_TILES = {"item_card", "item_card_road", "item_package"}
UNLOCKS = {"maroon_bike"}


class MissionError(ValueError):
    pass


@dataclass
class Mission:
    id: str
    title: str
    summary: str
    steps: list[dict]
    optional: bool = True
    any_order: bool = False
    giver: dict | None = None
    requires: list[str] = field(default_factory=list)
    teaches: list[str] = field(default_factory=list)
    reward: dict = field(default_factory=dict)
    done_say: list[str] = field(default_factory=list)


@dataclass
class Reaction:
    """Something to show the player, in order: lines of dialogue (from
    `speaker`), then a question or an offer if there is one."""
    lines: list[str] = field(default_factory=list)
    speaker: str = ""
    offer: Mission | None = None               # ask YES / NOT NOW, then call accept()
    question: dict | None = None               # {"mission", "step", "question", "options"}
    completed: Mission | None = None           # show MISSION COMPLETE
    rewards: list[str] = field(default_factory=list)  # e.g. "Stamp: Lost and Found"


# --- loading ---------------------------------------------------------------------
def _mission_from_dict(d: dict, where: str) -> Mission:
    for key in ("id", "title", "summary", "steps"):
        if key not in d:
            raise MissionError(f"{where}: missing {key!r}")
    if not d["steps"]:
        raise MissionError(f"{where}: needs at least one step")
    return Mission(
        id=d["id"], title=d["title"], summary=d["summary"], steps=list(d["steps"]),
        optional=bool(d.get("optional", True)),
        any_order=d.get("order", "in_order") == "any",
        giver=d.get("giver"), requires=list(d.get("requires", [])),
        teaches=list(d.get("teaches", [])), reward=dict(d.get("reward", {})),
        done_say=list(d.get("done_say", [])),
    )


def load_missions(folder: Path) -> list[Mission]:
    """Every *.json in the folder except ones starting with '_' (the template).
    The required mission (the checklist) comes first."""
    out = []
    for path in sorted(folder.glob("*.json")):
        if path.name.startswith("_"):
            continue
        try:
            d = json.loads(controls.fmt(path.read_text()))   # button names (decisions/0043)
        except ValueError as e:
            raise MissionError(f"{path.name}: not valid JSON ({e})") from e
        m = _mission_from_dict(d, path.name)
        if m.id != path.stem:
            raise MissionError(f"{path.name}: id {m.id!r} should match the file name")
        out.append(m)
    return sorted(out, key=lambda m: m.optional)


def validate(missions: list[Mission], locations: dict, npc_names: set[str],
             is_free: Callable[[int, int], bool]) -> list[str]:
    """Problems with the mission files, as readable strings (empty = all good).
    `npc_names`: people on the map. `is_free(x, y)`: walkable and unoccupied."""
    problems = []
    ids = {m.id for m in missions}
    stamps = set()
    givers = {m.giver["npc"] for m in missions if m.giver}
    people = npc_names | givers
    for m in missions:
        w = f"{m.id}"
        if m.giver:
            if not {"npc", "at"} <= set(m.giver):
                problems.append(f"{w}: giver needs 'npc' and 'at'")
            elif not is_free(*m.giver["at"]):
                problems.append(f"{w}: giver {m.giver['npc']!r} at {m.giver['at']} isn't on a free walkable tile")
            if not m.giver.get("offer"):
                problems.append(f"{w}: giver needs 'offer' lines")
        elif m.optional:
            problems.append(f"{w}: an optional mission needs a giver to offer it")
        for r in m.requires:
            if r != "bike" and not (r.startswith("mission:") and r[8:] in ids):
                problems.append(f"{w}: unknown requirement {r!r}")
        for i, s in enumerate(m.steps):
            sw = f"{w} step {i + 1}"
            kind = s.get("do")
            if kind not in STEP_TYPES:
                problems.append(f"{sw}: unknown step type {kind!r}")
                continue
            if kind in ("go_to", "read", "ride") and s.get("location") not in locations:
                problems.append(f"{sw}: unknown location {s.get('location')!r}")
            if kind in ("talk", "answer") and s.get("npc") not in people:
                problems.append(f"{sw}: no one called {s.get('npc')!r} on the map")
            if kind == "find":
                if not {"item", "name", "at"} <= set(s):
                    problems.append(f"{sw}: find needs 'item', 'name' and 'at'")
                elif not is_free(*s["at"]):
                    problems.append(f"{sw}: item at {s['at']} isn't on a free walkable tile")
                if s.get("tile", "item_card") not in ITEM_TILES:
                    problems.append(f"{sw}: unknown item tile {s.get('tile')!r}")
            if kind == "answer":
                opts = s.get("options", [])
                if not s.get("question") or len(opts) < 2:
                    problems.append(f"{sw}: a question needs text and at least two options")
                elif not (isinstance(s.get("correct"), int) and 0 <= s["correct"] < len(opts)):
                    problems.append(f"{sw}: 'correct' must be the index of one of the options")
            if kind == "ride":
                rf = s.get("restart_from", i)
                if not (0 <= rf <= i):
                    problems.append(f"{sw}: restart_from must be this step or an earlier one")
            if kind == "collect":
                targets = s.get("targets", [])
                if not targets or not (1 <= s.get("need", len(targets)) <= len(targets)):
                    problems.append(f"{sw}: collect needs targets and 1 <= need <= number of targets")
                for t in targets:
                    if t.get("location") not in locations:
                        problems.append(f"{sw}: unknown location {t.get('location')!r}")
                    if t.get("do", "read") not in ("read", "go_to"):
                        problems.append(f"{sw}: collect targets can be 'read' or 'go_to'")
            if s.get("badge") and s["badge"] not in BADGES:
                problems.append(f"{sw}: unknown badge {s['badge']!r}")
        r = m.reward
        if r.get("badge") and r["badge"] not in BADGES:
            problems.append(f"{w}: unknown badge {r['badge']!r}")
        if r.get("unlock") and r["unlock"] not in UNLOCKS:
            problems.append(f"{w}: unknown unlock {r['unlock']!r}")
        if not r.get("stamp"):
            problems.append(f"{w}: every mission earns a stamp")
        elif r["stamp"] in stamps:
            problems.append(f"{w}: stamp {r['stamp']!r} is used twice")
        stamps.add(r.get("stamp"))
    return problems


# --- running -----------------------------------------------------------------------
class MissionBook:
    """Runs the missions against the player's Progress. `has_bike` tells it
    whether the player has a bike (for "requires": ["bike"])."""

    def __init__(self, missions: list[Mission], progress: Progress,
                 location_names: dict[str, str] | None = None,
                 has_bike: Callable[[], bool] = lambda: False):
        self.missions = {m.id: m for m in missions}
        self.order = [m.id for m in missions]
        self.progress = progress
        self.names = location_names or {}
        self.has_bike = has_bike
        self.changed = False          # set whenever progress changes; the game saves and clears it

    # --- state helpers -------------------------------------------------------------
    def state(self, m: Mission) -> MissionState:
        return self.progress.mission(m.id)

    def active(self) -> list[Mission]:
        return [self.missions[i] for i in self.order if self.state(self.missions[i]).status == "active"]

    def current_steps(self, m: Mission) -> list[int]:
        st = self.state(m)
        if st.status != "active":
            return []
        todo = [i for i in range(len(m.steps)) if i not in st.done_steps]
        return todo if m.any_order else todo[:1]

    def requirements_met(self, m: Mission) -> bool:
        for r in m.requires:
            if r == "bike" and not self.has_bike():
                return False
            if r.startswith("mission:") and self.progress.mission(r[8:]).status != "done":
                return False
        return True

    def _name(self, location: str) -> str:
        return self.names.get(location, location.replace("_", " ").title())

    # --- starting ---------------------------------------------------------------------
    def auto_start(self) -> list[Reaction]:
        """Missions with no giver (the checklist) start on their own."""
        out = []
        for i in self.order:
            m = self.missions[i]
            if not m.giver and self.state(m).status == "available" and self.requirements_met(m):
                out += self.accept(m.id, quiet=True)
        return out

    def accept(self, mission_id: str, quiet: bool = False) -> list[Reaction]:
        m = self.missions[mission_id]
        st = self.state(m)
        st.status, st.done_steps, st.collected, st.timer = "active", [], {}, None
        if m.optional:
            self.progress.tracked = m.id      # follow the side mission you just took on
        self.changed = True
        out = []
        # a first "talk" step with the giver is done by agreeing to help
        first = m.steps[0]
        if m.giver and first.get("do") == "talk" and first.get("npc") == m.giver["npc"]:
            out += self._complete_step(m, 0, speaker=m.giver["npc"])
        else:
            self._activate(m)
        if not quiet and not out:
            out.append(Reaction(lines=[f"Mission started: {m.title}."]))
        return out

    def drop(self, mission_id: str) -> None:
        """Give up a mission; it can be offered again."""
        m = self.missions[mission_id]
        if m.optional:
            self.progress.missions[m.id] = MissionState()
            if self.progress.tracked == m.id:
                self.progress.tracked = None
            self.changed = True

    # --- what the player did ----------------------------------------------------------------
    def talk(self, npc: str) -> list[Reaction]:
        out = []
        for m in self.active():
            for i in self.current_steps(m):
                s = m.steps[i]
                if s.get("npc") != npc:
                    continue
                if s["do"] == "talk":
                    out += self._complete_step(m, i, speaker=npc)
                elif s["do"] == "answer":
                    out.append(Reaction(lines=list(s.get("ask_say", [])), speaker=npc,
                                        question={"mission": m.id, "step": i,
                                                  "question": s["question"], "options": s["options"]}))
        if out:
            return out
        for i in self.order:
            m = self.missions[i]
            if m.giver and m.giver["npc"] == npc and self.state(m).status == "available":
                if not self.requirements_met(m):
                    return [Reaction(lines=list(m.giver.get("requires_say", ["Come back a bit later!"])),
                                     speaker=npc)]
                return [Reaction(lines=list(m.giver["offer"]), speaker=npc, offer=m)]
        return []

    def answer(self, mission_id: str, step: int, choice: int) -> list[Reaction]:
        m = self.missions[mission_id]
        s = m.steps[step]
        if step not in self.current_steps(m):
            return []
        if choice == s["correct"]:
            return self._complete_step(m, step, speaker=s.get("npc", ""))
        return [Reaction(lines=list(s.get("wrong_say", ["Not quite. Have another look, then ask me again."])),
                         speaker=s.get("npc", ""))]

    def read(self, location: str) -> list[Reaction]:
        return self._place_event(location, "read")

    def near(self, location: str) -> list[Reaction]:
        return self._place_event(location, "go_to")

    def _place_event(self, location: str, how: str) -> list[Reaction]:
        out = []
        for m in self.active():
            for i in self.current_steps(m):
                s = m.steps[i]
                kind = s["do"]
                if s.get("location") == location and (
                        kind == how or (how == "go_to" and kind == "ride")
                        or (how == "read" and kind in ("go_to", "ride"))):
                    out += self._complete_step(m, i)
                elif kind == "collect":
                    for t in s["targets"]:
                        if t["location"] == location and t.get("do", "read") in (how, "go_to" if how == "read" else how):
                            out += self._collect(m, i, t)
        return out

    def pickup(self, item: str) -> list[Reaction]:
        out = []
        for m in self.active():
            for i in self.current_steps(m):
                s = m.steps[i]
                if s["do"] == "find" and s["item"] == item:
                    out += self._complete_step(m, i)
        return out

    def tick(self, frames: int = 1) -> list[Reaction]:
        """Run timers. A ride that runs out of time sends you back."""
        out = []
        for m in self.active():
            st = self.state(m)
            if st.timer is None:
                continue
            st.timer -= frames
            if st.timer <= 0:
                st.timer = None
                step = next((i for i in self.current_steps(m) if m.steps[i]["do"] == "ride"), None)
                if step is None:
                    continue
                s = m.steps[step]
                back = s.get("restart_from", step)
                st.done_steps = [i for i in st.done_steps if i < back]
                self.changed = True
                self._activate(m)
                out.append(Reaction(lines=list(s.get("fail_say", ["Out of time! Try again."]))))
        return out

    # --- completing ------------------------------------------------------------------------------
    def _collect(self, m: Mission, i: int, target: dict) -> list[Reaction]:
        st = self.state(m)
        got = st.collected.setdefault(str(i), [])
        if target["location"] in got:
            return []
        got.append(target["location"])
        self.changed = True
        s = m.steps[i]
        need = s.get("need", len(s["targets"]))
        out = []
        lines = list(target.get("say", []))
        if len(got) < need:
            lines.append(f"{s.get('label', m.title)}: {len(got)} of {need}.")
            out.append(Reaction(lines=lines))
        else:
            if lines:
                out.append(Reaction(lines=lines))
            out += self._complete_step(m, i)
        return out

    def _activate(self, m: Mission) -> None:
        """Start the clock on a timed ride that just became current."""
        st = self.state(m)
        for i in self.current_steps(m):
            s = m.steps[i]
            if s["do"] == "ride" and s.get("seconds") and st.timer is None:
                st.timer = int(s["seconds"] * FPS)

    def _complete_step(self, m: Mission, i: int, speaker: str = "") -> list[Reaction]:
        st = self.state(m)
        if i in st.done_steps:
            return []
        s = m.steps[i]
        st.done_steps.append(i)
        if s["do"] == "ride":
            st.timer = None
        self.changed = True
        out = []
        rewards = []
        if s.get("badge") and s["badge"] not in self.progress.badges:
            self.progress.badges.add(s["badge"])
            rewards.append(f"Badge: {s['badge'].title()}")
        if s.get("say") or rewards:
            out.append(Reaction(lines=list(s.get("say", [])), speaker=speaker if s["do"] in ("talk", "answer") else "",
                                rewards=rewards))
        if len(st.done_steps) == len(m.steps):
            out.append(self._finish(m))
        else:
            self._activate(m)
            # the same person asking the next question straight away
            if speaker:
                for j in self.current_steps(m):
                    nxt = m.steps[j]
                    if nxt["do"] == "answer" and nxt.get("npc") == speaker:
                        out.append(Reaction(lines=list(nxt.get("ask_say", [])), speaker=speaker,
                                            question={"mission": m.id, "step": j,
                                                      "question": nxt["question"], "options": nxt["options"]}))
                        break
        return out

    def _finish(self, m: Mission) -> Reaction:
        st = self.state(m)
        st.status, st.timer = "done", None
        r = m.reward
        rewards = []
        if r.get("stamp") and r["stamp"] not in self.progress.stamps:
            self.progress.stamps.append(r["stamp"])
            rewards.append(f"Ram Passport stamp: {r.get('stamp_name', m.title)}")
        if r.get("badge") and r["badge"] not in self.progress.badges:
            self.progress.badges.add(r["badge"])
            rewards.append(f"Badge: {r['badge'].title()}")
        if r.get("unlock") and r["unlock"] not in self.progress.unlocks:
            self.progress.unlocks.add(r["unlock"])
            rewards.append(r.get("unlock_name", r["unlock"].replace("_", " ").title()))
        if self.progress.tracked == m.id:
            nxt = [a for a in self.active() if a.optional] or self.active()
            self.progress.tracked = nxt[0].id if nxt else None
        self.changed = True
        return Reaction(lines=list(m.done_say), speaker=(m.giver or {}).get("npc", ""),
                        completed=m, rewards=rewards)

    # --- for the screen ------------------------------------------------------------------------------
    def npc_marker(self, npc: str) -> str | None:
        """'!' over someone with a mission for you, '?' over someone a
        mission you're doing is waiting on."""
        for m in self.active():
            for i in self.current_steps(m):
                if m.steps[i].get("npc") == npc:
                    return "?"
        for i in self.order:
            m = self.missions[i]
            if m.giver and m.giver["npc"] == npc and self.state(m).status == "available":
                return "!"
        return None

    def givers(self) -> list[dict]:
        return [m.giver for m in self.missions.values() if m.giver]

    def items(self) -> list[tuple[int, int, str, str]]:
        """(x, y, tile, item id) for items waiting to be picked up."""
        out = []
        for m in self.active():
            for i in self.current_steps(m):
                s = m.steps[i]
                if s["do"] == "find":
                    out.append((s["at"][0], s["at"][1], s.get("tile", "item_card"), s["item"]))
        return out

    def tracked(self) -> Mission | None:
        t = self.progress.tracked
        if t and t in self.missions and self.state(self.missions[t]).status == "active":
            return self.missions[t]
        act = self.active()
        return ([a for a in act if a.optional] or act or [None])[0]

    def step_text(self, m: Mission, i: int) -> str:
        s = m.steps[i]
        if s.get("label"):
            text = s["label"]
        else:
            kind = s["do"]
            text = {
                "talk": f"Talk to the {s.get('npc', '')}",
                "go_to": f"Go to {self._name(s.get('location', ''))}",
                "read": f"Visit {self._name(s.get('location', ''))}",
                "find": f"Find the {s.get('name', 'item')}",
                "answer": f"Answer the {s.get('npc', '')}'s question",
                "ride": f"Get to {self._name(s.get('location', ''))}",
                "collect": "Visit the places on the list",
            }[kind]
        if s["do"] == "collect":
            got = len(self.state(m).collected.get(str(i), []))
            text += f" ({got}/{s.get('need', len(s['targets']))})"
        return text

    def tracker(self) -> str | None:
        m = self.tracked()
        if not m:
            return None
        steps = self.current_steps(m)
        if not steps:
            return None
        text = self.step_text(m, steps[0])
        if len(steps) > 1:
            text = f"{len(steps)} things left"
        st = self.state(m)
        if st.timer is not None:
            secs = max(0, st.timer) // FPS
            text += f"  {secs // 60}:{secs % 60:02d}"
        return f"{m.title}: {text}"

    def targets(self) -> list[dict]:
        """What the tracked mission wants next, for the campus map's '!' pins:
        dicts with one of 'location', 'npc' or 'at'."""
        m = self.tracked()
        if not m:
            return []
        out = []
        st = self.state(m)
        for i in self.current_steps(m):
            s = m.steps[i]
            if s["do"] == "find":
                out.append({"at": s["at"]})
            elif s.get("npc"):
                out.append({"npc": s["npc"]})
            elif s.get("location"):
                out.append({"location": s["location"]})
            elif s["do"] == "collect":
                done = st.collected.get(str(i), [])
                out += [{"location": t["location"]} for t in s["targets"] if t["location"] not in done]
        return out
