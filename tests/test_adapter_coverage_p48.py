"""
P48 — Tests unitaires : couverture adapters.
Vérifie que les 10 adapters sont tous classifiés, unclassified=0, KX108_ONLY.
NO ACT. NO write. READONLY.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
INVENTORY_PATH = ROOT / "_runtime_wiring_preflight" / "P48_ADAPTER_INVENTORY_RAW.json"
COVERAGE_MAP_PATH = ROOT / "_runtime_wiring_preflight" / "P48_ADAPTER_COVERAGE_MAP.json"

EXPECTED_ADAPTERS = {
    "cognitive_to_context_packet",
    "rssi_rgpd_to_context_packet",
    "atlas_to_context_packet",
    "compliance_to_context_packet",
    "rssi_security_to_context_packet",
    "external_signals_to_context_packet",
    "npl_to_context_packet",
    "os_trad_reverse_to_context_packet",
    "reverse_os_interlanguage_to_context_packet",
    "route_entry_to_context_packet",
}

VALID_STATUSES = {
    "CONNECTED_CONTEXT_PACKET",
    "CONNECTED_SOURCE_RUNTIME",
    "CONNECTED_CAPABILITY",
    "CONNECTED_OS_MAP",
    "CONNECTED_READONLY_PREVIEW",
    "BLOCKED_ACTION_ADAPTER",
    "INTERNAL_ONLY",
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


# ── Test 1 : inventory raw existe ─────────────────────────────────────────────

def test_raw_inventory_exists():
    assert INVENTORY_PATH.exists()


# ── Test 2 : coverage map existe ──────────────────────────────────────────────

def test_coverage_map_exists():
    assert COVERAGE_MAP_PATH.exists()


# ── Test 3 : adapters_total == 10 ────────────────────────────────────────────

def test_adapters_total_is_10(inventory, coverage_map):
    assert inventory.get("adapters_total") == 10
    assert coverage_map.get("adapters_total") == 10


# ── Test 4 : adapters_classified == 10 ───────────────────────────────────────

def test_adapters_classified_is_10(coverage_map):
    assert coverage_map.get("adapters_classified") == 10


# ── Test 5 : adapters_unclassified_count == 0 ─────────────────────────────────

def test_adapters_unclassified_count_is_zero(coverage_map):
    count = coverage_map.get("adapters_unclassified_count", -1)
    assert count == 0, f"adapters_unclassified_count must be 0, got {count}"


# ── Test 6 : adapter_coverage_percent == 100 ─────────────────────────────────

def test_adapter_coverage_percent_is_100(coverage_map):
    pct = coverage_map.get("adapter_coverage_percent", 0.0)
    assert pct == 100.0, f"adapter_coverage_percent must be 100.0, got {pct}"


# ── Test 7 : reverse_os_interlanguage est CONNECTED ──────────────────────────

def test_reverse_os_interlanguage_is_connected(coverage_map):
    adapter_map = coverage_map.get("adapter_map", {})
    entry = adapter_map.get("reverse_os_interlanguage_to_context_packet", {})
    status = entry.get("coverage_status", "")
    assert status.startswith("CONNECTED"), (
        f"reverse_os_interlanguage_to_context_packet must be CONNECTED, got '{status}'"
    )


# ── Test 8 : atlas est CONNECTED ─────────────────────────────────────────────

def test_atlas_is_connected(coverage_map):
    adapter_map = coverage_map.get("adapter_map", {})
    entry = adapter_map.get("atlas_to_context_packet", {})
    status = entry.get("coverage_status", "")
    assert status.startswith("CONNECTED"), (
        f"atlas_to_context_packet must be CONNECTED, got '{status}'"
    )


# ── Test 9 : external_signals est CONNECTED ou DO_NOT_BIND_EXPLICIT ──────────

def test_external_signals_classified(coverage_map):
    adapter_map = coverage_map.get("adapter_map", {})
    entry = adapter_map.get("external_signals_to_context_packet", {})
    status = entry.get("coverage_status", "")
    assert status in {"CONNECTED_CONTEXT_PACKET", "DO_NOT_BIND_EXPLICIT"}, (
        f"external_signals_to_context_packet must be CONNECTED or DO_NOT_BIND_EXPLICIT, got '{status}'"
    )


# ── Test 10 : aucun adapter runtime_allowed_now=True ─────────────────────────

def test_no_adapter_runtime_allowed_now(coverage_map):
    assert coverage_map.get("runtime_allowed_now") is False
    adapter_map = coverage_map.get("adapter_map", {})
    for name, entry in adapter_map.items():
        assert entry.get("runtime_allowed_now") is False, (
            f"{name}: runtime_allowed_now must be False"
        )


# ── Test 11 : aucun adapter emits_act=True ────────────────────────────────────

def test_no_adapter_emits_act(coverage_map):
    assert coverage_map.get("emits_act") is False
    adapter_map = coverage_map.get("adapter_map", {})
    for name, entry in adapter_map.items():
        assert entry.get("emits_act") is False, (
            f"{name}: emits_act must be False"
        )


# ── Test 12 : decision_authority=KX108_ONLY partout ──────────────────────────

def test_decision_authority_kx108_only(coverage_map):
    assert coverage_map.get("decision_authority") == "KX108_ONLY"
    adapter_map = coverage_map.get("adapter_map", {})
    for name, entry in adapter_map.items():
        da = entry.get("decision_authority", "")
        assert da == "KX108_ONLY", (
            f"{name}: decision_authority must be KX108_ONLY, got '{da}'"
        )


# ── Tests supplémentaires ─────────────────────────────────────────────────────

def test_all_expected_adapters_in_map(coverage_map):
    adapter_map = coverage_map.get("adapter_map", {})
    for expected in EXPECTED_ADAPTERS:
        assert expected in adapter_map, f"{expected} missing from P48 coverage map"


def test_all_adapters_valid_status(coverage_map):
    adapter_map = coverage_map.get("adapter_map", {})
    for name, entry in adapter_map.items():
        status = entry.get("coverage_status", "")
        assert status in VALID_STATUSES, f"{name}: invalid status '{status}'"
        assert status != "UNCLASSIFIED", f"{name} is UNCLASSIFIED"


def test_coverage_map_status_ready(coverage_map):
    assert coverage_map.get("map_status") == "READY"
    assert coverage_map.get("adapter_coverage_status") == "FULL_COVERAGE"


def test_classifier_import():
    from runtime_wiring.source_runtime.adapter_coverage_classifier import (
        classify_adapter,
        get_adapter_coverage_summary,
    )
    assert callable(classify_adapter)
    assert callable(get_adapter_coverage_summary)


def test_capability_map_import():
    from runtime_wiring.source_runtime.adapter_capability_map import (
        get_adapter_capability_map,
        build_adapter_coverage_summary,
    )
    cap_map = get_adapter_capability_map()
    assert len(cap_map) == 10
    summary = build_adapter_coverage_summary()
    assert summary["adapters_unclassified_count"] == 0
    assert summary["adapter_coverage_percent"] == 100.0


def test_classifier_cognitive_adapter():
    from runtime_wiring.source_runtime.adapter_coverage_classifier import classify_adapter
    a = {
        "adapter_name": "cognitive_to_context_packet",
        "module_path": "runtime_wiring/source_adapters.py",
        "boundary": "COGNITIVE_REINTEGRATION_ADVISORY_ONLY",
        "action_risk": False,
    }
    assert classify_adapter(a) == "CONNECTED_CONTEXT_PACKET"


def test_classifier_os_trad_adapter():
    from runtime_wiring.source_runtime.adapter_coverage_classifier import classify_adapter
    a = {
        "adapter_name": "os_trad_reverse_to_context_packet",
        "module_path": "runtime_wiring/source_adapters.py",
        "boundary": "OS_TRAD_REVERSE_OS_ADVISORY_ONLY",
        "action_risk": False,
    }
    assert classify_adapter(a) == "CONNECTED_SOURCE_RUNTIME"


def test_classifier_route_entry_adapter():
    from runtime_wiring.source_runtime.adapter_coverage_classifier import classify_adapter
    a = {
        "adapter_name": "route_entry_to_context_packet",
        "module_path": "runtime_wiring/source_registry/registry_to_adapter_dry_run.py",
        "boundary": "DRY_RUN_ONLY_NO_ZIP",
        "action_risk": False,
    }
    assert classify_adapter(a) == "CONNECTED_CAPABILITY"


def test_classifier_all_inventory_adapters():
    """Test de bout en bout : le classifieur ne laisse aucun adapter UNCLASSIFIED."""
    from runtime_wiring.source_runtime.runtime_inventory_graph import build_runtime_inventory_graph
    from runtime_wiring.source_runtime.adapter_coverage_classifier import (
        get_adapter_coverage_summary,
    )
    g = build_runtime_inventory_graph()
    adapters = g.get("adapters", [])
    assert len(adapters) == 10

    summary = get_adapter_coverage_summary(adapters)
    assert summary["adapters_unclassified_count"] == 0, (
        f"Unclassified adapters: {summary['adapters_unclassified_count']}"
    )
    assert summary["adapter_coverage_percent"] == 100.0
    assert summary["adapter_coverage_status"] == "FULL_COVERAGE"


def test_inventory_all_adapters_readonly(inventory):
    adapters = inventory.get("adapters", [])
    for a in adapters:
        assert a.get("runtime_allowed_now") is False, f"{a['adapter_name']}: runtime_allowed_now must be False"
        assert a.get("emits_act") is False, f"{a['adapter_name']}: emits_act must be False"
        assert a.get("readonly") is True, f"{a['adapter_name']}: readonly must be True"
