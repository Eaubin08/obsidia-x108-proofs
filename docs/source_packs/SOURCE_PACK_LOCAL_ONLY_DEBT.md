# Source Pack Local-Only Debt

**Généré :** 2026-06-03  
**Palier :** P30 — Source Pack Canonization  
**Statut global :** P30_LOCAL_SOURCE_DEBT_DOCUMENTED

Ce document inventorie les artefacts locaux qui ne sont pas commités ou qui représentent des dettes d'intégration pour les paliers futurs.

---

## 1. Corpus Map — local-only

| Artefact | Chemin | Statut git | Risque | Action recommandée |
|----------|--------|-----------|--------|-------------------|
| Corpus Map V4 | `OBSIDIA_CANONICAL_COMPONENT_CORPUS_MAP_V4_20260602_130452.csv` | `??` non suivi | MEDIUM — référence canonique perdue si dossier effacé | Committer dans `docs/source_packs/` ou `_source_discovery/` au palier P31 |
| Registry V2 | `OBSIDIA_COMPONENT_GROUP_REGISTRY_20260602_125346.csv` | `??` non suivi | LOW — version intermédiaire | Archiver ou ignorer |
| Registry Group V2 | `OBSIDIA_COMPONENT_GROUP_REGISTRY_V2_20260602_125604/` | `??` non suivi | LOW | Archiver |
| Registry Split V3 | `OBSIDIA_COMPONENT_SPLIT_V3_20260602_125929/` | `??` non suivi | LOW | Archiver |

---

## 2. Source Discovery — local-only

| Artefact | Chemin | Statut git | Risque |
|----------|--------|-----------|--------|
| P24 Coverage Repair | `_source_discovery/P24_SOURCE_PACK_COVERAGE_REPAIR_20260603/` | `??` non suivi | LOW — audit intermédiaire |
| F03/F06/F07/F10 audits | `_source_discovery/F03_*/F06_*/F07_*/F10_*/` | `??` non suivi | LOW — audits de canon repair |
| F78B Deep Diff | `_source_discovery/F78B_SOURCE_PACKS_DEEP_DIFF_AUDIT_20260602_132021/` | `??` non suivi | MEDIUM — audit de référence utile |
| F78C XLSX Reconciliation | `_source_discovery/F78C_XLSX_IMPLEMENTATION_PLAN_RECONCILIATION_20260602_133600/` | `??` non suivi | LOW |
| Invariant Graph Audit | `_source_discovery/OBSIDIA_INVARIANT_GRAPH_AUDIT_V1/` | `??` non suivi | LOW |

---

## 3. _freezes — local-only (intentionnel)

| Freeze | Chemin | Contenu |
|--------|--------|---------|
| Plan3 contracts docs | `_freezes/PLAN3_RUNTIME_CONTRACTS_DOCS_FREEZE_V1_*` | Contracts/docs freezes |
| Post-merge V012 | `_freezes/POST_MERGE_V012_DRYRUN_PREVIEW_READY_20260603_111027/` | Dryrun state post-merge |
| Post-import runtime | `_freezes/POST_IMPORT_RUNTIME_CONTRACTS_DOCS_FREEZE_V1_*` | State post-import |
| Core registry backups | `_freezes/local_backups_core_registry_20260603_072326/` | Registry backup |
| Test conscience backups | `_freezes/local_backups_test_conscience_20260603_072619/` | Tests backup |
| P30 canonization | `_freezes/P30_SOURCE_CANONIZATION_<timestamp>/` | Snapshot P30 (créé par P30) |

**Politique :** `_freezes/` est intentionnellement local-only. Ne jamais committer dans cette branche.

---

## 4. NPL — dette résolue en P30

| État avant P30 | État après P30 |
|---------------|----------------|
| Directory dans Downloads, status FOUND_DOWNLOADS | Zip canonique dans `_source_packs/raw/`, status FOUND_LOCAL |
| Fragile si Downloads effacé | Stable dans le repo |
| Resolver hardcodé Downloads | Resolver P30 : zip local prioritaire, Downloads fallback |

✓ Dette NPL soldée par P30.

---

## 5. Packs sans zip dédié

### COMPLIANCE_DATA_GOVERNANCE
- **Statut :** Famille extraite de 3 packs RSSI (RGPD, Security, External Signals)
- **Impact :** Comportement acceptable pour P26-P30. Disponible via les packs RSSI.
- **Risque :** Si les 3 packs RSSI sont retirés, COMPLIANCE disparaît.
- **Action P31+ :** Créer un pack dédié `OBSIDIA_COMPLIANCE_DATA_GOVERNANCE_PACK_V1.zip` si nécessaire.

---

## 6. OS Trad / Reverse OS — bloqué

- **Statut :** Pas de source pack dédié. Architecture documentée mais pas de zip candidat.
- **Chemin envisagé :** `OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FINAL.zip` (présent dans Downloads)
- **Taille :** 4 157 886 B
- **Risque :** Import non validé. Contenu non audité pour .py / extraction.
- **Action P31+ :** Auditer le zip, décider famille (nouveau ou ATLAS), ajouter au registry.

---

## 7. Critical Worlds — spec-only, no pack

- **Statut :** Famille documentée dans le backlog XLSX mais aucun zip source.
- **Action P31+ :** Si le pack existe dans Downloads, l'identifier et l'auditer avant intégration.

---

## 8. Source packs dans _runtime_wiring_preflight — local-only

| Fichier | Statut |
|---------|--------|
| `_runtime_wiring_preflight/FULL_SERVER_MATRIX_REGRESSION_AUDIT.md` | local audit |
| `_runtime_wiring_preflight/MATRIX_API_8014_PREVIEW_RESPONSE.json` | local snapshot |
| `_runtime_wiring_preflight/MATRIX_OBSIDIASHELL_8011_STATUS.json` | local snapshot |
| `_runtime_wiring_preflight/MATRIX_VITE_5173_INDEX.html` | local snapshot |

Ces fichiers sont des snapshots de test d'intégration locaux. Non commités, non critiques.

---

## Priorités pour P31+

1. **COMPLIANCE pack dédié** si les entrées RSSI ne suffisent plus
2. **Corpus Map V4 commité** dans `docs/source_packs/` (référence canonique)
3. **OS Trad audit** du zip MMONDE_REVERSE_OS
4. **_source_discovery/ F78B** commité (audit utile pour la traçabilité)
5. **Critical Worlds** — identifier le pack source si disponible
