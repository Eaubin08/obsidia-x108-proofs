"""
Tests for WAVE005_C index: BRODY_PROTOCOLS_CONNECTORS_SCRIPTS_INDEX_V1

WC-001 to WC-090 — documentary, read-only, no runtime.
"""
import json
from pathlib import Path
import pytest

from periphery.agents.brody_protocols_connectors_scripts import (
    get_index,
    get_entries,
    get_protocol_entries,
    get_tooling_entries,
    get_test_entries,
    get_failing_test_entries,
    get_blocked_source_entries,
    get_blocker_queue,
    get_governance_invariants,
    get_scope_reconciliation,
    get_remaining_population,
    is_scope_complete,
    get_covered_slice,
    summary,
    validate_all_paths_exist,
)


# ---------------------------------------------------------------------------
# WC-001 to WC-010 — index metadata
# ---------------------------------------------------------------------------

def test_wc_001_index_id():
    idx = get_index()
    assert idx["index_id"] == "BRODY_PROTOCOLS_CONNECTORS_SCRIPTS_INDEX_V1"


def test_wc_002_schema_version():
    idx = get_index()
    assert idx["schema_version"] == "1.0"


def test_wc_003_campaign():
    idx = get_index()
    assert idx["campaign"] == "AGENTS_FILE_WIRING"


def test_wc_004_covered_slice():
    assert get_covered_slice() == "WAVE005_C_BRODY_PROTOCOLS_CONNECTORS_AND_SCRIPTS"


def test_wc_005_scope_complete_false():
    assert is_scope_complete() is False


def test_wc_006_authority_non_sovereign():
    idx = get_index()
    assert idx["authority"] == "NON_SOVEREIGN"


def test_wc_007_non_sovereign_flags():
    idx = get_index()
    assert idx["can_decide"] is False
    assert idx["can_act"] is False
    assert idx["emits_act"] is False
    assert idx["memory_write"] is False
    assert idx["model_calls"] == 0
    assert idx["runtime_consumed"] is False


def test_wc_008_total_entries():
    idx = get_index()
    assert idx["total_entries"] == 51


def test_wc_009_entries_count_matches():
    assert len(get_entries()) == 51


def test_wc_010_files_with_explicit_blocker():
    idx = get_index()
    assert idx["files_with_explicit_blocker"] == 2


# ---------------------------------------------------------------------------
# WC-011 to WC-020 — executability audit
# ---------------------------------------------------------------------------

def test_wc_011_executable_passes():
    idx = get_index()
    assert idx["executability_audit"]["EXECUTABLE_PASSES"] == 24


def test_wc_012_executable_fails():
    idx = get_index()
    assert idx["executability_audit"]["EXECUTABLE_FAILS"] == 1


def test_wc_013_executable_intermittent_zero():
    idx = get_index()
    assert idx["executability_audit"]["EXECUTABLE_INTERMITTENT"] == 0


def test_wc_014_not_a_test():
    idx = get_index()
    assert idx["executability_audit"]["NOT_A_TEST"] == 8


def test_wc_015_not_executable():
    idx = get_index()
    assert idx["executability_audit"]["NOT_EXECUTABLE"] == 18


def test_wc_016_executability_sum():
    idx = get_index()
    ea = idx["executability_audit"]
    total = sum(ea.values())
    assert total == 51


def test_wc_017_failing_test_path():
    idx = get_index()
    fails = idx["executable_fails_paths"]
    assert len(fails) == 1
    assert "test_brody_education_pack_v1_readonly_adapter" in fails[0]


def test_wc_018_blocked_source_path():
    idx = get_index()
    blocked = idx["blocked_source_paths"]
    assert len(blocked) == 1
    assert "brody_memory_readonly_flow" in blocked[0]


def test_wc_019_consistent_failing_test_files():
    idx = get_index()
    assert idx["consistent_failing_test_files"] == 1


def test_wc_020_blocked_source_without_consumer_count():
    idx = get_index()
    assert idx["blocked_source_without_consumer"] == 1


# ---------------------------------------------------------------------------
# WC-021 to WC-030 — population partition
# ---------------------------------------------------------------------------

def test_wc_021_partition_protocol():
    idx = get_index()
    assert idx["population_partition"]["BRODY_PROTOCOL_SOURCE_MODULES"] == 3


