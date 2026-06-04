# P46 — Workbench Views Coverage Report

**Date:** 2026-06-04  
**Phase:** P46  
**Branch:** p43-unconnected-runtime-surface-audit  
**Builds on:** P45 (full route coverage 100%)

---

## Verdict

**P46_WORKBENCH_VIEWS_COVERAGE_100_READY**

- Total views scanned : **13**  
- Views classified : **13**  
- Unclassified : **0**  
- Coverage : **100%**

---

## Classification Summary

| Catégorie | Count | Vues |
|---|---|---|
| CONNECTED_TO_RUNTIME | 5 | AuditView, ChatView, GraphitiView, MemoryView, RuntimeWiringPreviewView |
| CONNECTED_TO_OS_MAP | 1 | OSMapView |
| CONNECTED_TO_STATUS_ONLY | 1 | X108View |
| CONNECTED_TO_WORKBENCH_ONLY | 2 | SettingsView, TranslationView |
| BLOCKED_ACTION_VIEW | 3 | BlockchainView, GencoinView, WorldCallView |
| INTERNAL_UI_ONLY | 1 | OS3View |
| ARCHIVE_ONLY | 0 | — |
| DO_NOT_BIND_EXPLICIT | 0 | — |
| UNCLASSIFIED | **0** | — |

---

## Détail par vue

### AuditView.tsx — CONNECTED_TO_RUNTIME
- Endpoint : `GET /api/audit/events`
- Capability : `AUDIT_TRAIL_READONLY`
- runtime_allowed_now : false | emits_act : false
- Append-only audit trail replay — no deletion, no mutation

### BlockchainView.tsx — BLOCKED_ACTION_VIEW
- Endpoints : aucun (mock statique)
- Capability : `ACTION_REQUEST_BLOCKED`
- x108_decision : `BLOCK_OR_HOLD_CONTEXT_ONLY`
- Toutes les actions blockchain BLOCKED — pas de wallet, pas de contrat, pas de token réel

### ChatView.tsx — CONNECTED_TO_RUNTIME
- Endpoint : `POST /api/brody/chat`
- Capability : `BRODY_CONTEXT_ENGINE`
- runtime_allowed_now : false | emits_act : false
- readonly=true, allowed_to_decide=false, allowed_to_act=false

### GencoinView.tsx — BLOCKED_ACTION_VIEW
- Endpoints : aucun (MOCK_GENCOIN uniquement)
- Capability : `ACTION_REQUEST_BLOCKED`
- x108_decision : `BLOCK_OR_HOLD_CONTEXT_ONLY`
- Gencoin n'est pas un vrai token — LEDGER_ONLY, is_real_token=false

### GraphitiView.tsx — CONNECTED_TO_RUNTIME
- Endpoints : `/graph/v20/frozen/status`, `/metrics`, `/readiness`, `/context`
- Capability : `GRAPHITI_FROZEN_READONLY`
- runtime_allowed_now : false | emits_act : false
- neo4j_write=false, graphiti_write=false — READONLY

### MemoryView.tsx — CONNECTED_TO_RUNTIME
- Endpoint : `GET /api/memory/candidates`
- Capability : `MEMORY_CANDIDATE_READONLY`
- runtime_allowed_now : false | emits_act : false
- CANDIDATE_ONLY — memory_write=false, auto_promotion_allowed=false

### OS3View.tsx — INTERNAL_UI_ONLY
- Endpoints : aucun (MOCK_OS3_TICKET)
- Capability : `OS3_PROOF_DISPLAY`
- runtime_allowed_now : false | emits_act : false
- Affichage preuve mock — pas d'API, pas de décision kernel, artefacts PROTÉGÉS

### OSMapView.tsx — CONNECTED_TO_OS_MAP
- Endpoint : `POST /api/runtime-wiring/os-map/query`
- Capability : `WORKBENCH_PREVIEW`
- runtime_allowed_now : false | emits_act : false
- P38 — READONLY_PREVIEW_ONLY, KX108_ONLY

