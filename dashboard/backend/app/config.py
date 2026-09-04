"""
Central configuration for the Dashboard backend.

All values are overridable through environment variables so the
prototype can be pointed at different RF Simulator / AI Engine
instances without code changes (PRD section 2: "Configuration =
Environment variables and configuration files").
"""
import os
from pathlib import Path


def _bool(name: str, default: str) -> bool:
    return os.getenv(name, default).lower() in ("1", "true", "yes", "on")


BASE_DIR = Path(__file__).resolve().parent.parent

# --- Upstream / downstream services -----------------------------------
RF_SIMULATOR_URL = os.getenv("RF_SIMULATOR_URL", "http://127.0.0.1:8001")
AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://127.0.0.1:8002")

# --- AI Engine integration ----------------------------------------------
AI_REQUEST_TIMEOUT_S = float(os.getenv("AI_REQUEST_TIMEOUT_S", "1.5"))
AI_PREDICT_PATH = os.getenv("AI_PREDICT_PATH", "/api/v1/agent/predict")
AI_FEEDBACK_PATH = os.getenv("AI_FEEDBACK_PATH", "/api/v1/agent/feedback")

# --- Windows / history ---------------------------------------------------
OBSERVATION_WINDOW = int(os.getenv("OBSERVATION_WINDOW", "20"))
HISTORY_DISPLAY_LIMIT = int(os.getenv("HISTORY_DISPLAY_LIMIT", "200"))

# --- Fallback engine -------------------------------------------------------
FALLBACK_DIR = Path(os.getenv("FALLBACK_DIR", str(BASE_DIR / "data" / "fallback")))
FALLBACK_RECORDS_PER_SCENARIO = int(os.getenv("FALLBACK_RECORDS_PER_SCENARIO", "250"))

# --- Persistence -----------------------------------------------------------
RUNS_DIR = Path(os.getenv("RUNS_DIR", str(BASE_DIR / "data" / "runs")))
PERSIST_RUNS = _bool("PERSIST_RUNS", "true")

# --- Server ------------------------------------------------------------------
HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
PORT = int(os.getenv("DASHBOARD_PORT", "8000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# --- Validation bounds (Dashboard PRD section 10) ---------------------------
MIN_BAND = 1
MAX_BAND = 8

RUNS_DIR.mkdir(parents=True, exist_ok=True)
FALLBACK_DIR.mkdir(parents=True, exist_ok=True)
