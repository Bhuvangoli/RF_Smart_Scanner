class SimulationClock:
    """Logical clock. Correctness does not depend on wall-clock time."""

    def __init__(self, slot_ms: int = 100):
        self.slot_ms = slot_ms
        self.timestamp = 0

    def advance(self, dwell_ms: int | None = None) -> None:
        self.timestamp += dwell_ms if dwell_ms is not None else self.slot_ms

    def reset(self) -> None:
        self.timestamp = 0

    def get_time(self) -> int:
        return self.timestamp
