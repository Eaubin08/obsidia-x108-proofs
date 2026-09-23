"""
P49 — Tests unitaires : gate global runtime surface 100% coverage.
Vérifie que la consolidation P44→P48 est à 100%, UNCLASSIFIED=0, KX108_ONLY.
NO ACT. NO write. READONLY.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
GLOBAL_MAP_PATH = ROOT / "_runtime_wiring_preflight" / "P49_GLOBAL_RUNTIME_SURFACE_100_MAP.json"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def gate():
    from runtime_wiring.source_runtime.global_runtime_surface_gate import (
        build_global_runtime_surface_gate,
    )
    return build_global_runtime_surface_gate()


@pytest.fixture(scope="module")
def global_map():
    assert GLOBAL_MAP_PATH.exists(), f"Global map missing: {GLOBAL_MAP_PATH}"
    return json.loads(GLOBAL_MAP_PATH.read_text(encoding="utf-8"))


# ── Test 1 : module importable ────────────────────────────────────────────────

def test_global_runtime_surface_gate_importable():
    from runtime_wiring.source_runtime.global_runtime_surface_gate import (
        build_global_runtime_surface_gate,
    )
    assert callable(build_global_runtime_surface_gate)


# ── Test 2 : global map existe ────────────────────────────────────────────────

def test_global_map_exists():
    assert GLOBAL_MAP_PATH.exists()


# ── Test 3 : overall_coverage_percent == 100 ─────────────────────────────────

def test_overall_coverage_percent_is_100(gate):
    assert gate["overall_coverage_percent"] == 100.0


# ── Test 4 : unclassified_total == 0 ─────────────────────────────────────────

def test_unclassified_total_is_zero(gate):
    assert gate["unclassified_total"] == 0


# ── Test 5 : families coverage == 100 ────────────────────────────────────────

def test_families_coverage_is_100(gate):
    fam = gate["families"]
    assert fam["families_coverage_percent"] == 100.0
    assert fam["families_unclassified"] == 0
    assert fam["families_classified"] == fam["families_total"]
    assert len(fam["families_unconnected"]) == 0


# ── Test 6 : routes coverage == 100 ──────────────────────────────────────────

def test_routes_coverage_is_100(gate):
    routes = gate["routes"]
    assert routes["routes_coverage_percent"] == 100.0
    assert routes["routes_unclassified"] == 0
    assert routes["routes_classified"] == routes["routes_total"]
    assert routes["counts"]["UNCLASSIFIED"] == 0


# ── Test 7 : workbench views coverage == 100 ─────────────────────────────────

def test_workbench_views_coverage_is_100(gate):
    views = gate["workbench_views"]
    assert views["workbench_views_coverage_percent"] == 100.0
    assert views["workbench_views_unclassified"] == 0
    assert views["workbench_views_classified"] == views["workbench_views_total"]
    assert views["counts"]["UNCLASSIFIED"] == 0


# ── Test 8 : modules coverage == 100 ─────────────────────────────────────────

def test_modules_coverage_is_100(gate):
    mods = gate["modules"]
    assert mods["modules_coverage_percent"] == 100.0
    assert mods["modules_unclassified"] == 0
    assert mods["modules_classified"] == mods["modules_total"]
    assert mods["counts"]["UNCLASSIFIED"] == 0


# ── Test 9 : functions coverage == 100 ───────────────────────────────────────

def test_functions_coverage_is_100(gate):
    funcs = gate["functions"]
    assert funcs["functions_coverage_percent"] == 100.0
    assert funcs["functions_unclassified"] == 0
    assert funcs["functions_classified"] == funcs["functions_total"]
    assert funcs["counts"]["UNCLASSIFIED"] == 0


# ── Test 10 : adapters coverage == 100 ───────────────────────────────────────

def test_adapters_coverage_is_100(gate):
    adp = gate["adapters"]
    assert adp["adapters_coverage_percent"] == 100.0
    assert adp["adapters_unclassified"] == 0
    assert adp["adapters_classified"] == adp["adapters_total"]
    assert adp["counts"]["UNCLASSIFIED"] == 0


# ── Test 11 : activation_allowed == False ────────────────────────────────────

def test_activation_allowed_is_false(gate):
    assert gate["activation_allowed"] is False


# ── Test 12 : runtime_allowed_now == False ────────────────────────────────────

def test_runtime_allowed_now_is_false(gate):
    assert gate["runtime_allowed_now"] is False


# ── Test 13 : emits_act == False ──────────────────────────────────────────────

def test_emits_act_is_false(gate):
    assert gate["emits_act"] is False


# ── Test 14 : decision_authority == KX108_ONLY ───────────────────────────────

def test_decision_authority_is_kx108_only(gate):
    assert gate["decision_authority"] == "KX108_ONLY"


# ── Test bonus : global_runtime_surface_status == FULL_COVERAGE ──────────────

def test_global_status_is_full_coverage(gate):
    assert gate["global_runtime_surface_status"] == "FULL_COVERAGE"


# ── Test bonus : totaux corrects ──────────────────────────────────────────────

def test_totals_correct(gate):
    assert gate["families"]["families_total"] == 8
    assert gate["routes"]["routes_total"] == 147
    assert gate["workbench_views"]["workbench_views_total"] == 13
    assert gate["modules"]["modules_total"] == 121
    assert gate["functions"]["functions_total"] == 548
    assert gate["adapters"]["adapters_total"] == 10


# ── Test bonus : map JSON cohérente ──────────────────────────────────────────

def test_global_map_coverage_percent(global_map):
    assert global_map["overall_coverage_percent"] == 100.0


def test_global_map_unclassified_zero(global_map):
    assert global_map["unclassified_total"] == 0


def test_global_map_p49_status(global_map):
    assert global_map["p49_status"] == "P49_GLOBAL_RUNTIME_SURFACE_100_GATE_READY"
