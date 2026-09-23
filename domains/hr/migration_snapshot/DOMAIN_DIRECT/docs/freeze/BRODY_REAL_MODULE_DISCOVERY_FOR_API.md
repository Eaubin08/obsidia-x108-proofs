# Brody Real Module Discovery for API — V5B

**Date:** 2026-05-19
**Status:** BRODY_REAL_MODULE_DISCOVERY_PASS

---

## Module Inventory

| Module | Key Functions | Status |
|--------|---------------|--------|
| `periphery.brody.brody_runtime_readonly` | `brody_respond(query, language, context_refs, confidence)` → `BrodyResponse` | YES |
| `periphery.brody.brody_response_contract` | `BrodyResponseContract` — invariants: KX108_ONLY, advisory_only, no ACT | YES |
| `periphery.brody.brody_response_sanitizer` | `sanitize_brody_response(response)` → `SanitizedResponse` | YES |
| `periphery.brody.brody_language_router` | `route_brody_language(query_id, language_code)` | YES |
| `periphery.language.language_router` | `detect_language(text)`, `route_language(text)`, `has_authority_claim(text)` | YES |
| `periphery.context.context_packet_builder_v2` | `build_context_packet_v2(query, language, context_items)` → `ContextPacketV2` | YES |
| `periphery.x108_ingress.x108_context_boundary` | `check_x108_context_boundary(packet_dict)` → `BoundaryCheckResult` | YES |
| `periphery.reverse_os.action_projection_readonly` | `project_action_readonly(projection_id, intent, context)` | YES |
| `periphery.memory.memory_candidate` | `build_memory_candidate_v2(source_id, source_type, content)` → `MemoryCandidate` | YES |
| `periphery.memory.memory_promotion_policy` | `evaluate_promotion_policy(candidate)` → `PromotionDecision` | YES |
| `periphery.memory.memory_source_types` | `MemorySourceType`, `MemoryCandidateStatus` enums | YES |
| `periphery.graphiti.graphiti_readonly_bridge` | `query_graphiti_readonly(query_id, query, max_nodes)` → `GraphitiContextResult` | YES |
| `periphery.os3_ticket` | `OS3ProofTicket` dataclass | YES |
| `periphery.gencoin_ledger` | `read_ledger()` → `list[dict]` | YES |
| `periphery.common` | `ActionCandidate` dataclass | YES |
| `periphery.interface.interface_state_packet` | `InterfaceStatePacket` dataclass | YES |

---

## Modules NOT available in Python (BACKEND_STUB needed)

| Module | Reason |
|--------|--------|
| IR candidate builder | No `periphery/ir/` — logic exists only in frontend `irCandidateBuilder.ts` |
| Symbolic alphabet | No `periphery/alphabet/` — logic exists only in frontend `symbolicAlphabet.ts` |
| OS Reverse projection | Module exists but `project_action_readonly` requires structured IR input |
| Cognitive trees activation | Modules exist but require context packet as input |

**Fallback rule:** If a module is not available, the API route returns `source="BACKEND_STUB"` with a minimal but honest response. Never claim `REAL_BACKEND` when using stubs.

---

## API-Ready Routes

| Route | Real Module Available | Status |
|-------|----------------------|--------|
| `POST /api/brody/chat` | `brody_respond` + `detect_language` + `build_context_packet_v2` | REAL_BACKEND |
| `POST /api/translation/trace` | `detect_language` + `project_action_readonly` (partial) | BACKEND_STUB (IR/alphabet missing) |
| `POST /api/context/from-message` | `build_context_packet_v2` | REAL_BACKEND |
| `GET /api/status` | N/A (static) | REAL_BACKEND |
| `GET /api/memory` | `build_memory_candidate_v2` | REAL_BACKEND |
| `GET /api/gencoin` | `read_ledger` | REAL_BACKEND |
