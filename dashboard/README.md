# SIH26055 — Dashboard & Integration Layer

Implementation of the **Dashboard_PRD.md**: the service that sits
between the RF Environment Simulator and the AI Engine, strips ground
truth before it reaches the AI, computes hit/miss + performance
metrics, falls back to a deterministic engine when the AI is
unavailable, and drives a live Vite/React dashboard.

```
dashboard/
├── backend/                 FastAPI service (the Dashboard itself)
│   ├── app/
│   │   ├── main.py          App entrypoint, CORS, router wiring
│   │   ├── config.py        Env-driven configuration
│   │   ├── models.py        All API contract Pydantic models
│   │   ├── state.py         In-memory State Manager
│   │   ├── metrics.py       Hit/miss, Pd/Pfa, intercept time, reward, baseline
│   │   ├── fallback.py      Deterministic Fallback Engine
│   │   ├── scheduler_adapter.py   AI Engine HTTP client + fallback trigger
│   │   ├── persistence.py   Optional JSONL run logging
│   │   └── routers/
│   │       ├── rf.py            POST /api/v1/rf/observation (the core loop)
│   │       ├── dashboard.py     GET  /api/v1/dashboard/state, /history, /health
│   │       └── simulation.py    POST /api/v1/simulation/{start,pause,resume,reset}
│   ├── scripts/generate_fallback.py   Builds the 4 fallback datasets
│   ├── dev_stubs/            OPTIONAL mock RF Simulator + mock AI Engine
│   │                         (not part of the PRD — lets you run the
│   │                         Dashboard standalone before the real
│   │                         services exist)
│   ├── data/fallback/*.jsonl Pre-generated deterministic datasets
│   ├── data/runs/            Per-run JSONL logs (created at runtime)
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/                 Vite + React dashboard UI
    ├── src/
    │   ├── App.jsx            Lays out the 6 PRD dashboard areas
    │   ├── api/client.js       Backend API wrapper
    │   ├── hooks/usePolling.js Live-updates via polling
    │   └── components/
    │       ├── SystemStatus.jsx
    │       ├── RFSpectrum.jsx
    │       ├── ReceiverPanel.jsx
    │       ├── PredictionPanel.jsx
    │       ├── TimeSeriesPanel.jsx
    │       ├── ObservationTable.jsx
    │       ├── MetricsPanel.jsx
    │       ├── BaselineComparison.jsx
    │       └── SimulationControls.jsx
    ├── package.json
    └── vite.config.js
```

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # edit RF_SIMULATOR_URL / AI_ENGINE_URL as needed
python scripts/generate_fallback.py   # (already generated, re-run if you tweak it)
uvicorn app.main:app --reload --port 8000
```

Docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — it proxies `/api/*` to `localhost:8000`.

### 3. (Optional) Run standalone with the dev stubs

If the real RF Simulator / AI Engine aren't ready yet, you can
exercise the full loop with the bundled mocks:

```bash
# terminal 2
cd backend && uvicorn dev_stubs.mock_rf_simulator:app --port 8001
# terminal 3
cd backend && uvicorn dev_stubs.mock_ai_engine:app --port 8002
```

Then hit "Start" in the dashboard UI — the mock simulator pushes a
fake observation every 0.5s, the mock AI Engine returns predictions,
and you can watch the panels update live.

## API contracts implemented

| Endpoint | Direction | Contract source |
|---|---|---|
| `POST /api/v1/rf/observation` | RF Simulator → Dashboard | RFD_Sim_PRD.md §17-19 |
| `GET /api/v1/dashboard/state` | Dashboard → Frontend | Dashboard_PRD.md §33 |
| `GET /api/v1/history` | Dashboard → Frontend | Dashboard_PRD.md §31 |
| `GET /api/v1/health` | any → Dashboard | both PRDs |
| `POST /api/v1/simulation/{start,pause,resume,reset}` | Frontend → Dashboard → RF Simulator | Dashboard_PRD.md §28, RFD_Sim_PRD.md §18 |
| `POST /api/v1/agent/predict` | Dashboard → AI Engine | Dashboard_PRD.md §32 |
| `POST /api/v1/agent/feedback` | Dashboard → AI Engine | Dashboard_PRD.md §16 |

Ground truth (`outcome.ground_truth_active`, `outcome.emitter_ids`) is
read by the Dashboard for scoring but is **never** included in the
`AgentPredictRequest` sent to the AI Engine (`AISafeObservation` in
`app/models.py` is the enforced boundary).

## Notable design decisions & documented approximations

These are called out in code comments (`app/metrics.py`,
`app/fallback.py`) because the two source PRDs explicitly note the
final protocol/evaluation details may evolve once the AI Engine spec
is finalized:

- **Metrics** are computed only from what the Dashboard actually
  observes (ground truth for the *selected* band only), so
  Probability of Detection and Interception Ratio currently coincide.
- **Intercept time** is approximated per `emitter_id` using
  first-seen → hit timestamps from the event stream.
- **Baseline comparison** replays a sequential 1→8 schedule against
  the same history, but can only score slots where the sequential
  band happens to match the actually-scanned band (a structural
  limit of the privacy-preserving RF Event Contract) — this is
  labelled in the UI.
- **AI Engine internal model/design** is intentionally out of scope,
  per your instructions — only the HTTP contract is implemented.

## What's stubbed vs. real

- ✅ Real: all Dashboard business logic, contracts, fallback engine,
  metrics, persistence, and the full React UI.
- 🧪 Dev-only stubs: `dev_stubs/mock_rf_simulator.py` and
  `dev_stubs/mock_ai_engine.py` — delete this folder once the real
  RF Simulator and AI Engine are available; nothing else depends on it.
