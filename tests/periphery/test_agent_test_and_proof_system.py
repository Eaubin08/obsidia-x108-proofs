"""
Wave004 — AGENT_TEST_AND_PROOF_SYSTEM documentary index tests.

What is tested here: the Wave004 index itself (metadata, population, classification,
executability claims, role distribution). NOT a re-run of the underlying tests.

Population: 8 files (2 SOURCE_COMPONENT + 5 EXECUTABLE_UNIT_TEST + 1 STATIC_PLACEHOLDER).
"""
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
    get_placeholder_entries,
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


def test_w4_005_truth_audit():
    idx = get_index()
    assert idx["truth_audit"] == "WAVE004_FINAL_GATE_V1"


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
    assert idx["population_audit"]["previously_unresolved_path"] == (
        "periphery/modules_agents/test_agents_52_registry.py"
    )


# ---------------------------------------------------------------------------
# §3 — Existence fichiers + SHA256
# ---------------------------------------------------------------------------

def test_w4_020_all_paths_exist():
    existence = validate_all_paths_exist()
    missing = [p for p, ok in existence.items() if not ok]
    assert missing == [], f"Paths missing from disk: {missing}"


def test_w4_021_sha256_agent_contracts():
    entries = get_entries()
    e = next(e for e in entries if e["path"] == "periphery/agent_contracts.py")
    assert validate_sha256(e), f"SHA256 mismatch for {e['path']}"


def test_w4_022_sha256_agent_registry():
    entries = get_entries()
    e = next(e for e in entries if e["path"] == "periphery/agent_registry.py")
    assert validate_sha256(e), f"SHA256 mismatch for {e['path']}"


# ---------------------------------------------------------------------------
# §4 — Distribution des rôles
# ---------------------------------------------------------------------------

def test_w4_030_role_distribution():
    s = summary()
    assert s["by_role"]["EXECUTABLE_UNIT_TEST"] == 5
    assert s["by_role"]["SOURCE_COMPONENT"] == 2
    assert s["by_role"]["STATIC_PLACEHOLDER"] == 1


def test_w4_031_gate_v1_distribution_matches_entries():
    idx = get_index()
    dist = idx["gate_v1_distribution"]
    from collections import Counter
    actual = Counter(e["role"] for e in get_entries())
    assert actual["EXECUTABLE_UNIT_TEST"] == dist["EXECUTABLE_UNIT_TEST"] == 5
    assert actual["SOURCE_COMPONENT"] == dist["SOURCE_COMPONENT"] == 2
    assert actual["STATIC_PLACEHOLDER"] == dist["STATIC_PLACEHOLDER"] == 1


# ---------------------------------------------------------------------------
# §5 — Distribution executability
# ---------------------------------------------------------------------------

def test_w4_040_executability_distribution():
    s = summary()
    ex = s["by_executability"]
    assert ex["EXECUTABLE_PASSES"] == 4
    assert ex["EXECUTABLE_FAILS"] == 1
    assert ex["NOT_A_TEST"] == 2
    assert ex["NOT_EXECUTABLE_PLACEHOLDER"] == 1


def test_w4_041_source_components_not_a_test():
    for e in get_entries_by_role("SOURCE_COMPONENT"):
        assert e["executability_status"] == "NOT_A_TEST", (
            f"SOURCE_COMPONENT {e['path']} wrong executability: {e['executability_status']}"
        )


def test_w4_042_placeholder_not_executable():
    for e in get_entries_by_role("STATIC_PLACEHOLDER"):
        assert e["executability_status"] == "NOT_EXECUTABLE_PLACEHOLDER"


# ---------------------------------------------------------------------------
# §6 — Types de relation
# ---------------------------------------------------------------------------

_VALID_RELATION_TYPES = {
    "EXECUTABLE_TEST_LINKED_TO_SOURCE_COMPONENT",
    "SOURCE_COMPONENT_LINKED_TO_TEST_SYSTEM_INDEX",
    "STATIC_PLACEHOLDER_LINKED_TO_TEST_SYSTEM_INDEX",
}


def test_w4_043_all_relation_types_valid():
    for e in get_entries():
        assert e["relation_type"] in _VALID_RELATION_TYPES, (
            f"Invalid relation_type for {e['path']}: {e['relation_type']}"
        )


