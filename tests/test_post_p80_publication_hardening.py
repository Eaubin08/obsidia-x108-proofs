"""
Tests post-P80 Publication Security Hardening
Mode : SECURITY_HARDENING_CONTROLLED
"""

import json
import os
import sys
import importlib
import pytest

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
JSON_PATH = os.path.join(REPO_ROOT, "docs", "core_import",
                         "POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.json")
MD_PATH = os.path.join(REPO_ROOT, "docs", "core_import",
                       "POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.md")
SCRIPT_PATH = os.path.join(REPO_ROOT, "scripts",
                            "audit_post_p80_publication_hardening.py")

BOUNDARY_FLAGS = [
    "runtime_modified", "sigma_modified", "routes_modified", "srl_modified",
    "connectors_modified", "source_packs_modified", "proofs_modified",
    "lean_proofs_modified", "act_enabled", "memory_write_enabled",
    "graphiti_write_enabled", "neo4j_write_enabled", "kernel_mutation_enabled",
    "x108_merge_enabled", "github_pushed", "github_pr_created",
    "public_release_created",
]

SEC_IDS = ["SEC-1", "SEC-2", "SEC-3", "SEC-4", "SEC-5", "SEC-6"]

FORBIDDEN_TERMS = [
    "NEO4J_URI=", "neo4j_uri=",
    "NEO4J_USER=", "neo4j_user=",
    "password=bolt", "bolt+s://",
    "REGROUP_CANON",
]


@pytest.fixture(scope="module")
def report():
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


# ── Section 1 : Fichiers de sortie existent ───────────────────────────────────

def test_post_p80_json_exists():
    assert os.path.isfile(JSON_PATH)


def test_post_p80_md_exists():
    assert os.path.isfile(MD_PATH)


def test_post_p80_script_exists():
    assert os.path.isfile(SCRIPT_PATH)


# ── Section 2 : Champs de base ────────────────────────────────────────────────

def test_post_p80_status(report):
    assert report["status"] == "POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING_READY"


def test_post_p80_mode(report):
    assert report["mode"] == "SECURITY_HARDENING_CONTROLLED"


def test_post_p80_branch(report):
    assert report["branch"] == "post-p80-secret-rotation-publication-hardening"


def test_post_p80_dry_run_only(report):
    assert report["dry_run_only"] is True


def test_post_p80_date_present(report):
    assert "date" in report
    assert len(report["date"]) == 10


def test_post_p80_next_step(report):
    assert report["next_step"] == "OPTIONAL_PUBLICATION_READINESS_RECHECK"


def test_post_p80_publication_decision(report):
    assert report["publication_decision"] == "STILL_BLOCKED_UNTIL_SECRET_ROTATED_EXTERNALLY"


def test_post_p80_local_freeze_status(report):
    assert report["local_freeze_status"] == "LOCAL_FREEZE_APPROVED_WITH_SECURITY_NOTE"


# ── Section 3 : Flags boundary (tous False) ───────────────────────────────────

@pytest.mark.parametrize("flag", BOUNDARY_FLAGS)
def test_post_p80_boundary_flag_false(report, flag):
    assert report[flag] is False, f"BOUNDARY VIOLATION: {flag} must be False"


def test_post_p80_secret_value_not_printed(report):
    assert report["secret_value_printed"] is False


def test_post_p80_source_patch_not_applied(report):
    assert report["source_patch_applied"] is False


def test_post_p80_files_imported_count_zero(report):
    assert report["files_imported_count"] == 0


# ── Section 4 : Blockers SEC-1 à SEC-6 ───────────────────────────────────────

def test_post_p80_blockers_count(report):
    assert len(report["blockers_status"]) == 6


@pytest.mark.parametrize("sec_id", SEC_IDS)
def test_post_p80_blocker_id_present(report, sec_id):
    ids = [b["id"] for b in report["blockers_status"]]
    assert sec_id in ids


