"""
Wave005_B — BRODY_INTEGRATION_RUNTIME_AND_API_SYSTEM index validation tests.

Verifies: index structure, population count, role taxonomy, executability distribution,
SHA256 integrity, governance claims, and scope reconciliation.
"""
from __future__ import annotations

from pathlib import Path

import periphery.agents.brody_integration_runtime_api_system as biras


# ---------------------------------------------------------------------------
# WB-001 — Index metadata
# ---------------------------------------------------------------------------

def test_wb_001_index_loads():
    idx = biras.get_index()
    assert idx["index_id"] == "BRODY_INTEGRATION_RUNTIME_API_SYSTEM_INDEX_V1"


def test_wb_002_schema_version():
    idx = biras.get_index()
    assert idx["schema_version"] == "1.0"


def test_wb_003_authority_non_sovereign():
    idx = biras.get_index()
    assert idx["authority"] == "NON_SOVEREIGN"


def test_wb_004_non_sovereign_flags():
    idx = biras.get_index()
    assert idx["can_decide"] is False
    assert idx["can_act"] is False
    assert idx["emits_act"] is False
    assert idx["memory_write"] is False
    assert idx["model_calls"] == 0
    assert idx["runtime_consumed"] is False


def test_wb_005_subsystem():
    idx = biras.get_index()
    assert idx["subsystem"] == "BRODY_INTEGRATION_RUNTIME_AND_API_SYSTEM"


def test_wb_006_wave():
    idx = biras.get_index()
    assert idx["wave"] == "WAVE005"


def test_wb_007_wave_role():
    idx = biras.get_index()
    assert idx["wave_role"] == "WAVE005_B"


def test_wb_008_covered_slice():
    assert biras.get_covered_slice() == "WAVE005_B_BRODY_INTEGRATION_RUNTIME_AND_API_TESTS"


# ---------------------------------------------------------------------------
# WB-010 — Population count
# ---------------------------------------------------------------------------

def test_wb_010_total_population():
    entries = biras.get_entries()
    assert len(entries) == 144


def test_wb_011_population_audit_total():
    idx = biras.get_index()
    assert idx["population_audit"]["total"] == 144


def test_wb_012_population_audit_source_test_split():
    idx = biras.get_index()
    assert idx["population_audit"]["source_files"] == 70
    assert idx["population_audit"]["test_files"] == 74


def test_wb_013_integration_runtime_count():
    idx = biras.get_index()
    assert idx["population_audit"]["integration_runtime_modules"] == 5


def test_wb_014_api_protocol_count():
    idx = biras.get_index()
    assert idx["population_audit"]["api_protocol_sources"] == 65


# ---------------------------------------------------------------------------
# WB-020 — All paths exist on disk
# ---------------------------------------------------------------------------

def test_wb_020_all_paths_exist():
    result = biras.validate_all_paths_exist()
    missing = [p for p, ok in result.items() if not ok]
    assert missing == [], f"Missing files: {missing}"


# ---------------------------------------------------------------------------
# WB-030 — Role taxonomy
# ---------------------------------------------------------------------------

def test_wb_030_role_distribution():
    idx = biras.get_index()
    dist = idx["gate_v5_distribution"]
    assert dist["INTEGRATION_RUNTIME_READONLY_MODULE"] == 5
    assert dist["API_PROTOCOL_SOURCE_MODULE"] == 65
    assert dist["EXECUTABLE_UNIT_TEST"] == 74


def test_wb_031_integration_runtime_entries():
    entries = biras.get_integration_runtime_entries()
    assert len(entries) == 5
    paths = {e["path"] for e in entries}
    assert "periphery/brody_runtime/__init__.py" in paths
    assert "periphery/brody_runtime/f32_full_runtime_integration_readonly_packet.py" in paths


def test_wb_032_api_protocol_entries():
    entries = biras.get_api_protocol_entries()
    assert len(entries) == 65


def test_wb_033_test_entries():
    entries = biras.get_test_entries()
    assert len(entries) == 74


