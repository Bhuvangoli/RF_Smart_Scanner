"""
OPTIONAL DEV STUB - not part of the Dashboard PRD.

A minimal stand-in for the RF Environment Simulator so you can run
and click around the Dashboard before the real RFD_Sim service is
wired in. Implements just enough of RFD_Sim_PRD.md section 18 to
satisfy the Dashboard's simulation control proxy, and pushes a fake
observation to the Dashboard once a second while "running".

Run with:
    uvicorn dev_stubs.mock_rf_simulator:app --port 8001
"""
from __future__ import annotations

import asyncio
import random

import httpx
from fastapi import FastAPI

app = FastAPI(title="Mock RF Simulator (dev stub)")

DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://127.0.0.1:8000")
STATE = {"status": "idle", "simulation_id": "demo-001", "timestamp": 0}
_task: asyncio.Task | None = None


async def _loop():
    rng = random.Random(12345)
    band = 1
    while STATE["status"] == "running":
        STATE["timestamp"] += 1
        band = rng.choice(range(1, 9))
        active = rng.random() < 0.4
        detected = active and rng.random() < 0.8
        payload = {
            "simulation_id": STATE["simulation_id"],
            "timestamp": STATE["timestamp"],
            "receiver": {"band_id": band, "dwell_ms": 100},
            "observation": {
                "detected": detected,
                "signal_strength_db": round(rng.uniform(-90, -50), 1),
            },
            "outcome": {
                "ground_truth_active": active,
                "emitter_ids": ["E0" + str(rng.randint(1, 4))] if active else [],
            },
        }
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.post(f"{DASHBOARD_URL}/api/v1/rf/observation", json=payload)
        except Exception:
            pass
        await asyncio.sleep(0.5)


@app.post("/api/v1/simulation/start")
async def start():
    global _task
    STATE["status"] = "running"
    if _task is None or _task.done():
        _task = asyncio.create_task(_loop())
    return {"status": "started", "simulation_id": STATE["simulation_id"]}


@app.post("/api/v1/simulation/pause")
async def pause():
    STATE["status"] = "paused"
    return {"status": "paused"}


@app.post("/api/v1/simulation/resume")
async def resume():
    global _task
    STATE["status"] = "running"
    if _task is None or _task.done():
        _task = asyncio.create_task(_loop())
    return {"status": "running"}


@app.post("/api/v1/simulation/reset")
async def reset():
    STATE["status"] = "idle"
    STATE["timestamp"] = 0
    return {"status": "reset"}


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "component": "rf-simulator-mock"}