def test_wc_022_partition_tooling():
    idx = get_index()
    assert idx["population_partition"]["BRODY_DEVELOPMENT_TOOLING_MODULES"] == 23


def test_wc_023_partition_test():
    idx = get_index()
    assert idx["population_partition"]["BRODY_TEST_FILES"] == 25


def test_wc_024_partition_total():
    idx = get_index()
    p = idx["population_partition"]
    assert p["TOTAL"] == 51


def test_wc_025_partition_sum():
    idx = get_index()
    p = idx["population_partition"]
    assert p["BRODY_PROTOCOL_SOURCE_MODULES"] + p["BRODY_DEVELOPMENT_TOOLING_MODULES"] + p["BRODY_TEST_FILES"] == 51


def test_wc_026_partition_verified_from_census():
    idx = get_index()
    assert idx["population_partition"]["partition_verified_from_census"] is True


# ---------------------------------------------------------------------------
# WC-027 to WC-035 — relation distribution
# ---------------------------------------------------------------------------

def test_wc_027_protocol_linked():
    idx = get_index()
    assert idx["gate_v5_relation_distribution"]["PROTOCOL_LINKED_TO_BRODY_RUNTIME"] == 2


def test_wc_028_blocked_source_relation():
    idx = get_index()
    assert idx["gate_v5_relation_distribution"]["BLOCKED_SOURCE_WITHOUT_CONSUMER"] == 1


def test_wc_029_tooling_linked():
    idx = get_index()
    assert idx["gate_v5_relation_distribution"]["DEVELOPMENT_TOOLING_LINKED_TO_BRODY_RUNTIME"] == 23


def test_wc_030_test_linked():
    idx = get_index()
    assert idx["gate_v5_relation_distribution"]["EXECUTABLE_TEST_LINKED_TO_SOURCE_COMPONENT"] == 25


def test_wc_031_relation_sum():
    idx = get_index()
    d = idx["gate_v5_relation_distribution"]
    assert sum(d.values()) == 51


# ---------------------------------------------------------------------------
# WC-032 to WC-045 — validator API: entries
# ---------------------------------------------------------------------------

def test_wc_032_get_protocol_entries_count():
    assert len(get_protocol_entries()) == 3


def test_wc_033_get_tooling_entries_count():
    assert len(get_tooling_entries()) == 23


def test_wc_034_get_test_entries_count():
    assert len(get_test_entries()) == 25


def test_wc_035_get_failing_test_entries_count():
    fails = get_failing_test_entries()
    assert len(fails) == 1


def test_wc_036_failing_test_is_education_pack():
    fails = get_failing_test_entries()
    assert "test_brody_education_pack_v1_readonly_adapter" in fails[0]["path"]


def test_wc_037_get_blocked_source_entries_count():
    blocked = get_blocked_source_entries()
    assert len(blocked) == 1


def test_wc_038_blocked_source_is_memory_readonly_flow():
    blocked = get_blocked_source_entries()
    assert "brody_memory_readonly_flow" in blocked[0]["path"]


def test_wc_039_all_entries_have_required_fields():
    required = {
        "path", "sha256", "role", "canonicality_status",
        "relation_type", "owner_subsystem", "status",
        "semantic_verdict", "executability_status",
    }
    for entry in get_entries():
        missing = required - set(entry.keys())
        assert not missing, f"{entry['path']} missing fields: {missing}"


def test_wc_040_all_paths_exist():
    results = validate_all_paths_exist()
    missing = [p for p, ok in results.items() if not ok]
    assert missing == [], f"Missing files: {missing}"


def test_wc_041_all_roles_valid():
    valid = {"PROTOCOL_SOURCE_MODULE", "DEVELOPMENT_TOOLING_MODULE", "EXECUTABLE_UNIT_TEST"}
    for e in get_entries():
        assert e["role"] in valid, f"Invalid role for {e['path']}: {e['role']}"


def test_wc_042_all_executability_valid():
    valid = {"EXECUTABLE_PASSES", "EXECUTABLE_FAILS", "EXECUTABLE_INTERMITTENT", "NOT_A_TEST", "NOT_EXECUTABLE"}
    for e in get_entries():
        assert e["executability_status"] in valid, f"Invalid executability for {e['path']}: {e['executability_status']}"


