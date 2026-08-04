"""
Tests for WAVE005_D index: BRODY_MEMORY_INTERFACE_AND_SPECS_INDEX_V1

WD-001 to WD-080 — documentary, read-only, no runtime.
"""
import json
from pathlib import Path
import pytest

from periphery.agents.brody_memory_interface_and_specs import (
    get_index,
    get_entries,
    get_source_module_entries,
    get_artifact_entries,
    get_governance_rule_entries,
    get_blocked_backup_entries,
    get_blocker_queue,
    get_governance_invariants,
    get_scope_reconciliation,
    get_remaining_population,
    is_scope_complete,
    get_covered_slice,
    has_no_executable_tests,
    summary,
    validate_all_paths_exist,
)


# ---------------------------------------------------------------------------
# WD-001 to WD-010 — index metadata
# ---------------------------------------------------------------------------

def test_wd_001_index_id():
    idx = get_index()
    assert idx["index_id"] == "BRODY_MEMORY_INTERFACE_AND_SPECS_INDEX_V1"


def test_wd_002_schema_version():
    idx = get_index()
    assert idx["schema_version"] == "1.0"


def test_wd_003_campaign():
    idx = get_index()
    assert idx["campaign"] == "AGENTS_FILE_WIRING"


def test_wd_004_covered_slice():
    assert get_covered_slice() == "WAVE005_D_BRODY_MEMORY_INTERFACE_AND_SPECS"


def test_wd_005_scope_complete_false():
    assert is_scope_complete() is False


def test_wd_006_authority_non_sovereign():
    idx = get_index()
    assert idx["authority"] == "NON_SOVEREIGN"


def test_wd_007_non_sovereign_flags():
    idx = get_index()
    assert idx["can_decide"] is False
    assert idx["can_act"] is False
    assert idx["emits_act"] is False
    assert idx["memory_write"] is False
    assert idx["model_calls"] == 0
    assert idx["runtime_consumed"] is False


def test_wd_008_total_entries():
    idx = get_index()
    assert idx["total_entries"] == 507


def test_wd_009_entries_count_matches():
    assert len(get_entries()) == 507


def test_wd_010_files_with_explicit_blocker():
    idx = get_index()
    assert idx["files_with_explicit_blocker"] == 2


# ---------------------------------------------------------------------------
# WD-011 to WD-020 — executability audit
# ---------------------------------------------------------------------------

def test_wd_011_no_executable_passes():
    idx = get_index()
    assert idx["executability_audit"]["EXECUTABLE_PASSES"] == 0


def test_wd_012_no_executable_fails():
    idx = get_index()
    assert idx["executability_audit"]["EXECUTABLE_FAILS"] == 0


def test_wd_013_no_executable_intermittent():
    idx = get_index()
    assert idx["executability_audit"]["EXECUTABLE_INTERMITTENT"] == 0


def test_wd_014_not_a_test_160():
    idx = get_index()
    assert idx["executability_audit"]["NOT_A_TEST"] == 160


def test_wd_015_not_executable_347():
    idx = get_index()
    assert idx["executability_audit"]["NOT_EXECUTABLE"] == 347


def test_wd_016_executability_sum():
    idx = get_index()
    ea = idx["executability_audit"]
    assert sum(ea.values()) == 507


def test_wd_017_no_executable_tests_flag():
    assert has_no_executable_tests() is True


def test_wd_018_blocked_artifact_backups():
    idx = get_index()
    assert idx["blocked_artifact_backups"] == 2
    assert len(idx["blocked_artifact_backup_paths"]) == 2


# ---------------------------------------------------------------------------
# WD-019 to WD-026 — population partition
# ---------------------------------------------------------------------------

def test_wd_019_partition_memory_interface():
    idx = get_index()
    assert idx["population_partition"]["BRODY_MEMORY_INTERFACE_MODULES"] == 496


def test_wd_020_partition_governance_rule():
    idx = get_index()
    assert idx["population_partition"]["BRODY_GOVERNANCE_RULE_ARTIFACTS"] == 11


def test_wd_021_partition_total():
    idx = get_index()
    assert idx["population_partition"]["TOTAL"] == 507


def test_wd_022_partition_sum():
    idx = get_index()
    p = idx["population_partition"]
    assert p["BRODY_MEMORY_INTERFACE_MODULES"] + p["BRODY_GOVERNANCE_RULE_ARTIFACTS"] == 507


