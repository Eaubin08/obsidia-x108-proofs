# Backend Discovery Report — Obsidia Workbench

**Date:** 2026-05-19
**Scope:** `obsidia-engine-proof-core/` — FastAPI/Flask/uvicorn patterns

---

## 1. ObsidiaShell API Gateway ✅ PRIMARY

**File:** `obsidiashell-main/obsidia_core/agent_bridge.py`
**Framework:** FastAPI + uvicorn
**Port:** `8011` (confirmed from log files `obsidiashell_gateway_v20_canonical_ui_8011.out.log`)
**Venv:** `.venv_api8011/`
**CORS:** `allow_origins=["*"]` — no CORS issue for workbench

### Available Endpoints (read-only subset relevant to workbench)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Gateway health + service status |
| `/graph/v20/counts` | GET | Node/relation/episode counts |
| `/graph/v20/frozen/status` | GET | Frozen V20 status |
| `/graph/v20/frozen/context` | GET | Context query `?q=...&limit=N` |
| `/graph/v20/frozen/entities` | GET | Entity list `?q=...&limit=N` |
| `/graph/v20/frozen/relations` | GET | Relation list |
| `/graph/v20/frozen/episodes` | GET | Episode list |
| `/graph/v20/frozen/metrics` | GET | Counts + version |
| `/graph/v20/frozen/readiness` | GET | Readiness check |
| `/graph/v20/frozen/evidence` | GET | Evidence nodes |
| `/graph/v20/frozen/manifest` | GET | Freeze manifest |

### How to start

```powershell
cd C:\Users\User\Desktop\obsidia-engine-proof-core\obsidiashell-main
.venv_api8011\Scripts\uvicorn obsidia_core.agent_bridge:app `
  --host 127.0.0.1 --port 8011 --reload
```

### OpenAPI spec

Captured at: `obsidia-engine-proof-core/_BRODY_OPENAPI_8011.json`
Interactive docs when running: `http://127.0.0.1:8011/docs`

---

## 2. Engine Decision API — SECONDARY

**File:** `engine/api_server/main.py`
**Framework:** FastAPI
**Port:** Not fixed in code (likely 8000 based on uvicorn default)
**Auth:** `OBSIDIA_API_KEY` env var (optional)

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Engine status |
| `/v1/decision` | POST | Governance decision pipeline |
| `/v1/replay/{trace_id}` | GET | Replay stored trace |
| `/v1/audit/chain` | GET | Audit chain |
| `/auth/token` | POST | JWT mint |

### Note

This API requires `unified_interface.pipeline` and `obsidia_kernel.contract` modules which are part of the proof core. Start command not confirmed — workbench treats it as optional.

---

## 3. No Brody HTTP Endpoint Found

No dedicated `/brody` or `/context` endpoint was found in either server. Brody responses in the workbench are purely advisory mock responses. When a real Brody HTTP endpoint is available, update `obsidiaClient.ts::sendBrodyMessage()`.

---

## 4. Workbench API Mapping

| `obsidiaClient.ts` function | Backend endpoint | Fallback |
|----------------------------|-----------------|---------|
| `getBackendHealth()` | `GET :8011/health` | `MOCK_HEALTH` |
| `getKernelStatus()` | derived from health | `KERNEL_STATUS` |
| `getGraphitiStatus()` | `GET :8011/graph/v20/frozen/status` | `MOCK_GRAPHITI_STATUS` |
| `getGraphitiReadiness()` | `GET :8011/graph/v20/frozen/readiness` | `MOCK_GRAPHITI_READINESS` |
| `getContextPacket(q)` | `GET :8011/graph/v20/frozen/context?q=...` | `MOCK_CONTEXT_PACKET` |
| `getAuditEvents()` | `GET :8000/v1/audit/chain` | `MOCK_AUDIT_CHAIN` |
| `sendBrodyMessage()` | *no endpoint — mock only* | advisory mock |
| `getOS3Ticket()` | *no endpoint — mock only* | `MOCK_OS3_TICKET` |
| `getSovereignTickets()` | *no endpoint — mock only* | `MOCK_SOVEREIGN_TICKET` |
| `getWorldCalls()` | *no endpoint — mock only* | `MOCK_WORLD_CALLS` |
| `getMemoryCandidates()` | *no endpoint — mock only* | `MOCK_MEMORY_CANDIDATES` |
| `getGencoinLedger()` | *no endpoint — mock only* | `MOCK_GENCOIN` |

---

## 5. Sovereignty Constraints

All backend calls from the workbench are GET (read-only). No mutation. No wallet. No real action. `real_chain_action_allowed=false` enforced client-side.
