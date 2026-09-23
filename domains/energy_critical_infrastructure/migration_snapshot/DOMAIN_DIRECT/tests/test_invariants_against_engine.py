# Phase 3 — Invariant bridge: wired to real engine (obsidia_os2.metrics)
# Auto-detected entry: obsidia_os2.metrics / decision_act_hold
# Adapted from auto-generated stub: real API uses Metrics dataclass, not (intent, state)

import os
import sys
import importlib

ENGINE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "engine"))
sys.path.insert(0, ENGINE_ROOT)

ENGINE_MODULE_PATH = "obsidia_os2.metrics"
ENGINE_FUNC = "decision_act_hold"


def load_engine():
    """Load the real decision function from the engine."""
    mod = importlib.import_module(ENGINE_MODULE_PATH)
    return getattr(mod, ENGINE_FUNC)


def make_metrics(T_mean=0.5, H_score=0.5, A_score=0.1, S=0.5):
    """Helper: build a Metrics dataclass instance."""
    mod = importlib.import_module(ENGINE_MODULE_PATH)
    return mod.Metrics(T_mean=T_mean, H_score=H_score, A_score=A_score, S=S)


def test_determinism():
    """Invariant D1 — Same inputs must always produce the same output (determinism)."""
    decide = load_engine()
    metrics = make_metrics(S=0.5)
    r1 = decide(metrics)
    r2 = decide(metrics)
    assert r1 == r2, f"Determinism violated: got {r1} then {r2}"


def test_no_allow_before_tau():
    """Invariant E2 — S < theta_S must produce HOLD, never ACT (no execution before threshold)."""
    decide = load_engine()
    metrics_low = make_metrics(S=0.0)
    r = decide(metrics_low, theta_S=0.25)
    assert r != "ACT", f"Violation E2: ACT returned when S=0.0 (below tau threshold)"
    assert r == "HOLD", f"Expected HOLD when S < theta_S, got: {r}"


def test_act_above_threshold():
    """Invariant G1 — When S >= theta_S, decision must be ACT."""
    decide = load_engine()
    metrics_high = make_metrics(S=1.0)
    r = decide(metrics_high, theta_S=0.25)
    assert r == "ACT", f"Expected ACT when S=1.0 >= theta_S=0.25, got: {r}"


def test_hold_at_boundary():
    """Invariant G2 — At exact boundary S == theta_S, decision must be ACT (>= inclusive)."""
    decide = load_engine()
    metrics_boundary = make_metrics(S=0.25)
    r = decide(metrics_boundary, theta_S=0.25)
    assert r == "ACT", f"Expected ACT at boundary S=theta_S=0.25, got: {r}"


def test_monotonicity():
    """Invariant G3 — Higher S must not produce a weaker decision than lower S."""
    decide = load_engine()
    r_low = decide(make_metrics(S=0.1), theta_S=0.25)
    r_high = decide(make_metrics(S=0.9), theta_S=0.25)
    order = {"HOLD": 0, "ACT": 1}
    assert order[r_high] >= order[r_low], \
        f"Monotonicity violated: S=0.1->{r_low}, S=0.9->{r_high}"


def test_compute_metrics_pipeline():
    """Integration — Full pipeline: compute_metrics_core_fixed -> decision_act_hold."""
    mod = importlib.import_module(ENGINE_MODULE_PATH)
    W = [[0.0, 0.8, 0.6],
         [0.8, 0.0, 0.7],
         [0.6, 0.7, 0.0]]
    core_nodes = [0, 1, 2]
    metrics = mod.compute_metrics_core_fixed(W, core_nodes)
    r = mod.decision_act_hold(metrics)
    assert r in ("ACT", "HOLD"), f"Unexpected decision: {r}"