def test_wb_034_no_forbidden_roles():
    entries = biras.get_entries()
    forbidden = {"SOURCE_COMPONENT", "STATIC_PLACEHOLDER", "EXECUTABLE_PASSES", "EXECUTABLE_FAILS"}
    violations = [e["path"] for e in entries if e["role"] in forbidden]
    assert violations == [], f"Forbidden roles found: {violations}"


def test_wb_035_brody_bridge_is_api_protocol():
    entries = biras.get_api_protocol_entries()
    paths = {e["path"] for e in entries}
    assert "periphery/brody_bridge.py" in paths


# ---------------------------------------------------------------------------
# WB-040 — Executability distribution
# ---------------------------------------------------------------------------

def test_wb_040_executability_distribution():
    idx = biras.get_index()
    audit = idx["executability_audit"]
    assert audit["EXECUTABLE_PASSES"] == 66
    assert audit["EXECUTABLE_FAILS"] == 4, "4 files consistently fail"
    assert audit["EXECUTABLE_INTERMITTENT"] == 4, "4 files intermittently fail (flaky)"
    assert audit["NOT_A_TEST"] == 70
    assert audit["NOT_EXECUTABLE"] == 0


def test_wb_041_source_files_not_a_test():
    source_roles = {"INTEGRATION_RUNTIME_READONLY_MODULE", "API_PROTOCOL_SOURCE_MODULE"}
    entries = biras.get_entries()
    for e in entries:
        if e["role"] in source_roles:
            assert e["executability_status"] == "NOT_A_TEST", (
                f"{e['path']} should be NOT_A_TEST, got {e['executability_status']}"
            )


def test_wb_042_executable_fails_count():
    failing = biras.get_failing_test_entries()
    assert len(failing) == 4, "4 files have CONSISTENT failures"


def test_wb_042b_executable_intermittent_count():
    intermittent = biras.get_intermittent_test_entries()
    assert len(intermittent) == 4, "4 files have INTERMITTENT (flaky) failures"


def test_wb_043_known_consistent_failing_tests_declared():
    failing_paths = {e["path"] for e in biras.get_failing_test_entries()}
    expected_consistent_fails = {
        "tests/api/test_brody_automation_orchestrator.py",
        "tests/api/test_brody_memory_candidate_automation.py",
        "tests/api/test_brody_no_invented_metrics.py",
        "tests/api/test_brody_payload_packetization.py",
    }
    assert failing_paths == expected_consistent_fails


def test_wb_043b_known_intermittent_tests_declared():
    intermittent_paths = {e["path"] for e in biras.get_intermittent_test_entries()}
    expected_flaky = {
        "tests/api/test_brody_chat_readonly.py",
        "tests/api/test_brody_general_conversation_mode_readonly.py",
        "tests/api/test_brody_response_quality_fr.py",
        "tests/api/test_brody_response_source_not_frontend_mock.py",
    }
    assert intermittent_paths == expected_flaky


def test_wb_044_passing_tests_count():
    passing = biras.get_entries_by_executability("EXECUTABLE_PASSES")
    assert len(passing) == 66


def test_wb_045_all_test_files_in_tests_api():
    test_entries = biras.get_test_entries()
    for e in test_entries:
        assert e["path"].startswith("tests/api/"), (
            f"Test entry not in tests/api/: {e['path']}"
        )


# ---------------------------------------------------------------------------
# WB-050 — Relation types
# ---------------------------------------------------------------------------

def test_wb_050_relation_distribution():
    idx = biras.get_index()
    dist = idx["gate_v5_relation_distribution"]
    assert dist["INTEGRATION_RUNTIME_LINKED_TO_GOVERNANCE_INDEX"] == 5
    assert dist["API_PROTOCOL_LINKED_TO_GOVERNANCE_INDEX"] == 63  # 64 api - 1 blocked + 1 bridge = 65 protocol total; 1 has BLOCKED_SOURCE_WITHOUT_CONSUMER
    assert dist["BLOCKED_SOURCE_WITHOUT_CONSUMER"] == 1
    assert dist["EXECUTABLE_TEST_LINKED_TO_SOURCE_COMPONENT"] == 74