def test_wd_023_file_type_py_160():
    idx = get_index()
    assert idx["file_type_distribution"]["py_source_modules"] == 160


def test_wd_024_file_type_bak_2():
    idx = get_index()
    assert idx["file_type_distribution"]["bak_blocked_backups"] == 2


def test_wd_025_file_type_ps1_95():
    idx = get_index()
    assert idx["file_type_distribution"]["ps1_tooling_scripts"] == 95


def test_wd_026_partition_verified_from_census():
    idx = get_index()
    assert idx["population_partition"]["partition_verified_from_census"] is True


# ---------------------------------------------------------------------------
# WD-027 to WD-033 — relation distribution
# ---------------------------------------------------------------------------

def test_wd_027_memory_interface_linked_494():
    idx = get_index()
    assert idx["gate_v5_relation_distribution"]["MEMORY_INTERFACE_LINKED_TO_BRODY_RUNTIME"] == 494


def test_wd_028_governance_rule_linked_11():
    idx = get_index()
    assert idx["gate_v5_relation_distribution"]["GOVERNANCE_RULE_LINKED_TO_BRODY_RUNTIME"] == 11


def test_wd_029_blocked_artifact_backup_2():
    idx = get_index()
    assert idx["gate_v5_relation_distribution"]["BLOCKED_ARTIFACT_BACKUP"] == 2


def test_wd_030_relation_sum():
    idx = get_index()
    d = idx["gate_v5_relation_distribution"]
    assert sum(d.values()) == 507


# ---------------------------------------------------------------------------
# WD-031 to WD-045 — validator API: entries
# ---------------------------------------------------------------------------

def test_wd_031_get_source_module_entries_count():
    assert len(get_source_module_entries()) == 160


def test_wd_032_get_governance_rule_entries_count():
    assert len(get_governance_rule_entries()) == 11


def test_wd_033_get_blocked_backup_entries_count():
    blocked = get_blocked_backup_entries()
    assert len(blocked) == 2


def test_wd_034_blocked_backups_are_bak_files():
    blocked = get_blocked_backup_entries()
    for e in blocked:
        assert ".bak" in e["path"]
        assert "content_hydration_readonly" in e["path"]


def test_wd_035_all_entries_have_required_fields():
    required = {
        "path", "sha256", "role", "canonicality_status",
        "relation_type", "owner_subsystem", "status",
        "semantic_verdict", "executability_status",
    }
    for entry in get_entries():
        missing = required - set(entry.keys())
        assert not missing, f"{entry['path']} missing fields: {missing}"


def test_wd_036_all_paths_exist():
    results = validate_all_paths_exist()
    missing = [p for p, ok in results.items() if not ok]
    assert missing == [], f"Missing files: {missing}"


def test_wd_037_all_roles_valid():
    valid = {"MEMORY_INTERFACE_SOURCE_MODULE", "MEMORY_INTERFACE_ARTIFACT", "GOVERNANCE_RULE_ARTIFACT"}
    for e in get_entries():
        assert e["role"] in valid, f"Invalid role for {e['path']}: {e['role']}"


def test_wd_038_all_executability_valid():
    valid = {"EXECUTABLE_PASSES", "EXECUTABLE_FAILS", "EXECUTABLE_INTERMITTENT", "NOT_A_TEST", "NOT_EXECUTABLE"}
    for e in get_entries():
        assert e["executability_status"] in valid


def test_wd_039_all_relation_types_valid():
    valid = {
        "MEMORY_INTERFACE_LINKED_TO_BRODY_RUNTIME",
        "GOVERNANCE_RULE_LINKED_TO_BRODY_RUNTIME",
        "BLOCKED_ARTIFACT_BACKUP",
    }
    for e in get_entries():
        assert e["relation_type"] in valid, f"Invalid relation for {e['path']}: {e['relation_type']}"


def test_wd_040_all_canonicality_canonical():
    for e in get_entries():
        assert e["canonicality_status"] == "CANONICAL"


def test_wd_041_all_status_indexed():
    for e in get_entries():
        assert e["status"] == "INDEXED"


def test_wd_042_py_entries_are_not_a_test():
    for e in get_entries():
        if e["path"].endswith(".py"):
            assert e["executability_status"] == "NOT_A_TEST", f"{e['path']} should be NOT_A_TEST"


