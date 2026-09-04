"""
Fallback Engine (Dashboard_PRD.md sections 12-14, 35).

Loads pre-generated, deterministic per-scenario JSON Lines datasets
(see scripts/generate_fallback.py) and serves them in order. When a
dataset is exhausted the sequence restarts from the beginning while
the fallback timestamp is rebased to the current simulation
timestamp (section 35), so the simulation never stalls.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from app.config import FALLBACK_DIR
from app.models import FallbackRecord

SCENARIOS = ["periodic", "bursty", "frequency_agile", "mixed"]


class FallbackEngine:
    def __init__(self, directory: Path = FALLBACK_DIR) -> None:
        self.directory = directory
        self._datasets: Dict[str, List[FallbackRecord]] = {}
        self._cursors: Dict[str, int] = {}
        self._load_all()

    def _load_all(self) -> None:
        for scenario in SCENARIOS:
            path = self.directory / f"{scenario}.jsonl"
            records: List[FallbackRecord] = []
            if path.exists():
                with path.open() as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            records.append(FallbackRecord(**json.loads(line)))
            self._datasets[scenario] = records
            self._cursors[scenario] = 0

    def _resolve_scenario(self, scenario: str | None) -> str:
        if scenario and scenario.lower().replace(" ", "_").replace("-", "_") in self._datasets:
            return scenario.lower().replace(" ", "_").replace("-", "_")
        return "mixed"

    def next_decision(self, scenario: str | None, current_timestamp: int) -> FallbackRecord:
        """Returns the next deterministic fallback record. Rebases its
        timestamp to `current_timestamp` so it always looks current to
        the caller, per Dashboard_PRD.md section 35."""
        key = self._resolve_scenario(scenario)
        records = self._datasets.get(key) or []
        if not records:
            # absolute last resort: synthesize a safe, inert decision
            return FallbackRecord(
                timestamp=current_timestamp,
                selected_band=((current_timestamp % 8) + 1),
                prediction=0.5,
                confidence=0.3,
                actual=False,
                result="miss",
                intercept_time_ms=0.0,
                reward=0.0,
            )

        cursor = self._cursors[key]
        if cursor >= len(records):
            cursor = 0  # restart, retaining deterministic order (section 35)

        record = records[cursor]
        self._cursors[key] = cursor + 1

        return record.model_copy(update={"timestamp": current_timestamp})

    def reset(self, scenario: str | None = None) -> None:
        if scenario is None:
            for key in self._cursors:
                self._cursors[key] = 0
        else:
            key = self._resolve_scenario(scenario)
            self._cursors[key] = 0


fallback_engine = FallbackEngine()
