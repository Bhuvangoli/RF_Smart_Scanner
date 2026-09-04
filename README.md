# Smart Scan Strategy for Electronic Warfare

## Overview

This project implements a **Smart Scan Strategy for Electronic Warfare (EW)** in situations where there is no reliable prior intelligence about hostile emitters or their operating characteristics.

Instead of scanning the entire frequency spectrum uniformly, the system uses observations collected during scanning to make informed decisions about **which frequency band should be scanned next and for how long**. The project combines an RF environment simulator, a decision/coordination backend, an AI engine interface, and a web-based dashboard to demonstrate the complete closed-loop workflow.

The system is designed as a simulation and demonstration platform. It does **not** directly control real-world RF or electronic-warfare equipment.

---

## Key Features

- **RF Environment Simulation**
  - Simulates multiple frequency bands and emitter activity.
  - Produces observations such as frequency band, signal strength, detection status, and scan/dwell information.

- **Adaptive Scan Strategy**
  - Uses the latest observations and system state to determine the next scan band.
  - Supports configurable scan behaviour and simulation speed.

- **Closed-Loop Decision Pipeline**
  - RF Simulator → Dashboard Backend → AI/Decision Engine → next scan decision → RF Simulator.
  - Continuously updates the scan state based on new observations.

- **AI Engine Integration**
  - Dashboard Backend communicates with an AI Engine through a configurable API.
  - A local mock AI engine is provided for development and demonstration when a separate AI service is unavailable.

- **Real-Time Dashboard**
  - Displays the current receiver band, dwell time, signal information, detection status, latest result, and next-band decision.
  - Provides simulation controls and monitoring information.

- **Simulation Management**
  - Start, pause, resume, reset, and inspect simulation state.
  - Maintains a unique simulation ID for each run.

- **REST APIs**
  - FastAPI-based services expose health, simulation, observation, decision, state, history, and metrics endpoints.

---

## System Architecture

```text
                    ┌─────────────────────────┐
                    │   React Dashboard       │
                    │      Port 5173          │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Dashboard Backend      │
                    │      Port 8000          │
                    └───────┬─────────┬───────┘
                            │         │
              observations │         │ AI requests
                            │         │
                            ▼         ▼
                  ┌──────────────┐  ┌──────────────┐
                  │ RF Simulator │  │  AI Engine   │
                  │   Port 8001  │  │  Port 8002   │
                  └──────────────┘  └──────────────┘
                            ▲
                            │
                            └── Next scan decision
```

### Main Components

| Component | Port | Description |
|---|---:|---|
| Dashboard Frontend | `5173` | React/Vite web interface |
| Dashboard Backend | `8000` | API, orchestration, state and decision handling |
| RF Simulator | `8001` | Simulates RF observations and scan progression |
| AI Engine / Mock AI | `8002` | Provides AI decision/prediction interface |

---

## Project Structure

The recommended project layout is:

```text
SIH/
├── RFD-Simulator-complete/
│   ├── backend/
│   │   ├── main.py
│   │   ├── ...
│   │   └── ...
│   └── ...
│
├── dashboard/
│   ├── backend/
│   │   ├── app/
│   │   ├── dev_stubs/
│   │   └── ...
│   │
│   └── frontend/
│       ├── src/
│       ├── package.json
│       └── ...
│
└── README.md
```

> The exact internal files may vary depending on the current version of the project.

---

# Requirements

## Software

Install the following before running the project:

- **Python 3.12**
- **Node.js** and **npm**
- **Git** (recommended for version control)

Python 3.12 is recommended because the backend dependencies were configured and tested around this version.

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Bhuvangoli/RF_Smart_Scanner.git
cd SIH
```

If the project is already present on your computer, simply open a terminal in the project root.

---

## 2. Create the Python Virtual Environment

From the project root:

### Windows PowerShell

```powershell
cd D:\SIH\RFD-Simulator-complete
D:\python.exe -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Verify Python:

```powershell
python --version
```

The expected version is Python 3.12.x.

---

## 3. Install Backend Dependencies

