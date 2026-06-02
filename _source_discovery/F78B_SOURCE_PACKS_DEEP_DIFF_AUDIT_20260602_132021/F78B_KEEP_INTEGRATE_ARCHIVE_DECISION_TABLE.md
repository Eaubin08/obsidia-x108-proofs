# F78B_KEEP_INTEGRATE_ARCHIVE_DECISION_TABLE
# _source_discovery/F78B_SOURCE_PACKS_DEEP_DIFF_AUDIT_20260602_132021/
# Date: 2026-06-02
# Status: SOURCE_AUDIT_ONLY / READONLY

---

## Table de décision par pack

### Pack 1 — RSSI_EXTERNAL_SIGNALS (OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1.zip)

| Critère | Valeur |
|---------|--------|
| Fichiers total | 41 |
| .py | 0 |
| Dups internes | 0 |
| Déjà extrait | PARTIAL (F04 — 37/41 noms présents localement) |
| Chemin local | specs/external_signals/ |
| Boundary | EXTERNAL_SIGNALS_SIGNAL_ONLY |
| Décision | ALREADY_EXTRACTED_F04 / NO_REIMPORT |
| Next phase | Vérifier les 4 fichiers potentiellement manquants (proof/, tests/, VALIDATION_REPORT) |
| Claim scope | SPEC_IMPORTED — temporal sidecar advisory uniquement |
| Packages risk | AUCUN |
| Python risk | AUCUN |

**Sous-décisions :**
- `component_specs/C459-C482` : KEEP_EXTRACTED (déjà dans specs/)
- `packets/51-53` : KEEP_EXTRACTED (déjà dans specs/)
- `family_specs/46-48` : KEEP_EXTRACTED (déjà dans specs/)
- `merge_appendices/` : VERIFY_LOCAL — potentiellement manquants
- `proof/53_EXTERNAL_SIGNALS_PROOF_ARTIFACTS.md` : VERIFY_LOCAL
- `tests/52_EXTERNAL_SIGNALS_TEST_MATRIX.md` : VERIFY_LOCAL / P4 futur

---

### Pack 2 — RSSI_SECURITY (OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip)

| Critère | Valeur |
|---------|--------|
| Fichiers total | 167 |
| .py | **16 — RISQUE** |
| Dups internes | 0 |
| Déjà extrait | NON |
| Chemin local | — |
| Boundary | RSSI_EVIDENCE_ONLY |
| Décision | INTEGRATE_DOCS_ONLY (F03) — exclure periphery/.py |
| Next phase | F03_RSSI_IMPORT_AUDIT (après F78B validé) |
| Claim scope | EVIDENCE_ONLY / NO_RUNTIME_AUTHORITY |
| Packages risk | periphery/.py → DO_NOT_IMPORT |
| Python risk | HAUTE — 16 .py dans periphery/ |

**Sous-décisions :**
- `docs/` : INTEGRATE_TO_SPECS (F03) — docs RSSI security
- `specs/` : INTEGRATE_TO_SPECS (F03) — specs RSSI security
- `audit/` : INTEGRATE_TO_SPECS (F03) — evidence audit
- `periphery/**/*.py` : **DO_NOT_IMPORT_RUNTIME** (16 fichiers)
- `README.md` : INTEGRATE_RENAMED (prefix RSSI_SEC_)

---

### Pack 3 — RSSI_RGPD_ISO (OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip)

| Critère | Valeur |
|---------|--------|
| Fichiers total | 311 |
| .py | **23 — RISQUE** |
| Dups internes | 8 |
| Déjà extrait | NON |
| Chemin local | — |
| Boundary | RGPD_COMPLIANCE_SCOPE_GUARD |
| Décision | INTEGRATE_DOCS_ONLY (F03 + F10) — exclure periphery/.py + résoudre 8 dups |
| Next phase | F03_RGPD_IMPORT_AUDIT puis F10_COMPLIANCE |
| Claim scope | COMPLIANCE_CLAIM_SCOPE_GUARD — RGPD readiness ≠ conformité légale |
| Packages risk | periphery/.py → DO_NOT_IMPORT |
| Python risk | HAUTE — 23 .py dans periphery/ |

**Sous-décisions :**
- Docs MD : INTEGRATE_TO_SPECS (F03) — docs RGPD/ISO
- Specs : INTEGRATE_TO_SPECS (F03)
- `periphery/**/*.py` : **DO_NOT_IMPORT_RUNTIME** (23 fichiers)
- 8 dups : `RICHER_VERSION_TO_KEEP` — comparer contenu lors F03
- `DPA_TEMPLATE.md` (dup avec RSSI_SEC) : `RICHER_VERSION_TO_KEEP`
- `README.md` : INTEGRATE_RENAMED

