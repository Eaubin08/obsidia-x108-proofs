# Canonical Source Packs Index

**Generated:** 2026-06-03  
**Palier:** P30 — Source Pack Canonization  
**Registry:** `runtime_wiring/source_registry/source_file_registry.json`  
**Total entries:** 15 298  
**Families:** 7  
**Decision authority:** KX108_ONLY — readonly / no ACT / no extraction / no .py execution

---

## Résumé des 6 packs canoniques locaux

| Pack (zip) | Famille | Taille | Entrées registry | .py dans zip | Chemin canonique | Statut résolveur |
|------------|---------|--------|-----------------|--------------|------------------|-----------------|
| `OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip` | ATLAS | 4 203 414 B | 1 738 (V0.7 only) | 18 (bloqués par loader) | `_source_packs/.../raw/` | FOUND_LOCAL ✓ |
| `OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip` | COGNITIVE_REINTEGRATION | 847 755 B | 513 | 0 | `_source_packs/.../raw/` | FOUND_LOCAL ✓ |
| `OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX.zip` | NARRATIVE_PROVENANCE_LAYER | 268 382 B | 103 | 0 | `_source_packs/.../raw/` **(canonisé P30)** | FOUND_LOCAL ✓ |
| `OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1.zip` | EXTERNAL_SIGNALS | 58 538 B | 41 | 0 | `_source_packs/.../raw/` | FOUND_LOCAL ✓ |
| `OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip` | RSSI_RGPD | 802 276 B | 311 | 23 (bloqués) | `_source_packs/.../raw/` | FOUND_LOCAL ✓ |
| `OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip` | RSSI_SECURITY_PRESENTATION | 456 116 B | 167 | 16 (bloqués) | `_source_packs/.../raw/` | FOUND_LOCAL ✓ |

Chemin canonique complet : `_source_packs/OBSIDIA_UNIFIED_IMPLEMENTATION_BACKLOG_RICH_NO_DUPES_V1/raw/<nom_zip>`

---

## Détail par famille

### ATLAS — 11 263 entrées registry
- **Pack canonique actif :** `OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip`
- **Adapter target :** `atlas_to_context_packet`
- **Boundary :** ALLOW_CONTEXT_ONLY — no ACT — KX108_ONLY
- **Runtime status :** ACTIVE (P26+)
- **SHA256 :** `69d9352ea4a1ae8679bb...` (complet dans `SOURCE_FILES_MANIFEST_SHA256.json`)
- **Note :** 7 versions dans le registry (V0→V0.7). Seul V0.7 est en raw/ — les 6 anciennes versions (V0, V0.1×2, V0.2, V0.3, V0.4) ne sont pas en raw/ mais ATLAS reste disponible via V0.7. Pas de régression runtime.

### COGNITIVE_REINTEGRATION — 2 052 entrées registry
- **Pack canonique actif :** `OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip`
- **Adapter target :** `cognitive_to_context_packet`
- **Boundary :** ALLOW_CONTEXT_ONLY — KX108_ONLY
- **Runtime status :** ACTIVE (P26+)
- **SHA256 :** `7e8308f50e7212b1a486...`
- **Note :** 4 versions dans le registry (V1, V1(1), VERIFIED_FULL(1), final). Seul VERIFIED_FULL(1) en raw/.

### NARRATIVE_PROVENANCE_LAYER — 103 entrées registry
- **Pack canonique actif :** `OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX.zip`
- **Adapter target :** `npl_to_context_packet`
- **Boundary :** ALLOW_CONTEXT_ONLY — KX108_ONLY
- **Runtime status :** ACTIVE (P26+)
- **SHA256 (zip canonique P30) :** `203ca1447d09dfc0af3f0191dd61734a4eef29936f729275f74eb2315234c2e2`
- **Structure interne :** 12 sous-dossiers (00_INDEX, 01_MASTER_SPEC, …, 11_ADVANCED_PROVENANCE) + 8 fichiers plats
- **0 .py dans le zip**
- **Canonisation P30 :** zip créé depuis `Downloads/OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX/OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX/`. Resolver mis à jour pour préférer le zip local.

### RSSI_RGPD — 976 entrées registry
- **Pack canonique actif :** `OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip`
- **Adapter target :** `rssi_rgpd_to_context_packet`
- **Boundary :** ALLOW_CONTEXT_ONLY — KX108_ONLY
- **Runtime status :** ACTIVE (P26+)
- **SHA256 :** `319706db7a2284190286...`
- **Note :** 6 versions dans le registry. Seul V2 en raw/. `.py` dans le zip bloqués par `readonly_content_loader`.

