# Frontend / Backend Bridge Report

**Date:** 2026-05-19
**Status:** READY — mock fallback active, live bridge wired

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Obsidia Workbench (React + Tailwind, port 5173)    │
│                                                     │
│  src/api/obsidiaClient.ts                           │
│    ├── getBackendHealth()  ──────────────────────┐  │
│    ├── getKernelStatus()   (derived from health) │  │
│    ├── getGraphitiStatus() ──────────────────────┤  │
│    ├── getContextPacket()  ──────────────────────┤  │
│    ├── getAuditEvents()    ─────────────────┐    │  │
│    └── sendBrodyMessage()  (mock only)      │    │  │
└──────────────────────────────────────────────┼────┼──┘
                                               │    │
              ┌───────────────────────────────┘    │
              │    ┌──────────────────────────────┘
              ▼    ▼
┌─────────────────────────┐   ┌───────────────────────┐
│  ObsidiaShell (8011)    │   │  Engine API (8000)    │
│  agent_bridge.py        │   │  api_server/main.py   │
│  FastAPI + uvicorn      │   │  FastAPI + uvicorn    │
│                         │   │                       │
│  GET /health            │   │  GET /v1/audit/chain  │
│  GET /graph/v20/frozen/ │   │  GET /health          │
│    status               │   │  (optional)           │
│    context?q=...        │   └───────────────────────┘
│    metrics              │
│    readiness            │
│    entities             │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Neo4j (bolt 7688)      │
│  Graphiti V20 frozen    │
│  Read-only              │
└─────────────────────────┘
```

---

## Fallback Strategy

Every `obsidiaClient.ts` function uses `safeFetch()`:

```typescript
async function safeFetch<T>(url: string, fallback: T): Promise<Resolved<T>> {
  if (USE_MOCK) return { data: fallback, source: 'mock' }
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(TIMEOUT_MS) })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return { data: await res.json(), source: 'api' }
  } catch {
    return { data: fallback, source: 'mock' }
  }
}
```

- `source: 'api'` → live data from backend
- `source: 'mock'` → fallback from `mockFallback.ts`

The `BACKEND` panel in the workbench right panel shows which source is active.

---

## Files Created

```
src/api/
  contracts.ts       TypeScript types matching API response shapes
  mockFallback.ts    Fallback values (all sovereignty-invariant)
  obsidiaClient.ts   Main client: safeFetch + fallback logic

src/components/
  BackendStatusPanel.tsx  Real-time backend probe + sovereignty display
  RightPanel.tsx          Updated with BACKEND tab

BACKEND_DISCOVERY_REPORT.md
LOCAL_RUNBOOK.md
FRONTEND_BACKEND_BRIDGE_REPORT.md  (this file)
README_OBSIDIA_WORKBENCH.md
```

---

## Sovereignty enforcement

The bridge enforces the following at the TypeScript level:

- `sendBrodyMessage()` always returns `emits_act: false, memory_write: false, decision_authority: 'KX108_ONLY'`
- All fetch calls are `GET` — no POST/PUT/DELETE issued to backend
- `getContextPacket()` normalizes backend response into a `ContextPacket` with all `false`/`KX108_ONLY` fields
- `BackendStatusPanel` displays live invariant status (all green)

---

## Next steps to wire remaining mock-only endpoints

| Function | What to wire when ready |
|----------|------------------------|
| `sendBrodyMessage()` | POST `/brody/query` when Brody HTTP endpoint is added |
| `getMemoryCandidates()` | GET `/memory/candidates` |
| `getOS3Ticket()` | GET `/os3/ticket/{id}` |
| `getSovereignTickets()` | GET `/sovereign/tickets` |
| `getWorldCalls()` | GET `/worldcall/log` |
| `getGencoinLedger()` | GET `/gencoin/ledger` |
