"""
Wave005_A Stable Census Gate — scope reconciliation matrix tests.

Verifies: 3-population separation (primary/secondary/campaign_metadata),
census stability, partition A-F on primary only, intersection checks,
baseline marked non-reconstructible, zero silent double-count.
"""
from __future__ import annotations

from pathlib import Path

import pytest

import periphery.agents.brody_governance_scope_reconciliation as bgsr


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _primary_subwave_totals(partition: dict) -> int:
    return sum(v for k, v in partition.items() if k.startswith("WAVE005_"))


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


def test_wr_004_census_id_present():
    idx = bgsr.get_index()
    assert idx.get("census_id") == "BRODY_PRIMARY_POPULATION_CENSUS_V1"


# ---------------------------------------------------------------------------
# WR-010 — Total brody population (primary + secondary + metadata = 912)
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


def test_wr_013_normalized_total_is_912():
    s = bgsr.summary()
    assert s["normalized_current_total"] == 912


def test_wr_014_normalized_total_consistent_with_all_entries():
    all_entries = bgsr.get_entries()
    s = bgsr.summary()
    assert len(all_entries) == s["normalized_current_total"]


# ---------------------------------------------------------------------------
# WR-020 — 3-population separation
# ---------------------------------------------------------------------------

def test_wr_020_primary_census_total():
    s = bgsr.summary()
    assert s["primary_census_total"] == 902


def test_wr_021_campaign_metadata_total():
    s = bgsr.summary()
    assert s["campaign_metadata_total"] == 6


def test_wr_022_secondary_relation_total():
    s = bgsr.summary()
    assert s["secondary_relation_total"] == 4


def test_wr_023_population_sum_equals_normalized_total():
    s = bgsr.summary()
    total = s["primary_census_total"] + s["campaign_metadata_total"] + s["secondary_relation_total"]
    assert total == s["normalized_current_total"], (
        f"{s['primary_census_total']} + {s['campaign_metadata_total']} + "
        f"{s['secondary_relation_total']} = {total} != {s['normalized_current_total']}"
    )


def test_wr_024_campaign_metadata_entries_are_not_primary():
    meta = bgsr.get_campaign_metadata_entries()
    for e in meta:
        assert e.get("counted_in_brody_primary_census") is False, (
            f"Campaign metadata {e['path']} wrongly counted in primary census"
        )


def test_wr_025_secondary_relation_entries_are_not_primary():
    secondary = bgsr.get_secondary_relation_entries()
    for e in secondary:
        assert e.get("counted_in_brody_primary_census") is False, (
            f"Secondary relation {e['path']} wrongly counted in primary census"
        )


def test_wr_026_all_primary_entries_flagged():
    primary = bgsr.get_primary_entries()
    for e in primary:
        assert e.get("counted_in_brody_primary_census") is True, (
            f"Primary entry {e['path']} missing counted_in_brody_primary_census=True"
        )


def test_wr_027_campaign_metadata_six_known_paths():
    meta = bgsr.get_campaign_metadata_entries()
    paths = {e["path"] for e in meta}
    expected = {
        "periphery/agents/brody_governance_element_system.index.json",
        "periphery/agents/brody_governance_element_system.py",
        "tests/periphery/test_brody_governance_element_system.py",
        "periphery/agents/brody_governance_scope_reconciliation.index.json",
        "periphery/agents/brody_governance_scope_reconciliation.py",
        "tests/periphery/test_brody_governance_scope_reconciliation.py",
    }
    assert paths == expected


def test_wr_028_secondary_four_known_paths():
    secondary = bgsr.get_secondary_relation_entries()
    paths = {e["path"] for e in secondary}
    expected = {
        "periphery/agents/brody_memory_agent.py",
        "periphery/brody_memory_readonly/brody_agent_readonly_session_test_packet/run_brody_agent_readonly_session_test_packet_v1.ps1",
        "periphery/workflow_governance_readonly/integration/brody_workflow_governance_snapshot_adapter.py",
        "periphery/workflow_governance_readonly/operators/brody_workflow_operator_readonly.py",
    }
    assert paths == expected


