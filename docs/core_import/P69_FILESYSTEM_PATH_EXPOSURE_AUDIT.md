# P69 — Filesystem & Path Exposure Audit

**Audit ID :** P69  
**Statut :** `P69_FILESYSTEM_PATH_EXPOSURE_AUDIT_READY`  
**Mode :** `AUDIT_ONLY` — aucun patch, aucune correction, aucun import  
**Branche :** `p69-filesystem-path-exposure-audit`  
**Date :** 2026-06-07

---

## 1. Verdict court

### Fichiers scannés

| Surface | Fichiers |
|---|---:|
| `apps/obsidia_api` | 181 |
| `apps/obsidia_api/routes` | 44 |
| `runtime_wiring` | 111 |
| `sigma` | 136 |
| `periphery` | 3278 |
| `connectors` | 10 |
| `scripts` | 258 |
| `tools` | 33 |
| `proofs` | 188 |
| `tests` | 1030 |
| `audit` | 27 |
| `docs` | 883 |
| `_source_packs` | 51 |
| `_tmp_core_import` | 368 |
| `_freezes` | 2986 |
| `.local_audits` | 46 |
| **TOTAL** | **9 630** |

### Writes classifiés — 30 entrées

| Catégorie | Nb | Verdict |
|---|---:|---|
| `LOCAL_AUDIT_WRITE` | 10 | AUTORISÉ — classifié |
| `LOCAL_FILE_READ` | 6 | AUTORISÉ — lecture seule |
| `SOURCE_EXCERPT_REVIEW` | 2 | REVIEW requis (P70) |
| `MANIFEST_WRITE` | 2 | AUTORISÉ — scripts seulement |
| `ARTIFACT_WRITE` | 2 | AUTORISÉ — docs/core_import |
| `TEST_FIXTURE_WRITE` | 2 | AUTORISÉ — tests seulement |
| `SOURCE_PACK_READ` | 2 | AUTORISÉ — archive |
| `ABSOLUTE_PATH_EXPOSURE` | 2 | REVIEW requis (P70) |
| `SOURCE_NORMALIZATION_WRITE` | 1 | AUTORISÉ — script one-shot |
| `REPORT_WRITE` | 1 | AUTORISÉ — docs |

### Zones safe confirmées

- `runtime_wiring/` — gel P56E — aucun write, 0 exposition path
- `sigma/` — gel permanent — aucun write actif (path abs dans stdout capturé uniquement)
- `docs/core_import/` — rapports audit classifiés REPORT_WRITE
- `tests/` — os.remove uniquement dans test fixtures
- `tools/` — aucun write détecté
- `_tmp_core_import/` + `_freezes/` + `_source_packs/` — archives, non exposées API

### Zones à revoir (P70)

- `apps/obsidia_api/routes/source_runtime_status.py` — `POST /preview` expose contenu source pack sans auth
- `apps/obsidia_api/routes/os_map.py` — expose capability taxonomy sans auth
- `audit/RUN_METRICS_PALIER_LAST.json` — contient `C:\Users\User\Desktop\...` dans stdout sigma archivé
- `sigma/sigma_config.json` — chemin absolu résolu dans stdout capturé

### Aucun write dangereux détecté

Pas de `DANGEROUS_PATH_WRITE`, pas de `DANGEROUS_DELETE` actif hors test fixtures.

---

## 2. Modèle filesystem/path

