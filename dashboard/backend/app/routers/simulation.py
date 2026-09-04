"""
Simulation control endpoints (Dashboard_PRD.md sections 28 & 31).

The Dashboard does not own RF environment state (RFD_Sim_PRD.md /
Dashboard_PRD.md section 28: "The RF Simulator remains the owner of
RF environment state") — these endpoints simply proxy control
commands to the RF Simulator's own HTTP API and reset local Dashboard
state where appropriate.
"""
from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.config import RF_SIMULATOR_URL
from app.fallback import fallback_engine
from app.state import state

router = APIRouter(prefix="/api/v1/simulation", tags=["simulation"])
logger = logging.getLogger("dashboard.simulation")


async def _proxy(path: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(f"{RF_SIMULATOR_URL}{path}")
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as exc:
        logger.warning("RF Simulator unreachable at %s: %s", path, exc)
        raise HTTPException(
            status_code=502,
            detail=f"RF Simulator unavailable ({path}): {exc}",
        ) from exc


@router.post("/start")
async def start(scenario: str = Query(default="mixed"), seed: int | None = None) -> dict:
    result = await _proxy("/api/v1/simulation/start")
    simulation_id = result.get("simulation_id", state.next_run_id())
    state.start_new_run(simulation_id, scenario)
    fallback_engine.reset(scenario)
    return {"status": "started", "simulation_id": simulation_id, "scenario": scenario}


@router.post("/pause")
async def pause() -> dict:
    result = await _proxy("/api/v1/simulation/pause")
    state.simulation_status = "paused"
    return result or {"status": "paused"}


@router.post("/resume")
async def resume() -> dict:
    result = await _proxy("/api/v1/simulation/resume")
    state.simulation_status = "running"
    return result or {"status": "running"}


@router.post("/reset")
async def reset() -> dict:
    result = await _proxy("/api/v1/simulation/reset")
    scenario = state.scenario
    state.reset()
    fallback_engine.reset()
    return result or {"status": "reset", "scenario": scenario}