# ---------------------------------------------------------------------------
# WR-030 — Primary partition A to F: sum and no overlap
# ---------------------------------------------------------------------------

def test_wr_030_primary_partition_sum_equals_902():
    s = bgsr.summary()
    part_sum = _primary_subwave_totals(s["partition"])
    assert part_sum == 902, f"Primary partition sum {part_sum} != 902"


def test_wr_031_primary_partition_values():
    s = bgsr.summary()
    p = s["partition"]
    assert p["WAVE005_A_BRODY_CORE_GOVERNANCE_AND_TEST"] == 11
    assert p["WAVE005_B_BRODY_INTEGRATION_RUNTIME_AND_API_TESTS"] == 144
    assert p["WAVE005_C_BRODY_PROTOCOLS_CONNECTORS_AND_SCRIPTS"] == 51
    assert p["WAVE005_D_BRODY_MEMORY_INTERFACE_AND_SPECS"] == 506
    assert p["WAVE005_E_BRODY_DOCUMENTATION_ARCHITECTURE_AND_REPORTS"] == 124
    assert p["WAVE005_F_BRODY_LEGACY_ARCHIVE_TOOLING_AND_REVIEW"] == 66


def test_wr_032_no_path_overlap_between_primary_subwaves():
    seen: dict[str, str] = {}
    for e in bgsr.get_primary_entries():
        p = e["path"]
        sw = e["assigned_subwave"]
        assert p not in seen, (
            f"Primary path {p!r} appears in both {seen.get(p)} and {sw}"
        )
        seen[p] = sw


def test_wr_033_campaign_metadata_not_in_partition():
    meta_paths = {e["path"] for e in bgsr.get_campaign_metadata_entries()}
    primary_paths = {e["path"] for e in bgsr.get_primary_entries()}
    overlap = meta_paths & primary_paths
    assert overlap == set(), f"Campaign metadata in primary partition: {overlap}"


def test_wr_034_secondary_relations_not_in_partition():
    secondary_paths = {e["path"] for e in bgsr.get_secondary_relation_entries()}
    primary_paths = {e["path"] for e in bgsr.get_primary_entries()}
    overlap = secondary_paths & primary_paths
    assert overlap == set(), f"Secondary relations in primary partition: {overlap}"


# ---------------------------------------------------------------------------
# WR-040 — Wave005_A functional = exactly 6 sources + 5 governance tests
# ---------------------------------------------------------------------------

def test_wr_040_wave005a_functional_total():
    s = bgsr.summary()
    assert s["wave005a_indexed"] == 11


def test_wr_041_wave005a_core_sources_count():
    s = bgsr.summary()
    assert s["wave005a_core_sources"] == 6


def test_wr_042_wave005a_governance_tests_count():
    s = bgsr.summary()
    assert s["wave005a_governance_tests"] == 5


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
# WR-050 — Census stability: creating metadata does not change primary count
# ---------------------------------------------------------------------------

def test_wr_050_primary_count_excludes_own_index_files():
    """The reconciliation index/validator/test are NOT counted in primary census."""
    meta_paths = {e["path"] for e in bgsr.get_campaign_metadata_entries()}
    assert "periphery/agents/brody_governance_scope_reconciliation.index.json" in meta_paths
    assert "periphery/agents/brody_governance_scope_reconciliation.py" in meta_paths
    assert "tests/periphery/test_brody_governance_scope_reconciliation.py" in meta_paths


def test_wr_051_primary_count_excludes_element_system_artefacts():
    meta_paths = {e["path"] for e in bgsr.get_campaign_metadata_entries()}
    assert "periphery/agents/brody_governance_element_system.index.json" in meta_paths
    assert "periphery/agents/brody_governance_element_system.py" in meta_paths
    assert "tests/periphery/test_brody_governance_element_system.py" in meta_paths


def test_wr_052_primary_count_is_stable_at_902():
    """Stable sentinel: primary census must equal 902."""
    primary = bgsr.get_primary_entries()
    assert len(primary) == 902, (
        f"Primary census changed from 902 to {len(primary)} — "
        "check if a new campaign artefact was incorrectly classified as primary"
    )