def test_wc_043_all_relation_types_valid():
    valid = {
        "PROTOCOL_LINKED_TO_BRODY_RUNTIME",
        "BLOCKED_SOURCE_WITHOUT_CONSUMER",
        "DEVELOPMENT_TOOLING_LINKED_TO_BRODY_RUNTIME",
        "EXECUTABLE_TEST_LINKED_TO_SOURCE_COMPONENT",
    }
    for e in get_entries():
        assert e["relation_type"] in valid, f"Invalid relation_type for {e['path']}: {e['relation_type']}"


def test_wc_044_all_canonicality_canonical():
    for e in get_entries():
        assert e["canonicality_status"] == "CANONICAL"


def test_wc_045_all_status_indexed():
    for e in get_entries():
        assert e["status"] == "INDEXED"


# ---------------------------------------------------------------------------
# WC-046 to WC-055 — summary
# ---------------------------------------------------------------------------

def test_wc_046_summary_total():
    s = summary()
    assert s["total"] == 51


def test_wc_047_summary_by_role():
    s = summary()
    assert s["by_role"]["PROTOCOL_SOURCE_MODULE"] == 3
    assert s["by_role"]["DEVELOPMENT_TOOLING_MODULE"] == 23
    assert s["by_role"]["EXECUTABLE_UNIT_TEST"] == 25


def test_wc_048_summary_executable_fails():
    s = summary()
    assert s["executable_fails_count"] == 1


def test_wc_049_summary_blocked_source():
    s = summary()
    assert s["blocked_source_count"] == 1


def test_wc_050_summary_not_executable():
    s = summary()
    assert s["not_executable_count"] == 18


def test_wc_051_summary_by_family():
    s = summary()
    assert s["by_family"]["BRODY_PROTOCOL"] == 3
    assert s["by_family"]["BRODY_DEVELOPMENT_TOOLING"] == 23
    assert s["by_family"]["BRODY_TEST"] == 25


# ---------------------------------------------------------------------------
# WC-052 to WC-060 — blocker queue
# ---------------------------------------------------------------------------

def test_wc_052_blocker_queue_count():
    bq = get_blocker_queue()
    assert len(bq) == 2


def test_wc_053_blocker_ids():
    bq = get_blocker_queue()
    ids = {b["blocker_id"] for b in bq}
    assert "WC-BLK-001" in ids
    assert "WC-BLK-002" in ids


def test_wc_054_blk001_is_failing_test():
    bq = get_blocker_queue()
    blk001 = next(b for b in bq if b["blocker_id"] == "WC-BLK-001")
    assert blk001["blocker_type"] == "EXECUTABLE_FAILS"
    assert "test_brody_education_pack_v1_readonly_adapter" in blk001["path"]


def test_wc_055_blk002_is_blocked_source():
    bq = get_blocker_queue()
    blk002 = next(b for b in bq if b["blocker_id"] == "WC-BLK-002")
    assert blk002["blocker_type"] == "BLOCKED_SOURCE_WITHOUT_CONSUMER"
    assert "brody_memory_readonly_flow" in blk002["path"]


def test_wc_056_blk001_preexisting():
    bq = get_blocker_queue()
    blk001 = next(b for b in bq if b["blocker_id"] == "WC-BLK-001")
    assert blk001["preexisting_before_wave005"] is True
    assert blk001["preexisting_commit"] == "ac29729"


def test_wc_057_no_safe_fixes():
    bq = get_blocker_queue()
    for b in bq:
        assert b["safe_fix_possible"] is False


# ---------------------------------------------------------------------------
# WC-058 to WC-070 — scope reconciliation & remaining population
# ---------------------------------------------------------------------------

def test_wc_058_scope_reconciliation_total():
    sr = get_scope_reconciliation()
    assert sr["current_active_total"] == 902


def test_wc_059_scope_reconciliation_wave005a():
    sr = get_scope_reconciliation()
    assert sr["wave005a_processed"] == 11


def test_wc_060_scope_reconciliation_wave005b():
    sr = get_scope_reconciliation()
    assert sr["wave005b_accounted"] == 144


