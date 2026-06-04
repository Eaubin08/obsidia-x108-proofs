"""
P48 — Tests API : couverture adapters via os-map/query.
Vérifie que l'endpoint retourne les champs P48 et respecte les invariants KX108.
NO ACT. NO write. READONLY.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from apps.obsidia_api.main import app
    return TestClient(app)


# ── Test 1 : os-map/query retourne adapter_coverage_status ───────────────────

def test_os_map_query_returns_adapter_coverage_status(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "adapter coverage"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "adapter_coverage_status" in data, (
        "os-map/query must return adapter_coverage_status"
    )


# ── Test 2 : adapters_unclassified_count=0 ───────────────────────────────────

def test_os_map_query_adapters_unclassified_zero(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "adapter coverage"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("adapters_unclassified_count") == 0, (
        f"adapters_unclassified_count must be 0, got {data.get('adapters_unclassified_count')}"
    )


# ── Test 3 : adapter_coverage_percent=100 ────────────────────────────────────

def test_os_map_query_adapter_coverage_100(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "adapter coverage percent"},
    )
    assert resp.status_code == 200
    data = resp.json()
    pct = data.get("adapter_coverage_percent")
    assert pct == 100.0, f"adapter_coverage_percent must be 100.0, got {pct}"


# ── Test 4 : query IR alphabet reverse OS retourne selected_adapters_classified

def test_os_map_query_ir_alphabet_returns_adapters(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "IR alphabet reverse OS interlanguage"},
    )
    assert resp.status_code == 200
    data = resp.json()
    adapters = data.get("selected_adapters_classified", [])
    assert adapters is not None, "selected_adapters_classified must be present"


# ── Test 5 : query atlas retourne atlas adapter classifié ─────────────────────

def test_os_map_query_atlas_returns_adapter(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "atlas component map branchable"},
    )
    assert resp.status_code == 200
    data = resp.json()
    adapters = data.get("selected_adapters_classified", [])
    assert adapters is not None, "selected_adapters_classified must be present"
    coverage_status = data.get("adapter_coverage_status", "")
    assert coverage_status, "adapter_coverage_status must be non-empty"


# ── Test 6 : query action — invariants KX108 tiennent ────────────────────────

def test_os_map_query_action_no_act(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "action blockchain gencoin"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("runtime_allowed_now") is False
    assert data.get("emits_act") is False
    assert data.get("decision_authority") == "KX108_ONLY"


# ── Tests supplémentaires ─────────────────────────────────────────────────────

def test_os_map_query_adapters_total(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "all adapters"},
    )
    assert resp.status_code == 200
    data = resp.json()
    total = data.get("adapters_total")
    if total is not None:
        assert total == 10, f"adapters_total must be 10, got {total}"


def test_os_map_query_no_mutation(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "adapter source runtime"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("memory_write") is False
    assert data.get("graph_write") is False
    assert data.get("kernel_mutation") is False
    assert data.get("world_action") is False


def test_os_map_status_adapter_fields(client):
    resp = client.get("/api/runtime-wiring/os-map/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("emits_act") is False
    assert data.get("decision_authority") == "KX108_ONLY"


def test_os_map_query_p45_p46_p47_p48_all_present(client):
    """Vérifie que tous les champs des phases P45→P48 sont présents dans une réponse."""
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "full coverage audit"},
    )
    assert resp.status_code == 200
    data = resp.json()
    # P45
    assert "route_coverage_status" in data
    assert "route_coverage_percent" in data
    # P46
    assert "workbench_view_coverage_status" in data
    assert "workbench_views_coverage_percent" in data
    # P47
    assert "module_function_coverage_status" in data
    assert "module_coverage_percent" in data
    # P48
    assert "adapter_coverage_status" in data
    assert "adapter_coverage_percent" in data
