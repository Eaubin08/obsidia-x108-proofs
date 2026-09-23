"""
Tests P80 — Full Regression Freeze
"""

import json
import os
import pytest

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
P80_JSON = os.path.join(REPO_ROOT, "docs", "core_import", "P80_FULL_REGRESSION_FREEZE.json")
P80_MD = os.path.join(REPO_ROOT, "docs", "core_import", "P80_FULL_REGRESSION_FREEZE.md")
P80_SCRIPT = os.path.join(REPO_ROOT, "scripts", "audit_full_regression_freeze_p80.py")


@pytest.fixture(scope="module")
def p80():
    with open(P80_JSON, encoding="utf-8") as f:
        return json.load(f)


# ──────────────────────────────────────────────
# Section 1 — JSON de base
# ──────────────────────────────────────────────

def test_p80_json_exists():
    assert os.path.exists(P80_JSON), f"P80 JSON absent : {P80_JSON}"


def test_p80_status(p80):
    assert p80["status"] == "P80_FULL_REGRESSION_FREEZE_READY"


def test_p80_mode(p80):
    assert p80["mode"] == "LOCAL_FREEZE_CONTROLLED"


def test_p80_freeze_decision(p80):
    assert p80["freeze_decision"] == "LOCAL_FREEZE_APPROVED_WITH_SECURITY_NOTE"


def test_p80_public_release_blocked(p80):
    assert p80["public_release_decision"] == "PUBLIC_RELEASE_BLOCKED"


def test_p80_merge_blocked(p80):
    assert p80["merge_decision"] == "MERGE_BLOCKED_PENDING_REVIEW"


def test_p80_source_patch_not_applied(p80):
    assert p80["source_patch_applied"] is False


def test_p80_files_imported_zero(p80):
    assert p80["files_imported_count"] == 0


def test_p80_next_step(p80):
    assert p80["next_step"] == "POST_P80_SECRET_ROTATION_AND_PUBLICATION_HARDENING"


# ──────────────────────────────────────────────
# Section 2 — Modèle freeze
# ──────────────────────────────────────────────

def test_p80_freeze_model_present(p80):
    assert "freeze_model" in p80
    m = p80["freeze_model"]
    assert isinstance(m, dict)


def test_p80_freeze_model_local_freeze(p80):
    assert "local_freeze" in p80["freeze_model"]
    assert "APPROVED" in p80["freeze_model"]["local_freeze"].upper() or "approve" in p80["freeze_model"]["local_freeze"].lower()


def test_p80_freeze_model_public_release_blocked(p80):
    assert "public_release" in p80["freeze_model"]
    assert "BLOQUE" in p80["freeze_model"]["public_release"].upper() or "BLOCK" in p80["freeze_model"]["public_release"].upper()


def test_p80_freeze_model_secret_note(p80):
    assert "security_note" in p80["freeze_model"]
    assert "SECRET_VALUE_REDACTED" in p80["freeze_model"]["security_note"]


def test_p80_freeze_model_manifest(p80):
    assert "manifest" in p80["freeze_model"]
    assert "MANIFEST_VERIFIED" in p80["freeze_model"]["manifest"]


# ──────────────────────────────────────────────
# Section 3 — Paliers
# ──────────────────────────────────────────────

def test_p80_paliers_checked_present(p80):
    assert "paliers_checked" in p80
    assert isinstance(p80["paliers_checked"], list)
    assert len(p80["paliers_checked"]) >= 24


def test_p80_paliers_count_all_present(p80):
    paliers = [p["palier"] for p in p80["paliers_checked"]]
    for expected in ["P56A", "P57", "P58", "P65", "P72", "P76", "P77", "P78", "P79"]:
        assert expected in paliers, f"Palier {expected} absent de paliers_checked"


def test_p80_p79_palier_status(p80):
    p79 = next((p for p in p80["paliers_checked"] if p["palier"] == "P79"), None)
    assert p79 is not None
    assert p79["json_status"] == "P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT_READY"
    assert p79["commit"] == "b275c51"


def test_p80_p78_palier_status(p80):
    p78 = next((p for p in p80["paliers_checked"] if p["palier"] == "P78"), None)
    assert p78 is not None
    assert p78["commit"] == "d944b5a"


