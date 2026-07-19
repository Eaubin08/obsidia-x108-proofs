"""
scripts/audit_presentation_proof_public_private_split_p78.py

P78 -- Presentation Proof Public Private Split
Mode : AUDIT_AND_DOC_INDEX_ONLY
DRY_RUN_ONLY : True (aucun deplacement, aucune suppression)

Verrous absolus P78 :
  Ne pas toucher : sigma/, runtime_wiring/, apps/obsidia_api/routes/,
  apps/obsidia_api/*.py, connectors/, periphery/, proofs/V18_3_1/,
  proofs/lean/, _tmp_core_import/, _source_packs/, _freezes/,
  .local_audits/, audit/world_action_bus.jsonl, proofs/PROOFKIT_REPORT.json

Principe :
  Support presentation != preuve technique.
  Public proof != moteur proprietaire complet.
  Source pack local != canon public.
  Narratif investisseur != audit RSSI.
  Demo != runtime souverain.
  Archive != runtime load.
"""
from __future__ import annotations

import json
import os
import sys

DRY_RUN_ONLY: bool = True

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "docs", "core_import", "P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT.json")

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
}

# ---------------------------------------------------------------------------
# Modele split P78
# ---------------------------------------------------------------------------

SPLIT_MODEL = {
    "audit_id": "P78",
    "mode": "AUDIT_AND_DOC_INDEX_ONLY",
    "dry_run_only": DRY_RUN_ONLY,
    "technical_proof": "Preuves liees a tests, commits, manifests, hashes -- Lean/TLA/Merkle/RFC3161",
    "audit_trail": "Ledger paliers import controle P56->P77 + architecture audits F68-F77",
    "formal_proof_map": "Graphe invariants, specs constitutionnelles, entropy discipline",
    "rssi_evidence_candidate": "Candidates pack evidence RSSI : RFC3161, Merkle, P72, specs 00/01/09/11",
    "public_safe": "Docs safe publication : README, LIMITS, GLOSSAIRE, BANK_SCENARIOS, SIGMA, specs INDEX",
    "public_needs_softening": "Docs norme public apres relecture claims (F41 pitch, docs demo narratifs)",
    "investor_narrative": "Narratifs investisseur -- separes du proof technique",
    "demo_only": "Scripts demo, runbooks, phases F40-F60 demo reports",
    "private_proprietary": "Proprietaire : periphery 132 modules, AGI Tree34, BUV, Narrative Provenance, OS Trad IR",
    "source_pack_local_only": "Source packs locaux non canonises -- _source_packs/, _tmp_core_import/, specs/_source_index/",
    "archive_only": "Archives : _freezes/, .local_audits/, docs/freeze/, docs/runtime/, docs/real_engine/",
    "do_not_publish": "PROTEGE : sigma/, runtime_wiring/, connectors/, Gencoin specs, world_action_bus.jsonl",
}

# ---------------------------------------------------------------------------
# Matrice classification P78
# ---------------------------------------------------------------------------

