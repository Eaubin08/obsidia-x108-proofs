# P29 — Workbench / API Source Runtime Surface Report

**Branch:** p10-real-engine-controlled-bridge  
**Date:** 2026-06-03  
**Status:** P29_WORKBENCH_SOURCE_RUNTIME_SURFACE_READY

---

## Résumé

P29 rend la machinerie source runtime (P26-P28) visible et exploitable côté API et Workbench :
- Nouvel endpoint dédié `GET /api/runtime-wiring/source-runtime/status` — statut et stats purs, zéro hydration
- Nouvel endpoint preview `POST /api/runtime-wiring/source-runtime/preview` — même chaîne que Brody, sans `final_answer`
- `GET /api/runtime-wiring/preview` enrichi de 3 champs dérivés P29
- Section "SOURCE RUNTIME / BRODY CONTEXT ENGINE" dans `RuntimeWiringPreviewView.tsx`
- Panneau preview query interactif dans le Workbench (readonly, no ACT)

---

## Endpoints exposés

### `GET /api/runtime-wiring/source-runtime/status`

Payload type :
```json
{
  "source_runtime_status": "READY",
  "source_runtime_available": true,
  "source_runtime_cache_enabled": true,
  "source_runtime_families": [
    "ATLAS", "COGNITIVE_REINTEGRATION", "COMPLIANCE_DATA_GOVERNANCE",
    "EXTERNAL_SIGNALS", "NARRATIVE_PROVENANCE_LAYER", "RSSI_RGPD",
    "RSSI_SECURITY_PRESENTATION"
  ],
  "source_runtime_family_count": 7,
  "source_runtime_registry_entries": 15298,
  "cache_stats": {
    "cache_hits": 0,
    "cache_misses": 1,
    "ttl_seconds": 60.0,
    "cache_hit_rate": null
  },
  "brody_context_bridge_available": true,
  "real_readonly_hydration_available": true,
  "readonly": true,
  "emits_act": false,
  "memory_write": false,
  "graph_write": false,
  "kernel_mutation": false,
  "zip_extraction": false,
  "world_action": false,
  "decision_authority": "KX108_ONLY"
}
```

**source_runtime_status** dérivé :
- `READY` : modules disponibles + familles présentes
- `PARTIAL` : modules disponibles, 0 familles
- `UNAVAILABLE` : import échoue

### `POST /api/runtime-wiring/source-runtime/preview`

Input : `{"query": "X108 gouvernance cognitive", "limit": 5}`

Payload type :
```json
{
  "source_runtime_status": "PREVIEW_READY",
  "selected_families": ["COGNITIVE_REINTEGRATION"],
  "selector_reason": "KEYWORD_MATCH:COGNITIVE_REINTEGRATION",
  "entries_used": 5,
  "hydrated_entries": [...],
  "x108_decision": "ALLOW_CONTEXT_ONLY",
  "x108_decision_authority": "KX108_ONLY",
  "os3_evidence_id": "...",
  "context_summary_for_brody": "...",
  "readonly": true,
  "emits_act": false,
  "memory_write": false,
  "graph_write": false,
  "kernel_mutation": false,
  "zip_extraction": false,
  "world_action": false,
  "decision_authority": "KX108_ONLY"
}
```

### `GET /api/runtime-wiring/preview` — champs ajoutés par P29

| Champ | Type | Description |
|-------|------|-------------|
| `source_runtime_status` | str | READY / PARTIAL / UNAVAILABLE |
| `source_runtime_family_count` | int | Nombre de familles disponibles |
| `source_runtime_registry_entries` | int | Entrées dans le cache registry |

---

## Surface Workbench ajoutée

**Fichier :** `apps/obsidia-workbench/src/views/RuntimeWiringPreviewView.tsx`

### Carte "SOURCE RUNTIME / BRODY CONTEXT ENGINE"
- `source_runtime_status` (READY en vert, PARTIAL en ambre, UNAVAILABLE en rouge)
- `source_runtime_available`, `brody_context_bridge_available`, `real_readonly_hydration_available` (Flags)
- `source_runtime_family_count`, `source_runtime_registry_entries` (Pills)
- `cache_ttl_seconds`, `cache_hits`, `cache_misses` (Pills)
- `decision_authority` : KX108_ONLY
- Badges famille (liste compacte)

### Panneau preview query
- Input texte + bouton "Preview source context"
- POST vers `/api/runtime-wiring/source-runtime/preview`
- Affiche : status, entries_used, x108_decision, x108_decision_authority, os3_evidence_id, selector_reason, emits_act, familles sélectionnées (badges), context_summary_for_brody (details tronqué à 500 chars)

---

## Preuves no ACT / no write / no extraction

Tous les endpoints P29 :
- `emits_act: false`
- `memory_write: false`
- `graph_write: false`
- `kernel_mutation: false`
- `zip_extraction: false`
- `world_action: false`
- `decision_authority: "KX108_ONLY"`

Le status endpoint appelle uniquement `list_available_families_cached()` et `get_cache_stats()` — aucune hydration de fichier source.

Le preview endpoint appelle `build_brody_context_from_source_packs()` qui enforce `ALLOW_CONTEXT_ONLY` via X108 — identique à la chaîne Brody, sans `final_answer`.

---

## Résultats de validation

| Étape | Résultat |
|-------|----------|
| `python -m compileall apps/obsidia_api runtime_wiring -q` | PASS (aucune sortie) |
| `pytest tests/api/test_source_runtime_status_p29.py` | **11/11 PASS** |
| `pytest tests/*p28* tests/api/*p28*` | **25/25 PASS** |
| `pytest tests/` (suite complète) | **3505/3505 PASS** |
| `python scripts/check_forbidden_content.py` | FORBIDDEN_CONTENT_PASS |
| `python scripts/generate_recursive_manifest.py` | 7650 files |
| `python scripts/verify_recursive_manifest.py` | MANIFEST_VERIFIED — 7650 files match |
| `npm run build` (Workbench) | ✓ built in 1.51s (TypeScript + Vite, 0 erreur) |

---

## Composants créés / modifiés

| Fichier | Action | Rôle |
|---------|--------|------|
| `apps/obsidia_api/routes/source_runtime_status.py` | Créé | 2 nouveaux endpoints status + preview |
| `apps/obsidia_api/main.py` | Modifié | Import + enregistrement `source_runtime_status_router` |
| `apps/obsidia_api/routes/runtime_wiring_preview.py` | Modifié | 3 champs dérivés P29 dans la réponse |
| `apps/obsidia-workbench/src/views/RuntimeWiringPreviewView.tsx` | Modifié | Section SOURCE RUNTIME + panneau preview query |
| `tests/api/test_source_runtime_status_p29.py` | Créé | 11 tests ciblés P29 |

**Non touchés** : kernel, proofs/, merkle, seal, sigma/, brody.py, source_runtime_cache.py, source_family_selector.py, brody_source_context_bridge.py.

---

## Limites restantes / Prochain palier P30

- Le panneau preview query Workbench affiche le contexte Brody mais pas les entrées hydratées individuelles dans l'UI (données disponibles dans le payload, affichage tronqué)
- Les stats cache (`cache_hits`, `cache_misses`) sont des compteurs globaux de process — un redémarrage de l'API les remet à zéro
- P30 pourrait ajouter : historique des queries preview, export du contexte Brody, visualisation graphique des familles sélectionnées, persistance des stats cache via SQLite ou Redis
