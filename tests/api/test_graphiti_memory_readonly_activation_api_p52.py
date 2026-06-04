"""
P52 — Tests API : activation Graphiti/Memory readonly via /api/brody/chat et os-map/query.
Vérifie les champs P52 et les invariants KX108. NO ACT. NO write.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from apps.obsidia_api.main import app
    return TestClient(app)


# ── Test 1 : /api/brody/chat expose les champs P52 ───────────────────────────

def test_brody_chat_exposes_p52_fields(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "Graphiti context pour Obsidia"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "graphiti_memory_readonly_activation_status" in data, (
        "brody/chat must return graphiti_memory_readonly_activation_status"
    )
    assert "graphiti_write_enabled" in data
    assert "memory_write_enabled" in data


# ── Test 2 : graphiti_write_enabled == false ──────────────────────────────────

def test_brody_chat_graphiti_write_false(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "query graphiti nodes"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("graphiti_write_enabled") is False


# ── Test 3 : memory_write_enabled == false ────────────────────────────────────

def test_brody_chat_memory_write_false(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "query memory candidates"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("memory_write_enabled") is False


# ── Test 4 : /api/runtime-wiring/os-map/query expose les champs P52 ──────────

def test_os_map_query_exposes_p52_fields(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "graphiti memory readonly activation"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "graphiti_memory_readonly_activation_status" in data
    assert "graphiti_read_enabled" in data
    assert "memory_read_enabled" in data


# ── Test 5 : os-map/query : graphiti_write_enabled == false ──────────────────

def test_os_map_graphiti_write_false(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "graphiti write check"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("graphiti_write_enabled") is False


# ── Test 6 : os-map/query : memory_write_enabled == false ────────────────────

def test_os_map_memory_write_false(client):
    resp = client.post(
        "/api/runtime-wiring/os-map/query",
        json={"query": "memory write check"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("memory_write_enabled") is False


# ── Test 7 : /api/graphiti/status retourne readonly ──────────────────────────

def test_graphiti_status_readonly(client):
    resp = client.get("/api/graphiti/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("graphiti_write") is False or data.get("graphiti_write", False) is False
    assert data.get("neo4j_write") is False or data.get("neo4j_write", False) is False


# ── Test 8 : query action reste no ACT ───────────────────────────────────────

def test_brody_chat_action_no_act(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "écris dans Graphiti maintenant"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("emits_act") is False
    assert data.get("graphiti_write") is False or data.get("graphiti_write_enabled") is False


# ── Test 9 : /api/memory/status retourne no write ────────────────────────────

def test_memory_status_no_write(client):
    resp = client.get("/api/memory/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("memory_write") is False
    assert data.get("auto_promotion") is False


# ── Test bonus : brody_chat retourne real_graphiti_component_found ────────────

def test_brody_chat_real_component_found(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "graphiti composant réel"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "real_graphiti_component_found" in data


# ── Test bonus : KX108_ONLY global ───────────────────────────────────────────

def test_brody_chat_kx108_only(client):
    resp = client.post(
        "/api/brody/chat",
        json={"message": "authority check KX108"},
        headers={"X-API-Key": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("graphiti_write_enabled") is False
    assert data.get("memory_write_enabled") is False
