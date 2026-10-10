"""The gate ID check (Bert at the Webster Avenue gate). Pure Python.

choose -> tapping (short animation) -> granted -> done
"""

from dataclasses import dataclass

# Phone first: most students tap in with the ID in their phone wallet.
PHONE, CARD = 0, 1
CHOICES = ["Phone (Apple or Google Wallet)", "Fordham ID card"]
TAP_FRAMES = 45        # moving the card/phone to the reader
BEEP_AT = 30           # reader light turns green on this frame of the tap


@dataclass
class IdCheck:
    choice: int = 0
    state: str = "choose"  # choose | tapping | granted | done
    t: int = 0

    def move(self, delta: int) -> None:
        if self.state == "choose":
            self.choice = (self.choice + delta) % len(CHOICES)

    def confirm(self) -> None:
        if self.state == "choose":
            self.state, self.t = "tapping", 0
        elif self.state == "granted":
            self.state = "done"

    def tick(self) -> None:
        if self.state == "tapping":
            self.t += 1
            if self.t >= TAP_FRAMES:
                self.state, self.t = "granted", 0
        elif self.state == "granted":
            self.t += 1

    @property
    def light_green(self) -> bool:
        return self.state == "granted" or (self.state == "tapping" and self.t >= BEEP_AT)

    @property
    def tap_progress(self) -> float:
        """0..1: how far the card/phone has travelled toward the reader."""
        if self.state == "choose":
            return 0.0
        if self.state == "tapping":
            return min(1.0, self.t / BEEP_AT)
        return 1.0
