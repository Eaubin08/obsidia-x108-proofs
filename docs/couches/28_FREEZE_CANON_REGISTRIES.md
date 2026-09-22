# 28 · Freeze, canon, registres

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Registres et décisions de gel. Ce sont des entrées de gouvernance, pas du comportement.

## Où elle intervient dans le trajet d'une demande

Couche **transverse** : elle encadre toutes les étapes plutôt qu'une seule.

Voir le trajet complet : [guide général](../README.md).

## Où est son code aujourd'hui

D'après le registre de fonctionnalités V3, **52 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `freeze/OBSIDIA_OIE_V01_ENGINE_FREEZE_20260701_052940/` | 8 |
| `freeze/OBSIDIA_INFERENCE_ECONOMY_FREEZE_20260701_044702/` | 6 |
| `scripts/` | 6 |
| `proofs/V18_3_1/` | 5 |
| `_FREEZE/VERIFY_CLAUDE_LEAN_ANALYSIS_20260626_155453/` | 4 |
| `freeze/OBSIDIA_OIE_EXTERNAL_BENCHMARK_HARNESS_V0_FREEZE_20260701_055129/` | 4 |
| `_FREEZE/LEAN_SANDBOX_15_PASS_20260626_153034/` | 3 |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | 3 |
| `agents/` | 2 |
| `periphery/` | 2 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (73)

### Documents de référence — à lire en premier

- [F69 ? Canonical Test Suite Taxonomy](../architecture/F69_CANONICAL_TEST_SUITE_TAXONOMY.md) · `docs/architecture/F69_CANONICAL_TEST_SUITE_TAXONOMY.md`
  <br>- Status: FAILCANONICALTESTS
- [FREEZE_CRITERIA_FULL_STACK_V0](../architecture/FREEZE_CRITERIA_FULL_STACK_V0.md) · `docs/architecture/FREEZE_CRITERIA_FULL_STACK_V0.md`
  <br>Freeze si kernel inchangé, non-souveraineté PASS, Bank/Trading/GPS PASS, OS3/Gencoin PASS.
- [OBSIDIA CORE/PROOF METRIC DELTA — DETAIL REVIEW V0](../core_import/OBSIDIA_CORE_PROOF_METRIC_DELTA_DETAIL_REVIEW_V0.md) · `docs/core_import/OBSIDIA_CORE_PROOF_METRIC_DELTA_DETAIL_REVIEW_V0.md` *(référence probable)*
  <br>METRICBLOCKERSZEROBUTHUMANREVIEWREQUIRED
