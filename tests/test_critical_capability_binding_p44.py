"""P44 — Tests unitaires : liaison des 5 gaps critiques au capability router.

Vérifie :
1.  ATLAS_CONTEXT_LOOKUP existe dans la taxonomie.
2.  EXTERNAL_SIGNALS_CONTEXT existe.
3.  BRODY_CHAT_ENTRYPOINT existe.
4.  GRAPHITI_READONLY_CONTEXT est relié à graphiti_v20_readonly_client.
5.  OS_TRAD_ROUTE_CONTEXT existe.
6.  Query atlas sélectionne ATLAS_CONTEXT_LOOKUP et atlas_to_context_packet.
7.  Query timeverse sélectionne EXTERNAL_SIGNALS_CONTEXT.
8.  Query brody sélectionne BRODY_CHAT_ENTRYPOINT et /api/brody/chat.
9.  Query graphiti sélectionne GRAPHITI_READONLY_CONTEXT.
10. Query os-trad route sélectionne OS_TRAD_ROUTE_CONTEXT.
11. Aucun selected_path runtime_allowed_now=True.
12. Aucun selected_path emits_act=True.
13. decision_authority=KX108_ONLY partout.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from runtime_wiring.source_runtime.capability_taxonomy import (
    CAPABILITY_TAXONOMY,
    list_capability_ids,
)
from runtime_wiring.source_runtime.capability_path_router import (
    _CAPABILITY_PATH_TEMPLATES,
    route_capability_path,
)


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 — ATLAS_CONTEXT_LOOKUP existe
# ─────────────────────────────────────────────────────────────────────────────

def test_atlas_context_lookup_in_taxonomy():
    """P44: ATLAS_CONTEXT_LOOKUP déclaré dans la taxonomie."""
    assert "ATLAS_CONTEXT_LOOKUP" in CAPABILITY_TAXONOMY
    cap = CAPABILITY_TAXONOMY["ATLAS_CONTEXT_LOOKUP"]
    assert cap["runtime_allowed_now"] is False
    assert cap["emits_act"] is False
    assert cap["decision_authority"] == "KX108_ONLY"
    assert "ATLAS" in cap["candidate_source_families"]
    assert "atlas_to_context_packet" in cap["candidate_adapters"]


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 — EXTERNAL_SIGNALS_CONTEXT existe
# ─────────────────────────────────────────────────────────────────────────────

def test_external_signals_context_in_taxonomy():
    """P44: EXTERNAL_SIGNALS_CONTEXT déclaré dans la taxonomie."""
    assert "EXTERNAL_SIGNALS_CONTEXT" in CAPABILITY_TAXONOMY
    cap = CAPABILITY_TAXONOMY["EXTERNAL_SIGNALS_CONTEXT"]
    assert cap["runtime_allowed_now"] is False
    assert cap["emits_act"] is False
    assert cap["decision_authority"] == "KX108_ONLY"
    assert "EXTERNAL_SIGNALS" in cap["candidate_source_families"]
    assert "external_signals_to_context_packet" in cap["candidate_adapters"]


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 — BRODY_CHAT_ENTRYPOINT existe
# ─────────────────────────────────────────────────────────────────────────────

def test_brody_chat_entrypoint_in_taxonomy():
    """P44: BRODY_CHAT_ENTRYPOINT déclaré dans la taxonomie."""
    assert "BRODY_CHAT_ENTRYPOINT" in CAPABILITY_TAXONOMY
    cap = CAPABILITY_TAXONOMY["BRODY_CHAT_ENTRYPOINT"]
    assert cap["runtime_allowed_now"] is False
    assert cap["emits_act"] is False
    assert cap["decision_authority"] == "KX108_ONLY"
    assert "/api/brody/chat" in cap["candidate_routes"]


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 — GRAPHITI_READONLY_CONTEXT relié à graphiti_v20_readonly_client
# ─────────────────────────────────────────────────────────────────────────────

def test_legacy_provider_capability_is_catalog_only_during_cutover():
    assert (
        "GRAPHITI_READONLY_CONTEXT"
        in CAPABILITY_TAXONOMY
    )

    assert (
        "GRAPHITI_READONLY_CONTEXT"
        not in _CAPABILITY_PATH_TEMPLATES
    )




# ─────────────────────────────────────────────────────────────────────────────
# Test 5 — OS_TRAD_ROUTE_CONTEXT existe
# ─────────────────────────────────────────────────────────────────────────────

def test_os_trad_route_context_in_taxonomy():
    """P44: OS_TRAD_ROUTE_CONTEXT déclaré dans la taxonomie."""
    assert "OS_TRAD_ROUTE_CONTEXT" in CAPABILITY_TAXONOMY
    cap = CAPABILITY_TAXONOMY["OS_TRAD_ROUTE_CONTEXT"]
    assert cap["runtime_allowed_now"] is False
    assert cap["emits_act"] is False
    assert cap["decision_authority"] == "KX108_ONLY"
    assert "OS_TRAD_REVERSE_OS" in cap["candidate_source_families"]
    os_trad_routes = cap["candidate_routes"]
    assert any("os-trad" in r for r in os_trad_routes), (
        f"P44: aucune route os-trad dans candidate_routes: {os_trad_routes}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 6 — Query atlas → ATLAS_CONTEXT_LOOKUP + atlas_to_context_packet
# ─────────────────────────────────────────────────────────────────────────────

def test_atlas_query_selects_atlas_capability():
    """P44: query 'atlas component map' sélectionne ATLAS_CONTEXT_LOOKUP."""
    result = route_capability_path(query="atlas component map", max_paths=5)
    selected = result["selected_path"]
    cap_chain = selected.get("capability_chain", [])
    adapters = selected.get("adapters", [])

    assert "ATLAS_CONTEXT_LOOKUP" in cap_chain, (
        f"P44: ATLAS_CONTEXT_LOOKUP non sélectionné, cap_chain={cap_chain}"
    )
    assert "atlas_to_context_packet" in adapters, (
        f"P44: atlas_to_context_packet absent, adapters={adapters}"
    )
    assert selected.get("runtime_allowed_now") is False
    assert selected.get("emits_act") is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 7 — Query timeverse → EXTERNAL_SIGNALS_CONTEXT
# ─────────────────────────────────────────────────────────────────────────────

def test_timeverse_query_selects_external_signals():
    """P44: query 'timeverse temporal signal' sélectionne EXTERNAL_SIGNALS_CONTEXT."""
    result = route_capability_path(query="timeverse temporal signal", max_paths=5)
    selected = result["selected_path"]
    cap_chain = selected.get("capability_chain", [])

    assert "EXTERNAL_SIGNALS_CONTEXT" in cap_chain, (
        f"P44: EXTERNAL_SIGNALS_CONTEXT non sélectionné, cap_chain={cap_chain}"
    )
    assert "external_signals_to_context_packet" in selected.get("adapters", [])
    assert selected.get("runtime_allowed_now") is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 8 — Query brody → BRODY_CHAT_ENTRYPOINT + /api/brody/chat
# ─────────────────────────────────────────────────────────────────────────────

def test_brody_query_selects_brody_chat_entrypoint():
    """P44: query 'brody chat true voice' sélectionne BRODY_CHAT_ENTRYPOINT."""
    result = route_capability_path(query="brody chat true voice", max_paths=5)
    selected = result["selected_path"]
    cap_chain = selected.get("capability_chain", [])
    routes = selected.get("routes", [])

    assert "BRODY_CHAT_ENTRYPOINT" in cap_chain, (
        f"P44: BRODY_CHAT_ENTRYPOINT non sélectionné, cap_chain={cap_chain}"
    )
    assert "/api/brody/chat" in routes, (
        f"P44: /api/brody/chat absent de routes={routes}"
    )
    assert selected.get("runtime_allowed_now") is False
    assert selected.get("emits_act") is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 9 — Query graphiti → GRAPHITI_READONLY_CONTEXT
# ─────────────────────────────────────────────────────────────────────────────

def test_legacy_provider_query_cannot_select_provider_runtime():
    result = route_capability_path(
        query="graphiti v20 readonly client",
        max_paths=5,
    )

    selected = result[
        "selected_path"
    ]

    cap_chain = selected.get(
        "capability_chain",
        [],
    )

    modules = selected.get(
        "modules",
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

    assert (
        selected.get(
            "runtime_allowed_now"
        )
        is False
    )

    assert (
        selected.get(
            "emits_act"
        )
        is False
    )

    assert (
        selected.get(
            "decision_authority"
        )
        == "KX108_ONLY"
    )




# ─────────────────────────────────────────────────────────────────────────────
# Test 10 — Query os-trad route → OS_TRAD_ROUTE_CONTEXT
# ─────────────────────────────────────────────────────────────────────────────

def test_os_trad_route_query_selects_os_trad_route_context():
    """P44: query 'os-trad route translate endpoint' sélectionne OS_TRAD_ROUTE_CONTEXT."""
    result = route_capability_path(query="os-trad route translate endpoint", max_paths=5)
    selected = result["selected_path"]
    cap_chain = selected.get("capability_chain", [])
    routes = selected.get("routes", [])

    assert "OS_TRAD_ROUTE_CONTEXT" in cap_chain, (
        f"P44: OS_TRAD_ROUTE_CONTEXT non sélectionné, cap_chain={cap_chain}"
    )
    assert any("os-trad" in r for r in routes), (
        f"P44: aucune route os-trad, routes={routes}"
    )
    assert selected.get("runtime_allowed_now") is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 11 — Aucun selected_path runtime_allowed_now=True
# ─────────────────────────────────────────────────────────────────────────────

def test_no_selected_path_runtime_allowed_now():
    """P44: aucun chemin sélectionné n'active runtime_allowed_now."""
    new_capability_queries = [
        "atlas component map",
        "timeverse temporal signal",
        "brody chat true voice",
        "graphiti v20 readonly client",
        "os-trad route translate endpoint",
    ]
    for query in new_capability_queries:
        result = route_capability_path(query=query, max_paths=5)
        selected = result["selected_path"]
        assert selected.get("runtime_allowed_now") is False, (
            f"VIOLATION: runtime_allowed_now=True pour query={query!r}"
        )
        for path in result.get("ranked_runtime_paths", []):
            assert path.get("runtime_allowed_now") is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 12 — Aucun selected_path emits_act=True
