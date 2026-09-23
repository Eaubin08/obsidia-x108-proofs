"""
Tests Optional Publication Readiness Recheck
Mode : AUDIT_ONLY
"""

import json
import os
import importlib.util
import subprocess
import pytest

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
JSON_PATH = os.path.join(REPO_ROOT, "docs", "core_import",
                         "OPTIONAL_PUBLICATION_READINESS_RECHECK.json")
MD_PATH = os.path.join(REPO_ROOT, "docs", "core_import",
                       "OPTIONAL_PUBLICATION_READINESS_RECHECK.md")
SCRIPT_PATH = os.path.join(REPO_ROOT, "scripts",
                            "audit_optional_publication_readiness_recheck.py")

BOUNDARY_FLAGS = [
    "runtime_modified", "sigma_modified", "routes_modified", "srl_modified",
    "connectors_modified", "source_packs_modified", "proofs_modified",
    "lean_proofs_modified", "act_enabled", "memory_write_enabled",
    "graphiti_write_enabled", "neo4j_write_enabled", "kernel_mutation_enabled",
    "x108_merge_enabled", "github_pushed", "github_pr_created",
    "public_release_created",
]

BG_RUN_IDS = ["bjfgvb09f", "bfif00lx5"]


@pytest.fixture(scope="module")
def report():
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


# ── Section 1 : Fichiers de sortie ───────────────────────────────────────────

def test_recheck_json_exists():
    assert os.path.isfile(JSON_PATH)


def test_recheck_md_exists():
    assert os.path.isfile(MD_PATH)


def test_recheck_script_exists():
    assert os.path.isfile(SCRIPT_PATH)


# ── Section 2 : Champs JSON requis ───────────────────────────────────────────

def test_recheck_status(report):
    assert report["status"] == "OPTIONAL_PUBLICATION_READINESS_RECHECK_READY"


def test_recheck_mode(report):
    assert report["mode"] == "AUDIT_ONLY"


def test_recheck_branch(report):
    assert report["branch"] == "optional-publication-readiness-recheck"


def test_recheck_dry_run_only(report):
    assert report["dry_run_only"] is True


def test_recheck_next_step(report):
    assert report["next_step"] == "MANUAL_EXTERNAL_CONFIRMATION_REQUIRED_SEC1_SEC4"


# ── Section 3 : Background runs ──────────────────────────────────────────────

def test_recheck_background_runs_checked(report):
    assert report["background_runs_checked"] is True


def test_recheck_background_runs_count(report):
    assert len(report["background_runs"]) == 2


@pytest.mark.parametrize("run_id", BG_RUN_IDS)
def test_recheck_background_run_id_present(report, run_id):
    ids = [r["run_id"] for r in report["background_runs"]]
    assert run_id in ids


def test_recheck_background_runs_timeout_or_complete(report):
    for run in report["background_runs"]:
        status = run["status"]
        assert any(k in status for k in [
            "TIMEOUT", "COMPLETED", "UNKNOWN", "ACTIVE"
        ]), f"Statut inattendu : {status}"


# ── Section 4 : Boundary flags ───────────────────────────────────────────────

@pytest.mark.parametrize("flag", BOUNDARY_FLAGS)
def test_recheck_boundary_flag_false(report, flag):
    assert report[flag] is False, f"BOUNDARY VIOLATION: {flag} doit être False"


def test_recheck_secret_value_not_printed(report):
    assert report["secret_value_printed"] is False


# ── Section 5 : Réponses aux 10 questions ────────────────────────────────────

def test_recheck_answers_count(report):
    assert len(report["recheck_answers"]) == 10


def test_recheck_q1_rotation_not_confirmed(report):
    q1 = next(q for q in report["recheck_answers"] if q["q"] == 1)
    assert q1["answer"] is False
    assert "ROTATION" in q1["verdict"].upper()


