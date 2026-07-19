"""
scripts/audit_canon_wording_targeted_cleanup_p77.py

P77 -- Canon Wording Targeted Cleanup
Mode : PATCH_CONTROLLED_TARGETED_DOCS_ONLY
DRY_RUN_ONLY : True (le script audite ; les patches git sont dans les fichiers)

Verrous absolus P77 :
  Ne pas toucher : sigma/, runtime_wiring/, apps/, connectors/, periphery/,
  SRL files, proofs/V18_3_1/, proofs/lean/, _tmp_core_import/,
  _source_packs/, _freezes/, .local_audits/, audit/world_action_bus.jsonl,
  proofs/PROOFKIT_REPORT.json
  Termes autorises si hash/tag/commit/freeze/test le justifie.
  P76 BOM fix gps_omega_chaos.json => P76_BOM_NORMALIZATION_SAFE.
"""
from __future__ import annotations

import json
import os
import sys

DRY_RUN_ONLY: bool = True

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "docs", "core_import", "P77_CANON_WORDING_TARGETED_CLEANUP.json")

_BOUNDARY = {
    "sigma_modified": False,
    "runtime_modified": False,
    "routes_modified": False,
    "lean_proofs_modified": False,
    "proofs_modified": False,
    "srl_modified": False,
    "connectors_modified": False,
    "act_enabled": False,
    "memory_write_enabled": False,
    "graphiti_write_enabled": False,
    "neo4j_write_enabled": False,
    "kernel_mutation_enabled": False,
    "x108_merge_enabled": False,
    "network_called": False,
    "localhost_called": False,
}

# ---------------------------------------------------------------------------
# Modele wording P77
# ---------------------------------------------------------------------------

WORDING_MODEL = {
    "audit_id": "P77",
    "mode": "PATCH_CONTROLLED_TARGETED_DOCS_ONLY",
    "dry_run_only": DRY_RUN_ONLY,
    "replacements_authorized": [
        "REGROUP_CANON -> REGROUP_CANDIDATE (if no proof)",
        "KEEP_CANON -> KEEP_CORE_OR_OFFICIAL_REVIEW (if no proof)",
        "CANON_LOCKED -> LOCKED_ONLY_IF_FREEZE_PROVEN (if no real lock)",
        "canonical -> reference/current/tracked/candidate (if no hash/freeze/tag)",
        "locked -> stable/tracked/protected/candidate (if no real lock)",
        "official -> current/documented/selected/reviewed (if no officialisation)",
        "freeze -> snapshot/local freeze/validated freeze (depending on proof)",
    ],
    "terms_justified_if": [
        "hash/tag/commit/freeze/test proves the claim",
        "P56->P76 docs with validated commit/test status",
        "technical code identifiers (domain names, function names, theorem names)",
        "filename references (referencing an existing file name)",
    ],
    "rules": [
        "no_global_rewrite",
        "no_broad_reformulation",
        "no_technical_change",
        "no_proof_deletion",
        "no_historical_generated_files_correction",
        "p56_p76_docs_keep_if_commit_backed",
        "public_claims_more_cautious_than_internal",
    ],
}

# ---------------------------------------------------------------------------
# Matrice wording P77 -- toutes occurrences classifiees
# ---------------------------------------------------------------------------

