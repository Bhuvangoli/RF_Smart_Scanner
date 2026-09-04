"""
Scheduler Adapter (Dashboard_PRD.md section 5.3).

Talks to the AI Engine, normalizes its response into the internal
`AIDecision` format, detects timeouts/errors/invalid responses, and
falls back to the deterministic Fallback Engine when required
(sections 10-11). The AI Engine's own model/implementation is out of
scope here — this module only depends on the HTTP contract.
"""
from __future__ import annotations

import logging
from typing import Optional, Tuple

import httpx
from pydantic import ValidationError

from app.config import AI_ENGINE_URL, AI_FEEDBACK_PATH, AI_PREDICT_PATH, AI_REQUEST_TIMEOUT_S
from app.fallback import fallback_engine
from app.models import (
    AgentFeedbackRequest,
    AgentPredictRequest,
    AIDecision,
    DecisionSource,
)

logger = logging.getLogger("dashboard.scheduler_adapter")


class SchedulerAdapter:
    def __init__(self) -> None:
        self.ai_status = "unknown"  # LIVE | FALLBACK | ERROR

    async def request_decision(
        self,
        request: AgentPredictRequest,
        scenario: Optional[str],
        current_timestamp: int,
    ) -> Tuple[AIDecision, DecisionSource]:
        """Returns (decision, source). Never raises — on any failure
        this method transparently returns a fallback decision so the
        Dashboard is never blocked by AI Engine problems
        (Dashboard_PRD.md section 11: "shall not block the
        demonstration because of an AI failure")."""
        try:
            async with httpx.AsyncClient(timeout=AI_REQUEST_TIMEOUT_S) as client:
                resp = await client.post(
                    f"{AI_ENGINE_URL}{AI_PREDICT_PATH}",
                    json=request.model_dump(),
                )
            resp.raise_for_status()
            payload = resp.json()
            decision = AIDecision(**payload)
            self.ai_status = "LIVE"
            return decision, DecisionSource.AI_ENGINE

        except httpx.TimeoutException:
            logger.warning("AI Engine request timed out; using fallback.")
            self.ai_status = "FALLBACK"
        except (httpx.HTTPError, ValidationError, ValueError, KeyError) as exc:
            logger.warning("AI Engine request failed (%s); using fallback.", exc)
            self.ai_status = "ERROR"
        except Exception as exc:  # noqa: BLE001 - last-resort safety net
            logger.exception("Unexpected AI Engine failure: %s", exc)
            self.ai_status = "ERROR"

        record = fallback_engine.next_decision(scenario, current_timestamp)
        decision = AIDecision(
            next_band=record.selected_band,
            dwell_ms=100,
            prediction=record.prediction,
            confidence=record.confidence,
        )
        return decision, DecisionSource.FALLBACK

    async def send_feedback(self, feedback: AgentFeedbackRequest) -> bool:
        """Best-effort feedback delivery. Failure here must never break
        the main loop (Dashboard_PRD.md section 16)."""
        try:
            async with httpx.AsyncClient(timeout=AI_REQUEST_TIMEOUT_S) as client:
                resp = await client.post(
                    f"{AI_ENGINE_URL}{AI_FEEDBACK_PATH}",
                    json=feedback.model_dump(),
                )
            return resp.status_code < 300
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to deliver feedback to AI Engine: %s", exc)
            return False


scheduler_adapter = SchedulerAdapter()