def test_recheck_q2_secret_value_absent(report):
    q2 = next(q for q in report["recheck_answers"] if q["q"] == 2)
    assert q2["answer"] is True
    assert "ABSENT" in q2["verdict"].upper() or "CONFIRM" in q2["verdict"].upper()


def test_recheck_q3_sec1_unresolved(report):
    q3 = next(q for q in report["recheck_answers"] if q["q"] == 3)
    assert q3["answer"] is False
    assert "UNRESOLVED" in q3["verdict"].upper() or "SEC1" in q3["verdict"].upper()


def test_recheck_q4_branch_protection_guide_only(report):
    q4 = next(q for q in report["recheck_answers"] if q["q"] == 4)
    assert q4["answer"] is False
    assert "GUIDE" in q4["verdict"].upper() or "MANUAL" in q4["verdict"].upper()


def test_recheck_q5_codeowners_exists(report):
    q5 = next(q for q in report["recheck_answers"] if q["q"] == 5)
    assert q5["answer"] is True
    assert "CODEOWNERS" in q5["verdict"].upper()


def test_recheck_q6_dependabot_exists(report):
    q6 = next(q for q in report["recheck_answers"] if q["q"] == 6)
    assert q6["answer"] is True
    assert "DEPENDABOT" in q6["verdict"].upper()


def test_recheck_q7_secret_scan_ci_exists(report):
    q7 = next(q for q in report["recheck_answers"] if q["q"] == 7)
    assert q7["answer"] is True
    assert "SECRET_SCAN" in q7["verdict"].upper() or "CI" in q7["verdict"].upper()


def test_recheck_q8_forbidden_content_pass(report):
    q8 = next(q for q in report["recheck_answers"] if q["q"] == 8)
    assert q8["answer"] is True
    assert "PASS" in q8["verdict"].upper()


def test_recheck_q9_verify_all_pass(report):
    q9 = next(q for q in report["recheck_answers"] if q["q"] == 9)
    assert q9["answer"] is True
    assert "PASS" in q9["verdict"].upper()


def test_recheck_q10_publication_still_blocked(report):
    q10 = next(q for q in report["recheck_answers"] if q["q"] == 10)
    assert q10["answer"] is False
    assert "BLOCKED" in q10["verdict"].upper()


def test_recheck_conditions_met_count(report):
    assert report["conditions_met_count"] == 6


def test_recheck_conditions_unmet_count(report):
    assert report["conditions_unmet_count"] == 4


# ── Section 6 : Fields spécifiés dans le JSON attendu ────────────────────────

def test_recheck_secret_rotation_documented_false(report):
    assert report["secret_rotation_documented"] is False


def test_recheck_branch_protection_documented_false(report):
    assert report["branch_protection_documented"] is False


def test_recheck_codeowners_exists(report):
    assert report["codeowners_exists"] is True


def test_recheck_dependabot_exists(report):
    assert report["dependabot_exists"] is True


def test_recheck_secret_scan_ci_exists(report):
    assert report["secret_scan_ci_exists"] is True


def test_recheck_verify_all_status(report):
    assert report["verify_all_status"] == "PASS"


def test_recheck_forbidden_content_status(report):
    assert report["forbidden_content_status"] == "FORBIDDEN_CONTENT_PASS"


def test_recheck_publication_still_blocked(report):
    assert report["publication_decision"] == "STILL_BLOCKED_UNTIL_SECRET_ROTATED_EXTERNALLY"


# ── Section 7 : Publication gate ─────────────────────────────────────────────

def test_recheck_gate_not_passed(report):
    assert report["publication_gate"]["gate_status"] == "GATE_NOT_PASSED"


def test_recheck_gate_unmet_conditions(report):
    unmet = report["publication_gate"]["unmet_conditions"]
    assert len(unmet) >= 1


def test_recheck_gate_counts_consistent(report):
    gate = report["publication_gate"]
    assert gate["conditions_met_count"] + gate["conditions_unmet_count"] == len(report["recheck_answers"])


# ── Section 8 : Fichiers GitHub vérifiés ─────────────────────────────────────