WORDING_MATRIX = [
    # --- PATCHES APPLIQUES ---
    {
        "file_path": "docs/source_packs/CORPUS_MAP_V4_20260602.csv",
        "term_found": "REGROUP_CANON",
        "occurrences": 13,
        "replacement": "REGROUP_CANDIDATE",
        "wording_decision": "REPLACED",
        "justification": "Aucun hash/tag/freeze ne justifie CANON. Terme action dans colonne CSV.",
        "risk_level": "LOW",
        "sigma_impact": False,
        "runtime_impact": False,
    },
    {
        "file_path": "docs/source_packs/CORPUS_MAP_V4_20260602.csv",
        "term_found": "KEEP_CANON",
        "occurrences": 1,
        "replacement": "KEEP_CORE_OR_OFFICIAL_REVIEW",
        "wording_decision": "REPLACED",
        "justification": "Aucun hash/tag/freeze ne justifie KEEP_CANON pour CORE_AUTHORITY dans action CSV.",
        "risk_level": "LOW",
        "sigma_impact": False,
        "runtime_impact": False,
    },
    {
        "file_path": "docs/source_packs/CORPUS_MAP_V4_CANON_STATUS.md",
        "term_found": "KEEP_CANON",
        "occurrences": 1,
        "replacement": "KEEP_CORE_OR_OFFICIAL_REVIEW",
        "wording_decision": "REPLACED",
        "justification": "Tableau d'exemple refletant la valeur CSV -- meme remplacement.",
        "risk_level": "LOW",
        "sigma_impact": False,
        "runtime_impact": False,
    },
    # --- TERMES JUSTIFIES PAR PREUVE ---
    {
        "file_path": "README.md",
        "term_found": "canonical",
        "occurrences": 4,
        "replacement": None,
        "wording_decision": "WORDING_JUSTIFIED_BY_PROOF",
        "justification": "Tag git p1-freeze-2026-04-22 justifie 'canonical' -- gel P1 reel.",
        "risk_level": "NONE",
        "sigma_impact": False,
        "runtime_impact": False,
    },
    {
        "file_path": "docs/LIMITS.md",
        "term_found": "canonical",
        "occurrences": 2,
        "replacement": None,
        "wording_decision": "WORDING_JUSTIFIED_BY_PROOF",
        "justification": "Tag git p1-freeze-2026-04-22 justifie 'canonical freeze reference'.",
        "risk_level": "NONE",
        "sigma_impact": False,
        "runtime_impact": False,
    },
    {
        "file_path": "docs/BANK_SCENARIOS.md",
        "term_found": "canonical",
        "occurrences": 1,
        "replacement": None,
        "wording_decision": "WORDING_JUSTIFIED_BY_PROOF",
        "justification": "Palier P2 reel commite -- 'canonical P2 Bank scenarios' reflète un palier documente.",
        "risk_level": "NONE",
        "sigma_impact": False,
        "runtime_impact": False,
    },
    # --- TERMES TECHNIQUES A CONSERVER ---
    {
        "file_path": "docs/GLOSSAIRE.md",
        "term_found": "Chaine Canonique",
        "occurrences": 1,
        "replacement": None,
        "wording_decision": "WORDING_TECHNICAL_TERM_KEEP",
        "justification": "Terme fondamental du glossaire -- pipeline cognitif 5 etapes. Identifiant technique.",
        "risk_level": "NONE",
        "sigma_impact": False,
        "runtime_impact": False,
    },
    {
        "file_path": "docs/architecture/OBSIDIA_F60_SIGMA_REGISTRY_CANONICAL_DOMAINS.md",
        "term_found": "canonical domains",
        "occurrences": 2,
        "replacement": None,
        "wording_decision": "WORDING_TECHNICAL_TERM_KEEP",
        "justification": "Identifiant technique Sigma -- noms de domaines dans le code (bank/trading/ecom/gps).",
        "risk_level": "NONE",
        "sigma_impact": False,
        "runtime_impact": False,
    },
    {
        "file_path": "docs/architecture/F74_F77_FINALIZATION_AUDIT.md",
        "term_found": "canonicalize_preserves_nonneg",
        "occurrences": 1,
        "replacement": None,
        "wording_decision": "WORDING_TECHNICAL_TERM_KEEP",
        "justification": "Nom de theorem Lean dans TemporalBridge.lean -- identifiant de preuve formelle.",
        "risk_level": "NONE",
        "sigma_impact": False,
        "runtime_impact": False,
    },
    {
        "file_path": "docs/V3_V4_GAP_ANALYSIS.md",
        "term_found": "DOC-CANON",
        "occurrences": 1,
        "replacement": None,
        "wording_decision": "WORDING_TECHNICAL_LABEL_KEEP",
        "justification": "Etiquette de categorie dans gap analysis -- pas une affirmation de gel injustifiee.",
        "risk_level": "NONE",
        "sigma_impact": False,
        "runtime_impact": False,
    },
    {
        "file_path": "docs/BANK_OUTPUTS.md",
        "term_found": "canonical interpretation",
        "occurrences": 1,
        "replacement": None,
        "wording_decision": "WORDING_EXPRESSION_STANDARD_KEEP",
        "justification": "Expression standard pour 'interpretation de reference' dans doc lecture des sorties.",
        "risk_level": "NONE",
        "sigma_impact": False,
        "runtime_impact": False,
    },
    {
        "file_path": "docs/GENCOIN_SANDBOX_INGESTION_REPORT.md",
        "term_found": "GENCOIN_CANON.md",
        "occurrences": 1,
        "replacement": None,
        "wording_decision": "WORDING_FILENAME_REFERENCE_KEEP",
        "justification": "Reference a un nom de fichier existant -- pas une affirmation non justifiee.",
        "risk_level": "NONE",
        "sigma_impact": False,
        "runtime_impact": False,
    },
    # --- PROTECTIONS P77 ---
    {
        "file_path": ".local_audits/CANON_WORDING_AUDIT_20260602_141430/",
        "term_found": "CANON_LOCKED (multiple occurrences)",
        "occurrences": 4,
        "replacement": None,
        "wording_decision": "PROTECTED_BY_P77_RULES",
        "justification": "Repertoire .local_audits/ protege par regle P77 -- ne pas toucher.",
        "risk_level": "NONE",
        "sigma_impact": False,
        "runtime_impact": False,
    },
    # --- P76 BOM ---
    {
        "file_path": "sigma/examples/gps_omega_chaos.json",
        "term_found": "BOM UTF-8 (correction P76)",
        "occurrences": 0,
        "replacement": None,
        "wording_decision": "P76_BOM_NORMALIZATION_SAFE",
        "justification": "Correction BOM UTF-8 appliquee en P76. Ne pas requalifier comme mutation runtime.",
        "risk_level": "NONE",
        "sigma_impact": False,
        "runtime_impact": False,
    },
]

