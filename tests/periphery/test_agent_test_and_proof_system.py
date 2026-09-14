"""
Wave004 — AGENT_TEST_AND_PROOF_SYSTEM documentary index tests.

Tests the Wave004 index integrity: metadata, population, role classification,
executability claims, relation types. Does NOT re-run the 8 underlying files
as a proxy for the index — the §8 real-execution matrix does that.

Population: 8 files.
  TEST_CONFIGURATION x2
  EXECUTABLE_UNIT_TEST x4 + EXECUTABLE_AUTHORITY_TEST x1
  LEGACY_TEST_OR_PROOF x1
"""
import hashlib
import pytest
from periphery.agents.agent_test_and_proof_system import (
    get_index,
    get_entries,
    validate_all_paths_exist,
    validate_sha256,
    get_entries_by_role,
    get_entries_by_executability,
    get_entries_by_relation_type,
    get_blocked_entries,
    summary,
)

# ---------------------------------------------------------------------------
# §1 — Index structure et autorité
# ---------------------------------------------------------------------------

def test_w4_001_index_loads():
    idx = get_index()
    assert idx["schema_version"] == "1.0"
    assert idx["index_id"] == "AGENT_TEST_AND_PROOF_SYSTEM_INDEX_V1"


def test_w4_002_authority_non_sovereign():
    idx = get_index()
    assert idx["authority"] == "NON_SOVEREIGN"
    assert idx["can_decide"] is False
    assert idx["can_act"] is False
    assert idx["emits_act"] is False
    assert idx["memory_write"] is False
    assert idx["model_calls"] == 0
    assert idx["runtime_consumed"] is False


def test_w4_003_subsystem_and_wave():
    idx = get_index()
    assert idx["subsystem"] == "AGENT_TEST_AND_PROOF_SYSTEM"
    assert idx["wave"] == "WAVE004"


def test_w4_004_catalog_role_documentary():
    idx = get_index()
    assert idx["catalog_role"] == "DOCUMENTARY_INDEX"


def test_w4_005_truth_audit_v2():
    idx = get_index()
    assert idx["truth_audit"] == "WAVE004_FINAL_TRUTH_GATE_V2"


def test_w4_006_physical_membership_rule_documented():
    idx = get_index()
    assert "physical_membership_rule" in idx
    assert len(idx["physical_membership_rule"]) > 50


# ---------------------------------------------------------------------------
# §2 — Population
# ---------------------------------------------------------------------------

def test_w4_010_population_total_8():
    idx = get_index()
    assert idx["population_audit"]["total"] == 8


def test_w4_011_entries_count_8():
    assert len(get_entries()) == 8


def test_w4_012_previously_unresolved_resolved():
    idx = get_index()
    assert idx["population_audit"]["previously_unresolved"] == 1
    assert idx["population_audit"]["resolved_in_wave004"] == 1
    assert "OPTION_A_APPLIED" in idx["population_audit"]["resolution"]


# ---------------------------------------------------------------------------
# §3 — Existence fichiers + SHA256
# ---------------------------------------------------------------------------

def test_w4_020_all_paths_exist():
    existence = validate_all_paths_exist()
    missing = [p for p, ok in existence.items() if not ok]
    assert missing == [], f"Paths missing from disk: {missing}"


def test_w4_021_sha256_agent_contracts():
    e = next(e for e in get_entries() if e["path"] == "periphery/agent_contracts.py")
    assert validate_sha256(e), f"SHA256 mismatch for {e['path']}"


def test_w4_022_sha256_agent_registry():
    e = next(e for e in get_entries() if e["path"] == "periphery/agent_registry.py")
    assert validate_sha256(e), f"SHA256 mismatch for {e['path']}"


def test_w4_023_sha256_agents52_test_post_repair():
    e = next(e for e in get_entries() if "test_agents_52_registry" in e["path"])
    assert validate_sha256(e), "SHA256 mismatch — test_agents_52_registry.py was repaired, index must be updated"


# ---------------------------------------------------------------------------
# §4 — Distribution des rôles (Gate V2 corrigée)
# ---------------------------------------------------------------------------

_VALID_ROLES = {
    "EXECUTABLE_UNIT_TEST",
    "EXECUTABLE_INTEGRATION_TEST",
    "EXECUTABLE_RUNTIME_TEST",
    "EXECUTABLE_NEGATIVE_TEST",
    "EXECUTABLE_AUTHORITY_TEST",
    "TEST_FIXTURE",
    "TEST_HELPER",
    "TEST_CONFIGURATION",
    "STATIC_PROOF_ARTIFACT",
    "RUNTIME_PROOF_RECEIPT",
    "EXECUTION_REPORT",
    "CLAIM_MATRIX",
    "PROOF_DOCUMENTATION",
    "TEST_DOCUMENTATION",
    "GENERATED_TEST_OR_PROOF_OUTPUT",
    "LEGACY_TEST_OR_PROOF",
    "UNKNOWN_PENDING_REVIEW",
}

