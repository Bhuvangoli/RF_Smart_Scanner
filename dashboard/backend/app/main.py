"""
Dashboard backend entrypoint.

Run locally with:
    uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.config import CORS_ORIGINS
from app.models import ErrorResponse
from app.routers import dashboard, rf, simulation

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="SIH26055 Dashboard & Integration Layer",
    version="0.1.0",
    description=(
        "Receives simulated RF observations, manages the scheduler loop, "
        "displays system state, calculates performance metrics, and "
        "provides a reliable fallback when the AI Engine is unavailable."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rf.router)
app.include_router(dashboard.router)
app.include_router(simulation.router)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(error="validation_error", detail=str(exc)).model_dump(),
    )


@app.get("/")
async def root() -> dict:
    return {
        "component": "dashboard",
        "status": "ok",
        "docs": "/docs",
    }