def test_post_p80_blockers_resolved_count(report):
    assert report["blockers_resolved_count"] == 4


def test_post_p80_blockers_unresolved_count(report):
    assert report["blockers_unresolved_count"] == 2


def test_post_p80_sec1_not_resolved(report):
    sec1 = next(b for b in report["blockers_status"] if b["id"] == "SEC-1")
    assert sec1["resolved"] is False


def test_post_p80_sec1_secret_redacted(report):
    sec1 = next(b for b in report["blockers_status"] if b["id"] == "SEC-1")
    assert "SECRET_VALUE_REDACTED" in sec1["description"]


def test_post_p80_sec1_still_blocks(report):
    sec1 = next(b for b in report["blockers_status"] if b["id"] == "SEC-1")
    assert "STILL_BLOCKS" in sec1["publication_impact"]


def test_post_p80_sec2_resolved(report):
    sec2 = next(b for b in report["blockers_status"] if b["id"] == "SEC-2")
    assert sec2["resolved"] is True
    assert "CODEOWNERS" in sec2["resolution"]


def test_post_p80_sec3_resolved(report):
    sec3 = next(b for b in report["blockers_status"] if b["id"] == "SEC-3")
    assert sec3["resolved"] is True
    assert "DEPENDABOT" in sec3["resolution"]


def test_post_p80_sec4_not_resolved(report):
    sec4 = next(b for b in report["blockers_status"] if b["id"] == "SEC-4")
    assert sec4["resolved"] is False
    assert "MANUAL" in sec4["resolution"].upper()


def test_post_p80_sec5_resolved(report):
    sec5 = next(b for b in report["blockers_status"] if b["id"] == "SEC-5")
    assert sec5["resolved"] is True
    assert "SECRET_SCAN_CI" in sec5["resolution"]


def test_post_p80_sec6_resolved(report):
    sec6 = next(b for b in report["blockers_status"] if b["id"] == "SEC-6")
    assert sec6["resolved"] is True
    assert "GITIGNORE" in sec6["resolution"]


def test_post_p80_all_blockers_have_local_freeze_none(report):
    for b in report["blockers_status"]:
        assert b["local_freeze_impact"] == "NONE", f"{b['id']} : local_freeze_impact should be NONE"


# ── Section 5 : Créations GitHub ─────────────────────────────────────────────

def test_post_p80_codeowners_created(report):
    assert report["codeowners_created"] is True


def test_post_p80_dependabot_created(report):
    assert report["dependabot_created"] is True


def test_post_p80_branch_protection_policy_created(report):
    assert report["branch_protection_policy_created"] is True


def test_post_p80_secret_scan_ci_created(report):
    assert report["secret_scan_ci_created"] is True


def test_post_p80_proofkit_gitignore_reviewed(report):
    assert report["proofkit_gitignore_reviewed"] is True


def test_post_p80_secret_rotation_required(report):
    assert report["secret_rotation_required"] is True


# ── Section 6 : Gitignore changes ────────────────────────────────────────────

def test_post_p80_gitignore_changes_present(report):
    assert len(report["gitignore_changes"]) >= 1


def test_post_p80_gitignore_proofkit_removed(report):
    entries = [c["entry"] for c in report["gitignore_changes"]]
    assert "proofs/PROOFKIT_REPORT.json" in entries


def test_post_p80_gitignore_action_removed(report):
    change = report["gitignore_changes"][0]
    assert change["action"] == "REMOVED_ENTRY"


# ── Section 7 : Background runs ──────────────────────────────────────────────

def test_post_p80_background_runs_checked(report):
    assert report["background_runs_checked"] is True


def test_post_p80_background_runs_count(report):
    assert len(report["background_runs"]) == 2


def test_post_p80_background_run_ids(report):
    ids = [r["run_id"] for r in report["background_runs"]]
    assert "bjfgvb09f" in ids
    assert "bfif00lx5" in ids


# ── Section 8 : Created files ─────────────────────────────────────────────────