- [Optional Publication Readiness Recheck](../core_import/OPTIONAL_PUBLICATION_READINESS_RECHECK.md) · `docs/core_import/OPTIONAL_PUBLICATION_READINESS_RECHECK.md` *(référence probable)*
  <br>Note : Les deux runs appartiennent à un contexte de session compacté. Leurs outputs ne sont plus accessibles. Couverture assurée par 366 tests PASS exécutés dans ce palier (P79…
- [FULL_STACK_FREEZE_CHECKLIST_V0](../freeze/FULL_STACK_FREEZE_CHECKLIST_V0.md) · `docs/freeze/FULL_STACK_FREEZE_CHECKLIST_V0.md` *(référence probable)*
  <br>À remplir après exécution. Critère dur : kernel X-108 inchangé.
- [V5A Backlog Remaining](../freeze/V5A_BACKLOG_REMAINING.md) · `docs/freeze/V5A_BACKLOG_REMAINING.md` *(référence probable)*
  <br>No sovereignty-critical items deferred.
- [V5B Remaining Backlog](../freeze/V5B_REMAINING_BACKLOG.md) · `docs/freeze/V5B_REMAINING_BACKLOG.md` *(référence probable)*
  <br>No sovereignty-critical items deferred.
- [Corpus Map V4 — Canon Status](../source_packs/CORPUS_MAP_V4_CANON_STATUS.md) · `docs/source_packs/CORPUS_MAP_V4_CANON_STATUS.md` *(référence probable)*
  <br>canonicalcorpus, canonicalsubgroup, sourcepatterns, knownfilecount,

<details><summary><b>Rapports, audits et preuves d'exécution</b> (52)</summary>

**`docs/`**

- [P1_FREEZE_AUDIT_READABILITY_NOTE.md](../P1_FREEZE_AUDIT_READABILITY_NOTE.md) — P1 Freeze Audit Readability Note

**`docs/core_import/`** · *dossier lu par du code : ne pas déplacer*

- [OBSIDIA_CORE_PROOF_BLOCKING_DELTAS_V0.json](../core_import/OBSIDIA_CORE_PROOF_BLOCKING_DELTAS_V0.json)
- [OBSIDIA_CORE_PROOF_METRIC_DELTA_AUDIT_V0.md](../core_import/OBSIDIA_CORE_PROOF_METRIC_DELTA_AUDIT_V0.md) — OBSIDIA CORE/PROOF METRIC DELTA AUDIT V0
- [OBSIDIA_CORE_PROOF_METRIC_DELTA_DETAIL_REVIEW_V0.json](../core_import/OBSIDIA_CORE_PROOF_METRIC_DELTA_DETAIL_REVIEW_V0.json)
- [OBSIDIA_CORE_PROOF_METRIC_DELTA_MATRIX_V0.json](../core_import/OBSIDIA_CORE_PROOF_METRIC_DELTA_MATRIX_V0.json)
- [OPTIONAL_PUBLICATION_READINESS_RECHECK.json](../core_import/OPTIONAL_PUBLICATION_READINESS_RECHECK.json)
- [P56A_C0_GAMMA_IMPACT_AUDIT_VERDICT.json](../core_import/P56A_C0_GAMMA_IMPACT_AUDIT_VERDICT.json)
- [P56A_C_DIFF_protocols.diff](../core_import/P56A_C_DIFF_protocols.diff)
- [P56A_C_DIFF_run_pipeline.diff](../core_import/P56A_C_DIFF_run_pipeline.diff)
- [P56B_GAMMA_CONTROLLED_PATCH_REPORT.json](../core_import/P56B_GAMMA_CONTROLLED_PATCH_REPORT.json)
- [P56C_AUDIT_ONLY_P08_protocols.py.diff](../core_import/P56C_AUDIT_ONLY_P08_protocols.py.diff)
- [P56C_AUDIT_ONLY_P11_run_pipeline.py.diff](../core_import/P56C_AUDIT_ONLY_P11_run_pipeline.py.diff)
- [P56C_P08_P10_P11_CONFLICT_AUDIT_ONLY.json](../core_import/P56C_P08_P10_P11_CONFLICT_AUDIT_ONLY.json)
- [P56C_P08_P10_P11_CONFLICT_AUDIT_ONLY.md](../core_import/P56C_P08_P10_P11_CONFLICT_AUDIT_ONLY.md) — P56C — P08/P10/P11 Conflict Audit Only
- [P56E_POST_PATCH_METRIC_REAUDIT.json](../core_import/P56E_POST_PATCH_METRIC_REAUDIT.json)
- [P56E_POST_PATCH_METRIC_REAUDIT.md](../core_import/P56E_POST_PATCH_METRIC_REAUDIT.md) — P56E — POST-PATCH METRIC RE-AUDIT
- [P57_CORE_MACHINERY_INVENTORY.json](../core_import/P57_CORE_MACHINERY_INVENTORY.json)
- [P57_CORE_TO_PROOF_IMPORT_PLAN.json](../core_import/P57_CORE_TO_PROOF_IMPORT_PLAN.json)
- [P57_RUNTIME_BINDING_AUDIT.json](../core_import/P57_RUNTIME_BINDING_AUDIT.json)
- [P57_RUNTIME_BINDING_AUDIT.md](../core_import/P57_RUNTIME_BINDING_AUDIT.md) — P57 — RUNTIME BINDING AUDIT
- [P58_CORE_IMPORT_TRIAGE_OPERATIONAL_PATH_AWARE.json](../core_import/P58_CORE_IMPORT_TRIAGE_OPERATIONAL_PATH_AWARE.json)
- [P59_SAFE_BATCH_1_IMPORT.json](../core_import/P59_SAFE_BATCH_1_IMPORT.json)
- [P60_TEST_BATCH_2_IMPORT.json](../core_import/P60_TEST_BATCH_2_IMPORT.json)
- [P62_MANUAL_REVIEW_DEFERRED.json](../core_import/P62_MANUAL_REVIEW_DEFERRED.json)
- [P63_GLOBAL_FUSION_REALITY_AUDIT.json](../core_import/P63_GLOBAL_FUSION_REALITY_AUDIT.json)
- [P63_GLOBAL_FUSION_REALITY_AUDIT.md](../core_import/P63_GLOBAL_FUSION_REALITY_AUDIT.md) — P63 — Global Fusion Reality Audit
- [P64_FUSION_CONTINUITY_LEDGER.json](../core_import/P64_FUSION_CONTINUITY_LEDGER.json)
- [P69_FILESYSTEM_PATH_EXPOSURE_AUDIT.json](../core_import/P69_FILESYSTEM_PATH_EXPOSURE_AUDIT.json)
- [P71_SOURCE_RUNTIME_SOURCE_PACKS_DEEP_AUDIT.json](../core_import/P71_SOURCE_RUNTIME_SOURCE_PACKS_DEEP_AUDIT.json)
- [P73_AGENTS_COMPLEMENTARY_RECONCILIATION.json](../core_import/P73_AGENTS_COMPLEMENTARY_RECONCILIATION.json)
- [P75_RUNTIME_CORE_RISK_REVIEW.json](../core_import/P75_RUNTIME_CORE_RISK_REVIEW.json)
- [P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT.json](../core_import/P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT.json)
- [P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT.json](../core_import/P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT.json)
- [P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT.md](../core_import/P79_RSSI_EVIDENCE_PACK_GITHUB_SECURITY_AUDIT.md) — P79 — RSSI Evidence Pack and GitHub Security Audit
- [P80_FULL_REGRESSION_FREEZE.json](../core_import/P80_FULL_REGRESSION_FREEZE.json)
- [P80_FULL_REGRESSION_FREEZE.md](../core_import/P80_FULL_REGRESSION_FREEZE.md) — P80 — Full Regression Freeze
- [POST_P80_HARDENING_DEVIATION_REVIEW.json](../core_import/POST_P80_HARDENING_DEVIATION_REVIEW.json)

**`docs/freeze/`** · *dossier lu par du code : ne pas déplacer*

- [FULL_STACK_FREEZE_MANIFEST_V0.md](../freeze/FULL_STACK_FREEZE_MANIFEST_V0.md) — FULL_STACK_FREEZE_MANIFEST_V0
- [OS3_TICKET_BUILDER_V0_REPORT.md](../freeze/OS3_TICKET_BUILDER_V0_REPORT.md) — OS3_TICKET_BUILDER_V0_REPORT
- [P80_FULL_REGRESSION_FREEZE_LEDGER.md](../freeze/P80_FULL_REGRESSION_FREEZE_LEDGER.md) — P80 — Full Regression Freeze Ledger
- [PERIPHERY_READONLY_STACK_V0_REPORT.md](../freeze/PERIPHERY_READONLY_STACK_V0_REPORT.md) — PERIPHERY_READONLY_STACK_V0_REPORT
- [RECURSIVE_MANIFEST_REPORT.md](../freeze/RECURSIVE_MANIFEST_REPORT.md) — Recursive Manifest Report — V5A
- [V5A_DEMO_DECOUPLING_REPORT.md](../freeze/V5A_DEMO_DECOUPLING_REPORT.md) — V5A Demo Decoupling Report
- [V5A_FREEZE_CANDIDATE_REPORT.md](../freeze/V5A_FREEZE_CANDIDATE_REPORT.md) — V5A Freeze Candidate Report
- [V5A_PROTECTED_FILES_REPORT.md](../freeze/V5A_PROTECTED_FILES_REPORT.md) — V5A Protected Files Report
- [V5A_SINGLE_REPO_COMPLETION_REPORT.md](../freeze/V5A_SINGLE_REPO_COMPLETION_REPORT.md) — V5A Single Repo Completion Report
- [V5A_SINGLE_REPO_REALITY_REPORT.md](../freeze/V5A_SINGLE_REPO_REALITY_REPORT.md) — V5A Single Repo Reality Report
- [V5A_TEST_RESULTS.md](../freeze/V5A_TEST_RESULTS.md) — V5A Test Results
- [V5A_ZIP_CONTENT_AUDIT.md](../freeze/V5A_ZIP_CONTENT_AUDIT.md) — V5A Zip Content Audit
- [V5B_FINAL_BACKEND_BINDING_REPORT.md](../freeze/V5B_FINAL_BACKEND_BINDING_REPORT.md) — V5B Final Backend Binding Report
- [V5B_P0_RUNTIME_AUDIT_REPORT.md](../freeze/V5B_P0_RUNTIME_AUDIT_REPORT.md) — V5B P0 Runtime Audit Report

**`docs/source_packs/`** · *dossier lu par du code : ne pas déplacer*

- [CORPUS_MAP_V4_20260602.csv](../source_packs/CORPUS_MAP_V4_20260602.csv)

</details>

<details><summary><b>Rapports de phases passées</b> (13)</summary>

**`docs/`**

- [REPO_HYGIENE_FREEZE_20260506.md](../REPO_HYGIENE_FREEZE_20260506.md) — REPO HYGIENE FREEZE — 2026-05-06

**`docs/core_import/`** · *dossier lu par du code : ne pas déplacer*

- [P57_CORE_TO_PROOF_IMPORT_PLAN.md](../core_import/P57_CORE_TO_PROOF_IMPORT_PLAN.md) — P57 — CORE TO PROOF IMPORT PLAN
- [P58_CORE_IMPORT_TRIAGE_OPERATIONAL_PATH_AWARE.md](../core_import/P58_CORE_IMPORT_TRIAGE_OPERATIONAL_PATH_AWARE.md) — P58 — Core Import Triage Operational Path-Aware
- [P59_SAFE_BATCH_1_IMPORT.md](../core_import/P59_SAFE_BATCH_1_IMPORT.md) — P59 — Safe Batch 1 Import
- [P60_TEST_BATCH_2_IMPORT.md](../core_import/P60_TEST_BATCH_2_IMPORT.md) — P60 — Test Batch 2 Import
- [P64_FUSION_CONTINUITY_LEDGER.md](../core_import/P64_FUSION_CONTINUITY_LEDGER.md) — P64 — Fusion Continuity Ledger
- [P75_RUNTIME_CORE_RISK_REVIEW.md](../core_import/P75_RUNTIME_CORE_RISK_REVIEW.md) — P75 — Runtime Core Risk Review
- [P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT.md](../core_import/P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT.md) — P78 — Presentation Proof Public Private Split
- [POST_P80_HARDENING_DEVIATION_REVIEW.md](../core_import/POST_P80_HARDENING_DEVIATION_REVIEW.md) — Post-P80 Hardening — Deviation Review

**`docs/freeze/`** · *dossier lu par du code : ne pas déplacer*

- [P80_LOCAL_FREEZE_LIMITS.md](../freeze/P80_LOCAL_FREEZE_LIMITS.md) — P80 — Local Freeze Limits
- [P80_PUBLICATION_BLOCKERS.md](../freeze/P80_PUBLICATION_BLOCKERS.md) — P80 — Publication Blockers

**`docs/status/`** · *dossier lu par du code : ne pas déplacer*

- [P1_FREEZE_NOTE.md](../status/P1_FREEZE_NOTE.md) — Note de gel P1
- [PUBLIC_DOC_SURFACE_FREEZE_20260526.md](../status/PUBLIC_DOC_SURFACE_FREEZE_20260526.md) — PUBLIC DOC SURFACE FREEZE — 2026-05-26

</details>

## Fichiers liés au code

72 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
