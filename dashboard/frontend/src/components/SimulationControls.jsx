import React, { useState } from "react";
import { api } from "../api/client.js";

const SCENARIOS = ["mixed", "periodic", "frequency_agile", "bursty"];

// Dashboard_PRD.md section 28: Simulation Controls - Start, Pause,
// Resume, Reset, Scenario selection, Simulation speed.
export default function SimulationControls({ state }) {
  const [scenario, setScenario] = useState("mixed");
  const [busy, setBusy] = useState(false);
  const status = state?.simulation_status ?? "idle";

  async function run(action) {
    setBusy(true);
    try {
      await action();
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="controls-row">
      <select value={scenario} onChange={(e) => setScenario(e.target.value)} disabled={busy}>
        {SCENARIOS.map((s) => (
          <option key={s} value={s}>
            {s.replace("_", " ")}
          </option>
        ))}
      </select>
      <button
        className="primary"
        disabled={busy || status === "running"}
        onClick={() => run(() => api.startSimulation(scenario))}
      >
        Start
      </button>
      <button
        disabled={busy || status !== "running"}
        onClick={() => run(() => api.pauseSimulation())}
      >
        Pause
      </button>
      <button
        disabled={busy || status !== "paused"}
        onClick={() => run(() => api.resumeSimulation())}
      >
        Resume
      </button>
      <button disabled={busy} onClick={() => run(() => api.resetSimulation())}>
        Reset
      </button>
    </div>
  );
}