---

### Pack 4 — BRANCHABLE_ATLAS (OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip)

| Critère | Valeur |
|---------|--------|
| Fichiers total | 1738 |
| .py | **18 — RISQUE** |
| Dups internes | 92 (snapshots versionnés) |
| Déjà extrait | NON |
| Chemin local | — |
| Boundary | ATLAS_READONLY_ADVISORY_ONLY |
| Décision | SELECTIVE_INTEGRATE_DOCS (F06) — architecture complexe |
| Next phase | F06_ATLAS_IMPORT_AUDIT (après F78B validé) |
| Claim scope | COPIED_READONLY / advisory uniquement |
| Packages risk | periphery/.py → DO_NOT_IMPORT |
| Python risk | HAUTE — 18 .py dans periphery/ + patches/ |

**Sous-décisions :**
- `.pytest_cache/` : **QUARANTINE_DO_NOT_IMPORT** (artefacts pytest)
- `.runtime_freezes/` : **RAW_ARCHIVE_ONLY** (snapshots runtime figés)
- `periphery/**/*.py` : **DO_NOT_IMPORT_RUNTIME**
- `patches/*.py` : **DO_NOT_IMPORT_RUNTIME** (SNIPPET_NOT_APPLIED — mais .py)
- Audit docs MD (FINAL_PASS_AUDIT_V0_7.md, etc.) : INTEGRATE_TO_SPECS (F06)
- Spec MD/JSON : INTEGRATE_TO_SPECS (F06) après sélection
- 92 dups basenames : RAW_ARCHIVE_ONLY pour les snapshots dupliqués

---

### Pack 5 — COGNITIVE (OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip)

| Critère | Valeur |
|---------|--------|
| Fichiers total | 519 |
| .py | **0 — PROPRE** |
| Dups internes | **0 — PROPRE** |
| Déjà extrait | NON |
| Chemin local | — |
| Boundary | COGNITIVE_REINTEGRATION_ADVISORY_ONLY |
| Décision | INTEGRATE_TO_SPECS (F07) — pack le plus propre |
| Next phase | F07_COGNITIVE_IMPORT_AUDIT (après F78B validé) |
| Claim scope | COPIED_READONLY / COGNITIVE_REINTEGRATION_ADVISORY_ONLY |
| Packages risk | AUCUN |
| Python risk | AUCUN |

**Sous-décisions :**
- Fichiers yaml (490) : INTEGRATE_TO_SPECS (F07)
- Docs MD (12) : INTEGRATE_TO_SPECS (F07)
- JSON manifests (8) : INTEGRATE_TO_SPECS (F07)
- SHA256 (1) : KEEP_INTEGRITY_CHECK

**Cognitive = candidat prioritaire pour F07** : structure propre, 0 .py, 0 dups.

---

### XLSX — OBSIDIA_IMPLEMENTATION_PLAN_FILE_BY_FILE_V1.xlsx

| Critère | Valeur |
|---------|--------|
| Type | Tableur binaire |
| Rôle | Backlog file-by-file principal |
| Décision | SOURCE_ONLY — ne pas importer |
| Usage | Référence planning / séquencement |
| Claim scope | BACKLOG_REFERENCE_ONLY |

---

## Synthèse décisions

| Pack | Décision | Gate | .py action |
|------|----------|------|-----------|
| RSSI_EXT | ALREADY_EXTRACTED_F04 | Vérifier 4 manquants | N/A |
| RSSI_SEC | INTEGRATE_DOCS_ONLY | F03 | EXCLUDE periphery/ |
| RSSI_RGPD | INTEGRATE_DOCS_ONLY | F03+F10 | EXCLUDE periphery/ |
| ATLAS | SELECTIVE_INTEGRATE_DOCS | F06 | EXCLUDE periphery/+.pytest_cache+.runtime_freezes |
| COGNITIVE | INTEGRATE_TO_SPECS | F07 | N/A (0 .py) |
| XLSX | SOURCE_ONLY | — | N/A |

---

## Ordre recommandé

```
F07 en premier (Cognitive — le plus simple, 0 .py, 0 dups)
F03 (RSSI + RGPD — résoudre .py + 8 dups avant import)
F06 (Atlas — plus complexe — exclure .py + .pytest_cache + .runtime_freezes)
F10 (RGPD compliance final — après F03)
```
