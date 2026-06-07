# P77 — Canon Wording Targeted Cleanup

**Audit ID :** P77  
**Statut :** `P77_CANON_WORDING_TARGETED_CLEANUP_READY`  
**Mode :** `PATCH_CONTROLLED_TARGETED_DOCS_ONLY` — uniquement termes non justifiés dans docs/ git-trackées  
**Branche :** `p77-canon-wording-targeted-cleanup`  
**Date :** 2026-06-07

---

## 1. Verdict court

| Métrique | Valeur |
|---|---:|
| Fichiers git-trackés scannés | 14 entrées |
| Fichiers patchés | 2 |
| Remplacements appliqués | 15 occurrences |
| REPLACED | 3 entrées |
| WORDING_JUSTIFIED_BY_PROOF | 3 entrées |
| WORDING_TECHNICAL_TERM_KEEP | 3 entrées |
| WORDING_EXPRESSION_STANDARD_KEEP | 1 entrée |
| WORDING_TECHNICAL_LABEL_KEEP | 1 entrée |
| WORDING_FILENAME_REFERENCE_KEEP | 1 entrée |
| PROTECTED_BY_P77_RULES | 1 entrée |
| P76_BOM_NORMALIZATION_SAFE | 1 entrée |
| sigma/ modifié | NON |
| runtime modifié | NON |
| Réseau appelé | NON |
| localhost appelé | NON |
| ACT activé | NON |

**Conclusion principale :**  
Deux fichiers docs git-trackés contenaient des termes d'action (`REGROUP_CANON`, `KEEP_CANON`) sans ancrage hash/tag/freeze. Ces 15 occurrences ont été remplacées par des termes plus précis. Toutes les autres occurrences de `canonical`, `locked`, `official`, `freeze` dans le repo sont soit justifiées par une preuve réelle, soit des identifiants techniques, soit protégées par les règles P77.

---

## 2. Patches appliqués

### 2.1 `docs/source_packs/CORPUS_MAP_V4_20260602.csv`

| Terme | Occurrences | Remplacement | Justification |
|---|---:|---|---|
| `REGROUP_CANON` | 13 | `REGROUP_CANDIDATE` | Aucun hash/tag/freeze ne justifie CANON. Terme action colonne CSV. |
| `KEEP_CANON` | 1 | `KEEP_CORE_OR_OFFICIAL_REVIEW` | Aucun hash/tag/freeze ne justifie CANON pour CORE_AUTHORITY. |

**Total : 14 remplacements** dans ce fichier.

Lignes concernées (action column) :
- `REGROUP_CANDIDATE` : MMONDE_REVERSE_OS_34ARBRES (9 sous-groupes) + OBSIDIA_V4_STRUCTURED_FULL (4 sous-groupes)
- `KEEP_CORE_OR_OFFICIAL_REVIEW` : CORE_AUTHORITY / X108_KX108

### 2.2 `docs/source_packs/CORPUS_MAP_V4_CANON_STATUS.md`

| Terme | Ligne | Remplacement |
|---|---:|---|
| `KEEP_CANON` | 38 | `KEEP_CORE_OR_OFFICIAL_REVIEW` |

Tableau d'exemple mis à jour pour refléter la valeur CSV corrigée.

---

## 3. Termes justifiés — inchangés

| Fichier | Terme | Occurrences | Justification |
|---|---|---:|---|
| `README.md` | `canonical` | 4 | Tag git `p1-freeze-2026-04-22` — gel P1 réel |
| `docs/LIMITS.md` | `canonical` | 2 | Tag git `p1-freeze-2026-04-22` — référence freeze P1 |
| `docs/BANK_SCENARIOS.md` | `canonical` | 1 | Palier P2 réel commité — scénarios bancaires P2 |

Règle appliquée : *"Les termes 'canonical' sont autorisés si hash/tag/commit/freeze/test le justifie."*

---

## 4. Termes techniques — inchangés

| Fichier | Terme | Catégorie | Raison |
|---|---|---|---|
| `docs/GLOSSAIRE.md` | `Chaîne Canonique` | `WORDING_TECHNICAL_TERM_KEEP` | Pipeline cognitif 5 étapes — identifiant fondamental |
| `docs/architecture/OBSIDIA_F60_SIGMA_REGISTRY_CANONICAL_DOMAINS.md` | `canonical domains` | `WORDING_TECHNICAL_TERM_KEEP` | Identifiants techniques Sigma (bank/trading/ecom/gps) dans le code |
| `docs/architecture/F74_F77_FINALIZATION_AUDIT.md` | `canonicalize_preserves_nonneg` | `WORDING_TECHNICAL_TERM_KEEP` | Nom de theorem Lean `TemporalBridge.lean` — preuve formelle |
| `docs/V3_V4_GAP_ANALYSIS.md` | `DOC-CANON` | `WORDING_TECHNICAL_LABEL_KEEP` | Étiquette de catégorie dans gap analysis — pas une affirmation de gel |
| `docs/BANK_OUTPUTS.md` | `canonical interpretation` | `WORDING_EXPRESSION_STANDARD_KEEP` | Expression standard pour "interprétation de référence" — doc lecture sorties |
| `docs/GENCOIN_SANDBOX_INGESTION_REPORT.md` | `GENCOIN_CANON.md` | `WORDING_FILENAME_REFERENCE_KEEP` | Référence à un nom de fichier existant |

