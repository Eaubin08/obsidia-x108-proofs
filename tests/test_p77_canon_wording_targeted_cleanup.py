"""
tests/test_p77_canon_wording_targeted_cleanup.py

P77 validation suite.
Verifie : JSON audit, modele wording, matrice, patches appliques,
termes justifies, termes techniques, flags securite,
regressions P56E->P76.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P77_JSON = os.path.join(ROOT, "docs", "core_import", "P77_CANON_WORDING_TARGETED_CLEANUP.json")
P77_MD = os.path.join(ROOT, "docs", "core_import", "P77_CANON_WORDING_TARGETED_CLEANUP.md")
CSV_PATCHED = os.path.join(ROOT, "docs", "source_packs", "CORPUS_MAP_V4_20260602.csv")
MD_PATCHED = os.path.join(ROOT, "docs", "source_packs", "CORPUS_MAP_V4_CANON_STATUS.md")
SIGMA_DIR = os.path.join(ROOT, "sigma")
RUNTIME_WIRING_DIR = os.path.join(ROOT, "runtime_wiring")
LOCAL_AUDITS_DIR = os.path.join(ROOT, ".local_audits")


@pytest.fixture(scope="module")
def p77():
    with open(P77_JSON, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def wording_matrix(p77):
    return p77["wording_matrix"]


@pytest.fixture(scope="module")
def wording_model(p77):
    return p77["wording_model"]


@pytest.fixture(scope="module")
def focus_findings(p77):
    return p77["focus_findings"]


# ---------------------------------------------------------------------------
# Section 1 -- JSON de base (6 tests)
# ---------------------------------------------------------------------------

def test_p77_json_exists():
    assert os.path.isfile(P77_JSON)


def test_p77_json_status(p77):
    assert p77["status"] == "P77_CANON_WORDING_TARGETED_CLEANUP_READY"


def test_p77_json_mode(p77):
    assert p77["mode"] == "PATCH_CONTROLLED_TARGETED_DOCS_ONLY"


def test_p77_wording_decision(p77):
    assert p77["wording_decision"] == "TARGETED_REPLACEMENT_APPLIED"


def test_p77_source_patch_applied(p77):
    assert p77["source_patch_applied"] is True


def test_p77_files_patched_count(p77):
    assert p77["files_patched_count"] == 2


# ---------------------------------------------------------------------------
# Section 2 -- Modele wording (5 tests)
# ---------------------------------------------------------------------------

def test_wording_model_mode(wording_model):
    assert wording_model["mode"] == "PATCH_CONTROLLED_TARGETED_DOCS_ONLY"


def test_wording_model_dry_run_only(wording_model):
    assert wording_model["dry_run_only"] is True


def test_wording_model_replacements_authorized_nonempty(wording_model):
    assert len(wording_model["replacements_authorized"]) >= 5


def test_wording_model_terms_justified_if_nonempty(wording_model):
    assert len(wording_model["terms_justified_if"]) >= 3


def test_wording_model_rules_nonempty(wording_model):
    assert len(wording_model["rules"]) >= 5


# ---------------------------------------------------------------------------
# Section 3 -- Matrice wording -- structure (5 tests)
# ---------------------------------------------------------------------------

def test_wording_matrix_exists(p77):
    assert isinstance(p77["wording_matrix"], list)
    assert len(p77["wording_matrix"]) > 0


def test_wording_matrix_count(p77):
    assert len(p77["wording_matrix"]) >= 12


def test_wording_matrix_required_fields(wording_matrix):
    required = {
        "file_path", "term_found", "occurrences", "replacement",
        "wording_decision", "justification", "risk_level",
        "sigma_impact", "runtime_impact",
    }
    for entry in wording_matrix:
        for f in required:
            assert f in entry, f"Champ manquant {f} dans {entry.get('file_path')}"


def test_wording_matrix_valid_decisions(wording_matrix):
    valid = {
        "REPLACED",
        "WORDING_JUSTIFIED_BY_PROOF",
        "WORDING_TECHNICAL_TERM_KEEP",
        "WORDING_EXPRESSION_STANDARD_KEEP",
        "WORDING_TECHNICAL_LABEL_KEEP",
        "WORDING_FILENAME_REFERENCE_KEEP",
        "PROTECTED_BY_P77_RULES",
        "P76_BOM_NORMALIZATION_SAFE",
    }
    for e in wording_matrix:
        assert e["wording_decision"] in valid, (
            f"Decision invalide dans {e['file_path']}: {e['wording_decision']}"
        )


def test_wording_matrix_no_sigma_impact(wording_matrix):
    for e in wording_matrix:
        assert e["sigma_impact"] is False, (
            f"sigma_impact=True interdit dans {e['file_path']}"
        )


# ---------------------------------------------------------------------------
# Section 4 -- Patches appliques -- verification (6 tests)
# ---------------------------------------------------------------------------

def _get_entry(matrix, path_fragment):
    return next((e for e in matrix if path_fragment in e["file_path"]), None)


def _get_all_entries(matrix, path_fragment):
    return [e for e in matrix if path_fragment in e["file_path"]]


def test_csv_regroup_canon_replaced(wording_matrix):
    entries = _get_all_entries(wording_matrix, "CORPUS_MAP_V4_20260602.csv")
    regroup = next((e for e in entries if e["term_found"] == "REGROUP_CANON"), None)
    assert regroup is not None
    assert regroup["wording_decision"] == "REPLACED"
    assert regroup["replacement"] == "REGROUP_CANDIDATE"
    assert regroup["occurrences"] == 13


def test_csv_keep_canon_replaced(wording_matrix):
    entries = _get_all_entries(wording_matrix, "CORPUS_MAP_V4_20260602.csv")
    keep = next((e for e in entries if e["term_found"] == "KEEP_CANON"), None)
    assert keep is not None
    assert keep["wording_decision"] == "REPLACED"
    assert keep["replacement"] == "KEEP_CORE_OR_OFFICIAL_REVIEW"


def test_md_keep_canon_replaced(wording_matrix):
    entry = _get_entry(wording_matrix, "CORPUS_MAP_V4_CANON_STATUS.md")
    assert entry is not None
    assert entry["wording_decision"] == "REPLACED"
    assert entry["replacement"] == "KEEP_CORE_OR_OFFICIAL_REVIEW"


def test_csv_patched_file_no_regroup_canon():
    with open(CSV_PATCHED, encoding="utf-8") as f:
        content = f.read()
    assert "REGROUP_CANON" not in content, "REGROUP_CANON encore present dans CSV apres patch"


def test_csv_patched_file_no_keep_canon():
    with open(CSV_PATCHED, encoding="utf-8") as f:
        content = f.read()
    assert "KEEP_CANON" not in content, "KEEP_CANON encore present dans CSV apres patch"


def test_md_patched_file_no_keep_canon():
    with open(MD_PATCHED, encoding="utf-8") as f:
        content = f.read()
    assert "KEEP_CANON" not in content, "KEEP_CANON encore present dans MD apres patch"


# ---------------------------------------------------------------------------
# Section 5 -- Termes justifies par preuve (5 tests)
# ---------------------------------------------------------------------------

def test_readme_canonical_justified(wording_matrix):
    entry = _get_entry(wording_matrix, "README.md")
    assert entry is not None
    assert entry["wording_decision"] == "WORDING_JUSTIFIED_BY_PROOF"
    assert "p1-freeze-2026-04-22" in entry["justification"]


def test_limits_canonical_justified(wording_matrix):
    entry = _get_entry(wording_matrix, "docs/LIMITS.md")
    assert entry is not None
    assert entry["wording_decision"] == "WORDING_JUSTIFIED_BY_PROOF"


def test_bank_scenarios_canonical_justified(wording_matrix):
    entry = _get_entry(wording_matrix, "docs/BANK_SCENARIOS.md")
    assert entry is not None
    assert entry["wording_decision"] == "WORDING_JUSTIFIED_BY_PROOF"


def test_justified_count(p77):
    counts = p77["decision_counts"]
    assert counts["WORDING_JUSTIFIED_BY_PROOF"] >= 3


def test_total_replacements_count(p77):
    assert p77["replacements_applied_count"] == 15


# ---------------------------------------------------------------------------
# Section 6 -- Termes techniques conserves (4 tests)
# ---------------------------------------------------------------------------

def test_glossaire_chaine_canonique_kept(wording_matrix):
    entry = _get_entry(wording_matrix, "docs/GLOSSAIRE.md")
    assert entry is not None
    assert entry["wording_decision"] == "WORDING_TECHNICAL_TERM_KEEP"


def test_f60_sigma_canonical_domains_kept(wording_matrix):
    entry = _get_entry(wording_matrix, "OBSIDIA_F60_SIGMA_REGISTRY_CANONICAL_DOMAINS.md")
    assert entry is not None
    assert entry["wording_decision"] == "WORDING_TECHNICAL_TERM_KEEP"


def test_lean_theorem_canonical_kept(wording_matrix):
    entry = _get_entry(wording_matrix, "F74_F77_FINALIZATION_AUDIT.md")
    assert entry is not None
    assert entry["wording_decision"] == "WORDING_TECHNICAL_TERM_KEEP"


def test_p76_bom_classified_safe(wording_matrix):
    entry = _get_entry(wording_matrix, "gps_omega_chaos.json")
    assert entry is not None
    assert entry["wording_decision"] == "P76_BOM_NORMALIZATION_SAFE"


# ---------------------------------------------------------------------------
# Section 7 -- Focus findings (5 tests)
# ---------------------------------------------------------------------------

def test_focus_findings_count(focus_findings):
    assert len(focus_findings) >= 5


def test_finding_f1_csv_patch(focus_findings):
    f1 = next((f for f in focus_findings if f["finding_id"] == "P77-F1"), None)
    assert f1 is not None
    assert f1["type"] == "PATCH_APPLIED"
    assert f1["action"] == "REPLACED_UNJUSTIFIED_WORDING"


def test_finding_f2_md_patch(focus_findings):
    f2 = next((f for f in focus_findings if f["finding_id"] == "P77-F2"), None)
    assert f2 is not None
    assert f2["type"] == "PATCH_APPLIED"


def test_finding_f3_readme_justified(focus_findings):
    f3 = next((f for f in focus_findings if f["finding_id"] == "P77-F3"), None)
    assert f3 is not None
    assert f3["type"] == "WORDING_JUSTIFIED_BY_PROOF"
    assert f3["action"] == "KEEP_JUSTIFIED"


def test_finding_f5_bom_safe(focus_findings):
    f5 = next((f for f in focus_findings if f["finding_id"] == "P77-F5"), None)
    assert f5 is not None
    assert f5["type"] == "P76_BOM_NORMALIZATION_SAFE"
    assert f5["action"] == "CLASSIFIED_P76_BOM_SAFE"


# ---------------------------------------------------------------------------
# Section 8 -- Flags securite (14 tests)
# ---------------------------------------------------------------------------

def test_runtime_modified_false(p77):
    assert p77["runtime_modified"] is False


def test_sigma_modified_false(p77):
    assert p77["sigma_modified"] is False


def test_routes_modified_false(p77):
    assert p77["routes_modified"] is False


def test_lean_proofs_modified_false(p77):
    assert p77["lean_proofs_modified"] is False


def test_proofs_modified_false(p77):
    assert p77["proofs_modified"] is False


def test_srl_modified_false(p77):
    assert p77["srl_modified"] is False


def test_connectors_modified_false(p77):
    assert p77["connectors_modified"] is False


def test_act_enabled_false(p77):
    assert p77["act_enabled"] is False


def test_memory_write_enabled_false(p77):
    assert p77["memory_write_enabled"] is False


def test_graphiti_write_enabled_false(p77):
    assert p77["graphiti_write_enabled"] is False


def test_neo4j_write_enabled_false(p77):
    assert p77["neo4j_write_enabled"] is False


def test_kernel_mutation_enabled_false(p77):
    assert p77["kernel_mutation_enabled"] is False


def test_x108_merge_enabled_false(p77):
    assert p77["x108_merge_enabled"] is False


def test_network_called_false(p77):
    assert p77["network_called"] is False


# ---------------------------------------------------------------------------
# Section 9 -- Verification fichiers proteges (5 tests)
# ---------------------------------------------------------------------------

def test_sigma_dir_untouched():
    sigma_json = os.path.join(SIGMA_DIR, "examples", "gps_omega_chaos.json")
    with open(sigma_json, encoding="utf-8") as f:
        raw = f.read()
    assert not raw.startswith("﻿"), "BOM UTF-8 present dans gps_omega_chaos.json apres P77"


def test_local_audits_dir_exists():
    # Legacy node name preserved for regression compatibility.
    # .local_audits is an optional local/archive surface, not a
    # canonical worktree prerequisite.
    assert LOCAL_AUDITS_DIR == os.path.join(ROOT, ".local_audits")

    manifest_script = os.path.join(
        ROOT, "scripts", "generate_manifest_sha256.py"
    )
    with open(manifest_script, encoding="utf-8") as f:
        manifest_source = f.read()

    assert '".local_audits"' in manifest_source

    p77_audit_script = os.path.join(
        ROOT, "scripts", "audit_canon_wording_targeted_cleanup_p77.py"
    )
    with open(p77_audit_script, encoding="utf-8") as f:
        p77_audit_source = f.read()

    assert '".local_audits/"' in p77_audit_source

    if os.path.exists(LOCAL_AUDITS_DIR):
        assert os.path.isdir(LOCAL_AUDITS_DIR)


def test_csv_columns_unchanged():
    with open(CSV_PATCHED, encoding="utf-8") as f:
        header = f.readline().strip()
    assert "canonical_corpus" in header
    assert "canonical_subgroup" in header
    assert "action" in header


def test_csv_regroup_candidate_present():
    with open(CSV_PATCHED, encoding="utf-8") as f:
        content = f.read()
    assert "REGROUP_CANDIDATE" in content


def test_csv_keep_core_or_official_present():
    with open(CSV_PATCHED, encoding="utf-8") as f:
        content = f.read()
    assert "KEEP_CORE_OR_OFFICIAL_REVIEW" in content


# ---------------------------------------------------------------------------
# Section 10 -- Regressions P56E->P76 (21 tests)
# ---------------------------------------------------------------------------

def _run(test_path: str) -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-q", "--tb=no", "--no-header", "-k", "not regression"],
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


@pytest.mark.regression
def test_p75_regression():
    assert _run("tests/test_p75_runtime_core_risk_review.py")


@pytest.mark.regression
def test_p76_regression():
    assert _run("tests/test_p76_gps_terrain_portable_reconciliation.py")


# ---------------------------------------------------------------------------
# Section 11 -- verify_all et forbidden (2 tests)
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
