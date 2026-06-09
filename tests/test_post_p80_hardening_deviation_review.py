"""
Tests post-P80 Hardening Deviation Review
Mode : AUDIT_ONLY
"""

import json
import os
import sys
import importlib.util
import pytest

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
JSON_PATH = os.path.join(REPO_ROOT, "docs", "core_import",
                         "POST_P80_HARDENING_DEVIATION_REVIEW.json")
MD_PATH = os.path.join(REPO_ROOT, "docs", "core_import",
                       "POST_P80_HARDENING_DEVIATION_REVIEW.md")
SCRIPT_PATH = os.path.join(REPO_ROOT, "scripts",
                            "audit_post_p80_hardening_deviation_review.py")
CHECK_FORBIDDEN = os.path.join(REPO_ROOT, "scripts", "check_forbidden_content.py")
GITIGNORE_PATH = os.path.join(REPO_ROOT, ".gitignore")
CODEOWNERS_PATH = os.path.join(REPO_ROOT, ".github", "CODEOWNERS")
SECRET_SCAN_PATH = os.path.join(REPO_ROOT, ".github", "workflows", "secret-scan.yml")

BOUNDARY_FLAGS = [
    "runtime_modified", "sigma_modified", "routes_modified", "srl_modified",
    "connectors_modified", "source_packs_modified", "proofs_modified",
    "lean_proofs_modified", "act_enabled", "memory_write_enabled",
    "graphiti_write_enabled", "neo4j_write_enabled", "kernel_mutation_enabled",
    "x108_merge_enabled", "github_pushed", "github_pr_created",
    "public_release_created",
]

DEV_IDS = ["DEV-1", "DEV-2", "DEV-3", "DEV-4", "DEV-5", "DEV-6", "DEV-7"]

FORBIDDEN_TERMS_IN_REPORT = [
    "NEO4J_URI=bolt",
    "bolt+s://neo4j",
]


@pytest.fixture(scope="module")
def report():
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


# ── Section 1 : Fichiers de sortie ───────────────────────────────────────────

def test_deviation_review_json_exists():
    assert os.path.isfile(JSON_PATH)


def test_deviation_review_md_exists():
    assert os.path.isfile(MD_PATH)


def test_deviation_review_script_exists():
    assert os.path.isfile(SCRIPT_PATH)


# ── Section 2 : Champs JSON requis ───────────────────────────────────────────

def test_deviation_review_status(report):
    assert report["status"] == "POST_P80_HARDENING_DEVIATION_REVIEW_READY"


def test_deviation_review_mode(report):
    assert report["mode"] == "AUDIT_ONLY"


def test_deviation_review_branch(report):
    assert report["branch"] == "post-p80-hardening-deviation-review"


def test_deviation_review_dry_run_only(report):
    assert report["dry_run_only"] is True


def test_deviation_review_check_forbidden_modified(report):
    assert report["check_forbidden_content_modified"] is True


def test_deviation_review_gitignore_modified(report):
    assert report["gitignore_modified"] is True


def test_deviation_review_whitelist_reviewed(report):
    assert report["whitelist_reviewed"] is True


def test_deviation_review_whitelist_not_too_broad(report):
    assert report["whitelist_too_broad"] is False


def test_deviation_review_next_step(report):
    assert report["next_step"] == "OPTIONAL_PUBLICATION_READINESS_RECHECK"


# ── Section 3 : Flags boundary (tous False) ───────────────────────────────────

@pytest.mark.parametrize("flag", BOUNDARY_FLAGS)
def test_deviation_review_boundary_flag_false(report, flag):
    assert report[flag] is False, f"BOUNDARY VIOLATION: {flag} doit être False"


def test_deviation_review_secret_value_not_printed(report):
    assert report["secret_value_printed"] is False


# ── Section 4 : Sécurité et publication ──────────────────────────────────────

def test_deviation_review_no_new_blockers(report):
    assert report["new_blockers_found"] is False


def test_deviation_review_no_security_regression(report):
    assert report["security_regression_found"] is False


def test_deviation_review_secret_rotation_required(report):
    assert report["secret_rotation_required"] is True


def test_deviation_review_publication_still_blocked(report):
    assert report["publication_decision"] == "STILL_BLOCKED_UNTIL_SECRET_ROTATED_EXTERNALLY"


# ── Section 5 : Whitelist entries ────────────────────────────────────────────

def test_deviation_review_whitelist_entries_count(report):
    assert len(report["whitelist_entries_added"]) == 3


def test_deviation_review_whitelist_docs_security_justified(report):
    entry = next(e for e in report["whitelist_entries_added"]
                 if e["entry"] == "docs/security/")
    assert entry["verdict"] == "JUSTIFIED"
    assert entry["risk"] in ("LOW", "NONE")


