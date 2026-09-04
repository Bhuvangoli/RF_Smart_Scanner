from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LocalStorage:
    def __init__(self, root: str | Path = "data"):
        self.root = Path(root)
        self.scenarios = self.root / "scenarios"
        self.runs = self.root / "runs"
        self.fallback = self.root / "fallback"
        for directory in (self.scenarios, self.runs, self.fallback):
            directory.mkdir(parents=True, exist_ok=True)

    def append_observation(self, simulation_id: str, observation: dict[str, Any]) -> None:
        path = self.runs / f"{simulation_id}.jsonl"
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(observation) + "\n")
