# RF Environment Simulator — Prototype V0.1

This implementation follows the supplied `RFD Sim PRD.md` as the source of truth.

## Stack
- Backend: Python + FastAPI + Uvicorn
- Frontend: Vite + React
- Data: JSON / local files
- HTTP: REST
- No database required

## Backend setup (Windows PowerShell)

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend:
`http://127.0.0.1:8000`

Swagger:
`http://127.0.0.1:8000/docs`

## Frontend setup

Open a second terminal at the project root:

```powershell
cd frontend
npm install
npm run dev
```

Frontend:
`http://127.0.0.1:5173`

## Optional dashboard integration

Set the dashboard base URL before starting the backend:

```powershell
$env:DASHBOARD_URL="http://127.0.0.1:9000"
uvicorn main:app --reload
```

The simulator posts each RF observation to:

`POST {DASHBOARD_URL}/api/v1/rf/observation`

The dashboard may return:

```json
{
  "next_band": 3,
  "dwell_ms": 100
}
```

If the dashboard is unavailable, the simulator enters a waiting/retry state and does not invent scheduler decisions.

With no dashboard URL configured, the simulator uses the required sequential baseline schedule for local demonstration.

## API endpoints

- `GET /api/v1/health`
- `POST /api/v1/simulation/start`
- `POST /api/v1/simulation/pause`
- `POST /api/v1/simulation/resume`
- `POST /api/v1/simulation/reset`
- `GET /api/v1/simulation/state`
- `POST /api/v1/simulation/decision`
- `POST /api/v1/rf/observation`

## Tests

From `backend`:

```powershell
pytest -q
```

The tests cover health, controls, decision contract, and RF observation contract.

## PRD boundaries intentionally not implemented

This prototype does NOT attempt:
- raw IQ waveform generation
- physical antenna simulation
- electromagnetic propagation
- real SDR hardware
- real RF capture
- classified emitter signatures
- real operational frequency allocations
- full radar waveform modelling
- beamforming
- spatial antenna modelling
- multi-channel receiver hardware
- complex multipath
- GPU RF simulation
- large-scale distributed simulation
- online model training inside the simulator
