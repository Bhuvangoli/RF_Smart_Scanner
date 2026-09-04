import React from "react";

// Dashboard_PRD.md section 20: AI Prediction Panel
export default function PredictionPanel({ state }) {
  const pct = (v) => (v === null || v === undefined ? "—" : `${Math.round(v * 100)}%`);
  return (
    <>
      <h2>AI Prediction</h2>
      <div className="status-row" style={{ flexDirection: "column", gap: 10 }}>
        <div className="status-item">
          <span className="label">Next Band</span>
          <span className="value">{state?.latest_decision?.next_band ?? "—"}</span>
        </div>
        <div className="status-item">
          <span className="label">Predicted Activity</span>
          <span className="value">{pct(state?.latest_prediction)}</span>
        </div>
        <div className="status-item">
          <span className="label">Confidence</span>
          <span className="value">{pct(state?.latest_confidence)}</span>
        </div>
        <div className="status-item">
          <span className="label">Source</span>
          <span className={`pill ${state?.decision_source ?? ""}`}>
            {(state?.decision_source ?? "—").toString().toUpperCase()}
          </span>
        </div>
      </div>
    </>
  );
}
