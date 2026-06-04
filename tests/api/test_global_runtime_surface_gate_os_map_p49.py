"""
P49 — Tests API : gate global runtime surface via os-map/query.
Vérifie que l'endpoint retourne les champs P49 et respecte les invariants KX108.
NO ACT. NO write. READONLY.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from apps.obsidia_api.main import app
    return TestClient(app)


# ── Test 1 : os-map/query retourne global_runtime_surface_status ─────────────

def test_os_map_query_returns_global_runtime_surface_status(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "global runtime surface coverage"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "global_runtime_surface_status" in data, (
        "os-map/query must return global_runtime_surface_status"
    )


# ── Test 2 : overall_coverage_percent == 100 ─────────────────────────────────

def test_os_map_query_overall_coverage_100(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "global coverage percent"},
    )
    assert resp.status_code == 200
    data = resp.json()
    pct = data.get("overall_coverage_percent")
    assert pct == 100.0, f"overall_coverage_percent must be 100.0, got {pct}"


# ── Test 3 : global_unclassified_total == 0 ───────────────────────────────────

def test_os_map_query_global_unclassified_zero(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "unclassified surface audit"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("global_unclassified_total") == 0, (
        f"global_unclassified_total must be 0, got {data.get('global_unclassified_total')}"
    )


# ── Test 4 : activation_allowed == false ──────────────────────────────────────

def test_os_map_query_activation_allowed_false(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "check activation status"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("activation_allowed") is False, (
        f"activation_allowed must be False, got {data.get('activation_allowed')}"
    )


# ── Test 5 : global_surface_gate_passed == true ───────────────────────────────

def test_os_map_query_global_surface_gate_passed(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "global gate status"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("global_surface_gate_passed") is True, (
        f"global_surface_gate_passed must be True, got {data.get('global_surface_gate_passed')}"
    )


# ── Test 6 : query action garde ACTION_REQUEST_BLOCKED / pas d'ACT ───────────

def test_os_map_query_action_blocked(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "act execute write now"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("emits_act") is False, "emits_act must be False"
    assert data.get("runtime_allowed_now") is False, "runtime_allowed_now must be False"


# ── Test 7 : KX108_ONLY partout ───────────────────────────────────────────────

def test_os_map_query_kx108_only(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "decision authority check"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("decision_authority") == "KX108_ONLY", (
        f"decision_authority must be KX108_ONLY, got {data.get('decision_authority')}"
    )


# ── Test bonus : coverage_categories_summary présent ────────────────────────

def test_os_map_query_coverage_categories_summary_present(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "coverage categories summary"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "coverage_categories_summary" in data, (
        "os-map/query must return coverage_categories_summary"
    )
    summary = data["coverage_categories_summary"]
    if summary:
        for cat in ("families", "routes", "workbench_views", "modules", "functions", "adapters"):
            assert cat in summary, f"coverage_categories_summary must contain {cat}"


# ── Test bonus : runtime_allowed_now == False ────────────────────────────────

def test_os_map_query_runtime_allowed_now_false(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "runtime surface gate"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("runtime_allowed_now") is False
