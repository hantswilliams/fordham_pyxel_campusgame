"""Opening sequence data and timing (decisions/0016 Part 2). Pure Python.

The intro is a list of *beats*: a scene ("train", "station", "street") and
a caption that stays up for a number of frames. Consecutive beats with the
same scene form one continuous animation, so the drawing code only needs
`scene_progress` (0..1 through the current scene).
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

SCENES = {"train", "station", "street"}
CHARS_PER_FRAME = 2


@dataclass
class Beat:
    scene: str
    frames: int
    caption: str


@dataclass
class IntroData:
    beats: list[Beat]
    controls_title: str = "HOW TO PLAY"
    controls_rows: list[tuple[str, str]] = field(default_factory=list)
    tip: str = ""
    prompt: str = ""


def parse_intro(d: dict) -> IntroData:
    beats = []
    for i, b in enumerate(d.get("beats", [])):
        if b.get("scene") not in SCENES:
            raise ValueError(f"intro beat {i}: unknown scene {b.get('scene')!r}")
        if int(b.get("frames", 0)) <= 0 or not b.get("caption"):
            raise ValueError(f"intro beat {i}: needs positive 'frames' and a 'caption'")
        beats.append(Beat(b["scene"], int(b["frames"]), b["caption"]))
    if not beats:
        raise ValueError("intro needs at least one beat")
    c = d.get("controls", {})
    return IntroData(
        beats=beats,
        controls_title=c.get("title", "HOW TO PLAY"),
        controls_rows=[tuple(r) for r in c.get("rows", [])],
        tip=c.get("tip", ""),
        prompt=c.get("prompt", ""),
    )


def load_intro(path: Path) -> IntroData:
    return parse_intro(json.loads(path.read_text(encoding="utf-8")))


class IntroTimeline:
    def __init__(self, beats: list[Beat]):
        self.beats = beats
        self.index = 0
        self.t = 0  # frames into the current beat
        self.forced_reveal = False
        self.done = False

    @property
    def beat(self) -> Beat:
        return self.beats[min(self.index, len(self.beats) - 1)]

    def _scene_span(self) -> tuple[int, int]:
        """(first, last+1) beat indexes of the scene the current beat is in."""
        scene = self.beat.scene
        start = self.index
        while start > 0 and self.beats[start - 1].scene == scene:
            start -= 1
        end = self.index + 1
        while end < len(self.beats) and self.beats[end].scene == scene:
            end += 1
        return start, end

    @property
    def scene_progress(self) -> float:
        if self.done:
            return 1.0
        start, end = self._scene_span()
        before = sum(b.frames for b in self.beats[start:self.index])
        total = sum(b.frames for b in self.beats[start:end])
        return min(1.0, (before + self.t) / total)

    @property
    def scene_length(self) -> int:
        start, end = self._scene_span()
        return sum(b.frames for b in self.beats[start:end])

    @property
    def scene_frame(self) -> int:
        """Frames since the current scene started (for looping animation)."""
        start, _ = self._scene_span()
        return sum(b.frames for b in self.beats[start:self.index]) + self.t

    @property
    def revealed_chars(self) -> int:
        n = len(self.beat.caption)
        return n if self.forced_reveal else min(n, self.t * CHARS_PER_FRAME)

    @property
    def caption_complete(self) -> bool:
        return self.revealed_chars >= len(self.beat.caption)

    def tick(self) -> None:
        if self.done:
            return
        self.t += 1
        if self.t >= self.beat.frames:
            self._next()

    def confirm(self) -> None:
        """Z: finish typing the caption, or move on to the next beat."""
        if self.done:
            return
        if not self.caption_complete:
            self.forced_reveal = True
        else:
            self._next()

    def skip(self) -> None:
        self.done = True

    def _next(self) -> None:
        self.index += 1
        self.t = 0
        self.forced_reveal = False
        if self.index >= len(self.beats):
            self.done = True
            self.index = len(self.beats) - 1


def scroll_offset(progress: float, length: int, speed: float, brake: float = 0.35) -> float:
    """Distance travelled by scenery at `progress` through a scene of `length`
    frames, moving at `speed` px/frame and braking to a stop over the final
    `brake` fraction. Used for the view out of the train window."""
    t = progress * length
    a = (1 - brake) * length
    if t <= a:
        return speed * t
    s = t - a
    span = length - a
    return speed * a + speed * (s - s * s / (2 * span))
