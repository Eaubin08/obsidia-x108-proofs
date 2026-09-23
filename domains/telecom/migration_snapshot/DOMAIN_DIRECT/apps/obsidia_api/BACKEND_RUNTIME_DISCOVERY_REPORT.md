# Backend Runtime Discovery Report

**Date:** 2026-05-19
**Status:** BACKEND_RUNTIME_DISCOVERY_COMPLETE

---

## Objective

Map 15 frontend functions in `apps/obsidia-workbench/src/api/obsidiaClient.ts`
to real Python modules in `periphery/`. Determine which routes can serve `REAL_BACKEND`
data and which must fall back to `BACKEND_STUB`.

---

## Function → Module mapping

| # | Frontend function | Python module | Callable | Status |
|---|-------------------|---------------|----------|--------|
| 1 | `sendBrodyMessage()` | `periphery/brody/brody_runtime_readonly.py:brody_respond()` + `periphery/brody/brody_language_router.py:route_brody_language()` | YES | REAL_BACKEND |
| 2 | `getTranslationTrace()` | `periphery/language/language_router.py:route_language()` + `periphery/reverse_os/action_projection_readonly.py:project_action_readonly()` | YES | REAL_BACKEND |
| 3 | `getIRCandidate()` | No direct Python equivalent — logic lives in frontend `src/lib/irCandidateBuilder.ts` | PARTIAL | BACKEND_STUB (IR built in Python from language analysis) |
| 4 | `getOSReverseProjection()` | `periphery/reverse_os/action_projection_readonly.py:project_action_readonly()` | YES | REAL_BACKEND |
| 5 | `getContextPacket()` | `periphery/context/context_packet_builder.py:build_context_packet()` | YES | REAL_BACKEND |
| 6 | `getGraphitiStatus()` | ObsidiaShell proxy — `GET http://127.0.0.1:8011/graph/v20/frozen/status` | PROXY | REAL_BACKEND (if ObsidiaShell up), else BACKEND_STUB |
| 7 | `getGraphitiContext()` | ObsidiaShell proxy — `GET http://127.0.0.1:8011/graph/v20/frozen/context` | PROXY | REAL_BACKEND (if ObsidiaShell up), else BACKEND_STUB |
| 8 | `getMemoryCandidates()` | `periphery/memory/memory_candidate.py:build_memory_candidate_v2()` | YES | REAL_BACKEND |
| 9 | `getX108ReadonlyStatus()` | Derived from `periphery/brody/brody_response_contract.py:BRODY_CONTRACT` + kernel constants | YES | REAL_BACKEND |
| 10 | `getOS3Tickets()` | `periphery/os3_ticket.py:OS3ProofTicket` (schema only — build_os3_ticket needs full stack) | PARTIAL | BACKEND_STUB |
| 11 | `getGencoinLedger()` | `periphery/gencoin_ledger.py:read_ledger()` | YES | REAL_BACKEND (reads audit/gencoin_ledger.jsonl if exists, else stub) |
| 12 | `getWorldCalls()` | `periphery/world_action_gateway.py:WorldActionReadiness` (dry-run stub) | PARTIAL | BACKEND_STUB |
| 13 | `getSovereignTickets()` | `periphery/os3_ticket.py:OS3ProofTicket` schema only | PARTIAL | BACKEND_STUB |
| 14 | `getBlockchainStatus()` | `periphery/blockchain/blockchain_action_classifier.py:classify_blockchain_action()` | YES | REAL_BACKEND |
| 15 | `getAuditEvents()` | `periphery/brody_memory_readonly/` + connectors — no direct aggregator | PARTIAL | BACKEND_STUB |

---

## Real backend routes (port 8000)

