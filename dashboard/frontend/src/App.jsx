import React from "react";
import { api } from "./api/client.js";
import { usePolling } from "./hooks/usePolling.js";

import SystemStatus from "./components/SystemStatus.jsx";
import RFSpectrum from "./components/RFSpectrum.jsx";
import ReceiverPanel from "./components/ReceiverPanel.jsx";
import PredictionPanel from "./components/PredictionPanel.jsx";
import TimeSeriesPanel from "./components/TimeSeriesPanel.jsx";
import ObservationTable from "./components/ObservationTable.jsx";
import MetricsPanel from "./components/MetricsPanel.jsx";
import BaselineComparison from "./components/BaselineComparison.jsx";
import SimulationControls from "./components/SimulationControls.jsx";

// Dashboard_PRD.md section 18: the primary dashboard contains six
// areas - System Status, RF Spectrum, Receiver Panel, AI Prediction
// Panel, Time-Series Panel, Observation Table - plus performance
// metrics (section 23) and the baseline comparison (section 27).
export default function App() {
  const { data: state, error } = usePolling(api.getDashboardState, 1000);
  const { data: history } = usePolling(() => api.getHistory(200), 2000);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>SIH26055 · RF Receiver Scheduler Dashboard</h1>
          <div className="subtitle">
            RF Environment Simulator → Dashboard → AI Engine (closed loop)
          </div>
        </div>
        <SimulationControls state={state} />
      </header>

      {error && (
        <div className="error-banner">
          Dashboard connection unavailable: {error.message}
        </div>
      )}

      <div className="grid">
        <div className="col-12 panel">
          <SystemStatus state={state} />
        </div>

        <div className="col-4 panel">
          <RFSpectrum state={state} />
        </div>

        <div className="col-4 panel">
          <ReceiverPanel state={state} />
        </div>

        <div className="col-4 panel">
          <PredictionPanel state={state} />
        </div>

        <div className="col-8 panel">
          <TimeSeriesPanel history={history} />
        </div>

        <div className="col-4 panel">
          <MetricsPanel metrics={state?.metrics} />
        </div>

        <div className="col-8 panel">
          <ObservationTable history={history} />
        </div>

        <div className="col-4 panel">
          <BaselineComparison rows={state?.baseline_comparison} />
        </div>
      </div>
    </div>
  );
}