---

## 5. Fichiers protégés — non touchés

| Périmètre | Règle |
|---|---|
| `sigma/` | PROTECTED_BY_P77_RULES |
| `runtime_wiring/` | PROTECTED_BY_P77_RULES |
| `apps/obsidia_api/routes/` | PROTECTED_BY_P77_RULES |
| `apps/obsidia_api/*.py` | PROTECTED_BY_P77_RULES |
| `connectors/` | PROTECTED_BY_P77_RULES |
| `periphery/` | PROTECTED_BY_P77_RULES |
| `proofs/V18_3_1/`, `proofs/lean/` | PROTECTED_BY_P77_RULES |
| `_tmp_core_import/`, `_source_packs/`, `_freezes/` | PROTECTED_BY_P77_RULES |
| `.local_audits/` (CANON_LOCKED × 4) | PROTECTED_BY_P77_RULES |
| `audit/world_action_bus.jsonl` | PROTECTED_BY_P77_RULES |
| `proofs/PROOFKIT_REPORT.json` | PROTECTED_BY_P77_RULES |

---

## 6. P76 BOM — classification

`sigma/examples/gps_omega_chaos.json` — correction BOM UTF-8 (`﻿`) appliquée en P76.  
**Ne pas requalifier comme mutation runtime. Classé : `P76_BOM_NORMALIZATION_SAFE`.**

---

## 7. Règles P77 appliquées

| Règle | Statut |
|---|:---:|
| Pas de réécriture globale | RESPECTÉ |
| Pas de reformulation large | RESPECTÉ |
| Pas de changement technique | RESPECTÉ |
| Pas de suppression de preuves | RESPECTÉ |
| Fichiers générés anciens utiles historiquement — non corrigés | RESPECTÉ |
| Docs P56→P76 avec commit/test réel — gardés | RESPECTÉ |
| Claims publics plus prudents que claims internes | RESPECTÉ |
| Termes autorisés si hash/tag/commit/freeze/test le justifie | RESPECTÉ |

---

## 8. Contraintes P75/P76 héritées

| Contrainte héritée | Application P77 |
|---|---|
| `BLOCK_RUNTIME_IMPORT_PERMANENT` (P75) | engine/ non modifié |
| `GPS_TERRAIN_SEPARATED` (P76) | sigma/ non modifié |
| `P76_BOM_NORMALIZATION_SAFE` (P76) | gps_omega_chaos.json — correction BOM P76 uniquement |
| `CONNECTORS_DO_NOT_RUN` (P76) | aviation_robo.py, bank_normal_flow.py, trading_live.py — intacts |

---

## 9. Findings

| ID | Type | Composant | Action |
|---|---|---|---|
| P77-F1 | PATCH_APPLIED | docs/source_packs/CORPUS_MAP_V4_20260602.csv | REPLACED_UNJUSTIFIED_WORDING (14 occurrences) |
| P77-F2 | PATCH_APPLIED | docs/source_packs/CORPUS_MAP_V4_CANON_STATUS.md | REPLACED_UNJUSTIFIED_WORDING (1 occurrence) |
| P77-F3 | WORDING_JUSTIFIED_BY_PROOF | README.md | KEEP_JUSTIFIED (tag p1-freeze-2026-04-22) |
| P77-F4 | WORDING_TECHNICAL_TERM_KEEP | docs/GLOSSAIRE.md + docs/architecture/OBSIDIA_F60_* | KEEP_TECHNICAL |
| P77-F5 | P76_BOM_NORMALIZATION_SAFE | sigma/examples/gps_omega_chaos.json | CLASSIFIED_P76_BOM_SAFE |

---

## 10. Décision

P77 conclut que **15 occurrences de termes non justifiés ont été corrigées** dans 2 fichiers docs git-trackés.

- **Patches appliqués** : `REGROUP_CANON` → `REGROUP_CANDIDATE` (13×), `KEEP_CANON` → `KEEP_CORE_OR_OFFICIAL_REVIEW` (2×).
- **Termes justifiés conservés** : README.md et LIMITS.md (`canonical` ancré sur tag `p1-freeze-2026-04-22`), BANK_SCENARIOS.md (palier P2 réel).
- **Termes techniques conservés** : `Chaîne Canonique`, `canonical domains` Sigma, `canonicalize_preserves_nonneg` (theorem Lean).
- **Aucune modification** de sigma/, runtime_wiring/, apps/, connectors/, periphery/, proofs/, .local_audits/.
- **P76 BOM** : `gps_omega_chaos.json` correction BOM classée `P76_BOM_NORMALIZATION_SAFE`.

**wording_decision : TARGETED_REPLACEMENT_APPLIED**

**Prochain geste : P78 — Presentation Proof Public Private Split.**

---

**Verdict :** `P77_CANON_WORDING_TARGETED_CLEANUP_READY`