def test_wb_051_all_verdicts_true_documentary():
    entries = biras.get_entries()
    non_true = [e["path"] for e in entries if e["semantic_verdict"] != "TRUE_DOCUMENTARY_RELATION"]
    assert non_true == []


def test_wb_052_source_files_not_executable_test_relation():
    entries = biras.get_entries()
    source_relations = {
        "INTEGRATION_RUNTIME_LINKED_TO_GOVERNANCE_INDEX",
        "API_PROTOCOL_LINKED_TO_GOVERNANCE_INDEX",
    }
    for e in entries:
        if e["relation_type"] in source_relations:
            assert e["executability_status"] == "NOT_A_TEST"


# ---------------------------------------------------------------------------
# WB-060 — SHA256 integrity (spot checks)
# ---------------------------------------------------------------------------

def test_wb_060_all_sha256_valid():
    entries = biras.get_entries()
    failures = []
    for e in entries:
        if not biras.validate_sha256(e):
            failures.append(e["path"])
    assert failures == [], f"SHA256 mismatch for: {failures}"


# ---------------------------------------------------------------------------
# WB-070 — Governance claims
# ---------------------------------------------------------------------------

def test_wb_070_governance_claims_present():
    claims = biras.get_governance_invariants()
    assert len(claims) >= 4


def test_wb_071_brody_never_decides_claim():
    claims = biras.get_governance_invariants()
    assert "brody_never_decides" in claims


def test_wb_072_brody_never_emits_act_claim():
    claims = biras.get_governance_invariants()
    assert "brody_never_emits_act" in claims


def test_wb_073_runtime_readonly_claim():
    claims = biras.get_governance_invariants()
    assert "runtime_readonly" in claims


# ---------------------------------------------------------------------------
# WB-080 — Validator summary()
# ---------------------------------------------------------------------------

def test_wb_080_summary_total():
    s = biras.summary()
    assert s["total"] == 144


def test_wb_081_summary_executable_fails():
    s = biras.summary()
    assert s["executable_fails_count"] == 4, "4 consistent failures"
    assert s["executable_intermittent_count"] == 4, "4 flaky failures"


def test_wb_082_summary_source_files():
    s = biras.summary()
    assert s["source_files_count"] == 70


def test_wb_083_summary_by_role_keys():
    s = biras.summary()
    assert "INTEGRATION_RUNTIME_READONLY_MODULE" in s["by_role"]
    assert "API_PROTOCOL_SOURCE_MODULE" in s["by_role"]
    assert "EXECUTABLE_UNIT_TEST" in s["by_role"]


# ---------------------------------------------------------------------------
# WB-090 — Scope reconciliation
# ---------------------------------------------------------------------------

def test_wb_090_scope_complete_is_false():
    assert biras.is_scope_complete() is False


def test_wb_091_scope_reconciliation_present():
    rec = biras.get_scope_reconciliation()
    assert rec != {}
    assert "current_active_total" in rec
    assert "wave005_b_functional_total" in rec
    assert "wave005_b_indexed_entries" in rec


def test_wb_092_scope_current_active_total():
    rec = biras.get_scope_reconciliation()
    assert rec["current_active_total"] == 902


def test_wb_093_wave005b_functional_total():
    rec = biras.get_scope_reconciliation()
    assert rec["wave005_b_functional_total"] == 144
    assert rec["wave005_b_indexed_entries"] == 144


def test_wb_094_no_double_count():
    rec = biras.get_scope_reconciliation()
    assert rec["double_counted_silent"] == []
    assert rec["unaccounted_files"] == 0


