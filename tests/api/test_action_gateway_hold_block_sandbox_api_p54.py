"""
P54 — Tests API : Hold/Block sandbox via /api/brody/chat et os-map/query.
Vérifie que les endpoints exposent le sandbox verdict et respectent les invariants KX108.
NO ACT. NO write. SANDBOX.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from apps.obsidia_api.main import app
    return TestClient(app)


# ── Test 1 : /api/brody/chat query action expose action_gateway_sandbox_status ─

def test_brody_chat_exposes_sandbox_status(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "envoie un mail maintenant"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "action_gateway_sandbox_status" in data, (
        "brody/chat must return action_gateway_sandbox_status"
    )


# ── Test 2 : /api/brody/chat mail query donne sandbox_verdict BLOCK ──────────

def test_brody_chat_mail_gives_block_verdict(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "envoie un mail maintenant"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("action_gateway_sandbox_verdict") == "BLOCK", (
        f"Expected BLOCK for mail query, got: {data.get('action_gateway_sandbox_verdict')}"
    )


# ── Test 3 : /api/runtime-wiring/os-map/query expose P54 ─────────────────────

def test_os_map_query_exposes_p54(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "envoie un mail maintenant"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "action_gateway_sandbox_status" in data, (
        "os-map/query must return action_gateway_sandbox_status"
    )


# ── Test 4 : action_request_blocked == True ───────────────────────────────────

def test_action_request_blocked_true(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "lance une transaction blockchain"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("world_action_bus_action_request_blocked") is True


# ── Test 5 : can_emit_act == False ────────────────────────────────────────────

def test_can_emit_act_false(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "envoie un mail maintenant"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("action_gateway_can_emit_act") is False


# ── Test 6 : real_action_enabled == False ─────────────────────────────────────

def test_real_action_enabled_false(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "lance une transaction blockchain"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("action_gateway_real_action_enabled") is False


# ── Test 7 : KX108_ONLY ───────────────────────────────────────────────────────

def test_kx108_only(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "envoie un mail maintenant"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("brody_kx108_only") is True
