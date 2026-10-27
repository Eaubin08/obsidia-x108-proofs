# 08_GAP_REPORT_V1_VS_V2_FIXED_CLEAN — Comparaison V1 vs V2 (V2.1 clean patch)

**Correction V2.1** : Formule BRODY_ONLY corrigée — CANON 11→27, total 756→772  
**Clean patch** : Suppression du décompte de lignes CSV fragile — remplacé par description non-fragile  
**Résultat** : GRAND_TOTAL 4337→4353 ✓

---

## Résumé de l'écart V1 vs V2 (corrigé)

| Indicateur | V1 | V2.1 (corrigé) | Écart |
|---|---|---|---|
| Structure du ledger | 210 lignes composants/paliers | AGGREGATE_RECONCILED_LEDGER (voir ci-dessous) | V1 = non réconciliée à 4353 |
| Items audit V4 couverts | 210 / 4353 | **4353 / 4353** | +4143 items réconciliés |
| Formule Brody-only | absente | **96+36+24+18+9+35+25+27+2+45+11+17+354+73 = 772** ✓ | Corrigée V2.1 |
| Grand total validé | non | **61+772+204+3316 = 4353** ✓ | Corrigé V2.1 |
| Verdict | DESTINATION_MAP_V1_READY | **RECONCILED_4353_OK** | V2.1 est la référence |

**Structure du ledger V2.1** : Le ledger V2.1 est un AGGREGATE_RECONCILED_LEDGER — il ne contient pas 4353 lignes item-level, mais des lignes agrégées famille × statut + lignes de vérification, dont les compteurs réconcilient exactement 4353 items (61+772+204+3316=4353 ✓).

---

## Formule BRODY_ONLY — correction explicite

| Version | Formule | Total | Statut |
|---|---|---|---|
| V2 originale (fausse) | 96+36+24+18+9+35+25+**11**+2+45+11+17+354+73 | **756** | ❌ FAUX |
| V2.1 corrigée | 96+36+24+18+9+35+25+**27**+2+45+11+17+354+73 | **772** | ✓ CORRECT |

**Source** : Audit V4 page 5 — ligne CANON, colonne "Brody seul" = 27

---

## Défauts V1 corrigés dans V2 / V2.1

### Défaut 1 — Ledger V1 = 210 lignes non liées à 4353
**V1** : 210 lignes composants/paliers — total 4353 jamais réconcilié  
**V2.1** : AGGREGATE_RECONCILED_LEDGER — lignes agrégées famille × statut + lignes de vérification → 4353 ✓

### Défaut 2 — 772 Brody-only compressés en 6 composants
**V1** : 6 familles/composants haut niveau, aucun item nommé  
**V2.1** : 14 familles, CANON=27 (corrigé), items nommés pour MODULES/LOIS/ARBRES/AGENTS

### Défaut 3 — 3316 non branchés absents de V1
**V1** : terme "non branché" absent  
**V2.1** : table 14 familles, vérification 3316 ✓, items nommés pour 5 petites familles

### Défaut 4 — 204 partiels en 1 ligne V1
**V1** : 1 mention sans détail  
**V2.1** : 5 familles + 4 catégories (BRODY_RUNTIME_ONLY/API_RUNTIME_ONLY/DOMAIN_RUNTIME_MISSING/KERNEL_RUNTIME_MISSING) → 204 ✓

### Défaut 5 — 61 OK non détaillés V1
**V1** : 1 mention globale  
**V2.1** : 14 familles, 10 agents nommés, 51 aggregate ITEM_LEVEL_NOT_AVAILABLE_IN_SOURCE_PDF

---

## Ce que V1 reste valide pour (inchangé)

- Vue macro composants-fichiers-paliers (210 lignes P0→P8)
- Règles DO_NOT_CONNECT_NOW
- Phases de connexion séquencées
- Vue executive des 14 familles

**V2.1 complète V1 — elle ne la remplace pas.**

---

## Table de concordance V1 ↔ V2.1

| Fichier V1 | Équivalent V2.1 | Couverture |
|---|---|---|
| 01_BRODY_ONLY_MACHINATION.md | 02_BRODY_ONLY_772_RECONCILIATION_FIXED_CLEAN.md | 14 familles, CANON=27 corrigé |
| 09_DESTINATION_LEDGER.csv | 07_EXHAUSTIVE_DESTINATION_LEDGER_FIXED.csv | AGGREGATE_RECONCILED_LEDGER, 4353 ✓ |
| 10_EXECUTIVE_STATUS_TABLE.md | 01_AUDIT_TOTAL_RECONCILIATION_FIXED_CLEAN.md | 3 tables vérification |
| 11_NEXT_ACTION_AFTER_MAP.md | 06_DOMAIN_TARGET_EXPANSION_PLAN.md | Plan chiffré |
| (absent V1) | 03_NON_BRANCHES_3316_RECONCILIATION.md | 3316 non branchés |
| (absent V1) | 04_PARTIEL_RUNTIME_204_RECONCILIATION.md | 204 partiels |
| (absent V1) | 05_OK_61_BRODY_DOMAIN_RECONCILIATION.md | 61 OK |
| (absent V1) | 10_ARITHMETIC_VALIDATION_V2_1.md | Formules ligne par ligne |

---

## Verdict

- **V1 insuffisante pour réconciliation 4353** : OUI
- **V2 avait erreur CANON Brody-only** : OUI (11 au lieu de 27)
- **V2.1 corrige l'erreur** : OUI
- **Verdict V2.1** : **RECONCILED_4353_OK**
