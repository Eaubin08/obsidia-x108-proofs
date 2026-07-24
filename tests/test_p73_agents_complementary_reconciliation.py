"""
tests/test_p73_agents_complementary_reconciliation.py

P73 validation suite — 77 tests.
Verifie : JSON audit, modele agents, matrice agents, fichiers adaptes,
boundary constants, flags securite, regressions P56E->P72.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P73_JSON = os.path.join(ROOT, "docs", "core_import", "P73_AGENTS_COMPLEMENTARY_RECONCILIATION.json")
AGENTS_READONLY_DIR = os.path.join(ROOT, "apps", "obsidia_api", "agents_readonly")
SIGMA_DASH = os.path.join(AGENTS_READONLY_DIR, "sigma_dashboard_readonly.py")
INDICATORS = os.path.join(AGENTS_READONLY_DIR, "indicators_readonly.py")


@pytest.fixture(scope="module")
def p73():
    with open(P73_JSON, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def agents_matrix(p73):
    return p73["agents_matrix"]


@pytest.fixture(scope="module")
def adapted_files(p73):
    return p73["adapted_files"]


# ---------------------------------------------------------------------------
# Section 1 — JSON de base (5 tests)
# ---------------------------------------------------------------------------

def test_p73_json_exists():
    assert os.path.isfile(P73_JSON)


def test_p73_json_status(p73):
    assert p73["status"] == "P73_AGENTS_COMPLEMENTARY_RECONCILIATION_READY"


def test_p73_json_mode(p73):
    assert p73["mode"] == "AUDIT_AND_READONLY_ADAPTERS"


def test_p73_source_patch_applied(p73):
    assert p73["source_patch_applied"] is True


def test_p73_files_imported_zero(p73):
    assert p73["files_imported_count"] == 0


# ---------------------------------------------------------------------------
# Section 2 — Modele agents (7 tests)
# ---------------------------------------------------------------------------

def test_agents_model_keep_proof_version(p73):
    assert "keep_proof_version" in p73["agents_model"]


def test_agents_model_do_not_import_duplicate(p73):
    assert "do_not_import_duplicate" in p73["agents_model"]


def test_agents_model_adapt_readonly_signal(p73):
    assert "adapt_readonly_signal" in p73["agents_model"]


def test_agents_model_adapt_dry_run_proposal(p73):
    assert "adapt_dry_run_proposal" in p73["agents_model"]


def test_agents_model_import_doc_only(p73):
    assert "import_doc_only" in p73["agents_model"]


def test_agents_model_blocked(p73):
    assert "blocked_architectural_review" in p73["agents_model"]


def test_agents_model_unknown(p73):
    assert "unknown_requires_review" in p73["agents_model"]


# ---------------------------------------------------------------------------
# Section 3 — Matrice agents — structure (5 tests)
# ---------------------------------------------------------------------------

def test_agents_matrix_exists(p73):
    assert isinstance(p73["agents_matrix"], list)
    assert len(p73["agents_matrix"]) > 0


def test_agents_matrix_count(p73):
    assert p73["agents_scanned_count"] == 33
    assert len(p73["agents_matrix"]) == 33


def test_agents_matrix_required_fields(agents_matrix):
    required = {
        "agent_name", "source_path", "source_surface",
        "proof_equivalent_exists", "proof_wins",
        "detected_capabilities", "detected_risks",
        "p72_invariant_constraints", "authority_status",
        "category", "risk_level", "decision", "reason", "next_action",
    }
    for entry in agents_matrix:
        for f in required:
            assert f in entry, f"Champ manquant {f} dans {entry.get('agent_name')}"


def test_agents_matrix_each_has_decision(agents_matrix):
    for e in agents_matrix:
        assert e.get("decision"), f"decision manquante dans {e.get('agent_name')}"


def test_agents_matrix_each_has_risk_level(agents_matrix):
    for e in agents_matrix:
        assert e.get("risk_level"), f"risk_level manquant dans {e.get('agent_name')}"


# ---------------------------------------------------------------------------
# Section 4 — Counts categories (6 tests)
# ---------------------------------------------------------------------------

def test_category_counts_nonempty(p73):
    assert len(p73["category_counts"]) > 0


def test_keep_proof_version_count(p73):
    assert p73["category_counts"]["KEEP_PROOF_VERSION"] == 18


def test_do_not_import_duplicate_count(p73):
    assert p73["category_counts"]["DO_NOT_IMPORT_DUPLICATE"] == 6


def test_adapt_readonly_signal_count(p73):
    assert p73["category_counts"]["ADAPT_READONLY_SIGNAL"] == 1


def test_import_doc_only_count(p73):
    assert p73["category_counts"]["IMPORT_DOC_ONLY"] == 1


def test_blocked_count(p73):
    assert p73["category_counts"]["BLOCKED_REQUIRES_ARCHITECTURAL_REVIEW"] == 7


# ---------------------------------------------------------------------------
# Section 5 — Proof wins et sigma protege (4 tests)
# ---------------------------------------------------------------------------

def test_proof_wins_exists(p73):
    assert isinstance(p73["proof_wins"], list)
    assert len(p73["proof_wins"]) >= 18


def test_sigma_protected_exists(p73):
    assert isinstance(p73["sigma_protected"], list)
    assert len(p73["sigma_protected"]) >= 6


def test_core_candidates_exists(p73):
    assert isinstance(p73["core_candidates"], list)
    assert len(p73["core_candidates"]) >= 2


def test_sigma_protected_guard_present(p73):
    files = [e["file"] for e in p73["sigma_protected"]]
    assert any("guard" in f for f in files)


# ---------------------------------------------------------------------------
# Section 6 — Fichiers adaptes — structure (11 tests)
# ---------------------------------------------------------------------------

def test_adapted_files_exists(p73):
    assert isinstance(p73["adapted_files"], list)
    assert len(p73["adapted_files"]) >= 2


def _get_adapted(adapted_files, name):
    return next((e for e in adapted_files if name in e.get("target_path", "")), None)


def test_adapted_target_under_agents_readonly(adapted_files):
    for e in adapted_files:
        tp = e.get("target_path", "")
        assert "apps/obsidia_api/agents_readonly/" in tp, (
            f"Target {tp} n'est pas sous agents_readonly/"
        )


def test_adapted_readonly_true(adapted_files):
    for e in adapted_files:
        assert e["readonly"] is True


def test_adapted_dry_run_only_true(adapted_files):
    for e in adapted_files:
        assert e["dry_run_only"] is True


def test_adapted_decision_authority_kx108(adapted_files):
    for e in adapted_files:
        assert e["decision_authority"] == "KX108_ONLY"


def test_adapted_emits_act_false(adapted_files):
    for e in adapted_files:
        assert e["emits_act"] is False


def test_adapted_emits_verdict_false(adapted_files):
    for e in adapted_files:
        assert e["emits_verdict"] is False


def test_adapted_memory_write_false(adapted_files):
    for e in adapted_files:
        assert e["memory_write"] is False


def test_adapted_graphiti_write_false(adapted_files):
    for e in adapted_files:
        assert e["graphiti_write"] is False


def test_adapted_neo4j_write_false(adapted_files):
    for e in adapted_files:
        assert e["neo4j_write"] is False


def test_adapted_kernel_mutation_false(adapted_files):
    for e in adapted_files:
        assert e["kernel_mutation"] is False


def test_adapted_sigma_override_false(adapted_files):
    for e in adapted_files:
        assert e["sigma_override"] is False


# ---------------------------------------------------------------------------
# Section 7 — Restrictions de chemin (4 tests)
# ---------------------------------------------------------------------------

def test_no_adapted_under_sigma(adapted_files):
    for e in adapted_files:
        tp = e.get("target_path", "")
        assert not tp.startswith("sigma/"), f"Fichier adapte interdit sous sigma/: {tp}"


def test_no_adapted_under_runtime_wiring(adapted_files):
    for e in adapted_files:
        tp = e.get("target_path", "")
        assert not tp.startswith("runtime_wiring/"), f"Interdit sous runtime_wiring/: {tp}"


def test_no_adapted_under_proofs_v18_3_1(adapted_files):
    for e in adapted_files:
        tp = e.get("target_path", "")
        assert "proofs/V18_3_1" not in tp, f"Interdit sous proofs/V18_3_1/: {tp}"


def test_no_adapted_under_routes(adapted_files):
    for e in adapted_files:
        tp = e.get("target_path", "")
        assert "apps/obsidia_api/routes/" not in tp, f"Interdit sous routes/: {tp}"


# ---------------------------------------------------------------------------
# Section 8 — Fichiers adaptes crees sur disque (5 tests)
# ---------------------------------------------------------------------------

def test_agents_readonly_dir_exists():
    assert os.path.isdir(AGENTS_READONLY_DIR)


def test_agents_readonly_init_exists():
    assert os.path.isfile(os.path.join(AGENTS_READONLY_DIR, "__init__.py"))


def test_sigma_dashboard_readonly_exists():
    assert os.path.isfile(SIGMA_DASH)


def test_indicators_readonly_exists():
    assert os.path.isfile(INDICATORS)


def test_sigma_dashboard_readonly_no_file_write():
    content = open(SIGMA_DASH, encoding="utf-8").read()
    assert "plt.savefig" not in content
    assert "plt.close" not in content
    assert "plt.show" not in content
    assert "MEMORY_WRITE: bool = False" in content
    assert "KERNEL_MUTATION: bool = False" in content


# ---------------------------------------------------------------------------
# Section 9 — Boundary constants dans les adapters (6 tests)
# ---------------------------------------------------------------------------

def test_sigma_dashboard_boundary_constants():
    content = open(SIGMA_DASH, encoding="utf-8").read()
    assert "DRY_RUN_ONLY: bool = True" in content
    assert "READONLY: bool = True" in content
    assert "DECISION_AUTHORITY: str = \"KX108_ONLY\"" in content
    assert "EMITS_ACT: bool = False" in content
    assert "SIGMA_OVERRIDE: bool = False" in content


def test_indicators_boundary_constants():
    content = open(INDICATORS, encoding="utf-8").read()
    assert "DRY_RUN_ONLY: bool = True" in content
    assert "READONLY: bool = True" in content
    assert "DECISION_AUTHORITY: str = \"KX108_ONLY\"" in content
    assert "EMITS_ACT: bool = False" in content


def test_sigma_dashboard_returns_dict():
    sys.path.insert(0, ROOT)
    try:
        from apps.obsidia_api.agents_readonly import sigma_dashboard_readonly as sdr
        result = sdr.get_sigma_stability_data("proofs/PROOFKIT_REPORT.json")
        assert isinstance(result, dict)
        assert "boundary" in result
        assert result["boundary"]["dry_run_only"] is True
        assert result["boundary"]["emits_act"] is False
    finally:
        pass


def test_sigma_dashboard_no_act():
    sys.path.insert(0, ROOT)
    from apps.obsidia_api.agents_readonly import sigma_dashboard_readonly as sdr
    assert sdr.EMITS_ACT is False
    assert sdr.SIGMA_OVERRIDE is False
    assert sdr.KERNEL_MUTATION is False


def test_indicators_readonly_sma():
    sys.path.insert(0, ROOT)
    from apps.obsidia_api.agents_readonly import indicators_readonly as ir
    result = ir.sma([1.0, 2.0, 3.0, 4.0, 5.0], period=3)
    assert result is not None
    assert abs(result - 4.0) < 1e-9


def test_indicators_readonly_ema():
    sys.path.insert(0, ROOT)
    from apps.obsidia_api.agents_readonly import indicators_readonly as ir
    result = ir.ema([1.0, 2.0, 3.0], period=3)
    assert result is not None


# ---------------------------------------------------------------------------
# Section 10 — P72 invariants appliques (4 tests)
# ---------------------------------------------------------------------------

def test_p72_invariant_constraints_applied_nonempty(p73):
    assert len(p73["p72_invariant_constraints_applied"]) >= 6


def test_p72_no_periphery_decision_applied(p73):
    constraints = p73["p72_invariant_constraints_applied"]
    assert any("NO_PERIPHERY_DECISION_AUTHORITY" in c for c in constraints)


def test_p72_dry_run_only_adapters_applied(p73):
    constraints = p73["p72_invariant_constraints_applied"]
    assert any("DRY_RUN_ONLY_ADAPTERS" in c for c in constraints)


def test_p72_kx108_only_applied(p73):
    constraints = p73["p72_invariant_constraints_applied"]
    assert any("KX108_ONLY" in c for c in constraints)


# ---------------------------------------------------------------------------
# Section 11 — Flags securite (14 tests)
# ---------------------------------------------------------------------------

def test_runtime_modified_false(p73):
    assert p73["runtime_modified"] is False


def test_sigma_modified_false(p73):
    assert p73["sigma_modified"] is False


def test_routes_modified_false(p73):
    assert p73["routes_modified"] is False


def test_srl_modified_false(p73):
    assert p73["srl_modified"] is False


def test_connectors_modified_false(p73):
    assert p73["connectors_modified"] is False


def test_source_packs_modified_false(p73):
    assert p73["source_packs_modified"] is False


def test_proofs_modified_false(p73):
    assert p73["proofs_modified"] is False


def test_lean_proofs_modified_false(p73):
    assert p73["lean_proofs_modified"] is False


def test_act_enabled_false(p73):
    assert p73["act_enabled"] is False


def test_memory_write_enabled_false(p73):
    assert p73["memory_write_enabled"] is False


def test_graphiti_write_enabled_false(p73):
    assert p73["graphiti_write_enabled"] is False


def test_neo4j_write_enabled_false(p73):
    assert p73["neo4j_write_enabled"] is False


def test_kernel_mutation_enabled_false(p73):
    assert p73["kernel_mutation_enabled"] is False


def test_x108_merge_enabled_false(p73):
    assert p73["x108_merge_enabled"] is False


# ---------------------------------------------------------------------------
# Section 12 — Regressions P56E->P72 (17 tests)
# ---------------------------------------------------------------------------

def _run(test_path: str) -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-q", "--tb=no", "--no-header"],
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
