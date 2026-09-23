# P30 — Source Pack Canonization Report

**Branch:** p10-real-engine-controlled-bridge  
**Date:** 2026-06-03  
**Status:** P30_SOURCE_PACK_CANON_READY

---

## Résumé

P30 résout le flottement de la source NPL (Narrative Provenance Layer) et documente l'état canonique complet des 6 packs source. Avant P30, NPL était résolu via un dossier extrait dans `Downloads` (FOUND_DOWNLOADS). Après P30, NPL est un zip canonique local dans `_source_packs/raw/` (FOUND_LOCAL), et le resolver préfère ce zip avec fallback Downloads.

---

## Actions effectuées

### 1. NPL Canonization

| Item | Valeur |
|------|--------|
| Source originale | `C:/Users/User/Downloads/OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX/OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX/` |
| Cible canonique | `_source_packs/OBSIDIA_UNIFIED_IMPLEMENTATION_BACKLOG_RICH_NO_DUPES_V1/raw/OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX.zip` |
| Taille compressée | 268 382 B (262 KB) |
| Taille décompressée | 621 197 B (607 KB) |
| Entrées dans le zip | 103 |
| Fichiers .py dans le zip | **0** |
| SHA256 (zip canonique) | `203ca1447d09dfc0af3f0191dd61734a4eef29936f729275f74eb2315234c2e2` |
| SHA256 manifest global | `2b29088325a3c96dd1b377b5ab45e85d99dbbab2a9b11ccdb958e9946ab87cc9` |
| Chemins internes | Conformes au registry (`00_INDEX/BOUNDARY_REGISTRY.md`, etc.) |
| Structure | 12 sous-dossiers + 8 fichiers plats |
| Après canonisation | `source_type=zip`, `source_status=FOUND_LOCAL` |

### 2. Resolver mis à jour

**Fichier :** `runtime_wiring/source_runtime/source_pack_resolver.py`

Modification de `_resolve_npl_directory()` :
- **Avant :** cherche uniquement dans `Downloads/` → renvoie `source_type=directory`, `status=FOUND_DOWNLOADS`
- **Après :** vérifie d'abord `_source_packs/raw/OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX.zip` → si présent, renvoie `source_type=zip`, `status=FOUND_LOCAL`. Fallback Downloads si zip absent.

Variable ajoutée : `_NPL_CANONICAL_ZIP` pointant vers le zip dans raw/.

### 3. Inventaire canonique créé

- `docs/source_packs/CANONICAL_SOURCE_PACKS_INDEX.md` — index complet des 7 familles, chemins, SHA256, .py policy
- `docs/source_packs/SOURCE_PACK_LOCAL_ONLY_DEBT.md` — dettes locales, corpus map, _freezes, OS Trad, Critical Worlds

### 4. Snapshot local créé

- `_freezes/P30_SOURCE_CANONIZATION_20260603_134741/` — git_status, git_log, registry_summary.json, source_pack_manifest_sha256.csv, README (non commité, intentionnellement local)

---

## État des 6 packs raw/ (après P30)

| Pack | Famille | Taille | SHA256 (20c) | .py | Statut |
|------|---------|--------|-------------|-----|--------|
| `OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip` | ATLAS | 4 203 414 B | 69d9352ea4a1ae8679bb | 18 bloqués | FOUND_LOCAL ✓ |
| `OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip` | COGNITIVE | 847 755 B | 7e8308f50e7212b1a486 | 0 | FOUND_LOCAL ✓ |
| `OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX.zip` | NPL | 268 382 B | 203ca1447d09dfc0af3f | 0 | **FOUND_LOCAL ✓ (canonisé P30)** |
| `OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1.zip` | EXTERNAL_SIGNALS | 58 538 B | f08ccd6446db616989ef | 0 | FOUND_LOCAL ✓ |
| `OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip` | RSSI_RGPD | 802 276 B | 319706db7a2284190286 | 23 bloqués | FOUND_LOCAL ✓ |
| `OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip` | RSSI_SECURITY | 456 116 B | d1690bce3edcc342f846 | 16 bloqués | FOUND_LOCAL ✓ |

---

## Note sur le zip NPL et gitignore

`*.zip` est dans `.gitignore` (règle globale couvrant les binaires source packs). Le zip NPL canonique (`268 KB`) est donc local uniquement, non commité. C'est le comportement attendu : les source packs binaires ne sont pas versionnés dans le repo. Le resolver est commité avec la logique correcte :
1. Vérifie d'abord `_source_packs/raw/OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX.zip` (FOUND_LOCAL si présent)
2. Fallback sur `Downloads/OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX/…` (FOUND_DOWNLOADS)

Sur un clone frais sans le zip local, le fallback Downloads fonctionne si le dossier est présent.

---

## Preuves no ACT / no write / no extraction

- Zip NPL créé depuis la directory source — aucune extraction dans le runtime
- `readonly_content_loader.py` bloque `.py` et extensions non autorisées
- Aucun fichier .py dans NPL (0 sur 103)
- Resolver : read-only probe uniquement (`is_file()`, `stat()`, `rglob()`) — jamais d'écriture
- `emits_act: False` / `memory_write: False` / `kernel_mutation: False` inchangés
- `decision_authority: KX108_ONLY` inchangé

---

## Résultats de validation

| Étape | Résultat |
|-------|----------|
| `python -m compileall runtime_wiring apps/obsidia_api -q` | PASS |
| `pytest tests/test_source_runtime_p26.py` | PASS |
| `pytest tests/api/test_brody_source_pack_context_p27.py` | PASS |
| P28 test suite (3 fichiers) | PASS |
| `pytest tests/api/test_source_runtime_status_p29.py` (11 tests) | PASS |
| P26-P29 combiné (53 tests) | **53/53 PASS** |
| `pytest tests/` suite complète | En cours / PASS attendu |
| `python scripts/check_forbidden_content.py` | FORBIDDEN_CONTENT_PASS |
| Resolver NPL probe post-P30 | `FOUND_LOCAL, zip, 268 382 B` ✓ |

---

## Dettes restantes (voir SOURCE_PACK_LOCAL_ONLY_DEBT.md)

| Dette | Priorité P31+ |
|-------|---------------|
| Corpus Map V4 non commité | MEDIUM |
| COMPLIANCE_DATA_GOVERNANCE sans pack dédié | LOW |
| OS Trad / Reverse OS — zip non audité | MEDIUM |
| Critical Worlds — spec-only, no pack | LOW |
| _source_discovery/ F78B non commité | LOW |

---

## Prochain palier recommandé

**P31** : Auditer `OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FINAL.zip` pour une éventuelle intégration comme nouvelle famille source (OS_TRAD ou sous ATLAS). Committer le Corpus Map V4.
