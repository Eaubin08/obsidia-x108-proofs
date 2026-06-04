"""
P50 — Tests API : matrice d'activation contrôlée via os-map/query.
Vérifie que l'endpoint retourne les champs P50 et respecte les invariants KX108.
NO ACT. NO write. READONLY.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from apps.obsidia_api.main import app
    return TestClient(app)


# ── Test 1 : os-map/query retourne activation_matrix_status ──────────────────

def test_os_map_query_returns_activation_matrix_status(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "activation matrix readiness"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "activation_matrix_status" in data, (
        "os-map/query must return activation_matrix_status"
    )


# ── Test 2 : activation_allowed_now == false ──────────────────────────────────

def test_os_map_query_activation_allowed_now_false(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "activation allowed now"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("activation_allowed_now") is False, (
        f"activation_allowed_now must be False, got {data.get('activation_allowed_now')}"
    )


# ── Test 3 : next_activation_palier == P51 ───────────────────────────────────

def test_os_map_query_next_activation_palier(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "next activation palier"},
    )
    assert resp.status_code == 200
    data = resp.json()
    palier = data.get("next_activation_palier", "")
    assert "P51" in palier, (
        f"next_activation_palier must reference P51, got {palier!r}"
    )


# ── Test 4 : query brody retourne brody comme readonly candidate ──────────────

def test_os_map_query_brody_readonly_candidate(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "brody context activation level"},
    )
    assert resp.status_code == 200
    data = resp.json()
    candidates = data.get("readonly_activation_candidates", [])
    assert "brody_context_readonly" in candidates, (
        f"brody_context_readonly must be in readonly_activation_candidates; got {candidates}"
    )


# ── Test 5 : query action reste no ACT / KX108_ONLY ──────────────────────────

def test_os_map_query_action_no_act(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "execute action now real"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("emits_act") is False
    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("runtime_allowed_now") is False


# ── Test bonus : locked_items présent ─────────────────────────────────────────

def test_os_map_query_locked_items_present(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "locked items security check"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "locked_items" in data, "os-map/query must return locked_items"


# ── Test bonus : future_action_gate_items présent ────────────────────────────

def test_os_map_query_future_action_gate_items(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "future action gate items"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "future_action_gate_items" in data
    items = data["future_action_gate_items"]
    assert isinstance(items, list)


# ── Test bonus : readonly_activation_candidates non vide ─────────────────────

def test_os_map_query_readonly_candidates_not_empty(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "readonly activation candidates"},
    )
    assert resp.status_code == 200
    data = resp.json()
    candidates = data.get("readonly_activation_candidates", [])
    assert len(candidates) > 0, "readonly_activation_candidates must not be empty"


# ── Test bonus : dry_run_activation_candidates présent ───────────────────────

def test_os_map_query_dry_run_candidates_present(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "dry run simulation candidates"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "dry_run_activation_candidates" in data
