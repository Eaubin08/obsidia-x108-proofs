# Workbench V2 — Backend Status Report

**Date:** 2026-05-19
**Status:** BACKEND_STATUS_BY_MODULE_PASS

---

## Per-module status (default config: VITE_USE_MOCK_FALLBACK=true)

| Module | Status | Endpoint | Port |
|--------|--------|----------|------|
| ObsidiaShell | MOCK | /health | 8011 |
| Graphiti V20 | MOCK | /graph/v20/frozen/status | 8011 |
| X108 Engine | STUB | /api/x108/status | 8000 |
| Brody Runtime | STUB | /api/brody/chat | 8000 |
| ContextPacket API | STUB | /api/context | 8000 |
| OS3 API | STUB | /api/os3 | 8000 |
| Gencoin API | STUB | /api/gencoin | 8000 |
| WorldCall API | STUB | /api/worldcalls | 8000 |
| Blockchain Gate | STUB | /api/blockchain/status | 8000 |
| Memory Ledger | STUB | /api/memory | 8000 |
| OS Trad | STUB | /api/os-trad/translate | 8000 |
| IR Candidate | STUB | /api/ir/candidate | 8000 |
| OS Reverse | STUB | /api/os-reverse/project | 8000 |

---

## When VITE_USE_MOCK_FALLBACK=false

| Module | Status | Notes |
|--------|--------|-------|
| ObsidiaShell | LIVE (if running) | `cd obsidiashell-main && uvicorn ...` |
| Graphiti V20 | LIVE (if ObsidiaShell LIVE) | Frozen V20 context queries work |
| All others | OFFLINE/STUB | FastAPI adapter not yet created |

---

## No module claims to be LIVE when it is MOCK

The `probeAllModules()` function returns:
- `MOCK` when `VITE_USE_MOCK_FALLBACK=true`
- `LIVE` or `OFFLINE` when probing is enabled (8011 routes only)
- `STUB` for engine routes not yet implemented

Every panel displaying data shows its source: `LIVE / MOCK / STUB / OFFLINE`.

---

## To enable live ObsidiaShell

```powershell
cd path\to\obsidiashell-main
.venv_api8011\Scripts\uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011
```

Then set `VITE_USE_MOCK_FALLBACK=false` in `.env.local`.

---

## Mock fallback guarantee

If backend is absent or returns error:
- `safeFetch()` returns mock data
- Source is labeled `MOCK` in all panels
- UI continues to function fully
- No error propagated to user interface

Status: **MOCK_FALLBACK_READY**