DOC_MATRIX = [
    # ---- ROOT PUBLICS ----
    {
        "file_path": "README.md",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Freeze P1 tag, limites clairement enoncees, canonical justifie",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/LIMITS.md",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Limites P1 -- claims publics bornes, tag p1-freeze-2026-04-22",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/GLOSSAIRE.md",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Glossaire technique -- Chaine Canonique, termes fondamentaux",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/KERNEL_OVERVIEW.md",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Vue d'ensemble kernel -- public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/SIGMA.md",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Vue Sigma dispatcher -- public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/PROOF_SCOPE.md",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Perimetre proof P1 -- public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/REPO_MAP.md",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Carte repo -- public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/REPO_BOUNDARY.md",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Boundary repo -- public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/AUDIT_GUIDE.md",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Guide audit -- public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/AUDIT_TOOLS.md",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Tools audit -- public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/BANK_SCENARIOS.md",
        "category": "DOC_PROOF_TECHNICAL",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Scenarios P2 bank -- lies a tests Sigma, palier P2 commite",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/BANK_OUTPUTS.md",
        "category": "DOC_PROOF_TECHNICAL",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Format sorties Sigma -- reference technique lecture x108_gate/market_verdict",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/RFC3161.md",
        "category": "DOC_RSSI_EVIDENCE_CANDIDATE",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "RFC3161 anchor doc -- evidence RSSI, ancre timestamp cryptographique",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/TEST_RESULTS_FINAL.md",
        "category": "DOC_PROOF_TECHNICAL",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Resultats tests finaux -- lies a commits, public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    # ---- DOCS ROOT -- AUDIT TRAIL ----
    {
        "file_path": "docs/CI_POLICY.md",
        "category": "DOC_AUDIT_TRAIL",
        "decision": "KEEP_AS_AUDIT_LEDGER",
        "reason": "CI policy -- audit interne, pas de claims business",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/P1_FREEZE_AUDIT_READABILITY_NOTE.md",
        "category": "DOC_AUDIT_TRAIL",
        "decision": "KEEP_AS_AUDIT_LEDGER",
        "reason": "Note audit freeze P1 -- audit trail interne",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/DO_NOT_TOUCH_REPORT_FINAL.md",
        "category": "DOC_AUDIT_TRAIL",
        "decision": "KEEP_AS_AUDIT_LEDGER",
        "reason": "Rapport protected files -- audit interne",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/DEFERRED_PHASES_CLOSED_REPORT.md",
        "category": "DOC_ARCHIVE_ONLY",
        "decision": "KEEP_ARCHIVE_ONLY",
        "reason": "Phases fermees -- archive historique",
        "publish": False,
        "file_count_approx": 1,
    },
    # ---- P2 BANK ----
    {
        "file_path": "docs/P2_BANK_REPLAY_RESULTS.md",
        "category": "DOC_PROOF_TECHNICAL",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Resultats replay bank P2 -- lies a tests Sigma, public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/P2_BANK_*.md (21 autres fichiers scope/adversarial/shadow/etc.)",
        "category": "DOC_AUDIT_TRAIL",
        "decision": "KEEP_AS_AUDIT_LEDGER",
        "reason": "Scopes et audits bank P2 -- audit ledger interne, donnees locales",
        "publish": False,
        "file_count_approx": 21,
    },
    {
        "file_path": "docs/P2_ROADMAP.md",
        "category": "DOC_INVESTOR_NARRATIVE",
        "decision": "MOVE_LATER_INVESTOR",
        "reason": "Roadmap P2 -- narratif investisseur, separer du proof",
        "publish": False,
        "file_count_approx": 1,
    },
    # ---- BANK ROBO REAL ----
    {
        "file_path": "docs/BANK_ROBO_REAL_*.md (14 fichiers)",
        "category": "DOC_ARCHIVE_ONLY",
        "decision": "KEEP_ARCHIVE_ONLY",
        "reason": "Rapports tests E2E live terrain -- archive, donnees locales serveur",
        "publish": False,
        "file_count_approx": 14,
    },
    # ---- PRIVATE PROPRIETARY root docs ----
    {
        "file_path": "docs/EDUCATION_BIAS_LANGUAGE_BACKLOG_REPORT.md",
        "category": "DOC_PRIVATE_PROPRIETARY",
        "decision": "KEEP_PRIVATE_PROPRIETARY",
        "reason": "Backlog biais interne -- proprietaire",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/GITHUB_MCP_BENCHMARK_BACKLOG_REPORT.md",
        "category": "DOC_PRIVATE_PROPRIETARY",
        "decision": "KEEP_PRIVATE_PROPRIETARY",
        "reason": "Benchmark backlog interne -- proprietaire",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/MATH_CORE_POG_INTEGRATION_REPORT.md",
        "category": "DOC_PRIVATE_PROPRIETARY",
        "decision": "KEEP_PRIVATE_PROPRIETARY",
        "reason": "Math interne -- non publiable sans review formelle",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/GENCOIN_SANDBOX_INGESTION_REPORT.md",
        "category": "DOC_PRIVATE_PROPRIETARY",
        "decision": "KEEP_PRIVATE_PROPRIETARY",
        "reason": "Gencoin sandbox -- token non emis, non publiable sans review legale",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/WORLD_CALL_GATEWAY_INTEGRATION_REPORT.md",
        "category": "DOC_RUNTIME_INTERNAL",
        "decision": "DO_NOT_PUBLISH",
        "reason": "World call gateway -- interne runtime, chemins locaux",
        "publish": False,
        "file_count_approx": 1,
    },
    # ---- DOCS/CORE_IMPORT/ ----
    {
        "file_path": "docs/core_import/P56A->P77 (80 fichiers audit ledger)",
        "category": "DOC_CORE_IMPORT_LEDGER",
        "decision": "KEEP_AS_AUDIT_LEDGER",
        "reason": "Paliers import controle -- ledger audit complet P56->P77",
        "publish": False,
        "file_count_approx": 80,
    },
    {
        "file_path": "docs/core_import/P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT.*",
        "category": "DOC_RSSI_EVIDENCE_CANDIDATE",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Graphe invariants P72 -- RSSI evidence candidate, LEAN_PROVEN vs PYTHON_TESTED",
        "publish": True,
        "file_count_approx": 2,
    },
    {
        "file_path": "docs/core_import/P56D_SIGMA_POST_GUARD_VETO_BOUNDARY.md",
        "category": "DOC_RSSI_EVIDENCE_CANDIDATE",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Sigma post-guard veto-only -- RSSI evidence candidate, gel permanent",
        "publish": True,
        "file_count_approx": 1,
    },
    # ---- DOCS/FREEZE/ + DOCS/RUNTIME/ + DOCS/REAL_ENGINE/ ----
    {
        "file_path": "docs/freeze/ (83 fichiers Brody/runtime archives)",
        "category": "DOC_ARCHIVE_ONLY",
        "decision": "KEEP_ARCHIVE_ONLY",
        "reason": "Archives gel Brody/runtime -- donnees terrain locales, phases F40-F60",
        "publish": False,
        "file_count_approx": 83,
    },
    {
        "file_path": "docs/runtime/ (427 fichiers rapports Brody phases)",
        "category": "DOC_RUNTIME_INTERNAL",
        "decision": "DO_NOT_PUBLISH",
        "reason": "Rapports runtime/Brody phases -- internes, contiennent donnees locales et chemins",
        "publish": False,
        "file_count_approx": 427,
    },
    {
        "file_path": "docs/real_engine/ (31 fichiers P26-P56 reports)",
        "category": "DOC_ARCHIVE_ONLY",
        "decision": "KEEP_ARCHIVE_ONLY",
        "reason": "P26-P56 phase reports runtime -- archives, supersedes par P57+",
        "publish": False,
        "file_count_approx": 31,
    },
    # ---- DOCS/DEMO/ ----
    {
        "file_path": "docs/demo/OBSIDIA_F41_PUBLIC_INVESTOR_PITCH.md",
        "category": "DOC_INVESTOR_NARRATIVE",
        "decision": "MOVE_LATER_INVESTOR",
        "reason": "Pitch investisseur -- separer du proof technique, review claims avant publication",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/demo/OBSIDIA_F41_INVESTOR_JURY_FAQ.md",
        "category": "DOC_INVESTOR_NARRATIVE",
        "decision": "MOVE_LATER_INVESTOR",
        "reason": "FAQ jury investisseur -- narratif, pas preuve technique",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/demo/OBSIDIA_F41_DEMO_SCRIPT_3_5_MIN.md",
        "category": "DOC_DEMO_ONLY",
        "decision": "MOVE_LATER_DEMO",
        "reason": "Script demo 3.5 min -- demo uniquement, pas proof",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/demo/OBSIDIA_F41_WHAT_IT_PROVES_AND_DOES_NOT_PROVE.md",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Ce qu'il prouve/ne prouve pas -- separateur proof/pitch, public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/demo/OBSIDIA_F43_LIVE_SERVER_RUNBOOK.md",
        "category": "DOC_PRIVATE_PROPRIETARY",
        "decision": "KEEP_PRIVATE_PROPRIETARY",
        "reason": "Runbook serveur live -- proprietaire, chemins locaux",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/demo/OBSIDIA_F46_PUBLIC_READINESS_GATE.md",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Gate readiness public -- public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/demo/OBSIDIA_F48_RELEASE_READINESS_DECISION.md",
        "category": "DOC_AUDIT_TRAIL",
        "decision": "KEEP_AS_AUDIT_LEDGER",
        "reason": "Decision release readiness F48 -- audit trail",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/demo/OBSIDIA_F59_BUS_LAYER_PUBLIC_DEMO_INDEX.md",
        "category": "DOC_DEMO_ONLY",
        "decision": "MOVE_LATER_DEMO",
        "reason": "Demo index bus layer -- demo only",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/demo/ autres (17 fichiers F40-F58, F60, Brody GPT V1)",
        "category": "DOC_ARCHIVE_ONLY",
        "decision": "KEEP_ARCHIVE_ONLY",
        "reason": "Rapports phases F40-F60 -- archives, supersedes",
        "publish": False,
        "file_count_approx": 17,
    },
    # ---- DOCS/ARCHITECTURE/ ----
    {
        "file_path": "docs/architecture/ (45 fichiers F68-F77 + specs)",
        "category": "DOC_AUDIT_TRAIL",
        "decision": "KEEP_AS_AUDIT_LEDGER",
        "reason": "Architecture audits F68-F77 -- ledger technique interne",
        "publish": False,
        "file_count_approx": 45,
    },
    {
        "file_path": "docs/architecture/OBSIDIA_F60_SIGMA_REGISTRY_CANONICAL_DOMAINS.md",
        "category": "DOC_PROOF_TECHNICAL",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Registry Sigma 4 domaines -- preuve technique, public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    # ---- DOCS/SOURCE_PACKS/ ----
    {
        "file_path": "docs/source_packs/ (8 fichiers index CSV/MD)",
        "category": "DOC_SOURCE_PACK_LOCAL_ONLY",
        "decision": "KEEP_SOURCE_PACK_LOCAL_ONLY",
        "reason": "Index source packs locaux -- non publiables tels quels, snapshot 2026-06-02",
        "publish": False,
        "file_count_approx": 8,
    },
    # ---- DOCS/CIVILIZATION/ ----
    {
        "file_path": "docs/civilization/ (4 fichiers narratif AGI governance)",
        "category": "DOC_INVESTOR_NARRATIVE",
        "decision": "MOVE_LATER_INVESTOR",
        "reason": "Narratif AGI governance civilisationnelle -- investisseur, pas preuve technique",
        "publish": False,
        "file_count_approx": 4,
    },
    # ---- DOCS/BLOCKCHAIN/ ----
    {
        "file_path": "docs/blockchain/ (13 fichiers policies)",
        "category": "DOC_PROOF_TECHNICAL",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Policies blockchain dry-run -- pas de vrai token. Preuve technique sandbox.",
        "publish": True,
        "file_count_approx": 13,
    },
    # ---- DOCS/GENCOIN/ ----
    {
        "file_path": "docs/gencoin/ (7 fichiers)",
        "category": "DOC_DO_NOT_PUBLISH",
        "decision": "DO_NOT_PUBLISH",
        "reason": "Gencoin token speculatif non emis -- DO_NOT_PUBLISH sans review legale token",
        "publish": False,
        "file_count_approx": 7,
    },
    # ---- DOCS/HACKATHONS/ ----
    {
        "file_path": "docs/hackathons/ (5 fichiers)",
        "category": "DOC_PRIVATE_PROPRIETARY",
        "decision": "KEEP_PRIVATE_PROPRIETARY",
        "reason": "Rapports echecs hackathons -- donnees proprietaires, non publiables",
        "publish": False,
        "file_count_approx": 5,
    },
    # ---- DOCS/STATUS/ ----
    {
        "file_path": "docs/status/PUBLIC_STATUS.md",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Statut public repo -- public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/status/ autres (11 fichiers)",
        "category": "DOC_ARCHIVE_ONLY",
        "decision": "KEEP_ARCHIVE_ONLY",
        "reason": "Status archives phases -- historique",
        "publish": False,
        "file_count_approx": 11,
    },
    # ---- DOCS/RELEASE/ ----
    {
        "file_path": "docs/release/BRODY_GPT_V1_PUBLIC_RELEASE_PACKAGE.md",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Release Brody GPT V1 -- public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/release/BRODY_GPT_V1_LIMITATIONS_AND_BOUNDARIES.md",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Limitations Brody GPT V1 -- public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/release/ autres (3 fichiers proof index et bus release)",
        "category": "DOC_AUDIT_TRAIL",
        "decision": "KEEP_AS_AUDIT_LEDGER",
        "reason": "Proof index et release bus layer -- audit trail",
        "publish": False,
        "file_count_approx": 3,
    },
    # ---- DOCS/AGENTS/ ACT/ CI/ OS3/ ----
    {
        "file_path": "docs/agents/ (3 fichiers)",
        "category": "DOC_PROOF_TECHNICAL",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Contrats agents non-souverains -- preuve technique, public safe",
        "publish": True,
        "file_count_approx": 3,
    },
    {
        "file_path": "docs/act/ (4 fichiers)",
        "category": "DOC_PROOF_TECHNICAL",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Lifecycle action -- ACT policy docs, DRY_RUN_ONLY",
        "publish": True,
        "file_count_approx": 4,
    },
    {
        "file_path": "docs/ci/ (3 fichiers)",
        "category": "DOC_AUDIT_TRAIL",
        "decision": "KEEP_AS_AUDIT_LEDGER",
        "reason": "CI pipeline docs -- audit interne",
        "publish": False,
        "file_count_approx": 3,
    },
    {
        "file_path": "docs/os3/ (3 fichiers)",
        "category": "DOC_PROOF_TECHNICAL",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "OS3 hash chain, proof ticket, replay manifest -- preuve technique",
        "publish": True,
        "file_count_approx": 3,
    },
    # ---- INTERNAL DOCS ----
    {
        "file_path": "docs/brody/ (5 fichiers)",
        "category": "DOC_API_INTERNAL",
        "decision": "DO_NOT_PUBLISH",
        "reason": "Brody readonly policy -- API interne",
        "publish": False,
        "file_count_approx": 5,
    },
    {
        "file_path": "docs/memory/ (6 fichiers)",
        "category": "DOC_MEMORY_INTERNAL",
        "decision": "DO_NOT_PUBLISH",
        "reason": "Memory boundary docs -- interne",
        "publish": False,
        "file_count_approx": 6,
    },
    {
        "file_path": "docs/graphiti/ (4 fichiers)",
        "category": "DOC_MEMORY_INTERNAL",
        "decision": "DO_NOT_PUBLISH",
        "reason": "Graphiti readonly policy -- interne",
        "publish": False,
        "file_count_approx": 4,
    },
    {
        "file_path": "docs/context/ (4 fichiers)",
        "category": "DOC_API_INTERNAL",
        "decision": "DO_NOT_PUBLISH",
        "reason": "Context packet -- API interne",
        "publish": False,
        "file_count_approx": 4,
    },
    {
        "file_path": "docs/periphery/ (14 fichiers)",
        "category": "DOC_RUNTIME_INTERNAL",
        "decision": "DO_NOT_PUBLISH",
        "reason": "Periphery adapters docs -- interne runtime",
        "publish": False,
        "file_count_approx": 14,
    },
    {
        "file_path": "docs/interface/ (2 fichiers)",
        "category": "DOC_API_INTERNAL",
        "decision": "DO_NOT_PUBLISH",
        "reason": "Interface contracts -- API interne",
        "publish": False,
        "file_count_approx": 2,
    },
    {
        "file_path": "docs/translation/ (4 fichiers)",
        "category": "DOC_PRIVATE_PROPRIETARY",
        "decision": "KEEP_PRIVATE_PROPRIETARY",
        "reason": "OS Trad / IR pipeline -- proprietaire",
        "publish": False,
        "file_count_approx": 4,
    },
    {
        "file_path": "docs/world_calls/ (1 fichier)",
        "category": "DOC_RUNTIME_INTERNAL",
        "decision": "DO_NOT_PUBLISH",
        "reason": "World calls gateway -- interne runtime",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/mcp/ (1 fichier)",
        "category": "DOC_API_INTERNAL",
        "decision": "DO_NOT_PUBLISH",
        "reason": "MCP policy -- API interne",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/language/ (1 fichier)",
        "category": "DOC_PRIVATE_PROPRIETARY",
        "decision": "KEEP_PRIVATE_PROPRIETARY",
        "reason": "Language routing -- proprietaire",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/math/ (1 fichier)",
        "category": "DOC_PRIVATE_PROPRIETARY",
        "decision": "KEEP_PRIVATE_PROPRIETARY",
        "reason": "Math formelle interne -- non publiable sans review",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/roadmap/ (1 fichier NOT_YET_IMPLEMENTED)",
        "category": "DOC_INVESTOR_NARRATIVE",
        "decision": "MOVE_LATER_INVESTOR",
        "reason": "Roadmap NOT_YET_IMPLEMENTED -- investisseur interne",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/education/ (1 fichier README)",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Education README -- public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "docs/benchmarks/ (1 fichier README)",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Benchmarks README -- public safe",
        "publish": True,
        "file_count_approx": 1,
    },
    # ---- SPECS/ ----
    {
        "file_path": "specs/00_SCOPE_DISCIPLINE/ (9 fichiers)",
        "category": "DOC_RSSI_EVIDENCE_CANDIDATE",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Scope discipline -- claims publics bornes. RSSI evidence candidate.",
        "publish": True,
        "file_count_approx": 9,
    },
    {
        "file_path": "specs/01_X108_AUTHORITY/ (7 fichiers)",
        "category": "DOC_RSSI_EVIDENCE_CANDIDATE",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Autorite X108 -- GuardX108 Lean-proven, KX108_ONLY. RSSI candidate.",
        "publish": True,
        "file_count_approx": 7,
    },
    {
        "file_path": "specs/02_INTERLAYER_CONSTITUTION/ (8 fichiers)",
        "category": "DOC_FORMAL_PROOF_MAP",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Constitution interlayer -- formal proof map architecture",
        "publish": True,
        "file_count_approx": 8,
    },
    {
        "file_path": "specs/03_ENTROPY_DISCIPLINE/ (11 fichiers)",
        "category": "DOC_FORMAL_PROOF_MAP",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Entropie formelle -- formal proof map, pas pour investisseur",
        "publish": True,
        "file_count_approx": 11,
    },
    {
        "file_path": "specs/04_AGI_TREE34_FLUX/ (5 fichiers)",
        "category": "DOC_PRIVATE_PROPRIETARY",
        "decision": "KEEP_PRIVATE_PROPRIETARY",
        "reason": "Tree34 AGI -- proprietaire, pas public safe sans review formelle",
        "publish": False,
        "file_count_approx": 5,
    },
    {
        "file_path": "specs/05_BALANCE_BUV_GEOMETRIES/ (9 fichiers)",
        "category": "DOC_PRIVATE_PROPRIETARY",
        "decision": "KEEP_PRIVATE_PROPRIETARY",
        "reason": "BUV geometries -- proprietaire, pas public safe sans review",
        "publish": False,
        "file_count_approx": 9,
    },
    {
        "file_path": "specs/06_HIGH_PERIPHERY_SYSTEMS/ (7 fichiers)",
        "category": "DOC_PRIVATE_PROPRIETARY",
        "decision": "KEEP_PRIVATE_PROPRIETARY",
        "reason": "High periphery -- proprietaire, systemes non publies",
        "publish": False,
        "file_count_approx": 7,
    },
    {
        "file_path": "specs/07_AGENTS_CONNECTORS_MCP/ (10 fichiers)",
        "category": "DOC_PROOF_TECHNICAL",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Agents/connectors policies -- proof technique, no-act boundary",
        "publish": True,
        "file_count_approx": 10,
    },
    {
        "file_path": "specs/08_MEMORY_BRODY_GRAPHITI/ (7 fichiers)",
        "category": "DOC_PROOF_TECHNICAL",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Memory boundary -- proof technique readonly/no-write",
        "publish": True,
        "file_count_approx": 7,
    },
    {
        "file_path": "specs/09_CRITICAL_WORLDS/ (14 fichiers)",
        "category": "DOC_RSSI_EVIDENCE_CANDIDATE",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Domaines critiques GPS/bank/trading/aviation -- RSSI evidence candidate",
        "publish": True,
        "file_count_approx": 14,
    },
    {
        "file_path": "specs/10_VALUE_GENCOIN_JCOIN/ (11 fichiers)",
        "category": "DOC_DO_NOT_PUBLISH",
        "decision": "DO_NOT_PUBLISH",
        "reason": "Gencoin/Jcoin valeur -- DO_NOT_PUBLISH sans review legale token",
        "publish": False,
        "file_count_approx": 11,
    },
    {
        "file_path": "specs/11_PROOF_REPLAY_OS3/ (9 fichiers)",
        "category": "DOC_RSSI_EVIDENCE_CANDIDATE",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Replay OS3, RFC3161, Merkle, attestation -- RSSI evidence candidate",
        "publish": True,
        "file_count_approx": 9,
    },
    {
        "file_path": "specs/12_NARRATIVE_PROVENANCE_LAYER/ (34 fichiers)",
        "category": "DOC_PRIVATE_PROPRIETARY",
        "decision": "KEEP_PRIVATE_PROPRIETARY",
        "reason": "Narrative provenance -- proprietaire, contenu interne philosophique",
        "publish": False,
        "file_count_approx": 34,
    },
    {
        "file_path": "specs/_invariant_graph/ (10 fichiers)",
        "category": "DOC_FORMAL_PROOF_MAP",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Graphe invariants -- formal proof map, RSSI candidate cle",
        "publish": True,
        "file_count_approx": 10,
    },
    {
        "file_path": "specs/_source_index/ (7 fichiers)",
        "category": "DOC_SOURCE_PACK_LOCAL_ONLY",
        "decision": "KEEP_SOURCE_PACK_LOCAL_ONLY",
        "reason": "Index source -- local only tant que source packs non canonises",
        "publish": False,
        "file_count_approx": 7,
    },
    {
        "file_path": "specs/INDEX.md + OBSIDIA_READING_GUIDE.md",
        "category": "DOC_PUBLIC_SAFE",
        "decision": "KEEP_AS_PUBLIC_SAFE",
        "reason": "Index specs et guide lecture -- public safe",
        "publish": True,
        "file_count_approx": 2,
    },
    {
        "file_path": "specs/SPEC_REGISTRY.md + PLAN2_*.md",
        "category": "DOC_AUDIT_TRAIL",
        "decision": "KEEP_AS_AUDIT_LEDGER",
        "reason": "Registry specs et plans -- audit trail",
        "publish": False,
        "file_count_approx": 4,
    },
    # ---- PROOFS/ ----
    {
        "file_path": "proofs/lean/ (theoremes Lean LEAN_PROVEN)",
        "category": "DOC_PROOF_TECHNICAL",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Theoremes Lean -- LEAN_PROVEN, cle de la preuve formelle",
        "publish": True,
        "file_count_approx": 9,
    },
    {
        "file_path": "proofs/tla/ (TLA+ specs)",
        "category": "DOC_PROOF_TECHNICAL",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "TLA+ specs -- preuve formelle",
        "publish": True,
        "file_count_approx": 17,
    },
    {
        "file_path": "proofs/merkle_root.json",
        "category": "DOC_RSSI_EVIDENCE_CANDIDATE",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Racine Merkle -- evidence RSSI, ancre cryptographique",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "proofs/rfc3161_anchor.json",
        "category": "DOC_RSSI_EVIDENCE_CANDIDATE",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "RFC3161 timestamp anchor -- evidence RSSI, timestamp cryptographique",
        "publish": True,
        "file_count_approx": 1,
    },
    {
        "file_path": "proofs/V18_3_1/ + V18_7/ + V18_8/ (versions proof formelles)",
        "category": "DOC_PROOF_TECHNICAL",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Versions proof formelles -- PROTEGE P77, ne pas modifier",
        "publish": True,
        "file_count_approx": 12,
    },
    {
        "file_path": "proofs/verify_all.py + verify_decision.py + verify_merkle.py",
        "category": "DOC_PROOF_TECHNICAL",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "Verificateurs proof -- public safe, scripts cles",
        "publish": True,
        "file_count_approx": 3,
    },
    {
        "file_path": "proofs/PROOFKIT_REPORT.json",
        "category": "DOC_RSSI_EVIDENCE_CANDIDATE",
        "decision": "KEEP_AS_TECHNICAL_PROOF",
        "reason": "PROOFKIT report -- RSSI evidence (protege P77)",
        "publish": True,
        "file_count_approx": 1,
    },
    # ---- AUDIT/ ----
    {
        "file_path": "audit/sovereign_tickets.jsonl",
        "category": "DOC_RSSI_EVIDENCE_CANDIDATE",
        "decision": "KEEP_AS_AUDIT_LEDGER",
        "reason": "Tickets souverains -- RSSI evidence candidate (non publie directement)",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "audit/world_action_bus.jsonl",
        "category": "DOC_DO_NOT_PUBLISH",
        "decision": "DO_NOT_PUBLISH",
        "reason": "Bus actions -- PROTEGE P77, donnees runtime internes",
        "publish": False,
        "file_count_approx": 1,
    },
    {
        "file_path": "audit/ autres (11 fichiers templates/matrices)",
        "category": "DOC_AUDIT_TRAIL",
        "decision": "KEEP_AS_AUDIT_LEDGER",
        "reason": "Templates et matrices audit -- ledger interne",
        "publish": False,
        "file_count_approx": 11,
    },
    # ---- SIGMA/ RUNTIME_WIRING/ APPS/ ----
    {
        "file_path": "sigma/ (136 fichiers PROTEGE)",
        "category": "DOC_RUNTIME_INTERNAL",
        "decision": "DO_NOT_PUBLISH",
        "reason": "PROTEGE P77 -- sigma runtime souverain interne",
        "publish": False,
        "file_count_approx": 136,
    },
    {
        "file_path": "runtime_wiring/ (111 fichiers PROTEGE)",
        "category": "DOC_RUNTIME_INTERNAL",
        "decision": "DO_NOT_PUBLISH",
        "reason": "PROTEGE P77 -- runtime wiring interne",
        "publish": False,
        "file_count_approx": 111,
    },
    {
        "file_path": "apps/obsidia_api/ (PROTEGE)",
        "category": "DOC_API_INTERNAL",
        "decision": "DO_NOT_PUBLISH",
        "reason": "PROTEGE P77 -- API interne routes et apps",
        "publish": False,
        "file_count_approx": 0,
    },
    {
        "file_path": "apps/obsidia-workbench/",
        "category": "DOC_PRIVATE_PROPRIETARY",
        "decision": "KEEP_PRIVATE_PROPRIETARY",
        "reason": "Workbench UI -- proprietaire, pas public sans review",
        "publish": False,
        "file_count_approx": 0,
    },
    # ---- PERIPHERY/ CONNECTORS/ ----
    {
        "file_path": "periphery/ (3278 fichiers, 132 modules)",
        "category": "DOC_PRIVATE_PROPRIETARY",
        "decision": "KEEP_PRIVATE_PROPRIETARY",
        "reason": "Periphery -- proprietaire, contenu cognitif interne (AGI/BDF/Tree34/MMonde)",
        "publish": False,
        "file_count_approx": 3278,
    },
    {
        "file_path": "connectors/ (10 fichiers PROTEGE P70)",
        "category": "DOC_CONNECTOR_INTERNAL",
        "decision": "DO_NOT_PUBLISH",
        "reason": "PROTEGE P77 -- connectors P70 BLOCK_CONNECTOR_RUN, egress reseau",
        "publish": False,
        "file_count_approx": 10,
    },
    # ---- SOURCE PACKS / TMP / FREEZES / LOCAL AUDITS ----
    {
        "file_path": "_source_packs/ (40 fichiers PROTEGE)",
        "category": "DOC_SOURCE_PACK_LOCAL_ONLY",
        "decision": "KEEP_SOURCE_PACK_LOCAL_ONLY",
        "reason": "PROTEGE P77 -- source packs locaux non canonises",
        "publish": False,
        "file_count_approx": 40,
    },
    {
        "file_path": "_tmp_core_import/ (282 fichiers PROTEGE)",
        "category": "DOC_SOURCE_PACK_LOCAL_ONLY",
        "decision": "KEEP_SOURCE_PACK_LOCAL_ONLY",
        "reason": "PROTEGE P77 -- core import temporaire P75 NO_RUNTIME_IMPORT",
        "publish": False,
        "file_count_approx": 282,
    },
    {
        "file_path": "_freezes/ (2455 fichiers PROTEGE)",
        "category": "DOC_ARCHIVE_ONLY",
        "decision": "KEEP_ARCHIVE_ONLY",
        "reason": "PROTEGE P77 -- 19 archives freeze locales, non publiables",
        "publish": False,
        "file_count_approx": 2455,
    },
    {
        "file_path": ".local_audits/ (42 fichiers PROTEGE)",
        "category": "DOC_ARCHIVE_ONLY",
        "decision": "KEEP_ARCHIVE_ONLY",
        "reason": "PROTEGE P77 -- audits locaux non publiables",
        "publish": False,
        "file_count_approx": 42,
    },
]

# ---------------------------------------------------------------------------
# Contraintes P72/P77
# ---------------------------------------------------------------------------

P72_CLAIM_CONSTRAINTS_APPLIED = [
    "GUARD_X108_FINAL_AUTHORITY : specs/01_X108_AUTHORITY/* -- RSSI candidate",
    "NO_ACT_BEFORE_TAU : connectors/ -- DO_NOT_PUBLISH, BLOCK_CONNECTOR_RUN",
    "SIGMA_POST_GUARD_VETO_ONLY : sigma/ -- RUNTIME_INTERNAL, DO_NOT_PUBLISH",
    "NO_MEMORY_WRITE_WITHOUT_GATE : audit/world_action_bus.jsonl -- DO_NOT_PUBLISH",
    "LEAN_PROVEN_VS_PYTHON_TESTED : proofs/lean/ -- DOC_PROOF_TECHNICAL public safe",
    "NETWORK_EGRESS_REVIEW_REQUIRED : connectors/ aviation_robo.py/bank/trading -- DO_NOT_PUBLISH",
    "KX108_ONLY_DECISION_AUTHORITY : specs/01_X108_AUTHORITY/ -- RSSI candidate",
    "DETERMINISM : proofs/verify_*.py -- DOC_PROOF_TECHNICAL public safe",
]

P77_WORDING_CONSTRAINTS_APPLIED = [
    "REGROUP_CANDIDATE (was REGROUP_CANON) : docs/source_packs/ -- SOURCE_PACK_LOCAL_ONLY",
    "KEEP_CORE_OR_OFFICIAL_REVIEW (was KEEP_CANON) : docs/source_packs/ -- SOURCE_PACK_LOCAL_ONLY",
    "canonical justifie si hash/tag/commit/freeze/test : README.md, LIMITS.md, BANK_SCENARIOS.md",
    "P76_BOM_NORMALIZATION_SAFE : sigma/examples/gps_omega_chaos.json -- RUNTIME_INTERNAL",
]

# ---------------------------------------------------------------------------
# Focus findings P78
# ---------------------------------------------------------------------------

FOCUS_FINDINGS = [
    {
        "finding_id": "P78-F1",
        "type": "SEPARATION_PROOF_VS_DEMO",
        "description": "docs/demo/ melange narratifs investisseur (F41 pitch/FAQ) et archives phases (F40-F60). Separer INVESTOR_NARRATIVE de DEMO_ONLY avant freeze P80.",
        "action": "MOVE_LATER_INVESTOR + MOVE_LATER_DEMO",
    },
    {
        "finding_id": "P78-F2",
        "type": "DO_NOT_PUBLISH_TOKEN",
        "description": "docs/gencoin/ et specs/10_VALUE_GENCOIN_JCOIN/ -- 18 fichiers token non emis. DO_NOT_PUBLISH sans review legale.",
        "action": "DO_NOT_PUBLISH",
    },
    {
        "finding_id": "P78-F3",
        "type": "RSSI_EVIDENCE_PACK_CANDIDATES",
        "description": "8 groupes RSSI evidence candidate identifies : RFC3161, Merkle, P72 invariants, specs/00-01-09-11, proofs/lean/tla/, PROOFKIT_REPORT.",
        "action": "KEEP_AS_TECHNICAL_PROOF -- constitue le socle P79 RSSI pack",
    },
    {
        "finding_id": "P78-F4",
        "type": "PERIPHERY_MASSIVE_PROPRIETARY",
        "description": "periphery/ = 3278 fichiers, 132 modules (AGI/BDF/Tree34/MMonde/etc.). Tout proprietaire. Ne pas publier sans review complete.",
        "action": "KEEP_PRIVATE_PROPRIETARY",
    },
    {
        "finding_id": "P78-F5",
        "type": "PUBLIC_SAFE_SURFACE_IDENTIFIED",
        "description": "Surface public safe identifiee : README, LIMITS, GLOSSAIRE, KERNEL_OVERVIEW, SIGMA, BANK_SCENARIOS, BANK_OUTPUTS, PROOF_SCOPE, specs/INDEX, specs/00-02-07-08-11, docs/act, docs/agents, docs/os3, proofs/lean/tla/verify_*.",
        "action": "KEEP_AS_PUBLIC_SAFE -- constitue le pack public P80",
    },
    {
        "finding_id": "P78-F6",
        "type": "ARCHIVE_LOAD",
        "description": "5 zones archives massives : _freezes/ 2455 fichiers, docs/runtime/ 427 fichiers, periphery/ 3278 fichiers, _tmp_core_import/ 282 fichiers, _freezes/ local. Ne pas charger en runtime.",
        "action": "KEEP_ARCHIVE_ONLY / KEEP_PRIVATE_PROPRIETARY",
    },
    {
        "finding_id": "P78-F7",
        "type": "INDEX_DOCS_CREATED",
        "description": "4 index docs crees : docs/public/README_PUBLIC_BOUNDARY.md, docs/investor/README_INVESTOR_BOUNDARY.md, docs/proof/README_PROOF_BOUNDARY.md, docs/demo/README_DEMO_BOUNDARY.md.",
        "action": "CREATED_INDEX_DOCS",
    },
]

# ---------------------------------------------------------------------------
# Compute listes par categorie
# ---------------------------------------------------------------------------

def _list_by_decision(decision: str) -> list[str]:
    return [e["file_path"] for e in DOC_MATRIX if e["decision"] == decision]


def _list_by_category(cat: str) -> list[str]:
    return [e["file_path"] for e in DOC_MATRIX if e["category"] == cat]


def _count_decisions() -> dict:
    counts: dict[str, int] = {}
    for e in DOC_MATRIX:
        d = e["decision"]
        counts[d] = counts.get(d, 0) + 1
    return counts


def _count_categories() -> dict:
    counts: dict[str, int] = {}
    for e in DOC_MATRIX:
        c = e["category"]
        counts[c] = counts.get(c, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Rapport
# ---------------------------------------------------------------------------

CREATED_INDEXES = [
    "docs/public/README_PUBLIC_BOUNDARY.md",
    "docs/investor/README_INVESTOR_BOUNDARY.md",
    "docs/proof/README_PROOF_BOUNDARY.md",
    "docs/demo/README_DEMO_BOUNDARY.md",
]

REPORT = {
    "audit_id": "P78",
    "status": "P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT_READY",
    "mode": "AUDIT_AND_DOC_INDEX_ONLY",
    "branch": "p78-presentation-proof-public-private-split",
    "date": "2026-06-09",
    "dry_run_only": DRY_RUN_ONLY,
    "source_patch_applied": False,
    "files_imported_count": 0,
    "split_decision": "CLASSIFY_AND_INDEX_ONLY",
    "split_model": SPLIT_MODEL,
    "files_scanned_count": len(DOC_MATRIX),
    "doc_matrix": DOC_MATRIX,
    "category_counts": _count_categories(),
    "decision_counts": _count_decisions(),
    "technical_proof": _list_by_category("DOC_PROOF_TECHNICAL"),
    "audit_trail": _list_by_decision("KEEP_AS_AUDIT_LEDGER"),
    "formal_proof_map": _list_by_category("DOC_FORMAL_PROOF_MAP"),
    "rssi_evidence_candidates": _list_by_category("DOC_RSSI_EVIDENCE_CANDIDATE"),
    "public_safe": _list_by_decision("KEEP_AS_PUBLIC_SAFE"),
    "public_needs_softening": _list_by_decision("MOVE_LATER_PUBLIC"),
    "investor_narrative": _list_by_decision("MOVE_LATER_INVESTOR"),
    "demo_only": _list_by_decision("MOVE_LATER_DEMO"),
    "private_proprietary": _list_by_decision("KEEP_PRIVATE_PROPRIETARY"),
    "source_pack_local_only": _list_by_decision("KEEP_SOURCE_PACK_LOCAL_ONLY"),
    "archive_only": _list_by_decision("KEEP_ARCHIVE_ONLY"),
    "do_not_publish": _list_by_decision("DO_NOT_PUBLISH"),
    "unknown_review": _list_by_decision("REQUIRES_REVIEW"),
    "created_indexes": CREATED_INDEXES,
    "focus_findings": FOCUS_FINDINGS,
    "p72_claim_constraints_applied": P72_CLAIM_CONSTRAINTS_APPLIED,
    "p77_wording_constraints_applied": P77_WORDING_CONSTRAINTS_APPLIED,
    **_BOUNDARY,
    "next_step": "P79_RSSI_EVIDENCE_PACK_AND_GITHUB_SECURITY_AUDIT",
}


def run_audit() -> dict:
    for key, val in _BOUNDARY.items():
        assert val is False, f"BLOCK_RUNTIME_IMPORT: {key} = {val}"

    public = _list_by_decision("KEEP_AS_PUBLIC_SAFE")
    rssi = _list_by_category("DOC_RSSI_EVIDENCE_CANDIDATE")
    dnp = _list_by_decision("DO_NOT_PUBLISH")

    print(f"P78 audit => {len(DOC_MATRIX)} entrees matrice")
    print(f"Public safe => {len(public)} entrees")
    print(f"RSSI evidence candidates => {len(rssi)} entrees")
    print(f"DO_NOT_PUBLISH => {len(dnp)} entrees")
    print(f"JSON => {OUT_JSON}")

    return REPORT


if __name__ == "__main__":
    report = run_audit()
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT_READY")
    sys.exit(0)