def test_wc_061_scope_reconciliation_wave005c():
    sr = get_scope_reconciliation()
    assert sr["wave005c_accounted"] == 51


def test_wc_062_scope_reconciliation_remaining():
    sr = get_scope_reconciliation()
    assert sr["wave005d_to_f_remaining"] == 696


def test_wc_063_scope_reconciliation_sum():
    sr = get_scope_reconciliation()
    total = (
        sr["wave005a_processed"]
        + sr["wave005b_accounted"]
        + sr["wave005c_accounted"]
        + sr["wave005d_to_f_remaining"]
    )
    assert total == 902


def test_wc_064_remaining_population_wave005d():
    rp = get_remaining_population()
    assert rp["WAVE005_D"] == 506


def test_wc_065_remaining_population_wave005e():
    rp = get_remaining_population()
    assert rp["WAVE005_E"] == 124


def test_wc_066_remaining_population_wave005f():
    rp = get_remaining_population()
    assert rp["WAVE005_F"] == 66


def test_wc_067_remaining_population_total():
    rp = get_remaining_population()
    assert rp["total_remaining"] == 696


def test_wc_068_remaining_sum():
    rp = get_remaining_population()
    assert rp["WAVE005_D"] + rp["WAVE005_E"] + rp["WAVE005_F"] == 696


# ---------------------------------------------------------------------------
# WC-069 to WC-075 — governance invariants
# ---------------------------------------------------------------------------

def test_wc_069_non_sovereign_invariant():
    gi = get_governance_invariants()
    assert gi["NON_SOVEREIGN"] is True


def test_wc_070_documentary_index_only():
    gi = get_governance_invariants()
    assert gi["documentary_index_only"] is True


def test_wc_071_no_agent_invoked():
    gi = get_governance_invariants()
    assert gi["no_agent_invoked"] is True


def test_wc_072_no_model_called():
    gi = get_governance_invariants()
    assert gi["no_model_called"] is True


def test_wc_073_no_memory_written():
    gi = get_governance_invariants()
    assert gi["no_memory_written"] is True


def test_wc_074_no_runtime_consumed():
    gi = get_governance_invariants()
    assert gi["no_runtime_consumed"] is True


# ---------------------------------------------------------------------------
# WC-075 to WC-085 — spot checks on specific entries
# ---------------------------------------------------------------------------

def test_wc_075_brody_readonly_activation_is_protocol():
    entries = get_entries()
    e = next((x for x in entries if "brody_readonly_activation" in x["path"] and "test" not in x["path"]), None)
    assert e is not None
    assert e["role"] == "PROTOCOL_SOURCE_MODULE"
    assert e["relation_type"] == "PROTOCOL_LINKED_TO_BRODY_RUNTIME"
    assert e["executability_status"] == "NOT_A_TEST"


def test_wc_076_brody_source_context_bridge_is_protocol():
    entries = get_entries()
    e = next((x for x in entries if "brody_source_context_bridge" in x["path"]), None)
    assert e is not None
    assert e["role"] == "PROTOCOL_SOURCE_MODULE"
    assert e["relation_type"] == "PROTOCOL_LINKED_TO_BRODY_RUNTIME"


def test_wc_077_brody_memory_readonly_flow_blocked():
    entries = get_entries()
    e = next((x for x in entries if "brody_memory_readonly_flow" in x["path"]), None)
    assert e is not None
    assert e["relation_type"] == "BLOCKED_SOURCE_WITHOUT_CONSUMER"
    assert e["semantic_verdict"] == "BLOCKED_NO_CONSUMER"


def test_wc_078_ps1_scripts_not_executable():
    entries = get_entries()
    ps1_entries = [e for e in entries if e["path"].endswith(".ps1")]
    assert len(ps1_entries) == 16
    for e in ps1_entries:
        assert e["executability_status"] == "NOT_EXECUTABLE", f"{e['path']} should be NOT_EXECUTABLE"


def test_wc_079_md_json_not_executable():
    entries = get_entries()
    non_py = [e for e in entries if e["path"].endswith(".md") or e["path"].endswith(".json")]
    assert len(non_py) == 2
    for e in non_py:
        assert e["executability_status"] == "NOT_EXECUTABLE"


