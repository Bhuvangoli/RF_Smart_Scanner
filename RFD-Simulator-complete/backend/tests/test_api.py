import pytest
from fastapi.testclient import TestClient
from main import app, engine


@pytest.fixture(autouse=True)
def cleanup():
    yield
    import asyncio
    asyncio.run(engine.stop())


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["component"] == "rf-simulator"


def test_controls(client):
    assert client.post("/api/v1/simulation/start").status_code == 200
    assert client.post("/api/v1/simulation/pause").json()["status"] == "paused"
    assert client.post("/api/v1/simulation/resume").status_code == 200
    assert client.post("/api/v1/simulation/reset").json()["status"] == "reset"


def test_decision_contract(client):
    client.post("/api/v1/simulation/start")
    state = client.get("/api/v1/simulation/state").json()
    r = client.post(
        "/api/v1/simulation/decision",
        json={
            "simulation_id": state["simulation_id"],
            "next_band": 6,
            "dwell_ms": 100,
        },
    )
    assert r.status_code == 200
    assert r.json()["status"] == "decision_received"
    client.post("/api/v1/simulation/reset")


def test_stale_decision_rejected(client):
    client.post("/api/v1/simulation/start")
    r = client.post(
        "/api/v1/simulation/decision",
        json={
            "simulation_id": "stale-id-12345",
            "next_band": 6,
            "dwell_ms": 100,
        },
    )
    assert r.status_code == 400
    assert "simulation_id does not match" in r.json()["detail"]
    client.post("/api/v1/simulation/reset")


def test_observation_contract(client):
    payload = {
        "simulation_id": "demo-001",
        "timestamp": 173,
        "receiver": {"band_id": 6, "dwell_ms": 100},
        "observation": {"detected": True, "signal_strength_db": -61.4},
        "outcome": {"ground_truth_active": True, "emitter_ids": ["E02"]},
    }
    r = client.post("/api/v1/rf/observation", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "observation_received"


def test_configuration(client):
    r = client.post(
        "/api/v1/simulation/configure",
        json={"scenario": "mixed", "seed": 12345, "speed": 2},
    )
    assert r.status_code == 200
    assert r.json()["scenario"] == "mixed"


