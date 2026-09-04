"""
Pydantic models implementing the contracts defined in:
- RFD_Sim_PRD.md  (RF Event Contract, sections 15-19)
- Dashboard_PRD.md (AI Input/Decision/Feedback contracts, sections 9-16)

These models are the single source of truth for request/response
shapes crossing the Dashboard's API boundary. AI Engine internal
model design is intentionally out of scope.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.config import MIN_BAND, MAX_BAND


# ---------------------------------------------------------------------------
# RF Event Contract (RFD_Sim_PRD.md section 17 / 19)
# Sent by the RF Simulator to POST /api/v1/rf/observation
# ---------------------------------------------------------------------------
class ReceiverInfo(BaseModel):
    band_id: int = Field(..., ge=MIN_BAND, le=MAX_BAND)
    dwell_ms: int = Field(..., gt=0)


class ObservationInfo(BaseModel):
    detected: bool
    signal_strength_db: Optional[float] = None


class OutcomeInfo(BaseModel):
    """Ground truth. The Dashboard MUST strip this before forwarding
    anything to the AI Engine (RFD_Sim_PRD.md section 16-17,
    Dashboard_PRD.md section 8)."""
    ground_truth_active: bool
    emitter_ids: List[str] = Field(default_factory=list)


class RFObservationRequest(BaseModel):
    simulation_id: str
    timestamp: int = Field(..., ge=0)
    receiver: ReceiverInfo
    observation: ObservationInfo
    outcome: OutcomeInfo


class NextDecisionResponse(BaseModel):
    """What the Dashboard returns synchronously to the RF Simulator's
    POST /api/v1/rf/observation call (RFD_Sim_PRD.md section 19)."""
    next_band: int = Field(..., ge=MIN_BAND, le=MAX_BAND)
    dwell_ms: int = Field(..., gt=0)


# ---------------------------------------------------------------------------
# AI-safe observation (what the Dashboard is allowed to forward)
# ---------------------------------------------------------------------------
class AISafeObservation(BaseModel):
    """Same as RFObservationRequest MINUS the outcome/ground-truth
    fields. This is what actually goes into the AI observation window."""
    simulation_id: str
    timestamp: int
    receiver: ReceiverInfo
    observation: ObservationInfo
    # populated only for *past* slots once the outcome is known,
    # i.e. hit/miss feedback the AI Engine has already received.
    result: Optional[str] = None  # "hit" | "miss" | None


# ---------------------------------------------------------------------------
# AI Decision contract (Dashboard_PRD.md section 10)
# ---------------------------------------------------------------------------
class DecisionSource(str, Enum):
    AI_ENGINE = "ai_engine"
    FALLBACK = "fallback"


class AIDecision(BaseModel):
    next_band: int = Field(..., ge=MIN_BAND, le=MAX_BAND)
    dwell_ms: int = Field(..., gt=0)
    prediction: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)

    @field_validator("prediction", "confidence")
    @classmethod
    def _finite(cls, v: float) -> float:
        if v != v:  # NaN check
            raise ValueError("value must be a finite number")
        return v


class AgentPredictRequest(BaseModel):
    """Dashboard -> AI Engine (Dashboard_PRD.md section 32)."""
    simulation_id: str
    observation_window: List[AISafeObservation]
    current_receiver: ReceiverInfo
    previous_decisions: List[AIDecision] = Field(default_factory=list)
    previous_results: List[str] = Field(default_factory=list)  # "hit"/"miss"
    previous_rewards: List[float] = Field(default_factory=list)


class AgentFeedbackRequest(BaseModel):
    """Dashboard -> AI Engine, sent AFTER the outcome is known
    (Dashboard_PRD.md section 16)."""
    simulation_id: str
    timestamp: int
    selected_band: int
    prediction: float
    confidence: float
    detection_result: bool
    signal_strength_db: Optional[float] = None
    result: str  # "hit" | "miss"
    intercept_time_ms: Optional[float] = None
    reward: float
    decision_source: DecisionSource


# ---------------------------------------------------------------------------
# Fallback dataset record schema (Dashboard_PRD.md section 12)
# ---------------------------------------------------------------------------
class FallbackRecord(BaseModel):
    timestamp: int
    selected_band: int
    prediction: float
    confidence: float
    actual: bool
    result: str
    intercept_time_ms: float
    reward: float


# ---------------------------------------------------------------------------
# Dashboard state model (Dashboard_PRD.md section 33)
# ---------------------------------------------------------------------------
class BandView(BaseModel):
    band_id: int
    predicted_activity: float = 0.0
    is_current_receiver: bool = False


class MetricsSnapshot(BaseModel):
    probability_of_detection: float = 0.0
    false_alarm_probability: float = 0.0
    average_intercept_time_ms: Optional[float] = None
    average_intercept_time_error_ms: Optional[float] = None
    interception_ratio: float = 0.0
    prediction_accuracy: float = 0.0
    average_reward: float = 0.0
    total_observations: int = 0
    total_hits: int = 0
    total_misses: int = 0


class BaselineComparisonRow(BaseModel):
    metric: str
    sequential: Optional[float] = None
    ai: Optional[float] = None


class DashboardStateModel(BaseModel):
    simulation_id: Optional[str] = None
    simulation_status: str = "idle"  # idle | running | paused | stopped
    scenario: Optional[str] = None
    current_timestamp: Optional[int] = None
    current_receiver_band: Optional[int] = None
    current_dwell_ms: Optional[int] = None
    latest_observation: Optional[ObservationInfo] = None
    latest_prediction: Optional[float] = None
    latest_confidence: Optional[float] = None
    latest_decision: Optional[NextDecisionResponse] = None
    latest_result: Optional[str] = None  # "hit" | "miss"
    bands: List[BandView] = Field(default_factory=list)
    recent_history: List[dict] = Field(default_factory=list)
    metrics: MetricsSnapshot = Field(default_factory=MetricsSnapshot)
    baseline_comparison: List[BaselineComparisonRow] = Field(default_factory=list)
    ai_status: str = "unknown"  # LIVE | FALLBACK | ERROR
    decision_source: Optional[DecisionSource] = None


# ---------------------------------------------------------------------------
# Simple structured error envelope (Dashboard_PRD.md section 34)
# ---------------------------------------------------------------------------
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
