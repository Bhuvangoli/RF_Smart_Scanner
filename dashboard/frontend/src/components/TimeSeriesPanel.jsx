import React, { useMemo, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";

// Dashboard_PRD.md section 21: Time-Series Panel - activity history of
// the RF bands, selectable per band, showing observed vs predicted
// activity, receiver selections and hit/miss events.
export default function TimeSeriesPanel({ history }) {
  const [band, setBand] = useState("all");
  const records = history?.records ?? [];

  const chartData = useMemo(() => {
    return records
      .filter((r) => band === "all" || r.receiver_band === Number(band))
      .map((r) => ({
        timestamp: r.timestamp,
        observed: r.ground_truth_active ? 1 : 0,
        predicted: r.prediction ?? 0,
        hit: r.result === "hit" ? 1 : 0,
      }));
  }, [records, band]);

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 style={{ margin: 0 }}>Time Series</h2>
        <select value={band} onChange={(e) => setBand(e.target.value)}>
          <option value="all">All bands</option>
          {Array.from({ length: 8 }, (_, i) => i + 1).map((b) => (
            <option key={b} value={b}>
              Band {b}
            </option>
          ))}
        </select>
      </div>
      <div style={{ height: 260, marginTop: 12 }}>
        {chartData.length === 0 ? (
          <p className="muted">No history yet — start a simulation to see live data.</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#232c38" />
              <XAxis dataKey="timestamp" stroke="#8b98a5" fontSize={11} />
              <YAxis domain={[0, 1]} stroke="#8b98a5" fontSize={11} />
              <Tooltip
                contentStyle={{ background: "#121820", border: "1px solid #232c38" }}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Line type="stepAfter" dataKey="observed" name="Ground truth active" stroke="#f85149" dot={false} />
              <Line type="monotone" dataKey="predicted" name="Predicted activity" stroke="#4fd1c5" dot={false} />
              <Line type="stepAfter" dataKey="hit" name="Hit" stroke="#3fb950" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </>
  );
}