def test_wd_043_non_py_entries_are_not_executable():
    for e in get_entries():
        if not e["path"].endswith(".py"):
            assert e["executability_status"] == "NOT_EXECUTABLE", f"{e['path']} should be NOT_EXECUTABLE"


def test_wd_044_sha256_format():
    for e in get_entries():
        sha = e["sha256"]
        assert len(sha) == 64
        assert all(c in "0123456789abcdef" for c in sha)


def test_wd_045_get_artifact_entries():
    arts = get_artifact_entries()
    # includes both MEMORY_INTERFACE_ARTIFACT with NOT_EXECUTABLE (bak included)
    blocked = [e for e in arts if e.get("relation_type") == "BLOCKED_ARTIFACT_BACKUP"]
    assert len(blocked) == 2


# ---------------------------------------------------------------------------
# WD-046 to WD-052 — summary
# ---------------------------------------------------------------------------

def test_wd_046_summary_total():
    s = summary()
    assert s["total"] == 507


def test_wd_047_summary_source_modules():
    s = summary()
    assert s["source_modules_count"] == 160


def test_wd_048_summary_blocked_backup():
    s = summary()
    assert s["blocked_backup_count"] == 2


def test_wd_049_summary_not_executable():
    s = summary()
    assert s["not_executable_count"] == 347


def test_wd_050_summary_not_a_test():
    s = summary()
    assert s["not_a_test_count"] == 160


def test_wd_051_summary_by_family():
    s = summary()
    assert s["by_family"]["BRODY_MEMORY_INTERFACE"] == 496
    assert s["by_family"]["BRODY_GOVERNANCE_RULE"] == 11


# ---------------------------------------------------------------------------
# WD-052 to WD-058 — blocker queue
# ---------------------------------------------------------------------------

def test_wd_052_blocker_queue_count():
    bq = get_blocker_queue()
    assert len(bq) == 2


def test_wd_053_blocker_ids():
    bq = get_blocker_queue()
    ids = {b["blocker_id"] for b in bq}
    assert "WD-BLK-001" in ids
    assert "WD-BLK-002" in ids


def test_wd_054_blk001_type():
    bq = get_blocker_queue()
    blk001 = next(b for b in bq if b["blocker_id"] == "WD-BLK-001")
    assert blk001["blocker_type"] == "BLOCKED_ARTIFACT_BACKUP"
    assert "content_hydration_readonly" in blk001["path"]


def test_wd_055_blk002_type():
    bq = get_blocker_queue()
    blk002 = next(b for b in bq if b["blocker_id"] == "WD-BLK-002")
    assert blk002["blocker_type"] == "BLOCKED_ARTIFACT_BACKUP"


def test_wd_056_blockers_preexisting():
    bq = get_blocker_queue()
    for b in bq:
        assert b["preexisting_before_wave005"] is True


def test_wd_057_no_safe_fixes():
    bq = get_blocker_queue()
    for b in bq:
        assert b["safe_fix_possible"] is False


# ---------------------------------------------------------------------------
# WD-058 to WD-068 — scope reconciliation & remaining population
# ---------------------------------------------------------------------------

def test_wd_058_scope_brody_primary_902():
    sr = get_scope_reconciliation()
    assert sr["brody_primary_total"] == 902


def test_wd_059_scope_wave005a_11():
    sr = get_scope_reconciliation()
    assert sr["wave005a_processed"] == 11


def test_wd_060_scope_wave005b_144():
    sr = get_scope_reconciliation()
    assert sr["wave005b_accounted"] == 144


def test_wd_061_scope_wave005c_51():
    sr = get_scope_reconciliation()
    assert sr["wave005c_accounted"] == 51


def test_wd_062_scope_wave005d_primary_506():
    sr = get_scope_reconciliation()
    assert sr["wave005d_accounted"] == 506
    assert sr["wave005d_all_matrix_rows"] == 507
    assert sr["wave005d_secondary_relation_rows"] == 1


def test_wd_063_scope_census_sum_d_to_f():
    sr = get_scope_reconciliation()
    assert sr["census_physical_sum_d_to_f"] == 697


def test_wd_064_scope_census_vs_primary_delta():
    sr = get_scope_reconciliation()
    assert sr["census_vs_primary_delta"] == 10


def test_wd_065_remaining_wave005e():
    rp = get_remaining_population()
    assert rp["WAVE005_E"] == 124


