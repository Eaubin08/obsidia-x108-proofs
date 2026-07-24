# P71 — Source Runtime & Source Packs Deep Audit

**Audit ID :** P71  
**Statut :** `P71_SOURCE_RUNTIME_SOURCE_PACKS_DEEP_AUDIT_READY`  
**Mode :** `AUDIT_ONLY` — aucun patch, aucune correction, aucun import  
**Branche :** `p71-source-runtime-source-packs-deep-audit`  
**Date :** 2026-06-07

---

## 1. Verdict court

### Fichiers scannés : 9 630

### Source packs détectés : 14 entrées classifiées

| Classification | Nb | Verdict |
|---|---:|---|
| `SOURCE_FULL_LOCAL` | 8 | SAFE — zip/dir local + adapter déclaré |
| `SOURCE_ARCHIVE_ONLY` | 3 | SAFE — freeze/proof, non runtime |
| `SOURCE_METADATA_ONLY` | 1 | SAFE — xlsx non lisible par loader |
| `SOURCE_LOCAL_ONLY_UNCANONIZED` | 1 | LOW — orphan markdown hors registre |
| `SOURCE_PACK_DO_NOT_RUNTIME_LOAD` | 1 | MEDIUM — import staging uniquement |

### Adapters classifiés : 14 entrées

| Classification | Nb | Verdict |
|---|---:|---|
| `ADAPTER_HYDRATES_CONTENT` | 8 | LOW — dry_run, advisory_only, .py forbidden |
| `ADAPTER_AUTH_REQUIRED` | 2 | MEDIUM — endpoints preview sans auth (P69 carried) |
| `ADAPTER_DRY_RUN_SAFE` | 2 | LOW — loader + hydrator boundary enforced |
| `ADAPTER_METADATA_ONLY` | 1 | LOW — xlsx non hydratable |
| `ADAPTER_PATH_EXPOSING` | 1 | LOW — C:/Users/User/Downloads dans resolver |

### Registre source

| Métrique | Valeur |
|---|---:|
| Total entrées | 15 853 |
| Familles | 8 |
| Fichiers .py (DO_NOT_IMPORT_RUNTIME) | 272 |
| py_files_all_do_not_import | TRUE |
| runtime_allowed_now (count) | 0 |
| emits_act (count) | 0 |
| safety_invariants_ok | TRUE |

### Zones safe confirmées

- `runtime_wiring/source_runtime/readonly_content_loader.py` — `.py` interdit, `extracted_to_disk=False`, max 8KB preview, max 512KB, `KX108_ONLY`
- `runtime_wiring/source_runtime/source_context_hydrator.py` — `emits_act=False`, `advisory_only=True` enforced post-hydration
- `_source_packs/REVERSE_OS_INTERLANGUAGE_CANON_V1/` — canonisé P34/P35, `MANIFEST_SHA256.json`, `readonly=True` dans manifest
- `runtime_wiring/source_registry/source_file_registry.json` — safety invariants confirmés
- `_freezes/` — archives preuve uniquement, hors registre

### Zones à adresser (P71+)

1. `POST /api/runtime-wiring/source-runtime/preview` — pas d'auth → `ADD_REQUIRE_API_KEY`
2. `POST /api/runtime-wiring/os-map/query` — pas d'auth → `ADD_REQUIRE_API_KEY`
3. `source_pack_resolver.py` — chemin absolu `C:/Users/User/Downloads` → remplacer par env var ou relative path
4. `_tmp_core_import/OBSIDIA_CORE_ONLY_FULL_MACHINERY` — import staging non runtime-loadable
5. `COMPLIANCE_DATA_GOVERNANCE` xlsx — metadata only, non hydratable via loader

---

## 2. Modèle source runtime

