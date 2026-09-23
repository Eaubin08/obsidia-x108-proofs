# Brody Runtime Module Usage Report — V5B

**Date:** 2026-05-19
**Status:** BRODY_RUNTIME_MODULE_USAGE_REPORT_PASS

---

## Real Modules Used (REAL_MODULE)

| Module | Function | Route |
|--------|----------|-------|
| `periphery.brody.brody_runtime_readonly` | `brody_respond()` | `POST /api/brody/chat` |
| `periphery.brody.brody_response_sanitizer` | `sanitize_brody_response()` | `POST /api/brody/chat` |
| `periphery.language.language_router` | `detect_language()`, `has_authority_claim()` | `POST /api/brody/chat`, `POST /api/translation/trace` |
| `periphery.context.context_packet_builder_v2` | `build_context_packet_v2()` | `POST /api/brody/chat`, `POST /api/context/from-message` |
| `periphery.x108_ingress.x108_context_boundary` | `check_x108_context_boundary()` | `POST /api/brody/chat` |
| `periphery.reverse_os.action_projection_readonly` | `project_action_readonly()` | `POST /api/brody/chat` |
| `periphery.memory.memory_candidate` | `build_memory_candidate_v2()` | `GET /api/memory` |
| `periphery.memory.memory_promotion_policy` | `evaluate_promotion_policy()` | `GET /api/memory` |
| `periphery.gencoin_ledger` | `read_ledger()` | `GET /api/gencoin` |

## Modules Still BACKEND_STUB

| Module | Reason |
|--------|--------|
| IR candidate builder | No `periphery/ir/` module exists. Frontend `irCandidateBuilder.ts` is the only implementation. |
| Symbolic alphabet | No Python equivalent. Frontend `symbolicAlphabet.ts` is the only implementation. |
| OS Reverse full pipeline | `project_action_readonly()` exists but requires structured IR input which is BACKEND_STUB. |
| Graphiti (via API) | `periphery.graphiti.graphiti_readonly_bridge:query_graphiti_readonly()` exists but requires Neo4j/Graphiti backend. Proxy to 8011 not implemented in API. |

## Source Labels per Route

| Route | Source |
|-------|--------|
| `GET /api/status` | REAL_BACKEND |
| `GET /api/x108/status` | REAL_BACKEND |
| `POST /api/brody/chat` | REAL_BACKEND |
| `POST /api/translation/trace` | BACKEND_STUB |
| `POST /api/context/from-message` | REAL_BACKEND |
| `GET /api/memory` | REAL_BACKEND |
| `GET /api/gencoin` | REAL_BACKEND |

**No route returns FRONTEND_MOCK.** The API is always honest about its source.
