from __future__ import annotations

import random


class Receiver:
    def __init__(self, seed: int, detection_probability: float = 0.90):
        self.rng = random.Random(seed)
        self.band_id = 1
        self.dwell_ms = 100
        self.detection_probability = detection_probability

    def reset(self) -> None:
        self.band_id = 1
        self.dwell_ms = 100

    def apply_decision(self, next_band: int, dwell_ms: int) -> None:
        if not 1 <= next_band <= 8:
            raise ValueError("next_band must be between 1 and 8")
        if dwell_ms <= 0:
            raise ValueError("dwell_ms must be positive")
        self.band_id = next_band
        self.dwell_ms = dwell_ms

    def baseline_next_band(self) -> int:
        return 1 if self.band_id >= 8 else self.band_id + 1

    def observe(self, ground_truth: dict) -> dict:
        band = ground_truth[self.band_id]
        active_emitters = band["emitters"]

        if not active_emitters:
            return {"detected": False, "signal_strength_db": None}

        # Use a nominal signal strength for the strongest active emitter.
        # Small controlled variation is seeded.
        nominal = -60.0
        signal = nominal + self.rng.uniform(-3.0, 3.0)

        detected = self.rng.random() < self.detection_probability
        return {
            "detected": detected,
            "signal_strength_db": round(signal, 1) if detected else None,
        }
