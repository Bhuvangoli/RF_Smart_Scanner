"""
Dashboard-facing read endpoints (Dashboard_PRD.md section 31, 33).
Consumed by the Vite/React frontend.
"""
from __future__ import annotations

from fastapi import APIRouter

from app import metrics
from app.models import (
    BandView,
    BaselineComparisonRow,
    DashboardStateModel,
    DecisionSource,
    NextDecisionResponse,
    ObservationInfo,
)
from app.state import state

router = APIRouter(prefix="/api/v1", tags=["dashboard"])


@router.get("/dashboard/state", response_model=DashboardStateModel)
async def get_dashboard_state() -> DashboardStateModel:
    bands = [
        BandView(
            band_id=b,
            predicted_activity=round(state.predicted_activity.get(b, 0.0), 4),
            is_current_receiver=(b == state.current_receiver_band),
        )
        for b in range(1, 9)
    ]

    latest_observation = None
    if state.latest_observation is not None:
        latest_observation = ObservationInfo(
            detected=state.latest_observation.observation.detected,
            signal_strength_db=state.latest_observation.observation.signal_strength_db,
        )

    baseline = metrics.compute_sequential_baseline(list(state.history))
    metrics_snapshot = metrics.snapshot(state)

    comparison_rows = []
    if baseline is not None:
        comparison_rows = [
            BaselineComparisonRow(
                metric="Detection / Interception Ratio",
                sequential=baseline["interception_ratio"],
                ai=metrics_snapshot.interception_ratio,
            ),
            BaselineComparisonRow(
                metric="Average Reward",
                sequential=baseline["average_reward"],
                ai=metrics_snapshot.average_reward,
            ),
        ]

    return DashboardStateModel(
        simulation_id=state.simulation_id,
        simulation_status=state.simulation_status,
        scenario=state.scenario,
        current_timestamp=state.current_timestamp,
        current_receiver_band=state.current_receiver_band,
        current_dwell_ms=state.current_dwell_ms,
        latest_observation=latest_observation,
        latest_prediction=(
            state.latest_ai_decision.prediction if state.latest_ai_decision else None
        ),
        latest_confidence=(
            state.latest_ai_decision.confidence if state.latest_ai_decision else None
        ),
        latest_decision=(
            NextDecisionResponse(
                next_band=state.latest_decision.next_band,
                dwell_ms=state.latest_decision.dwell_ms,
            )
            if state.latest_decision
            else None
        ),
        latest_result=state.latest_result,
        bands=bands,
        recent_history=list(state.history)[-20:],
        metrics=metrics_snapshot,
        baseline_comparison=comparison_rows,
        ai_status=state.ai_status,
        decision_source=state.decision_source,
    )


@router.get("/history")
async def get_history(limit: int = 200) -> dict:
    """Returns recent observation and scheduler history
    (Dashboard_PRD.md section 31 - History)."""
    records = list(state.history)[-limit:]
    return {"count": len(records), "records": records}


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "component": "dashboard"}
