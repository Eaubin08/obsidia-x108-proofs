"""P45 — Tests API : couverture des routes via /api/runtime-wiring/os-map/query.

Vérifie :
1.  os-map/query retourne route_coverage_status.
2.  Query brody retourne /api/brody/chat classée CONNECTED_READONLY.
3.  Query action retourne ACTION_BLOCKED.
4.  unclassified_routes_count = 0.
5.  route_coverage_percent = 100.
6.  No ACT / no write / no mutation.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app)

_BOUNDARY_KEYS = ("emits_act", "memory_write", "graph_write", "kernel_mutation", "zip_extraction")


def _assert_boundary_safe(data: dict, label: str = "") -> None:
    for key in _BOUNDARY_KEYS:
        assert data.get(key) is False, f"VIOLATION: {key}=True {label}"
    assert data.get("decision_authority") == "KX108_ONLY", f"VIOLATION: decision_authority {label}"
    assert data.get("runtime_allowed_now") is False, f"VIOLATION: runtime_allowed_now=True {label}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 — os-map/query retourne route_coverage_status
# ─────────────────────────────────────────────────────────────────────────────

def test_os_map_query_returns_route_coverage_status():
    """P45 API: os-map/query inclut route_coverage_status."""
    r = client.post("/api/runtime-wiring/os-map/query", json={
        "query": "atlas component map",
        "max_paths": 3,
    })
    assert r.status_code == 200
    data = r.json()
    assert "route_coverage_status" in data, "P45: route_coverage_status absent"
    assert "route_coverage_percent" in data, "P45: route_coverage_percent absent"
    assert "unclassified_routes_count" in data, "P45: unclassified_routes_count absent"
    _assert_boundary_safe(data, "coverage status check")


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 — Query brody → /api/brody/chat classée CONNECTED_READONLY
# ─────────────────────────────────────────────────────────────────────────────

def test_os_map_brody_query_shows_chat_route_classified():
    """P45 API: query brody retourne /api/brody/chat dans selected_routes_classified."""
    r = client.post("/api/runtime-wiring/os-map/query", json={
        "query": "brody chat true voice",
        "max_paths": 3,
    })
    assert r.status_code == 200
    data = r.json()
    _assert_boundary_safe(data, "brody chat route")

    # /api/brody/chat doit être dans selected_routes
    selected_routes = data.get("selected_routes", [])
    assert "/api/brody/chat" in selected_routes, (
        f"P45: /api/brody/chat absent de selected_routes={selected_routes}"
    )

    # selected_routes_classified doit montrer CONNECTED_READONLY
    classified = data.get("selected_routes_classified", [])
    if classified:
        brody_entry = next((c for c in classified if c.get("path") == "/api/brody/chat"), None)
        if brody_entry:
            assert brody_entry.get("coverage_status") == "CONNECTED_READONLY", (
                f"P45: /api/brody/chat coverage_status={brody_entry.get('coverage_status')}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 — Query action → ACTION_BLOCKED
# ─────────────────────────────────────────────────────────────────────────────

def test_os_map_action_query_blocked():
    """P45 API: query action → ACTION_BLOCKED invariant maintenu."""
    r = client.post("/api/runtime-wiring/os-map/query", json={
        "query": "envoie un mail à l'équipe",
        "max_paths": 3,
    })
    assert r.status_code == 200
    data = r.json()
    _assert_boundary_safe(data, "action query")
    assert data.get("action_blocked") is True
    assert data.get("os_map_status") == "ACTION_BLOCKED"


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 — unclassified_routes_count = 0
# ─────────────────────────────────────────────────────────────────────────────

def test_os_map_unclassified_routes_count_zero():
    """P45 API: unclassified_routes_count = 0 dans os-map/query."""
    r = client.post("/api/runtime-wiring/os-map/query", json={
        "query": "atlas component map",
        "max_paths": 3,
    })
    assert r.status_code == 200
    data = r.json()
    count = data.get("unclassified_routes_count", -1)
    assert count == 0, f"P45: unclassified_routes_count={count} (attendu 0)"


# ─────────────────────────────────────────────────────────────────────────────
# Test 5 — route_coverage_percent = 100
# ─────────────────────────────────────────────────────────────────────────────

def test_os_map_route_coverage_percent_100():
    """P45 API: route_coverage_percent = 100.0 dans os-map/query."""
    r = client.post("/api/runtime-wiring/os-map/query", json={
        "query": "atlas component map",
        "max_paths": 3,
    })
    assert r.status_code == 200
    data = r.json()
    pct = data.get("route_coverage_percent", 0)
    assert pct == 100.0, f"P45: route_coverage_percent={pct} (attendu 100.0)"


# ─────────────────────────────────────────────────────────────────────────────
# Test 6 — No ACT / no write / no mutation sur toutes les queries P45
# ─────────────────────────────────────────────────────────────────────────────

def test_os_map_p45_queries_all_safe():
    """P45 API: toutes les queries P45 restent KX108_ONLY, readonly, no ACT."""
    queries = [
        "atlas component map",
        "timeverse temporal signal",
        "brody chat true voice",
        "graphiti v20 readonly client",
        "os-trad route translate endpoint",
        "reverse os 34 arbres",
        "rssi sécurité conformité",
    ]
    for query in queries:
        r = client.post("/api/runtime-wiring/os-map/query", json={
            "query": query,
            "max_paths": 3,
        })
        assert r.status_code == 200
        _assert_boundary_safe(r.json(), f"query={query!r}")
