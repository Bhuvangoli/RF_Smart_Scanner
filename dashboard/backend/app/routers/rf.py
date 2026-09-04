"""
RF Observation endpoint (RFD_Sim_PRD.md section 19, Dashboard_PRD.md
section 7 & 31).

This is the heart of the closed loop:

    RF Simulator --POST /api/v1/rf/observation--> Dashboard
    Dashboard --POST /api/v1/agent/predict--> AI Engine (or fallback)
    Dashboard --calculates hit/miss + metrics--
    Dashboard --POST /api/v1/agent/feedback--> AI Engine (best-effort)
    Dashboard --NextDecisionResponse--> RF Simulator

Implements Dashboard_PRD.md section 6, steps 1-15.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app import metrics, persistence
from app.config import MAX_BAND, MIN_BAND
from app.models import (
    AgentFeedbackRequest,
    AgentPredictRequest,
    AISafeObservation,
    DecisionSource,
    NextDecisionResponse,
    ReceiverInfo,
    RFObservationRequest,
)
from app.scheduler_adapter import scheduler_adapter
from app.state import state

router = APIRouter(prefix="/api/v1/rf", tags=["rf"])
logger = logging.getLogger("dashboard.rf")


@router.post("/observation", response_model=NextDecisionResponse)
async def receive_observation(payload: RFObservationRequest) -> NextDecisionResponse:
    # -- 2. Validate the request (structural validation is handled by
    #        Pydantic already; add the extra band-range guard here). --
    if not (MIN_BAND <= payload.receiver.band_id <= MAX_BAND):
        raise HTTPException(status_code=400, detail="receiver.band_id out of range")

    # if this is the first observation of a run, or a different
    # simulation_id shows up, (re)initialise tracking for it.
    if state.simulation_id != payload.simulation_id:
        logger.info("New simulation run detected in observation: %s (was %s)", payload.simulation_id, state.simulation_id)
        state.start_new_run(payload.simulation_id, scenario=state.scenario)

    state.current_timestamp = payload.timestamp
    state.current_receiver_band = payload.receiver.band_id
    state.current_dwell_ms = payload.receiver.dwell_ms
    state.latest_observation = payload

    # -- 3 & 4. Store the observation, add it to the time series. -----
    ai_safe_record = AISafeObservation(
        simulation_id=payload.simulation_id,
        timestamp=payload.timestamp,
        receiver=payload.receiver,
        observation=payload.observation,
        result=None,
    )
    state.observation_window.append(ai_safe_record.model_dump())

    # -- 5. Prepare the AI input (ground truth excluded). --------------
    predict_request = AgentPredictRequest(
        simulation_id=payload.simulation_id,
        observation_window=[
            AISafeObservation(**rec) for rec in state.observation_window
        ],
        current_receiver=payload.receiver,
        previous_decisions=[state.latest_ai_decision] if state.latest_ai_decision else [],
        previous_results=[state.latest_result] if state.latest_result else [],
        previous_rewards=state.rewards[-5:],
    )

    # -- 6 & 7 & 8. Call the AI Engine; fall back transparently. -------
    decision, source = await scheduler_adapter.request_decision(
        predict_request, state.scenario, payload.timestamp
    )
    state.latest_ai_decision = decision
    state.decision_source = source
    state.ai_status = scheduler_adapter.ai_status

    # -- 9. Apply the selected receiver band (this happens on the ------
    #        simulator's NEXT slot; here we just return the decision).
    next_decision = NextDecisionResponse(next_band=decision.next_band, dwell_ms=decision.dwell_ms)

    # -- 10 & 11. Compare the decision against ground truth for the ----
    #        band that was just observed and compute hit/miss.
    flat_record = {
        "timestamp": payload.timestamp,
        "receiver_band": payload.receiver.band_id,
        "dwell_ms": payload.receiver.dwell_ms,
        "detected": payload.observation.detected,
        "signal_strength_db": payload.observation.signal_strength_db,
        "ground_truth_active": payload.outcome.ground_truth_active,
        "emitter_ids": payload.outcome.emitter_ids,
        "prediction": decision.prediction,
        "confidence": decision.confidence,
        "next_band": decision.next_band,
        "decision_source": source.value,
    }
    result = metrics.record_observation(state, flat_record)
    state.latest_result = result

    # per-band predicted activity, for the RF Spectrum panel
    state.predicted_activity[payload.receiver.band_id] = decision.prediction

    # -- 12. current performance metrics are computed on demand by the
    #         /dashboard/state endpoint (metrics.snapshot); nothing to
    #         do here besides having updated the running counters above.

    # -- 13. Send feedback to the AI Engine (best-effort). --------------
    feedback = AgentFeedbackRequest(
        simulation_id=payload.simulation_id,
        timestamp=payload.timestamp,
        selected_band=payload.receiver.band_id,
        prediction=decision.prediction,
        confidence=decision.confidence,
        detection_result=payload.observation.detected,
        signal_strength_db=payload.observation.signal_strength_db,
        result=result,
        intercept_time_ms=(
            state.intercept_times_ms[-1] if state.intercept_times_ms else None
        ),
        reward=flat_record["reward"],
        decision_source=source,
    )
    await scheduler_adapter.send_feedback(feedback)

    # -- 14. Return the next receiver decision to the RF Simulator. ----
    state.latest_decision = next_decision

    # bookkeeping: append to bounded display history + persist to disk
    state.history.append(flat_record)
    persistence.append_slot(payload.simulation_id, flat_record)

    # -- 15. Update the frontend happens via polling /dashboard/state --
    return next_decision
