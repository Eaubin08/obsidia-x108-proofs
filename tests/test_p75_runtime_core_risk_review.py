"""
tests/test_p75_runtime_core_risk_review.py

P75 validation suite.
Verifie : JSON audit, modele runtime, matrice, composants bloques,
candidats adapters, invariants P72, flags securite,
regressions P56E->P74.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P75_JSON = os.path.join(ROOT, "docs", "core_import", "P75_RUNTIME_CORE_RISK_REVIEW.json")
P75_MD = os.path.join(ROOT, "docs", "core_import", "P75_RUNTIME_CORE_RISK_REVIEW.md")
SIGMA_DIR = os.path.join(ROOT, "sigma")
RUNTIME_WIRING_DIR = os.path.join(ROOT, "runtime_wiring")


@pytest.fixture(scope="module")
def p75():
    with open(P75_JSON, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def runtime_matrix(p75):
    return p75["runtime_matrix"]


@pytest.fixture(scope="module")
def p72_constraints(p75):
    return p75["p72_invariant_constraints_applied"]


@pytest.fixture(scope="module")
def focus_findings(p75):
    return p75["focus_findings"]


# ---------------------------------------------------------------------------
# Section 1 — JSON de base (6 tests)
# ---------------------------------------------------------------------------

def test_p75_json_exists():
    assert os.path.isfile(P75_JSON)


def test_p75_json_status(p75):
    assert p75["status"] == "P75_RUNTIME_CORE_RISK_REVIEW_READY"


def test_p75_json_mode(p75):
    assert p75["mode"] == "AUDIT_ONLY"


def test_p75_runtime_decision(p75):
    assert p75["runtime_decision"] == "NO_RUNTIME_IMPORT"


def test_p75_source_patch_not_applied(p75):
    assert p75["source_patch_applied"] is False


def test_p75_files_imported_zero(p75):
    assert p75["files_imported_count"] == 0


# ---------------------------------------------------------------------------
# Section 2 — Modele runtime (5 tests)
# ---------------------------------------------------------------------------

def test_runtime_model_kernel_mutation_blocked(p75):
    assert "kernel_mutation_blocked" in p75["runtime_model"]


def test_runtime_model_action_risk_blocked(p75):
    assert "action_risk_blocked" in p75["runtime_model"]


def test_runtime_model_write_risk_blocked(p75):
    assert "write_risk_blocked" in p75["runtime_model"]


def test_runtime_model_adapter_candidate_readonly(p75):
    assert "adapter_candidate_readonly" in p75["runtime_model"]


def test_runtime_model_adapter_candidate_dry_run(p75):
    assert "adapter_candidate_dry_run" in p75["runtime_model"]


# ---------------------------------------------------------------------------
# Section 3 — Matrice runtime — structure (5 tests)
# ---------------------------------------------------------------------------

def test_runtime_matrix_exists(p75):
    assert isinstance(p75["runtime_matrix"], list)
    assert len(p75["runtime_matrix"]) > 0


def test_runtime_matrix_count(p75):
    assert p75["runtime_files_scanned_count"] >= 30
    assert len(p75["runtime_matrix"]) >= 30


def test_runtime_matrix_required_fields(runtime_matrix):
    required = {
        "file_path", "component_name", "category",
        "decision", "risk_level", "risk_patterns_found",
        "description", "reason_blocked", "proof_wins",
        "runtime_wiring_covers", "sigma_covers", "p72_invariants",
    }
    for entry in runtime_matrix:
        for f in required:
            assert f in entry, f"Champ manquant {f} dans {entry.get('file_path')}"


def test_runtime_matrix_all_decisions_valid(runtime_matrix):
    valid = {
        "BLOCK_RUNTIME_IMPORT", "BLOCK_UNTIL_FORMAL_REVIEW",
        "KEEP_PROOF_VERSION", "ADAPT_READONLY_LATER", "ADAPT_DRY_RUN_LATER",
        "IMPORT_TEST_ONLY_LATER", "IMPORT_DOC_ONLY_LATER", "DO_NOT_IMPORT_DUPLICATE",
    }
    for e in runtime_matrix:
        assert e["decision"] in valid, (
            f"Decision invalide dans {e['file_path']}: {e['decision']}"
        )


def test_runtime_matrix_block_count(p75):
    counts = p75["decision_counts"]
    blocked = counts.get("BLOCK_RUNTIME_IMPORT", 0) + counts.get("BLOCK_UNTIL_FORMAL_REVIEW", 0)
    assert blocked >= 13


# ---------------------------------------------------------------------------
# Section 4 — Composants bloques (8 tests)
# ---------------------------------------------------------------------------

def _get_entry(matrix, path_fragment):
    return next((e for e in matrix if path_fragment in e["file_path"]), None)


def test_engine_final_blocked(runtime_matrix):
    entry = _get_entry(runtime_matrix, "engine_final.py")
    assert entry is not None
    assert entry["decision"] == "BLOCK_RUNTIME_IMPORT"
    assert entry["category"] == "RUNTIME_KERNEL_MUTATION_BLOCKED"
    assert entry["risk_level"] == "CRITICAL"


def test_kernel_py_blocked(runtime_matrix):
    entry = _get_entry(runtime_matrix, "obsidia_kernel/kernel.py")
    assert entry is not None
    assert entry["decision"] == "BLOCK_RUNTIME_IMPORT"
    assert entry["category"] == "RUNTIME_KERNEL_MUTATION_BLOCKED"


def test_entrypoint_blocked(runtime_matrix):
    entry = _get_entry(runtime_matrix, "entrypoint.py")
    assert entry is not None
    assert entry["decision"] == "BLOCK_RUNTIME_IMPORT"
    assert entry["category"] == "RUNTIME_KERNEL_MUTATION_BLOCKED"


def test_orchestrator_blocked(runtime_matrix):
    entry = _get_entry(runtime_matrix, "orchestrator.py")
    assert entry is not None
    assert entry["decision"] == "BLOCK_RUNTIME_IMPORT"
    assert entry["category"] == "RUNTIME_ACTION_RISK_BLOCKED"


def test_os1_blocked(runtime_matrix):
    entry = _get_entry(runtime_matrix, "os1/os1.py")
    assert entry is not None
    assert entry["decision"] == "BLOCK_RUNTIME_IMPORT"
    assert entry["category"] == "RUNTIME_ACTION_RISK_BLOCKED"


def test_worm_uploader_blocked(runtime_matrix):
    entry = _get_entry(runtime_matrix, "worm_uploader.py")
    assert entry is not None
    assert entry["decision"] == "BLOCK_RUNTIME_IMPORT"
    assert entry["category"] == "RUNTIME_NETWORK_RISK_BLOCKED"


def test_audit_log_blocked(runtime_matrix):
    entry = _get_entry(runtime_matrix, "audit_log.py")
    assert entry is not None
    assert entry["decision"] == "BLOCK_RUNTIME_IMPORT"
    assert entry["category"] == "RUNTIME_WRITE_RISK_BLOCKED"


def test_adapter_formal_review(runtime_matrix):
    entry = _get_entry(runtime_matrix, "os_trad/adapter.py")
    assert entry is not None
    assert entry["decision"] == "BLOCK_UNTIL_FORMAL_REVIEW"
    assert entry["category"] == "RUNTIME_REQUIRES_FORMAL_REVIEW"


# ---------------------------------------------------------------------------
# Section 5 — Composants deja couverts (3 tests)
# ---------------------------------------------------------------------------

def test_x108_keep_proof_version(runtime_matrix):
    entry = _get_entry(runtime_matrix, "os1/x108.py")
    assert entry is not None
    assert entry["decision"] == "KEEP_PROOF_VERSION"
    assert entry["proof_wins"] is True
    assert entry["sigma_covers"] is True


def test_already_covered_list_nonempty(p75):
    covered = p75["already_covered_by_proof"]
    assert len(covered) >= 2


def test_x108_wiring_exists():
    stub = os.path.join(RUNTIME_WIRING_DIR, "x108_admission_stub.py")
    assert os.path.isfile(stub)


# ---------------------------------------------------------------------------
# Section 6 — Candidats adapters readonly/dry-run (6 tests)
# ---------------------------------------------------------------------------

def test_os0_contract_adapt_readonly(runtime_matrix):
    entry = _get_entry(runtime_matrix, "os0/contract.py")
    assert entry is not None
    assert entry["decision"] == "ADAPT_READONLY_LATER"


def test_os0_determinism_adapt_readonly(runtime_matrix):
    entry = _get_entry(runtime_matrix, "os0/determinism.py")
    assert entry is not None
    assert entry["decision"] == "ADAPT_READONLY_LATER"


def test_os3_metrics_adapt_readonly(runtime_matrix):
    entry = _get_entry(runtime_matrix, "os3/metrics.py")
    assert entry is not None
    assert entry["decision"] == "ADAPT_READONLY_LATER"
    assert "gamma=1.0" in entry["description"] or "gamma=1.0" in entry["reason_blocked"]


def test_os0_sandbox_adapt_dry_run(runtime_matrix):
    entry = _get_entry(runtime_matrix, "os0/sandbox.py")
    assert entry is not None
    assert entry["decision"] == "ADAPT_DRY_RUN_LATER"


def test_parse_input_adapt_dry_run(runtime_matrix):
    entry = _get_entry(runtime_matrix, "os1/parse_input.py")
    assert entry is not None
    assert entry["decision"] == "ADAPT_DRY_RUN_LATER"


def test_adapter_readonly_list_nonempty(p75):
    candidates = p75["adapter_candidate_readonly"]
    assert len(candidates) >= 5


# ---------------------------------------------------------------------------
# Section 7 — Invariants P72 (5 tests)
# ---------------------------------------------------------------------------

def test_p72_constraints_nonempty(p72_constraints):
    assert len(p72_constraints) >= 10


def test_p72_guard_x108_constraint_present(p72_constraints):
    assert any("GUARD_X108_FINAL_AUTHORITY" in c for c in p72_constraints)


def test_p72_no_act_before_tau_constraint_present(p72_constraints):
    assert any("NO_ACT_BEFORE_TAU" in c for c in p72_constraints)


def test_p72_no_kernel_mutation_constraint_present(p72_constraints):
    assert any("NO_KERNEL_MUTATION_FROM_PERIPHERY" in c for c in p72_constraints)


def test_p72_no_memory_write_constraint_present(p72_constraints):
    assert any("NO_MEMORY_WRITE_WITHOUT_GATE" in c for c in p72_constraints)


# ---------------------------------------------------------------------------
# Section 8 — Focus findings (5 tests)
# ---------------------------------------------------------------------------

def test_focus_findings_count(focus_findings):
    assert len(focus_findings) >= 7


def test_finding_f1_triangle_kernel(focus_findings):
    f1 = next((f for f in focus_findings if f["finding_id"] == "P75-F1"), None)
    assert f1 is not None
    assert f1["type"] == "CRITICAL_BLOCKED"
    assert f1["action"] == "BLOCK_RUNTIME_IMPORT"


def test_finding_f2_orchestrator_side_effect(focus_findings):
    f2 = next((f for f in focus_findings if f["finding_id"] == "P75-F2"), None)
    assert f2 is not None
    assert f2["type"] == "CRITICAL_BLOCKED"
    assert "ObsidiaKernel()" in f2["description"] or "side-effect" in f2["description"]


def test_finding_f4_os0_safe_for_later(focus_findings):
    f4 = next((f for f in focus_findings if f["finding_id"] == "P75-F4"), None)
    assert f4 is not None
    assert f4["type"] == "VERIFIED_SAFE_FOR_LATER"


def test_finding_f6_formal_review(focus_findings):
    f6 = next((f for f in focus_findings if f["finding_id"] == "P75-F6"), None)
    assert f6 is not None
    assert f6["action"] == "BLOCK_UNTIL_FORMAL_REVIEW"


# ---------------------------------------------------------------------------
# Section 9 — Flags securite (14 tests)
# ---------------------------------------------------------------------------

def test_runtime_modified_false(p75):
    assert p75["runtime_modified"] is False


def test_sigma_modified_false(p75):
    assert p75["sigma_modified"] is False


def test_routes_modified_false(p75):
    assert p75["routes_modified"] is False


def test_lean_proofs_modified_false(p75):
    assert p75["lean_proofs_modified"] is False


def test_proofs_modified_false(p75):
    assert p75["proofs_modified"] is False


def test_srl_modified_false(p75):
    assert p75["srl_modified"] is False


def test_connectors_modified_false(p75):
    assert p75["connectors_modified"] is False


def test_source_packs_modified_false(p75):
    assert p75["source_packs_modified"] is False


def test_act_enabled_false(p75):
    assert p75["act_enabled"] is False


def test_memory_write_enabled_false(p75):
    assert p75["memory_write_enabled"] is False


def test_graphiti_write_enabled_false(p75):
    assert p75["graphiti_write_enabled"] is False


def test_neo4j_write_enabled_false(p75):
    assert p75["neo4j_write_enabled"] is False


def test_kernel_mutation_enabled_false(p75):
    assert p75["kernel_mutation_enabled"] is False


def test_x108_merge_enabled_false(p75):
    assert p75["x108_merge_enabled"] is False


# ---------------------------------------------------------------------------
# Section 10 — Regressions P56E->P74 (19 tests)
# ---------------------------------------------------------------------------

def _run(test_path: str) -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-q", "--tb=no", "--no-header"],
        capture_output=True, text=True, cwd=ROOT,
    )
    return result.returncode == 0


@pytest.mark.regression
def test_p56e_regression():
    assert _run("tests/test_p56e_post_patch_metric_reaudit.py")


@pytest.mark.regression
def test_p57_regression():
    assert _run("tests/test_p57_core_machinery_runtime_binding_audit.py")


@pytest.mark.regression
def test_p58_regression():
    assert _run("tests/test_p58_core_import_triage_operational_path_aware.py")


@pytest.mark.regression
def test_p59_regression():
    assert _run("tests/test_p59_safe_batch_1_import.py")


@pytest.mark.regression
def test_p60_regression():
    assert _run("tests/test_p60_test_batch_2_import.py")


@pytest.mark.regression
def test_p61_regression():
    assert _run("tests/test_p61_bus_adapter_batch.py")


@pytest.mark.regression
def test_p62_regression():
    assert _run("tests/test_p62_manual_review_deferred.py")


@pytest.mark.regression
def test_p63_regression():
    assert _run("tests/test_p63_global_fusion_reality_audit.py")


@pytest.mark.regression
def test_p64_regression():
    assert _run("tests/test_p64_fusion_continuity_ledger.py")


@pytest.mark.regression
def test_p65_regression():
    assert _run("tests/test_p65_os_adapters_unlock_bus_registry.py")


@pytest.mark.regression
def test_p66_regression():
    assert _run("tests/test_p66_srl_readonly_memory_layer.py")


@pytest.mark.regression
def test_p67_regression():
    assert _run("tests/test_p67_boundary_semantic_split_audit.py")


@pytest.mark.regression
def test_p68_regression():
    assert _run("tests/test_p68_api_auth_route_exposure_audit.py")


@pytest.mark.regression
def test_p69_regression():
    assert _run("tests/test_p69_filesystem_path_exposure_audit.py")


@pytest.mark.regression
def test_p70_regression():
    assert _run("tests/test_p70_network_egress_connectors_audit.py")


@pytest.mark.regression
def test_p71_regression():
    assert _run("tests/test_p71_source_runtime_source_packs_deep_audit.py")


@pytest.mark.regression
def test_p72_regression():
    assert _run("tests/test_p72_invariant_graph_formal_proof_alignment.py")


@pytest.mark.regression
def test_p73_regression():
    assert _run("tests/test_p73_agents_complementary_reconciliation.py")


@pytest.mark.regression
def test_p74_regression():
    assert _run("tests/test_p74_sigma_safe_evolution.py")


# ---------------------------------------------------------------------------
# Section 11 — verify_all et forbidden (2 tests)
# ---------------------------------------------------------------------------

def test_verify_all_pass():
    result = subprocess.run(
        [sys.executable, "proofs/verify_all.py"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert "PASS" in result.stdout


def test_forbidden_content_pass():
    result = subprocess.run(
        [sys.executable, "scripts/check_forbidden_content.py"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert "FORBIDDEN_CONTENT_PASS" in result.stdout