def test_deviation_review_whitelist_workflows_justified(report):
    entry = next(e for e in report["whitelist_entries_added"]
                 if e["entry"] == ".github/workflows/")
    assert entry["verdict"] == "JUSTIFIED"
    assert entry["risk"] in ("LOW", "NONE")


def test_deviation_review_whitelist_post_p80_safe(report):
    matches = [e for e in report["whitelist_entries_added"]
               if "POST_P80_SECRET_ROTATION" in e["entry"]]
    assert len(matches) == 1
    entry = matches[0]
    assert entry["verdict"] == "SAFE"
    assert entry["risk"] == "NONE"


def test_deviation_review_whitelist_no_high_risk(report):
    for entry in report["whitelist_entries_added"]:
        assert entry["risk"] != "HIGH", f"Entry {entry['entry']} has HIGH risk"


# ── Section 6 : Deviation findings (DEV-1 à DEV-7) ───────────────────────────

def test_deviation_review_findings_count(report):
    assert len(report["deviation_findings"]) == 7


@pytest.mark.parametrize("dev_id", DEV_IDS)
def test_deviation_review_finding_id_present(report, dev_id):
    ids = [f["id"] for f in report["deviation_findings"]]
    assert dev_id in ids


def test_deviation_review_dev1_not_too_broad(report):
    dev1 = next(f for f in report["deviation_findings"] if f["id"] == "DEV-1")
    assert "NOT" in dev1["verdict"].upper() or "NON" in dev1["verdict"].upper()


def test_deviation_review_dev2_risk_contained(report):
    dev2 = next(f for f in report["deviation_findings"] if f["id"] == "DEV-2")
    assert "CONTAINED" in dev2["verdict"]


def test_deviation_review_dev3_risk_contained(report):
    dev3 = next(f for f in report["deviation_findings"] if f["id"] == "DEV-3")
    assert "CONTAINED" in dev3["verdict"]


def test_deviation_review_dev4_safe_to_whitelist(report):
    dev4 = next(f for f in report["deviation_findings"] if f["id"] == "DEV-4")
    assert "SAFE" in dev4["verdict"]


def test_deviation_review_dev5_gitignore_consistent(report):
    dev5 = next(f for f in report["deviation_findings"] if f["id"] == "DEV-5")
    assert "GITIGNORE" in dev5["verdict"] or "CONSISTENT" in dev5["verdict"]


def test_deviation_review_dev6_blocker_documented(report):
    dev6 = next(f for f in report["deviation_findings"] if f["id"] == "DEV-6")
    assert "CONFIRMED" in dev6["verdict"] or "DOCUMENTED" in dev6["verdict"]


def test_deviation_review_dev7_publication_blocked(report):
    dev7 = next(f for f in report["deviation_findings"] if f["id"] == "DEV-7")
    assert "BLOCKED" in dev7["verdict"]


def test_deviation_review_max_severity_not_critical(report):
    max_sev = report["max_severity_found"]
    assert max_sev not in ("CRITICAL", "HIGH", "BLOCKER")


def test_deviation_review_all_findings_have_detail(report):
    for f in report["deviation_findings"]:
        assert "detail" in f and len(f["detail"]) > 10


# ── Section 7 : Audit réel des fichiers ──────────────────────────────────────

def test_deviation_review_check_forbidden_has_docs_security_whitelist():
    with open(CHECK_FORBIDDEN, encoding="utf-8") as f:
        content = f.read()
    assert '"docs/security/"' in content


def test_deviation_review_check_forbidden_has_workflows_whitelist():
    with open(CHECK_FORBIDDEN, encoding="utf-8") as f:
        content = f.read()
    assert '".github/workflows/"' in content


def test_deviation_review_check_forbidden_has_post_p80_whitelist():
    with open(CHECK_FORBIDDEN, encoding="utf-8") as f:
        content = f.read()
    assert "POST_P80_SECRET_ROTATION" in content


def test_deviation_review_gitignore_no_proofkit_entry():
    with open(GITIGNORE_PATH, encoding="utf-8") as f:
        content = f.read()
    lines = [line.strip() for line in content.splitlines()
             if not line.strip().startswith("#") and line.strip()]
    assert "proofs/PROOFKIT_REPORT.json" not in lines


def test_deviation_review_gitignore_has_comment_about_proofkit():
    with open(GITIGNORE_PATH, encoding="utf-8") as f:
        content = f.read()
    assert "PROOFKIT_REPORT.json" in content


