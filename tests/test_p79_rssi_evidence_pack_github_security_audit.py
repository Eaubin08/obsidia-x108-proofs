"""
Tests P79 — RSSI Evidence Pack and GitHub Security Audit
"""

import json
import os
import pytest

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
P79_JSON = os.path.join(REPO_ROOT, "docs", "core_import", "P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT.json")
P79_MD = os.path.join(REPO_ROOT, "docs", "core_import", "P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT.md")
P79_SCRIPT = os.path.join(REPO_ROOT, "scripts", "audit_rssi_evidence_pack_github_security_p79.py")


@pytest.fixture(scope="module")
def p79():
    with open(P79_JSON, encoding="utf-8") as f:
        return json.load(f)


# ──────────────────────────────────────────────
# Section 1 — JSON de base
# ──────────────────────────────────────────────

def test_p79_json_exists():
    assert os.path.exists(P79_JSON), f"P79 JSON absent : {P79_JSON}"


def test_p79_status(p79):
    assert p79["status"] == "P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT_READY"


def test_p79_mode(p79):
    assert p79["mode"] == "AUDIT_AND_DOCS_ONLY"


def test_p79_rssi_decision(p79):
    assert p79["rssi_decision"] == "LOCAL_RSSI_EVIDENCE_PACK_INDEXED"


def test_p79_github_security_decision(p79):
    assert p79["github_security_decision"] == "SECURITY_AUDIT_INDEXED_NO_PUBLICATION"


def test_p79_source_patch_applied(p79):
    assert p79["source_patch_applied"] is False


def test_p79_files_imported_count(p79):
    assert p79["files_imported_count"] == 0


def test_p79_next_step(p79):
    assert p79["next_step"] == "P80_FULL_REGRESSION_FREEZE"


# ──────────────────────────────────────────────
# Section 2 — Modèle RSSI
# ──────────────────────────────────────────────

def test_p79_rssi_model_present(p79):
    assert "rssi_model" in p79
    m = p79["rssi_model"]
    assert isinstance(m, dict)


def test_p79_rssi_model_evidence_core(p79):
    assert "evidence_core" in p79["rssi_model"]
    assert "Merkle" in p79["rssi_model"]["evidence_core"]
    assert "RFC3161" in p79["rssi_model"]["evidence_core"]


def test_p79_rssi_model_formal_proof(p79):
    assert "formal_proof" in p79["rssi_model"]
    assert "Lean" in p79["rssi_model"]["formal_proof"]


def test_p79_rssi_model_audit_trail(p79):
    assert "audit_trail" in p79["rssi_model"]
    assert "P56A" in p79["rssi_model"]["audit_trail"] or "P56" in p79["rssi_model"]["audit_trail"]


def test_p79_rssi_model_replay(p79):
    assert "replay" in p79["rssi_model"]
    assert "verify_all" in p79["rssi_model"]["replay"]


# ──────────────────────────────────────────────
# Section 3 — Modèle sécurité
# ──────────────────────────────────────────────

def test_p79_security_model_present(p79):
    assert "security_model" in p79
    m = p79["security_model"]
    assert isinstance(m, dict)


def test_p79_security_model_secret_risk(p79):
    assert "secret_risk" in p79["security_model"]
    assert "SECRET_VALUE_REDACTED" in p79["security_model"]["secret_risk"]


def test_p79_security_model_ci_present(p79):
    assert "ci_present" in p79["security_model"]
    assert "verify-proofs" in p79["security_model"]["ci_present"]


def test_p79_security_model_ci_missing(p79):
    assert "ci_missing" in p79["security_model"]


def test_p79_security_model_github_config(p79):
    assert "github_config_present" in p79["security_model"]
    assert "SECURITY.md" in p79["security_model"]["github_config_present"]


# ──────────────────────────────────────────────
# Section 4 — RSSI Evidence Matrix
# ──────────────────────────────────────────────

def test_p79_rssi_evidence_matrix_present(p79):
    assert "rssi_evidence_matrix" in p79
    assert isinstance(p79["rssi_evidence_matrix"], list)
    assert len(p79["rssi_evidence_matrix"]) > 0


