# SIH RF Simulator + Dashboard

## Project Structure

```text
SIH/
├── dashboard/
│   ├── backend/
│   └── frontend/
└── RFD-Simulator-complete/
    ├── .venv/
    ├── backend/
    └── frontend/
```

## First-Time Setup

### 1. RF Simulator Backend

```powershell
cd D:\SIH\RFD-Simulator-complete
& "D:\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
```

### 2. Dashboard Backend

Open a new terminal:

```powershell
cd D:\SIH\dashboard\backend
& "D:\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Dashboard Frontend

```powershell
cd D:\SIH\dashboard\frontend
npm install
```

## Running the Project

Run the following four services in separate terminals.

### Terminal 1 — RF Simulator

```powershell
cd D:\SIH\RFD-Simulator-complete
.\.venv\Scripts\Activate.ps1
cd backend
$env:DASHBOARD_URL="http://127.0.0.1:8000"
uvicorn main:app --reload --port 8001
```

Runs on:

`http://127.0.0.1:8001`

### Terminal 2 — Dashboard Backend

```powershell
cd D:\SIH\dashboard\backend
.\.venv\Scripts\Activate.ps1
$env:RF_SIMULATOR_URL="http://127.0.0.1:8001"
$env:AI_ENGINE_URL="http://127.0.0.1:8002"
uvicorn app.main:app --reload --port 8000
```

Runs on:

`http://127.0.0.1:8000`

### Terminal 3 — AI Stub

```powershell
cd D:\SIH\dashboard\backend
.\.venv\Scripts\Activate.ps1
uvicorn dev_stubs.mock_ai_engine:app --port 8002
```

Runs on:

`http://127.0.0.1:8002`

### Terminal 4 — Dashboard Frontend

```powershell
cd D:\SIH\dashboard\frontend
npm run dev
```

Runs on:

`http://localhost:5173`

## Open the Dashboard

Open the following URL in your browser:

`http://localhost:5173`

Then select a simulation scenario and click **START**.

## Service Ports

| Component | Port |
|---|---:|
| Dashboard Frontend | 5173 |
| Dashboard Backend | 8000 |
| RF Simulator | 8001 |
| AI Stub | 8002 |

## Important

Use **Python 3.12.10** from:

```text
D:\python.exe
```

Do not use:

```text
D:\Scripts\python.exe
```

because that Python installation is broken and produces the `No pyvenv.cfg file` error.
