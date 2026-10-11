"""The bike (decisions/0030): borrow one from the rack outside Walsh
Library, then hop on and off anywhere with X to cross campus twice as fast,
Pokemon-style. Pure logic, no Pyxel."""

from game import config

TAKE_LINES = [
    "A bike rack outside Walsh Library. You borrow a bike!",
    "Press X to hop on or off. Riding is twice as fast as walking.",
    "Bring it back to any bike rack when you're done.",
]
RETURN_LINES = ["You park the bike back in the rack."]
NO_BIKE_LINES = ["A bike rack outside Walsh Library. Bikes are free to borrow."]


class Bike:
    def __init__(self):
        self.have = False    # borrowed from a rack
        self.riding = False  # on it right now

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
