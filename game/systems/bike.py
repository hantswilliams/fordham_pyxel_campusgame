"""The bike (decisions/0030): borrow one from the rack outside Walsh
Library, then hop on and off anywhere with X to cross campus twice as fast,
Pokemon-style. Pure logic, no Pyxel."""

from game import config
from game.systems import controls

from .progress import Progress

TAKE_LINES = [controls.fmt(s) for s in (
    "A bike rack outside Walsh Library. You borrow a bike!",
    "Press {back} to hop on or off. Riding is twice as fast as walking.",
    "Bring it back to any bike rack when you're done.",
)]
RETURN_LINES = ["You park the bike back in the rack."]
NO_BIKE_LINES = ["A bike rack outside Walsh Library. Bikes are free to borrow."]


class Bike:
    """Whether you've borrowed a bike and are riding it, kept in Progress so
    it's saved (decisions/0031)."""

    def __init__(self, progress: Progress | None = None):
        self.progress = progress or Progress()

    @property
    def have(self) -> bool:          # borrowed from a rack
        return self.progress.has_bike

    @have.setter
    def have(self, value: bool) -> None:
        self.progress.has_bike = value

    @property
    def riding(self) -> bool:        # on it right now
        return self.progress.riding

    @riding.setter
    def riding(self, value: bool) -> None:
        self.progress.riding = value

    @property
    def speed(self) -> int:
        return config.BIKE_SPEED if self.riding else config.WALK_SPEED

    def use_rack(self) -> list[str]:
        """Pressing Z at a rack: borrow a bike (and get on), or give it back."""
        if self.have:
            self.have = self.riding = False
            return RETURN_LINES
        self.have = self.riding = True
        return TAKE_LINES

    def toggle(self) -> str | None:
        """X in the overworld: hop on or off. None if there's no bike."""
        if not self.have:
            return None
        self.riding = not self.riding
        return "ON THE BIKE" if self.riding else "WALKING"