| Catégorie | Sens | Runtime load ? | Public claim ? | Exemple |
|---|---|:---:|:---:|---|
| `SOURCE_FULL_LOCAL` | Pack complet localement. Contenu lisible par loader. | ✓ DRY_RUN | — local only | ATLAS zip, COGNITIVE zip |
| `SOURCE_METADATA_ONLY` | Pack présent mais format non lisible (xlsx). Métadonnées uniquement. | ✗ NO | ✗ | COMPLIANCE xlsx |
| `SOURCE_DOCUMENTED_FALLBACK` | Pack canonical absent localement — fallback Downloads déclaré. | ✓ FALLBACK | — local only | NPL Downloads fallback (pré-P30) |
| `SOURCE_BLOCKED_ABSENT` | Pack absent ni local ni fallback. MissingSourcePackError. | ✗ BLOCKED | ✗ | — (aucun détecté) |
| `SOURCE_LOCAL_ONLY_UNCANONIZED` | Pack local hors registre officiel. Non accessible au runtime. | ✗ NO | ✗ | Fichier markdown collision raw/ |
| `SOURCE_ARCHIVE_ONLY` | Freeze / archive de preuve. Hors registre. | ✗ ARCHIVE | ✗ | _freezes/P55, _freezes/PLAN3 |
| `SOURCE_RUNTIME_HYDRATABLE` | Pack local + adapter enregistré. Hydratable en dry_run/preview. | ✓ DRY_RUN | — advisory | 8 familles zip/dir |
| `SOURCE_RUNTIME_PREVIEW_REVIEW` | Endpoint preview expose excerpt sans auth. Review: auth obligatoire. | ⚠️ REVIEW | ✗ | POST /preview, POST /os-map/query |
| `SOURCE_EXCERPT_AUTH_REQUIRED` | Endpoint expose content_preview des packs. Auth OBSIDIA_API_KEY requise. | ⚠️ REQUIRE_AUTH | ✗ | POST /preview → hydrated_entries |
| `SOURCE_PATH_EXPOSURE_REVIEW` | Chemin absolu système dans resolver/logs. Remplacer par hash/env. | ⚠️ REVIEW | ✗ | source_pack_resolver Downloads path |

---

## 3. Matrice source packs