_FORBIDDEN_ROLES = {"SOURCE_COMPONENT", "STATIC_PLACEHOLDER", "EXECUTABLE_PASSES", "EXECUTABLE_FAILS"}


def test_w4_030_no_forbidden_roles():
    for e in get_entries():
        assert e["role"] not in _FORBIDDEN_ROLES, (
            f"Forbidden role '{e['role']}' still present in {e['path']}"
        )


def test_w4_031_all_roles_valid():
    for e in get_entries():
        assert e["role"] in _VALID_ROLES, (
            f"Invalid role '{e['role']}' for {e['path']}"
        )


def test_w4_032_gate_v2_role_distribution():
    s = summary()
    r = s["by_role"]
    assert r.get("EXECUTABLE_UNIT_TEST", 0) == 4
    assert r.get("EXECUTABLE_AUTHORITY_TEST", 0) == 1
    assert r.get("TEST_CONFIGURATION", 0) == 2
    assert r.get("LEGACY_TEST_OR_PROOF", 0) == 1
    assert r.get("SOURCE_COMPONENT", 0) == 0
    assert r.get("STATIC_PLACEHOLDER", 0) == 0


def test_w4_033_gate_v2_distribution_matches_entries():
    idx = get_index()
    dist = idx["gate_v2_distribution"]
    from collections import Counter
    actual = Counter(e["role"] for e in get_entries())
    for role, count in dist.items():
        assert actual[role] == count, f"Role {role}: expected {count}, got {actual[role]}"


# ---------------------------------------------------------------------------
# §5 — Executability distribution (Gate V2)
# ---------------------------------------------------------------------------

def test_w4_040_executability_distribution():
    s = summary()
    ex = s["by_executability"]
    assert ex.get("EXECUTABLE_PASSES", 0) == 5
    assert ex.get("EXECUTABLE_FAILS", 0) == 0
    assert ex.get("NOT_A_TEST", 0) == 2
    assert ex.get("NOT_EXECUTABLE", 0) == 1


def test_w4_041_test_configuration_not_a_test():
    for e in get_entries_by_role("TEST_CONFIGURATION"):
        assert e["executability_status"] == "NOT_A_TEST", (
            f"TEST_CONFIGURATION {e['path']} wrong executability"
        )


def test_w4_042_legacy_test_not_executable():
    for e in get_entries_by_role("LEGACY_TEST_OR_PROOF"):
        assert e["executability_status"] == "NOT_EXECUTABLE", (
            f"LEGACY_TEST_OR_PROOF {e['path']} wrong executability"
        )


def test_w4_043_all_zero_executable_fails():
    for e in get_entries():
        assert e["executability_status"] != "EXECUTABLE_FAILS", (
            f"EXECUTABLE_FAILS still present: {e['path']}"
        )


# ---------------------------------------------------------------------------
# §6 — Types de relation
# ---------------------------------------------------------------------------

_VALID_RELATION_TYPES = {
    "EXECUTABLE_TEST_LINKED_TO_SOURCE_COMPONENT",
    "TEST_CONFIGURATION_LINKED_TO_TEST_SYSTEM_INDEX",
    "LEGACY_TEST_LINKED_TO_TEST_SYSTEM_INDEX",
}


def test_w4_044_all_relation_types_valid():
    for e in get_entries():
        assert e["relation_type"] in _VALID_RELATION_TYPES, (
            f"Invalid relation_type for {e['path']}: {e['relation_type']}"
        )


def test_w4_045_relation_distribution():
    idx = get_index()
    rd = idx["gate_v2_relation_distribution"]
    assert rd["EXECUTABLE_TEST_LINKED_TO_SOURCE_COMPONENT"] == 5
    assert rd["TEST_CONFIGURATION_LINKED_TO_TEST_SYSTEM_INDEX"] == 2
    assert rd["LEGACY_TEST_LINKED_TO_TEST_SYSTEM_INDEX"] == 1


# ---------------------------------------------------------------------------
# §7 — Verdicts sémantiques
# ---------------------------------------------------------------------------

def test_w4_046_all_semantic_verdicts_documentary():
    for e in get_entries():
        assert e["semantic_verdict"] == "TRUE_DOCUMENTARY_RELATION", (
            f"Wrong verdict for {e['path']}: {e['semantic_verdict']}"
        )


# ---------------------------------------------------------------------------
# §8 — Propriétés des EXECUTABLE_PASSES
# ---------------------------------------------------------------------------