def test_w4_044_relation_distribution():
    s = summary()
    rt = s["by_relation_type"]
    assert rt["EXECUTABLE_TEST_LINKED_TO_SOURCE_COMPONENT"] == 5
    assert rt["SOURCE_COMPONENT_LINKED_TO_TEST_SYSTEM_INDEX"] == 2
    assert rt["STATIC_PLACEHOLDER_LINKED_TO_TEST_SYSTEM_INDEX"] == 1


# ---------------------------------------------------------------------------
# §7 — Verdicts sémantiques
# ---------------------------------------------------------------------------

def test_w4_045_all_semantic_verdicts_documentary():
    for e in get_entries():
        assert e["semantic_verdict"] == "TRUE_DOCUMENTARY_RELATION", (
            f"Wrong verdict for {e['path']}: {e['semantic_verdict']}"
        )


# ---------------------------------------------------------------------------
# §8 — Propriétés des entrées EXECUTABLE_PASSES
# ---------------------------------------------------------------------------

def test_w4_050_test_agent_contracts_documented():
    e = next(
        e for e in get_entries()
        if e["path"] == "tests/periphery/test_agent_contracts.py"
    )
    assert e["role"] == "EXECUTABLE_UNIT_TEST"
    assert e["executability_status"] == "EXECUTABLE_PASSES"
    assert e["test_count"] == 2
    assert e["runner"] == "pytest"
    assert e["destination"] == "periphery/agent_contracts.py"
    assert "limitations" in e and len(e["limitations"]) > 20


def test_w4_051_test_agent_registry_documented():
    e = next(
        e for e in get_entries()
        if e["path"] == "tests/periphery/test_agent_registry.py"
    )
    assert e["executability_status"] == "EXECUTABLE_PASSES"
    assert e["test_count"] == 2
    assert e["runner"] == "pytest"
    assert "limitations" in e


def test_w4_052_test_agent_registry_v3v4_documented():
    e = next(
        e for e in get_entries()
        if e["path"] == "tests/periphery/test_agent_registry_v3_v4.py"
    )
    assert e["executability_status"] == "EXECUTABLE_PASSES"
    assert e["test_count"] == 6
    assert "target_agents" in e and len(e["target_agents"]) == 5


def test_w4_053_non_sovereignty_test_documented():
    e = next(e for e in get_entries() if "test_agents_cannot_emit_act" in e["path"])
    assert e["executability_status"] == "EXECUTABLE_PASSES"
    assert e["test_count"] == 5
    assert e.get("governance_invariant") == "NON_SOVEREIGNTY_ACT_PROHIBITION"


def test_w4_054_non_sovereignty_test_in_correct_dir():
    e = next(e for e in get_entries() if "test_agents_cannot_emit_act" in e["path"])
    assert e["path"].startswith("tests/non_sovereignty/")


def test_w4_055_all_executable_passes_have_test_count():
    for e in get_entries_by_executability("EXECUTABLE_PASSES"):
        assert "test_count" in e and e["test_count"] > 0, (
            f"EXECUTABLE_PASSES {e['path']} missing positive test_count"
        )


def test_w4_056_all_executable_passes_have_runner():
    for e in get_entries_by_executability("EXECUTABLE_PASSES"):
        assert e.get("runner") == "pytest", (
            f"EXECUTABLE_PASSES {e['path']} missing runner=pytest"
        )


def test_w4_057_all_executable_tests_have_limitations():
    for e in get_entries_by_role("EXECUTABLE_UNIT_TEST"):
        has_limitations = "limitations" in e or "claim_text_intended" in e
        assert has_limitations, f"EXECUTABLE_UNIT_TEST {e['path']} missing limitations"


# ---------------------------------------------------------------------------
# §9 — Entrée EXECUTABLE_FAILS (chemin cassé)
# ---------------------------------------------------------------------------

def test_w4_060_broken_test_is_executable_fails():
    e = next(e for e in get_entries() if "test_agents_52_registry" in e["path"])
    assert e["executability_status"] == "EXECUTABLE_FAILS"
    assert e["status"] == "BLOCKED_BROKEN_PATH"


