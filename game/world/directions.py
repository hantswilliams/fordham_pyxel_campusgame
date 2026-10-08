from enum import Enum


class Direction(Enum):
    # value = (dx, dy, sprite row index)
    DOWN = (0, 1, 0)
    UP = (0, -1, 1)
    LEFT = (-1, 0, 2)
    RIGHT = (1, 0, 3)

    @property
    def dx(self) -> int:
        return self.value[0]

    @property
    def dy(self) -> int:
        return self.value[1]

    @property
    def sprite_index(self) -> int:
        return self.value[2]

    @property
    def opposite(self) -> "Direction":
        return {
            Direction.DOWN: Direction.UP,
            Direction.UP: Direction.DOWN,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }[self]

    @classmethod
    def from_name(cls, name: str) -> "Direction":
        return cls[name.upper()]