def test_w4_050_test_agent_contracts_documented():
    e = next(e for e in get_entries() if e["path"] == "tests/periphery/test_agent_contracts.py")
    assert e["role"] == "EXECUTABLE_UNIT_TEST"
    assert e["executability_status"] == "EXECUTABLE_PASSES"
    assert e["last_result"] == "PASS"
    assert e["test_count"] == 2
    assert e["runner"] == "pytest"
    assert e["destination"] == "periphery/agent_contracts.py"
    assert "limitations" in e


def test_w4_051_test_agent_registry_documented():
    e = next(e for e in get_entries() if e["path"] == "tests/periphery/test_agent_registry.py")
    assert e["executability_status"] == "EXECUTABLE_PASSES"
    assert e["last_result"] == "PASS"
    assert e["test_count"] == 2
    assert "limitations" in e


def test_w4_052_test_agent_registry_v3v4_documented():
    e = next(e for e in get_entries() if e["path"] == "tests/periphery/test_agent_registry_v3_v4.py")
    assert e["executability_status"] == "EXECUTABLE_PASSES"
    assert e["last_result"] == "PASS"
    assert e["test_count"] == 6
    assert "target_agents" in e and len(e["target_agents"]) == 5


def test_w4_053_non_sovereignty_test_documented():
    e = next(e for e in get_entries() if "test_agents_cannot_emit_act" in e["path"])
    assert e["executability_status"] == "EXECUTABLE_PASSES"
    assert e["last_result"] == "PASS"
    assert e["test_count"] == 5
    assert e.get("governance_invariant") == "NON_SOVEREIGNTY_ACT_PROHIBITION"
    assert "side_effect_isolation" in e


def test_w4_054_non_sovereignty_test_in_correct_dir():
    e = next(e for e in get_entries() if "test_agents_cannot_emit_act" in e["path"])
    assert e["path"].startswith("tests/non_sovereignty/")


def test_w4_055_all_executable_passes_have_test_count():
    for e in get_entries():
        if e["executability_status"] == "EXECUTABLE_PASSES":
            assert "test_count" in e and e["test_count"] > 0, (
                f"EXECUTABLE_PASSES {e['path']} missing positive test_count"
            )


def test_w4_056_all_executable_passes_have_runner():
    for e in get_entries():
        if e["executability_status"] == "EXECUTABLE_PASSES":
            assert e.get("runner") == "pytest", (
                f"EXECUTABLE_PASSES {e['path']} missing runner=pytest"
            )


def test_w4_057_all_executable_tests_have_limitations():
    for e in get_entries():
        if e["role"] in ("EXECUTABLE_UNIT_TEST", "EXECUTABLE_AUTHORITY_TEST"):
            assert "limitations" in e, f"Missing limitations for {e['path']}"


# ---------------------------------------------------------------------------
# §9 — Test Agents52 réparé (Option A)
# ---------------------------------------------------------------------------

def test_w4_060_agents52_test_is_now_pass():
    e = next(e for e in get_entries() if "test_agents_52_registry" in e["path"])
    assert e["executability_status"] == "EXECUTABLE_PASSES"
    assert e["last_result"] == "PASS"
    assert e["status"] == "ACTIVE"


def test_w4_061_agents52_test_is_authority_role():
    e = next(e for e in get_entries() if "test_agents_52_registry" in e["path"])
    assert e["role"] == "EXECUTABLE_AUTHORITY_TEST"


def test_w4_062_agents52_repair_documented():
    e = next(e for e in get_entries() if "test_agents_52_registry" in e["path"])
    assert "wave004_repair" in e
    assert "OPTION_A_APPLIED" in e["wave004_repair"]


def test_w4_063_no_blocked_entries():
    blocked = get_blocked_entries()
    assert len(blocked) == 0, f"Unexpected blocked entries: {[e['path'] for e in blocked]}"


def test_w4_064_no_executable_fails():
    fails = get_entries_by_executability("EXECUTABLE_FAILS")
    assert len(fails) == 0, f"EXECUTABLE_FAILS entries: {[e['path'] for e in fails]}"


# ---------------------------------------------------------------------------
# §10 — TEST_CONFIGURATION reclassification (ex-SOURCE_COMPONENT)
# ---------------------------------------------------------------------------

def test_w4_065_agent_contracts_is_test_configuration():
    e = next(e for e in get_entries() if e["path"] == "periphery/agent_contracts.py")
    assert e["role"] == "TEST_CONFIGURATION"
    assert e["executability_status"] == "NOT_A_TEST"
    assert "real_role" in e and len(e["real_role"]) > 20