### RF Simulator

```powershell
cd D:\SIH\RFD-Simulator-complete\backend
D:\SIH\RFD-Simulator-complete\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Dashboard Backend

```powershell
cd D:\SIH\dashboard\backend
D:\SIH\RFD-Simulator-complete\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If the project uses a shared environment and the dependencies have already been installed, this step can be skipped.

---

## 4. Install Frontend Dependencies

```powershell
cd D:\SIH\dashboard\frontend
npm install
```

---

# Running the Complete System

The services should be started in separate terminals.

## Terminal 1 — RF Simulator

```powershell
cd D:\SIH\RFD-Simulator-complete\backend

$env:DASHBOARD_URL="http://127.0.0.1:8000"

D:\SIH\RFD-Simulator-complete\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001
```

The RF Simulator will be available at:

```text
http://127.0.0.1:8001
```

---

## Terminal 2 — Dashboard Backend

```powershell
cd D:\SIH\dashboard\backend

$env:RF_SIMULATOR_URL="http://127.0.0.1:8001"
$env:AI_ENGINE_URL="http://127.0.0.1:8002"

D:\SIH\RFD-Simulator-complete\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The Dashboard Backend will be available at:

```text
http://127.0.0.1:8000
```

---

## Terminal 3 — AI Engine / Mock AI

For local development and demonstration, the project includes a mock AI engine:

```powershell
cd D:\SIH\dashboard\backend

D:\SIH\RFD-Simulator-complete\.venv\Scripts\python.exe -m uvicorn dev_stubs.mock_ai_engine:app --host 127.0.0.1 --port 8002
```

The mock AI service will be available at:

```text
http://127.0.0.1:8002
```

If a separate AI Engine implementation is available, configure `AI_ENGINE_URL` to point to that service instead.

---

## Terminal 4 — Dashboard Frontend

```powershell
cd D:\SIH\dashboard\frontend
npm run dev
```

Open the dashboard in a browser:

```text
http://localhost:5173
```

---

# Startup Order

For the most reliable startup, use this order:

```text
1. AI Engine / Mock AI       → Port 8002
2. Dashboard Backend         → Port 8000
3. RF Simulator              → Port 8001
4. Dashboard Frontend        → Port 5173
```

The important requirement is that the Dashboard Backend and RF Simulator can communicate with each other, and that the configured AI Engine endpoint is available.

---

# How the System Works

The project follows a closed-loop scanning process.

```text
┌──────────────────────┐
│ RF Environment       │
│ / Emitter Scenario   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ RF Receiver Scans    │
│ Current Band         │
└──────────┬───────────┘
           │ Observation
           ▼
┌──────────────────────┐
│ Dashboard Backend    │
│ Stores Observation   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ AI / Decision Engine │
│ Select Next Band     │
└──────────┬───────────┘
           │ Decision
           ▼
┌──────────────────────┐
│ RF Simulator         │
│ Advances Scan        │
└──────────┬───────────┘
           │
           └──────────────► Next Observation
```

At every scan step:

1. The receiver scans the current frequency band.
2. The RF Simulator generates an observation.
3. The observation is sent to the Dashboard Backend.
4. The Dashboard Backend processes the observation.
5. The AI/decision component determines the next scan action.
6. The decision is returned to the RF Simulator.
7. The simulator advances to the next band/slot.
8. The process repeats.

This creates an adaptive scan loop instead of a simple static sequential scan.

---

# Configuration

The services communicate through environment variables.

## RF Simulator

```powershell
$env:DASHBOARD_URL="http://127.0.0.1:8000"
```

## Dashboard Backend

```powershell
$env:RF_SIMULATOR_URL="http://127.0.0.1:8001"
$env:AI_ENGINE_URL="http://127.0.0.1:8002"
```

For a different deployment, replace these URLs with the appropriate service addresses.

### Example

```powershell
$env:RF_SIMULATOR_URL="http://192.168.1.10:8001"
$env:AI_ENGINE_URL="http://192.168.1.11:8002"
```

Do not commit real secrets, API keys, credentials, or private configuration values to Git.

---

# API and Service Verification

After starting the services, verify that the backend processes are running.

For FastAPI services, the automatically generated API documentation is generally available at:

```text
RF Simulator:
http://127.0.0.1:8001/docs