def test_p79_rssi_evidence_matrix_has_merkle(p79):
    paths = [e["file_path"] for e in p79["rssi_evidence_matrix"]]
    assert "proofs/merkle_root.json" in paths


def test_p79_rssi_evidence_matrix_has_rfc3161(p79):
    paths = [e["file_path"] for e in p79["rssi_evidence_matrix"]]
    assert "proofs/rfc3161_anchor.json" in paths


def test_p79_rssi_evidence_matrix_has_lean(p79):
    paths = [e["file_path"] for e in p79["rssi_evidence_matrix"]]
    assert any("lean" in p for p in paths)


def test_p79_rssi_evidence_matrix_no_secret_displayed(p79):
    for entry in p79["rssi_evidence_matrix"]:
        reason = entry.get("reason", "")
        # Aucune valeur de secret réelle ne doit apparaître
        assert "obsidia_neo4j" not in reason.lower()
        assert "password=" not in reason.lower()


# ──────────────────────────────────────────────
# Section 5 — Pack RSSI (include_rssi_pack)
# ──────────────────────────────────────────────

def test_p79_include_rssi_pack_nonempty(p79):
    assert len(p79["include_rssi_pack"]) > 0


def test_p79_include_rssi_pack_has_merkle(p79):
    assert "proofs/merkle_root.json" in p79["include_rssi_pack"]


def test_p79_include_rssi_pack_has_rfc3161(p79):
    assert "proofs/rfc3161_anchor.json" in p79["include_rssi_pack"]


def test_p79_include_rssi_pack_has_lean(p79):
    assert any("lean" in p for p in p79["include_rssi_pack"])


def test_p79_include_rssi_pack_has_specs_00(p79):
    assert any("00_SCOPE_DISCIPLINE" in p for p in p79["include_rssi_pack"])


def test_p79_include_rssi_pack_has_specs_01(p79):
    assert any("01_X108_AUTHORITY" in p for p in p79["include_rssi_pack"])


def test_p79_include_rssi_pack_has_specs_09(p79):
    assert any("09_CRITICAL_WORLDS" in p for p in p79["include_rssi_pack"])


def test_p79_include_rssi_pack_has_specs_11(p79):
    assert any("11_PROOF_REPLAY_OS3" in p for p in p79["include_rssi_pack"])


# ──────────────────────────────────────────────
# Section 6 — Secret scan
# ──────────────────────────────────────────────

def test_p79_secret_scan_matrix_present(p79):
    assert "secret_scan_matrix" in p79
    assert isinstance(p79["secret_scan_matrix"], list)
    assert len(p79["secret_scan_matrix"]) > 0


def test_p79_secret_risks_nonempty(p79):
    assert len(p79["secret_risks"]) > 0


def test_p79_secret_scan_no_real_values_displayed(p79):
    for entry in p79["secret_scan_matrix"]:
        secret_val = entry.get("secret_value", "")
        assert secret_val == "SECRET_VALUE_REDACTED" or secret_val == ""


def test_p79_secret_scan_neo4j_detected(p79):
    types = [e.get("secret_type", "") for e in p79["secret_scan_matrix"]]
    assert any("NEO4J" in t for t in types)


def test_p79_secret_scan_requires_rotation_flagged(p79):
    actions = [e.get("action_required", "") or "" for e in p79["secret_scan_matrix"]]
    assert any("REQUIRES_SECRET_ROTATION" in a for a in actions)


# ──────────────────────────────────────────────
# Section 7 — GitHub Security Matrix
# ──────────────────────────────────────────────

def test_p79_github_security_matrix_present(p79):
    assert "github_security_matrix" in p79
    assert isinstance(p79["github_security_matrix"], list)
    assert len(p79["github_security_matrix"]) > 0


def test_p79_ci_present_nonempty(p79):
    assert len(p79["ci_present"]) >= 2


def test_p79_ci_present_has_verify_proofs(p79):
    assert any("verify-proofs" in p for p in p79["ci_present"])


def test_p79_ci_present_has_periphery_ci(p79):
    assert any("periphery" in p for p in p79["ci_present"])


