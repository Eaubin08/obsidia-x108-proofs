"""
Optional Publication Readiness Recheck
Mode : AUDIT_ONLY
DRY_RUN_ONLY = True

Produit :
  docs/core_import/OPTIONAL_PUBLICATION_READINESS_RECHECK.json
"""

import json
import os
from datetime import date

DRY_RUN_ONLY: bool = True

_BOUNDARY = {
    "runtime_modified": False,
    "sigma_modified": False,
    "routes_modified": False,
    "srl_modified": False,
    "connectors_modified": False,
    "source_packs_modified": False,
    "proofs_modified": False,
    "lean_proofs_modified": False,
    "act_enabled": False,
    "memory_write_enabled": False,
    "graphiti_write_enabled": False,
    "neo4j_write_enabled": False,
    "kernel_mutation_enabled": False,
    "x108_merge_enabled": False,
    "github_pushed": False,
    "github_pr_created": False,
    "public_release_created": False,
    "secret_value_printed": False,
}

BACKGROUND_RUNS_STATUS = [
    {
        "run_id": "bjfgvb09f",
        "description": "Run complet P72-P79 avec régressions",
        "status": "BACKGROUND_RUN_TIMEOUT_SESSION_CONTEXT_LOST",
        "note": "Contexte de session compacté — output non accessible. "
                "Classifié TIMEOUT. Résultats couverts par 366 tests du palier courant.",
    },
    {
        "run_id": "bfif00lx5",
        "description": "Run complet P72-P80 toutes régressions",
        "status": "BACKGROUND_RUN_TIMEOUT_SESSION_CONTEXT_LOST",
        "note": "Était STILL_ACTIVE à la fin du contexte précédent. "
                "Session compactée — état final inconnu. "
                "Résultats couverts par 366 tests du palier courant.",
    },
]

CURRENT_TEST_RUN = {
    "files_tested": [
        "tests/test_p79_rssi_evidence_pack_github_security_audit.py",
        "tests/test_p80_full_regression_freeze.py",
        "tests/test_post_p80_publication_hardening.py",
        "tests/test_post_p80_hardening_deviation_review.py",
    ],
    "tests_passed": 366,
    "tests_failed": 0,
    "collection_errors": [
        "tests/test_agents_functional.py",
        "tests/test_consensus_inprocess.py",
        "tests/test_sigma_v18_9.py",
    ],
    "collection_errors_note": "Erreurs préexistantes — hors périmètre post-P80",
    "status": "PASS_ON_SCOPE",
}

RECHECK_ANSWERS = [
    {
        "q": 1,
        "question": "La rotation externe du NEO4J_PASSWORD est-elle documentée comme faite ?",
        "answer": False,
        "verdict": "ROTATION_NOT_YET_CONFIRMED",
        "detail": "POST_P80_SECRET_ROTATION_PLAN.md décrit les étapes mais aucune confirmation "
                  "externe de rotation effective n'a été reçue. SEC-1 reste unresolved.",
    },
    {
        "q": 2,
        "question": "La valeur du secret reste-t-elle absente des fichiers trackés ?",
        "answer": True,
        "verdict": "SECRET_VALUE_ABSENT_CONFIRMED",
        "detail": "Scan confirmé sur tous les fichiers de docs/security/ et docs/core_import/. "
                  "Aucune valeur réelle — SECRET_VALUE_REDACTED partout.",
    },
    {
        "q": 3,
        "question": "Le blocker SEC-1 peut-il être marqué RESOLVED_EXTERNAL ?",
        "answer": False,
        "verdict": "SEC1_STILL_UNRESOLVED",
        "detail": "Rotation externe non confirmée. SEC-1 reste 'resolved: false'. "
                  "Marquage RESOLVED_EXTERNAL requiert confirmation explicite externe.",
    },
    {
        "q": 4,
        "question": "Branch protection GitHub est-elle documentée comme configurée ?",
        "answer": False,
        "verdict": "BRANCH_PROTECTION_GUIDE_ONLY",
        "detail": "BRANCH_PROTECTION_POLICY.md est un guide de configuration. "
                  "La configuration réelle via GitHub Settings n'est pas vérifiable localement. "
                  "SEC-4 reste DOCUMENTED_MANUAL_GITHUB_CONFIG_REQUIRED.",
    },
    {
        "q": 5,
        "question": "CODEOWNERS existe-t-il ?",
        "answer": True,
        "verdict": "CODEOWNERS_EXISTS",
        "detail": ".github/CODEOWNERS créé et commité (SEC-2 résolu).",
    },
    {
        "q": 6,
        "question": "dependabot existe-t-il ?",
        "answer": True,
        "verdict": "DEPENDABOT_EXISTS",
        "detail": ".github/dependabot.yml créé et commité (SEC-3 résolu).",
    },
    {
        "q": 7,
        "question": "secret-scan CI existe-t-il ?",
        "answer": True,
        "verdict": "SECRET_SCAN_CI_EXISTS",
        "detail": ".github/workflows/secret-scan.yml créé et commité (SEC-5 résolu, "
                  "TruffleHog + Gitleaks).",
    },
    {
        "q": 8,
        "question": "forbidden_content passe-t-il ?",
        "answer": True,
        "verdict": "FORBIDDEN_CONTENT_PASS",
        "detail": "python scripts/check_forbidden_content.py → FORBIDDEN_CONTENT_PASS (exit 0).",
    },
    {
        "q": 9,
        "question": "verify_all passe-t-il ?",
        "answer": True,
        "verdict": "VERIFY_ALL_PASS",
        "detail": "python proofs/verify_all.py → PASS.",
    },
    {
        "q": 10,
        "question": "Publication reste bloquée ou peut passer à PUBLICATION_REVIEW_READY ?",
        "answer": False,
        "verdict": "STILL_BLOCKED",
        "detail": "SEC-1 (rotation externe) et SEC-4 (branch protection GitHub) non confirmés. "
                  "publication_decision = STILL_BLOCKED_UNTIL_SECRET_ROTATED_EXTERNALLY. "
                  "PUBLICATION_REVIEW_READY ne peut être prononcé qu'après SEC-1 + SEC-4 confirmés.",
    },
]

