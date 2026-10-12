"""Everything the game remembers between sessions (decisions/0031): where
you are, the bike, places you've visited, missions, stamps, badges and
unlocks. Pure data plus JSON save/load; no Pyxel here, so it's easy to test.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

SAVE_VERSION = 1
BADGES = ["academics", "wellness", "community", "career", "dining"]  # D-0003


@dataclass
class MissionState:
    status: str = "available"          # available | active | done
    done_steps: list[int] = field(default_factory=list)
    collected: dict[str, list[str]] = field(default_factory=dict)  # step index -> targets done
    timer: int | None = None           # frames left on a timed step

    def to_dict(self) -> dict:
        return {"status": self.status, "done_steps": self.done_steps,
                "collected": self.collected, "timer": self.timer}

    @classmethod
    def from_dict(cls, d: dict) -> "MissionState":
        return cls(status=d.get("status", "available"),
                   done_steps=list(d.get("done_steps", [])),
                   collected={k: list(v) for k, v in d.get("collected", {}).items()},
                   timer=d.get("timer"))


@dataclass
class Progress:
    started: bool = False               # past the gate at least once
    position: tuple[int, int] | None = None
    facing: str = "up"
    gate_open: bool = False
    has_bike: bool = False
    riding: bool = False
    visited: set[str] = field(default_factory=set)        # location ids whose card you opened
    missions: dict[str, MissionState] = field(default_factory=dict)
    stamps: list[str] = field(default_factory=list)       # Ram Passport, in the order earned
    badges: set[str] = field(default_factory=set)
    unlocks: set[str] = field(default_factory=set)        # e.g. "maroon_bike"
    tracked: str | None = None                            # mission shown in the tracker
    show_tracker: bool = False                            # pinned on (M in the TAB menu); off = clean screen

    def mission(self, mission_id: str) -> MissionState:
        return self.missions.setdefault(mission_id, MissionState())

    # --- JSON -------------------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "version": SAVE_VERSION,
            "started": self.started,
            "position": list(self.position) if self.position else None,
            "facing": self.facing,
            "gate_open": self.gate_open,
            "has_bike": self.has_bike,
            "riding": self.riding,
            "visited": sorted(self.visited),
            "missions": {k: v.to_dict() for k, v in sorted(self.missions.items())},
            "stamps": self.stamps,
            "badges": sorted(self.badges),
            "unlocks": sorted(self.unlocks),
            "tracked": self.tracked,
            "pin_tracker": self.show_tracker,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Progress":
        pos = d.get("position")
        return cls(
            started=bool(d.get("started", False)),
            position=tuple(pos) if pos else None,
            facing=d.get("facing", "up"),
            gate_open=bool(d.get("gate_open", False)),
            has_bike=bool(d.get("has_bike", False)),
            riding=bool(d.get("riding", False)),
            visited=set(d.get("visited", [])),
            missions={k: MissionState.from_dict(v) for k, v in d.get("missions", {}).items()},
            stamps=list(d.get("stamps", [])),
            badges=set(d.get("badges", [])) & set(BADGES),
            unlocks=set(d.get("unlocks", [])),
            tracked=d.get("tracked"),
            show_tracker=bool(d.get("pin_tracker", False)),
        )


SAVE_KEY = "fordham_campus_quest_save"   # the browser local-storage key (decisions/0034)


def browser_storage():
    """The browser's localStorage when the game runs in a web page (Pyodide,
    decisions/0034); None on the desktop."""
    import sys
    if sys.platform != "emscripten":
        return None
    try:
        from js import localStorage  # type: ignore[import-not-found]
        return localStorage
    except Exception:
        return None


class SaveFile:
    """Reads and writes Progress as JSON: to a file on the desktop, or to the
    browser's local storage in the web build (`storage`, anything with
    getItem / setItem / removeItem). With neither (`path=None`), everything
    stays in memory (tests, screenshots), so they never touch a real save."""

    def __init__(self, path: Path | None, storage=None):
        self.path = path
        self.storage = storage

    def _read(self) -> str | None:
        if self.storage is not None:
            try:
                return self.storage.getItem(SAVE_KEY)
            except Exception:
                return None
        if self.path and self.path.exists():
            try:
                return self.path.read_text()
            except OSError:
                return None
        return None

    def exists(self) -> bool:
        return self._read() is not None

    def load(self) -> Progress:
        text = self._read()
        if text is None:
            return Progress()
        try:
            return Progress.from_dict(json.loads(text))
        except (ValueError, TypeError, AttributeError):
            return Progress()          # a damaged save starts fresh rather than crashing

    def save(self, progress: Progress) -> None:
        text = json.dumps(progress.to_dict(), indent=1)
        if self.storage is not None:
            try:
                self.storage.setItem(SAVE_KEY, text)
            except Exception:
                pass                   # e.g. storage full or blocked: never crash over a save
            return
        if not self.path:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(text)
            tmp.replace(self.path)
        except OSError:
            pass                       # never crash the game over a save

    def delete(self) -> None:
        if self.storage is not None:
            try:
                self.storage.removeItem(SAVE_KEY)
            except Exception:
                pass
            return
        if self.path and self.path.exists():
            try:
                self.path.unlink()
            except OSError:
                pass
