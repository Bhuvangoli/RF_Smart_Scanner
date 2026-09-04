from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EmitterConfig:
    emitter_id: str
    behaviour: str
    bands: list[int]
    period_slots: int = 20
    active_slots: int = 5
    initial_phase: int = 0
    jitter: int = 0
    signal_strength_db: float = -60.0
    signal_variation_db: float = 3.0
    burst_probability: float = 0.25
    burst_duration: int = 3
    inter_burst_interval: int = 5
    timing_variation: int = 0
    transition_matrix: dict[int, dict[int, float]] | None = None
    duty_cycle: float = 0.10


class Emitter:
    def __init__(self, config: EmitterConfig, rng: random.Random):
        self.config = config
        self.rng = rng
        self.current_band = config.bands[0]
        self._burst_remaining = 0
        self._next_burst_slot = 0

    def reset(self) -> None:
        self.current_band = self.config.bands[0]
        self._burst_remaining = 0
        self._next_burst_slot = 0

    def _periodic_active(self, slot: int) -> bool:
        phase = self.config.initial_phase
        # Jitter is controlled and seeded; it shifts the effective phase.
        if self.config.jitter:
            jitter = self.rng.randint(-self.config.jitter, self.config.jitter)
        else:
            jitter = 0
        position = (slot + phase + jitter) % self.config.period_slots
        return position < self.config.active_slots

    def _bursty_active(self, slot: int) -> bool:
        if self._burst_remaining > 0:
            self._burst_remaining -= 1
            return True

        if slot < self._next_burst_slot:
            return False

        if self.rng.random() < self.config.burst_probability:
            variation = (
                self.rng.randint(-self.config.timing_variation, self.config.timing_variation)
                if self.config.timing_variation
                else 0
            )
            self._burst_remaining = max(1, self.config.burst_duration + variation) - 1
            self._next_burst_slot = slot + max(0, self.config.inter_burst_interval)
            return True

        return False

    def _frequency_agile_band(self) -> int:
        matrix = self.config.transition_matrix or {}
        row = matrix.get(self.current_band, {})
        if not row:
            return self.current_band
        next_bands = list(row)
        weights = list(row.values())
        self.current_band = self.rng.choices(next_bands, weights=weights, k=1)[0]
        return self.current_band

    def state_at(self, slot: int) -> tuple[bool, int]:
        behaviour = self.config.behaviour

        if behaviour == "periodic":
            return self._periodic_active(slot), self.current_band

        if behaviour == "bursty":
            return self._bursty_active(slot), self.current_band

        if behaviour == "frequency_agile":
            if slot > 0:
                self._frequency_agile_band()
            # Frequency-agile emitters are active on their current band.
            return True, self.current_band

        if behaviour == "intermittent":
            return self.rng.random() < self.config.duty_cycle, self.current_band

        raise ValueError(f"Unknown emitter behaviour: {behaviour}")


def default_transition_matrix() -> dict[int, dict[int, float]]:
    # Multiple non-zero transitions from every band, as required by the PRD.
    matrix: dict[int, dict[int, float]] = {}
    for band in range(1, 9):
        choices = [b for b in range(1, 9) if b != band]
        # Keep persistence plus several alternatives.
        selected = choices[:3]
        row = {band: 0.40}
        for b, p in zip(selected, (0.25, 0.20, 0.15)):
            row[b] = p
        matrix[band] = row
    return matrix


def build_emitters(scenario: str, seed: int) -> list[Emitter]:
    rng = random.Random(seed)
    matrix = default_transition_matrix()

    if scenario == "periodic":
        specs = [
            ("E01", "periodic", [3]),
            ("E02", "periodic", [5]),
            ("E03", "intermittent", [7]),
            ("E04", "periodic", [1]),
        ]
    elif scenario == "frequency_agile":
        specs = [
            ("E01", "frequency_agile", [2]),
            ("E02", "frequency_agile", [5]),
            ("E03", "intermittent", [7]),
            ("E04", "bursty", [4]),
        ]
    else:
        specs = [
            ("E01", "periodic", [3]),
            ("E02", "bursty", [5]),
            ("E03", "frequency_agile", [2]),
            ("E04", "intermittent", [7]),
        ]

    emitters = []
    for emitter_id, behaviour, bands in specs:
        config = EmitterConfig(
            emitter_id=emitter_id,
            behaviour=behaviour,
            bands=bands,
            period_slots=20,
            active_slots=5,
            initial_phase=rng.randint(0, 19),
            jitter=1,
            signal_strength_db=-60.0,
            signal_variation_db=3.0,
            burst_probability=0.35,
            burst_duration=3,
            inter_burst_interval=5,
            timing_variation=1,
            transition_matrix=matrix,
            duty_cycle=0.10,
        )
        emitters.append(Emitter(config, rng))
    return emitters
