"""
Performance metrics (Dashboard_PRD.md sections 23-27).

Notes on the approximations used in this prototype (documented as
required by Dashboard_PRD.md section 25 / 27: "the exact ... can
change when the AI Engine specification defines the final evaluation
protocol"):

- The RF Simulator only reports ground truth for the *selected* band
  each slot (privacy-preserving RF Event Contract). This is treated
  as one binary relevant/irrelevant event per slot:
    ground_truth_active == True  -> a "relevant emitter event"
    hit (detected == True)       -> a "successfully intercepted event"
  Probability of Detection / Interception Ratio therefore coincide in
  this simplified single-receiver model. They are kept as separate
  fields so the AI Engine PRD can later refine the definitions
  independently without changing the API shape.

- Intercept time is approximated per emitter_id: the first slot in
  which an emitter_id appears in `outcome.emitter_ids` (since the
  last time that emitter was hit) is treated as its "activation".
  Intercept time = timestamp_of_hit - timestamp_of_first_seen. This
  is a reasonable proxy given the information available at the
  Dashboard boundary and is explicitly flagged as provisional.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from app.models import MetricsSnapshot
from app.state import DashboardState


def record_observation(state: DashboardState, obs: dict) -> str:
    """Update running counters from one completed RF Event Contract
    record (already merged with the decision that produced it and
    the AI prediction, if any). Returns "hit" or "miss".

    Expected `obs` shape (a flattened HistoryRecord, see routers/rf.py):
        timestamp, receiver_band, dwell_ms, detected, signal_strength_db,
        ground_truth_active, emitter_ids, prediction, confidence,
        decision_source
    """
    detected = bool(obs["detected"])
    active = bool(obs["ground_truth_active"])
    result = "hit" if (detected and active) else "miss"
    obs["result"] = result

    state.total_observations += 1
    if detected and active:
        state.true_positive += 1
    elif (not detected) and active:
        state.false_negative += 1
    elif detected and not active:
        state.false_positive += 1
    else:
        state.true_negative += 1

    # prediction accuracy: did predicted activity (>0.5) match ground truth?
    prediction = obs.get("prediction")
    if prediction is not None:
        predicted_active = prediction >= 0.5
        state.prediction_total += 1
        if predicted_active == active:
            state.prediction_correct += 1

    # intercept time bookkeeping, per emitter id present this slot
    ts = obs["timestamp"]
    for emitter_id in obs.get("emitter_ids", []):
        if emitter_id not in state._emitter_first_seen:
            state._emitter_first_seen[emitter_id] = ts
        if result == "hit":
            start = state._emitter_first_seen.pop(emitter_id, ts)
            state.intercept_times_ms.append(float(ts - start) * obs.get("dwell_ms", 100))

    reward = compute_reward(detected, active, obs)
    obs["reward"] = reward
    state.rewards.append(reward)

    return result


def compute_reward(detected: bool, active: bool, obs: dict) -> float:
    """Preliminary reward model (Dashboard_PRD.md section 26):
    rewards a genuine hit, penalises a missed active emitter, and
    lightly penalises scanning a band that turned out inactive
    (discourages repeated scans of dead bands)."""
    if detected and active:
        return 1.0
    if (not detected) and active:
        return -1.0
    if detected and not active:
        return -0.25
    return -0.1


def snapshot(state: DashboardState) -> MetricsSnapshot:
    tp, fn, fp, tn = (
        state.true_positive,
        state.false_negative,
        state.false_positive,
        state.true_negative,
    )

    pd = tp / (tp + fn) if (tp + fn) else 0.0
    pfa = fp / (fp + tn) if (fp + tn) else 0.0
    interception_ratio = pd  # see module docstring
    accuracy = (
        state.prediction_correct / state.prediction_total
        if state.prediction_total
        else 0.0
    )
    avg_reward = sum(state.rewards) / len(state.rewards) if state.rewards else 0.0
    avg_intercept = (
        sum(state.intercept_times_ms) / len(state.intercept_times_ms)
        if state.intercept_times_ms
        else None
    )

    return MetricsSnapshot(
        probability_of_detection=round(pd, 4),
        false_alarm_probability=round(pfa, 4),
        average_intercept_time_ms=(
            round(avg_intercept, 2) if avg_intercept is not None else None
        ),
        average_intercept_time_error_ms=None,  # requires a target/expected intercept
        interception_ratio=round(interception_ratio, 4),
        prediction_accuracy=round(accuracy, 4),
        average_reward=round(avg_reward, 4),
        total_observations=state.total_observations,
        total_hits=tp,
        total_misses=fn + fp + tn,
    )


# ---------------------------------------------------------------------------
# Baseline (sequential scan) comparison, computed against the SAME history
# using each record's ground truth (Dashboard_PRD.md section 27).
# ---------------------------------------------------------------------------
def compute_sequential_baseline(history: List[dict]) -> Optional[Dict[str, float]]:
    """Replays the sequential 1->8 schedule against the recorded ground
    truth to give a like-for-like comparison point. Because the
    simulator only reports ground truth for the band it actually
    observed each slot, this baseline can only score slots where the
    sequential band happens to equal the actually-selected band. This
    is a known prototype limitation (RFD_Sim_PRD.md / Dashboard_PRD.md
    both flag full physical-layer ground truth as out of scope); it is
    still useful as an approximate reference and is clearly labelled
    as such in the UI.
    """
    if not history:
        return None

    hits = 0
    relevant = 0
    rewards: List[float] = []
    seq_band = 1
    matched_slots = 0

    for record in history:
        actual_band = record["receiver_band"]
        active = record["ground_truth_active"]
        would_hit = active and (seq_band == actual_band)

        if seq_band == actual_band:
            matched_slots += 1
            if active:
                relevant += 1
                if would_hit:
                    hits += 1
            rewards.append(compute_reward(would_hit, active, record))

        seq_band = (seq_band % 8) + 1

    if matched_slots == 0:
        return None

    return {
        "detection_rate": round(hits / relevant, 4) if relevant else 0.0,
        "interception_ratio": round(hits / relevant, 4) if relevant else 0.0,
        "average_reward": round(sum(rewards) / len(rewards), 4) if rewards else 0.0,
        "sampled_slots": matched_slots,
    }
