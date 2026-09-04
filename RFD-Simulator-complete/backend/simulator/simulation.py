from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Any

import httpx

from .clock import SimulationClock
from .emitters import build_emitters
from .environment import RFEnvironment
from .receiver import Receiver
from .scenarios import DEFAULT_SCENARIO, DEFAULT_SEED
from .storage import LocalStorage


class SimulationEngine:
    def __init__(self, dashboard_url: str = ""):
        self.dashboard_url = dashboard_url
        self.clock = SimulationClock(100)
        self.scenario = DEFAULT_SCENARIO
        self.seed = DEFAULT_SEED
        self.simulation_id = "demo-001"
        self.status = "idle"
        self.speed = 1
        self.environment = RFEnvironment(build_emitters(self.scenario, self.seed))
        self.receiver = Receiver(self.seed)
        self.storage = LocalStorage()
        self.recent_observations: list[dict[str, Any]] = []
        self.last_ground_truth: dict[int, dict[str, Any]] = self.environment.get_state()
        self.last_observation: dict[str, Any] | None = None
        self.pending_decision: dict[str, Any] | None = None
        self._task: asyncio.Task | None = None
        self._decision_event = asyncio.Event()
        self._lock = asyncio.Lock()
        self.connection_message = ""

    def start_background_tasks(self) -> None:
        # The actual task is started by POST /start; this keeps startup cheap.
        return None

    def _rebuild(self) -> None:
        self.clock.reset()
        self.environment = RFEnvironment(build_emitters(self.scenario, self.seed))
        self.receiver = Receiver(self.seed)
        self.recent_observations = []
        self.last_ground_truth = self.environment.get_state()
        self.last_observation = None
        self.pending_decision = None
        self.connection_message = ""
        self._decision_event.clear()

    async def start(self) -> dict:
        async with self._lock:
            if self.status == "running":
                return {"status": "started", "simulation_id": self.simulation_id}

            if self.status == "idle":
                self.simulation_id = f"run-{uuid.uuid4().hex[:8]}"
                self._rebuild()

            self.status = "running"
            if self._task is None or self._task.done():
                self._task = asyncio.create_task(self._run_loop())

            return {"status": "started", "simulation_id": self.simulation_id}

    async def pause(self) -> dict:
        self.status = "paused"
        return {"status": "paused"}

    async def resume(self) -> dict:
        if self.status == "idle":
            return await self.start()
        self.status = "running"
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run_loop())
        return {"status": "resumed"}

    async def reset(self) -> dict:
        self.status = "idle"
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = None
        self.simulation_id = f"run-{uuid.uuid4().hex[:8]}"
        self._rebuild()
        return {"status": "reset", "simulation_id": self.simulation_id}

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def state(self) -> dict:
        return {
            "status": self.status,
            "simulation_id": self.simulation_id,
            "timestamp": self.clock.get_time(),
            "scenario": self.scenario,
            "seed": self.seed,
            "speed": self.speed,
            "receiver": {
                "band_id": self.receiver.band_id,
                "dwell_ms": self.receiver.dwell_ms,
            },
            "bands": self.last_ground_truth,
            "last_observation": self.last_observation,
            "connection": self.connection_message,
        }

    async def apply_decision(self, decision: dict[str, Any]) -> dict:
        if decision["simulation_id"] != self.simulation_id:
            raise ValueError(f"simulation_id does not match current run: expected {self.simulation_id}, got {decision['simulation_id']}")
        self.pending_decision = decision
        self._decision_event.set()
        return {"status": "decision_received"}

    def record_observation(self, observation: dict[str, Any]) -> None:
        self.last_observation = observation
        self.recent_observations.append(observation)
        self.recent_observations = self.recent_observations[-50:]

    async def _send_observation(self, event: dict[str, Any]) -> dict | None:
        if not self.dashboard_url:
            return None

        url = f"{self.dashboard_url}/api/v1/rf/observation"
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                response = await client.post(url, json=event)
                response.raise_for_status()
                self.connection_message = ""
                data = response.json()
                if isinstance(data, dict) and "next_band" in data:
                    return data
                return None
        except (httpx.HTTPError, ValueError) as exc:
            self.connection_message = "Dashboard connection unavailable"
            print(f"[DEBUG _send_observation EXCEPTION]: {exc!r}", flush=True)
            return None

    async def _wait_for_decision(self, event: dict[str, Any]) -> dict:
        # With no configured dashboard, use the PRD baseline sequential schedule.
        if not self.dashboard_url:
            return {
                "simulation_id": self.simulation_id,
                "next_band": self.receiver.baseline_next_band(),
                "dwell_ms": 100,
            }

        self._decision_event.clear()
        self.pending_decision = None

        # Dashboard failure: wait and retry sending observation, or apply pending_decision if provided.
        while self.status == "running":
            if self.pending_decision is not None:
                d = self.pending_decision
                self.pending_decision = None
                return d

            dashboard_decision = await self._send_observation(event)
            if dashboard_decision is not None:
                return dashboard_decision

            self._decision_event.clear()
            try:
                await asyncio.wait_for(self._decision_event.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

        return {
            "simulation_id": self.simulation_id,
            "next_band": self.receiver.band_id,
            "dwell_ms": self.receiver.dwell_ms,
        }

    async def _run_loop(self) -> None:
        try:
            while self.status == "running":
                slot = self.clock.get_time() // self.clock.slot_ms
                self.last_ground_truth = self.environment.generate(slot)

                selected_band = self.receiver.band_id
                active = self.last_ground_truth[selected_band]
                observation = self.receiver.observe(self.last_ground_truth)

                event = {
                    "simulation_id": self.simulation_id,
                    "timestamp": self.clock.get_time(),
                    "receiver": {
                        "band_id": selected_band,
                        "dwell_ms": self.receiver.dwell_ms,
                    },
                    "observation": observation,
                    "outcome": {
                        "ground_truth_active": bool(active["emitters"]),
                        "emitter_ids": list(active["emitters"]),
                    },
                }

                self.record_observation(event)
                self.storage.append_observation(self.simulation_id, event)

                dashboard_decision = await self._send_observation(event)
                decision = dashboard_decision or await self._wait_for_decision(event)

                if self.status != "running":
                    break

                self.receiver.apply_decision(
                    decision["next_band"],
                    decision["dwell_ms"],
                )
                self.clock.advance(decision["dwell_ms"])

                # Logical time advances immediately; speed controls presentation/demo rate.
                await asyncio.sleep(max(0.01, 0.1 / max(1, self.speed)))
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self.status = "waiting"
            self.connection_message = str(exc)

    def configure(self, scenario: str, seed: int, speed: int) -> None:
        if scenario not in {"mixed", "periodic", "frequency_agile"}:
            raise ValueError("Unsupported scenario")
        if speed not in {1, 2, 5, 10}:
            raise ValueError("Unsupported speed")
        self.scenario = scenario
        self.seed = seed
        self.speed = speed
        self._rebuild()