# ---------------------------------------------------------------------------
# WR-060 — Zero silent double-count and prior wave intersections
# ---------------------------------------------------------------------------

def test_wr_060_silent_double_count_zero():
    s = bgsr.summary()
    assert s["silent_double_count"] == 0


def test_wr_061_prior_wave_primary_owners_zero():
    s = bgsr.summary()
    assert s["prior_wave_primary_owners"] == 0, (
        "No brody primary file should be primary owner in Wave001-004"
    )


def test_wr_062_prior_wave_secondary_intersections_two():
    s = bgsr.summary()
    assert s["prior_wave_secondary_intersections"] == 2


def test_wr_063_prior_wave_intersection_paths():
    inter = bgsr.get_prior_wave_intersections()
    w2 = inter["wave002_intersection_paths"]
    assert "periphery/agents/brody_memory_agent.py" in w2
    w1 = inter["wave001_intersection_paths"]
    assert any("run_brody_agent_readonly" in p for p in w1)


def test_wr_064_wave003_intersection_empty():
    inter = bgsr.get_prior_wave_intersections()
    assert inter.get("wave003_intersection_paths", []) == []


def test_wr_065_wave004_intersection_empty():
    inter = bgsr.get_prior_wave_intersections()
    assert inter.get("wave004_intersection_paths", []) == []


# ---------------------------------------------------------------------------
# WR-070 — UNRESOLVED: 0 primary unresolved after reclassification
# ---------------------------------------------------------------------------

def test_wr_070_primary_unresolved_count_zero():
    unresolved = bgsr.get_unresolved_entries()
    assert len(unresolved) == 0, (
        f"Expected 0 primary unresolved, got {len(unresolved)}: "
        f"{[e['path'] for e in unresolved]}"
    )


def test_wr_071_workflow_governance_are_secondary():
    secondary = bgsr.get_secondary_relation_entries()
    s_paths = {e["path"] for e in secondary}
    assert "periphery/workflow_governance_readonly/integration/brody_workflow_governance_snapshot_adapter.py" in s_paths
    assert "periphery/workflow_governance_readonly/operators/brody_workflow_operator_readonly.py" in s_paths


def test_wr_072_unexplained_primary_unresolved_zero():
    unresolved = bgsr.get_unresolved_entries()
    assert unresolved == [], "No primary unresolved files expected"


# ---------------------------------------------------------------------------
# WR-080 — Baseline non reconstructible
# ---------------------------------------------------------------------------

def test_wr_080_baseline_reference_905():
    s = bgsr.summary()
    assert s["baseline_reference"] == 905


def test_wr_081_baseline_status_non_reconstructible():
    s = bgsr.summary()
    assert s["baseline_reference_status"] == "NON_RECONSTRUCTIBLE_AGGREGATE_COUNTER"


def test_wr_082_net_delta_unknown():
    s = bgsr.summary()
    assert s["net_delta_from_baseline"] == "UNKNOWN", (
        "Exact delta from baseline 905 is not reconstructible — must be UNKNOWN"
    )


# ---------------------------------------------------------------------------
# WR-090 — Physical existence for primary entries
# ---------------------------------------------------------------------------

def test_wr_090_all_primary_current_present_files_exist():
    result = bgsr.validate_all_current_paths_exist()
    missing = [p for p, ok in result.items() if not ok]
    assert missing == [], f"Primary files marked current_present=True but missing on disk: {missing}"


# ---------------------------------------------------------------------------
# WR-100 — Governance invariants (no ACT, no decision, no memory write)
# ---------------------------------------------------------------------------

def test_wr_100_no_entry_emits_act():
    idx = bgsr.get_index()
    assert idx["emits_act"] is False


def test_wr_101_no_entry_can_decide():
    idx = bgsr.get_index()
    assert idx["can_decide"] is False


def test_wr_102_no_sovereign_memory_write():
    idx = bgsr.get_index()
    assert idx["memory_write"] is False


