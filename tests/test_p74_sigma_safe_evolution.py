"""
tests/test_p74_sigma_safe_evolution.py

P74 validation suite.
Verifie : JSON audit, modele sigma, matrice sigma, POST_GUARD_VETO_ONLY,
gamma=1.0, pression agents_readonly, invariants P72, flags securite,
regressions P56E->P73.
"""
import json
import os
import re
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P74_JSON = os.path.join(ROOT, "docs", "core_import", "P74_SIGMA_SAFE_EVOLUTION.json")
SIGMA_DIR = os.path.join(ROOT, "sigma")
RUN_PIPELINE = os.path.join(SIGMA_DIR, "run_pipeline.py")
SIGMA_V130 = os.path.join(SIGMA_DIR, "obsidia_sigma_v130.py")
SIGMA_CONFIG = os.path.join(SIGMA_DIR, "sigma_config.json")
SIGMA_GUARD = os.path.join(SIGMA_DIR, "guard.py")


@pytest.fixture(scope="module")
def p74():
    with open(P74_JSON, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def sigma_matrix(p74):
    return p74["sigma_matrix"]


@pytest.fixture(scope="module")
def p72_invariants(p74):
    return p74["p72_invariants_checked"]


# ---------------------------------------------------------------------------
# Section 1 — JSON de base (6 tests)
# ---------------------------------------------------------------------------

def test_p74_json_exists():
    assert os.path.isfile(P74_JSON)


def test_p74_json_status(p74):
    assert p74["status"] == "P74_SIGMA_SAFE_EVOLUTION_READY"


def test_p74_json_mode(p74):
    assert p74["mode"] == "AUDIT_AND_PATCH_IF_SAFE"


def test_p74_sigma_decision(p74):
    assert p74["sigma_decision"] == "NO_SIGMA_CHANGE_REQUIRED"


def test_p74_source_patch_not_applied(p74):
    assert p74["source_patch_applied"] is False


def test_p74_files_imported_zero(p74):
    assert p74["files_imported_count"] == 0


# ---------------------------------------------------------------------------
# Section 2 — Modele sigma (8 tests)
# ---------------------------------------------------------------------------

def test_sigma_model_post_guard_veto_only(p74):
    assert "post_guard_veto_only" in p74["sigma_model"]


def test_sigma_model_guard_x108_final_authority(p74):
    assert "guard_x108_final_authority" in p74["sigma_model"]


def test_sigma_model_no_act_authority(p74):
    assert "no_act_authority" in p74["sigma_model"]


def test_sigma_model_no_hold_block_promotion(p74):
    assert "no_hold_block_to_act_promotion" in p74["sigma_model"]


def test_sigma_model_no_memory_write(p74):
    assert "no_memory_write" in p74["sigma_model"]


def test_sigma_model_no_graphiti_write(p74):
    assert "no_graphiti_write" in p74["sigma_model"]


def test_sigma_model_no_kernel_mutation(p74):
    assert "no_kernel_mutation" in p74["sigma_model"]


def test_sigma_model_gamma_1_0_preserved(p74):
    assert "gamma_1_0_preserved" in p74["sigma_model"]


# ---------------------------------------------------------------------------
# Section 3 — Matrice sigma — structure (5 tests)
# ---------------------------------------------------------------------------

def test_sigma_matrix_exists(p74):
    assert isinstance(p74["sigma_matrix"], list)
    assert len(p74["sigma_matrix"]) > 0


def test_sigma_matrix_count(p74):
    assert p74["sigma_files_scanned_count"] >= 20
    assert len(p74["sigma_matrix"]) >= 20


def test_sigma_matrix_required_fields(sigma_matrix):
    required = {
        "file_path", "sigma_role", "current_version",
        "p56b_patched", "p56d_patched", "proof_wins",
        "needs_change", "change_type", "risk_level",
        "decision", "reason", "p72_invariants_checked",
    }
    for entry in sigma_matrix:
        for f in required:
            assert f in entry, f"Champ manquant {f} dans {entry.get('file_path')}"


def test_sigma_matrix_all_no_change(sigma_matrix):
    for e in sigma_matrix:
        assert e["change_type"] == "NO_CHANGE", (
            f"Changement inattendu dans {e['file_path']}: {e['change_type']}"
        )


def test_sigma_matrix_all_proof_wins(sigma_matrix):
    for e in sigma_matrix:
        assert e["proof_wins"] is True, (
            f"proof_wins=False inattendu dans {e['file_path']}"
        )


# ---------------------------------------------------------------------------
# Section 4 — Fichiers critiques dans la matrice (6 tests)
# ---------------------------------------------------------------------------

def _get_sigma_entry(sigma_matrix, path_fragment):
    return next((e for e in sigma_matrix if path_fragment in e["file_path"]), None)


def test_guard_py_in_matrix(sigma_matrix):
    entry = _get_sigma_entry(sigma_matrix, "guard.py")
    assert entry is not None
    assert entry["p56d_patched"] is True
    assert entry["needs_change"] is False


def test_run_pipeline_in_matrix(sigma_matrix):
    entry = _get_sigma_entry(sigma_matrix, "run_pipeline.py")
    assert entry is not None
    assert entry["p56d_patched"] is True
    assert entry["needs_change"] is False


def test_obsidia_sigma_v130_in_matrix(sigma_matrix):
    entry = _get_sigma_entry(sigma_matrix, "obsidia_sigma_v130.py")
    assert entry is not None
    assert entry["p56b_patched"] is True
    assert entry["needs_change"] is False


def test_contracts_py_in_matrix(sigma_matrix):
    entry = _get_sigma_entry(sigma_matrix, "contracts.py")
    assert entry is not None
    assert "broken" not in entry["file_path"]
    assert entry["p56b_patched"] is True


def test_evaluate_py_in_matrix(sigma_matrix):
    entry = _get_sigma_entry(sigma_matrix, "evaluate.py")
    assert entry is not None
    assert entry["needs_change"] is False


def test_sigma_config_in_matrix(sigma_matrix):
    entry = _get_sigma_entry(sigma_matrix, "sigma_config.json")
    assert entry is not None
    assert entry["needs_change"] is False


# ---------------------------------------------------------------------------
# Section 5 — POST_GUARD_VETO_ONLY verifie (5 tests)
# ---------------------------------------------------------------------------

def test_post_guard_veto_only_check_verified(p74):
    check = p74["post_guard_veto_only_check"]
    assert check["verified"] is True


def test_post_guard_veto_only_findings_nonempty(p74):
    check = p74["post_guard_veto_only_check"]
    assert len(check["findings"]) >= 3


def test_run_pipeline_contains_post_guard_veto_only():
    assert os.path.isfile(RUN_PIPELINE)
    content = open(RUN_PIPELINE, encoding="utf-8").read()
    assert "POST_GUARD_VETO_ONLY" in content


def test_run_pipeline_contains_hold_stability_alert():
    content = open(RUN_PIPELINE, encoding="utf-8").read()
    assert "HOLD_STABILITY_ALERT" in content


def test_run_pipeline_sigma_authority_veto_only():
    content = open(RUN_PIPELINE, encoding="utf-8").read()
    assert "VETO_ONLY" in content
    assert "REPORT_ONLY" in content


# ---------------------------------------------------------------------------
# Section 6 — gamma=1.0 verifie — aucun gamma=0.5 (5 tests)
# ---------------------------------------------------------------------------

def test_no_gamma_05_check_verified(p74):
    check = p74["no_gamma_05_check"]
    assert check["verified"] is True


def test_no_gamma_05_no_violations(p74):
    check = p74["no_gamma_05_check"]
    assert check["violations"] == []


def test_sigma_v130_no_gamma_05():
    assert os.path.isfile(SIGMA_V130)
    content = open(SIGMA_V130, encoding="utf-8").read()
    assert not re.search(r"gamma\s*=\s*0\.5", content)


def test_sigma_config_no_gamma_05():
    assert os.path.isfile(SIGMA_CONFIG)
    cfg = json.loads(open(SIGMA_CONFIG, encoding="utf-8").read())
    assert cfg.get("tau_max") != 0.5
    assert cfg.get("accel_limit") != 0.5


def test_sigma_v130_default_tau_max_075():
    content = open(SIGMA_V130, encoding="utf-8").read()
    assert "_DEFAULT_TAU_MAX = 0.75" in content


# ---------------------------------------------------------------------------
# Section 7 — GuardX108 autorite finale (4 tests)
# ---------------------------------------------------------------------------

def test_guard_py_exists():
    assert os.path.isfile(SIGMA_GUARD)


def test_guard_py_no_sigma_import():
    content = open(SIGMA_GUARD, encoding="utf-8").read()
    assert "from sigma" not in content
    assert "import sigma" not in content
    assert "ObsidiaSigmaMonitor" not in content


def test_guard_py_decide_method():
    content = open(SIGMA_GUARD, encoding="utf-8").read()
    assert "def decide" in content
    assert "X108Gate.BLOCK" in content
    assert "X108Gate.HOLD" in content
    assert "X108Gate.ALLOW" in content


def test_guard_x108_final_authority_invariant_checked(p72_invariants):
    ids = [e["invariant_id"] for e in p72_invariants]
    assert "GUARD_X108_FINAL_AUTHORITY" in ids
    entry = next(e for e in p72_invariants if e["invariant_id"] == "GUARD_X108_FINAL_AUTHORITY")
    assert entry["p74_verification"] == "VERIFIED"
    assert entry["formal_status"] == "LEAN_PROVEN"


# ---------------------------------------------------------------------------
# Section 8 — Pression agents_readonly/ (4 tests)
# ---------------------------------------------------------------------------

def test_agent_pressure_check_no_pressure(p74):
    check = p74["p73_agent_pressure_checked"]
    assert check["sigma_pressure"] is False
    assert check["verified_no_pressure"] is True


def test_agent_pressure_no_sigma_imports(p74):
    check = p74["p73_agent_pressure_checked"]
    assert check["sigma_imports_from_agents_readonly"] == []


def test_sigma_dashboard_readonly_no_sigma_import():
    path = os.path.join(ROOT, "apps", "obsidia_api", "agents_readonly", "sigma_dashboard_readonly.py")
    assert os.path.isfile(path)
    content = open(path, encoding="utf-8").read()
    assert "from sigma" not in content
    assert "import sigma" not in content


def test_sigma_dashboard_readonly_sigma_override_false():
    path = os.path.join(ROOT, "apps", "obsidia_api", "agents_readonly", "sigma_dashboard_readonly.py")
    content = open(path, encoding="utf-8").read()
    assert "SIGMA_OVERRIDE: bool = False" in content


# ---------------------------------------------------------------------------
# Section 9 — SRL hors sigma (2 tests)
# ---------------------------------------------------------------------------

def test_srl_outside_sigma_check(p74):
    check = p74["srl_outside_sigma_check"]
    assert check["verified_srl_outside_sigma"] is True
    assert check["srl_in_sigma"] is False


def test_srl_not_in_sigma_dir():
    srl_in_sigma = os.path.join(SIGMA_DIR, "srl_session_registry_layer_readonly")
    assert not os.path.isdir(srl_in_sigma)


# ---------------------------------------------------------------------------
# Section 10 — P72 invariants (5 tests)
# ---------------------------------------------------------------------------

def test_p72_invariants_checked_nonempty(p72_invariants):
    assert len(p72_invariants) >= 6


def test_p72_sigma_post_guard_veto_only_verified(p72_invariants):
    entry = next((e for e in p72_invariants if e["invariant_id"] == "SIGMA_POST_GUARD_VETO_ONLY"), None)
    assert entry is not None
    assert entry["p74_verification"] == "VERIFIED"


def test_p72_no_kernel_mutation_verified(p72_invariants):
    entry = next((e for e in p72_invariants if e["invariant_id"] == "NO_KERNEL_MUTATION_FROM_PERIPHERY"), None)
    assert entry is not None
    assert entry["p74_verification"] == "VERIFIED"
    assert entry["formal_status"] == "LEAN_PROVEN"


def test_p72_determinism_verified(p72_invariants):
    entry = next((e for e in p72_invariants if e["invariant_id"] == "DETERMINISM"), None)
    assert entry is not None
    assert entry["p74_verification"] == "VERIFIED"


def test_p72_no_graphiti_write_verified(p72_invariants):
    entry = next((e for e in p72_invariants if e["invariant_id"] == "NO_GRAPHITI_WRITE"), None)
    assert entry is not None
    assert entry["p74_verification"] == "VERIFIED"


# ---------------------------------------------------------------------------
# Section 11 — Flags securite (14 tests)
# ---------------------------------------------------------------------------

def test_sigma_modified_false(p74):
    assert p74["sigma_modified"] is False


def test_runtime_modified_false(p74):
    assert p74["runtime_modified"] is False


def test_routes_modified_false(p74):
    assert p74["routes_modified"] is False


def test_lean_proofs_modified_false(p74):
    assert p74["lean_proofs_modified"] is False


def test_proofs_modified_false(p74):
    assert p74["proofs_modified"] is False


def test_srl_modified_false(p74):
    assert p74["srl_modified"] is False


def test_connectors_modified_false(p74):
    assert p74["connectors_modified"] is False


def test_source_packs_modified_false(p74):
    assert p74["source_packs_modified"] is False


def test_act_enabled_false(p74):
    assert p74["act_enabled"] is False


def test_memory_write_enabled_false(p74):
    assert p74["memory_write_enabled"] is False


def test_graphiti_write_enabled_false(p74):
    assert p74["graphiti_write_enabled"] is False


def test_neo4j_write_enabled_false(p74):
    assert p74["neo4j_write_enabled"] is False


def test_kernel_mutation_enabled_false(p74):
    assert p74["kernel_mutation_enabled"] is False


def test_x108_merge_enabled_false(p74):
    assert p74["x108_merge_enabled"] is False


# ---------------------------------------------------------------------------
# Section 12 — Regressions P56E->P73 (18 tests)
# ---------------------------------------------------------------------------

def _run(test_path: str) -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-q", "--tb=no", "--no-header", "-k", "not regression"],
        capture_output=True, text=True, cwd=ROOT,
    )
    return result.returncode == 0


