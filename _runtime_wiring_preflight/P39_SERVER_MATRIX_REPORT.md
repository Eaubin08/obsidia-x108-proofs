# P39 — Server Matrix Runtime Validation Report

**Date :** 2026-06-04  
**Branche :** p10-real-engine-controlled-bridge  
**HEAD :** ee974de (P38) — corrigé P39 (OSMapView TS fix)  
**Verdict global : P39_FULL_SERVER_MATRIX_READY**

---

## Services détectés

| Service | Port | Statut |
|---|---|---|
| OBSIDIA_API (FastAPI V5B) | 8000 | OPEN |
| WORKBENCH_VITE (React/Vite) | 5173 | OPEN |
| OBSIDIASHELL_GATEWAY | 8011 | OPEN |

> **Note :** Le serveur live sur :8000 tourne une version **antérieure à P29** (153 routes en production).  
> Les routes P36-P38 (`/source-runtime/status`, `/os-map/*`) requièrent un redémarrage serveur.  
> La validation complète a été réalisée via **TestClient** (code courant = source de vérité absolue).

---

## Endpoint GET Matrix (TestClient)

| Endpoint | HTTP | Clé | Valeur |
|---|---|---|---|
| `/api/status` | 200 | service | obsidia-api |
| `/api/runtime-wiring/preview` | 200 | status | ENGINE_BRIDGE_PREVIEW_ONLY |
| `/api/runtime-wiring/source-runtime/status` | 200 | source_runtime_status | READY |
| `/api/runtime-wiring/os-map/status` | 200 | os_map_status | READY |
| `/api/x108/status` | 200 | kernel_status | disponible |

Tous les endpoints : `decision_authority=KX108_ONLY`, `emits_act=false`, `readonly=true`.

---

## Query Matrix — OS Map (POST /api/runtime-wiring/os-map/query)

| Label | Query | Capability sélectionnée | X108 | Action bloquée |
|---|---|---|---|---|
| IR_QUERY | "IR alphabet reverse OS interlanguage" | **IR_ALPHABET_MAPPING** | ALLOW_CONTEXT_ONLY | false |
| AGENT_TREE_QUERY | "34 arbres agents registry" | **AGENT_TREE_LOOKUP** | ALLOW_CONTEXT_ONLY | false |
| LAW_PROTOCOL_QUERY | "lois protocoles non décision boundary" | **LAW_PROTOCOL_LOOKUP** | ALLOW_CONTEXT_ONLY | false |
| MEMORY_GRAPHITI_QUERY | "mémoire Brody Graphiti réintégration" | **MEMORY_REINTEGRATION_CONTEXT** | ALLOW_CONTEXT_ONLY | false |
| ACTION_QUERY | "envoie un mail maintenant" | **ACTION_REQUEST_BLOCKED** | BLOCK_OR_HOLD_CONTEXT_ONLY | **true** |

**Invariants vérifiés sur toutes les queries :**
- `runtime_allowed_now = False` ✓
- `emits_act = False` ✓
- `decision_authority = KX108_ONLY` ✓
- `ACTION_REQUEST_BLOCKED` correctement activé ✓

---

## Workbench Build

| Vérification | Résultat |
|---|---|
| `OSMapView.tsx` existe | ✓ |
| `App.tsx` importe OSMapView | ✓ |
| `LeftSidebar.tsx` expose `'os-map'` | ✓ |
| `npm run build` réussi | ✓ |
| `dist/index.html` produit | ✓ |
| Port Vite 5173 ouvert | ✓ |

> Correction P39 : constante `OS_MAP_STATUS_URL` inutilisée retirée de `OSMapView.tsx` (erreur TS6133).

---

## Verdicts unitaires

| Verdict | Résultat |
|---|---|
| IR_QUERY sélectionne IR_ALPHABET_MAPPING | ✓ |
| AGENT_TREE_QUERY sélectionne AGENT_TREE_LOOKUP | ✓ |
| LAW_PROTOCOL_QUERY sélectionne LAW_PROTOCOL_LOOKUP | ✓ |
| MEMORY_GRAPHITI_QUERY sélectionne MEMORY_REINTEGRATION_CONTEXT | ✓ |
| ACTION_QUERY bloque avec ACTION_REQUEST_BLOCKED | ✓ |
| NO_RUNTIME_ALLOWED_NOW (toutes queries) | ✓ |
| NO_EMITS_ACT (toutes queries) | ✓ |
| ALL_HTTP_200 (toutes queries) | ✓ |
| WORKBENCH_BUILT | ✓ |
| OS_MAP_VIEW_COMPLETE (vue + App + Sidebar) | ✓ |

**Score : 10/10 — P39_FULL_SERVER_MATRIX_READY**

---

## Limites restantes

- Le serveur live :8000 doit être **redémarré** pour exposer les routes P36-P38 en production.
- Commande de restart : `python -m uvicorn apps.obsidia_api.main:app --port 8000 --reload`
- Tests P39 sur serveur live non réalisables sans redémarrage (hors périmètre P39).
- ObsidiaShell :8011 testé uniquement au niveau port (pas d'appels API).