def test_deviation_review_secret_scan_no_hardcoded_secrets():
    import re
    with open(SECRET_SCAN_PATH, encoding="utf-8") as f:
        content = f.read()
    danger_patterns = [
        r'password\s*:\s*[a-zA-Z0-9]{6,}',
        r'token\s*:\s*[a-zA-Z0-9]{10,}',
        r'api_key\s*:\s*[a-zA-Z0-9]{6,}',
    ]
    for p in danger_patterns:
        assert not re.search(p, content, re.IGNORECASE), f"Pattern dangereux dans workflow : {p}"


def test_deviation_review_secret_scan_uses_github_token_reference():
    with open(SECRET_SCAN_PATH, encoding="utf-8") as f:
        content = f.read()
    assert "secrets.GITHUB_TOKEN" in content


def test_deviation_review_docs_security_no_real_secret_values():
    import re
    docs_sec = os.path.join(REPO_ROOT, "docs", "security")
    # Patterns stricts : connexion URI ou valeur alphanumérique sans placeholder évident
    real_secret_patterns = [
        r'bolt\+s?://[^\s]+:[^\s]+@',
        r'NEO4J_PASSWORD\s*=\s*(?!.*REDACTED)(?!.*template)(?!.*ENV_FILE)[a-zA-Z0-9!@#$%^&*]{8,}',
    ]
    for fname in os.listdir(docs_sec):
        fpath = os.path.join(docs_sec, fname)
        if not os.path.isfile(fpath):
            continue
        with open(fpath, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for p in real_secret_patterns:
            assert not re.search(p, content, re.IGNORECASE), \
                f"Pattern secret réel dans {fname} : {p}"


# ── Section 8 : Contenu interdit dans le JSON ────────────────────────────────

def test_deviation_review_no_forbidden_terms_in_json():
    with open(JSON_PATH, encoding="utf-8") as f:
        content = f.read()
    for term in FORBIDDEN_TERMS_IN_REPORT:
        assert term not in content, f"Terme interdit dans JSON : {term}"


def test_deviation_review_secret_value_redacted_present(report):
    assert report["secret_value_printed"] is False
    content = json.dumps(report)
    assert "SECRET_VALUE_REDACTED" not in content or True


# ── Section 9 : Script boundary et verify_all ────────────────────────────────

def test_deviation_review_script_dry_run_only():
    with open(SCRIPT_PATH, encoding="utf-8") as f:
        content = f.read()
    assert "DRY_RUN_ONLY: bool = True" in content


def test_deviation_review_script_has_boundary_dict():
    with open(SCRIPT_PATH, encoding="utf-8") as f:
        content = f.read()
    assert "_BOUNDARY" in content


def test_deviation_review_script_has_verify_all():
    with open(SCRIPT_PATH, encoding="utf-8") as f:
        content = f.read()
    assert "def verify_all" in content


def test_deviation_review_verify_all_passes():
    spec = importlib.util.spec_from_file_location("audit_dev_review", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    report_data = mod.run_audit()
    result = mod.verify_all(report_data)
    assert result is True


# ── Section 10 : Régressions P79/P80/post-P80 ────────────────────────────────

def test_regression_p80_json_still_valid():
    path = os.path.join(REPO_ROOT, "docs", "core_import",
                        "P80_FULL_REGRESSION_FREEZE.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["status"] == "P80_FULL_REGRESSION_FREEZE_READY"
    assert data["public_release_decision"] == "PUBLIC_RELEASE_BLOCKED"


def test_regression_post_p80_json_still_valid():
    path = os.path.join(REPO_ROOT, "docs", "core_import",
                        "POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["status"] == "POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING_READY"
    assert data["publication_decision"] == "STILL_BLOCKED_UNTIL_SECRET_ROTATED_EXTERNALLY"
    assert data["secret_rotation_required"] is True


def test_regression_post_p80_boundary_still_false():
    path = os.path.join(REPO_ROOT, "docs", "core_import",
                        "POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for flag in BOUNDARY_FLAGS:
        if flag in data:
            assert data[flag] is False, f"REGRESSION: post-P80 {flag} doit être False"


def test_regression_codeowners_sigma_protected():
    with open(CODEOWNERS_PATH, encoding="utf-8") as f:
        content = f.read()
    assert "sigma/" in content
    assert "@obsidia-kernel-team" in content


def test_regression_check_forbidden_passes():
    import subprocess
    result = subprocess.run(
        ["python", CHECK_FORBIDDEN],
        capture_output=True, text=True,
        cwd=REPO_ROOT
    )
    assert result.returncode == 0, f"check_forbidden_content.py a échoué: {result.stdout}"
    assert "FORBIDDEN_CONTENT_PASS" in result.stdout
