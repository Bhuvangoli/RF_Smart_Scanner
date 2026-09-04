from __future__ import annotations

from .emitters import Emitter


class RFEnvironment:
    def __init__(self, emitters: list[Emitter]):
        self.emitters = emitters
        self.bands = {band: {"active": False, "emitters": []} for band in range(1, 9)}

    def reset(self) -> None:
        for emitter in self.emitters:
            emitter.reset()
        self.bands = {band: {"active": False, "emitters": []} for band in range(1, 9)}

    def generate(self, slot: int) -> dict:
        self.bands = {band: {"active": False, "emitters": []} for band in range(1, 9)}

        for emitter in self.emitters:
            active, band = emitter.state_at(slot)
            if active:
                self.bands[band]["active"] = True
                self.bands[band]["emitters"].append(emitter.config.emitter_id)

        return self.bands

    def get_state(self) -> dict:
        return self.bands