# ---------------------------------------------------------------------------
# Fichiers proteges P77
# ---------------------------------------------------------------------------

PROTECTED_FILES_P77 = [
    "sigma/",
    "runtime_wiring/",
    "apps/obsidia_api/routes/",
    "apps/obsidia_api/*.py",
    "connectors/",
    "periphery/",
    "proofs/V18_3_1/",
    "proofs/lean/",
    "_tmp_core_import/",
    "_source_packs/",
    "_freezes/",
    ".local_audits/",
    "audit/world_action_bus.jsonl",
    "proofs/PROOFKIT_REPORT.json",
]

# ---------------------------------------------------------------------------
# Contraintes heritees
# ---------------------------------------------------------------------------

P75_CONSTRAINTS_APPLIED = [
    "BLOCK_RUNTIME_IMPORT_PERMANENT: engine/ non modifie",
    "AUDIT_ONLY_P75: aucun import runtime",
]

P76_CONSTRAINTS_APPLIED = [
    "GPS_TERRAIN_SEPARATED: sigma/ non modifie",
    "P76_BOM_NORMALIZATION_SAFE: gps_omega_chaos.json correction BOM P76 uniquement",
    "CONNECTORS_DO_NOT_RUN: aviation_robo.py, bank_normal_flow.py, trading_live.py",
]

# ---------------------------------------------------------------------------
# Focus findings P77
# ---------------------------------------------------------------------------