def test_wc_080_education_pack_fails():
    fails = get_failing_test_entries()
    e = fails[0]
    assert e["executability_status"] == "EXECUTABLE_FAILS"
    assert e["semantic_verdict"] == "BLOCKED_PREEXISTING_FAILURE"
    assert "blocker" in e


def test_wc_081_cic_brody_readonly_binding_passes():
    entries = get_entries()
    e = next((x for x in entries if "test_cic_brody_readonly_binding_v0" in x["path"]), None)
    assert e is not None
    assert e["executability_status"] == "EXECUTABLE_PASSES"


def test_wc_082_secret_scrubber_passes():
    entries = get_entries()
    e = next((x for x in entries if "test_brody_v3_secret_scrubber" in x["path"]), None)
    assert e is not None
    assert e["executability_status"] == "EXECUTABLE_PASSES"


def test_wc_083_tooling_py_not_a_test():
    entries = get_entries()
    tooling_py = [
        e for e in entries
        if e["role"] == "DEVELOPMENT_TOOLING_MODULE"
        and e["path"].endswith(".py")
    ]
    assert len(tooling_py) == 5
    for e in tooling_py:
        assert e["executability_status"] == "NOT_A_TEST"


def test_wc_084_all_test_entries_have_executable_status():
    for e in get_test_entries():
        assert e["executability_status"] in {"EXECUTABLE_PASSES", "EXECUTABLE_FAILS", "EXECUTABLE_INTERMITTENT"}


def test_wc_085_sha256_format():
    for e in get_entries():
        sha = e["sha256"]
        assert len(sha) == 64, f"Bad SHA256 for {e['path']}: {sha!r}"
        assert all(c in "0123456789abcdef" for c in sha), f"Non-hex SHA256 for {e['path']}"


# ---------------------------------------------------------------------------
# WC-086 to WC-090 — regression: global registration blocker superseded
# ---------------------------------------------------------------------------

def test_wc_086_global_registration_blocked_superseded():
    root = Path(__file__).resolve()
    for p in root.parents:
        if (p / ".git").exists():
            break
    artifact_idx = p / "periphery" / "agents" / "agents_file_wiring_artifact_index.json"
    with open(artifact_idx, encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("global_registration_blocked") is False


def test_wc_087_census_902_preserved():
    root = Path(__file__).resolve()
    for p in root.parents:
        if (p / ".git").exists():
            break
    global_state = p / "periphery" / "agents" / "agents_file_wiring_global_state.json"
    with open(global_state, encoding="utf-8") as f:
        data = json.load(f)
    assert data["global_summary"]["current_active_brody_primary"] == 902


def test_wc_088_wave005b_still_partially_blocked():
    root = Path(__file__).resolve()
    for p in root.parents:
        if (p / ".git").exists():
            break
    global_state = p / "periphery" / "agents" / "agents_file_wiring_global_state.json"
    with open(global_state, encoding="utf-8") as f:
        data = json.load(f)
    assert data["wave_registry"]["WAVE005_B"]["status"] == "AGENTS_FILE_WIRING_WAVE005_B_PARTIALLY_BLOCKED"


def test_wc_089_wave005c_registered_in_global_state():
    root = Path(__file__).resolve()
    for p in root.parents:
        if (p / ".git").exists():
            break
    global_state = p / "periphery" / "agents" / "agents_file_wiring_global_state.json"
    with open(global_state, encoding="utf-8") as f:
        data = json.load(f)
    assert "WAVE005_C" in data["wave_registry"]
    assert data["wave_registry"]["WAVE005_C"]["status"] == "AGENTS_FILE_WIRING_WAVE005_C_PARTIALLY_BLOCKED"


def test_wc_090_wave005c_registered_in_artifact_index():
    root = Path(__file__).resolve()
    for p in root.parents:
        if (p / ".git").exists():
            break
    artifact_idx = p / "periphery" / "agents" / "agents_file_wiring_artifact_index.json"
    with open(artifact_idx, encoding="utf-8") as f:
        data = json.load(f)
    manifests = data["wave_file_manifests"]
    assert "WAVE005_C" in manifests
    assert manifests["WAVE005_C"]["status"] == "AGENTS_FILE_WIRING_WAVE005_C_PARTIALLY_BLOCKED"