def test_p80_p72_palier_status(p80):
    p72 = next((p for p in p80["paliers_checked"] if p["palier"] == "P72"), None)
    assert p72 is not None
    assert p72["commit"] == "1d61ebb"


# ──────────────────────────────────────────────
# Section 4 — Chaîne de commits
# ──────────────────────────────────────────────

def test_p80_commit_chain_present(p80):
    assert "commit_chain" in p80
    assert len(p80["commit_chain"]) >= 15


def test_p80_commit_chain_p65(p80):
    c = next((x for x in p80["commit_chain"] if x["palier"] == "P65"), None)
    assert c is not None
    assert c["commit"] == "759b6d9"


def test_p80_commit_chain_p79(p80):
    c = next((x for x in p80["commit_chain"] if x["palier"] == "P79"), None)
    assert c is not None
    assert c["commit"] == "b275c51"


def test_p80_commit_chain_ordered(p80):
    paliers = [int(c["palier"][1:]) for c in p80["commit_chain"]]
    assert paliers == sorted(paliers), "Commit chain not ordered by palier number"


# ──────────────────────────────────────────────
# Section 5 — Tests / Vérifications
# ──────────────────────────────────────────────

def test_p80_verify_all_pass(p80):
    assert p80["verify_all_status"] == "PASS"


def test_p80_forbidden_content_pass(p80):
    assert p80["forbidden_content_status"] == "FORBIDDEN_CONTENT_PASS"


def test_p80_manifest_verified(p80):
    assert p80["manifest_status"] == "MANIFEST_VERIFIED"


def test_p80_manifest_file_count(p80):
    assert p80.get("manifest_file_count", 0) > 0


def test_p80_tests_passed_nonempty(p80):
    assert len(p80["tests_passed"]) > 0


def test_p80_tests_failed_empty(p80):
    assert p80["tests_failed"] == []


# ──────────────────────────────────────────────
# Section 6 — Sécurité / Blockers
# ──────────────────────────────────────────────

def test_p80_secret_rotation_required(p80):
    assert p80["secret_rotation_required"] is True


def test_p80_publication_blocked(p80):
    assert p80.get("publication_blocked") is True


def test_p80_local_freeze_approved(p80):
    assert p80.get("local_freeze_approved") is True


def test_p80_security_blockers_present(p80):
    assert "security_blockers" in p80
    assert len(p80["security_blockers"]) >= 5


def test_p80_security_blocker_secret_rotation(p80):
    types = [b["type"] for b in p80["security_blockers"]]
    assert "REQUIRES_SECRET_ROTATION" in types


def test_p80_security_blockers_no_secret_value_displayed(p80):
    for blocker in p80["security_blockers"]:
        val = blocker.get("secret_value", "")
        if val:
            assert val == "SECRET_VALUE_REDACTED"


def test_p80_publication_blockers_nonempty(p80):
    assert len(p80["publication_blockers"]) >= 5


def test_p80_no_real_secret_in_report(p80):
    report_str = json.dumps(p80)
    assert "obsidia_neo4j_2026" not in report_str


# ──────────────────────────────────────────────
# Section 7 — Git status
# ──────────────────────────────────────────────

def test_p80_git_status_findings_present(p80):
    assert "git_status_findings" in p80
    assert len(p80["git_status_findings"]) >= 2


def test_p80_git_status_local_noise_only(p80):
    classifications = [f["classification"] for f in p80["git_status_findings"]]
    assert all(c == "GIT_STATUS_LOCAL_NOISE_ONLY" for c in classifications)


def test_p80_world_action_bus_not_staged(p80):
    wab = next((f for f in p80["git_status_findings"] if "world_action_bus" in f["file"]), None)
    assert wab is not None
    assert "NE PAS STAGER" in wab["action"] or "NOT_STAGED" in wab.get("action", "")


def test_p80_claude_settings_not_staged(p80):
    cs = next((f for f in p80["git_status_findings"] if "settings.json" in f["file"]), None)
    assert cs is not None
    assert "NE PAS STAGER" in cs["action"] or "NOT_STAGED" in cs.get("action", "")


