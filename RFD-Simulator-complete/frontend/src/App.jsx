import React, { useEffect, useState } from "react";

const API = "/api/v1";

async function call(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export default function App() {
  const [state, setState] = useState(null);
  const [scenario, setScenario] = useState("mixed");
  const [seed, setSeed] = useState(12345);
  const [speed, setSpeed] = useState(1);
  const [error, setError] = useState("");

  const refresh = async () => {
    try {
      setState(await call("/simulation/state"));
      setError("");
    } catch (e) {
      setError("Backend connection unavailable");
    }
  };

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 500);
    return () => clearInterval(id);
  }, []);

  const action = async (name) => {
    try {
      await call(`/simulation/${name}`, { method: "POST" });
      await refresh();
    } catch (e) {
      setError(e.message);
    }
  };

  const configure = async () => {
    try {
      await call("/simulation/configure", {
        method: "POST",
        body: JSON.stringify({ scenario, seed: Number(seed), speed }),
      });
      await refresh();
    } catch (e) {
      setError(e.message);
    }
  };

  const bands = state?.bands || {};

  return (
    <main className="page">
      <h1>RF Environment Simulator</h1>
      <p className="sub">Prototype V0.1 · 8 logical bands · 1 receiver</p>

      <section className="panel controls">
        <div>
          <button onClick={() => action("start")}>START</button>
          <button onClick={() => action("pause")}>PAUSE</button>
          <button onClick={() => action("reset")}>RESET</button>
        </div>

        <label>
          Scenario
          <select value={scenario} onChange={e => setScenario(e.target.value)}>
            <option value="mixed">Mixed</option>
            <option value="periodic">Periodic</option>
            <option value="frequency_agile">Frequency Agile</option>
          </select>
        </label>

        <label>
          Speed
          <select value={speed} onChange={e => setSpeed(Number(e.target.value))}>
            <option value={1}>1x</option>
            <option value={2}>2x</option>
            <option value={5}>5x</option>
            <option value={10}>10x</option>
          </select>
        </label>

        <label>
          Seed
          <input value={seed} onChange={e => setSeed(e.target.value)} />
        </label>

        <button onClick={configure}>APPLY CONFIG</button>
      </section>

      {error && <div className="error">{error}</div>}
      {state?.connection && <div className="warning">{state.connection}</div>}

      <section className="grid">
        <div className="panel">
          <h2>Simulation</h2>
          <p>Status: <b>{state?.status || "loading"}</b></p>
          <p>Simulation ID: {state?.simulation_id}</p>
          <p>Scenario: {state?.scenario}</p>
          <p>Seed: {state?.seed}</p>
          <p>Logical time: {state?.timestamp} ms</p>
        </div>

        <div className="panel">
          <h2>Current Receiver</h2>
          <p>Current Band: <b>{state?.receiver?.band_id}</b></p>
          <p>Dwell: {state?.receiver?.dwell_ms} ms</p>
        </div>
      </section>

      <section className="panel">
        <h2>Environment View</h2>
        <div className="bands">
          {Array.from({ length: 8 }, (_, i) => i + 1).map(band => {
            const b = bands[band] || { active: false, emitters: [] };
            return (
              <div className={`band ${b.active ? "active" : ""}`} key={band}>
                <strong>Band {band}</strong>
                <span>{b.active ? "ACTIVE" : "INACTIVE"}</span>
                <small>{b.emitters?.length ? b.emitters.join(", ") : "No emitter"}</small>
              </div>
            );
          })}
        </div>
      </section>

      <section className="panel">
        <h2>Latest Observation</h2>
        <pre>{JSON.stringify(state?.last_observation, null, 2)}</pre>
      </section>
    </main>
  );
}
