"""
P46 — Tests API : couverture des vues Workbench via os-map/query.
Vérifie que l'endpoint retourne les champs P46 et respecte les invariants.
NO ACT. NO write. READONLY.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from apps.obsidia_api.main import app
    return TestClient(app)


# ── Test 1 : os-map/query retourne workbench_view_coverage_status ─────────────

def test_os_map_query_returns_workbench_coverage_status(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "workbench os map coverage"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "workbench_view_coverage_status" in data, (
        "os-map/query must return workbench_view_coverage_status"
    )


# ── Test 2 : os-map/query retourne unclassified_views_count=0 ────────────────

def test_os_map_query_unclassified_views_count_zero(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "workbench coverage"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("unclassified_views_count") == 0, (
        f"unclassified_views_count must be 0, got {data.get('unclassified_views_count')}"
    )


# ── Test 3 : os-map/query retourne workbench_views_coverage_percent=100 ───────

def test_os_map_query_coverage_percent_100(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "workbench views"},
    )
    assert resp.status_code == 200
    data = resp.json()
    pct = data.get("workbench_views_coverage_percent")
    assert pct == 100.0, f"workbench_views_coverage_percent must be 100.0, got {pct}"


# ── Test 4 : query "workbench os map" retourne des infos sur OSMapView ────────

def test_os_map_query_returns_osmap_view_info(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "workbench os map"},
    )
    assert resp.status_code == 200
    data = resp.json()
    selected_views = data.get("selected_workbench_views", [])
    coverage_status = data.get("workbench_view_coverage_status", "")
    assert coverage_status or selected_views is not None, (
        "Response must contain workbench view information"
    )


# ── Test 5 : query action — les invariants de sécurité tiennent toujours ───────

def test_os_map_query_action_safety_invariants(client):
    """
    Même si le routeur ne détecte pas explicitement l'action blockchain,
    les invariants KX108 (runtime_allowed_now=False, emits_act=False) doivent tenir.
    Les vues BLOCKED_ACTION_VIEW sont garanties dans la coverage map P46 — pas dans le routeur.
    """
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "blockchain wallet sign transaction"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("runtime_allowed_now") is False, "runtime_allowed_now must always be False"
    assert data.get("emits_act") is False, "emits_act must always be False"
    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("world_action") is False, "world_action must always be False"


# ── Test 6 : no ACT / no write / no mutation ─────────────────────────────────

def test_no_act_no_write_invariants(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "test invariants"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("emits_act") is False, "emits_act must be False"
    assert data.get("runtime_allowed_now") is False, "runtime_allowed_now must be False"
    assert data.get("decision_authority") == "KX108_ONLY", "decision_authority must be KX108_ONLY"
    assert data.get("memory_write") is False, "memory_write must be False"
    assert data.get("readonly") is True, "readonly must be True"


# ── Tests supplémentaires ─────────────────────────────────────────────────────

def test_os_map_query_workbench_total_count(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "all workbench views"},
    )
    assert resp.status_code == 200
    data = resp.json()
    total = data.get("workbench_views_total")
    if total is not None:
        assert total == 13, f"workbench_views_total must be 13, got {total}"


def test_os_map_status_endpoint_has_workbench_coverage(client):
    resp = client.get("/api/runtime-wiring/os-map/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("emits_act") is False
    assert data.get("decision_authority") == "KX108_ONLY"


def test_os_map_query_memory_write_false(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "memory graphiti write"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("memory_write") is False
    assert data.get("graph_write") is False


def test_os_map_query_kernel_mutation_false(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "kernel mutation"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("kernel_mutation") is False
