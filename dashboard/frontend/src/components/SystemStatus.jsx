import React from "react";

// Dashboard_PRD.md section 18, Area 1: System Status
export default function SystemStatus({ state }) {
  const status = state?.simulation_status ?? "idle";
  const aiStatus = (state?.ai_status ?? "unknown").toLowerCase();
  const scenario = state?.scenario ?? "—";

  return (
    <div className="status-row">
      <div className="status-item">
        <span className="label">Simulation</span>
        <span className={`pill ${status}`}>{status.toUpperCase()}</span>
      </div>
      <div className="status-item">
        <span className="label">AI Engine</span>
        <span className={`pill ${aiStatus}`}>{(state?.ai_status ?? "UNKNOWN").toUpperCase()}</span>
      </div>
      <div className="status-item">
        <span className="label">Decision Source</span>
        <span className={`pill ${state?.decision_source ?? ""}`}>
          {(state?.decision_source ?? "—").toString().toUpperCase()}
        </span>
      </div>
      <div className="status-item">
        <span className="label">Scenario</span>
        <span className="value">{scenario}</span>
      </div>
      <div className="status-item">
        <span className="label">Simulation ID</span>
        <span className="value">{state?.simulation_id ?? "—"}</span>
      </div>
      <div className="status-item">
        <span className="label">Timestamp</span>
        <span className="value">{state?.current_timestamp ?? "—"}</span>
      </div>
    </div>
  );
}
