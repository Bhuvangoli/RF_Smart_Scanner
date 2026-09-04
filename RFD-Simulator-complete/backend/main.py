from __future__ import annotations

import asyncio
import os
import time
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from simulator.simulation import SimulationEngine

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rf_simulator")

app = FastAPI(title="RF Environment Simulator", version="0.1.0")

DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://127.0.0.1:8000").rstrip("/")
engine = SimulationEngine(dashboard_url=DASHBOARD_URL)


class Decision(BaseModel):
    simulation_id: str
    next_band: int = Field(ge=1, le=8)
    dwell_ms: int = Field(gt=0)


class Receiver(BaseModel):
    band_id: int = Field(ge=1, le=8)
    dwell_ms: int = Field(gt=0)


class Observation(BaseModel):
    detected: bool
    signal_strength_db: float | None


class Outcome(BaseModel):
    ground_truth_active: bool
    emitter_ids: list[str]


class RFObservation(BaseModel):
    simulation_id: str
    timestamp: int
    receiver: Receiver
    observation: Observation
    outcome: Outcome


class SimulationConfig(BaseModel):
    scenario: str
    seed: int
    speed: int


@app.post("/api/v1/simulation/configure")
async def configure_simulation(config: SimulationConfig):
    try:
        logger.info("Configuring simulation: scenario=%s, seed=%s, speed=%s", config.scenario, config.seed, config.speed)
        engine.configure(config.scenario, config.seed, config.speed)
        return {"status": "configured", "scenario": config.scenario, "seed": config.seed, "speed": config.speed}
    except ValueError as exc:
        logger.warning("Configure failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "component": "rf-simulator"}


@app.post("/api/v1/simulation/start")
async def start_simulation():
    result = await engine.start()
    logger.info("Simulation start requested: %s", result)
    return result


@app.post("/api/v1/simulation/pause")
async def pause_simulation():
    logger.info("Simulation pause requested")
    return await engine.pause()


@app.post("/api/v1/simulation/resume")
async def resume_simulation():
    logger.info("Simulation resume requested")
    return await engine.resume()


@app.post("/api/v1/simulation/reset")
async def reset_simulation():
    result = await engine.reset()
    logger.info("Simulation reset requested: %s", result)
    return result


@app.get("/api/v1/simulation/state")
def simulation_state():
    return engine.state()


@app.post("/api/v1/simulation/decision")
async def receive_decision(decision: Decision):
    try:
        result = await engine.apply_decision(decision.model_dump())
        logger.info("Decision applied successfully for simulation_id: %s", decision.simulation_id)
        return result
    except ValueError as exc:
        logger.warning("Decision rejected: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/v1/rf/observation")
def receive_observation(data: RFObservation):
    # This endpoint accepts the shared RF event contract. In normal operation
    # the simulator itself POSTs this event to the configured dashboard.
    engine.record_observation(data.model_dump())
    return {
        "status": "observation_received",
        "simulation_id": data.simulation_id,
    }


@app.on_event("startup")
async def startup():
    engine.start_background_tasks()


@app.on_event("shutdown")
async def shutdown():
    await engine.stop()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)

