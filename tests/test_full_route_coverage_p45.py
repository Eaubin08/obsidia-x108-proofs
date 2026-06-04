"""P45 — Tests unitaires : couverture complète des routes API.

Vérifie :
1.  L'inventaire brut P45 existe.
2.  La carte de couverture complète P45 existe.
3.  Toutes les routes ont une classification.
4.  unclassified_routes_count == 0.
5.  coverage_percent == 100.
6.  /api/brody/chat est BRODY_CHAT_ENTRYPOINT.
7.  /api/runtime-wiring/os-map/query est CONNECTED_READONLY.
8.  Routes actionnelles n'ont jamais runtime_allowed_now=True.
9.  Routes actionnelles n'ont jamais emits_act=True.
10. decision_authority=KX108_ONLY partout.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_INVENTORY_PATH = _REPO_ROOT / "_runtime_wiring_preflight" / "P45_ROUTE_INVENTORY_RAW.json"
_MAP_PATH = _REPO_ROOT / "_runtime_wiring_preflight" / "P45_FULL_ROUTE_COVERAGE_MAP.json"


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 — L'inventaire brut existe
# ─────────────────────────────────────────────────────────────────────────────

def test_p45_route_inventory_exists():
    """P45: P45_ROUTE_INVENTORY_RAW.json existe et contient des routes."""
    assert _INVENTORY_PATH.is_file(), f"P45 inventory absent: {_INVENTORY_PATH}"
    data = json.loads(_INVENTORY_PATH.read_text(encoding="utf-8"))
    assert data["total"] > 0, "Inventaire vide"
    assert len(data["routes"]) == data["total"]


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 — La carte de couverture existe
# ─────────────────────────────────────────────────────────────────────────────

def test_p45_coverage_map_exists():
    """P45: P45_FULL_ROUTE_COVERAGE_MAP.json existe et est valide."""
    assert _MAP_PATH.is_file(), f"P45 coverage map absent: {_MAP_PATH}"
    data = json.loads(_MAP_PATH.read_text(encoding="utf-8"))
    assert "route_map" in data
    assert "coverage_percent" in data
    assert "coverage_counts" in data


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 — Toutes les routes ont une classification
# ─────────────────────────────────────────────────────────────────────────────

def test_all_routes_have_classification():
    """P45: aucune route UNCLASSIFIED dans la carte."""
    from runtime_wiring.source_runtime.route_capability_map import build_route_capability_map
    coverage = build_route_capability_map(force_rebuild=True)
    route_map = coverage["route_map"]

    unclassified = [
        path for path, data in route_map.items()
        if data.get("coverage_status") == "UNCLASSIFIED"
    ]
    assert not unclassified, (
        f"P45: {len(unclassified)} routes UNCLASSIFIED détectées: {unclassified[:5]}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 — unclassified_count == 0
# ─────────────────────────────────────────────────────────────────────────────

def test_unclassified_count_zero():
    """P45: unclassified_routes_count == 0."""
    from runtime_wiring.source_runtime.route_capability_map import build_route_capability_map
    coverage = build_route_capability_map()
    assert coverage["unclassified_count"] == 0, (
        f"P45: unclassified_count={coverage['unclassified_count']}, "
        f"routes={coverage['unclassified_routes']}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 5 — coverage_percent == 100
# ─────────────────────────────────────────────────────────────────────────────

def test_coverage_percent_100():
    """P45: coverage_percent == 100.0."""
    from runtime_wiring.source_runtime.route_capability_map import build_route_capability_map
    coverage = build_route_capability_map()
    assert coverage["coverage_percent"] == 100.0, (
        f"P45: coverage_percent={coverage['coverage_percent']} (attendu 100.0)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 6 — /api/brody/chat est BRODY_CHAT_ENTRYPOINT
# ─────────────────────────────────────────────────────────────────────────────

def test_brody_chat_classified_as_brody_entrypoint():
    """P45: /api/brody/chat → CONNECTED_READONLY + BRODY_CHAT_ENTRYPOINT."""
    from runtime_wiring.source_runtime.route_capability_map import get_route_classification
    cls = get_route_classification("/api/brody/chat")
    assert cls["coverage_status"] == "CONNECTED_READONLY", (
        f"P45: /api/brody/chat status={cls['coverage_status']}"
    )
    assert cls["capability"] == "BRODY_CHAT_ENTRYPOINT", (
        f"P45: /api/brody/chat capability={cls['capability']}"
    )
    assert cls["runtime_allowed_now"] is False
    assert cls["emits_act"] is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 7 — /api/runtime-wiring/os-map/query est CONNECTED_READONLY
# ─────────────────────────────────────────────────────────────────────────────

def test_os_map_query_route_connected_readonly():
    """P45: /api/runtime-wiring/os-map/query → CONNECTED_READONLY."""
    from runtime_wiring.source_runtime.route_capability_map import get_route_classification
    cls = get_route_classification("/api/runtime-wiring/os-map/query")
    assert cls["coverage_status"] == "CONNECTED_READONLY", (
        f"P45: os-map/query status={cls['coverage_status']}"
    )
    assert cls["runtime_allowed_now"] is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 8 — Routes actionnelles : runtime_allowed_now=False
# ─────────────────────────────────────────────────────────────────────────────

def test_action_routes_no_runtime_allowed():
    """P45: routes CONNECTED_BLOCKED_ACTION n'activent jamais runtime_allowed_now."""
    from runtime_wiring.source_runtime.route_capability_map import build_route_capability_map
    coverage = build_route_capability_map()
    for path, data in coverage["route_map"].items():
        if data.get("coverage_status") == "CONNECTED_BLOCKED_ACTION":
            assert data.get("runtime_allowed_now") is False, (
                f"VIOLATION: runtime_allowed_now=True sur route action {path}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Test 9 — Routes actionnelles : emits_act=False
# ─────────────────────────────────────────────────────────────────────────────

def test_action_routes_no_emits_act():
    """P45: routes CONNECTED_BLOCKED_ACTION n'émettent jamais ACT."""
    from runtime_wiring.source_runtime.route_capability_map import build_route_capability_map
    coverage = build_route_capability_map()
    for path, data in coverage["route_map"].items():
        if data.get("coverage_status") == "CONNECTED_BLOCKED_ACTION":
            assert data.get("emits_act") is False, (
                f"VIOLATION: emits_act=True sur route action {path}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Test 10 — decision_authority=KX108_ONLY partout
# ─────────────────────────────────────────────────────────────────────────────

def test_all_routes_kx108_only():
    """P45: decision_authority=KX108_ONLY sur toutes les routes classifiées."""
    from runtime_wiring.source_runtime.route_capability_map import build_route_capability_map
    coverage = build_route_capability_map()
    violations = []
    for path, data in coverage["route_map"].items():
        if data.get("decision_authority") != "KX108_ONLY":
            violations.append(path)
    assert not violations, (
        f"VIOLATION: decision_authority != KX108_ONLY sur {len(violations)} routes: {violations[:5]}"
    )