def test_post_p80_created_files_count(report):
    assert len(report["created_files"]) == 10


def test_post_p80_created_files_codeowners(report):
    assert ".github/CODEOWNERS" in report["created_files"]


def test_post_p80_created_files_dependabot(report):
    assert ".github/dependabot.yml" in report["created_files"]


def test_post_p80_created_files_secret_scan(report):
    assert ".github/workflows/secret-scan.yml" in report["created_files"]


def test_post_p80_created_files_json(report):
    assert "docs/core_import/POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.json" in report["created_files"]


# ── Section 9 : Checklist post-publication ───────────────────────────────────

def test_post_p80_checklist_present(report):
    assert len(report["post_publication_checklist"]) >= 5


def test_post_p80_checklist_contains_rotation(report):
    checklist_str = " ".join(report["post_publication_checklist"])
    assert "NEO4J" in checklist_str or "rotation" in checklist_str.lower()


def test_post_p80_checklist_contains_verify_all(report):
    checklist_str = " ".join(report["post_publication_checklist"])
    assert "verify_all" in checklist_str


# ── Section 10 : Remaining blockers ──────────────────────────────────────────

def test_post_p80_remaining_blockers_count(report):
    assert len(report["remaining_blockers"]) == 2


def test_post_p80_remaining_blocker_sec1(report):
    joined = " ".join(report["remaining_blockers"])
    assert "SEC-1" in joined


def test_post_p80_remaining_blocker_sec4(report):
    joined = " ".join(report["remaining_blockers"])
    assert "SEC-4" in joined


# ── Section 11 : Contenu interdit dans le JSON ───────────────────────────────

def test_post_p80_no_forbidden_terms_in_report():
    with open(JSON_PATH, encoding="utf-8") as f:
        content = f.read()
    for term in FORBIDDEN_TERMS:
        assert term not in content, f"Terme interdit trouvé dans le JSON : {term}"


def test_post_p80_no_real_secret_value():
    with open(JSON_PATH, encoding="utf-8") as f:
        content = f.read()
    assert "SECRET_VALUE_REDACTED" in content or "secret_value_printed" in content
    forbidden_patterns = ["bolt+s://", "NEO4J_URI=bolt", "password="]
    for p in forbidden_patterns:
        assert p not in content, f"Pattern secret potentiel dans JSON : {p}"


# ── Section 12 : Script Python boundary ──────────────────────────────────────

def test_post_p80_script_has_dry_run_only():
    with open(SCRIPT_PATH, encoding="utf-8") as f:
        content = f.read()
    assert "DRY_RUN_ONLY: bool = True" in content


def test_post_p80_script_has_boundary_dict():
    with open(SCRIPT_PATH, encoding="utf-8") as f:
        content = f.read()
    assert "_BOUNDARY" in content


def test_post_p80_script_has_verify_all():
    with open(SCRIPT_PATH, encoding="utf-8") as f:
        content = f.read()
    assert "def verify_all" in content


def test_post_p80_script_has_run_audit():
    with open(SCRIPT_PATH, encoding="utf-8") as f:
        content = f.read()
    assert "def run_audit" in content


def test_post_p80_script_no_secret_printed():
    with open(SCRIPT_PATH, encoding="utf-8") as f:
        content = f.read()
    for term in FORBIDDEN_TERMS:
        assert term not in content, f"Terme interdit dans script : {term}"


# ── Section 13 : Fichiers créés accessibles ──────────────────────────────────

def test_post_p80_codeowners_file_exists():
    path = os.path.join(REPO_ROOT, ".github", "CODEOWNERS")
    assert os.path.isfile(path)


def test_post_p80_dependabot_file_exists():
    path = os.path.join(REPO_ROOT, ".github", "dependabot.yml")
    assert os.path.isfile(path)


def test_post_p80_secret_scan_workflow_exists():
    path = os.path.join(REPO_ROOT, ".github", "workflows", "secret-scan.yml")
    assert os.path.isfile(path)