| Route | Method | Source |
|-------|--------|--------|
| `GET  /api/status` | GET | REAL_BACKEND |
| `GET  /api/x108/status` | GET | REAL_BACKEND |
| `POST /api/brody/chat` | POST | REAL_BACKEND |
| `POST /api/translation/trace` | POST | REAL_BACKEND |
| `GET  /api/translation/alphabet` | GET | REAL_BACKEND |
| `POST /api/context/from-message` | POST | REAL_BACKEND |
| `GET  /api/context/{packet_id}` | GET | BACKEND_STUB (no persistent store) |
| `GET  /api/graphiti/status` | GET | PROXY → 8011 (BACKEND_STUB if 8011 offline) |
| `GET  /api/graphiti/context` | GET | PROXY → 8011 (BACKEND_STUB if 8011 offline) |
| `GET  /api/memory` | GET | REAL_BACKEND |
| `GET  /api/os3` | GET | BACKEND_STUB |
| `GET  /api/gencoin` | GET | REAL_BACKEND (reads ledger file) |
| `GET  /api/worldcalls` | GET | BACKEND_STUB |
| `GET  /api/blockchain/status` | GET | REAL_BACKEND |
| `GET  /api/audit` | GET | BACKEND_STUB |

---

## Periphery modules available

### FOUND — directly callable

| Module | Key functions | Notes |
|--------|---------------|-------|
| `periphery/brody/brody_runtime_readonly.py` | `brody_respond(query, language, context_refs, confidence)` | Returns `BrodyResponse` — validates `BRODY_CONTRACT` |
| `periphery/brody/brody_language_router.py` | `route_brody_language(query_id, language_code)` | Routes to language-specific chain |
| `periphery/brody/brody_response_contract.py` | `BRODY_CONTRACT.validate()` | Invariants: readonly, no ACT, no verdict |
| `periphery/brody/brody_context_query.py` | `build_context_query(query_id, text, language)` | Builds context query object |
| `periphery/language/language_router.py` | `detect_language(text)`, `has_authority_claim(text)`, `route_language(text)` | FR/EN detection + authority check |
| `periphery/reverse_os/action_projection_readonly.py` | `project_action_readonly(projection_id, intent, context)` | `_FORBIDDEN_TOKENS` enforced; returns `ActionProjection` |
| `periphery/context/context_packet_builder.py` | `build_context_packet(action_id, signals, status)` | Returns `ContextPacket` with hash |
| `periphery/memory/memory_candidate.py` | `build_memory_candidate_v2(source_id, source_type, content)` | Returns `MemoryCandidate` CANDIDATE_ONLY |
| `periphery/memory/memory_source_types.py` | `MemorySourceType`, `MemoryCandidateStatus` enums | — |
| `periphery/gencoin_ledger.py` | `read_ledger()` | Reads `audit/gencoin_ledger.jsonl`; returns `[]` if file absent |
| `periphery/blockchain/blockchain_action_classifier.py` | `classify_blockchain_action(action_id, action_class)` | Returns `BlockchainActionDecision` |
| `periphery/os3_ticket.py` | `OS3ProofTicket`, `ticket_is_valid()` | Build requires full action stack — stub only for API |
| `periphery/world_action_gateway.py` | `evaluate_world_action_readiness()` | Needs ticket + envelope — stub only for API |

### MISSING — no periphery module found

| Missing | Notes |
|---------|-------|
| `periphery/os_trad/` | IR building, alphabet tokenization live in frontend only |
| `periphery/ir/` | No Python IR candidate builder |
| `periphery/alphabet/` | No Python symbolic alphabet |
| Audit event aggregator | Partial in `periphery/brody_memory_readonly/` but no HTTP-ready aggregator |

---

## Source labels after binding

| Condition | Label |
|-----------|-------|
| Backend route called, periphery returned data | `REAL_BACKEND` |
| Backend route called, periphery unavailable / ImportError | `BACKEND_STUB` |
| Backend unreachable from frontend, mock returned | `FRONTEND_MOCK` |
| ObsidiaShell proxy success | `REAL_BACKEND` |
| ObsidiaShell proxy failure | `BACKEND_STUB` |

---

## Sovereignty constraints (unchanged)

All backend routes are READ-ONLY. The backend:
- NEVER writes to memory
- NEVER writes to Graphiti / Neo4j
- NEVER emits ACT / HOLD / BLOCK / DECIDE / VERDICT from Brody
- NEVER connects a wallet or signs a transaction
- NEVER triggers a real WorldAction
- All `decision_authority = KX108_ONLY`

Status: **BACKEND_RUNTIME_DISCOVERY_COMPLETE**