| Catégorie | Sens | Autorisé ? | Exemple |
|---|---|:---:|---|
| `CANONICAL_MEMORY_WRITE` | Écriture mémoire canonique Brody/session | ✗ INTERDIT | — (aucun détecté) |
| `LOCAL_AUDIT_WRITE` | Écriture .jsonl log audit local | ✓ AUTORISÉ | audit_middleware.py → audit_logs/ |
| `ARTIFACT_WRITE` | Écriture JSON/MD rapport audit par script | ✓ AUTORISÉ | scripts/audit_p67.py → docs/core_import/ |
| `REPORT_WRITE` | Écriture narrative MD dans docs/ | ✓ AUTORISÉ | docs/core_import/P69_*.md |
| `MANIFEST_WRITE` | Écriture manifest SHA256 | ✓ AUTORISÉ (scripts/) | generate_recursive_manifest.py |
| `SOURCE_NORMALIZATION_WRITE` | Copie module source (import contrôlé) | ✓ AUTORISÉ (one-shot) | f30_2_copy_v5_readonly_module.py |
| `FREEZE_WRITE` | Écriture snapshot freeze | REVIEW opérateur | _freezes/ (archive, non runtime) |
| `TEST_FIXTURE_WRITE` | Écriture/delete fixture test | ✓ AUTORISÉ (tests/) | test_seal_tamper.py |
| `TEMP_WRITE` | Écriture fichier temp/swap | REVIEW | — (non détecté) |
| `DANGEROUS_PATH_WRITE` | Écriture hors chemins classifiés | ✗ INTERDIT | — (non détecté) |
| `DANGEROUS_DELETE` | os.remove / shutil.rmtree hors test | ✗ INTERDIT | — (non détecté actif) |
| `LOCAL_FILE_READ` | Lecture fichiers locaux | ✓ AUTORISÉ (relatif) | brody_freeze_metrics_snapshot.py |
| `SOURCE_PACK_READ` | Lecture source packs via cache | ✓ AUTORISÉ | source_runtime_status.py (via cache) |
| `PATH_EXPOSURE_REVIEW` | Chemin local dans réponse API | REVIEW | — utiliser relative_path |
| `SOURCE_EXCERPT_REVIEW` | Contenu source pack dans réponse API | REVIEW (auth requis) | source_runtime_status POST /preview |
| `ABSOLUTE_PATH_EXPOSURE` | Chemin absolu Windows dans données | REVIEW | audit/RUN_METRICS_PALIER_LAST.json |

---

## 3. Matrice par surface

| Surface | Fichiers | Reads | Writes locaux | Reports | Manifests | Path exposure | Risque |
|---|---:|---:|---:|---:|---:|---:|---|
| `apps/obsidia_api` | 181 | 3 | 1 | 0 | 0 | 0 | LOW |
| `routes` | 44 | 2 | 0 | 0 | 0 | 0 | MEDIUM |
| `runtime_wiring` | 111 | 1 | 0 | 0 | 0 | 0 | NONE — FROZEN_P56E |
| `sigma` | 136 | 1 | 0 | 0 | 0 | 1 | MEDIUM — abs_path_stdout |
| `periphery` | 3278 | 2 | 7 | 0 | 0 | 0 | LOW |
| `connectors` | 10 | 0 | 0 | 0 | 0 | 0 | LOW — CONNECTOR_EGRESS_P68 |
| `scripts/tools` | 291 | 1 | 0 | 2 | 1 | 0 | LOW |
| `proofs/tests` | 1218 | 1 | 0 | 0 | 1 | 0 | LOW — DRIFT_PREEXISTING |
| `audit/docs` | 910 | 0 | 2 | 4 | 0 | 1 | MEDIUM — abs_path_in_data |
| `_source_packs` | 51 | 1 | 0 | 0 | 0 | 0 | LOW — ARCHIVE |
| `_tmp_core_import` | 368 | 1 | 0 | 0 | 0 | 0 | LOW — ARCHIVE |
| `_freezes` | 2986 | 1 | 0 | 0 | 0 | 0 | LOW — ARCHIVE |
| `.local_audits` | 46 | 1 | 1 | 0 | 0 | 0 | LOW |

---

## 4. Focus findings

### 1. audit_middleware.py — LOCAL_AUDIT_WRITE — AUTORISÉ

`apps/obsidia_api/audit_middleware.py` crée `audit_logs/` au démarrage et écrit `http_audit_{date}.jsonl` en mode append asynchrone.  
Classifié `LOCAL_AUDIT_WRITE`. Aucun write canonique. Boundary documenté (`memory_write=False`).

### 2. event_bus.py — LOCAL_AUDIT_WRITE — AUTORISÉ

`periphery/event_bus.py` — `AuditEventWriter` écrit `audit_logs/event_bus_{date}.jsonl` asynchrone.  
Classifié `LOCAL_AUDIT_WRITE`. Never blocks HTTP. Boundary documenté.

### 3. world_action_bus.py → audit/world_action_bus.jsonl — DRIFT PRÉEXISTANT

