"""
Wave005 — BRODY_GOVERNANCE_ELEMENT_SYSTEM index validation tests.

Verifies: index structure, population count, role taxonomy, relation types,
executability distribution, SHA256 integrity, governance claims, and
non-modification of audit bus.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

import periphery.agents.brody_governance_element_system as bges


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _bus_path() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / ".git").exists():
            return p / "audit" / "world_action_bus.jsonl"
    raise RuntimeError("Cannot locate repo root")


# ---------------------------------------------------------------------------
# W5-001 — Index metadata
# ---------------------------------------------------------------------------

def test_w5_001_index_loads():
    idx = bges.get_index()
    assert idx["index_id"] == "BRODY_GOVERNANCE_ELEMENT_SYSTEM_INDEX_V1"


def test_w5_002_schema_version():
    idx = bges.get_index()
    assert idx["schema_version"] == "1.0"


def test_w5_003_authority_non_sovereign():
    idx = bges.get_index()
    assert idx["authority"] == "NON_SOVEREIGN"


def test_w5_004_non_sovereign_flags():
    idx = bges.get_index()
    assert idx["can_decide"] is False
    assert idx["can_act"] is False
    assert idx["emits_act"] is False
    assert idx["memory_write"] is False
    assert idx["model_calls"] == 0
    assert idx["runtime_consumed"] is False


def test_w5_005_subsystem():
    idx = bges.get_index()
    assert idx["subsystem"] == "BRODY_GOVERNANCE_ELEMENT_SYSTEM"


def test_w5_006_wave():
    idx = bges.get_index()
    assert idx["wave"] == "WAVE005"


# ---------------------------------------------------------------------------
# W5-010 — Population count
# ---------------------------------------------------------------------------

def test_w5_010_total_population():
    entries = bges.get_entries()
    assert len(entries) == 11


def test_w5_011_population_audit_total():
    idx = bges.get_index()
    assert idx["population_audit"]["total"] == 11


def test_w5_012_population_audit_source_test_split():
    idx = bges.get_index()
    assert idx["population_audit"]["source_files"] == 6
    assert idx["population_audit"]["test_files"] == 5


def test_w5_013_test_count_total():
    idx = bges.get_index()
    assert idx["population_audit"]["test_count_total"] == 25


# ---------------------------------------------------------------------------
# W5-020 — All paths exist on disk
# ---------------------------------------------------------------------------

def test_w5_020_all_paths_exist():
    result = bges.validate_all_paths_exist()
    missing = [p for p, ok in result.items() if not ok]
    assert missing == [], f"Missing files: {missing}"


# ---------------------------------------------------------------------------
# W5-030 — Role taxonomy
# ---------------------------------------------------------------------------

def test_w5_030_no_forbidden_roles():
    entries = bges.get_entries()
    forbidden = {"SOURCE_COMPONENT", "STATIC_PLACEHOLDER", "EXECUTABLE_PASSES", "EXECUTABLE_FAILS"}
    violations = [e["path"] for e in entries if e["role"] in forbidden]
    assert violations == [], f"Forbidden roles found: {violations}"


def test_w5_031_role_distribution():
    idx = bges.get_index()
    dist = idx["gate_v5_distribution"]
    assert dist["TEST_CONFIGURATION"] == 5
    assert dist["STATIC_PROOF_ARTIFACT"] == 1
    assert dist["EXECUTABLE_UNIT_TEST"] == 2
    assert dist["EXECUTABLE_NEGATIVE_TEST"] == 3


def test_w5_032_static_proof_artifact_is_response_contract():
    entries = bges.get_static_proof_entries()
    assert len(entries) == 1
    assert entries[0]["path"] == "periphery/brody/brody_response_contract.py"


def test_w5_033_negative_tests_are_non_sovereignty():
    entries = bges.get_negative_test_entries()
    assert len(entries) == 3
    paths = {e["path"] for e in entries}
    assert "tests/non_sovereignty/test_brody_no_act.py" in paths
    assert "tests/non_sovereignty/test_brody_no_decision.py" in paths
    assert "tests/non_sovereignty/test_brody_response_never_emits_verdict.py" in paths


# ---------------------------------------------------------------------------
# W5-040 — Executability distribution
# ---------------------------------------------------------------------------

def test_w5_040_executability_distribution():
    idx = bges.get_index()
    audit = idx["executability_audit"]
    assert audit["EXECUTABLE_PASSES"] == 5
    assert audit["EXECUTABLE_FAILS"] == 0
    assert audit["NOT_A_TEST"] == 6
    assert audit["NOT_EXECUTABLE"] == 0


def test_w5_041_source_files_not_a_test():
    source_paths = {
        "periphery/brody/__init__.py",
        "periphery/brody/brody_response_contract.py",
        "periphery/brody/brody_runtime_readonly.py",
        "periphery/brody/brody_context_query.py",
        "periphery/brody/brody_language_router.py",
        "periphery/brody/brody_response_sanitizer.py",
    }
    entries = bges.get_entries()
    for e in entries:
        if e["path"] in source_paths:
            assert e["executability_status"] == "NOT_A_TEST", (
                f"{e['path']} should be NOT_A_TEST, got {e['executability_status']}"
            )


def test_w5_042_test_files_executable_passes():
    test_paths = {
        "tests/periphery/test_brody_response_contract.py",
        "tests/periphery/test_brody_runtime_readonly.py",
        "tests/non_sovereignty/test_brody_no_act.py",
        "tests/non_sovereignty/test_brody_no_decision.py",
        "tests/non_sovereignty/test_brody_response_never_emits_verdict.py",
    }
    entries = bges.get_entries()
    for e in entries:
        if e["path"] in test_paths:
            assert e["executability_status"] == "EXECUTABLE_PASSES", (
                f"{e['path']} should be EXECUTABLE_PASSES, got {e['executability_status']}"
            )


# ---------------------------------------------------------------------------
# W5-050 — Relation types
# ---------------------------------------------------------------------------

def test_w5_050_relation_distribution():
    idx = bges.get_index()
    dist = idx["gate_v5_relation_distribution"]
    assert dist["TEST_CONFIGURATION_LINKED_TO_GOVERNANCE_ELEMENT_SYSTEM_INDEX"] == 5
    assert dist["STATIC_PROOF_ARTIFACT_LINKED_TO_GOVERNANCE_ELEMENT_SYSTEM_INDEX"] == 1
    assert dist["EXECUTABLE_TEST_LINKED_TO_SOURCE_COMPONENT"] == 2
    assert dist["EXECUTABLE_NEGATIVE_TEST_LINKED_TO_SOURCE_COMPONENT"] == 3


def test_w5_051_all_verdicts_true_documentary():
    entries = bges.get_entries()
    non_true = [e["path"] for e in entries if e["semantic_verdict"] != "TRUE_DOCUMENTARY_RELATION"]
    assert non_true == []


# ---------------------------------------------------------------------------
# W5-060 — SHA256 integrity for all 11 entries
# ---------------------------------------------------------------------------

def test_w5_060_all_sha256_valid():
    entries = bges.get_entries()
    failures = []
    for e in entries:
        if not bges.validate_sha256(e):
            failures.append(e["path"])
    assert failures == [], f"SHA256 mismatch for: {failures}"


def test_w5_061_brody_init_sha256():
    entries = bges.get_entries()
    e = next(x for x in entries if x["path"] == "periphery/brody/__init__.py")
    assert e["sha256"] == "80db90aa6c6e0de30a66fd17bfa6231f6e464e0f2c9b1398ec5d7f7345b3ef58"
    assert bges.validate_sha256(e)


def test_w5_062_response_contract_sha256():
    entries = bges.get_entries()
    e = next(x for x in entries if x["path"] == "periphery/brody/brody_response_contract.py")
    assert e["sha256"] == "50cb79699549effe3a289c107c39b541c589b397ae1e87e9f19145347a789c2e"
    assert bges.validate_sha256(e)


# ---------------------------------------------------------------------------
# W5-070 — Governance claims block
# ---------------------------------------------------------------------------

def test_w5_070_governance_claims_present():
    claims = bges.get_governance_invariants()
    assert len(claims) >= 5


def test_w5_071_brody_never_decides_claim():
    claims = bges.get_governance_invariants()
    assert "brody_never_decides" in claims


def test_w5_072_brody_never_emits_act_claim():
    claims = bges.get_governance_invariants()
    assert "brody_never_emits_act" in claims


def test_w5_073_sovereign_tokens_redacted_claim():
    claims = bges.get_governance_invariants()
    assert "sovereign_tokens_redacted" in claims


# ---------------------------------------------------------------------------
# W5-080 — Validator summary()
# ---------------------------------------------------------------------------

def test_w5_080_summary_total():
    s = bges.summary()
    assert s["total"] == 11


def test_w5_081_summary_negative_tests():
    s = bges.summary()
    assert s["negative_tests"] == 3


def test_w5_082_summary_static_proof_artifacts():
    s = bges.summary()
    assert s["static_proof_artifacts"] == 1


def test_w5_083_summary_by_role_keys():
    s = bges.summary()
    assert "TEST_CONFIGURATION" in s["by_role"]
    assert "STATIC_PROOF_ARTIFACT" in s["by_role"]
    assert "EXECUTABLE_UNIT_TEST" in s["by_role"]
    assert "EXECUTABLE_NEGATIVE_TEST" in s["by_role"]


# ---------------------------------------------------------------------------
# W5-090 — World action bus not modified by Wave005 module calls
# ---------------------------------------------------------------------------

def test_w5_090_world_action_bus_unchanged_by_wave005_module():
    bus = _bus_path()
    if not bus.exists():
        pytest.skip("world_action_bus.jsonl not present — skipping bus integrity check")
    before = _sha256(bus)
    _ = bges.get_index()
    _ = bges.get_entries()
    _ = bges.summary()
    _ = bges.validate_all_paths_exist()
    after = _sha256(bus)
    assert before == after, "world_action_bus.jsonl was modified by Wave005 module calls"
