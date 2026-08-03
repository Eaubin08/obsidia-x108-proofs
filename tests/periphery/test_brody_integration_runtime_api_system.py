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
    assert audit["EXECUTABLE_FAILS"] == 8
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
    assert len(failing) == 8


def test_wb_043_known_failing_tests_declared():
    failing_paths = {e["path"] for e in biras.get_failing_test_entries()}
    expected_fails = {
        "tests/api/test_brody_automation_orchestrator.py",
        "tests/api/test_brody_chat_readonly.py",
        "tests/api/test_brody_general_conversation_mode_readonly.py",
        "tests/api/test_brody_memory_candidate_automation.py",
        "tests/api/test_brody_no_invented_metrics.py",
        "tests/api/test_brody_payload_packetization.py",
        "tests/api/test_brody_response_quality_fr.py",
        "tests/api/test_brody_response_source_not_frontend_mock.py",
    }
    assert failing_paths == expected_fails, (
        f"Failing paths mismatch:\n  expected={expected_fails}\n  got={failing_paths}"
    )


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
    assert dist["API_PROTOCOL_LINKED_TO_GOVERNANCE_INDEX"] == 65
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
    assert s["executable_fails_count"] == 8


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