def test_wb_095_accounting_adds_up():
    rec = biras.get_scope_reconciliation()
    rem = biras.get_remaining_population()
    wave_a = rec["files_already_processed_by_waves_001_to_005a"]
    wave_b = rec["wave005_b_functional_total"]
    remaining = rem["total_remaining"]
    current = rec["current_active_total"]
    assert wave_a + wave_b + remaining == current, (
        f"{wave_a} + {wave_b} + {remaining} != {current}"
    )


def test_wb_096_remaining_population():
    rem = biras.get_remaining_population()
    assert rem["WAVE005_C_BRODY_PROTOCOLS_CONNECTORS_AND_SCRIPTS"] == 51
    assert rem["WAVE005_D_BRODY_MEMORY_INTERFACE_AND_SPECS"] == 506
    assert rem["WAVE005_E_BRODY_DOCUMENTATION_ARCHITECTURE_AND_REPORTS"] == 124
    assert rem["WAVE005_F_BRODY_LEGACY_ARCHIVE_TOOLING_AND_REVIEW"] == 66
    assert rem["total_remaining"] == 747


def test_wb_097_wave005b_source_test_partition():
    rec = biras.get_scope_reconciliation()
    assert rec["wave005_b_source_files"] == 70
    assert rec["wave005_b_test_files"] == 74
    assert rec["wave005_b_source_files"] + rec["wave005_b_test_files"] == 144


# ---------------------------------------------------------------------------
# WB-100 — Scope: Wave005_B contains only brody_runtime and obsidia_api
# ---------------------------------------------------------------------------

def test_wb_100_no_brody_core_in_b():
    """Wave005_B must not contain periphery/brody/ files (those are Wave005_A)."""
    entries = biras.get_entries()
    wrong = [e["path"] for e in entries if "periphery/brody/" in e["path"]
             and "brody_runtime" not in e["path"] and "brody_bridge" not in e["path"]]
    assert wrong == [], f"Wave005_A files in Wave005_B: {wrong}"


def test_wb_101_no_tests_periphery_in_b():
    """Wave005_B must not contain tests/periphery/ or tests/non_sovereignty/."""
    entries = biras.get_entries()
    wrong = [e["path"] for e in entries if e["path"].startswith("tests/periphery/")
             or e["path"].startswith("tests/non_sovereignty/")]
    assert wrong == [], f"Wave005_A test files in Wave005_B: {wrong}"


def test_wb_102_all_integration_runtime_in_brody_runtime():
    entries = biras.get_integration_runtime_entries()
    for e in entries:
        assert "brody_runtime" in e["path"], (
            f"Integration runtime entry not in brody_runtime/: {e['path']}"
        )


def test_wb_103_all_api_protocol_in_obsidia_api_or_periphery():
    entries = biras.get_api_protocol_entries()
    for e in entries:
        assert e["path"].startswith("apps/obsidia_api/") or e["path"].startswith("periphery/"), (
            f"API protocol entry outside expected dirs: {e['path']}"
        )


# ---------------------------------------------------------------------------
# WB-110 — Source/test partition proof
# ---------------------------------------------------------------------------

def test_wb_110_partition_proof_present():
    idx = biras.get_index()
    proof = idx.get("source_test_partition_proof", {})
    assert proof.get("SUM") == 144
    assert proof.get("TOTAL_SOURCE") == 70
    assert proof.get("TOTAL_TEST") == 74


def test_wb_111_partition_proof_verified_from_census():
    idx = biras.get_index()
    proof = idx["source_test_partition_proof"]
    assert proof["partition_verified_from_census"] is True
    assert proof["all_test_files_have_test_functions"] is True
    assert proof["all_test_files_collected_by_pytest"] is True


def test_wb_112_partition_families_consistent():
    idx = biras.get_index()
    proof = idx["source_test_partition_proof"]
    assert proof["BRODY_RUNTIME_SOURCE_MODULES"] == 5
    assert proof["BRODY_BRIDGE_SOURCE_MODULES"] == 1
    assert proof["BRODY_API_SOURCE_MODULES_IN_APPS"] == 64
    assert proof["BRODY_API_ROUTE_FILES"] == 2
    assert proof["BRODY_API_TEST_FILES"] == 74
    assert proof["OTHER_TEST_FILES"] == 0


