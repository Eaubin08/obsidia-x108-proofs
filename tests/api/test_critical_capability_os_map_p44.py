"""P44 — Tests API OS Map : routage des 5 gaps critiques via /api/runtime-wiring/os-map/query.

Vérifie :
1.  Query atlas → ATLAS_CONTEXT_LOOKUP dans os-map/query.
2.  Query timeverse → EXTERNAL_SIGNALS_CONTEXT dans os-map/query.
3.  Query brody → BRODY_CHAT_ENTRYPOINT et /api/brody/chat dans os-map/query.
4.  Query graphiti → GRAPHITI_READONLY_CONTEXT et graphiti_v20_readonly_client.
5.  Query os-trad route → OS_TRAD_ROUTE_CONTEXT dans os-map/query.
6.  ACTION_REQUEST_BLOCKED pour "envoie un mail".
7.  No ACT / no write / no mutation sur tous les retours.
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
    """Vérifie que tous les flags boundary sont False."""
    for key in _BOUNDARY_KEYS:
        assert data.get(key) is False, (
            f"VIOLATION: {key}=True {label}"
        )
    assert data.get("decision_authority") == "KX108_ONLY", (
        f"VIOLATION: decision_authority != KX108_ONLY {label}"
    )
    assert data.get("runtime_allowed_now") is False, (
        f"VIOLATION: runtime_allowed_now=True {label}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 — Query atlas → ATLAS_CONTEXT_LOOKUP
# ─────────────────────────────────────────────────────────────────────────────

def test_os_map_atlas_query_selects_atlas_context():
    """P44 API: os-map/query 'atlas component map' → ATLAS_CONTEXT_LOOKUP."""
    r = client.post("/api/runtime-wiring/os-map/query", json={
        "query": "atlas component map",
        "max_paths": 5,
    })
    assert r.status_code == 200
    data = r.json()

    _assert_boundary_safe(data, "atlas query")

    selected = data.get("selected_runtime_path", {})
    cap_chain = selected.get("capability_chain", [])
    adapters = data.get("selected_adapters", [])

    assert "ATLAS_CONTEXT_LOOKUP" in cap_chain, (
        f"P44: ATLAS_CONTEXT_LOOKUP non sélectionné, cap_chain={cap_chain}"
    )
    assert "atlas_to_context_packet" in adapters, (
        f"P44: atlas_to_context_packet absent, adapters={adapters}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 — Query timeverse → EXTERNAL_SIGNALS_CONTEXT
# ─────────────────────────────────────────────────────────────────────────────

def test_os_map_timeverse_query_selects_external_signals():
    """P44 API: os-map/query 'timeverse temporal signal' → EXTERNAL_SIGNALS_CONTEXT."""
    r = client.post("/api/runtime-wiring/os-map/query", json={
        "query": "timeverse temporal signal",
        "max_paths": 5,
    })
    assert r.status_code == 200
    data = r.json()

    _assert_boundary_safe(data, "timeverse query")

    selected = data.get("selected_runtime_path", {})
    cap_chain = selected.get("capability_chain", [])

    assert "EXTERNAL_SIGNALS_CONTEXT" in cap_chain, (
        f"P44: EXTERNAL_SIGNALS_CONTEXT non sélectionné, cap_chain={cap_chain}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 — Query brody → BRODY_CHAT_ENTRYPOINT + /api/brody/chat
# ─────────────────────────────────────────────────────────────────────────────

def test_os_map_brody_query_selects_brody_chat_entrypoint():
    """P44 API: os-map/query 'brody chat true voice' → BRODY_CHAT_ENTRYPOINT."""
    r = client.post("/api/runtime-wiring/os-map/query", json={
        "query": "brody chat true voice",
        "max_paths": 5,
    })
    assert r.status_code == 200
    data = r.json()

    _assert_boundary_safe(data, "brody query")

    selected = data.get("selected_runtime_path", {})
    cap_chain = selected.get("capability_chain", [])
    routes = data.get("selected_routes", [])

    assert "BRODY_CHAT_ENTRYPOINT" in cap_chain, (
        f"P44: BRODY_CHAT_ENTRYPOINT non sélectionné, cap_chain={cap_chain}"
    )
    assert "/api/brody/chat" in routes, (
        f"P44: /api/brody/chat absent de routes={routes}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 — Query graphiti → GRAPHITI_READONLY_CONTEXT + graphiti_v20_readonly_client
# ─────────────────────────────────────────────────────────────────────────────

def test_os_map_legacy_provider_query_cannot_select_provider_runtime():
    r = client.post(
        "/api/runtime-wiring/os-map/query",
        json={
            "query":
                "graphiti v20 readonly client",
            "max_paths": 5,
        },
    )

    assert r.status_code == 200

    data = r.json()

    _assert_boundary_safe(
        data,
        "legacy provider query",
    )

    selected = data.get(
        "selected_runtime_path",
        {},
    )

    cap_chain = selected.get(
        "capability_chain",
        [],
    )

    modules = data.get(
        "selected_modules",
        [],
    )

    assert (
        "GRAPHITI_READONLY_CONTEXT"
        not in cap_chain
    )

    assert (
        "graphiti_v20_readonly_client"
        not in modules
    )




# ─────────────────────────────────────────────────────────────────────────────
# Test 5 — Query os-trad route → OS_TRAD_ROUTE_CONTEXT
# ─────────────────────────────────────────────────────────────────────────────

def test_os_map_os_trad_route_query_selects_os_trad_route_context():
    """P44 API: os-map/query 'os-trad route translate endpoint' → OS_TRAD_ROUTE_CONTEXT."""
    r = client.post("/api/runtime-wiring/os-map/query", json={
        "query": "os-trad route translate endpoint",
        "max_paths": 5,
    })
    assert r.status_code == 200
    data = r.json()

    _assert_boundary_safe(data, "os-trad route query")

    selected = data.get("selected_runtime_path", {})
    cap_chain = selected.get("capability_chain", [])
    routes = data.get("selected_routes", [])

    assert "OS_TRAD_ROUTE_CONTEXT" in cap_chain, (
        f"P44: OS_TRAD_ROUTE_CONTEXT non sélectionné, cap_chain={cap_chain}"
    )
    assert any("os-trad" in r for r in routes), (
        f"P44: aucune route os-trad, routes={routes}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 6 — ACTION_REQUEST_BLOCKED pour "envoie un mail"
# ─────────────────────────────────────────────────────────────────────────────

def test_os_map_action_request_blocked():
    """P44 API: ACTION_REQUEST_BLOCKED pour query action — invariant P36 maintenu."""
    r = client.post("/api/runtime-wiring/os-map/query", json={
        "query": "envoie un mail à l'équipe",
        "max_paths": 5,
    })
    assert r.status_code == 200
    data = r.json()

    _assert_boundary_safe(data, "action request")
    assert data.get("action_blocked") is True, (
        "P44: action_blocked doit être True pour une requête d'action"
    )
    assert data.get("os_map_status") == "ACTION_BLOCKED"


# ─────────────────────────────────────────────────────────────────────────────
# Test 7 — No ACT / no write / no mutation sur tous les retours
# ─────────────────────────────────────────────────────────────────────────────

def test_os_map_all_new_queries_no_act():
    """P44 API: tous les nouveaux paths sont readonly, no ACT, KX108_ONLY."""
    queries = [
        "atlas component map",
        "timeverse temporal signal",
        "brody chat true voice",
        "graphiti v20 readonly client",
        "os-trad route translate endpoint",
    ]
    for query in queries:
        r = client.post("/api/runtime-wiring/os-map/query", json={
            "query": query,
            "max_paths": 5,
        })
        assert r.status_code == 200
        _assert_boundary_safe(r.json(), f"query={query!r}")
