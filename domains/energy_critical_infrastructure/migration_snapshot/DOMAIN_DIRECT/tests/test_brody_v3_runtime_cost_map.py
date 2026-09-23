"""
Tests V3 RUNTIME_DISSIPATION — brody_runtime_cost_map
DECISION_AUTHORITY=KX108_ONLY. COMMIT=NO. ACT=NO.
"""
import pytest
from apps.obsidia_api.brody_runtime_cost_map import (
    compute_runtime_cost_map,
    fastpath_cost_map,
    lazy_cost_map,
    full_pipeline_cost_map,
)


# ── 1. Structure de base ───────────────────────────────────────────────────────

def test_compute_returns_dict():
    r = compute_runtime_cost_map()
    assert isinstance(r, dict)


def test_useful_compute_ms_present():
    r = compute_runtime_cost_map(useful_compute_ms=1100.0)
    assert "useful_compute_ms" in r
    assert r["useful_compute_ms"] == 1100.0


def test_orchestration_ms_present():
    r = compute_runtime_cost_map(orchestration_ms=20000.0)
    assert "orchestration_ms" in r
    assert r["orchestration_ms"] == 20000.0


def test_total_ms_is_sum():
    r = compute_runtime_cost_map(
        useful_compute_ms=1100.0,
        orchestration_ms=18000.0,
        diagnostics_ms=500.0,
        memory_readonly_ms=50.0,
        scrub_ms=1.0,
    )
    expected = 1100.0 + 18000.0 + 500.0 + 50.0 + 1.0
    assert abs(r["total_ms"] - expected) < 0.1


# ── 2. Formule dissipation_ratio ──────────────────────────────────────────────

def test_dissipation_ratio_formula():
    r = compute_runtime_cost_map(useful_compute_ms=1100.0, orchestration_ms=20000.0)
    expected = 20000.0 / 1100.0
    assert abs(r["dissipation_ratio"] - expected) < 0.001


def test_dissipation_ratio_no_divide_by_zero():
    r = compute_runtime_cost_map(useful_compute_ms=0.0, orchestration_ms=5000.0)
    assert r["dissipation_ratio"] == 5000.0 / 1.0
    assert r["dissipation_ratio"] == 5000.0


def test_dissipation_ratio_fastpath_minimal():
    r = fastpath_cost_map()
    fp = full_pipeline_cost_map(pipeline_ms=1100.0, handler_ms=21000.0)
    # fastpath dissipation doit être très inférieure au pipeline complet (~18x)
    assert r["dissipation_ratio"] < fp["dissipation_ratio"]
    assert r["total_ms"] < 10.0


# ── 3. Invariants KX108 ───────────────────────────────────────────────────────

def test_decision_authority_kx108_only():
    for fn in (compute_runtime_cost_map, fastpath_cost_map, lazy_cost_map):
        r = fn()
        assert r["decision_authority"] == "KX108_ONLY"


def test_canonical_write_false_always():
    for fn in (compute_runtime_cost_map, fastpath_cost_map, lazy_cost_map, full_pipeline_cost_map):
        r = fn()
        assert r["canonical_write"] is False


def test_emits_act_false_always():
    for fn in (compute_runtime_cost_map, fastpath_cost_map, lazy_cost_map, full_pipeline_cost_map):
        r = fn()
        assert r["emits_act"] is False


# ── 4. Listes skipped/lazy/expensive ──────────────────────────────────────────

def test_skipped_steps_is_list():
    r = compute_runtime_cost_map(skipped_steps=["automation_snapshot", "true_voice_snapshot"])
    assert isinstance(r["skipped_steps"], list)
    assert "automation_snapshot" in r["skipped_steps"]


def test_fastpath_skipped_includes_pipeline():
    r = fastpath_cost_map("adversarial_fastpath")
    assert "real_pipeline" in r["skipped_steps"]
    assert r["fastpath_type"] == "adversarial_fastpath"


def test_full_pipeline_expensive_steps_non_empty():
    r = full_pipeline_cost_map(pipeline_ms=1100.0, handler_ms=21000.0)
    assert isinstance(r["expensive_steps"], list)
    assert len(r["expensive_steps"]) > 0
