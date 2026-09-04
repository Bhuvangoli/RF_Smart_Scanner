"""
Generates the deterministic fallback dataset (Dashboard_PRD.md
sections 12 & 14):

    250 records for periodic behaviour
    250 records for bursty behaviour
    250 records for frequency-agile behaviour
    250 records for mixed behaviour

Each record follows the FallbackRecord schema:
    timestamp, selected_band, prediction, confidence, actual, result,
    intercept_time_ms, reward

The generator is itself seeded so the dataset is reproducible
(RFD_Sim_PRD.md section 9 / 25 - reproducibility applies to fallback
data too, since it must be "a coherent sequence rather than
independent random values", Dashboard_PRD.md section 13).

Usage:
    python scripts/generate_fallback.py
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import FALLBACK_DIR, FALLBACK_RECORDS_PER_SCENARIO  # noqa: E402

SEED = 12345
BANDS = list(range(1, 9))


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def generate_periodic(n: int, rng: random.Random) -> list[dict]:
    """Recurring band with occasional jitter, mimics a periodic emitter
    being tracked well by the scheduler (RFD_Sim_PRD.md section 8.1)."""
    records = []
    period_band_cycle = [3, 3, 3, 6, 6, 1, 1, 5]
    for t in range(n):
        band = period_band_cycle[t % len(period_band_cycle)]
        if rng.random() < 0.1:
            band = rng.choice(BANDS)
        active = rng.random() < 0.75
        detected = active and rng.random() < 0.85
        prediction = _clip01(0.8 if active else 0.2 + rng.uniform(-0.1, 0.1))
        confidence = _clip01(0.75 + rng.uniform(-0.1, 0.15))
        result = "hit" if detected and active else "miss"
        intercept_time = round(rng.uniform(50, 400), 1) if result == "hit" else 0.0
        reward = 1.0 if result == "hit" else (-1.0 if active else -0.1)
        records.append(
            dict(
                timestamp=t,
                selected_band=band,
                prediction=round(prediction, 3),
                confidence=round(confidence, 3),
                actual=active,
                result=result,
                intercept_time_ms=intercept_time,
                reward=reward,
            )
        )
    return records


def generate_bursty(n: int, rng: random.Random) -> list[dict]:
    """Clustered activity across a couple of bands (RFD_Sim_PRD.md
    section 8.2)."""
    records = []
    burst_bands = [2, 7]
    in_burst = False
    burst_len_left = 0
    for t in range(n):
        if not in_burst and rng.random() < 0.15:
            in_burst = True
            burst_len_left = rng.randint(3, 8)
        band = rng.choice(burst_bands) if in_burst else rng.choice(BANDS)
        active = in_burst and rng.random() < 0.8
        detected = active and rng.random() < 0.7
        prediction = _clip01((0.7 if in_burst else 0.25) + rng.uniform(-0.1, 0.1))
        confidence = _clip01(0.6 + rng.uniform(-0.15, 0.2))
        result = "hit" if detected and active else "miss"
        intercept_time = round(rng.uniform(80, 600), 1) if result == "hit" else 0.0
        reward = 1.0 if result == "hit" else (-1.0 if active else -0.1)
        records.append(
            dict(
                timestamp=t,
                selected_band=band,
                prediction=round(prediction, 3),
                confidence=round(confidence, 3),
                actual=active,
                result=result,
                intercept_time_ms=intercept_time,
                reward=reward,
            )
        )
        if in_burst:
            burst_len_left -= 1
            if burst_len_left <= 0:
                in_burst = False
    return records


def generate_frequency_agile(n: int, rng: random.Random) -> list[dict]:
    """Band hops using a simple Markov transition matrix (RFD_Sim_PRD.md
    section 8.3)."""
    records = []
    band = rng.choice(BANDS)
    transition_bias = {b: [b, (b % 8) + 1, ((b + 3) % 8) + 1] for b in BANDS}
    for t in range(n):
        band = rng.choice(transition_bias[band])
        active = rng.random() < 0.6
        detected = active and rng.random() < 0.6
        prediction = _clip01(0.55 + rng.uniform(-0.2, 0.2))
        confidence = _clip01(0.5 + rng.uniform(-0.15, 0.2))
        result = "hit" if detected and active else "miss"
        intercept_time = round(rng.uniform(100, 700), 1) if result == "hit" else 0.0
        reward = 1.0 if result == "hit" else (-1.0 if active else -0.1)
        records.append(
            dict(
                timestamp=t,
                selected_band=band,
                prediction=round(prediction, 3),
                confidence=round(confidence, 3),
                actual=active,
                result=result,
                intercept_time_ms=intercept_time,
                reward=reward,
            )
        )
    return records


def generate_mixed(n: int, rng: random.Random) -> list[dict]:
    """Blend of all behaviours - the primary demonstration scenario
    (RFD_Sim_PRD.md section 22, Scenario C)."""
    generators = [generate_periodic, generate_bursty, generate_frequency_agile]
    chunk = n // len(generators)
    records: list[dict] = []
    for i, gen in enumerate(generators):
        part = gen(chunk if i < len(generators) - 1 else n - len(records), rng)
        records.extend(part)
    for i, r in enumerate(records):
        r["timestamp"] = i
    return records


def main() -> None:
    rng = random.Random(SEED)
    FALLBACK_DIR.mkdir(parents=True, exist_ok=True)

    datasets = {
        "periodic": generate_periodic(FALLBACK_RECORDS_PER_SCENARIO, rng),
        "bursty": generate_bursty(FALLBACK_RECORDS_PER_SCENARIO, rng),
        "frequency_agile": generate_frequency_agile(FALLBACK_RECORDS_PER_SCENARIO, rng),
        "mixed": generate_mixed(FALLBACK_RECORDS_PER_SCENARIO, rng),
    }

    for name, records in datasets.items():
        path = FALLBACK_DIR / f"{name}.jsonl"
        with path.open("w") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")
        print(f"wrote {len(records):4d} records -> {path}")


if __name__ == "__main__":
    main()
