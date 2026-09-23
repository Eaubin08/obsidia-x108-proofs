# P26 — Source Pack Runtime Bridge Report

**Branch:** p10-real-engine-controlled-bridge  
**Date:** 2026-06-03  
**Status:** P26_SOURCE_PACK_RUNTIME_BRIDGE_READY

---

## Résumé

P26 connecte les source packs/zips au moteur Brody comme couche de contexte readonly réelle. Brody peut désormais interroger la registry, hydrater les fichiers pertinents, passer par X108, et produire une réponse contextualisée — sans ACT, sans extraction disque, sans écriture, sans mutation kernel.

---

## Familles branchées

| Famille | Packs disponibles | Statut |
|---------|------------------|--------|
| ATLAS | OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip | FOUND_LOCAL |
| COGNITIVE_REINTEGRATION | OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip | FOUND_LOCAL |
| COMPLIANCE_DATA_GOVERNANCE | (dans ATLAS zip) | FOUND_LOCAL |
| EXTERNAL_SIGNALS | OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1.zip | FOUND_LOCAL |
| NARRATIVE_PROVENANCE_LAYER | Répertoire extrait dans Downloads/ | FOUND_DOWNLOADS |
| RSSI_RGPD | OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip | FOUND_LOCAL |
| RSSI_SECURITY_PRESENTATION | OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip | FOUND_LOCAL |

**Total familles disponibles localement : 7 / 7**

---

## Composants créés

| Module | Rôle |
|--------|------|
| `runtime_wiring/source_runtime/__init__.py` | Constantes de frontière P26 |
| `runtime_wiring/source_runtime/source_pack_resolver.py` | Résolution zip → chemin local, MissingSourcePackError |
| `runtime_wiring/source_runtime/readonly_content_loader.py` | Lecture in-zip read-only, refuse .py/traversal, 8KB preview |
| `runtime_wiring/source_runtime/source_context_hydrator.py` | Entry → ContextPacket avec contenu réel injecté |
| `runtime_wiring/source_runtime/source_runtime_query.py` | Requête filtrée, max 20 entrées, dédup par famille |
| `runtime_wiring/source_runtime/brody_source_context_bridge.py` | Bridge principal : query → X108 → dict Brody |

---

## Injection Brody

**Point d'injection :** `apps/obsidia_api/routes/brody.py`, après le bloc `runtime_context`, avant `reverse_os_bridge`.

**Nouvelles clés dans la réponse Brody :**
- `source_pack_context` — dict complet avec hydrated_entries, summary, OS3
- `source_pack_context_used` — bool
- `source_pack_families` — list de familles utilisées
- `source_pack_entries_used` — int
- `source_pack_x108_decision` — décision X108
- `source_pack_os3_evidence_id` — référence OS3

**Fallback propre** si packs absents ou module non importé : `source_pack_context_used=False`, aucun crash.

---

## Résultats des tests

### Tests unitaires (11/11)
```
tests/test_source_runtime_p26.py    11 passed in 8.14s
```

| Test | Résultat |
|------|---------|
| Resolver trouve au moins un pack | PASS |
| Loader refuse .py | PASS |
| Loader refuse path traversal | PASS |
| Loader lit .md en readonly | PASS |
| Hydrator produit ContextPacket valide | PASS |
| Query COGNITIVE_REINTEGRATION | PASS |
| Query ≥ 3 familles | PASS |
| X108 retourne ALLOW_CONTEXT_ONLY | PASS |
| OS3 evidence présent, proof_claim=False | PASS |
| No ACT / no write / no mutation | PASS |
| Pack absent → fallback propre | PASS |

### Tests API Brody (4/4)
```
tests/api/test_brody_source_pack_context_p26.py    4 passed in 10.13s
```

### Régression (75/75)
```
test_runtime_wiring_p8c.py + test_source_registry_p9b.py + test_engine_bridge_p10c.py + test_api_runtime_wiring_preview_p10d.py    75 passed in 1.79s
```

---

## Décision X108

**Décision : `ALLOW_CONTEXT_ONLY`**  
**Autorité : `KX108_ONLY`**  
**Gate status : `X108_EVALUATED_DRY_RUN`**

X108 autorise uniquement le contexte informatif. Aucune action réelle, aucune décision, aucune mutation.

---

## OS3 Evidence

**Type :** `HASH_CHAIN` (dry-run)  
**proof_claim :** `False`  
**verification_status :** `NOT_VERIFIED_DRY_RUN`  
**seal_status :** `NOT_SEALED`  
**merkle_status :** `NOT_BUILT`

Le dry-run est honnête : aucune chaîne Merkle, aucun sceau RFC3161.

---

## Preuves de sécurité

### No ACT
- `emits_act=False` sur tous les ContextPackets (validé par `validate_invariants()`)
- `no_act=True` dans le retour du bridge
- `safe_backend_response()` réapplique les flags souverains après merge — ne peut pas être contourné

### No extraction disque
- `readonly_content_loader.py` utilise `zipfile.ZipFile.read()` — aucun `extract()` ni `extractall()`
- `extracted_to_disk=False` sur tous les `LoadedContent`
- `FORBIDDEN_CONTENT_PASS` confirmé

### No write
- `memory_write=False`, `graph_write=False`, `kernel_mutation=False`, `x108_mutation=False`
- Flags dans `_BOUNDARY` du bridge + réappliqués par `safe_backend_response`

### No .py execution
- `_FORBIDDEN_EXTENSIONS` inclut `.py`, `.pyc`, `.pyo`, `.sh`, `.bat`, `.exe`
- Raise `ForbiddenFileError` avant toute tentative de lecture

---

## Limites

- Les packs ne sont pas indexés en mémoire : chaque requête relit le registry JSON (15 298 entrées)
- Preview limité à 8 KB par fichier, 4 KB dans l'adaptateur hydrator
- NPL : résolution via répertoire local dans Downloads/ — dépendance machine
- Max 20 entrées par requête (cap interne `_MAX_LIMIT`)
- `context_summary_for_brody` est injecté dans `source_pack_context` mais pas encore dans `final_answer`

---

## Prochain palier : P27

- Injecter `context_summary_for_brody` dans la synthèse `true_voice` pour enrichir `final_answer`
- Indexation légère en mémoire pour éviter la relecture des 15 298 entrées à chaque requête
- Preview workbench API (`/api/runtime-wiring/preview`) avec `source_runtime_available`
- Compaction propre de `source_pack_context` en mode `compact=True`
- Cache manifest pour résolution rapide des packs fréquemment utilisés
