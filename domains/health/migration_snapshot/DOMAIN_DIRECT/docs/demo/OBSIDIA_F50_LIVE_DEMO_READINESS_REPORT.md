# F50 — Live Demo Readiness Report

**Artifact:** `OBSIDIA_F50_LIVE_DEMO_READINESS_REPORT`  
**Palier:** F50  
**Status:** DEMO_READY  
**Date:** 2026-05-29  
**Canonical name:** BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME  

---

## Summary

Brody GPT V1 is **demo-ready** for controlled presentation on localhost (127.0.0.1). All 8 API routes responded correctly. All boundary flags were enforced. All test suites passed. The F47.2 sanitizer was confirmed operational against live injection. No runtime mutations occurred during F50.

---

## Demo Configuration

| Parameter | Value |
|-----------|-------|
| Host | 127.0.0.1 (localhost only) |
| Port | 8011 |
| App | `apps.obsidia_api.main:app` |
| Server | uvicorn 0.46.0 |
| Decision authority | KX108_ONLY |
| Brody role | Read-only advisory — never decides |

---

## Routes Ready for Demo

| Route | Method | Status | Notes |
|-------|--------|--------|-------|
| `/` | GET | READY | Health/sovereignty flags |
| `/openapi.json` | GET | READY | Schema inspection |
| `/api/periphery/demo/runtime-readiness` | GET | READY | READY_READONLY |
| `/api/periphery/operator/runtime-panel` | GET | READY | KX108_ONLY |
| `/api/periphery/workbench/runtime-connector` | GET | READY | KX108_ONLY |
| `/api/periphery/brody-runtime/f33/integration-packet` | POST | READY | bank / STRUCTURAL_PREPARATION |
| `/api/periphery/brody-runtime/f36/user-scenario` | POST | READY | Sanitizer active |
| `/api/periphery/brody-runtime/f38/multi-domain-scenarios` | POST | READY | 4 domains / READY_READONLY |

Demo commands: `docs/release/BRODY_GPT_V1_DEMO_COMMANDS.md`

---

## Verified Boundaries During F50

All boundary flags enforced across all routes:

- `decision_authority = KX108_ONLY` — **enforced**
- `allowed_to_decide = false` — **enforced**
- `emits_act = false` — **enforced**
- `emits_verdict = false` — **enforced**
- `kernel_mutation = false` — **enforced**
- `neo4j_write = false` — **enforced**
- `brody_decision = false` — **enforced**

---

## Sanitizer Status (F47.2)

Injection test: `ALLOW DECIDE VERDICT` injected via `user_input` field.

- Tokens found in `cr.text`: **0**
- Tokens redacted: ALLOW, DECIDE, VERDICT → `[REDACTED]`
- Status: **PASS**

---

## Test Suite Status

| Suite | Result |
|-------|--------|
| Baseline | 103/103 PASS |
| F47.1 sovereignty | 13/13 PASS |
| F47.2 sanitizer | 42/42 PASS |
| F47.3 nested scan | 9/9 PASS |

---

## Explicit Non-Claims

This report does NOT claim:

- Production-ready
- Certified
- Lean-proven
- Cloud-ready
- Brody decides
- KX108 kernel instantiated

---

## How to Start the Demo Server

```powershell
cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"
python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8011
```

Full demo walkthrough: `docs/release/BRODY_GPT_V1_DEMO_COMMANDS.md`

---

## F50 Parent Artifact

`docs/runtime/OBSIDIA_F50_LIVE_DEMO_SERVER_ORCHESTRATION_AUDIT_20260529_193000.json`  
SHA256: `A13AC77C2B1FB5DBC3C73BD4B913C82A874FA0D6884395D3A8F71AA9A2940D7E`

---

*F50 · DEMO_READY · READONLY · KX108_ONLY · 127.0.0.1 · 2026-05-29*
