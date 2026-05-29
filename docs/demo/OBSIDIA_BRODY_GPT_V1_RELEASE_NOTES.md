# Brody GPT V1 — Release Notes

**Version:** V1.0.0-RC-CLOSED  
**Canonical name:** `BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME`  
**Sealed at:** F42 · HEAD b67b2c3 · Tag: BRODY_F41_PUBLIC_INVESTOR_DEMO_NARRATIVE_PACK_PALIER_20260529  
**Status:** V1_CLOSED · AUDIT_READY · RUNTIME_SMOKE_PROVEN · LIVE_SERVER_PROVEN  
**Date:** 2026-05-29

---

## Summary

Brody GPT V1 is the first closed, auditable version of the Brody advisory runtime. It delivers a read-only, multi-domain advisory component with 7 runtime surfaces, 7 API routes, 4 domain support, and a verifiable boundary contract enforced at three independent layers.

**No sovereign decision. No state mutation. No memory write. KX108_ONLY decides.**

---

## Palier Changelog (F24 → F41)

### Foundation layer

#### F24 — Deferred Block Reconciliation
- Reconciled deferred blocks from prior paliers
- Established clean baseline for Brody controlled runtime build

#### F31 — Cleanup Untracked Debt
- Removed untracked technical debt
- Clean repo state established for F32+

---

### Runtime layer (F32→F38)

#### F32 — Full Runtime Integration Readonly Packet
- **7-surface integration packet** (`sigma_dispatcher`, `tree_signal_packet`, `monitoring_adapters`, `operator_view_packet`, `brody_runtime_context`, `workflow_governance_readonly`, `neo4j_guide_bridge`)
- Internal `build_brody_full_runtime_integration_packet()` function
- BOUNDARY dict (15 flags) established
- 17 unit tests

#### F33 — Runtime Entrypoint Readonly
- HTTP route `POST /api/periphery/brody-runtime/f33/integration-packet`
- `call_brody_runtime_entrypoint()` exposed via FastAPI
- Validates 7 surfaces READY_READONLY
- 12 unit tests

#### F34 — Live Route Smoke API Contract
- Full API contract smoke (73 checks, TestClient)
- Validates status codes, content-type, all boundary flags, forbidden tokens
- Smoke script: `smoke_f34_live_route_contract_readonly.py`

#### F34B — True Live Uvicorn Server Smoke
- First live-server proof: port 9010, source `REAL_BACKEND`
- SHA256: `20A27188...` · 73/73 checks
- Proves boundary holds on a real uvicorn process, not just TestClient

#### F35 — Operator Demo Workbench Surfaces
- 3 new routes: `operator/runtime-panel` (JSON + HTML), `demo/runtime-readiness`, `workbench/runtime-connector`
- HTML operator dashboard showing READY_READONLY / KX108_ONLY live
- 12 unit tests

#### F36 — User Scenario Brody Workbench Controlled Response
- `POST /api/periphery/brody-runtime/f36/user-scenario`
- End-to-end: user_input → F33 → F32 → workbench summary → controlled readonly response
- Word-boundary forbidden token check applied to `controlled_response.text` and user-facing response fields (F47 hardening); KERNEL_TRACE stderr is internal computation only
- 14 unit tests

#### F36B — True Live Uvicorn User Scenario Smoke
- Second live-server proof: port 8011, source `LIVE_SERVER_8011`
- SHA256: `A6FD4BC2...` · 61/61 checks
- Proves F36 user scenario boundary holds on live uvicorn

#### F37 — Multi-Domain User Scenarios Readonly
- 4-domain orchestrator: bank, gps_defense_aviation, trading, unknown_refusal
- `build_multi_domain_user_scenarios()` — no HTTP route at this palier
- `unknown_refusal` handled by direct refusal builder (no F33 call — semantically correct)
- 139 smoke checks (DirectCall, no server required)
- 18 unit tests

