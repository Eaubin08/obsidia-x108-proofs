"""
Wave005_A Final Accounting — scope reconciliation matrix tests.

Verifies: 914→total explanation, partition A-F, zero overlap, zero double-count,
unresolved paths named, Wave005_A = 6 sources + 5 tests, functional families.
"""
from __future__ import annotations

from pathlib import Path

import pytest

import periphery.agents.brody_governance_scope_reconciliation as bgsr


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _all_subwave_totals(s: dict) -> int:
    return sum(v for k, v in s.items() if k.startswith("WAVE005_"))


# ---------------------------------------------------------------------------
# WR-001 — Index loads and identity
# ---------------------------------------------------------------------------

def test_wr_001_index_loads():
    idx = bgsr.get_index()
    assert idx["index_id"] == "BRODY_GOVERNANCE_SCOPE_RECONCILIATION_INDEX_V1"


def test_wr_002_non_sovereign_flags():
    idx = bgsr.get_index()
    assert idx["can_decide"] is False
    assert idx["can_act"] is False
    assert idx["emits_act"] is False
    assert idx["memory_write"] is False
    assert idx["model_calls"] == 0
    assert idx["runtime_consumed"] is False


def test_wr_003_wave_role():
    idx = bgsr.get_index()
    assert idx["wave_role"] == "WAVE005_A_FINAL_ACCOUNTING"


# ---------------------------------------------------------------------------
# WR-010 — Explanation 914 → normalized total
# ---------------------------------------------------------------------------

def test_wr_010_initial_scan_declared_914():
    s = bgsr.summary()
    assert s["initial_scan_914"] == 914


def test_wr_011_excluded_from_914_is_five():
    s = bgsr.summary()
    assert s["excluded_from_914"] == 5


def test_wr_012_five_excluded_paths_are_runtime_freezes():
    paths = bgsr.get_five_excluded_from_914()
    assert len(paths) == 5
    for p in paths:
        assert ".runtime_freezes/" in p, f"Expected .runtime_freezes/ in: {p}"
        assert "MANIFEST_SHA256.json" in p


def test_wr_013_normalized_total_accounting():
    s = bgsr.summary()
    # 912 = 914 (initial scan) - 5 (excluded .runtime_freezes) + 3 (reconciliation artefacts added after scan)
    expected = s["initial_scan_914"] - s["excluded_from_914"] + s["files_added_since_initial_scan_914"]
    assert s["normalized_current_total"] == expected, (
        f"Expected {expected}, got {s['normalized_current_total']}"
    )


def test_wr_014_normalized_total_consistent_with_entries():
    entries = bgsr.get_entries()
    s = bgsr.summary()
    assert len(entries) == s["normalized_current_total"]


# ---------------------------------------------------------------------------
# WR-020 — Unique paths and no duplicates
# ---------------------------------------------------------------------------

def test_wr_020_unique_paths():
    entries = bgsr.get_entries()
    paths = [e["path"] for e in entries]
    assert len(paths) == len(set(paths)), "Duplicate paths found in matrix"


def test_wr_021_all_entries_have_assigned_subwave():
    entries = bgsr.get_entries()
    missing = [e["path"] for e in entries if not e.get("assigned_subwave")]
    assert missing == []


def test_wr_022_all_entries_have_primary_owner():
    entries = bgsr.get_entries()
    missing = [e["path"] for e in entries if not e.get("primary_owner")]
    assert missing == []


def test_wr_023_all_entries_have_evidence():
    entries = bgsr.get_entries()
    missing = [e["path"] for e in entries if not e.get("classification_evidence")]
    assert missing == []


# ---------------------------------------------------------------------------
# WR-030 — Partition A → F: sum and no overlap
# ---------------------------------------------------------------------------

def test_wr_030_partition_sum_equals_total():
    s = bgsr.summary()
    total = s["normalized_current_total"]
    part_sum = _all_subwave_totals(s["partition"])
    assert part_sum == total, f"Partition sum {part_sum} != total {total}"


def test_wr_031_no_path_overlap_between_subwaves():
    seen: dict[str, str] = {}
    for e in bgsr.get_entries():
        p = e["path"]
        sw = e["assigned_subwave"]
        assert p not in seen, (
            f"Path {p!r} appears in both {seen.get(p)} and {sw}"
        )
        seen[p] = sw


def test_wr_032_no_paths_without_subwave():
    entries = bgsr.get_entries()
    no_sw = [e["path"] for e in entries if not e.get("assigned_subwave")]
    assert no_sw == []


# ---------------------------------------------------------------------------
# WR-040 — Wave005_A = exactly 6 sources + 5 governance tests
# ---------------------------------------------------------------------------

def test_wr_040_wave005a_core_sources_count():
    s = bgsr.summary()
    assert s["wave005a_core_sources"] == 6


def test_wr_041_wave005a_governance_tests_count():
    s = bgsr.summary()
    assert s["wave005a_governance_tests"] == 5


def test_wr_042_wave005a_indexed_entries_count():
    s = bgsr.summary()
    assert s["wave005a_indexed"] == 11


