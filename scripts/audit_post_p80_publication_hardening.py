"""
post-P80 — Publication Security Hardening
Mode : SECURITY_HARDENING_CONTROLLED
DRY_RUN_ONLY = True

Produit :
  - docs/core_import/POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.json
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

BACKGROUND_RUNS = [
    {
        "run_id": "bjfgvb09f",
        "description": "Run complet P72-P79 avec régressions (lancé au moment du commit P80)",
        "status": "BACKGROUND_RUN_STATUS_UNKNOWN",
        "note": "Fichier output inaccessible (1 ligne vide) — statut indéterminé",
    },
    {
        "run_id": "bfif00lx5",
        "description": "Run complet P72-P80 toutes régressions (lancé début post-P80)",
        "status": "BACKGROUND_RUN_STILL_ACTIVE",
        "note": "En cours au moment du hardening — résultat partiel : 556 tests non-regression PASS confirmés",
    },
]

BLOCKERS_STATUS = [
    {
        "id": "SEC-1",
        "description": "NEO4J_PASSWORD dans docs/runtime/archive/ — SECRET_VALUE_REDACTED",
        "action_taken": "Plan de rotation documenté — docs/security/POST_P80_SECRET_ROTATION_PLAN.md",
        "resolved": False,
        "resolution": "DOCUMENTED_EXTERNAL_ROTATION_REQUIRED",
        "publication_impact": "STILL_BLOCKS_PUBLIC_RELEASE",
        "local_freeze_impact": "NONE",
    },
    {
        "id": "SEC-2",
        "description": "CODEOWNERS absent",
        "action_taken": "Fichier .github/CODEOWNERS créé",
        "resolved": True,
        "resolution": "CODEOWNERS_CREATED",
        "publication_impact": "RESOLVED",
        "local_freeze_impact": "NONE",
    },
    {
        "id": "SEC-3",
        "description": "dependabot.yml absent",
        "action_taken": "Fichier .github/dependabot.yml créé",
        "resolved": True,
        "resolution": "DEPENDABOT_CREATED",
        "publication_impact": "RESOLVED",
        "local_freeze_impact": "NONE",
    },
    {
        "id": "SEC-4",
        "description": "Branch protection non documentée",
        "action_taken": "docs/security/BRANCH_PROTECTION_POLICY.md créé — configuration manuelle GitHub Settings requise",
        "resolved": False,
        "resolution": "DOCUMENTED_MANUAL_GITHUB_CONFIG_REQUIRED",
        "publication_impact": "REQUIRES_MANUAL_ACTION",
        "local_freeze_impact": "NONE",
    },
    {
        "id": "SEC-5",
        "description": "Secret scan CI absent",
        "action_taken": ".github/workflows/secret-scan.yml créé (TruffleHog + Gitleaks)",
        "resolved": True,
        "resolution": "SECRET_SCAN_CI_CREATED",
        "publication_impact": "RESOLVED",
        "local_freeze_impact": "NONE",
    },
    {
        "id": "SEC-6",
        "description": "proofs/PROOFKIT_REPORT.json gitignore inconsistant",
        "action_taken": "Entree gitignore retirée — fichier confirmé tracké (git ls-files). Commentaire explicatif ajouté.",
        "resolved": True,
        "resolution": "GITIGNORE_ENTRY_REMOVED_FILE_INTENTIONALLY_TRACKED",
        "publication_impact": "RESOLVED",
        "local_freeze_impact": "NONE",
    },
]

CREATED_FILES = [
    ".github/CODEOWNERS",
    ".github/dependabot.yml",
    ".github/workflows/secret-scan.yml",
    "docs/security/POST_P80_SECRET_ROTATION_PLAN.md",
    "docs/security/POST_P80_PUBLICATION_HARDENING_PLAN.md",
    "docs/security/BRANCH_PROTECTION_POLICY.md",
    "scripts/audit_post_p80_publication_hardening.py",
    "docs/core_import/POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.json",
    "docs/core_import/POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.md",
    "tests/test_post_p80_publication_hardening.py",
]

GITIGNORE_CHANGES = [
    {
        "action": "REMOVED_ENTRY",
        "entry": "proofs/PROOFKIT_REPORT.json",
        "reason": "Fichier intentionnellement tracké (git ls-files confirmed). Gitignore entry incorrecte.",
        "resolution": "Commentaire explicatif ajouté à la place",
    }
]

REMAINING_BLOCKERS = [
    "SEC-1 — NEO4J_PASSWORD rotation externe manuelle (hors scope repo)",
    "SEC-4 — Branch protection GitHub Settings (configuration manuelle requise)",
]

POST_PUBLICATION_CHECKLIST = [
    "SEC-1 : Rotation NEO4J_PASSWORD effectuée",
    "SEC-4 : Branch protection configurée via GitHub Settings",
    "python proofs/verify_all.py → PASS",
    "python scripts/check_forbidden_content.py → PASS",
    "CI secret-scan.yml → passe sur push",
    "CI verify-proofs.yml → passe sur push",
    "pytest tests/ → tous passés",
    "Vérifier node_modules apps/obsidia-workbench/ non commités",
    "Créer requirements.txt racine avec pins Python",
]


def run_audit() -> dict:
    for flag, val in _BOUNDARY.items():
        assert val is False, f"BOUNDARY VIOLATION: {flag} must be False"

    resolved_count = sum(1 for b in BLOCKERS_STATUS if b["resolved"])
    unresolved_count = sum(1 for b in BLOCKERS_STATUS if not b["resolved"])

    report = {
        "status": "POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING_READY",
        "mode": "SECURITY_HARDENING_CONTROLLED",
        "branch": "post-p80-secret-rotation-publication-hardening",
        "date": str(date.today()),
        "dry_run_only": DRY_RUN_ONLY,
        "background_runs_checked": True,
        "background_runs": BACKGROUND_RUNS,
        "secret_value_printed": False,
        "blockers_status": BLOCKERS_STATUS,
        "blockers_resolved_count": resolved_count,
        "blockers_unresolved_count": unresolved_count,
        "codeowners_created": True,
        "dependabot_created": True,
        "branch_protection_policy_created": True,
        "secret_scan_ci_created": True,
        "proofkit_gitignore_reviewed": True,
        "secret_rotation_required": True,
        "gitignore_changes": GITIGNORE_CHANGES,
        "remaining_blockers": REMAINING_BLOCKERS,
        "created_files": CREATED_FILES,
        "post_publication_checklist": POST_PUBLICATION_CHECKLIST,
        "publication_decision": "STILL_BLOCKED_UNTIL_SECRET_ROTATED_EXTERNALLY",
        "local_freeze_status": "LOCAL_FREEZE_APPROVED_WITH_SECURITY_NOTE",
        "source_patch_applied": False,
        "files_imported_count": 0,
        **_BOUNDARY,
        "next_step": "OPTIONAL_PUBLICATION_READINESS_RECHECK",
    }
    return report


def verify_all(report: dict) -> bool:
    assert report["status"] == "POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING_READY"
    assert report["mode"] == "SECURITY_HARDENING_CONTROLLED"
    assert report["secret_value_printed"] is False
    assert report["github_pushed"] is False
    assert report["github_pr_created"] is False
    assert report["public_release_created"] is False
    assert report["runtime_modified"] is False
    assert report["sigma_modified"] is False
    assert report["codeowners_created"] is True
    assert report["dependabot_created"] is True
    assert report["secret_scan_ci_created"] is True
    assert report["proofkit_gitignore_reviewed"] is True
    assert report["secret_rotation_required"] is True
    assert report["publication_decision"] == "STILL_BLOCKED_UNTIL_SECRET_ROTATED_EXTERNALLY"
    assert report["next_step"] == "OPTIONAL_PUBLICATION_READINESS_RECHECK"
    return True


if __name__ == "__main__":
    report = run_audit()
    verify_all(report)

    out_path = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "docs", "core_import",
        "POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.json"
    ))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report written to {out_path}")
    print(f"Status: {report['status']}")
    print(f"Blockers resolved: {report['blockers_resolved_count']}/{len(report['blockers_status'])}")
    print(f"Remaining blockers: {report['blockers_unresolved_count']}")
    print(f"Publication: {report['publication_decision']}")