# ──────────────────────────────────────────────
# Section 8 — Surfaces protégées
# ──────────────────────────────────────────────

def test_p80_protected_surface_findings_present(p80):
    assert "protected_surface_findings" in p80
    assert len(p80["protected_surface_findings"]) >= 5


def test_p80_sigma_intact(p80):
    sigma = next((f for f in p80["protected_surface_findings"] if "sigma" in f["surface"]), None)
    assert sigma is not None
    assert sigma["status"] in ("INTACT", "MODIFIED_LOCAL_ONLY")


def test_p80_lean_intact(p80):
    lean = next((f for f in p80["protected_surface_findings"] if "lean" in f["surface"]), None)
    assert lean is not None
    assert lean["status"] == "INTACT"


def test_p80_connectors_intact(p80):
    conn = next((f for f in p80["protected_surface_findings"] if "connectors" in f["surface"]), None)
    assert conn is not None
    assert conn["status"] == "INTACT"


# ──────────────────────────────────────────────
# Section 9 — Flags boundary
# ──────────────────────────────────────────────

def test_p80_runtime_not_modified(p80):
    assert p80["runtime_modified"] is False


def test_p80_sigma_not_modified(p80):
    assert p80["sigma_modified"] is False


def test_p80_routes_not_modified(p80):
    assert p80["routes_modified"] is False


def test_p80_connectors_not_modified(p80):
    assert p80["connectors_modified"] is False


def test_p80_proofs_not_modified(p80):
    assert p80["proofs_modified"] is False


def test_p80_lean_proofs_not_modified(p80):
    assert p80["lean_proofs_modified"] is False


def test_p80_act_not_enabled(p80):
    assert p80["act_enabled"] is False


def test_p80_memory_write_not_enabled(p80):
    assert p80["memory_write_enabled"] is False


def test_p80_github_not_pushed(p80):
    assert p80["github_pushed"] is False


def test_p80_github_pr_not_created(p80):
    assert p80["github_pr_created"] is False


def test_p80_public_release_not_created(p80):
    assert p80["public_release_created"] is False


# ──────────────────────────────────────────────
# Section 10 — Index docs créés
# ──────────────────────────────────────────────

def test_p80_md_exists():
    assert os.path.exists(P80_MD)


def test_p80_script_exists():
    assert os.path.exists(P80_SCRIPT)


def test_p80_freeze_ledger_exists():
    path = os.path.join(REPO_ROOT, "docs", "freeze", "P80_FULL_REGRESSION_FREEZE_LEDGER.md")
    assert os.path.exists(path)


def test_p80_local_freeze_limits_exists():
    path = os.path.join(REPO_ROOT, "docs", "freeze", "P80_LOCAL_FREEZE_LIMITS.md")
    assert os.path.exists(path)


def test_p80_publication_blockers_doc_exists():
    path = os.path.join(REPO_ROOT, "docs", "freeze", "P80_PUBLICATION_BLOCKERS.md")
    assert os.path.exists(path)


def test_p80_created_indexes_count(p80):
    assert len(p80["created_indexes"]) >= 5


# ──────────────────────────────────────────────
# Section 11 — Post-freeze actions
# ──────────────────────────────────────────────

def test_p80_post_freeze_actions_present(p80):
    assert "post_freeze_actions" in p80
    assert len(p80["post_freeze_actions"]) >= 8


def test_p80_post_freeze_secret_rotation(p80):
    actions = [a["action"] for a in p80["post_freeze_actions"]]
    assert "SECRET_ROTATION" in actions


def test_p80_post_freeze_codeowners(p80):
    actions = [a["action"] for a in p80["post_freeze_actions"]]
    assert "ADD_CODEOWNERS" in actions


def test_p80_post_freeze_branch_protection(p80):
    actions = [a["action"] for a in p80["post_freeze_actions"]]
    assert "ADD_BRANCH_PROTECTION" in actions


# ──────────────────────────────────────────────
# Section 12 — Régressions P56E→P79
# ──────────────────────────────────────────────

@pytest.mark.regression
def test_regression_p56d_sigma_veto_intact():
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
def test_regression_p79_json_intact():
    path = os.path.join(REPO_ROOT, "docs", "core_import", "P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT.json")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["status"] == "P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT_READY"