| Source | Path | Catégorie | Manifest | Adapter | Preview | Risque | Prochain geste |
|---|---|---|:---:|:---:|:---:|---|---|
| ATLAS | _source_packs/raw/ATLAS.zip | SOURCE_FULL_LOCAL | ✓ | atlas_to_context_packet | ✓ | LOW | ADD_AUTH_PREVIEW |
| COGNITIVE_REINTEGRATION | _source_packs/raw/COGNITIVE.zip | SOURCE_FULL_LOCAL | ✓ | cognitive_to_context_packet | ✓ | LOW | ADD_AUTH_PREVIEW |
| OS_TRAD_REVERSE_OS | _source_packs/raw/MMONDE_REVERSE.zip | SOURCE_FULL_LOCAL | ✓ | os_trad_reverse_to_context_packet | ✓ | LOW | OK |
| OS_TRAD_INTERLANGUAGE | _source_packs/REVERSE_OS_INTERLANGUAGE_CANON_V1/ | SOURCE_FULL_LOCAL | ✓ | reverse_os_interlanguage_to_context_packet | ✓ | LOW | OK P34 |
| NARRATIVE_PROVENANCE | _source_packs/raw/NPL.zip | SOURCE_FULL_LOCAL | ✓ | npl_to_context_packet | ✓ | LOW | NPL P30 |
| RSSI_RGPD | _source_packs/raw/RSSI_RGPD.zip | SOURCE_FULL_LOCAL | ✓ | rssi_rgpd_to_context_packet | ✓ | LOW | OK |
| RSSI_SECURITY | _source_packs/raw/RSSI_SECURITY.zip | SOURCE_FULL_LOCAL | ✓ | rssi_security_to_context_packet | ✓ | LOW | OK |
| EXTERNAL_SIGNALS | _source_packs/raw/EXTERNAL_SIGNALS.zip | SOURCE_FULL_LOCAL | ✓ | external_signals_to_context_packet | ✓ | LOW | OK |
| COMPLIANCE | _source_packs/raw/IMPLEMENTATION_PLAN.xlsx | SOURCE_METADATA_ONLY | — | compliance_to_context_packet | ✗ | LOW | XLSX_NOT_HYDRATABLE |
| ORPHAN_MD | _source_packs/raw/*.md coll* | SOURCE_LOCAL_ONLY_UNCANONIZED | ✗ | — | ✗ | LOW | CLEANUP_LATER |
| TMP_CORE_MACHINERY | _tmp_core_import/OBSIDIA_CORE_ONLY_FULL_MACHINERY | SOURCE_PACK_DO_NOT_RUNTIME_LOAD | ✓ | — | ✗ | MEDIUM | IMPORT_STAGING_ONLY |
| FREEZE_P55 | _freezes/P55_CONTROLLED_ACTIVATION | SOURCE_ARCHIVE_ONLY | ✓ | — | ✗ | NONE | ARCHIVE_OK |
| FREEZE_PLAN3 | _freezes/PLAN3_RUNTIME_CONTRACTS | SOURCE_ARCHIVE_ONLY | ✓ | — | ✗ | NONE | ARCHIVE_OK |
| LOCAL_AUDITS | .local_audits/ | SOURCE_ARCHIVE_ONLY | ✗ | — | ✗ | NONE | ARCHIVE_OK |

---

## 4. Matrice adapters

| Adapter | Source | Contenu | Metadata | Preview | Path exp. | Auth | Risque |
|---|---|:---:|:---:|:---:|:---:|:---:|---|
| atlas_to_context_packet | ATLAS | ✓ | — | ✓ | ✗ | ✗ | LOW |
| cognitive_to_context_packet | COGNITIVE | ✓ | — | ✓ | ✗ | ✗ | LOW |
| os_trad_reverse_to_context_packet | OS_TRAD | ✓ | — | ✓ | ✗ | ✗ | LOW |
| reverse_os_interlanguage_to_context_packet | OS_INTERLANGUAGE | ✓ | — | ✓ | ✗ | ✗ | LOW |
| npl_to_context_packet | NPL | ✓ | — | ✓ | ✗ | ✗ | LOW |
| rssi_rgpd_to_context_packet | RSSI_RGPD | ✓ | — | ✓ | ✗ | ✗ | LOW |
| rssi_security_to_context_packet | RSSI_SECURITY | ✓ | — | ✓ | ✗ | ✗ | LOW |
| external_signals_to_context_packet | EXTERNAL_SIGNALS | ✓ | — | ✓ | ✗ | ✗ | LOW |
| compliance_to_context_packet | COMPLIANCE | ✗ | ✓ | ✗ | ✗ | ✗ | LOW |
| source_pack_resolver | ALL | ✗ | ✓ | ✗ | ✓ | ✗ | LOW |
| POST /source-runtime/preview | ALL_FAMILIES | ✓ | — | ✓ | ✗ | **✗ MISSING** | MEDIUM |
| POST /os-map/query | ALL_CAPABILITIES | ✓ | — | ✓ | ✗ | **✗ MISSING** | MEDIUM |
| readonly_content_loader | ALL_PACKS | ✓ | — | ✓ | ✗ | — | LOW |
| source_context_hydrator | ALL_PACKS | ✓ | — | ✓ | ✗ | — | LOW |

---

## 5. Findings repris P69/P70

### Findings P69 repris

#### 1. POST /source-runtime/preview — SOURCE_EXCERPT_AUTH_REQUIRED ⚠️

`POST /api/runtime-wiring/source-runtime/preview` sans `Depends(require_api_key)`.  
Retourne `hydrated_entries` avec `content_preview` des packs de toutes les 8 familles.  
P69 finding confirmé — **Auth requise.**

#### 2. POST /os-map/query — SOURCE_EXCERPT_AUTH_REQUIRED ⚠️

`POST /api/runtime-wiring/os-map/query` sans auth.  
Expose `CAPABILITY_TAXONOMY`, `build_runtime_inventory_graph`, `hydration_plan`, `source_file_refs`.  
P69 finding confirmé — **Auth requise.**

#### 3. source_pack_resolver.py — SOURCE_PATH_EXPOSURE_REVIEW

`pathlib.Path("C:/Users/User/Downloads")` codé en dur comme fallback search root.  
Exposé dans `MissingSourcePackError` messages. P69 finding confirmé.  
Remplacer par variable d'environnement ou relative path dans un palier futur.

#### 4. audit/ stdout — ABSOLUTE_PATH_EXPOSURE

Chemins absolus `C:\Users\User\Desktop\...` dans stdout sigma archivé (`RUN_METRICS_PALIER_LAST.json`, `sigma_config.json`). P69 finding confirmé — données test uniquement, ne pas exposer via API.

### Findings P70 repris

#### 5. Connecteurs actifs — DO_NOT_RUN

`connectors/aviation_robo.py`, `connectors/bank_normal_flow.py` — `while True` + `requests.post()` + `irreversible=True` — **DO_NOT_RUN** sans dry_run + KX108 gate. Inchangé depuis P70.

`connectors/trading_live.py` — + `ccxt.binance()` externe — **DO_NOT_RUN**. Inchangé.

#### 6. Graphiti readonly — DRY_RUN_SAFE

`graphiti_v20_readonly_client.py` — GET readonly, write flags False, fallback stub. **SAFE.**

### _tmp_core_import — DO_NOT_RUNTIME_LOAD

`_tmp_core_import/OBSIDIA_CORE_ONLY_FULL_MACHINERY` — 282 fichiers, agents/, engine/, governance/,  distributed/, python_agents/. **Import staging uniquement.** Hors `source_file_registry`. Jamais runtime-loadable.

### _freezes — ARCHIVE_ONLY

6 sous-répertoires freeze + zips. P30_SOURCE_CANONIZATION, P41_RUNTIME_CAPABILITY, P55_CONTROLLED_ACTIVATION, PLAN3_RUNTIME_CONTRACTS (5 versions), POST_IMPORT, POST_MERGE. **Preuve/archive uniquement.** Jamais runtime-loadable.

---

## 6. Décision

P71 ne corrige pas. P71 classe les sources.

**Sources classifiées :**
- 8 packs `SOURCE_FULL_LOCAL` + `SOURCE_RUNTIME_HYDRATABLE` — dry_run safe, advisory_only enforced
- 1 pack `SOURCE_METADATA_ONLY` — xlsx non lisible via loader
- 1 pack `SOURCE_LOCAL_ONLY_UNCANONIZED` — hors registre
- 3 surfaces `SOURCE_ARCHIVE_ONLY` — freeze/proof
- 1 surface `SOURCE_PACK_DO_NOT_RUNTIME_LOAD` — import staging

**Actions P71+ obligatoires :**
1. `POST /preview` + `POST /os-map/query` → `Depends(require_api_key)` — `SOURCE_EXCERPT_AUTH_REQUIRED`
2. `source_pack_resolver` Downloads path → env var / `OBSIDIA_SOURCE_FALLBACK_ROOT` — `SOURCE_PATH_EXPOSURE_REVIEW`
3. Connectors P70 (aviation/bank/trading) → dry_run gate — portés P71

**Safety invariants registre confirmés :** `py_files_all_do_not_import=True`, `runtime_allowed_now=0`, `emits_act=0`.

**Prochain geste : P72 — Invariant Graph & Formal Proof Alignment.**

---

**Verdict :** `P71_SOURCE_RUNTIME_SOURCE_PACKS_DEEP_AUDIT_READY`
