import React from "react";

// Dashboard_PRD.md section 18, Area 2: RF Spectrum - all eight bands,
// each showing band id, predicted activity, and current receiver state.
export default function RFSpectrum({ state }) {
  const bands = state?.bands ?? Array.from({ length: 8 }, (_, i) => ({
    band_id: i + 1,
    predicted_activity: 0,
    is_current_receiver: false,
  }));

  return (
    <>
      <h2>RF Spectrum</h2>
      <div className="band-list">
        {bands.map((b) => (
          <div key={b.band_id} className={`band-row ${b.is_current_receiver ? "current" : ""}`}>
            <span className="band-label">Band {b.band_id}</span>
            <div className="bar-track">
              <div
                className="bar-fill"
                style={{ width: `${Math.round(b.predicted_activity * 100)}%` }}
              />
            </div>
            <span className="muted">{Math.round(b.predicted_activity * 100)}%</span>
          </div>
        ))}
      </div>
    </>
  );
}