def test_p79_github_config_present_security_md(p79):
    assert any("SECURITY" in p for p in p79["github_config_present"])


def test_p79_github_config_missing_codeowners(p79):
    assert any("CODEOWNERS" in p for p in p79["github_config_missing"])


def test_p79_github_config_missing_dependabot(p79):
    assert any("dependabot" in p for p in p79["github_config_missing"])


def test_p79_branch_protection_review_flagged(p79):
    assert len(p79["branch_protection_review"]) > 0


# ──────────────────────────────────────────────
# Section 8 — Flags sécurité (boundary)
# ──────────────────────────────────────────────

def test_p79_runtime_not_modified(p79):
    assert p79["runtime_modified"] is False


def test_p79_sigma_not_modified(p79):
    assert p79["sigma_modified"] is False


def test_p79_routes_not_modified(p79):
    assert p79["routes_modified"] is False


def test_p79_srl_not_modified(p79):
    assert p79["srl_modified"] is False


def test_p79_connectors_not_modified(p79):
    assert p79["connectors_modified"] is False


def test_p79_source_packs_not_modified(p79):
    assert p79["source_packs_modified"] is False


def test_p79_proofs_not_modified(p79):
    assert p79["proofs_modified"] is False


def test_p79_lean_proofs_not_modified(p79):
    assert p79["lean_proofs_modified"] is False


def test_p79_act_not_enabled(p79):
    assert p79["act_enabled"] is False


def test_p79_memory_write_not_enabled(p79):
    assert p79["memory_write_enabled"] is False


def test_p79_graphiti_write_not_enabled(p79):
    assert p79["graphiti_write_enabled"] is False


def test_p79_neo4j_write_not_enabled(p79):
    assert p79["neo4j_write_enabled"] is False


def test_p79_kernel_mutation_not_enabled(p79):
    assert p79["kernel_mutation_enabled"] is False


def test_p79_x108_merge_not_enabled(p79):
    assert p79["x108_merge_enabled"] is False


def test_p79_github_not_pushed(p79):
    assert p79["github_pushed"] is False


def test_p79_github_pr_not_created(p79):
    assert p79["github_pr_created"] is False


def test_p79_public_release_not_created(p79):
    assert p79["public_release_created"] is False


# ──────────────────────────────────────────────
# Section 9 — Index docs créés
# ──────────────────────────────────────────────

def test_p79_md_exists():
    assert os.path.exists(P79_MD), f"P79 MD absent : {P79_MD}"


def test_p79_script_exists():
    assert os.path.exists(P79_SCRIPT), f"P79 script absent : {P79_SCRIPT}"


def test_p79_rssi_readme_exists():
    path = os.path.join(REPO_ROOT, "docs", "rssi", "README_RSSI_EVIDENCE_PACK.md")
    assert os.path.exists(path), f"README RSSI absent : {path}"


def test_p79_rssi_evidence_index_exists():
    path = os.path.join(REPO_ROOT, "docs", "rssi", "RSSI_EVIDENCE_INDEX.md")
    assert os.path.exists(path), f"RSSI Evidence Index absent : {path}"


def test_p79_rssi_evidence_boundary_exists():
    path = os.path.join(REPO_ROOT, "docs", "rssi", "RSSI_EVIDENCE_BOUNDARY.md")
    assert os.path.exists(path), f"RSSI Evidence Boundary absent : {path}"


def test_p79_rssi_do_not_publish_exists():
    path = os.path.join(REPO_ROOT, "docs", "rssi", "RSSI_DO_NOT_PUBLISH.md")
    assert os.path.exists(path), f"RSSI DO_NOT_PUBLISH absent : {path}"


def test_p79_github_security_audit_exists():
    path = os.path.join(REPO_ROOT, "docs", "security", "GITHUB_SECURITY_AUDIT.md")
    assert os.path.exists(path), f"GitHub Security Audit absent : {path}"


def test_p79_pre_publication_checklist_exists():
    path = os.path.join(REPO_ROOT, "docs", "security", "PRE_PUBLICATION_SECURITY_CHECKLIST.md")
    assert os.path.exists(path), f"Pre-Publication Checklist absent : {path}"