def test_p56e_regression():
    assert _run("tests/test_p56e_post_patch_metric_reaudit.py")


def test_p57_regression():
    assert _run("tests/test_p57_core_machinery_runtime_binding_audit.py")


def test_p58_regression():
    assert _run("tests/test_p58_core_import_triage_operational_path_aware.py")


def test_p59_regression():
    assert _run("tests/test_p59_safe_batch_1_import.py")


def test_p60_regression():
    assert _run("tests/test_p60_test_batch_2_import.py")


def test_p61_regression():
    assert _run("tests/test_p61_bus_adapter_batch.py")


def test_p62_regression():
    assert _run("tests/test_p62_manual_review_deferred.py")


def test_p63_regression():
    assert _run("tests/test_p63_global_fusion_reality_audit.py")


def test_p64_regression():
    assert _run("tests/test_p64_fusion_continuity_ledger.py")


def test_p65_regression():
    assert _run("tests/test_p65_os_adapters_unlock_bus_registry.py")


def test_p66_regression():
    assert _run("tests/test_p66_srl_readonly_memory_layer.py")


def test_p67_regression():
    assert _run("tests/test_p67_boundary_semantic_split_audit.py")


def test_p68_regression():
    assert _run("tests/test_p68_api_auth_route_exposure_audit.py")


def test_p69_regression():
    assert _run("tests/test_p69_filesystem_path_exposure_audit.py")


def test_p70_regression():
    assert _run("tests/test_p70_network_egress_connectors_audit.py")


def test_p71_regression():
    assert _run("tests/test_p71_source_runtime_source_packs_deep_audit.py")


def test_p72_regression():
    assert _run("tests/test_p72_invariant_graph_formal_proof_alignment.py")


def test_p73_regression():
    assert _run("tests/test_p73_agents_complementary_reconciliation.py")


# ---------------------------------------------------------------------------
# Section 13 — verify_all et forbidden (2 tests)
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
