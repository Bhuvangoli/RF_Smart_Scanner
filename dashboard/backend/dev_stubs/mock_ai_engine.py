"""
OPTIONAL DEV STUB - not part of the Dashboard PRD.

A trivial AI Engine stand-in implementing only the two endpoints the
Dashboard calls (Dashboard_PRD.md section 32). Picks a random band
and returns a plausible prediction/confidence - just enough to
exercise the Dashboard's "LIVE" path end-to-end.

Run with:
    uvicorn dev_stubs.mock_ai_engine:app --port 8002
"""
from __future__ import annotations

import random

from fastapi import FastAPI, Request

app = FastAPI(title="Mock AI Engine (dev stub)")


@app.post("/api/v1/agent/predict")
async def predict(request: Request):
    body = await request.json()
    current_band = body.get("current_receiver", {}).get("band_id", 1)
    next_band = ((current_band % 8) + 1) if random.random() < 0.5 else random.randint(1, 8)
    return {
        "next_band": next_band,
        "dwell_ms": 100,
        "prediction": round(random.uniform(0.3, 0.9), 3),
        "confidence": round(random.uniform(0.4, 0.95), 3),
    }


@app.post("/api/v1/agent/feedback")
async def feedback(request: Request):
    _ = await request.json()
    return {"status": "ack"}