Dashboard Backend:
http://127.0.0.1:8000/docs

AI / Mock AI:
http://127.0.0.1:8002/docs
```

The exact available endpoints depend on the current implementation.

---

# Typical Demonstration Flow

For an SIH demonstration, the following sequence can be used:

1. Start all four services.
2. Open the dashboard at `http://localhost:5173`.
3. Configure the desired simulation scenario.
4. Start the simulation.
5. Observe the receiver's current band.
6. Observe signal strength and detection status.
7. Observe the AI/decision output.
8. Observe the next selected frequency band.
9. Allow several scan slots to execute.
10. Use the dashboard metrics/history to demonstrate how the scan progresses.
11. Pause and resume the simulation if required.
12. Reset the simulation to demonstrate a fresh run.

---

# Troubleshooting

## Dashboard shows a blank page

Check the browser developer console for JavaScript errors.

Also verify that the Dashboard Backend is running:

```text
http://127.0.0.1:8000
```

Then refresh the frontend.

---

## RF Simulator cannot connect to Dashboard

Check:

```powershell
echo $env:DASHBOARD_URL
```

It should be:

```text
http://127.0.0.1:8000
```

Also make sure the Dashboard Backend is running before starting the simulation.

---

## Dashboard cannot communicate with RF Simulator

Check:

```powershell
echo $env:RF_SIMULATOR_URL
```

It should be:

```text
http://127.0.0.1:8001
```

Verify that the RF Simulator is running.

---

## AI Engine is unavailable

For local demonstration, start the mock AI service:

```powershell
cd D:\SIH\dashboard\backend
D:\SIH\RFD-Simulator-complete\.venv\Scripts\python.exe -m uvicorn dev_stubs.mock_ai_engine:app --host 127.0.0.1 --port 8002
```

Then verify:

```powershell
echo $env:AI_ENGINE_URL
```

Expected:

```text
http://127.0.0.1:8002
```

---

## Port already in use

Check which process is using a port:

```powershell
netstat -ano | findstr :8000
netstat -ano | findstr :8001
netstat -ano | findstr :8002
netstat -ano | findstr :5173
```

Stop the conflicting process or configure the service to use another port.

---

# Git and Repository Hygiene

The repository should not contain generated environments or local machine files.

Recommended entries in `.gitignore` include:

```gitignore
.venv/
__pycache__/
*.pyc
.env
.env.*
node_modules/
dist/
.vite/
*.log
.vscode/
.idea/
.DS_Store
Thumbs.db
```

Do **not** ignore project source files or dependency manifests such as:

```text
package.json
package-lock.json
requirements.txt
pyproject.toml
README.md
src/
app/
backend/
frontend/
```

---

# Technology Stack

### Frontend

- React
- Vite
- JavaScript
- HTML/CSS

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- HTTP-based service communication

### AI Layer

- AI Engine API interface
- Local mock AI engine for development/demo

### Simulation

- Python-based RF environment and receiver simulation
- Configurable scenarios and scan progression

---

# Project Objective

The primary objective is to demonstrate how an intelligent scan strategy can improve the use of limited receiver scanning time in an uncertain RF environment.

The system continuously learns from observations and adapts subsequent scan decisions, providing a practical demonstration of **observation-driven and AI-assisted electronic-warfare spectrum scanning**.

---

# Disclaimer

This project is an academic/research simulation and demonstration system. It is intended for software development, algorithm evaluation, visualization, and educational purposes. It does not constitute a real-world electronic-warfare control system and should not be connected to operational RF equipment without appropriate authorization, safety controls, and domain-specific validation.

---

## Team

**Smart Scan Strategy for Electronic Warfare**

Developed as part of the **Smart India Hackathon (SIH)** project.

---

## License

Add the project's applicable license here before publishing the repository.
