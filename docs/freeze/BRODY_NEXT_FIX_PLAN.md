# Brody Next Fix Plan — V5B

**Date:** 2026-05-19
**Target:** Make Brody respond from real `periphery/` modules via FastAPI backend.
**Status:** PROPOSAL — no modifications made

---

## P0 — Critical: Create FastAPI Backend

### P0.1 Create `apps/obsidia_api/main.py`

FastAPI app with CORS, mounting routes, and startup verification:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.obsidia_api.routes import brody, translation, context, status, memory, gencoin

app = FastAPI(title="Obsidia API", version="V5B")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET","POST"])

app.include_router(status.router)
app.include_router(brody.router)
app.include_router(translation.router)
app.include_router(context.router)
app.include_router(memory.router)
app.include_router(gencoin.router)
```

### P0.2 Create `apps/obsidia_api/routes/brody.py`

```
POST /api/brody/chat
```
- Accepts `BrodyChatRequest` (message, language, session_id, context_refs)
- Calls `periphery/brody/brody_runtime_readonly.py:brody_respond(query, language, context_refs, confidence)`
- Calls `periphery/brody/brody_response_contract.py:BRODY_CONTRACT.validate()`
- Returns `BrodyChatResponse` with response_text, language, confidence, decision_authority=KX108_ONLY, readonly=True, source="REAL_BACKEND"

### P0.3 Create `apps/obsidia_api/routes/translation.py`

```
POST /api/translation/trace
```
- Accepts message text + language
- Calls `periphery/language/language_router.py:detect_language(text)`
- Calls `periphery/reverse_os/action_projection_readonly.py:project_action_readonly()`
- Builds IR candidate in Python (or imports from future `periphery/ir/`)
- Returns `TranslationTraceResponse` with alphabet units, IR candidate, OS reverse projection, source="REAL_BACKEND"

### P0.4 Create `apps/obsidia_api/routes/context.py`

```
POST /api/context/from-message
```
- Calls `periphery/context/context_packet_builder.py:build_context_packet()`
- Returns `ContextPacketResponse`

### P0.5 Create `apps/obsidia_api/routes/status.py`

```
GET /api/status
GET /api/x108/status
```
- Returns `StatusResponse` and `X108StatusResponse` with kernel info

### P0.6 Create `apps/obsidia_api/routes/memory.py`

```
GET /api/memory
```
- Calls `periphery/memory/memory_candidate.py:build_memory_candidate_v2()`
- Returns `MemoryResponse` with candidates

### P0.7 Create `apps/obsidia_api/routes/gencoin.py`

```
GET /api/gencoin
```
- Calls `periphery/gencoin_ledger.py:read_ledger()`
- Returns `GencoinResponse` with entries, is_real_token=False

### P0.8 Launch backend

```powershell
cd apps/obsidia_api
uvicorn main:app --host 127.0.0.1 --port 8000
```

---

## P1 — Important: Bridge Frontend to Backend

### P1.1 Update `sendBrodyMessage()` in `obsidiaClient.ts`

Replace the STUB with an actual fetch:

```typescript
export async function sendBrodyMessage(text: string, language: string = 'fr') {
  if (USE_MOCK) return mockFallbackResponse(text, language)
  try {
    const res = await fetch(`${ENGINE_BASE}/api/brody/chat`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text, language}),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return { data: await res.json(), source: 'api' }
  } catch {
    return { data: mockFallbackResponse(text, language), source: 'mock' }
  }
}
```

### P1.2 Update ChatView to use backend response

When backend returns `response_text`, display it. When backend is offline, fall back to `brodyResponseComposer.ts` with `source: 'backend_stub'` badge.

### P1.3 Update `getTranslationTrace()` to call real route

```typescript
export async function getTranslationTrace(text: string, language: string) {
  // Try POST /api/translation/trace → if success, source='api'
  // Fallback to osTradPipeline.ts → source='mock'
}
```

### P1.4 Add source badge to every response

Brody message bubbles should display:
- `REAL_BACKEND` (green) if response came from port 8000
- `BACKEND_STUB` (yellow) if backend is up but route is stub
- `FRONTEND_MOCK` (gray) if using brodyResponseComposer fallback

---

## P2 — Polish: UI Cleanup

### P2.1 Rename `brodyResponseComposer.ts` to `brodyFallbackComposer.ts`

Clarify that it's the fallback, not the primary source.

### P2.2 Add "Engine API (8000)" row to BackendStatusPanel

Currently only shows ObsidiaShell (8011). Add engine API probe.

### P2.3 Implement `GET /api/graphiti/status` as proxy

Route in FastAPI that proxies to `http://127.0.0.1:8011/graph/v20/frozen/status` — so the frontend only needs to talk to port 8000, not two servers.

### P2.4 Add `IRCandidateBuilder` in Python

Move `irCandidateBuilder.ts` logic to `periphery/ir/ir_candidate_builder.py` so IR candidates are backend-generated.

---

## Execution Order

1. P0.1 — `main.py`
2. P0.2 — `routes/brody.py` (Brody chat → THE critical path)
3. P0.4 — `routes/status.py` (needed for health probe)
4. P1.1 — Update `sendBrodyMessage()` frontend
5. P1.4 — Source badges
6. P0.3 — `routes/translation.py`
7. P1.3 — Update `getTranslationTrace()`
8. P0.5-P0.7 — Remaining routes (context, memory, gencoin)
9. P2.1-P2.4 — Polish

---

## What NOT to Change

- `sigma/guard.py`, `sigma/contracts.py`, `sigma/protocols.py`, `sigma/aggregation.py`
- `proofs/lean/`, `formal/tla/`, `merkle_seal.json`
- `periphery/brody/brody_response_contract.py` (absolute invariants)
- `periphery/brody/brody_runtime_readonly.py` (already correct)
- No real ACT, no memory write, no wallet, no chain tx

---

## Claude Prompt (paste to Claude Code)

```
BUILD FASTAPI BACKEND — OBSIDIA X108 V5B

Ne pas modifier les fichiers protégés.

Créer dans apps/obsidia_api/ :
- main.py (FastAPI + CORS + routers)
- routes/brody.py → POST /api/brody/chat
- routes/translation.py → POST /api/translation/trace
- routes/context.py → POST /api/context/from-message
- routes/status.py → GET /api/status, GET /api/x108/status
- routes/memory.py → GET /api/memory
- routes/gencoin.py → GET /api/gencoin

Chaque route appelle les vrais modules periphery/.
Réponses : decision_authority=KX108_ONLY, readonly=True, source="REAL_BACKEND".

Puis mettre à jour apps/obsidia-workbench/src/api/obsidiaClient.ts pour appeler port 8000 en premier, fallback mock en second.
Ajouter source badge (REAL_BACKEND / BACKEND_STUB / FRONTEND_MOCK) dans ChatView.

Lancer : uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000
```