### RSSI_SECURITY_PRESENTATION — 334 entrées registry
- **Pack canonique actif :** `OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip`
- **Adapter target :** `rssi_security_to_context_packet`
- **Boundary :** ALLOW_CONTEXT_ONLY — KX108_ONLY
- **Runtime status :** ACTIVE (P26+)
- **SHA256 :** `d1690bce3edcc342f846...`

### EXTERNAL_SIGNALS — 82 entrées registry
- **Pack canonique actif :** `OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1.zip`
- **Adapter target :** `external_signals_to_context_packet`
- **Boundary :** ALLOW_CONTEXT_ONLY — KX108_ONLY
- **Runtime status :** ACTIVE (P26+)
- **SHA256 :** `f08ccd6446db616989ef...`

### COMPLIANCE_DATA_GOVERNANCE — 488 entrées registry
- **Pack dédié :** AUCUN — entrées issues de 3 packs RSSI existants
  - `OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip` : 280 entrées
  - `OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip` : 167 entrées
  - `OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1.zip` : 41 entrées
- **Adapter target :** `compliance_to_context_packet`
- **Runtime status :** ACTIVE — famille disponible via les packs RSSI
- **Dette P30 :** aucun zip dédié COMPLIANCE. Comportement acceptable pour P26-P30.

---

## Politique .py dans les zips

Le `readonly_content_loader.py` bloque toute lecture de `.py` :
- Extensions interdites : `.py`, `.pyc`, `.pyo`, `.sh`, `.bat`, `.exe`, `.dll`, etc.
- Les zips ATLAS (18 .py), RSSI_RGPD (23 .py), RSSI_SECURITY (16 .py) contiennent des fichiers Python
- Ces fichiers ne sont **jamais** lus, exécutés, ni extraits par le runtime
- La politique est vérifiée à chaque accès par `_validate_path()` et `_FORBIDDEN_EXTENSIONS`

---

## Inventaire complet _source_packs/raw/

| Fichier | Taille (B) | SHA256 (20 chars) | Entrées | .py |
|---------|-----------|-------------------|---------|-----|
| `OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip` | 4 203 414 | 69d9352ea4a1ae8679bb | 1 738 | 18 |
| `OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip` | 847 755 | 7e8308f50e7212b1a486 | 519 | 0 |
| `OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX.zip` | 268 382 | 203ca1447d09dfc0af3f | 103 | 0 |
| `OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1.zip` | 58 538 | f08ccd6446db616989ef | 41 | 0 |
| `OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip` | 802 276 | 319706db7a2284190286 | 311 | 23 |
| `OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip` | 456 116 | d1690bce3edcc342f846 | 167 | 16 |

Autres fichiers dans raw/ (non-zips) :
- `Fichier markdown (2)(3).md collé` / `(3)(3)` / `(4)(1)` / `(5)` — 4 fichiers collés, hors registry
- `OBSIDIA_IMPLEMENTATION_PLAN_FILE_BY_FILE_V1.xlsx` — plan d'implémentation, hors runtime
- `VERIFY_NON_EMPTY_NAME_METRICS_BOUNDARY_STATUS_V2_PASS.txt` — audit de vérification

---

## Versions manquantes mais non bloquantes

Les entrées registry référencent des versions plus anciennes (V0, V0.1, V0.2, etc.) qui ne sont pas en `raw/`. Le résolveur n'en a pas besoin car la règle est : **une famille est disponible si au moins un de ses zips est présent**. La version canonique (la plus récente) est toujours en `raw/`.

| Famille | Versions manquantes en raw/ | Impact runtime |
|---------|----------------------------|---------------|
| ATLAS | V0, V0.1×2, V0.2, V0.3, V0.4 | Aucun (V0.7 présent) |
| COGNITIVE | V1, V1(1), final | Aucun (VERIFIED_FULL(1) présent) |
| RSSI_RGPD | V2(2), ExternalSignals(3) | Aucun (V2 présent) |
| RSSI_SECURITY | (3) | Aucun (V1 présent) |
| EXTERNAL_SIGNALS | (3) | Aucun (V1 présent) |
| NPL | — (canonisé P30) | Résolu ✓ |
| COMPLIANCE | — (pas de pack dédié) | Comportement attendu |

---

## Paliers P26-P30

| Palier | Action source packs | Statut |
|--------|--------------------|----|
| P26 | Source packs branchés runtime readonly | ✓ |
| P27 | Propagation contexte → final_answer | ✓ |
| P28 | Cache TTL 60s + selector familles | ✓ |
| P29 | API + Workbench surface | ✓ |
| P30 | NPL canonisé en zip local, resolver mis à jour | ✓ |