@pytest.mark.regression
def test_regression_merkle_root_intact():
    path = os.path.join(REPO_ROOT, "proofs", "merkle_root.json")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["merkle_root"]) == 64


@pytest.mark.regression
def test_regression_rfc3161_intact():
    path = os.path.join(REPO_ROOT, "proofs", "rfc3161_anchor.json")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["hash_algorithm"] == "SHA-256"


@pytest.mark.regression
def test_regression_security_md_intact():
    path = os.path.join(REPO_ROOT, "SECURITY.md")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        content = f.read()
    assert "security@obsidia.io" in content


@pytest.mark.regression
def test_regression_lean_proofs_dir_intact():
    lean_dir = os.path.join(REPO_ROOT, "proofs", "lean")
    assert os.path.isdir(lean_dir)


@pytest.mark.regression
def test_regression_sigma_dir_intact():
    assert os.path.isdir(os.path.join(REPO_ROOT, "sigma"))


@pytest.mark.regression
def test_regression_corpus_map_no_regroup_canon():
    csv_path = os.path.join(REPO_ROOT, "docs", "source_packs", "CORPUS_MAP_V4_20260602.csv")
    if os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as f:
            content = f.read()
        assert "REGROUP_CANON" not in content


@pytest.mark.regression
def test_regression_ci_verify_proofs_intact():
    assert os.path.exists(os.path.join(REPO_ROOT, ".github", "workflows", "verify-proofs.yml"))


@pytest.mark.regression
def test_regression_ci_periphery_intact():
    assert os.path.exists(os.path.join(REPO_ROOT, ".github", "workflows", "x108-periphery-ci.yml"))


@pytest.mark.regression
def test_regression_gitignore_excludes_env():
    path = os.path.join(REPO_ROOT, ".gitignore")
    with open(path, encoding="utf-8") as f:
        content = f.read()
    assert ".env" in content
    assert "!.env.example" in content


@pytest.mark.regression
def test_regression_p80_dry_run_only(p80):
    assert p80.get("dry_run_only") is True


@pytest.mark.regression
def test_regression_rssi_readme_intact():
    assert os.path.exists(os.path.join(REPO_ROOT, "docs", "rssi", "README_RSSI_EVIDENCE_PACK.md"))


@pytest.mark.regression
def test_regression_github_security_audit_intact():
    assert os.path.exists(os.path.join(REPO_ROOT, "docs", "security", "GITHUB_SECURITY_AUDIT.md"))


@pytest.mark.regression
def test_regression_pre_publication_checklist_intact():
    assert os.path.exists(os.path.join(REPO_ROOT, "docs", "security", "PRE_PUBLICATION_SECURITY_CHECKLIST.md"))


@pytest.mark.regression
def test_regression_p78_public_boundary_intact():
    assert os.path.exists(os.path.join(REPO_ROOT, "docs", "public", "README_PUBLIC_BOUNDARY.md"))


@pytest.mark.regression
def test_regression_p78_proof_boundary_intact():
    assert os.path.exists(os.path.join(REPO_ROOT, "docs", "proof", "README_PROOF_BOUNDARY.md"))


@pytest.mark.regression
def test_regression_sigma_not_in_post_freeze_rssi_pack(p80):
    # Le pack RSSI ne doit pas inclure sigma/
    public_decisions = [b["action"] for b in p80["post_freeze_actions"]]
    assert not any("sigma" in a.lower() and "include" in a.lower() for a in public_decisions)


# ──────────────────────────────────────────────
# Section 13 — verify_all + forbidden
# ──────────────────────────────────────────────

def test_p80_verify_all_boundary(p80):
    from scripts.audit_full_regression_freeze_p80 import verify_all
    assert verify_all(p80) is True


def test_p80_no_forbidden_terms_in_report(p80):
    report_str = json.dumps(p80)
    forbidden_fragments = [
        "obsidia_neo4j_2026",
        "REGROUP_CANON",
        "KEEP_CANON",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in report_str, f"Fragment interdit dans rapport P80 : {fragment!r}"