def test_recheck_codeowners_file_present():
    path = os.path.join(REPO_ROOT, ".github", "CODEOWNERS")
    assert os.path.isfile(path)


def test_recheck_dependabot_file_present():
    path = os.path.join(REPO_ROOT, ".github", "dependabot.yml")
    assert os.path.isfile(path)


def test_recheck_secret_scan_workflow_present():
    path = os.path.join(REPO_ROOT, ".github", "workflows", "secret-scan.yml")
    assert os.path.isfile(path)


def test_recheck_rotation_plan_present():
    path = os.path.join(REPO_ROOT, "docs", "security", "POST_P80_SECRET_ROTATION_PLAN.md")
    assert os.path.isfile(path)


def test_recheck_branch_protection_guide_present():
    path = os.path.join(REPO_ROOT, "docs", "security", "BRANCH_PROTECTION_POLICY.md")
    assert os.path.isfile(path)


# ── Section 9 : Vérifications live ───────────────────────────────────────────

def test_recheck_verify_all_live():
    result = subprocess.run(
        ["python", "proofs/verify_all.py"],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_recheck_forbidden_content_live():
    result = subprocess.run(
        ["python", "scripts/check_forbidden_content.py"],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    assert result.returncode == 0
    assert "FORBIDDEN_CONTENT_PASS" in result.stdout


def test_recheck_script_verify_all_passes():
    spec = importlib.util.spec_from_file_location("audit_recheck", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    report_data = mod.run_audit()
    result = mod.verify_all(report_data)
    assert result is True


# ── Section 10 : Absence de secrets dans les sorties ────────────────────────

def test_recheck_no_secret_value_in_json():
    with open(JSON_PATH, encoding="utf-8") as f:
        content = f.read()
    assert "bolt+s://neo4j" not in content
    assert "NEO4J_URI=bolt" not in content


def test_recheck_rotation_plan_no_real_value():
    import re
    path = os.path.join(REPO_ROOT, "docs", "security", "POST_P80_SECRET_ROTATION_PLAN.md")
    with open(path, encoding="utf-8") as f:
        content = f.read()
    assert not re.search(r'bolt\+s?://[^\s]+:[^\s]+@', content)


# ── Section 11 : Script structure ────────────────────────────────────────────

def test_recheck_script_dry_run_only():
    with open(SCRIPT_PATH, encoding="utf-8") as f:
        content = f.read()
    assert "DRY_RUN_ONLY: bool = True" in content


def test_recheck_script_boundary_dict():
    with open(SCRIPT_PATH, encoding="utf-8") as f:
        content = f.read()
    assert "_BOUNDARY" in content


def test_recheck_script_ten_questions():
    with open(SCRIPT_PATH, encoding="utf-8") as f:
        content = f.read()
    assert "RECHECK_ANSWERS" in content


# ── Section 12 : Régressions P79→post-P80 ────────────────────────────────────

def test_regression_p80_public_release_blocked():
    path = os.path.join(REPO_ROOT, "docs", "core_import",
                        "P80_FULL_REGRESSION_FREEZE.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["public_release_decision"] == "PUBLIC_RELEASE_BLOCKED"


def test_regression_post_p80_publication_still_blocked():
    path = os.path.join(REPO_ROOT, "docs", "core_import",
                        "POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["publication_decision"] == "STILL_BLOCKED_UNTIL_SECRET_ROTATED_EXTERNALLY"
    assert data["secret_rotation_required"] is True


def test_regression_deviation_review_max_severity_not_critical():
    path = os.path.join(REPO_ROOT, "docs", "core_import",
                        "POST_P80_HARDENING_DEVIATION_REVIEW.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["max_severity_found"] not in ("CRITICAL", "HIGH", "BLOCKER")
    assert data["security_regression_found"] is False


def test_regression_all_boundary_flags_false(report):
    for flag in BOUNDARY_FLAGS:
        assert report[flag] is False, f"REGRESSION: {flag} doit être False"
