# P45 — Full Route Coverage Binding Report

**Date:** 2026-06-04
**Branch:** p43-unconnected-runtime-surface-audit
**Status:** P45_FULL_ROUTE_COVERAGE_100_READY
**Basé sur:** P44 — Critical Capability Binding

---

## Objectif

Classifier 100% des 147 routes API détectées par P37. Aucune route ne doit rester UNCLASSIFIED.

---

## Résultats de couverture

| Catégorie | Routes | % |
|---|---|---|
| CONNECTED_READONLY | 101 | 68.7% |
| CONNECTED_BLOCKED_ACTION | 16 | 10.9% |
| STATUS_ONLY | 21 | 14.3% |
| WORKBENCH_ONLY | 6 | 4.1% |
| INTERNAL_ONLY | 3 | 2.0% |
| ARCHIVE_ONLY | 0 | 0% |
| DO_NOT_BIND_EXPLICIT | 0 | 0% |
| **UNCLASSIFIED** | **0** | **0%** |
| **TOTAL** | **147** | **100%** |

**Coverage : 100.0% — P45_FULL_ROUTE_COVERAGE_100_READY** ✓

---

## Description des catégories

### CONNECTED_READONLY (101 routes)
Routes reliées au capability router, readonly, no ACT. Incluent :
- Toute la surface `/api/runtime-wiring/*` (source-runtime, os-map, os-trad)
- `/api/brody/chat` → BRODY_CHAT_ENTRYPOINT
- `/api/x108/*` (cognitive, math, memory replay, oracle, readonly-ingress, timeverse)
- `/api/os3/*` (tickets, replay)
- `/api/sigma/*` (6 routes evaluation)
- `/api/periphery/*` (brody, cognitive, context, graphiti, ingestion, os3, pipeline, gencoin, governance, education, feedback, interface, sigma, workflow)
- `/api/memory/*` (lecture seule : candidates, sources, ledger)
- `/api/adapters/*` (3 moniteurs)
- `/api/hexaflux/*` (2 routes)
- `/api/context/from-message`, `/api/translation/trace`, `/api/query`

### CONNECTED_BLOCKED_ACTION (16 routes)
Routes pouvant représenter une action, reliées à ACTION_REQUEST_BLOCKED ou X108 HOLD/BLOCK.
Toutes maintiennent `runtime_allowed_now=False`, `emits_act=False` :
- `/api/blockchain/world/*` (gateway, bus-dispatch, dry-run)
- `/api/blockchain/wallet/gate`, `/api/blockchain/policy/evaluate`
- `/api/blockchain/classifiers/fraud-check`, `/api/blockchain/sandbox/*`
- `/api/blockchain/signature/check`, `/api/blockchain/gencoin/compute`
- `/api/x108/memory/candidates/append`
- `/api/operator/governed-runtime`, `/api/periphery/operator/governed-runtime`
- `/api/bus/bus/signal`
- `/api/periphery/governance/agent-run`
- `/api/memory/candidate/from-message`

### STATUS_ONLY (21 routes)
Health, statuts, métriques, listes statiques. Sans hydratation ni routing capability.

### WORKBENCH_ONLY (6 routes)
Routes purement UI/preview : `/api/runtime-wiring/preview`, workbench, demo, operator panel.

### INTERNAL_ONLY (3 routes)
Infrastructure interne : audit events, bus bridge, interface log-event.

---

## Fichiers créés

### `runtime_wiring/source_runtime/route_coverage_classifier.py`
Classifie chaque route dans l'une des 7 catégories par lookup explicite puis règles préfixes.
Garantit que tous les champs de sécurité (`runtime_allowed_now=False`, `emits_act=False`,
`decision_authority=KX108_ONLY`) sont maintenus pour toute route classifiée.

### `runtime_wiring/source_runtime/route_capability_map.py`
Construit et cache la carte complète `route → classification` depuis l'inventaire P37.
Expose `build_route_capability_map()`, `get_route_classification()`, `get_coverage_summary()`.

### `apps/obsidia_api/routes/os_map.py` (mis à jour)
L'endpoint `POST /api/runtime-wiring/os-map/query` expose maintenant :
- `route_coverage_status`: FULL_COVERAGE ou PARTIAL_COVERAGE
- `route_coverage_percent`: 100.0
- `unclassified_routes_count`: 0
- `selected_routes_classified`: classification des routes sélectionnées par le chemin

---

## Routes actionnelles — Safety invariants

Pour les 16 routes `CONNECTED_BLOCKED_ACTION` :
- `runtime_allowed_now = False` sur toutes ✓
- `emits_act = False` sur toutes ✓
- `decision_authority = KX108_ONLY` sur toutes ✓
- `x108_decision = BLOCK_OR_HOLD_CONTEXT_ONLY` sur toutes ✓

---

## Tests P45

### `tests/test_full_route_coverage_p45.py` (10 tests)
1. Inventaire brut existe
2. Carte de couverture existe
3. Toutes routes ont une classification
4. `unclassified_count == 0`
5. `coverage_percent == 100.0`
6. `/api/brody/chat` → BRODY_CHAT_ENTRYPOINT
7. `/api/runtime-wiring/os-map/query` → CONNECTED_READONLY
8. Routes actionnelles : `runtime_allowed_now=False`
9. Routes actionnelles : `emits_act=False`
10. `decision_authority=KX108_ONLY` partout

### `tests/api/test_route_coverage_os_map_p45.py` (6 tests)
Tests via API `/api/runtime-wiring/os-map/query`

---

## Résultats validation

```
python -m pytest tests/test_full_route_coverage_p45.py tests/api/test_route_coverage_os_map_p45.py -q
→ 16 passed

python -m pytest tests/ -q
→ 3716 passed, 4 skipped

python scripts/check_forbidden_content.py → FORBIDDEN_CONTENT_PASS
python scripts/verify_recursive_manifest.py → MANIFEST_VERIFIED (7777 files)
```

---

## Limites restantes pour P46

La classification P45 couvre 100% des routes mais ne branche pas les routes dans le capability router.
Les routes `CONNECTED_READONLY` ont une capability SUGGÉRÉE mais ne sont pas toutes dans les templates.

Priorités P46 :
1. Ajouter `BRODY_FINAL_ANSWER` capability pour `brody_v1_4_12a_final_answer_adapter`
2. Ajouter capabilities X108 (`X108_COGNITIVE`, `X108_MATH`, `X108_MEMORY`)
3. Ajouter `OS3_AUDIT` pour les 7 routes OS3
4. Ajouter `MEMORY_CANDIDATE` pour les routes memory (lecture/création)
5. Route `os-map/status` → enrichir le status endpoint avec la couverture P45

---

*P45 — lecture seule, aucun ACT, aucune mutation kernel.*
