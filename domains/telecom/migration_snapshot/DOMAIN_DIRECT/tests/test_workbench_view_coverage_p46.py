"""
P46 — Tests unitaires : couverture des vues Workbench.
Vérifie que toutes les vues sont classifiées, qu'aucune n'est UNCLASSIFIED,
et que les vues actionnelles sont bien bloquées.
NO ACT. NO write. READONLY.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
INVENTORY_PATH = ROOT / "_runtime_wiring_preflight" / "P46_WORKBENCH_VIEW_INVENTORY_RAW.json"
COVERAGE_MAP_PATH = ROOT / "_runtime_wiring_preflight" / "P46_WORKBENCH_VIEW_COVERAGE_MAP.json"
VIEWS_DIR = ROOT / "apps" / "obsidia-workbench" / "src" / "views"

EXPECTED_VIEWS = {
    "AuditView.tsx",
    "BlockchainView.tsx",
    "ChatView.tsx",
    "GencoinView.tsx",
    "GraphitiView.tsx",
    "MemoryView.tsx",
    "OS3View.tsx",
    "OSMapView.tsx",
    "RuntimeWiringPreviewView.tsx",
    "SettingsView.tsx",
    "TranslationView.tsx",
    "WorldCallView.tsx",
    "X108View.tsx",
}

ACTION_VIEWS = {"BlockchainView.tsx", "GencoinView.tsx", "WorldCallView.tsx"}


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def inventory():
    assert INVENTORY_PATH.exists(), f"Inventory missing: {INVENTORY_PATH}"
    return json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def coverage_map():
    assert COVERAGE_MAP_PATH.exists(), f"Coverage map missing: {COVERAGE_MAP_PATH}"
    return json.loads(COVERAGE_MAP_PATH.read_text(encoding="utf-8"))


# ── Test 1 : raw inventory existe ─────────────────────────────────────────────

def test_raw_inventory_exists():
    assert INVENTORY_PATH.exists(), "P46_WORKBENCH_VIEW_INVENTORY_RAW.json must exist"


# ── Test 2 : coverage map existe ──────────────────────────────────────────────

def test_coverage_map_exists():
    assert COVERAGE_MAP_PATH.exists(), "P46_WORKBENCH_VIEW_COVERAGE_MAP.json must exist"


# ── Test 3 : toutes les vues ont une classification ───────────────────────────

def test_all_views_have_classification(coverage_map):
    view_map = coverage_map.get("view_map", {})
    assert len(view_map) > 0, "view_map must not be empty"
    for view_file, entry in view_map.items():
        status = entry.get("coverage_status", "")
        assert status, f"{view_file} has no coverage_status"
        assert status != "UNCLASSIFIED", f"{view_file} is UNCLASSIFIED — P46 requires 100% coverage"


# ── Test 4 : unclassified_views_count == 0 ────────────────────────────────────

def test_unclassified_views_count_is_zero(coverage_map):
    count = coverage_map.get("unclassified_views_count", -1)
    assert count == 0, f"unclassified_views_count must be 0, got {count}"


# ── Test 5 : workbench_views_coverage_percent == 100 ─────────────────────────

def test_workbench_views_coverage_percent_is_100(coverage_map):
    pct = coverage_map.get("workbench_views_coverage_percent", 0.0)
    assert pct == 100.0, f"workbench_views_coverage_percent must be 100.0, got {pct}"


# ── Test 6 : OSMapView est CONNECTED_TO_OS_MAP ───────────────────────────────

def test_osmap_view_connected_to_os_map(coverage_map):
    view_map = coverage_map.get("view_map", {})
    entry = view_map.get("OSMapView.tsx", {})
    assert entry.get("coverage_status") == "CONNECTED_TO_OS_MAP", (
        f"OSMapView.tsx must be CONNECTED_TO_OS_MAP, got {entry.get('coverage_status')}"
    )


# ── Test 7 : ChatView est CONNECTED_TO_RUNTIME ou CONNECTED_TO_WORKBENCH_ONLY ─

def test_chat_view_classification(coverage_map):
    view_map = coverage_map.get("view_map", {})
    entry = view_map.get("ChatView.tsx", {})
    allowed = {"CONNECTED_TO_RUNTIME", "CONNECTED_TO_WORKBENCH_ONLY"}
    assert entry.get("coverage_status") in allowed, (
        f"ChatView.tsx must be in {allowed}, got {entry.get('coverage_status')}"
    )


# ── Test 8 : vues actionnelles ne sont jamais runtime_allowed_now=True ────────

def test_action_views_runtime_not_allowed(coverage_map):
    view_map = coverage_map.get("view_map", {})
    for view_file in ACTION_VIEWS:
        entry = view_map.get(view_file, {})
        assert entry.get("runtime_allowed_now") is False, (
            f"{view_file}: runtime_allowed_now must be False"
        )


# ── Test 9 : vues actionnelles ne sont jamais emits_act=True ─────────────────

def test_action_views_emits_act_false(coverage_map):
    view_map = coverage_map.get("view_map", {})
    for view_file in ACTION_VIEWS:
        entry = view_map.get(view_file, {})
        assert entry.get("emits_act") is False, (
            f"{view_file}: emits_act must be False"
        )


# ── Test 10 : decision_authority=KX108_ONLY partout ──────────────────────────

def test_decision_authority_kx108_only_everywhere(coverage_map):
    view_map = coverage_map.get("view_map", {})
    for view_file, entry in view_map.items():
        da = entry.get("decision_authority", "")
        assert da == "KX108_ONLY", (
            f"{view_file}: decision_authority must be KX108_ONLY, got {da}"
        )


# ── Tests supplémentaires ─────────────────────────────────────────────────────

def test_all_expected_views_in_map(coverage_map):
    view_map = coverage_map.get("view_map", {})
    for expected in EXPECTED_VIEWS:
        assert expected in view_map, f"{expected} missing from P46 coverage map"


def test_inventory_view_count(inventory):
    views = inventory.get("views", [])
    assert len(views) == 13, f"Expected 13 views in inventory, got {len(views)}"


def test_coverage_map_status_ready(coverage_map):
    assert coverage_map.get("map_status") == "READY"


def test_no_act_no_write_invariants(coverage_map):
    assert coverage_map.get("runtime_allowed_now") is False
    assert coverage_map.get("emits_act") is False
    assert coverage_map.get("decision_authority") == "KX108_ONLY"


def test_classifier_import():
    from runtime_wiring.source_runtime.workbench_view_coverage_classifier import (
        classify_workbench_view,
        get_coverage_summary,
    )
    assert callable(classify_workbench_view)
    assert callable(get_coverage_summary)


def test_capability_map_import():
    from runtime_wiring.source_runtime.workbench_view_capability_map import (
        get_view_capability_map,
        build_workbench_coverage_summary,
    )
    cap_map = get_view_capability_map()
    assert len(cap_map) == 13
    summary = build_workbench_coverage_summary()
    assert summary["unclassified_views_count"] == 0
    assert summary["workbench_views_coverage_percent"] == 100.0


def test_classifier_osmap_view():
    from runtime_wiring.source_runtime.workbench_view_coverage_classifier import classify_workbench_view
    view = {
        "file": "OSMapView.tsx",
        "backend_endpoints": ["/api/runtime-wiring/os-map/query"],
        "runtime_family": "CAPABILITY_PATH_ROUTER",
        "status": "connected",
    }
    assert classify_workbench_view(view) == "CONNECTED_TO_OS_MAP"


def test_classifier_blockchain_blocked():
    from runtime_wiring.source_runtime.workbench_view_coverage_classifier import classify_workbench_view
    view = {
        "file": "BlockchainView.tsx",
        "backend_endpoints": [],
        "runtime_family": "BLOCKCHAIN_GATE",
        "status": "mock_only",
    }
    assert classify_workbench_view(view) == "BLOCKED_ACTION_VIEW"