# ─────────────────────────────────────────────────────────────────────────────

def test_no_selected_path_emits_act():
    """P44: aucun chemin sélectionné n'émet ACT."""
    new_capability_queries = [
        "atlas component map",
        "timeverse temporal signal",
        "brody chat true voice",
        "graphiti v20 readonly client",
        "os-trad route translate endpoint",
    ]
    for query in new_capability_queries:
        result = route_capability_path(query=query, max_paths=5)
        selected = result["selected_path"]
        assert selected.get("emits_act") is False, (
            f"VIOLATION: emits_act=True pour query={query!r}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Test 13 — decision_authority=KX108_ONLY partout
# ─────────────────────────────────────────────────────────────────────────────

def test_decision_authority_kx108_only_new_capabilities():
    """P44: decision_authority=KX108_ONLY dans toutes les nouvelles capabilities."""
    new_caps = [
        "ATLAS_CONTEXT_LOOKUP",
        "EXTERNAL_SIGNALS_CONTEXT",
        "BRODY_CHAT_ENTRYPOINT",
        "OS_TRAD_ROUTE_CONTEXT",
    ]
    for cap_id in new_caps:
        cap = CAPABILITY_TAXONOMY[cap_id]
        assert cap["decision_authority"] == "KX108_ONLY", (
            f"VIOLATION: decision_authority != KX108_ONLY pour {cap_id}"
        )
        tmpl = _CAPABILITY_PATH_TEMPLATES.get(cap_id, {})
        assert tmpl.get("decision_authority", "KX108_ONLY") == "KX108_ONLY"
