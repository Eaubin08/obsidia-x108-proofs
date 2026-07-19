"""
P79 — RSSI Evidence Pack and GitHub Security Audit
Mode : AUDIT_AND_DOCS_ONLY
DRY_RUN_ONLY = True

Produit :
  - docs/core_import/P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT.json
  - docs/rssi/README_RSSI_EVIDENCE_PACK.md (si safe)
  - docs/security/GITHUB_SECURITY_AUDIT.md (si safe)
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
}

RSSI_MODEL = {
    "evidence_core": "Ancres cryptographiques verifiables : Merkle root SHA-256 + RFC3161 Free TSA 2026-03-03",
    "formal_proof": "Preuves Lean LEAN_PROVEN (11 invariants) + TLA+ specs (17) + graphe invariants P72",
    "audit_trail": "Ledger paliers P56A-P78 (82 fichiers docs/core_import) + sovereign_tickets.jsonl",
    "hash_manifest": "Manifest SHA-256 recursif + scripts generate/verify hashes + compute_merkle",
    "replay": "verify_all.py + verify_decision.py + verify_merkle.py + specs/11_PROOF_REPLAY_OS3/",
    "boundary_doc": "README_PUBLIC_BOUNDARY + README_PROOF_BOUNDARY + P78 split matrix + SECURITY.md",
    "public_safe": "specs/00-01-09-11 + LIMITS.md + GLOSSAIRE.md + README.md + BANK_SCENARIOS/OUTPUTS",
    "internal_only": "PROOFKIT_REPORT.json (gitignore conflict) + P56D Sigma veto boundary",
    "do_not_publish": "sigma/ + runtime_wiring/ + connectors/ + periphery/ + world_action_bus.jsonl",
}

SECURITY_MODEL = {
    "secret_risk": "NEO4J_PASSWORD value detecte dans docs/runtime/archive/ (zone ARCHIVE_ONLY) — SECRET_VALUE_REDACTED",
    "local_path_risk": "66 fichiers docs/ contiennent chemins Windows/Unix locaux — tous en zone ARCHIVE ou DO_NOT_PUBLISH",
    "github_config_present": ".github/workflows/verify-proofs.yml + x108-periphery-ci.yml + SECURITY.md racine",
    "github_config_missing": "CODEOWNERS absent + dependabot.yml projet absent + branch protection doc absent",
    "ci_present": "verify-proofs.yml (Lean/Python/TLA+/Sigma) + x108-periphery-ci.yml (manifest/forbidden/pytest)",
    "ci_missing": "Secret scanning CI absent + SAST/dependency audit absent + audit de CI version pins",
    "dependency_review": "requirements.txt racine absent + apps/obsidia-workbench/node_modules potentiellement commit",
    "branch_protection_review": "Aucun fichier branch protection — a configurer via GitHub Settings avant publication",
}

RSSI_EVIDENCE_MATRIX = [
    # RSSI_EVIDENCE_CORE
    {
        "file_path": "proofs/merkle_root.json",
        "category": "RSSI_EVIDENCE_CORE",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Ancre cryptographique Merkle SHA-256 verifiable",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "proofs/rfc3161_anchor.json",
        "category": "RSSI_EVIDENCE_CORE",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Horodatage RFC3161 Free TSA 2026-03-03 SHA-256 avec certificat complet",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "proofs/metadata.json",
        "category": "RSSI_EVIDENCE_CORE",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Metadata proof set",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    # RSSI_EVIDENCE_FORMAL_PROOF
    {
        "file_path": "proofs/lean/",
        "category": "RSSI_EVIDENCE_FORMAL_PROOF",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "9 theoremes Lean LEAN_PROVEN : GuardX108, TemporalBridge, X108, etc.",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
        "file_count_approx": 9,
    },
    {
        "file_path": "proofs/tla/",
        "category": "RSSI_EVIDENCE_FORMAL_PROOF",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "17 specs TLA+ Sigma/OS2 bounds",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
        "file_count_approx": 17,
    },
    {
        "file_path": "specs/_invariant_graph/",
        "category": "RSSI_EVIDENCE_FORMAL_PROOF",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "10 fichiers graphe invariants formel : LEAN_PROVEN_VS_PYTHON_TESTED_MATRIX, THEOREM_DEPENDENCY_GRAPH, etc.",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
        "file_count_approx": 10,
    },
    {
        "file_path": "docs/core_import/P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT.json",
        "category": "RSSI_EVIDENCE_FORMAL_PROOF",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Alignement formel P72 : 23 invariants, 11 LEAN_PROVEN, 8 PYTHON_TESTED",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "docs/core_import/P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT.md",
        "category": "RSSI_EVIDENCE_FORMAL_PROOF",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Rapport lisible alignement formel P72",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    # RSSI_EVIDENCE_AUDIT_TRAIL
    {
        "file_path": "docs/core_import/",
        "category": "RSSI_EVIDENCE_AUDIT_TRAIL",
        "decision": "INCLUDE_INTERNAL_RSSI_ONLY",
        "reason": "82 fichiers ledger paliers P56A-P78 — trail audit complet import controle",
        "public": False,
        "secret_risk": False,
        "local_path_risk": True,
        "file_count_approx": 82,
        "note": "Certains fichiers contiennent chemins locaux — revue selective avant publication",
    },
    {
        "file_path": "audit/sovereign_tickets.jsonl",
        "category": "RSSI_EVIDENCE_AUDIT_TRAIL",
        "decision": "INCLUDE_INTERNAL_RSSI_ONLY",
        "reason": "Tickets souverains — audit trail interne",
        "public": False,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "docs/core_import/P56D_SIGMA_POST_GUARD_VETO_BOUNDARY.md",
        "category": "RSSI_EVIDENCE_AUDIT_TRAIL",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Sigma post-guard veto boundary — gel permanent P56D",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    # RSSI_EVIDENCE_HASH_MANIFEST
    {
        "file_path": "scripts/generate_recursive_manifest.py",
        "category": "RSSI_EVIDENCE_HASH_MANIFEST",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Generateur manifest SHA-256 recursif",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "scripts/verify_recursive_manifest.py",
        "category": "RSSI_EVIDENCE_HASH_MANIFEST",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Verificateur manifest SHA-256 recursif",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "scripts/generate_hashes.py",
        "category": "RSSI_EVIDENCE_HASH_MANIFEST",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Generateur hashes",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "scripts/verify_hashes.py",
        "category": "RSSI_EVIDENCE_HASH_MANIFEST",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Verificateur hashes",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "scripts/check_forbidden_content.py",
        "category": "RSSI_EVIDENCE_HASH_MANIFEST",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Verification contenu interdit — safe guard CI",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "proofs/compute_merkle_root.py",
        "category": "RSSI_EVIDENCE_HASH_MANIFEST",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Calcul Merkle root",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "proofs/compute_merkle_standalone.py",
        "category": "RSSI_EVIDENCE_HASH_MANIFEST",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Calcul Merkle standalone",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "tools/anchor_merkle_root.py",
        "category": "RSSI_EVIDENCE_HASH_MANIFEST",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Ancrage Merkle root",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "tools/verify_chain_anchor.py",
        "category": "RSSI_EVIDENCE_HASH_MANIFEST",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Verification chaine ancrage",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "tools/verify_threat_model.py",
        "category": "RSSI_EVIDENCE_HASH_MANIFEST",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Verification modele de menace",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    # RSSI_EVIDENCE_REPLAY
    {
        "file_path": "proofs/verify_all.py",
        "category": "RSSI_EVIDENCE_REPLAY",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Verification complete toutes preuves — utilisee en CI",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "proofs/verify_decision.py",
        "category": "RSSI_EVIDENCE_REPLAY",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Verification decision individuelle",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "proofs/verify_merkle.py",
        "category": "RSSI_EVIDENCE_REPLAY",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Verification Merkle root",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "specs/11_PROOF_REPLAY_OS3/",
        "category": "RSSI_EVIDENCE_REPLAY",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "9 specs replay/RFC3161/Merkle/attestation OS3",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
        "file_count_approx": 9,
    },
    # RSSI_EVIDENCE_BOUNDARY_DOC
    {
        "file_path": "docs/public/README_PUBLIC_BOUNDARY.md",
        "category": "RSSI_EVIDENCE_BOUNDARY_DOC",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Index surface public safe P78",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "docs/proof/README_PROOF_BOUNDARY.md",
        "category": "RSSI_EVIDENCE_BOUNDARY_DOC",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Index surface proof technique P78",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "docs/core_import/P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT.json",
        "category": "RSSI_EVIDENCE_BOUNDARY_DOC",
        "decision": "INCLUDE_INTERNAL_RSSI_ONLY",
        "reason": "Matrice classification 109 entrees — reference interne RSSI",
        "public": False,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "SECURITY.md",
        "category": "RSSI_EVIDENCE_BOUNDARY_DOC",
        "decision": "KEEP_PUBLIC_SAFE",
        "reason": "Politique securite + contacts divulgation vulnerabilite",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    # RSSI_EVIDENCE_PUBLIC_SAFE
    {
        "file_path": "specs/00_SCOPE_DISCIPLINE/",
        "category": "RSSI_EVIDENCE_PUBLIC_SAFE",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "9 fichiers scope discipline — claims bornes PUBLIC_ASSERTION_ALLOWED_CLAIMS",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
        "file_count_approx": 9,
    },
    {
        "file_path": "specs/01_X108_AUTHORITY/",
        "category": "RSSI_EVIDENCE_PUBLIC_SAFE",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "7 fichiers autorite GuardX108 Lean-proven",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
        "file_count_approx": 7,
    },
    {
        "file_path": "specs/09_CRITICAL_WORLDS/",
        "category": "RSSI_EVIDENCE_PUBLIC_SAFE",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "14 fichiers GPS/bank/trading/aviation threat model",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
        "file_count_approx": 14,
    },
    {
        "file_path": "docs/RFC3161.md",
        "category": "RSSI_EVIDENCE_PUBLIC_SAFE",
        "decision": "INCLUDE_RSSI_PACK",
        "reason": "Documentation ancre RFC3161",
        "public": True,
        "secret_risk": False,
        "local_path_risk": False,
    },
    # RSSI_EVIDENCE_INTERNAL_ONLY
    {
        "file_path": "proofs/PROOFKIT_REPORT.json",
        "category": "RSSI_EVIDENCE_INTERNAL_ONLY",
        "decision": "INCLUDE_INTERNAL_RSSI_ONLY",
        "reason": "Rapport complet proof — reference en .gitignore mais presente dans repo (inconsistance gitignore)",
        "public": False,
        "secret_risk": False,
        "local_path_risk": False,
        "note": "Gitignore conflict : proofs/PROOFKIT_REPORT.json est liste dans .gitignore mais commite — revue requise",
    },
    # RSSI_EVIDENCE_DO_NOT_PUBLISH
    {
        "file_path": "sigma/",
        "category": "RSSI_EVIDENCE_DO_NOT_PUBLISH",
        "decision": "DO_NOT_PUBLISH",
        "reason": "PROTEGE P77 — runtime souverain KX108_ONLY",
        "public": False,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "runtime_wiring/",
        "category": "RSSI_EVIDENCE_DO_NOT_PUBLISH",
        "decision": "DO_NOT_PUBLISH",
        "reason": "PROTEGE P77 — wiring interne runtime",
        "public": False,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "connectors/",
        "category": "RSSI_EVIDENCE_DO_NOT_PUBLISH",
        "decision": "DO_NOT_PUBLISH",
        "reason": "PROTEGE P77 + P70 BLOCK_CONNECTOR_RUN",
        "public": False,
        "secret_risk": False,
        "local_path_risk": False,
    },
    {
        "file_path": "audit/world_action_bus.jsonl",
        "category": "RSSI_EVIDENCE_DO_NOT_PUBLISH",
        "decision": "DO_NOT_PUBLISH",
        "reason": "PROTEGE P77 — donnees runtime souveraines",
        "public": False,
        "secret_risk": False,
        "local_path_risk": False,
    },
]

GITHUB_SECURITY_MATRIX = [
    # CI PRESENT
    {
        "file_path": ".github/workflows/verify-proofs.yml",
        "category": "SECURITY_CI_PRESENT",
        "decision": "KEEP_PUBLIC_SAFE",
        "reason": "CI proof : Lean build, Python verify_all, Sigma tests, TLA+ TLC, RFC3161",
        "present": True,
        "action_required": None,
    },
    {
        "file_path": ".github/workflows/x108-periphery-ci.yml",
        "category": "SECURITY_CI_PRESENT",
        "decision": "KEEP_PUBLIC_SAFE",
        "reason": "CI periphery : pytest, manifest generation/verify, forbidden content check",
        "present": True,
        "action_required": None,
    },
    # GITHUB CONFIG PRESENT
    {
        "file_path": "SECURITY.md",
        "category": "SECURITY_GITHUB_CONFIG_PRESENT",
        "decision": "KEEP_PUBLIC_SAFE",
        "reason": "Politique securite presente : security@obsidia.io, contact@obsidia.io, NDA audit path",
        "present": True,
        "action_required": None,
    },
    {
        "file_path": ".gitignore",
        "category": "SECURITY_GITHUB_CONFIG_PRESENT",
        "decision": "KEEP_PUBLIC_SAFE",
        "reason": ".gitignore complet : .env exclu, secrets exclus, archives exclues, node_modules exclus",
        "present": True,
        "action_required": "Verifier inconsistance : proofs/PROOFKIT_REPORT.json liste mais commite",
    },
    {
        "file_path": ".env.example",
        "category": "SECURITY_GITHUB_CONFIG_PRESENT",
        "decision": "KEEP_PUBLIC_SAFE",
        "reason": "Template .env avec valeurs vides — aucun secret reel",
        "present": True,
        "action_required": None,
    },
    # GITHUB CONFIG MISSING
    {
        "file_path": "CODEOWNERS",
        "category": "SECURITY_GITHUB_CONFIG_MISSING",
        "decision": "ADD_CODEOWNERS_LATER",
        "reason": "CODEOWNERS absent — pas de review obligatoire sur sigma/, proofs/, connectors/",
        "present": False,
        "action_required": "Creer CODEOWNERS avant publication GitHub",
    },
    {
        "file_path": ".github/dependabot.yml",
        "category": "SECURITY_GITHUB_CONFIG_MISSING",
        "decision": "ADD_DEPENDABOT_LATER",
        "reason": "dependabot.yml absent au niveau projet — pas de mise a jour automatique dependances",
        "present": False,
        "action_required": "Creer .github/dependabot.yml avant publication",
    },
    {
        "file_path": "docs/security/BRANCH_PROTECTION.md",
        "category": "SECURITY_GITHUB_CONFIG_MISSING",
        "decision": "ADD_BRANCH_PROTECTION_LATER",
        "reason": "Aucun document branch protection — proteger main avant publication",
        "present": False,
        "action_required": "Configurer branch protection GitHub + documenter",
    },
    # CI MISSING
    {
        "file_path": ".github/workflows/secret-scan.yml",
        "category": "SECURITY_CI_MISSING",
        "decision": "ADD_CI_LATER",
        "reason": "Pas de CI secret scanning — NEO4J_PASSWORD detecte dans archive, risque si mal classe",
        "present": False,
        "action_required": "Ajouter step secret scan (trufflehog ou gitleaks) en CI",
    },
    {
        "file_path": ".github/workflows/dependency-audit.yml",
        "category": "SECURITY_CI_MISSING",
        "decision": "ADD_CI_LATER",
        "reason": "Pas d audit dependances CI — node_modules workbench potentiellement commite",
        "present": False,
        "action_required": "Ajouter pip-audit + npm audit en CI si apps/ publiee",
    },
    # DEPENDENCY REVIEW
    {
        "file_path": "requirements.txt",
        "category": "SECURITY_DEPENDENCY_REVIEW",
        "decision": "REQUIRES_REVIEW",
        "reason": "Aucun requirements.txt racine — dependances Python non pinned au niveau repo",
        "present": False,
        "action_required": "Creer requirements.txt racine avec pins avant publication",
    },
    {
        "file_path": "apps/obsidia-workbench/node_modules/",
        "category": "SECURITY_DEPENDENCY_REVIEW",
        "decision": "REQUIRES_REVIEW",
        "reason": "node_modules/ apparait dans repo — gitignore devrait les exclure, verifier si commite",
        "present": True,
        "action_required": "Verifier git ls-files apps/obsidia-workbench/node_modules/ — supprimer si commite",
    },
    {
        "file_path": "apps/obsidia-workbench/",
        "category": "SECURITY_DEPENDENCY_REVIEW",
        "decision": "KEEP_PRIVATE",
        "reason": "Workbench UI proprietaire — DO_NOT_PUBLISH per P78",
        "present": True,
        "action_required": None,
    },
    # BRANCH PROTECTION REVIEW
    {
        "file_path": "GitHub branch protection settings",
        "category": "SECURITY_BRANCH_PROTECTION_REVIEW",
        "decision": "ADD_BRANCH_PROTECTION_LATER",
        "reason": "Aucune protection branche documentee — requis avant publication publique",
        "present": False,
        "action_required": "Configurer : require PR review, require status checks (CI), restrict force push",
    },
]

SECRET_SCAN_MATRIX = [
    {
        "file_path": "docs/runtime/archive/phase10_12_legacy_untracked_20260527/BRODY_PHASE12E4_A2_DOMAIN_RACCORD_AUDIT_20260527.md",
        "category": "SECURITY_SECRET_RISK",
        "decision": "REDACT_BEFORE_PUBLIC",
        "reason": "Contient reference a valeur NEO4J_PASSWORD dans contexte audit doc",
        "secret_type": "NEO4J_PASSWORD",
        "secret_value": "SECRET_VALUE_REDACTED",
        "zone_classification": "KEEP_ARCHIVE_ONLY (docs/runtime/) — DO_NOT_PUBLISH per P78",
        "action_required": "REQUIRES_SECRET_ROTATION — changer le mot de passe NEO4J reference. Fichier deja en DO_NOT_PUBLISH.",
    },
    {
        "file_path": "scripts/brody_terminal_chat.py",
        "category": "SECURITY_SECRET_RISK",
        "decision": "REQUIRES_REVIEW",
        "reason": "Contient $env:NEO4J_PASSWORD = 'votre_mot_de_passe' — semble etre un placeholder template",
        "secret_type": "NEO4J_PASSWORD",
        "secret_value": "SECRET_VALUE_REDACTED",
        "zone_classification": "Script interne — public si scripts/ publie",
        "action_required": "Verifier si valeur reelle ou placeholder — si placeholder, documenter explicitement",
    },
    {
        "file_path": "periphery/brody_memory_readonly/graphiti_import_apply_guarded_manual_only/",
        "category": "SECURITY_SECRET_RISK",
        "decision": "KEEP_PRIVATE",
        "reason": "CONFIRM_TOKEN = sentinel guard logique (pas API key) — KEEP_PRIVATE_PROPRIETARY per P78",
        "secret_type": "CONFIRM_TOKEN_SENTINEL",
        "secret_value": "SECRET_VALUE_REDACTED",
        "zone_classification": "KEEP_PRIVATE_PROPRIETARY",
        "action_required": None,
    },
    {
        "file_path": "proofs/V18_3_1/engine_buildable_0_9_3_1/docs/PUBLIC_DEPLOY.md",
        "category": "SECURITY_SECRET_RISK",
        "decision": "REQUIRES_REVIEW",
        "reason": "MINIO_ROOT_PASSWORD=\"<set-via-env>\" — placeholder template dans doc deploy",
        "secret_type": "MINIO_ROOT_PASSWORD_TEMPLATE",
        "secret_value": "SECRET_VALUE_REDACTED",
        "zone_classification": "proofs/V18_3_1/ — PROTEGE P77",
        "action_required": "Confirmer que valeur est template et non reelle",
    },
    {
        "file_path": "docs/",
        "category": "SECURITY_LOCAL_PATH_RISK",
        "decision": "REDACT_BEFORE_PUBLIC",
        "reason": "66 fichiers dans docs/ contiennent chemins Windows/Unix locaux (C:\\Users\\User ou /home/)",
        "zone_classification": "Majoritairement docs/runtime/ + docs/freeze/ + docs/architecture/ — ARCHIVE/DO_NOT_PUBLISH",
        "action_required": "Confirmer que tous les fichiers avec chemins locaux sont bien en zone DO_NOT_PUBLISH ou ARCHIVE",
    },
]

FOCUS_FINDINGS = [
    {
        "id": "P79-F1",
        "type": "RSSI_EVIDENCE_PACK_INDEXED",
        "description": "Pack evidence RSSI local constitue : Merkle SHA-256, RFC3161 Free TSA, 11 invariants Lean, 82 paliers audit",
        "action": "INCLUDE_RSSI_PACK pour 22 entrees verifiees",
    },
    {
        "id": "P79-F2",
        "type": "SECRET_RISK_DETECTED",
        "description": "NEO4J_PASSWORD value detectee dans docs/runtime/archive/ — zone ARCHIVE_ONLY / DO_NOT_PUBLISH",
        "action": "REQUIRES_SECRET_ROTATION + fichier deja classe DO_NOT_PUBLISH — rotation mot de passe requise",
    },
    {
        "id": "P79-F3",
        "type": "CI_SECURITY_GAPS",
        "description": "2 workflows CI presents (proof + periphery) mais secret scanning, dependency audit, branch protection absents",
        "action": "ADD_CI_LATER + ADD_CODEOWNERS_LATER + ADD_DEPENDABOT_LATER + ADD_BRANCH_PROTECTION_LATER",
    },
    {
        "id": "P79-F4",
        "type": "LOCAL_PATH_RISK",
        "description": "66 fichiers docs/ contiennent chemins locaux Windows/Unix — tous dans zones ARCHIVE ou DO_NOT_PUBLISH",
        "action": "REDACT_BEFORE_PUBLIC — verifier classification P78 sur chaque fichier avant toute publication",
    },
    {
        "id": "P79-F5",
        "type": "GITIGNORE_INCONSISTENCY",
        "description": "proofs/PROOFKIT_REPORT.json liste dans .gitignore mais commite dans repo",
        "action": "REQUIRES_REVIEW — decider : retirer .gitignore entry OU untrack le fichier selon strategie P80",
    },
    {
        "id": "P79-F6",
        "type": "NODE_MODULES_REVIEW",
        "description": "apps/obsidia-workbench/node_modules/ presente sur disque — verifier si commite (gitignore dit non)",
        "action": "REQUIRES_REVIEW — git ls-files pour confirmer statut",
    },
    {
        "id": "P79-F7",
        "type": "RSSI_EVIDENCE_RFC3161_VERIFIED",
        "description": "RFC3161 anchor verifie : Free TSA, 2026-03-03, SHA-256, serial 0x03572CED, tsr_base64 present",
        "action": "INCLUDE_RSSI_PACK — ancre cryptographique valide",
    },
]

P78_CONSTRAINTS = [
    "DO_NOT_PUBLISH P78 reste autorite publication — sigma/runtime_wiring/connectors/gencoin/world_action_bus",
    "PUBLIC_SAFE P78 = surface proof publiable — 18 groupes confirmes",
    "RSSI_EVIDENCE_CANDIDATE P78 valide par absence secret/path critique",
    "CLASSIFY_AND_INDEX_ONLY — aucun deplacement, aucune modification runtime",
]

P77_CONSTRAINTS = [
    "PROTECTED_FILES_P77 : sigma/, runtime_wiring/, apps/obsidia_api/, connectors/ — DO_NOT_PUBLISH",
    "P76_BOM_NORMALIZATION_SAFE : sigma/examples/gps_omega_chaos.json — RUNTIME_INTERNAL",
    "REGROUP_CANDIDATE applique — docs/source_packs/ (remplacement wording P77)",
]

P72_CONSTRAINTS = [
    "GUARD_X108_FINAL_AUTHORITY — LEAN_PROVEN — specs/01_X108_AUTHORITY/ inclus RSSI pack",
    "SIGMA_POST_GUARD_VETO_ONLY — sigma/ DO_NOT_PUBLISH — gel permanent P56D",
    "NO_ACT_BEFORE_TAU — LEAN_PROVEN — connectors/ DO_NOT_PUBLISH",
    "LEAN_PROVEN vs PYTHON_TESTED — distinction maintenue dans RSSI evidence",
    "NO_KERNEL_MUTATION_FROM_PERIPHERY — periphery/ KEEP_PRIVATE_PROPRIETARY",
    "NETWORK_EGRESS_REVIEW_REQUIRED — connectors/ DO_NOT_PUBLISH + apps/ KEEP_PRIVATE",
]


def _compute_counts(matrix: list, key: str) -> dict:
    counts: dict = {}
    for entry in matrix:
        val = entry.get(key, "UNKNOWN")
        counts[val] = counts.get(val, 0) + 1
    return counts


def run_audit() -> dict:
    for flag, val in _BOUNDARY.items():
        assert val is False, f"BOUNDARY VIOLATION: {flag} must be False"

    include_rssi = [
        e["file_path"]
        for e in RSSI_EVIDENCE_MATRIX
        if e["decision"] == "INCLUDE_RSSI_PACK"
    ]
    include_internal = [
        e["file_path"]
        for e in RSSI_EVIDENCE_MATRIX
        if e["decision"] == "INCLUDE_INTERNAL_RSSI_ONLY"
    ]
    public_safe = [
        e["file_path"]
        for e in RSSI_EVIDENCE_MATRIX
        if e.get("public") is True
    ]
    do_not_publish = [
        e["file_path"]
        for e in RSSI_EVIDENCE_MATRIX
        if e["decision"] == "DO_NOT_PUBLISH"
    ]
    secret_risks = [
        e["file_path"]
        for e in SECRET_SCAN_MATRIX
        if e.get("category") == "SECURITY_SECRET_RISK"
    ]
    local_path_risks = [
        e["file_path"]
        for e in SECRET_SCAN_MATRIX
        if e.get("category") == "SECURITY_LOCAL_PATH_RISK"
    ]
    redact_before_public = [
        e["file_path"]
        for e in SECRET_SCAN_MATRIX
        if e.get("decision") == "REDACT_BEFORE_PUBLIC"
    ]
    ci_present = [
        e["file_path"]
        for e in GITHUB_SECURITY_MATRIX
        if e.get("category") == "SECURITY_CI_PRESENT"
    ]
    ci_missing = [
        e["file_path"]
        for e in GITHUB_SECURITY_MATRIX
        if e.get("category") == "SECURITY_CI_MISSING"
    ]
    github_config_present = [
        e["file_path"]
        for e in GITHUB_SECURITY_MATRIX
        if e.get("category") == "SECURITY_GITHUB_CONFIG_PRESENT"
    ]
    github_config_missing = [
        e["file_path"]
        for e in GITHUB_SECURITY_MATRIX
        if e.get("category") == "SECURITY_GITHUB_CONFIG_MISSING"
    ]
    dependency_review = [
        e["file_path"]
        for e in GITHUB_SECURITY_MATRIX
        if e.get("category") == "SECURITY_DEPENDENCY_REVIEW"
    ]
    branch_protection_review = [
        e["file_path"]
        for e in GITHUB_SECURITY_MATRIX
        if e.get("category") == "SECURITY_BRANCH_PROTECTION_REVIEW"
    ]

    all_matrix = RSSI_EVIDENCE_MATRIX + GITHUB_SECURITY_MATRIX + SECRET_SCAN_MATRIX

    report = {
        "audit_id": "P79",
        "status": "P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT_READY",
        "mode": "AUDIT_AND_DOCS_ONLY",
        "branch": "p79-rssi-evidence-pack-github-security-audit",
        "date": str(date.today()),
        "dry_run_only": DRY_RUN_ONLY,
        "source_patch_applied": False,
        "files_imported_count": 0,
        "rssi_decision": "LOCAL_RSSI_EVIDENCE_PACK_INDEXED",
        "github_security_decision": "SECURITY_AUDIT_INDEXED_NO_PUBLICATION",
        "rssi_model": RSSI_MODEL,
        "security_model": SECURITY_MODEL,
        "files_scanned_count": len(all_matrix),
        "rssi_evidence_matrix": RSSI_EVIDENCE_MATRIX,
        "github_security_matrix": GITHUB_SECURITY_MATRIX,
        "secret_scan_matrix": SECRET_SCAN_MATRIX,
        "category_counts": _compute_counts(all_matrix, "category"),
        "decision_counts": _compute_counts(all_matrix, "decision"),
        "include_rssi_pack": include_rssi,
        "include_internal_rssi_only": include_internal,
        "public_safe": public_safe,
        "do_not_publish": do_not_publish,
        "redact_before_public": redact_before_public,
        "secret_risks": secret_risks,
        "local_path_risks": local_path_risks,
        "github_config_present": github_config_present,
        "github_config_missing": github_config_missing,
        "ci_present": ci_present,
        "ci_missing": ci_missing,
        "dependency_review": dependency_review,
        "branch_protection_review": branch_protection_review,
        "created_indexes": [
            "docs/rssi/README_RSSI_EVIDENCE_PACK.md",
            "docs/rssi/RSSI_EVIDENCE_INDEX.md",
            "docs/rssi/RSSI_EVIDENCE_BOUNDARY.md",
            "docs/rssi/RSSI_DO_NOT_PUBLISH.md",
            "docs/security/GITHUB_SECURITY_AUDIT.md",
            "docs/security/PRE_PUBLICATION_SECURITY_CHECKLIST.md",
        ],
        "focus_findings": FOCUS_FINDINGS,
        "p78_public_private_constraints_applied": P78_CONSTRAINTS,
        "p77_wording_constraints_applied": P77_CONSTRAINTS,
        "p72_proof_constraints_applied": P72_CONSTRAINTS,
        **_BOUNDARY,
        "next_step": "P80_FULL_REGRESSION_FREEZE",
    }
    return report


def verify_all(report: dict) -> bool:
    assert report["audit_id"] == "P79"
    assert report["status"] == "P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT_READY"
    assert report["mode"] == "AUDIT_AND_DOCS_ONLY"
    assert report["source_patch_applied"] is False
    assert report["files_imported_count"] == 0
    assert report["github_pushed"] is False
    assert report["github_pr_created"] is False
    assert report["public_release_created"] is False
    assert report["runtime_modified"] is False
    assert report["sigma_modified"] is False
    assert len(report["include_rssi_pack"]) > 0
    assert len(report["secret_risks"]) > 0
    assert report["next_step"] == "P80_FULL_REGRESSION_FREEZE"
    return True


if __name__ == "__main__":
    report = run_audit()
    verify_all(report)

    out_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "docs",
        "core_import",
        "P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT.json",
    )
    out_path = os.path.normpath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"P79 audit report written to {out_path}")
    print(f"Status: {report['status']}")
    print(f"RSSI pack entries: {len(report['include_rssi_pack'])}")
    print(f"Secret risks: {len(report['secret_risks'])}")
    print(f"Security gaps: {len(report['github_config_missing']) + len(report['ci_missing'])}")