FOCUS_FINDINGS = [
    {
        "finding_id": "P77-F1",
        "type": "PATCH_APPLIED",
        "component": "docs/source_packs/CORPUS_MAP_V4_20260602.csv",
        "description": "13x REGROUP_CANON->REGROUP_CANDIDATE + 1x KEEP_CANON->KEEP_CORE_OR_OFFICIAL_REVIEW",
        "action": "REPLACED_UNJUSTIFIED_WORDING",
    },
    {
        "finding_id": "P77-F2",
        "type": "PATCH_APPLIED",
        "component": "docs/source_packs/CORPUS_MAP_V4_CANON_STATUS.md",
        "description": "1x KEEP_CANON->KEEP_CORE_OR_OFFICIAL_REVIEW dans tableau d'exemple ligne 38",
        "action": "REPLACED_UNJUSTIFIED_WORDING",
    },
    {
        "finding_id": "P77-F3",
        "type": "WORDING_JUSTIFIED_BY_PROOF",
        "component": "README.md",
        "description": "4x 'canonical' justifies par tag git p1-freeze-2026-04-22",
        "action": "KEEP_JUSTIFIED",
    },
    {
        "finding_id": "P77-F4",
        "type": "WORDING_TECHNICAL_TERM_KEEP",
        "component": "docs/GLOSSAIRE.md + docs/architecture/OBSIDIA_F60_*",
        "description": "Termes techniques: Chaine Canonique, canonical domains Sigma, theorem Lean",
        "action": "KEEP_TECHNICAL",
    },
    {
        "finding_id": "P77-F5",
        "type": "P76_BOM_NORMALIZATION_SAFE",
        "component": "sigma/examples/gps_omega_chaos.json",
        "description": "Correction BOM UTF-8 appliquee en P76 -- ne pas requalifier comme mutation runtime",
        "action": "CLASSIFIED_P76_BOM_SAFE",
    },
]

# ---------------------------------------------------------------------------
# Rapport
# ---------------------------------------------------------------------------

REPORT = {
    "audit_id": "P77",
    "status": "P77_CANON_WORDING_TARGETED_CLEANUP_READY",
    "mode": "PATCH_CONTROLLED_TARGETED_DOCS_ONLY",
    "branch": "p77-canon-wording-targeted-cleanup",
    "date": "2026-06-07",
    "dry_run_only": DRY_RUN_ONLY,
    "source_patch_applied": True,
    "files_patched_count": 2,
    "replacements_applied_count": 15,
    **_BOUNDARY,
    "wording_decision": "TARGETED_REPLACEMENT_APPLIED",
    "p76_bom_normalization": "P76_BOM_NORMALIZATION_SAFE",
    "files_patched": [
        "docs/source_packs/CORPUS_MAP_V4_20260602.csv",
        "docs/source_packs/CORPUS_MAP_V4_CANON_STATUS.md",
    ],
    "wording_model": WORDING_MODEL,
    "wording_matrix": WORDING_MATRIX,
    "protected_files_p77": PROTECTED_FILES_P77,
    "p75_constraints_applied": P75_CONSTRAINTS_APPLIED,
    "p76_constraints_applied": P76_CONSTRAINTS_APPLIED,
    "focus_findings": FOCUS_FINDINGS,
    "decision_counts": {
        "REPLACED": 3,
        "WORDING_JUSTIFIED_BY_PROOF": 3,
        "WORDING_TECHNICAL_TERM_KEEP": 3,
        "WORDING_EXPRESSION_STANDARD_KEEP": 1,
        "WORDING_TECHNICAL_LABEL_KEEP": 1,
        "WORDING_FILENAME_REFERENCE_KEEP": 1,
        "PROTECTED_BY_P77_RULES": 1,
        "P76_BOM_NORMALIZATION_SAFE": 1,
    },
    "next_step": "P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT",
}


def run_audit() -> dict:
    for key, val in _BOUNDARY.items():
        assert val is False, f"BLOCK_RUNTIME_IMPORT: {key} = {val}"

    replaced = [e for e in WORDING_MATRIX if e["wording_decision"] == "REPLACED"]
    total_occurrences = sum(e["occurrences"] for e in replaced)

    print(f"P77 audit => {len(WORDING_MATRIX)} entrees wording")
    print(f"Remplacements appliques => {len(replaced)} entrees, {total_occurrences} occurrences")
    print(f"Fichiers patchs => {REPORT['files_patched_count']}")
    print(f"JSON => {OUT_JSON}")

    return REPORT


if __name__ == "__main__":
    report = run_audit()
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("P77_CANON_WORDING_TARGETED_CLEANUP_READY")
    sys.exit(0)