# ---------------------------------------------------------------------------
# WB-120 — Blocker queue and partially blocked status
# ---------------------------------------------------------------------------

def test_wb_120_blocker_queue_present():
    queue = biras.get_blocker_queue()
    assert len(queue) == 9, f"Expected 9 blocker entries, got {len(queue)}"


def test_wb_121_blocker_consistent_failures_documented():
    queue = biras.get_blocker_queue()
    consistent = [b for b in queue if b.get("failure_type") == "CONSISTENT"]
    assert len(consistent) == 4


def test_wb_122_blocker_intermittent_failures_documented():
    queue = biras.get_blocker_queue()
    intermittent = [b for b in queue if b.get("failure_type") == "INTERMITTENT"]
    assert len(intermittent) == 4


def test_wb_123_blocked_source_without_consumer_documented():
    queue = biras.get_blocker_queue()
    source_blockers = [b for b in queue if b.get("failure_type") == "SOURCE_BLOCKER"]
    assert len(source_blockers) == 1
    assert source_blockers[0]["path"] == "apps/obsidia_api/brody_backend_response_composer.py"


def test_wb_124_no_safe_fix_declared():
    queue = biras.get_blocker_queue()
    safe_fixes = [b for b in queue if b.get("safe_to_fix_in_wave005b") is True]
    assert safe_fixes == [], f"No safe fix should exist: {safe_fixes}"


def test_wb_125_all_preexisting_failures():
    queue = biras.get_blocker_queue()
    test_blockers = [b for b in queue if b.get("failure_type") != "SOURCE_BLOCKER"]
    for b in test_blockers:
        assert "preexisting_commit" in b, f"Missing preexisting_commit for {b['path']}"


def test_wb_126_no_failing_file_marked_executable_passes():
    fails_paths = {
        e["path"] for e in biras.get_failing_test_entries()
    } | {
        e["path"] for e in biras.get_intermittent_test_entries()
    }
    passing = biras.get_entries_by_executability("EXECUTABLE_PASSES")
    for e in passing:
        assert e["path"] not in fails_paths, (
            f"File {e['path']} is in fails set but marked EXECUTABLE_PASSES"
        )


# ---------------------------------------------------------------------------
# WB-130 — Global registration blocker superseded (accounting error resolved)
# ---------------------------------------------------------------------------

def test_wb_130_global_registration_blocked_superseded():
    from pathlib import Path
    import json

    def _repo_root():
        here = Path(__file__).resolve()
        for p in here.parents:
            if (p / ".git").exists():
                return p
        raise RuntimeError("Cannot locate repo root")

    root = _repo_root()
    gs = json.loads((root / "periphery/agents/agents_file_wiring_global_state.json").read_text(encoding="utf-8"))
    assert gs["global_manifest_complete"] is True
    assert gs["global_relation_graph_complete"] is True
    ai = json.loads((root / "periphery/agents/agents_file_wiring_artifact_index.json").read_text(encoding="utf-8"))
    assert ai["global_registration_blocked"] is False
    assert ai["global_manifest_complete"] is True
    assert ai["global_relation_graph_complete"] is True


def test_wb_131_census_primary_unchanged():
    rec = biras.get_scope_reconciliation()
    assert rec["current_active_total"] == 902


def test_wb_132_c_to_f_remaining_correct():
    rem = biras.get_remaining_population()
    assert rem["total_remaining"] == 747
    assert rem["WAVE005_C_BRODY_PROTOCOLS_CONNECTORS_AND_SCRIPTS"] == 51
    assert rem["WAVE005_D_BRODY_MEMORY_INTERFACE_AND_SPECS"] == 506
    assert rem["WAVE005_E_BRODY_DOCUMENTATION_ARCHITECTURE_AND_REPORTS"] == 124
    assert rem["WAVE005_F_BRODY_LEGACY_ARCHIVE_TOOLING_AND_REVIEW"] == 66