def test_wd_066_remaining_wave005f():
    rp = get_remaining_population()
    assert rp["WAVE005_F"] == 66


def test_wd_067_remaining_total():
    rp = get_remaining_population()
    assert rp["total_remaining"] == 190


def test_wd_068_remaining_ef_sum():
    rp = get_remaining_population()
    assert rp["WAVE005_E"] + rp["WAVE005_F"] == 190


# ---------------------------------------------------------------------------
# WD-069 to WD-075 — governance invariants
# ---------------------------------------------------------------------------

def test_wd_069_non_sovereign_invariant():
    gi = get_governance_invariants()
    assert gi["NON_SOVEREIGN"] is True


def test_wd_070_documentary_index_only():
    gi = get_governance_invariants()
    assert gi["documentary_index_only"] is True


def test_wd_071_no_agent_invoked():
    gi = get_governance_invariants()
    assert gi["no_agent_invoked"] is True


def test_wd_072_no_model_called():
    gi = get_governance_invariants()
    assert gi["no_model_called"] is True


def test_wd_073_no_memory_written():
    gi = get_governance_invariants()
    assert gi["no_memory_written"] is True


# ---------------------------------------------------------------------------
# WD-074 to WD-080 — regression: global state invariants
# ---------------------------------------------------------------------------

def test_wd_074_census_902_preserved():
    root = Path(__file__).resolve()
    for p in root.parents:
        if (p / ".git").exists():
            break
    with open(p / "periphery/agents/agents_file_wiring_global_state.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["global_summary"]["current_active_brody_primary"] == 902


def test_wd_075_global_registration_blocked():
    root = Path(__file__).resolve()
    for p in root.parents:
        if (p / ".git").exists():
            break
    with open(p / "periphery/agents/agents_file_wiring_artifact_index.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["global_registration_blocked"] is True


def test_wd_076_wave005c_still_partially_blocked():
    root = Path(__file__).resolve()
    for p in root.parents:
        if (p / ".git").exists():
            break
    with open(p / "periphery/agents/agents_file_wiring_global_state.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["wave_registry"]["WAVE005_C"]["status"] == "AGENTS_FILE_WIRING_WAVE005_C_PARTIALLY_BLOCKED"


def test_wd_077_wave005d_registered_in_global_state():
    root = Path(__file__).resolve()
    for p in root.parents:
        if (p / ".git").exists():
            break
    with open(p / "periphery/agents/agents_file_wiring_global_state.json", encoding="utf-8") as f:
        data = json.load(f)
    assert "WAVE005_D" in data["wave_registry"]
    assert data["wave_registry"]["WAVE005_D"]["status"] == "AGENTS_FILE_WIRING_WAVE005_D_PARTIALLY_BLOCKED"
    assert data["wave_registry"]["WAVE005_D"]["functional_files_accounted"] == 506
    assert data["wave_registry"]["WAVE005_D"]["all_matrix_rows"] == 507
    assert data["wave_registry"]["WAVE005_D"]["secondary_relation_rows"] == 1


def test_wd_078_wave005d_in_artifact_index():
    root = Path(__file__).resolve()
    for p in root.parents:
        if (p / ".git").exists():
            break
    with open(p / "periphery/agents/agents_file_wiring_artifact_index.json", encoding="utf-8") as f:
        data = json.load(f)
    assert "WAVE005_D" in data["wave_file_manifests"]
    assert data["wave_file_manifests"]["WAVE005_D"]["status"] == "AGENTS_FILE_WIRING_WAVE005_D_PARTIALLY_BLOCKED"


def test_wd_079_wave005d_blockers_2():
    root = Path(__file__).resolve()
    for p in root.parents:
        if (p / ".git").exists():
            break
    with open(p / "periphery/agents/agents_file_wiring_global_state.json", encoding="utf-8") as f:
        data = json.load(f)
    w5d = data["wave_registry"]["WAVE005_D"]
    assert w5d["files_with_explicit_blocker"] == 2
    assert w5d["blocked_artifact_backups"] == 2


def test_wd_080_gross_wave_index_entries_updated():
    root = Path(__file__).resolve()
    for p in root.parents:
        if (p / ".git").exists():
            break
    with open(p / "periphery/agents/agents_file_wiring_global_state.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["global_summary"]["gross_wave_index_entries"] == 1734
    assert data["global_summary"]["gross_documentary_rows_including_secondary"] == 1735