def test_w4_066_agent_registry_is_test_configuration():
    e = next(e for e in get_entries() if e["path"] == "periphery/agent_registry.py")
    assert e["role"] == "TEST_CONFIGURATION"
    assert e["executability_status"] == "NOT_A_TEST"


def test_w4_067_test_configuration_entries_have_related_test():
    for e in get_entries_by_role("TEST_CONFIGURATION"):
        assert "related_test" in e and len(e["related_test"]) > 0, (
            f"TEST_CONFIGURATION {e['path']} missing related_test"
        )


# ---------------------------------------------------------------------------
# §11 — LEGACY_TEST_OR_PROOF reclassification (ex-STATIC_PLACEHOLDER)
# ---------------------------------------------------------------------------

def test_w4_070_kernel_boundary_is_legacy():
    e = next(e for e in get_entries() if "kernel_boundary_tests" in e["path"])
    assert e["role"] == "LEGACY_TEST_OR_PROOF"
    assert e["executability_status"] == "NOT_EXECUTABLE"
    assert e["status"] == "LEGACY_STUB"


def test_w4_071_legacy_has_reason():
    e = next(e for e in get_entries() if "kernel_boundary_tests" in e["path"])
    assert "reason" in e and len(e["reason"]) > 20


def test_w4_072_legacy_has_intended_role():
    e = next(e for e in get_entries() if "kernel_boundary_tests" in e["path"])
    assert "intended_role" in e


# ---------------------------------------------------------------------------
# §12 — Side-effect isolation: world_action_bus unchanged after Wave004 tests
# ---------------------------------------------------------------------------

def test_w4_073_world_action_bus_unchanged_by_wave004_module():
    """Wave004 validator functions must not write to audit/world_action_bus.jsonl."""
    from pathlib import Path
    import sys
    for p in sys.path:
        candidate = Path(p) / ".git"
        if candidate.exists():
            root = Path(p)
            break
    else:
        root = Path(__file__).resolve().parents[2]

    bus_path = root / "audit" / "world_action_bus.jsonl"
    if not bus_path.exists():
        pytest.skip("world_action_bus.jsonl not present")

    def sha(p):
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    before = sha(bus_path)
    _ = get_index()
    _ = get_entries()
    _ = validate_all_paths_exist()
    _ = summary()
    after = sha(bus_path)
    assert before == after, "Wave004 validator functions wrote to audit/world_action_bus.jsonl"


def test_w4_074_side_effect_audit_in_index():
    idx = get_index()
    audit = idx.get("side_effect_audit", {})
    assert audit.get("world_action_bus_restored") is True
    assert "isolation_fixture_added" in audit


# ---------------------------------------------------------------------------
# §13 — Erreurs de collecte préexistantes documentées
# ---------------------------------------------------------------------------

def test_w4_075_preexisting_failures_documented():
    idx = get_index()
    failures = idx.get("preexisting_external_collection_failures", {})
    assert len(failures) == 4
    expected_files = {
        "tests/sigma_stress_test.py",
        "tests/test_agents_functional.py",
        "tests/test_consensus_inprocess.py",
        "tests/test_sigma_v18_9.py",
    }
    assert set(failures.keys()) == expected_files


# ---------------------------------------------------------------------------
# §14 — Exclusion invariants
# ---------------------------------------------------------------------------

def test_w4_076_no_wave001_files():
    excluded = {
        "periphery/agents_obsidia_config_registry.py",
        "tests/periphery/test_agents_obsidia_config_registry.py",
    }
    for e in get_entries():
        assert e["path"] not in excluded, f"Wave001 file in Wave004: {e['path']}"


def test_w4_077_no_wave002_operational_agents():
    for e in get_entries():
        path = e["path"]
        if path.startswith("periphery/agents/") and path.endswith(".py"):
            assert "agent_test_and_proof_system" in path, (
                f"Wave002 agent file in Wave004 index: {path}"
            )


def test_w4_078_no_wave003_mmonde_files():
    for e in get_entries():
        assert "MMONDE_REVERSE_OS" not in e["path"], (
            f"Wave003 MMONDE file in Wave004: {e['path']}"
        )


# ---------------------------------------------------------------------------
# §15 — Cohérence globale
# ---------------------------------------------------------------------------

def test_w4_079_all_entries_correct_owner_subsystem():
    for e in get_entries():
        assert e["owner_subsystem"] == "AGENT_TEST_AND_PROOF_SYSTEM"


def test_w4_080_all_entries_have_required_fields():
    required = {
        "path", "sha256", "role", "canonicality_status",
        "relation_type", "owner_subsystem", "status",
        "semantic_verdict", "executability_status",
    }
    for e in get_entries():
        missing = required - set(e.keys())
        assert not missing, f"Entry {e['path']} missing required fields: {missing}"