`periphery/world_calls/world_action_bus.py` écrit `audit/world_action_bus.jsonl`.  
Dry-run only, `blocked=True` par défaut. **Hash mismatch préexistant documenté P65.** Ne pas corriger ici.

### 4. scripts/generate_recursive_manifest.py — MANIFEST_WRITE — AUTORISÉ

Écrit `MANIFEST_SHA256_RECURSIVE.json` + `MANIFEST_SHA256_RECURSIVE_ROOT.txt`.  
Script standalone non appelé depuis l'API. Classifié `MANIFEST_WRITE`.

### 5. source_runtime_status.py POST /preview — SOURCE_EXCERPT_REVIEW ⚠️

`POST /api/runtime-wiring/source-runtime/preview` appelle `build_brody_context_from_source_packs()` sans auth.  
Contenu des source packs potentiellement visible dans la réponse. **Nécessite auth P70.**

### 6. os_map.py — SOURCE_EXCERPT_REVIEW ⚠️

Expose `CAPABILITY_TAXONOMY` + `build_runtime_inventory_graph()` sans auth.  
Cartographie interne du runtime. **Nécessite auth P70.**

### 7. audit/RUN_METRICS_PALIER_LAST.json — ABSOLUTE_PATH_EXPOSURE ⚠️

Contient `C:\Users\User\Desktop\obsidia-engine-proof-core\...` dans stdout sigma archivé.  
Données de test — ne pas exposer via API. **Review P70 : masquer paths dans réponses.**

### 8. sigma/sigma_config.json — ABSOLUTE_PATH_EXPOSURE ⚠️

Chemin absolu résolu dans stdout `Config source : C:\Users\User\Desktop\...`.  
Données capturées de runs sigma. Ne pas exposer dans réponse API publique.

### 9. _source_packs/ + _tmp_core_import/ + _freezes/ — ARCHIVES SAFE

- `_source_packs/` : 51 fichiers, 0 py. Accès via source_runtime cache uniquement.
- `_tmp_core_import/` : 368 fichiers, 137 py. Archive d'import — non chargé en runtime API.
- `_freezes/` : 2986 fichiers, 0 py. Freeze snapshots — lecture uniquement via pointers.

### 10. Aucun write canonique mémoire détecté

`memory_write=False` confirmé dans tous les adapters scannés.  
Aucune écriture Graphiti ou Neo4j en runtime API.

### 11. Dettes préexistantes (inchangées)

| Fichier | Statut |
|---|---|
| `audit/world_action_bus.jsonl` | HASH_MISMATCH_PREEXISTING_P65 |
| `proofs/PROOFKIT_REPORT.json` | HASH_MISMATCH_PREEXISTING_P65 |
| `tests/test_invariants_against_engine.py` | ModuleNotFoundError: obsidia_os2 |
| `tests/sigma_stress_test.py` | ModuleNotFoundError: agents.obsidia_sigma_v130 |
| `tests/test_agents_functional.py` | ImportError: TradingState |
| `tests/test_consensus_inprocess.py` | ModuleNotFoundError: agents.run_pipeline |
| `tests/test_sigma_v18_9.py` | ModuleNotFoundError: agents.obsidia_sigma_v130 |

---

## 5. Décision

P69 ne corrige pas. P69 classe.

**Writes autorisés (10 LOCAL_AUDIT_WRITE + 2 ARTIFACT_WRITE + 1 REPORT_WRITE + 2 MANIFEST_WRITE + 1 SOURCE_NORMALIZATION_WRITE) :** tous documentés, tous classifiés.

**Writes interdits non détectés :** CANONICAL_MEMORY_WRITE, DANGEROUS_PATH_WRITE, DANGEROUS_DELETE actif.

**Reviews P70 obligatoires :**
1. `POST /preview source_runtime` + `os_map.py` → ajouter auth (SOURCE_EXCERPT_REVIEW)
2. `audit/RUN_METRICS_PALIER_LAST.json` + `sigma stdout` → masquer chemins absolus dans réponses API (ABSOLUTE_PATH_EXPOSURE)

**Prochain geste : P70 — Network Egress & Connectors Audit.**

---

**Verdict :** `P69_FILESYSTEM_PATH_EXPOSURE_AUDIT_READY`