def test_w4_061_broken_test_has_failure_cause():
    e = next(e for e in get_entries() if "test_agents_52_registry" in e["path"])
    assert "failure_cause" in e
    assert "FileNotFoundError" in e["failure_cause"]
    assert "10_AGENTS_52" in e["failure_cause"]


def test_w4_062_broken_test_wave004_resolution():
    e = next(e for e in get_entries() if "test_agents_52_registry" in e["path"])
    assert "wave004_resolution" in e
    assert "PREVIOUSLY_UNRESOLVED" in e["wave004_resolution"]
    assert "EXECUTABLE_FAILS" in e["wave004_resolution"]


def test_w4_063_broken_test_not_claimed_as_pass():
    e = next(e for e in get_entries() if "test_agents_52_registry" in e["path"])
    assert e["executability_status"] != "EXECUTABLE_PASSES"


def test_w4_064_blocked_count_is_1():
    blocked = get_blocked_entries()
    assert len(blocked) == 1
    assert "test_agents_52_registry" in blocked[0]["path"]


# ---------------------------------------------------------------------------
# §10 — Entrée STATIC_PLACEHOLDER
# ---------------------------------------------------------------------------

def test_w4_065_placeholder_documented():
    e = next(e for e in get_entries() if "kernel_boundary_tests" in e["path"])
    assert e["role"] == "STATIC_PLACEHOLDER"
    assert e["executability_status"] == "NOT_EXECUTABLE_PLACEHOLDER"
    assert e["status"] == "STATIC_PLACEHOLDER"


def test_w4_066_placeholder_has_reason():
    e = next(e for e in get_entries() if "kernel_boundary_tests" in e["path"])
    assert "reason" in e and len(e["reason"]) > 20


def test_w4_067_placeholder_no_claim():
    e = next(e for e in get_entries() if "kernel_boundary_tests" in e["path"])
    claim = e.get("claim_text", "")
    assert "None" in claim or claim == ""


def test_w4_068_placeholder_count_is_1():
    assert len(get_placeholder_entries()) == 1


# ---------------------------------------------------------------------------
# §11 — Invariants d'exclusion (pas de fichiers Wave001/002/003)
# ---------------------------------------------------------------------------

def test_w4_070_no_wave001_files():
    excluded = {
        "periphery/agents_obsidia_config_registry.py",
        "tests/periphery/test_agents_obsidia_config_registry.py",
    }
    for e in get_entries():
        assert e["path"] not in excluded, f"Wave001 file in Wave004: {e['path']}"


def test_w4_071_no_wave002_operational_agents():
    for e in get_entries():
        path = e["path"]
        if path.startswith("periphery/agents/") and path.endswith(".py"):
            assert "agent_test_and_proof_system" in path, (
                f"Wave002 agent file in Wave004 index: {path}"
            )


def test_w4_072_no_wave003_mmonde_files():
    for e in get_entries():
        assert "MMONDE_REVERSE_OS" not in e["path"], (
            f"Wave003 MMONDE file in Wave004: {e['path']}"
        )


def test_w4_073_no_prior_wave_test_files():
    excluded = {
        "tests/periphery/test_agents_obsidia_config_registry.py",
        "tests/periphery/test_operational_source_catalog.py",
        "tests/periphery/test_agent_source_pack_documentation.py",
    }
    for e in get_entries():
        assert e["path"] not in excluded, f"Prior-wave test in Wave004: {e['path']}"


# ---------------------------------------------------------------------------
# §12 — Cohérence globale
# ---------------------------------------------------------------------------

def test_w4_074_all_entries_correct_owner_subsystem():
    for e in get_entries():
        assert e["owner_subsystem"] == "AGENT_TEST_AND_PROOF_SYSTEM", (
            f"Wrong owner_subsystem for {e['path']}: {e['owner_subsystem']}"
        )


def test_w4_075_all_entries_have_required_fields():
    required = {
        "path", "sha256", "role", "canonicality_status",
        "relation_type", "owner_subsystem", "status",
        "semantic_verdict", "executability_status",
    }
    for e in get_entries():
        missing = required - set(e.keys())
        assert not missing, f"Entry {e['path']} missing required fields: {missing}"
