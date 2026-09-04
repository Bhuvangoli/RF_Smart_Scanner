import React from "react";

// Dashboard_PRD.md section 27: Baseline Comparison - AI scheduling
// vs sequential scanning (1->2->3->...->8->repeat).
export default function BaselineComparison({ rows }) {
  return (
    <>
      <h2>AI vs Sequential Baseline</h2>
      {(!rows || rows.length === 0) ? (
        <p className="muted">Not enough data yet to compare against the baseline.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Metric</th>
              <th>Sequential</th>
              <th>AI</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.metric}>
                <td>{r.metric}</td>
                <td>{r.sequential ?? "—"}</td>
                <td>{r.ai ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <p className="muted" style={{ marginTop: 8, fontSize: 11 }}>
        Approximate: computed only over slots where the sequential
        schedule would have chosen the same band the receiver actually
        scanned (see backend/app/metrics.py).
      </p>
    </>
  );
}