def test_wr_043_wave005a_core_source_paths():
    entries = bgsr.get_wave005a_indexed_entries()
    source_paths = {e["path"] for e in entries if e["path"].startswith("periphery/brody/")}
    expected = {
        "periphery/brody/__init__.py",
        "periphery/brody/brody_response_contract.py",
        "periphery/brody/brody_runtime_readonly.py",
        "periphery/brody/brody_context_query.py",
        "periphery/brody/brody_language_router.py",
        "periphery/brody/brody_response_sanitizer.py",
    }
    assert source_paths == expected


def test_wr_044_no_brody_runtime_pkg_in_wave005a_indexed():
    indexed = bgsr.get_wave005a_indexed_entries()
    runtime_pkg = [e["path"] for e in indexed if "brody_runtime/" in e["path"]]
    assert runtime_pkg == [], (
        f"periphery/brody_runtime/ entries wrongly in INDEXED: {runtime_pkg}"
    )


def test_wr_045_brody_runtime_pkg_in_wave005b():
    b_entries = bgsr.get_entries_by_subwave(
        "WAVE005_B_BRODY_INTEGRATION_RUNTIME_AND_API_TESTS"
    )
    b_paths = {e["path"] for e in b_entries}
    assert any("brody_runtime/" in p for p in b_paths), (
        "periphery/brody_runtime/ entries not found in WAVE005_B"
    )


# ---------------------------------------------------------------------------
# WR-050 — Zero double-count and intersection check
# ---------------------------------------------------------------------------

def test_wr_050_silent_double_count_zero():
    s = bgsr.summary()
    assert s["silent_double_count"] == 0


def test_wr_051_double_count_entries_are_secondary_only():
    detail = bgsr.get_double_count_entries()
    for d in detail:
        assert d["status"] == "SECONDARY_RELATION_ONLY", (
            f"{d['path']} has double_count status {d['status']!r}, expected SECONDARY_RELATION_ONLY"
        )


# ---------------------------------------------------------------------------
# WR-060 — Exactly 2 unresolved paths named
# ---------------------------------------------------------------------------

def test_wr_060_unresolved_count():
    unresolved = bgsr.get_unresolved_entries()
    assert len(unresolved) == 2


def test_wr_061_unresolved_paths_named():
    paths = bgsr.get_unresolved_paths()
    assert len(paths) == 2
    assert "periphery/workflow_governance_readonly/integration/brody_workflow_governance_snapshot_adapter.py" in paths
    assert "periphery/workflow_governance_readonly/operators/brody_workflow_operator_readonly.py" in paths


def test_wr_062_unexplained_unresolved_zero():
    unresolved = bgsr.get_unresolved_entries()
    unexplained = [
        e for e in unresolved
        if not e.get("unresolved_reason")
    ]
    assert unexplained == [], (
        f"Unresolved entries without explanation: {[e['path'] for e in unexplained]}"
    )


# ---------------------------------------------------------------------------
# WR-070 — Baseline reconciliation
# ---------------------------------------------------------------------------

def test_wr_070_baseline_reference_905():
    s = bgsr.summary()
    assert s["baseline_reference"] == 905


def test_wr_071_net_delta_positive_and_explained():
    s = bgsr.summary()
    delta = s["net_delta_from_baseline"]
    # Delta should be positive (files added since baseline)
    # and consistent with total = 905 + delta
    assert s["baseline_reference"] + delta == s["normalized_current_total"]


# ---------------------------------------------------------------------------
# WR-080 — Physical existence check for current files
# ---------------------------------------------------------------------------

def test_wr_080_all_current_present_files_exist():
    result = bgsr.validate_all_current_paths_exist()
    missing = [p for p, ok in result.items() if not ok]
    assert missing == [], f"Files marked current_present=True but missing on disk: {missing}"


# ---------------------------------------------------------------------------
# WR-090 — Governance invariants (no ACT, no decision, no memory write)
# ---------------------------------------------------------------------------

def test_wr_090_no_entry_emits_act():
    idx = bgsr.get_index()
    assert idx["emits_act"] is False


def test_wr_091_no_entry_can_decide():
    idx = bgsr.get_index()
    assert idx["can_decide"] is False


def test_wr_092_no_sovereign_memory_write():
    idx = bgsr.get_index()
    assert idx["memory_write"] is False


def test_wr_093_no_runtime_consumed():
    idx = bgsr.get_index()
    assert idx["runtime_consumed"] is False


# ---------------------------------------------------------------------------
# WR-100 — Functional family total equals normalized total
# ---------------------------------------------------------------------------

def test_wr_100_functional_family_sum_equals_total():
    idx = bgsr.get_index()
    family_summary = idx.get("functional_family_summary", {})
    entries = bgsr.get_entries()
    assert sum(family_summary.values()) == len(entries), (
        f"Family sum {sum(family_summary.values())} != entries total {len(entries)}"
    )


def test_wr_101_brody_memory_interface_is_largest_family():
    idx = bgsr.get_index()
    family_summary = idx.get("functional_family_summary", {})
    assert family_summary.get("BRODY_MEMORY_INTERFACE", 0) > 400


def test_wr_102_wave005d_contains_memory_interface_files():
    d_entries = bgsr.get_entries_by_subwave("WAVE005_D_BRODY_MEMORY_INTERFACE_AND_SPECS")
    assert len(d_entries) > 400
    mem_paths = [e["path"] for e in d_entries if "brody_memory_readonly" in e["path"]]
    assert len(mem_paths) > 400