def test_wr_103_no_runtime_consumed():
    idx = bgsr.get_index()
    assert idx["runtime_consumed"] is False


# ---------------------------------------------------------------------------
# WR-110 — Functional family total on primary entries only
# ---------------------------------------------------------------------------

def test_wr_110_functional_family_sum_within_range():
    idx = bgsr.get_index()
    family_summary = idx.get("functional_family_summary", {})
    primary = bgsr.get_primary_entries()
    # Family summary was built on total (912) but primary is 902
    # Check family sum is <= total entries (may include all 912 or just 902)
    assert sum(family_summary.values()) <= len(bgsr.get_entries()) + 1


def test_wr_111_brody_memory_interface_is_largest_family():
    idx = bgsr.get_index()
    family_summary = idx.get("functional_family_summary", {})
    assert family_summary.get("BRODY_MEMORY_INTERFACE", 0) > 400


def test_wr_112_wave005d_contains_memory_interface_files():
    d_entries = bgsr.get_entries_by_subwave("WAVE005_D_BRODY_MEMORY_INTERFACE_AND_SPECS")
    assert len(d_entries) > 400
    mem_paths = [e["path"] for e in d_entries if "brody_memory_readonly" in e["path"]]
    assert len(mem_paths) > 400


# ---------------------------------------------------------------------------
# WR-120 — Artifact registration: local vs global role separation
# ---------------------------------------------------------------------------

def test_wr_120_local_matrix_is_not_global_manifest():
    idx = bgsr.get_index()
    assert idx.get("artifact_role") == "WAVE005_A_LOCAL_SCOPE_RECONCILIATION_MATRIX", (
        "Reconciliation matrix must declare LOCAL role, not global manifest"
    )
    assert idx.get("is_global_file_manifest") is False


def test_wr_121_local_matrix_is_not_global_relation_graph():
    idx = bgsr.get_index()
    assert idx.get("is_global_relation_graph") is False


def test_wr_122_prior_wave_intersections_is_local_view():
    idx = bgsr.get_index()
    assert "local_scope_relation_view_note" in idx or "prior_wave_intersections" in idx, (
        "prior_wave_intersections must exist as LOCAL_SCOPE_RELATION_VIEW"
    )


def test_wr_123_global_state_path_declared():
    idx = bgsr.get_index()
    assert idx.get("global_state_path") == "periphery/agents/agents_file_wiring_global_state.json"


# ---------------------------------------------------------------------------
# WR-130 — Census stability sentinel
# ---------------------------------------------------------------------------

def test_wr_130_primary_census_stable_at_902():
    primary = bgsr.get_primary_entries()
    assert len(primary) == 902, (
        f"Primary census is {len(primary)}, expected 902. "
        "New campaign artefacts must NOT increase this count."
    )


def test_wr_131_pending_bf_subwaves_sum_891():
    s = bgsr.summary()
    p = s["partition"]
    pending = (
        p.get("WAVE005_B_BRODY_INTEGRATION_RUNTIME_AND_API_TESTS", 0) +
        p.get("WAVE005_C_BRODY_PROTOCOLS_CONNECTORS_AND_SCRIPTS", 0) +
        p.get("WAVE005_D_BRODY_MEMORY_INTERFACE_AND_SPECS", 0) +
        p.get("WAVE005_E_BRODY_DOCUMENTATION_ARCHITECTURE_AND_REPORTS", 0) +
        p.get("WAVE005_F_BRODY_LEGACY_ARCHIVE_TOOLING_AND_REVIEW", 0)
    )
    assert pending == 891, f"B+C+D+E+F primary sum = {pending}, expected 891"


def test_wr_132_campaign_metadata_total_not_in_primary():
    meta = bgsr.get_campaign_metadata_entries()
    assert len(meta) == 6
    primary_paths = {e["path"] for e in bgsr.get_primary_entries()}
    for e in meta:
        assert e["path"] not in primary_paths, (
            f"Campaign metadata {e['path']} wrongly in primary census"
        )
