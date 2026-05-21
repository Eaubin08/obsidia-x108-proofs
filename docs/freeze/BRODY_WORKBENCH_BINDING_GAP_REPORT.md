# Brody Workbench Binding Gap Report

**Date:** 2026-05-19
**Status:** GAP ANALYSIS — classifies each module binding status

---

## Classification Legend

| Label | Meaning |
|-------|---------|
| REAL_BACKEND | Backend route exists, calls periphery module, returns real data |
| BACKEND_STUB | Backend route exists, returns static/simulated data |
| PROXY | Frontend proxies to external server (ObsidiaShell 8011) |
| FRONTEND_MOCK | Response composed entirely in TypeScript, no backend call |
| NOT_CONNECTED | No frontend→backend path exists |
| MISSING | Module/route not yet created |

---

## Component Binding Status

### Brody chat
**Status:** FRONTEND_MOCK
- Primary source: `brodyResponseComposer.ts` — hardcoded FR/EN responses per intent
- `sendBrodyMessage()` in `obsidiaClient.ts` returns empty string — STUB
- No Python route at `/api/brody/chat`
- No call to `periphery/brody/brody_runtime_readonly.py:brody_respond()`

### Language router
**Status:** FRONTEND_MOCK
- `detectUserLanguage()` in `language.ts` detects FR/EN via keyword matching
- No call to `periphery/language/language_router.py:route_language()`
- BrodyResponseComposer hardcodes FR and EN response pools

### OS Trad
**Status:** FRONTEND_MOCK
- `osTradPipeline.ts` runs entirely in TypeScript
- `buildAlphabetUnits()` in `symbolicAlphabet.ts` — TypeScript only
- `getTranslationTrace()` in `obsidiaClient.ts` returns `NEEDS_FASTAPI_ROUTE`
- No Python route at `/api/translation/trace`

### Symbolic alphabet
**Status:** FRONTEND_MOCK
- `symbolicAlphabet.ts` — TypeScript regex tokenizer
- No Python equivalent in `periphery/`

### IR candidate
**Status:** FRONTEND_MOCK
- `irCandidateBuilder.ts` — TypeScript intent + entity extraction
- `getIRCandidate()` returns `NEEDS_FASTAPI_ROUTE`
- No Python `periphery/ir/` module exists

### OS Reverse
**Status:** FRONTEND_MOCK
- `osReverseProjection.ts` — TypeScript projection builder
- `getOSReverseProjection()` returns `NEEDS_FASTAPI_ROUTE`
- Python module exists: `periphery/reverse_os/action_projection_readonly.py:project_action_readonly()` — but never called

### ContextPacket
**Status:** PROXY (if 8011 up) / FRONTEND_MOCK (if 8011 down)
- `getContextPacket()` fetches from Graphiti 8011 `/graph/v20/frozen/context`
- If 8011 down → `mockFallback.ts` MOCK_CONTEXT_PACKET used
- Assembly is frontend-only — `periphery/context/context_packet_builder.py` never called

### Graphiti V20 readonly
**Status:** PROXY (if 8011 up) / MOCK (if 8011 down)
- `VITE_OBSIDIA_API_BASE` = `http://127.0.0.1:8011`
- Routes: `/graph/v20/frozen/status`, `/context`, `/search`, `/metrics`, `/readiness`
- `backendProbe.ts` probes port 8011 — if live → status=LIVE
- If 8011 offline → all mock fallbacks active
- Python module exists: `periphery/graphiti/graphiti_readonly_bridge.py:query_graphiti_readonly()` — but never called from API

### X108 readonly boundary
**Status:** FRONTEND_MOCK (display) / NOT_CONNECTED (backend)
- `ChatView.tsx` displays `decision_authority=KX108_ONLY`, `readonly=true`
- `x108_context_boundary.py:check_x108_context_boundary()` exists — never called from API
- No route at `/api/x108/boundary`

### OS3 ticket viewer
**Status:** FRONTEND_MOCK
- `getOS3Ticket()` in `obsidiaClient.ts` → returns `mock.MOCK_OS3_TICKET` directly
- No backend route. `os3_ticket.py:OS3ProofTicket` schema exists — never called

### Gencoin ledger
**Status:** FRONTEND_MOCK
- `getGencoinLedger()` → returns `mock.MOCK_GENCOIN` directly
- `periphery/gencoin_ledger.py:read_ledger()` exists — never called from API
- No route at `/api/gencoin`

### WorldCall gateway
**Status:** FRONTEND_MOCK
- `getWorldCalls()` → returns `mock.MOCK_WORLD_CALLS` directly
- `periphery/world_action_gateway.py:evaluate_world_action_readiness()` exists — never called

### Memory candidate ledger
**Status:** FRONTEND_MOCK
- `getMemoryCandidates()` → returns `mock.MOCK_MEMORY_CANDIDATES` directly
- `periphery/memory/memory_candidate.py:build_memory_candidate_v2()` exists — never called from API

### Audit events
**Status:** PROXY (if 8000 up) / FRONTEND_MOCK (if down)
- `getAuditEvents()` → fetches `http://127.0.0.1:8000/v1/audit/chain`
- Falls back to `mock.MOCK_AUDIT_CHAIN`
- No route at `/api/audit` in API skeleton

### Backend status panel
**Status:** REAL_BACKEND (ObsidiaShell 8011) / MOCK (8000)
- `BackendStatusPanel.tsx` probes 8011 health → honest
- Engine API (8000) always shows `MOCK` — honest
- Invariants displayed: readonly, auto-promo, graphiti write, worldaction dry-run, real chain action, decision_authority


## Summary Count

| Status | Count | Components |
|--------|-------|------------|
| REAL_BACKEND | 0 | — (no backend API running) |
| PROXY | 2 | ContextPacket (via 8011), Graphiti V20 (via 8011) |
| BACKEND_STUB | 0 | — |
| FRONTEND_MOCK | 11 | Brody chat, Language router, OS Trad, Alphabet, IR, OS Reverse, X108 boundary, OS3, Gencoin, WorldCall, Memory |
| NOT_CONNECTED | 0 | — |
| MISSING | 1 | FastAPI main.py (entire backend) |
