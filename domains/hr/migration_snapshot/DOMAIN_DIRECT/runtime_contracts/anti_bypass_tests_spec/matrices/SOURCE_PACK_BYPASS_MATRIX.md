# SOURCE_PACK_BYPASS_MATRIX
# runtime_contracts/anti_bypass_tests_spec/matrices/
# Plan 3 P4 — Matrice documentaire bypass source packs — NO TEST EXECUTION
# Date: 2026-06-02
# import_allowed_now: false — TOUTES LES LIGNES (sauf External Signals F04 déjà fait)

---

## Règle

```
import_allowed_now = false pour tous les packs non encore passés F03/F06/F07/F10
runtime_allowed_now = false pour tous les packs
Aucun pack ne peut bypasser X108 même après import
```

---

## Matrice

| Source | Current status | Bypass risk | Boundary | Required future test | Import allowed now? | Notes |
|--------|---------------|-------------|----------|---------------------|--------------------|-|
| External Signals (RSSI_EXT) | SPEC_IMPORTED (F04) — 27/41 fichiers dans specs/ | LOW — déjà en advisory | EXTERNAL_SIGNALS_SIGNAL_ONLY | TB-17, TB-20, TB-43, TB-57 | PARTIAL (F04 done) — merger appendices pending | Temporal advisory uniquement. Jamais autorité décision. |
| NPL | SPEC_IMPORTED (F04) — specs/12/ (34 fichiers) | LOW — advisory importé | NPL_ADVISORY_ONLY | TB-21, TB-22, TB-14 | SPEC_IMPORTED (advisory) — pas de runtime | Jamais verdict final. Jamais diagnostic. |
| Audio/Entropy | SPEC_CANDIDATE — specs/03_ENTROPY_DISCIPLINE/ | MEDIUM — claim scope risk | AUDIO_ENTROPY_ADVISORY_ONLY | TB-25, TB-18 | ADVISORY SPEC seulement | source_partial — not physical law certified |
| P107/P161 | PYTHON_SPEC_NOT_LEAN_PROVEN — specs/03/ | MEDIUM — claim de preuve Lean | P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY | TB-23, TB-24 | PYTHON_SPEC (advisory) — pas Lean | Jamais LEAN_PROVEN claim. Jamais autorité runtime. |
| Graphiti | READONLY — periphery (runtime existant) | MEDIUM — écriture possible | READONLY_CONTEXT_ONLY | TB-09, TB-15, TB-35 | N/A — existant readonly | Corpus Brody absent de V20. Écriture interdite. |
| Brody | READONLY — periphery (runtime existant) | MEDIUM — écriture possible | READONLY_CONTEXT_ONLY | TB-10, TB-16, TB-35 | N/A — existant readonly | Écriture interdite. Contexte uniquement. |
| Cognitive Reintegration | COPIED_READONLY — _source_packs/raw/ — 519 fichiers | HIGH — 0 .py mais runtime claim risk | COGNITIVE_REINTEGRATION_ADVISORY_ONLY | TB-26, TB-27, TB-28, TB-55 | false — F78B ✅ + F07 required | Pack le plus propre. Advisory uniquement. |
| Branchable Atlas | COPIED_READONLY — _source_packs/raw/ — 1738 fichiers | HIGH — 18 .py + .runtime_freezes | ATLAS_READONLY_ADVISORY_ONLY | TB-29, TB-30, TB-51, TB-55 | false — F78B ✅ + F06 required | 18 .py + .pytest_cache + .runtime_freezes à exclure. |
| RSSI Security | COPIED_READONLY — _source_packs/raw/ — 167 fichiers | HIGH — 16 .py + certification claim | RSSI_EVIDENCE_ONLY | TB-31, TB-32, TB-47, TB-53 | false — F78B ✅ + F03 required | 16 .py à exclure. Claim RSSI_CERTIFIED interdit. |
| RGPD ISO | COPIED_READONLY — _source_packs/raw/ — 311 fichiers | HIGH — 23 .py + conformité claim | RGPD_COMPLIANCE_SCOPE_GUARD | TB-33, TB-34, TB-48, TB-54 | false — F78B ✅ + F03+F10 required | 23 .py à exclure. Claim ISO_CERTIFIED interdit. |
| XLSX backlog | SOURCE_ONLY — _source_packs/raw/ | MEDIUM — write authority assumption | XLSX_AUDIT_ONLY | TB-52 | false — audit référence uniquement | XLSX = planning uniquement. target_path ≠ autorisation d'écriture. |
| Raw markdowns (4 fichiers "Réponse X/5") | SOURCE_ONLY — _source_packs/raw/ | LOW — descriptions narratives | AUDIT_SOURCE | N/A direct | false — indexation F78B seulement | Descriptions narratives des zips. À renommer/indexer lors F03/F06/F07. |
| .py files from zips | DO_NOT_IMPORT_RUNTIME — dans les zips | CRITICAL — code exécutable | NO_PACKAGES_RUNTIME_BOUNDARY | TB-47, TB-48 | false — DO_NOT_IMPORT absolu | 57 .py total (16+23+18). Jamais dans periphery/ ou runtime. |
| .runtime_freezes (Atlas) | ARCHIVE_ONLY — dans le zip Atlas | HIGH — état runtime figé | ATLAS_READONLY_ADVISORY_ONLY | TB-51 | false — ARCHIVE_ONLY | Snapshots états figés. Jamais dans specs/. |
| .pytest_cache (Atlas) | QUARANTINE — dans le zip Atlas | HIGH — artefacts pytest | NO_PACKAGES_RUNTIME_BOUNDARY | TB-50 | false — QUARANTINE absolu | 20 fichiers. Jamais importés. |

---

## Tests prioritaires par niveau de risque

### CRITICAL (bypass immédiat possible)

| Source | Tests | Gate minimale |
|--------|-------|--------------|
| .py files | TB-47, TB-48 | F78B ✅ + exclusion lors F03/F06 |
| packages/ | TB-49 | NO_PACKAGES invariant |
| .pytest_cache | TB-50 | QUARANTINE absolu |
| Forged DecisionTicket | TB-05, TB-06 | X108_GATEWAY_REQUIRED |

### HIGH (contournement si mal géré)

| Source | Tests | Gate minimale |
|--------|-------|--------------|
| RSSI (16 .py + cert claim) | TB-31, TB-32, TB-53 | F78B + F03 + exclure .py |
| RGPD (23 .py + compliance claim) | TB-33, TB-34, TB-54 | F78B + F03+F10 + exclure .py |
| Atlas (.runtime_freezes + 18 .py) | TB-29, TB-51, TB-55 | F78B + F06 + exclusions |
| Cognitive (runtime claim prématuré) | TB-28 | F78B + F07 |

### MEDIUM (risque si spec mal interprétée)

| Source | Tests | Gate minimale |
|--------|-------|--------------|
| P107/P161 | TB-23, TB-24 | Claim scope lock respecté |
| Audio/Entropy | TB-25 | Advisory uniquement |
| NPL | TB-21, TB-22 | Advisory uniquement |
| Graphiti/Brody | TB-09, TB-10 | Readonly enforced |
| XLSX | TB-52 | Audit référence uniquement |
