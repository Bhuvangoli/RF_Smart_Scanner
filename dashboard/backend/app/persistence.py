"""
Local persistence (Dashboard_PRD.md section 36).

Prototype V0.1 does not require a database. Active state lives in
memory (app/state.py); this module optionally appends each completed
slot to a per-run JSON Lines file under data/runs/, and can write a
final summary when a run ends.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from app.config import PERSIST_RUNS, RUNS_DIR


def _run_path(simulation_id: str) -> Path:
    return RUNS_DIR / f"{simulation_id}.jsonl"


def append_slot(simulation_id: Optional[str], record: dict) -> None:
    if not PERSIST_RUNS or not simulation_id:
        return
    path = _run_path(simulation_id)
    with path.open("a") as f:
        f.write(json.dumps(record, default=str) + "\n")


def write_summary(simulation_id: Optional[str], summary: dict) -> None:
    if not PERSIST_RUNS or not simulation_id:
        return
    path = RUNS_DIR / f"{simulation_id}.summary.json"
    with path.open("w") as f:
        json.dump(summary, f, indent=2, default=str)