def test_p79_created_indexes_count(p79):
    assert len(p79["created_indexes"]) >= 6


# ──────────────────────────────────────────────
# Section 10 — Focus findings
# ──────────────────────────────────────────────

def test_p79_focus_findings_present(p79):
    assert "focus_findings" in p79
    assert isinstance(p79["focus_findings"], list)
    assert len(p79["focus_findings"]) >= 7


def test_p79_finding_rssi_pack_indexed(p79):
    ids = [f["id"] for f in p79["focus_findings"]]
    assert "P79-F1" in ids


def test_p79_finding_secret_risk(p79):
    types = [f["type"] for f in p79["focus_findings"]]
    assert "SECRET_RISK_DETECTED" in types


def test_p79_finding_ci_gaps(p79):
    types = [f["type"] for f in p79["focus_findings"]]
    assert "CI_SECURITY_GAPS" in types


def test_p79_finding_rfc3161_verified(p79):
    ids = [f["id"] for f in p79["focus_findings"]]
    assert "P79-F7" in ids


def test_p79_finding_gitignore_inconsistency(p79):
    types = [f["type"] for f in p79["focus_findings"]]
    assert "GITIGNORE_INCONSISTENCY" in types


# ──────────────────────────────────────────────
# Section 11 — Contraintes héritées
# ──────────────────────────────────────────────

def test_p79_p78_constraints_applied(p79):
    assert "p78_public_private_constraints_applied" in p79
    c = p79["p78_public_private_constraints_applied"]
    assert isinstance(c, list)
    assert len(c) > 0


def test_p79_p77_constraints_applied(p79):
    assert "p77_wording_constraints_applied" in p79
    c = p79["p77_wording_constraints_applied"]
    assert any("sigma" in x.lower() or "PROTECTED" in x for x in c)


def test_p79_p72_constraints_applied(p79):
    assert "p72_proof_constraints_applied" in p79
    c = p79["p72_proof_constraints_applied"]
    assert any("LEAN_PROVEN" in x for x in c)


def test_p79_p78_do_not_publish_preserved(p79):
    do_not = p79["do_not_publish"]
    assert any("sigma" in p for p in do_not)
    assert any("world_action_bus" in p for p in do_not)


# ──────────────────────────────────────────────
# Section 12 — Régressions P56E→P78
# ──────────────────────────────────────────────

@pytest.mark.regression
def test_regression_p56d_sigma_veto():
    path = os.path.join(REPO_ROOT, "docs", "core_import", "P56D_SIGMA_POST_GUARD_VETO_BOUNDARY.md")
    assert os.path.exists(path)


@pytest.mark.regression
def test_regression_p72_json_intact():
    path = os.path.join(REPO_ROOT, "docs", "core_import", "P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT.json")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["status"] == "P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT_READY"


@pytest.mark.regression
def test_regression_p77_json_intact():
    path = os.path.join(REPO_ROOT, "docs", "core_import", "P77_CANON_WORDING_TARGETED_CLEANUP.json")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["status"] == "P77_CANON_WORDING_TARGETED_CLEANUP_READY"


@pytest.mark.regression
def test_regression_p78_json_intact():
    path = os.path.join(REPO_ROOT, "docs", "core_import", "P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT.json")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["status"] == "P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT_READY"


@pytest.mark.regression
def test_regression_sigma_not_modified():
    sigma_dir = os.path.join(REPO_ROOT, "sigma")
    assert os.path.isdir(sigma_dir)
    # sigma/ doit exister mais ne doit pas avoir de fichiers P79 ajoutés
    sigma_files = os.listdir(sigma_dir)
    assert not any("p79" in f.lower() for f in sigma_files)


@pytest.mark.regression
def test_regression_lean_proofs_intact():
    lean_dir = os.path.join(REPO_ROOT, "proofs", "lean")
    assert os.path.isdir(lean_dir)


@pytest.mark.regression
def test_regression_merkle_root_intact():
    path = os.path.join(REPO_ROOT, "proofs", "merkle_root.json")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert "merkle_root" in data
    assert len(data["merkle_root"]) == 64  # SHA-256 hex


