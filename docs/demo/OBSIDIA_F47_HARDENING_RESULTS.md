# F47 — Hardening Results

**Canonical name:** `BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME`  
**Palier:** F47_CANONICAL_HARDENING_PATCH_SEQUENCE  
**Status:** F47_COMPLETE · REGRESSION_PASS · PUBLIC_RELEASE_GATE_LIFTED  
**Date:** 2026-05-29

---

## Summary

F47 executed the canonical hardening patch sequence defined in F46. All 6 patch phases completed and verified. The public release gate (`BLOCKED_UNTIL_F47_HARDENING`) is lifted.

**0 CONFIRMED findings remain. KX108_ONLY remains sole decision authority.**

---

## Patch Results

| Phase | Name | Status |
|-------|------|--------|
| F47.1 | Protected Response Envelope | PASS — 13/13 sovereignty checks |
| F47.2 | Controlled Response Text Sanitizer | PASS — 42/42 sanitizer checks |
| F47.3 | Nested Scan Scope Verification | PASS — 9/9 nested checks |
| F47.4 | Legacy Boundary Isolation | PASS — legacy annotated |
| F47.5 | Documentation Wording Corrections | PASS — 5 files corrected |
| F47.6 | Regression and Smoke Verification | PASS — 103/103 baseline |

---

## Findings Status After F47

| Finding | Status |
|---------|--------|
| F2 — controlled_response.text unsanitized | **RESOLVED** |
| F4 — sovereignty override risk | **RESOLVED** |
| F5 — token scan scope imprecision | **RESOLVED** (docs corrected) |
| F1 — _BOUNDARY truncated (legacy) | **RESOLVED** (isolated, annotated) |
| F6 — KERNEL_TRACE tokens | **CLARIFIED** (internal-only, doc updated) |
| F3 — surfaces_ready nominal qualifier | **CLARIFIED** (doc updated) |
| F7 — proof_links static snapshot | **ANNOTATED** (doc updated) |

---

## Regression (F47.6)

| Metric | Result |
|--------|--------|
| Baseline tests | **103/103 PASS** |
| Sovereignty flags enforced | **13/13** |
| Forbidden tokens in cr.text | **0** |
| Cumulative smoke checks (V1) | **474/474** |

---

## What Changed

**`apps/obsidia_api/safe_response.py`**
- Added `_SOVEREIGNTY_PROTECTED` (13 flags always enforced)
- Reversed merge order — sovereignty unconditionally wins
- Added `_ISOLATED_TOKEN_RE` and `sanitize_user_facing_text()`
- `safe_backend_response()` now sanitizes `controlled_response.text`

**`periphery/brody_runtime/f36_user_scenario_controlled_response.py`**
- `_build_controlled_response_text()` sanitizes `user_input` before embedding

**`apps/obsidia_api/routes/periphery_ops.py`**
- `_BOUNDARY` annotated as `LEGACY_BOUNDARY_TRUNCATED` with rationale comment
- `proof_links` annotated as static F34B snapshot

**Documentation (5 files)**
- Scan scope claims corrected from "all generated text" to specific fields
- KERNEL_TRACE internal-only status documented
- `surfaces_ready=7` nominal qualifier added
- `proof_links` static-snapshot annotation added

---

## What Did NOT Change

- KX108_ONLY is still the sole decision authority
- `allowed_to_decide=false` — unchanged
- `emits_act=false`, `emits_verdict=false`, `kernel_mutation=false` — unchanged
- No new routes added
- No X108 core modified
- No kernel modified
- No Neo4j write introduced
- No memory write introduced
- Proof chain integrity preserved

---

## Proof Chain

```
F44_AUDIT → F45_TERMINAL_TEST → F46_HARDENING_PLAN → F47_PATCH_SEQUENCE
```

Full artifact:  
`docs/runtime/OBSIDIA_F47_CANONICAL_HARDENING_PATCH_SEQUENCE_20260529_181500.json`  
SHA256: `C3F2F523F1A919091A6524AAAA20C8688DD1EFE4C368D38A2DF0A18AF8B31ADA`

---

*F47 · READONLY · KX108_ONLY · Sealed 2026-05-29*