#### F38 — Multi-Domain Live Uvicorn API Smoke
- `POST /api/periphery/brody-runtime/f38/multi-domain-scenarios` — exposes F37 via API
- Third live-server proof: port 8011, source `LIVE_SERVER_8011`
- SHA256: `746621E5...` · 141/141 checks
- 20 unit tests

---

### Demo and narrative layer (F39→F41)

#### F39 — Operator Demo Pack Consolidation
- JSON pack index + MD consolidation report + operator README (`docs/demo/OBSIDIA_OPERATOR_DEMO_README_F39.md`)
- No new code — documentation consolidation only

#### F40 — Release Candidate Demo Freeze Index (RC1)
- Full RC1 freeze: JSON index, MD report, 12-point operator checklist, freeze manifest
- Verified: 10/10 tags, 19 reports, 6 smoke scripts, 103/103 tests, 474 cumulative smoke checks
- `docs/demo/OBSIDIA_F40_OPERATOR_RELEASE_CANDIDATE_CHECKLIST.md` — 12-point pre-demo checklist

#### F41 — Public Investor Demo Narrative Pack
- 4 public-facing documents: investor pitch, oral demo script (3–5 min), proof perimeter audit, investor/jury FAQ
- No new code — narrative documentation only

---

## V1 Proof Summary

| Metric | Value |
|--------|-------|
| Unit tests | **103/103 PASS** |
| Smoke checks (cumulative) | **474** |
| Live-server proofs | **3** |
| API routes | **7 READY_READONLY** |
| Git tags | **14/14 present** |
| Forbidden tokens found | **0** |
| Mutation flags triggered | **0** |

---

## Known Limitations (V1)

These are documented limitations — not bugs. See `OBSIDIA_F41_WHAT_IT_PROVES_AND_DOES_NOT_PROVE.md` for full audit.

| Limitation | Status |
|------------|--------|
| Formal Lean proof of boundary | Not available at this layer |
| KX108 kernel instantiated | Declared authority only — not integrated |
| Adversarial red-teaming | Not performed |
| Scalability / load testing | Not performed |
| Memory persistence | `memory_write=false` — by design in V1 |
| Full Graphiti binding | Outside V1 scope |

---

## Upgrade Path

**F50+ roadmap:**
- KX108 kernel full integration and decision handoff
- Formal Lean proof of boundary enforcement at periphery layer
- Adversarial hardening (red-teaming, fuzzing)
- Multi-instance deployment and performance testing
- Full Graphiti/Brody deep memory binding
- Cloud deployment artifacts

---

## Verification

```powershell
# Check out V1 sealed HEAD
git checkout b67b2c3

# Run full test suite
python -m pytest tests\api\ -q
# Expected: 103 passed

# Start server and run live smoke
python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8011
python scripts\smoke_f38_multi_domain_live_uvicorn_api.py
# Expected: PASS · CHECKS=141/141
```

---

## Files Introduced in V1 (F32→F42)

| Layer | Files |
|-------|-------|
| Runtime modules | `periphery/brody_runtime/f32_*.py`, `f33_*.py`, `f36_*.py`, `f37_*.py` |
| API routes | `apps/obsidia_api/routes/periphery_ops.py` (F33/F35/F36/F38 routes appended) |
| Unit tests | `tests/api/test_f32_*` through `test_f38_*` |
| Smoke scripts | `scripts/smoke_f34_*` through `smoke_f38_*` |
| Runtime proofs | `docs/runtime/F34B_*`, `F36B_*`, `F38_*` JSON proofs |
| Freeze dirs | `.runtime_freezes/F32_*` through `.runtime_freezes/F42_*` |
| Demo/narrative docs | `docs/demo/OBSIDIA_F39_*` through `OBSIDIA_F42_*` |

---

*Brody GPT V1.0.0-RC-CLOSED · READONLY · KX108_ONLY · Released 2026-05-29*
