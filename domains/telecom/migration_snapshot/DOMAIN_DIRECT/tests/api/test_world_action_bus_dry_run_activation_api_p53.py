"""
P53 — Tests API : activation World Action Bus DRY_RUN via /api/brody/chat et os-map/query.
Vérifie que les endpoints retournent les champs P53 et respectent les invariants KX108.
NO ACT. NO write. DRY_RUN.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from apps.obsidia_api.main import app
    return TestClient(app)


# ── Test 1 : /api/brody/chat query action retourne world_action_bus_dry_run_status ──

def test_brody_chat_action_query_returns_dry_run_status(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "envoie un mail maintenant"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "world_action_bus_dry_run_status" in data, (
        "brody/chat must return world_action_bus_dry_run_status for action query"
    )


# ── Test 2 : /api/brody/chat query action retourne dry_run_packet ─────────────

def test_brody_chat_action_query_returns_dry_run_packet(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "envoie un mail maintenant"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "world_action_bus_dry_run_packet" in data, (
        "brody/chat must return world_action_bus_dry_run_packet for action query"
    )


# ── Test 3 : action_request_blocked == True ───────────────────────────────────

def test_brody_chat_action_blocked(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "envoie un mail maintenant"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("world_action_bus_action_request_blocked") is True


# ── Test 4 : real_action_enabled == False ─────────────────────────────────────

def test_brody_chat_real_action_disabled(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "lance une transaction blockchain"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("world_action_bus_real_action_enabled") is False


# ── Test 5 : runtime_allowed_now ou allowed_to_act == False ───────────────────

def test_brody_chat_runtime_not_allowed(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "envoie un mail maintenant"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    # Either field must be False or absent (default False)
    runtime_allowed = data.get("world_action_bus_runtime_allowed_now", False)
    allowed_to_act = data.get("allowed_to_act", False)
    assert runtime_allowed is False
    assert allowed_to_act is False


# ── Test 6 : emits_act == False ───────────────────────────────────────────────

def test_brody_chat_emits_act_false(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "lance une transaction blockchain"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("emits_act") is False


# ── Test 7 : /api/runtime-wiring/os-map/query expose P53 ─────────────────────

def test_os_map_query_exposes_p53(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "envoie un mail maintenant"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "world_action_bus_dry_run_status" in data, (
        "os-map/query must return world_action_bus_dry_run_status"
    )


# ── Test 8 : no Graphiti write ────────────────────────────────────────────────

def test_brody_chat_no_graphiti_write(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "envoie un mail maintenant"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("graphiti_write", False) is False
    assert data.get("graphiti_write_enabled", False) is False


# ── Test 9 : no memory write ──────────────────────────────────────────────────

def test_brody_chat_no_memory_write(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "écris en mémoire"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("memory_write", False) is False
    assert data.get("brody_can_write_memory", False) is False


# ── Test 10 : KX108_ONLY ──────────────────────────────────────────────────────

def test_brody_chat_kx108_only(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "envoie un mail maintenant"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("brody_kx108_only") is True
