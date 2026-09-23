# Backend Binding Plan — X108 Proofs

**Date:** 2026-05-19
**Status:** V2 — includes OS Trad / IR / OS Reverse endpoints

---

## Frontend functions → Backend mapping

| Function | Current Status | Source module | Future endpoint | Constraint |
|----------|---------------|---------------|-----------------|-----------|
| `getKernelStatus()` | LIVE (ObsidiaShell /health) | `periphery/brody/brody_runtime_readonly.py` | `GET /api/x108/status` | readonly |
| `getBackendHealth()` | LIVE (ObsidiaShell /health) | ObsidiaShell core | `GET /health` | readonly |
| `getGraphitiStatus()` | LIVE (ObsidiaShell /graph/v20/frozen/status) | Graphiti V20 | existing | readonly |
| `getGraphitiReadiness()` | LIVE (ObsidiaShell /graph/v20/frozen/readiness) | Graphiti V20 | existing | readonly |
| `getGraphitiMetrics()` | LIVE (ObsidiaShell /graph/v20/frozen/metrics) | Graphiti V20 | existing | readonly |
| `getContextPacket()` | LIVE (ObsidiaShell /graph/v20/frozen/context) | `periphery/context/context_packet_builder_v2.py` | existing | readonly |
| `sendBrodyMessage()` | STUB (composer in frontend) | `periphery/brody/brody_runtime_readonly.py` | `POST /api/brody/chat` | advisory_only |
| `getOS3Ticket()` | MOCK_ONLY | `periphery/os3_ticket.py` | `GET /api/os3/tickets` | readonly |
| `getSovereignTickets()` | MOCK_ONLY | `periphery/world_calls/` | `GET /api/worldcalls/sovereign` | readonly |
| `getWorldCalls()` | MOCK_ONLY | `periphery/world_action_gateway.py` | `GET /api/worldcalls` | dry_run_only |
| `getMemoryCandidates()` | MOCK_ONLY | `periphery/brody_memory_readonly/` | `GET /api/memory/candidates` | readonly |
| `getGencoinLedger()` | MOCK_ONLY | `periphery/gencoin_ledger.py` | `GET /api/gencoin/ledger` | readonly |
| `getAuditEvents()` | MOCK (engine /v1/audit/chain) | `periphery/world_action_gateway.py` | `GET /api/audit/events` | readonly |
| `getTranslationTrace()` | STUB | periphery/language/language_router.py + new | `POST /api/os-trad/translate` | advisory_only |
| `getIRCandidate()` | STUB | new periphery/ir module needed | `POST /api/ir/candidate` | allowed_to_decide=false |
| `getOSReverseProjection()` | STUB | `periphery/reverse_os/action_projection_readonly.py` | `POST /api/os-reverse/project` | advisory_only |
| `getAlphabetUnits()` | STUB | new periphery/alphabet module needed | `GET /api/alphabet/units` | readonly |

---

## Status legend

| Status | Meaning |
|--------|---------|
| LIVE | Connected to real backend endpoint |
| MOCK_ONLY | Always returns mock data regardless of VITE_USE_MOCK_FALLBACK |
| STUB | Function exists but returns null/empty — needs FastAPI route |
| NEEDS_FASTAPI_ROUTE | Backend module exists in Python but no HTTP endpoint yet |

---

## ObsidiaShell endpoints (port 8011) — already live

| Endpoint | Status |
|----------|--------|
| `GET /health` | LIVE |
| `GET /graph/v20/frozen/status` | LIVE |
| `GET /graph/v20/frozen/readiness` | LIVE |
| `GET /graph/v20/frozen/metrics` | LIVE |
| `GET /graph/v20/frozen/context?q=...` | LIVE |

---

## OS Trad / IR / OS Reverse — future endpoints

| Endpoint | Maps to | Source |
|----------|---------|--------|
| `POST /api/os-trad/translate` | Language detection + intent structuring | `periphery/language/language_router.py` |
| `POST /api/ir/candidate` | IR candidate builder | new module needed |
| `POST /api/os-reverse/project` | Reverse projection | `periphery/reverse_os/action_projection_readonly.py` |
| `GET /api/alphabet/units` | Symbolic tokenization | new module needed |
| `POST /api/context/from-ir` | Context packet from IR | `periphery/context/context_packet_builder_v2.py` |
| `GET /api/brody/language-route` | Brody language routing | `periphery/brody/brody_language_router.py` |

---

## All endpoints are read-only / dry-run

- No mutation endpoints
- No memory write endpoints
- No wallet/chain endpoints
- No ACT emission
- decision_authority = KX108_ONLY for all
