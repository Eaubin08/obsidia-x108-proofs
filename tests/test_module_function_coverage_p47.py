"""
P47 — Tests unitaires : couverture modules et fonctions.
Vérifie que tous les modules/fonctions sont classifiés, aucun UNCLASSIFIED,
et que les modules actionnels sont bloqués.
NO ACT. NO write. READONLY.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
INVENTORY_PATH = ROOT / "_runtime_wiring_preflight" / "P47_MODULE_FUNCTION_INVENTORY_RAW.json"
COVERAGE_MAP_PATH = ROOT / "_runtime_wiring_preflight" / "P47_MODULE_FUNCTION_COVERAGE_MAP.json"

KEY_CAPABILITY_MODULE = "runtime_wiring/source_runtime/capability_path_router.py"
KEY_CAPABILITY_FN = "runtime_wiring/source_runtime/capability_path_router.py::route_capability_path"
OS_MAP_MODULE = "apps/obsidia_api/routes/os_map.py"
OS_MAP_FN = "apps/obsidia_api/routes/os_map.py::os_map_query"

ACTION_MODULES = {
    "apps/obsidia_api/routes/blockchain.py",
    "apps/obsidia_api/routes/gencoin.py",
    "apps/obsidia_api/routes/worldcalls.py",
}

VALID_STATUSES = {
    "CONNECTED_RUNTIME",
    "CONNECTED_ROUTE_HANDLER",
    "CONNECTED_ADAPTER",
    "CONNECTED_CAPABILITY",
    "CONNECTED_STATUS_ONLY",
    "CONNECTED_TEST_ONLY",
    "CONNECTED_WORKBENCH_SUPPORT",
    "BLOCKED_ACTION_RUNTIME",
    "INTERNAL_HELPER",
    "ARCHIVE_ONLY",
    "DO_NOT_BIND_EXPLICIT",
}


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
    assert INVENTORY_PATH.exists()


# ── Test 2 : coverage map existe ──────────────────────────────────────────────

def test_coverage_map_exists():
    assert COVERAGE_MAP_PATH.exists()


# ── Test 3 : tous les modules ont une classification ──────────────────────────

def test_all_modules_have_classification(inventory):
    mods = inventory.get("modules", [])
    assert len(mods) > 0
    for m in mods:
        status = m.get("coverage_status", "")
        assert status, f"{m.get('module_path')} has no coverage_status"
        assert status in VALID_STATUSES, f"{m.get('module_path')}: invalid status '{status}'"
        assert status != "UNCLASSIFIED", f"{m.get('module_path')} is UNCLASSIFIED"


# ── Test 4 : functions_unclassified_count == 0 ───────────────────────────────

def test_functions_unclassified_count_is_zero(coverage_map):
    count = coverage_map.get("functions_unclassified_count", -1)
    assert count == 0, f"functions_unclassified_count must be 0, got {count}"


# ── Test 5 : modules_unclassified_count == 0 ─────────────────────────────────

def test_modules_unclassified_count_is_zero(coverage_map):
    count = coverage_map.get("modules_unclassified_count", -1)
    assert count == 0, f"modules_unclassified_count must be 0, got {count}"


# ── Test 6 : module_coverage_percent == 100 ──────────────────────────────────

def test_module_coverage_percent_is_100(coverage_map):
    pct = coverage_map.get("module_coverage_percent", 0.0)
    assert pct == 100.0, f"module_coverage_percent must be 100.0, got {pct}"


# ── Test 7 : function_coverage_percent == 100 ────────────────────────────────

def test_function_coverage_percent_is_100(coverage_map):
    pct = coverage_map.get("function_coverage_percent", 0.0)
    assert pct == 100.0, f"function_coverage_percent must be 100.0, got {pct}"


# ── Test 8 : capability_path_router est CONNECTED_CAPABILITY ─────────────────

def test_capability_path_router_module_classification(coverage_map):
    key_mods = coverage_map.get("key_module_classifications", {})
    status = key_mods.get(KEY_CAPABILITY_MODULE, "")
    assert status == "CONNECTED_CAPABILITY", (
        f"{KEY_CAPABILITY_MODULE} must be CONNECTED_CAPABILITY, got '{status}'"
    )


# ── Test 9 : route_capability_path est CONNECTED_CAPABILITY ──────────────────

def test_route_capability_path_function_classification(coverage_map):
    key_fns = coverage_map.get("key_function_classifications", {})
    status = key_fns.get(KEY_CAPABILITY_FN, "")
    assert status == "CONNECTED_CAPABILITY", (
        f"{KEY_CAPABILITY_FN} must be CONNECTED_CAPABILITY, got '{status}'"
    )


# ── Test 10 : os_map.py est CONNECTED_ROUTE_HANDLER ──────────────────────────

def test_os_map_module_is_route_handler(coverage_map):
    key_mods = coverage_map.get("key_module_classifications", {})
    status = key_mods.get(OS_MAP_MODULE, "")
    assert status == "CONNECTED_ROUTE_HANDLER", (
        f"{OS_MAP_MODULE} must be CONNECTED_ROUTE_HANDLER, got '{status}'"
    )


# ── Test 11 : route handlers P45 sont classés ────────────────────────────────

def test_p45_route_handlers_classified(coverage_map):
    key_mods = coverage_map.get("key_module_classifications", {})
    p45_handlers = [
        "apps/obsidia_api/routes/brody.py",
        "apps/obsidia_api/routes/audit.py",
        "apps/obsidia_api/routes/memory.py",
        "apps/obsidia_api/routes/os_map.py",
    ]
    for handler in p45_handlers:
        status = key_mods.get(handler, "")
        assert status, f"{handler} not found in key_module_classifications"
        assert status != "UNCLASSIFIED", f"{handler} is UNCLASSIFIED"


# ── Test 12 : workbench support P46 est classé ───────────────────────────────

def test_p46_workbench_support_classified(coverage_map):
    key_mods = coverage_map.get("key_module_classifications", {})
    wb_mods = [
        "runtime_wiring/source_runtime/workbench_view_capability_map.py",
        "runtime_wiring/source_runtime/workbench_view_coverage_classifier.py",
    ]
    for wb in wb_mods:
        status = key_mods.get(wb, "")
        assert status, f"{wb} not found in key_module_classifications"
        assert "WORKBENCH" in status or status != "UNCLASSIFIED", f"{wb} must be workbench-related"


# ── Test 13 : modules actionnels sont BLOCKED_ACTION_RUNTIME ─────────────────

def test_action_modules_are_blocked(coverage_map):
    key_mods = coverage_map.get("key_module_classifications", {})
    for action_mod in ACTION_MODULES:
        status = key_mods.get(action_mod, "")
        assert status == "BLOCKED_ACTION_RUNTIME", (
            f"{action_mod} must be BLOCKED_ACTION_RUNTIME, got '{status}'"
        )


# ── Test 14 : aucun module actionnel runtime_allowed_now=True ─────────────────

def test_no_action_module_runtime_allowed(coverage_map):
    assert coverage_map.get("runtime_allowed_now") is False


# ── Test 15 : aucun module actionnel emits_act=True ──────────────────────────

def test_no_action_module_emits_act(coverage_map):
    assert coverage_map.get("emits_act") is False


# ── Test 16 : decision_authority=KX108_ONLY partout ──────────────────────────

def test_decision_authority_kx108_only(coverage_map):
    assert coverage_map.get("decision_authority") == "KX108_ONLY"


# ── Tests supplémentaires ─────────────────────────────────────────────────────

def test_inventory_module_count(inventory):
    mods = inventory.get("modules", [])
    total = inventory.get("modules_total", 0)
    assert total == 121, f"Expected 121 modules, got {total}"
    assert len(mods) == 121, f"Expected 121 entries, got {len(mods)}"


def test_inventory_function_count(inventory):
    total = inventory.get("functions_total", 0)
    assert total == 548, f"Expected 548 functions, got {total}"


def test_coverage_map_status_ready(coverage_map):
    assert coverage_map.get("map_status") == "READY"
    assert coverage_map.get("module_function_coverage_status") == "FULL_COVERAGE"


def test_classifier_import():
    from runtime_wiring.source_runtime.module_function_coverage_classifier import (
        classify_module,
        classify_function,
        get_module_coverage_summary,
    )
    assert callable(classify_module)
    assert callable(classify_function)
    assert callable(get_module_coverage_summary)


def test_capability_map_import():
    from runtime_wiring.source_runtime.module_function_capability_map import (
        get_module_function_capability_map,
        build_module_function_coverage_summary,
    )
    cap_map = get_module_function_capability_map()
    assert len(cap_map) > 10
    summary = build_module_function_coverage_summary()
    assert summary["modules_unclassified_count"] == 0
    assert summary["functions_unclassified_count"] == 0
    assert summary["module_coverage_percent"] == 100.0
    assert summary["function_coverage_percent"] == 100.0


def test_classifier_capability_router():
    from runtime_wiring.source_runtime.module_function_coverage_classifier import classify_module
    m = {"module_path": "runtime_wiring/source_runtime/capability_path_router.py", "risk_flags": []}
    assert classify_module(m) == "CONNECTED_CAPABILITY"


def test_classifier_blockchain_blocked():
    from runtime_wiring.source_runtime.module_function_coverage_classifier import classify_module
    m = {"module_path": "apps/obsidia_api/routes/blockchain.py", "risk_flags": []}
    assert classify_module(m) == "BLOCKED_ACTION_RUNTIME"


def test_classifier_os_map_route_handler():
    from runtime_wiring.source_runtime.module_function_coverage_classifier import classify_module
    m = {"module_path": "apps/obsidia_api/routes/os_map.py", "risk_flags": []}
    assert classify_module(m) == "CONNECTED_ROUTE_HANDLER"


def test_classifier_workbench_support():
    from runtime_wiring.source_runtime.module_function_coverage_classifier import classify_module
    m = {"module_path": "runtime_wiring/source_runtime/workbench_view_capability_map.py", "risk_flags": []}
    assert classify_module(m) == "CONNECTED_WORKBENCH_SUPPORT"


def test_classifier_all_inventory_modules_classified():
    """Test de bout en bout : le classifieur ne laisse aucun module UNCLASSIFIED."""
    from runtime_wiring.source_runtime.runtime_inventory_graph import build_runtime_inventory_graph
    from runtime_wiring.source_runtime.module_function_coverage_classifier import (
        classify_module,
        get_module_coverage_summary,
    )
    g = build_runtime_inventory_graph()
    mods = g.get("modules", [])
    assert len(mods) > 0

    summary = get_module_coverage_summary(mods)
    assert summary["modules_unclassified_count"] == 0, (
        f"Unclassified modules: {summary['modules_unclassified_count']}"
    )
    assert summary["module_coverage_percent"] == 100.0
    assert summary["function_coverage_percent"] == 100.0
    assert summary["module_function_coverage_status"] == "FULL_COVERAGE"
