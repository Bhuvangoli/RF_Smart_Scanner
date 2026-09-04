"""
State Manager (Dashboard_PRD.md section 5.2).

Holds everything in memory for the single active simulation supported
by Prototype V0.1: current state, observation history, prediction
history, hit/miss results, performance metrics, AI Engine state.

This module intentionally has no HTTP or business-rule logic; it is
a thin, thread-safe-ish store (single asyncio event loop, no real
concurrency hazards for this prototype).
"""
from __future__ import annotations

import itertools
from collections import deque
from typing import Deque, Dict, List, Optional

from app.config import HISTORY_DISPLAY_LIMIT, OBSERVATION_WINDOW
from app.models import (
    AIDecision,
    DecisionSource,
    NextDecisionResponse,
    RFObservationRequest,
)

_run_id_counter = itertools.count(1)


class HistoryRecord(dict):
    """A single completed simulation slot: observation + decision +
    outcome + result, all in one flat dict for easy JSON/history use."""


class DashboardState:
    def __init__(self) -> None:
        self.reset()

    # -- lifecycle -----------------------------------------------------
    def reset(self) -> None:
        self.simulation_id: Optional[str] = None
        self.scenario: Optional[str] = None
        self.simulation_status: str = "idle"

        self.current_timestamp: Optional[int] = None
        self.current_receiver_band: Optional[int] = None
        self.current_dwell_ms: Optional[int] = None

        self.latest_observation: Optional[RFObservationRequest] = None
        self.latest_decision: Optional[NextDecisionResponse] = None
        self.latest_ai_decision: Optional[AIDecision] = None
        self.latest_result: Optional[str] = None
        self.decision_source: Optional[DecisionSource] = None

        self.ai_status: str = "unknown"

        # bounded history buffers
        self.history: Deque[HistoryRecord] = deque(maxlen=HISTORY_DISPLAY_LIMIT)
        self.observation_window: Deque[HistoryRecord] = deque(maxlen=OBSERVATION_WINDOW)

        # per-band predicted activity (for the RF Spectrum panel)
        self.predicted_activity: Dict[int, float] = {b: 0.0 for b in range(1, 9)}

        # per-emitter "first seen active since last hit" timestamps,
        # used for the approximate intercept-time calculation
        self._emitter_first_seen: Dict[str, int] = {}

        # running counters for metrics (kept alongside history for O(1) updates)
        self.total_observations = 0
        self.true_positive = 0  # hit AND ground_truth_active
        self.false_negative = 0  # miss AND ground_truth_active
        self.false_positive = 0  # detected AND NOT ground_truth_active
        self.true_negative = 0  # not detected AND NOT ground_truth_active
        self.intercept_times_ms: List[float] = []
        self.rewards: List[float] = []
        self.prediction_correct = 0
        self.prediction_total = 0

        self.fallback_cursor: Dict[str, int] = {}

    def start_new_run(self, simulation_id: str, scenario: Optional[str]) -> None:
        self.reset()
        self.simulation_id = simulation_id
        self.scenario = scenario
        self.simulation_status = "running"

    # -- helpers ---------------------------------------------------------
    def next_run_id(self) -> str:
        return f"run-{next(_run_id_counter):04d}"


# Single process-wide instance (Prototype V0.1 supports one active
# simulation only, per Dashboard_PRD.md section 4).
state = DashboardState()
