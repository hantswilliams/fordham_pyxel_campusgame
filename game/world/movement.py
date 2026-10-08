"""Pokemon-style grid movement: input picks the next tile, then the sprite
slides there over a few frames. Pure logic, no Pyxel."""

from typing import Callable

from .directions import Direction


class GridMover:
    def __init__(self, x: int, y: int, tile: int, speed: int,
                 facing: Direction = Direction.DOWN):
        self.tile_x = x
        self.tile_y = y
        self.tile = tile
        self.speed = speed
        self.facing = facing
        self.moving = False
        self.progress = 0  # pixels travelled toward the next tile
        self.steps_taken = 0  # used to alternate walking legs

    @property
    def pixel_x(self) -> int:
        off = self.progress * self.facing.dx if self.moving else 0
        return self.tile_x * self.tile + off

    @property
    def pixel_y(self) -> int:
        off = self.progress * self.facing.dy if self.moving else 0
        return self.tile_y * self.tile + off

    @property
    def front_tile(self) -> tuple[int, int]:
        return self.tile_x + self.facing.dx, self.tile_y + self.facing.dy

    def try_move(self, direction: Direction,
                 is_blocked: Callable[[int, int], bool]) -> bool:
        """Face `direction` and start walking if the target tile is free.
        Returns True if a step started. Ignored while already moving."""
        if self.moving:
            return False
        self.facing = direction
        tx, ty = self.front_tile
        if is_blocked(tx, ty):
            return False
        self.moving = True
        self.progress = 0
        return True

    def update(self) -> bool:
        """Advance the current step. Returns True on the frame a step ends."""
        if not self.moving:
            return False
        self.progress += self.speed
        if self.progress >= self.tile:
            self.tile_x += self.facing.dx
            self.tile_y += self.facing.dy
            self.moving = False
            self.progress = 0
            self.steps_taken += 1
            return True
        return False

    @property
    def anim_frame(self) -> int:
        """0 = standing, 1 = left foot, 2 = right foot."""
        if self.moving and self.progress < self.tile // 2:
            return 1 + (self.steps_taken % 2)
        return 0