def test_post_p80_secret_rotation_plan_exists():
    path = os.path.join(REPO_ROOT, "docs", "security", "POST_P80_SECRET_ROTATION_PLAN.md")
    assert os.path.isfile(path)


def test_post_p80_publication_hardening_plan_exists():
    path = os.path.join(REPO_ROOT, "docs", "security", "POST_P80_PUBLICATION_HARDENING_PLAN.md")
    assert os.path.isfile(path)


def test_post_p80_branch_protection_policy_exists():
    path = os.path.join(REPO_ROOT, "docs", "security", "BRANCH_PROTECTION_POLICY.md")
    assert os.path.isfile(path)


# ── Section 14 : verify_all programmatique ───────────────────────────────────

def test_post_p80_verify_all_passes():
    sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
    spec = importlib.util.spec_from_file_location(
        "audit_post_p80", SCRIPT_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    report_data = mod.run_audit()
    result = mod.verify_all(report_data)
    assert result is True


# ── Section 15 : Régressions P79/P80 ─────────────────────────────────────────

def test_regression_p79_json_exists():
    path = os.path.join(REPO_ROOT, "docs", "core_import",
                        "P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT.json")
    assert os.path.isfile(path)


def test_regression_p80_json_exists():
    path = os.path.join(REPO_ROOT, "docs", "core_import",
                        "P80_FULL_REGRESSION_FREEZE.json")
    assert os.path.isfile(path)


def test_regression_p79_status():
    path = os.path.join(REPO_ROOT, "docs", "core_import",
                        "P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["status"] == "P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT_READY"


def test_regression_p80_status():
    path = os.path.join(REPO_ROOT, "docs", "core_import",
                        "P80_FULL_REGRESSION_FREEZE.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["status"] == "P80_FULL_REGRESSION_FREEZE_READY"


def test_regression_p80_next_step():
    path = os.path.join(REPO_ROOT, "docs", "core_import",
                        "P80_FULL_REGRESSION_FREEZE.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["next_step"] == "POST_P80_SECRET_ROTATION_AND_PUBLICATION_HARDENING"


def test_regression_p80_merge_blocked():
    path = os.path.join(REPO_ROOT, "docs", "core_import",
                        "P80_FULL_REGRESSION_FREEZE.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["merge_decision"] == "MERGE_BLOCKED_PENDING_REVIEW"


def test_regression_p80_public_release_blocked():
    path = os.path.join(REPO_ROOT, "docs", "core_import",
                        "P80_FULL_REGRESSION_FREEZE.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["public_release_decision"] == "PUBLIC_RELEASE_BLOCKED"


def test_regression_p79_boundary_all_false():
    path = os.path.join(REPO_ROOT, "docs", "core_import",
                        "P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for flag in BOUNDARY_FLAGS:
        if flag in data:
            assert data[flag] is False, f"P79: {flag} doit être False"


def test_regression_p80_boundary_all_false():
    path = os.path.join(REPO_ROOT, "docs", "core_import",
                        "P80_FULL_REGRESSION_FREEZE.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for flag in BOUNDARY_FLAGS:
        if flag in data:
            assert data[flag] is False, f"P80: {flag} doit être False"


def test_regression_gitignore_proofkit_entry_removed():
    gitignore_path = os.path.join(REPO_ROOT, ".gitignore")
    with open(gitignore_path, encoding="utf-8") as f:
        content = f.read()
    assert "proofs/PROOFKIT_REPORT.json" not in content or "intentionnellement traque" in content


def test_regression_codeowners_contains_sigma():
    path = os.path.join(REPO_ROOT, ".github", "CODEOWNERS")
    with open(path, encoding="utf-8") as f:
        content = f.read()
    assert "sigma/" in content


def test_regression_secret_scan_yml_contains_trufflehog():
    path = os.path.join(REPO_ROOT, ".github", "workflows", "secret-scan.yml")
    with open(path, encoding="utf-8") as f:
        content = f.read()
    assert "trufflehog" in content.lower()
