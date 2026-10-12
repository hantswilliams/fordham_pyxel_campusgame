"""Scene stack. The top scene receives input; overlay scenes (dialogue,
menus) are drawn on top of the scene beneath them, which stays frozen."""

from __future__ import annotations

from typing import TYPE_CHECKING

from game.gfx import display

if TYPE_CHECKING:
    from game.app import App


class Scene:
    overlay = False  # True: draw the scene underneath first

    def __init__(self, app: App):
        self.app = app

    @property
    def input(self):
        return self.app.input

    def on_enter(self) -> None: ...
    def on_exit(self) -> None: ...
    def update(self) -> None: ...
    def draw(self) -> None: ...


class SceneManager:
    def __init__(self):
        self.stack: list[Scene] = []

    @property
    def top(self) -> Scene | None:
        return self.stack[-1] if self.stack else None

    def push(self, scene: Scene) -> None:
        self.stack.append(scene)
        scene.on_enter()

    def pop(self) -> Scene:
        scene = self.stack.pop()
        scene.on_exit()
        return scene

    def replace(self, scene: Scene) -> None:
        while self.stack:
            self.pop()
        self.push(scene)

    def update(self) -> None:
        if self.top:
            self.top.update()

    def draw(self) -> None:
        # Find the lowest scene that must be drawn (first non-overlay from top).
        start = len(self.stack) - 1
        while start > 0 and self.stack[start].overlay:
            start -= 1
        for i, scene in enumerate(self.stack[start:]):
            if i:
                display.layer()     # an overlay covers the text beneath it too
            scene.draw()
