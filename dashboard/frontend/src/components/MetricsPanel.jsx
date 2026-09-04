import React from "react";

// Dashboard_PRD.md sections 23-26: Performance Metrics
const CARDS = [
  { key: "probability_of_detection", label: "P(Detection)", pct: true },
  { key: "false_alarm_probability", label: "P(False Alarm)", pct: true },
  { key: "interception_ratio", label: "Interception Ratio", pct: true },
  { key: "average_intercept_time_ms", label: "Avg Intercept Time", unit: "ms" },
  { key: "prediction_accuracy", label: "Prediction Accuracy", pct: true },
  { key: "average_reward", label: "Average Reward" },
  { key: "total_observations", label: "Observations" },
  { key: "total_hits", label: "Hits" },
];

export default function MetricsPanel({ metrics }) {
  return (
    <>
      <h2>Performance Metrics</h2>
      <div className="metric-grid">
        {CARDS.map((c) => {
          const raw = metrics?.[c.key];
          let display = "—";
          if (raw !== null && raw !== undefined) {
            display = c.pct ? `${Math.round(raw * 100)}%` : `${raw}${c.unit ? ` ${c.unit}` : ""}`;
          }
          return (
            <div className="metric-card" key={c.key}>
              <div className="metric-label">{c.label}</div>
              <div className="metric-value">{display}</div>
            </div>
          );
        })}
      </div>
    </>
  );
}