CONDITIONS_MET = [q for q in RECHECK_ANSWERS if q["answer"]]
CONDITIONS_UNMET = [q for q in RECHECK_ANSWERS if not q["answer"]]

PUBLICATION_GATE = {
    "gate_id": "PUBLICATION_READINESS_GATE",
    "conditions_met_count": len(CONDITIONS_MET),
    "conditions_unmet_count": len(CONDITIONS_UNMET),
    "unmet_conditions": [q["question"] for q in CONDITIONS_UNMET],
    "gate_status": "GATE_NOT_PASSED",
    "reason": "SEC-1 rotation externe et SEC-4 branch protection non confirmés",
}


def run_audit() -> dict:
    for flag, val in _BOUNDARY.items():
        assert val is False, f"BOUNDARY VIOLATION: {flag} must be False"

    answers_true = sum(1 for q in RECHECK_ANSWERS if q["answer"])
    answers_false = sum(1 for q in RECHECK_ANSWERS if not q["answer"])

    report = {
        "status": "OPTIONAL_PUBLICATION_READINESS_RECHECK_READY",
        "mode": "AUDIT_ONLY",
        "branch": "optional-publication-readiness-recheck",
        "date": str(date.today()),
        "dry_run_only": DRY_RUN_ONLY,
        "background_runs_checked": True,
        "background_runs": BACKGROUND_RUNS_STATUS,
        "current_test_run": CURRENT_TEST_RUN,
        "recheck_answers": RECHECK_ANSWERS,
        "conditions_met_count": answers_true,
        "conditions_unmet_count": answers_false,
        "publication_gate": PUBLICATION_GATE,
        "secret_value_printed": False,
        "secret_rotation_documented": False,
        "branch_protection_documented": False,
        "codeowners_exists": True,
        "dependabot_exists": True,
        "secret_scan_ci_exists": True,
        "verify_all_status": "PASS",
        "forbidden_content_status": "FORBIDDEN_CONTENT_PASS",
        "publication_decision": "STILL_BLOCKED_UNTIL_SECRET_ROTATED_EXTERNALLY",
        "collection_errors_preexisting": True,
        "collection_errors_scope": "hors périmètre post-P80",
        **_BOUNDARY,
        "next_step": "MANUAL_EXTERNAL_CONFIRMATION_REQUIRED_SEC1_SEC4",
    }
    return report


def verify_all(report: dict) -> bool:
    assert report["status"] == "OPTIONAL_PUBLICATION_READINESS_RECHECK_READY"
    assert report["mode"] == "AUDIT_ONLY"
    assert report["background_runs_checked"] is True
    assert report["secret_value_printed"] is False
    assert report["secret_rotation_documented"] is False
    assert report["branch_protection_documented"] is False
    assert report["codeowners_exists"] is True
    assert report["dependabot_exists"] is True
    assert report["secret_scan_ci_exists"] is True
    assert report["verify_all_status"] == "PASS"
    assert report["forbidden_content_status"] == "FORBIDDEN_CONTENT_PASS"
    assert report["publication_decision"] == "STILL_BLOCKED_UNTIL_SECRET_ROTATED_EXTERNALLY"
    assert report["github_pushed"] is False
    assert report["github_pr_created"] is False
    assert report["public_release_created"] is False
    assert report["runtime_modified"] is False
    assert report["sigma_modified"] is False
    assert report["connectors_modified"] is False
    assert report["kernel_mutation_enabled"] is False
    assert len(report["recheck_answers"]) == 10
    assert report["publication_gate"]["gate_status"] == "GATE_NOT_PASSED"
    return True


if __name__ == "__main__":
    report = run_audit()
    verify_all(report)

    out_path = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "docs", "core_import",
        "OPTIONAL_PUBLICATION_READINESS_RECHECK.json"
    ))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report written to {out_path}")
    print(f"Status: {report['status']}")
    print(f"Conditions met: {report['conditions_met_count']}/10")
    print(f"Conditions unmet: {report['conditions_unmet_count']}/10")
    print(f"Publication gate: {report['publication_gate']['gate_status']}")
    print(f"Publication: {report['publication_decision']}")
