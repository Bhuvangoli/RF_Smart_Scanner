import React from "react";

// Dashboard_PRD.md section 22: Observation Table - Time, Band,
// Prediction, Actual, Result, Confidence, latest 20 observations.
export default function ObservationTable({ history }) {
  const records = (history?.records ?? []).slice(-20).reverse();

  return (
    <>
      <h2>Recent Observations</h2>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Band</th>
            <th>Prediction</th>
            <th>Actual</th>
            <th>Result</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {records.length === 0 ? (
            <tr>
              <td colSpan={6} className="muted">
                No observations yet.
              </td>
            </tr>
          ) : (
            records.map((r, idx) => (
              <tr key={`${r.timestamp}-${idx}`}>
                <td>{r.timestamp}</td>
                <td>{r.receiver_band}</td>
                <td>{r.prediction !== undefined ? `${Math.round(r.prediction * 100)}%` : "—"}</td>
                <td>{r.ground_truth_active ? "ACTIVE" : "inactive"}</td>
                <td>
                  <span className={`pill ${r.result}`}>{(r.result ?? "—").toUpperCase()}</span>
                </td>
                <td>{r.confidence !== undefined ? `${Math.round(r.confidence * 100)}%` : "—"}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </>
  );
}
