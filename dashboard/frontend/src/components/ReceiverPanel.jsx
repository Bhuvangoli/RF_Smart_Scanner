import React from "react";

// Dashboard_PRD.md section 19: Receiver Panel
export default function ReceiverPanel({ state }) {
  const result = state?.latest_result;
  const observation = state?.latest_observation;
  const signalStrength = observation?.signal_strength_db;

  return (
    <>
      <h2>Receiver</h2>

      <div className="status-row" style={{ flexDirection: "column", gap: 10 }}>
        <div className="status-item">
          <span className="label">Current Band</span>
          <span className="value">
            {state?.current_receiver_band ?? "—"}
          </span>
        </div>

        <div className="status-item">
          <span className="label">Dwell</span>
          <span className="value">
            {state?.current_dwell_ms != null
              ? `${state.current_dwell_ms} ms`
              : "—"}
          </span>
        </div>

        <div className="status-item">
          <span className="label">Signal</span>
          <span className="value">
            {signalStrength != null
              ? `${signalStrength.toFixed(1)} dB`
              : "—"}
          </span>
        </div>

        <div className="status-item">
          <span className="label">Detected</span>
          <span className="value">
            {observation
              ? observation.detected
                ? "Yes"
                : "No"
              : "—"}
          </span>
        </div>

        <div className="status-item">
          <span className="label">Last Result</span>
          {result ? (
            <span className={`pill ${result}`}>
              {result.toUpperCase()}
            </span>
          ) : (
            <span className="value">—</span>
          )}
        </div>

        <div className="status-item">
          <span className="label">Next Band</span>
          <span className="value">
            {state?.latest_decision?.next_band ?? "—"}
          </span>
        </div>
      </div>
    </>
  );
}