@pytest.mark.regression
def test_regression_rfc3161_intact():
    path = os.path.join(REPO_ROOT, "proofs", "rfc3161_anchor.json")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["hash_algorithm"] == "SHA-256"
    assert data["serial_number"] == "0x03572CED"


@pytest.mark.regression
def test_regression_security_md_intact():
    path = os.path.join(REPO_ROOT, "SECURITY.md")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        content = f.read()
    assert "security@obsidia.io" in content


@pytest.mark.regression
def test_regression_p78_public_boundary_intact():
    path = os.path.join(REPO_ROOT, "docs", "public", "README_PUBLIC_BOUNDARY.md")
    assert os.path.exists(path)


@pytest.mark.regression
def test_regression_p78_proof_boundary_intact():
    path = os.path.join(REPO_ROOT, "docs", "proof", "README_PROOF_BOUNDARY.md")
    assert os.path.exists(path)


@pytest.mark.regression
def test_regression_p78_investor_boundary_intact():
    path = os.path.join(REPO_ROOT, "docs", "investor", "README_INVESTOR_BOUNDARY.md")
    assert os.path.exists(path)


@pytest.mark.regression
def test_regression_p78_demo_boundary_intact():
    path = os.path.join(REPO_ROOT, "docs", "demo", "README_DEMO_BOUNDARY.md")
    assert os.path.exists(path)


@pytest.mark.regression
def test_regression_gitignore_excludes_env():
    path = os.path.join(REPO_ROOT, ".gitignore")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        content = f.read()
    assert ".env" in content
    assert "!.env.example" in content


@pytest.mark.regression
def test_regression_ci_verify_proofs_intact():
    path = os.path.join(REPO_ROOT, ".github", "workflows", "verify-proofs.yml")
    assert os.path.exists(path)


@pytest.mark.regression
def test_regression_ci_periphery_intact():
    path = os.path.join(REPO_ROOT, ".github", "workflows", "x108-periphery-ci.yml")
    assert os.path.exists(path)


@pytest.mark.regression
def test_regression_connectors_not_in_public_safe(p79):
    public = p79["public_safe"]
    assert not any("connectors" in p for p in public)


@pytest.mark.regression
def test_regression_sigma_not_in_public_safe(p79):
    public = p79["public_safe"]
    assert not any(p.startswith("sigma") or p == "sigma/" for p in public)


@pytest.mark.regression
def test_regression_p75_no_runtime_import():
    path = os.path.join(REPO_ROOT, "docs", "core_import", "P75_RUNTIME_CORE_RISK_REVIEW.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("runtime_import_decision") == "NO_RUNTIME_IMPORT" or \
               data.get("status", "").endswith("READY")


@pytest.mark.regression
def test_regression_p76_bom_normalization_safe():
    path = os.path.join(REPO_ROOT, "docs", "core_import", "P76_GPS_TERRAIN_PORTABLE_RECONCILIATION.json")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("status", "").endswith("READY")


@pytest.mark.regression
def test_regression_corpus_map_no_regroup_canon():
    csv_path = os.path.join(REPO_ROOT, "docs", "source_packs", "CORPUS_MAP_V4_20260602.csv")
    if os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as f:
            content = f.read()
        assert "REGROUP_CANON" not in content


@pytest.mark.regression
def test_regression_p79_dry_run_only(p79):
    assert p79.get("dry_run_only") is True


# ──────────────────────────────────────────────
# Section 13 — verify_all + forbidden
# ──────────────────────────────────────────────

def test_p79_verify_all_boundary(p79):
    from scripts.audit_rssi_evidence_pack_github_security_p79 import verify_all
    assert verify_all(p79) is True


def test_p79_no_forbidden_terms_in_report(p79):
    report_str = json.dumps(p79)
    # Termes interdits : valeurs de secrets réelles, wording non justifié
    forbidden_fragments = [
        "obsidia_neo4j_2026",  # valeur réelle détectée lors de l'audit
        "REGROUP_CANON",       # remplacé en P77
        "KEEP_CANON",          # remplacé en P77
    ]
    for fragment in forbidden_fragments:
        assert fragment not in report_str, f"Fragment interdit trouvé dans rapport P79 : {fragment!r}"
