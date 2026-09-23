# Brody Real Backend Audit Report — V5B Audit

**Date:** 2026-05-19
**Auditor:** DeepSeek TUI (v0.8.17)
**Mode:** AUDIT_ONLY — no modifications
**Layer:** CONNECTORS — Brody/Workbench binding inspection

---

## Verdict

**BRODY_REAL_BACKEND_AUDIT_PARTIAL** — The backend API skeleton exists (contracts defined), but no FastAPI app is running. Brody responses are 100% frontend-composed. The bridge to real `periphery/` modules is planned but not built.

---

## Audit Matrix

| Question | Answer | Evidence |
|----------|--------|----------|
| Backend API exists? | **SKELETON** | `apps/obsidia_api/` has `contracts.py` + empty `routes/__init__.py`. No `main.py`, no FastAPI app, no uvicorn launch. |
| Endpoint `/api/brody/chat` exists? | **NO** | `obsidiaClient.ts:sendBrodyMessage()` returns `{response:''}` — stub only. No Python route. |
| Endpoint calls real periphery modules? | **NO** | No FastAPI routes exist. Periphery modules (`brody_respond`, `route_brody_language`, `build_context_packet`) are importable but never called from API. |
| Frontend calls backend first? | **NO — MOCK PRIMARY** | `brodyResponseComposer.ts` is the sole Brody response source. It contains 10 intent types × multiple hardcoded FR/EN responses. |
| Frontend mock still primary? | **YES** | `brodyResponseComposer.ts` detects intent via regex, picks from hardcoded arrays. `osTradPipeline.ts` builds traces entirely in TypeScript (`source:'MOCK'`). |
| Graphiti 8011 real readonly bridge? | **YES (if ObsidiaShell running)** | `VITE_OBSIDIA_API_BASE` defaults to `http://127.0.0.1:8011`. Frontend probes `/graph/v20/frozen/status`. If 8011 is up → LIVE. If down → MOCK fallback. |
| ContextPacket backend-generated? | **NO — FRONTEND MOCK** | `getContextPacket()` in `obsidiaClient.ts` fetches from Graphiti 8011 if available, but context packet assembly is frontend-only. |
| OS Trad / IR backend-generated? | **NO — FRONTEND MOCK** | `osTradPipeline.ts` + `irCandidateBuilder.ts` + `symbolicAlphabet.ts` + `osReverseProjection.ts` are all TypeScript-only. API stubs return `NEEDS_FASTAPI_ROUTE`. |
| Response language routing works? | **YES — FRONTEND** | `detectUserLanguage()` in `language.ts` detects FR/EN. `brodyResponseComposer.ts` picks FR or EN responses. |
| Authority escalation refusal works? | **YES — FRONTEND** | `irCandidateBuilder.ts` detects ACT/authorize/deploy keywords. `osTradPipeline.ts` sets `os_trad_status=BLOCKED` when risk flags detected. `ChatView.tsx` displays `allowed_to_decide=false`, `allowed_to_act=false`. |
| UI status badges honest? | **PARTIAL** | `BackendStatusPanel.tsx` shows Engine API (8000) as `MOCK` — honest. Brody status shows `MOCK` in ChatView header — honest. But Graphiti source label sometimes ambiguous. |

---

## Architecture Snapshot

```
┌─────────────────────────────────────────────────────────────────┐
│  FRONTEND (localhost:5173)                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ brodyResponseComposer.ts  ← PRIMARY Brody source          │  │
│  │ osTradPipeline.ts         ← PRIMARY Translation source    │  │
│  │ irCandidateBuilder.ts     ← TypeScript IR builder         │  │
│  │ osReverseProjection.ts    ← TypeScript projection         │  │
│  │ symbolicAlphabet.ts       ← TypeScript alphabet           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                           │ (planned, NOT built)                │
│                           ▼                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ obsidiaClient.ts  →  sendBrodyMessage()  = STUB (empty)   │  │
│  │                  →  getTranslationTrace() = NEEDS_ROUTE    │  │
│  │                  →  getIRCandidate()      = NEEDS_ROUTE    │  │
│  │                  →  getContextPacket()    → Graphiti 8011  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  BACKEND (planned, NOT implemented)                             │
│  apps/obsidia_api/                                              │
│  ├── contracts.py      ✓  (Pydantic models complete)            │
│  ├── routes/__init__.py  (empty — no routes)                    │
│  ├── main.py           ✗  (MISSING — no FastAPI app)            │
│  └── routes/brody.py   ✗  (MISSING)                             │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  PERIPHERY MODULES (importable but NOT called from API)         │
│  periphery/brody/brody_runtime_readonly.py  → brody_respond()   │
│  periphery/brody/brody_language_router.py   → route_brody_lang()│
│  periphery/brody/brody_response_contract.py → BRODY_CONTRACT    │
│  periphery/context/context_packet_builder.py→ build_context_pkt │
│  periphery/language/language_router.py      → detect_language() │
│  periphery/reverse_os/action_projection.py  → project_action()  │
│  periphery/memory/memory_candidate.py       → build_candidate() │
│  periphery/gencoin_ledger.py                → read_ledger()     │
│  periphery/blockchain/blockchain_action_classifier.py           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Sovereignty Compliance (Frontend)

The frontend correctly displays:
- `decision_authority=KX108_ONLY` on every Brody message
- `readonly=true`, `emits_act=false`, `memory_write=false`
- `allowed_to_decide=false`, `allowed_to_act=false` in trace panels
- `ADVISORY ONLY` badge
- "no real action" lock icon in ChatView header
- `BACKEND: MOCK` status in ChatView header

---

## Conclusion

The frontend is sovereignty-compliant but Brody is frontend-composed, not backend-driven. The FastAPI backend at port 8000 is a **skeleton** — contracts defined, routes empty, no `main.py`. The `BACKEND_RUNTIME_DISCOVERY_REPORT.md` maps the correct `periphery/` modules to routes, but the implementation has not been built yet.

**What exists:** Contracts, discovery report, frontend mock pipeline, Graphiti 8011 proxy.
**What's missing:** FastAPI `main.py`, route implementations calling `periphery/` modules, Brody response coming from `brody_respond()` instead of `brodyResponseComposer.ts`.
