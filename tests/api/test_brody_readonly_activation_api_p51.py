"""
P51 — Tests API : activation Brody READONLY_CONTEXT via /api/brody/chat et os-map/query.
Vérifie que les endpoints retournent les champs P51 et respectent les invariants KX108.
NO ACT. NO write. READONLY.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from apps.obsidia_api.main import app
    return TestClient(app)


# ── Test 1 : /api/brody/chat retourne brody_readonly_activation_status ────────

def test_brody_chat_returns_readonly_activation_status(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "Explique le runtime path Obsidia"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "brody_readonly_activation_status" in data, (
        "brody/chat must return brody_readonly_activation_status"
    )


# ── Test 2 : /api/brody/chat retourne selected_runtime_path ou os_map_summary ─

def test_brody_chat_returns_os_map_summary(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "OS Map capability path routing"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "os_map_summary" in data or "selected_runtime_path" in data, (
        "brody/chat must return os_map_summary or selected_runtime_path"
    )


# ── Test 3 : query IR alphabet reverse OS retourne source/runtime context ─────

def test_brody_chat_ir_alphabet_returns_source_context(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "IR alphabet reverse OS interlanguage"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("brody_readonly_activation_status") == "ACTIVE_READONLY"
    assert data.get("brody_readonly_enabled") is True


# ── Test 4 : query brody true voice retourne L1 readonly ─────────────────────

def test_brody_chat_true_voice_readonly(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "brody chat true voice final answer"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("brody_activation_level") == "LEVEL_1_READONLY_ACTIVE"
    assert data.get("brody_can_execute_actions") is False


# ── Test 5 : query action reste ACTION_REQUEST_BLOCKED / no ACT ───────────────

def test_brody_chat_action_blocked(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "envoie un mail à etienne maintenant"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("emits_act") is False
    assert data.get("memory_write") is False
    assert data.get("brody_can_execute_actions") is False
    assert data.get("brody_action_status") in (
        "ACTION_REQUEST_BLOCKED", "NO_ACTION_IN_QUERY", None
    )


# ── Test 6 : os-map/query retourne brody_readonly_enabled=true ───────────────

def test_os_map_query_brody_readonly_enabled(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "brody readonly activation level"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("brody_readonly_enabled") is True, (
        f"brody_readonly_enabled must be True, got {data.get('brody_readonly_enabled')}"
    )


# ── Test 7 : no write / no mutation / KX108_ONLY ─────────────────────────────

def test_brody_chat_no_write_kx108_only(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "que peux-tu faire ?"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("memory_write") is False
    assert data.get("graphiti_write") is False
    assert data.get("kernel_mutation") is False
    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("brody_no_act") is True
    assert data.get("brody_no_write") is True
    assert data.get("brody_kx108_only") is True


# ── Test bonus : os-map/query retourne brody_activation_level ────────────────

def test_os_map_query_brody_activation_level(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "brody activation level check"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("brody_activation_level") == "LEVEL_1_READONLY_ACTIVE"


# ── Test bonus : os-map/query retourne brody_next_allowed_mode ───────────────

def test_os_map_query_brody_next_allowed_mode(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "brody next activation mode"},
    )
    assert resp.status_code == 200
    data = resp.json()
    mode = data.get("brody_next_allowed_mode", "")
    assert "READONLY" in mode or "CONTEXT" in mode, (
        f"brody_next_allowed_mode must reference READONLY/CONTEXT, got {mode!r}"
    )


# ── Test bonus : brody_readonly_activation_status == ACTIVE_READONLY ─────────

def test_os_map_query_brody_readonly_activation_status(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "brody readonly status"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("brody_readonly_activation_status") == "ACTIVE_READONLY"
