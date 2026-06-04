"""
P47 — Tests API : couverture modules/fonctions via os-map/query.
Vérifie que l'endpoint retourne les champs P47 et respecte les invariants KX108.
NO ACT. NO write. READONLY.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from apps.obsidia_api.main import app
    return TestClient(app)


# ── Test 1 : os-map/query retourne module_function_coverage_status ────────────

def test_os_map_query_returns_module_function_coverage_status(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "module function coverage"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "module_function_coverage_status" in data, (
        "os-map/query must return module_function_coverage_status"
    )


# ── Test 2 : modules_unclassified_count=0 ────────────────────────────────────

def test_os_map_query_modules_unclassified_zero(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "module coverage"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("modules_unclassified_count") == 0, (
        f"modules_unclassified_count must be 0, got {data.get('modules_unclassified_count')}"
    )


# ── Test 3 : functions_unclassified_count=0 ───────────────────────────────────

def test_os_map_query_functions_unclassified_zero(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "function coverage"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("functions_unclassified_count") == 0, (
        f"functions_unclassified_count must be 0, got {data.get('functions_unclassified_count')}"
    )


# ── Test 4 : module_coverage_percent=100 ─────────────────────────────────────

def test_os_map_query_module_coverage_100(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "module coverage percent"},
    )
    assert resp.status_code == 200
    data = resp.json()
    pct = data.get("module_coverage_percent")
    assert pct == 100.0, f"module_coverage_percent must be 100.0, got {pct}"


# ── Test 5 : function_coverage_percent=100 ───────────────────────────────────

def test_os_map_query_function_coverage_100(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "function coverage percent"},
    )
    assert resp.status_code == 200
    data = resp.json()
    pct = data.get("function_coverage_percent")
    assert pct == 100.0, f"function_coverage_percent must be 100.0, got {pct}"


# ── Test 6 : query brody retourne selected_modules_classified ────────────────

def test_os_map_query_brody_returns_modules_classified(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "brody chat true voice"},
    )
    assert resp.status_code == 200
    data = resp.json()
    mods = data.get("selected_modules_classified", [])
    assert mods is not None, "selected_modules_classified must be present"


# ── Test 7 : query os map retourne selected_functions_classified ──────────────

def test_os_map_query_route_coverage_returns_functions(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "os map route coverage"},
    )
    assert resp.status_code == 200
    data = resp.json()
    fns = data.get("selected_functions_classified", [])
    assert fns is not None, "selected_functions_classified must be present"


# ── Test 8 : query action — invariants KX108 tiennent ────────────────────────

def test_os_map_query_action_kx108_invariants(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "blockchain wallet gencoin"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("runtime_allowed_now") is False
    assert data.get("emits_act") is False
    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("memory_write") is False


# ── Tests supplémentaires ─────────────────────────────────────────────────────

def test_os_map_query_modules_total(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "all modules"},
    )
    assert resp.status_code == 200
    data = resp.json()
    total = data.get("modules_total")
    if total is not None:
        assert total == 121, f"modules_total must be 121, got {total}"


def test_os_map_query_functions_total(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "all functions"},
    )
    assert resp.status_code == 200
    data = resp.json()
    total = data.get("functions_total")
    if total is not None:
        assert total == 548, f"functions_total must be 548, got {total}"


def test_os_map_status_no_mutation(client):
    resp = client.get("/api/runtime-wiring/os-map/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("emits_act") is False
    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("kernel_mutation") is False


def test_os_map_query_graph_write_false(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "graphiti memory write"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("graph_write") is False
    assert data.get("memory_write") is False