### RuntimeWiringPreviewView.tsx — CONNECTED_TO_RUNTIME
- Endpoints : `GET /api/runtime-wiring/preview`, `GET /api/runtime-wiring/source-runtime/preview`
- Capability : `SOURCE_RUNTIME_PREVIEW`
- runtime_allowed_now : false | emits_act : false
- P11A+P29 — dry-run state, READONLY_PREVIEW_ONLY

### SettingsView.tsx — CONNECTED_TO_WORKBENCH_ONLY
- Endpoints : aucun (lecture config VITE)
- Capability : `WORKBENCH_CONFIG_DISPLAY`
- runtime_allowed_now : false | emits_act : false
- Affichage configuration env — pas d'appel API

### TranslationView.tsx — CONNECTED_TO_WORKBENCH_ONLY
- Endpoints : aucun (lib locale `runOSTradPipeline`)
- Capability : `OS_TRAD_LOCAL_PIPELINE`
- runtime_allowed_now : false | emits_act : false
- Pipeline OS Trad entièrement frontend — pas de backend

### WorldCallView.tsx — BLOCKED_ACTION_VIEW
- Endpoints : aucun (MOCK_WORLD_CALLS, MOCK_SOVEREIGN_TICKET)
- Capability : `ACTION_REQUEST_BLOCKED`
- x108_decision : `BLOCK_OR_HOLD_CONTEXT_ONLY`
- DRY_RUN ONLY — no real egress, real_action_blocked=true

### X108View.tsx — CONNECTED_TO_STATUS_ONLY
- Endpoint : `GET /health` (via getKernelStatus)
- Capability : `GOVERNANCE_KERNEL_STATUS`
- runtime_allowed_now : false | emits_act : false
- Health + invariants kernel — READONLY, pas de mutation

---

## Preuves NO ACT

| Invariant | Valeur |
|---|---|
| runtime_allowed_now | false (toutes vues) |
| emits_act | false (toutes vues) |
| decision_authority | KX108_ONLY (toutes vues) |
| memory_write | false |
| graph_write | false |
| kernel_mutation | false |
| zip_extraction | false |
| world_action | false |

---

## Fichiers produits

| Fichier | Rôle |
|---|---|
| `_runtime_wiring_preflight/P46_WORKBENCH_VIEW_INVENTORY_RAW.json` | Inventaire brut des 13 vues |
| `_runtime_wiring_preflight/P46_WORKBENCH_VIEW_COVERAGE_MAP.json` | Carte de couverture 100% |
| `runtime_wiring/source_runtime/workbench_view_coverage_classifier.py` | Classificateur P46 |
| `runtime_wiring/source_runtime/workbench_view_capability_map.py` | Map vue → capability/routes |
| `apps/obsidia_api/routes/os_map.py` | Enrichi avec champs P46 |
| `tests/test_workbench_view_coverage_p46.py` | Tests unitaires P46 |
| `tests/api/test_workbench_view_coverage_os_map_p46.py` | Tests API P46 |
| `docs/real_engine/P46_WORKBENCH_VIEWS_COVERAGE_REPORT.md` | Ce rapport |

---

## Limites restantes pour P47

- Les vues CONNECTED_TO_WORKBENCH_ONLY (SettingsView, TranslationView) n'ont pas d'endpoint backend — P47 pourrait câbler des routes OS Trad support si nécessaire.
- INTERNAL_UI_ONLY (OS3View) reste sur mock — câblage réel vers `/api/os3/tickets` possible en P47.
- Les 3 BLOCKED_ACTION_VIEW restent permanentes — aucun câblage autorisé sans SovereignTicket X-108.
- `workbench_view_coverage_percent` est maintenant exposé via `os-map/query` — P47 peut enrichir le filtre par vue.
