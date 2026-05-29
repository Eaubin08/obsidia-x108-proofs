# F47 — Canonical Hardening Patch Sequence

**Artifact:** `OBSIDIA_F47_CANONICAL_HARDENING_PATCH_SEQUENCE_20260529_181500`  
**Palier:** F47  
**Parent audit:** F44_CANONICAL_INTEGRITY_AUDIT_SINCE_20260526  
**Parent plan:** F46_CANONICAL_HARDENING_PLAN  
**Sealed at:** 20260529_181500  
**Status:** F47_COMPLETE_REGRESSION_PASS  
**Public release gate:** LIFTED — F47 hardening complete  

---

## Sovereignty Contract (preserved throughout)

| Flag | Value |
|------|-------|
| `decision_authority` | `KX108_ONLY` |
| `allowed_to_decide` | `false` |
| `emits_act` | `false` |
| `emits_verdict` | `false` |
| `kernel_mutation` | `false` |
| `x108_mutation` | `false` |
| `neo4j_write` | `false` |
| `brody_decision` | `false` |

---

## Patch Summary

### F47.1 — Protected Response Envelope

**Files:** `apps/obsidia_api/safe_response.py`  
**Status:** PASS · 13/13 sovereignty checks  

Reversed merge order in `safe_backend_response()`. Previously `base.update(data)` allowed module data to override sovereignty flags. Fixed to `merged = dict(data); merged.update(_SOVEREIGNTY_PROTECTED)` — sovereignty always wins unconditionally.

Added `_SOVEREIGNTY_PROTECTED` dict (13 flags): `decision_authority`, `allowed_to_decide`, `readonly`, `advisory_only`, `context_signal_only`, `emits_act`, `emits_verdict`, `memory_write`, `kernel_mutation`, `x108_mutation`, `neo4j_write`, `brody_decision`, `real_action`.

**Resolves:** F4_base_update_override (CONFIRMED_ARCHITECTURAL → RESOLVED)

---

### F47.2 — Controlled Response Text Sanitizer

**Files:** `apps/obsidia_api/safe_response.py`, `periphery/brody_runtime/f36_user_scenario_controlled_response.py`  
**Status:** PASS · 42/42 sanitizer checks  

Added `_ISOLATED_TOKEN_RE = re.compile(r"\b(ALLOW|HOLD|BLOCK|ACT|DECIDE|VERDICT)\b", re.IGNORECASE)` and `sanitize_user_facing_text()`.

Dual-layer defense:
1. **Route level:** `safe_backend_response()` now sanitizes `controlled_response.text` after merge
2. **Module level:** `_build_controlled_response_text()` in f36 sanitizes `user_input` before embedding via lazy import

Zero false positives verified on trap words: `transaction`, `interaction`, `artifact`, `react`, `reactivity`, `ACTOR`, `BLOCK_CHAIN`, `VERDICT_FINAL`.

**Resolves:** F2_controlled_response_text_unsanitized (CONFIRMED_PARTIAL → RESOLVED)

---

### F47.3 — Nested Scan Scope Verification

**Files:** `scripts/_f47_test_nested_scan.py` (audit script)  
**Status:** PASS · 9/9 checks  

Verified:
- F37 multi-domain packet: all 4 domain `controlled_response.text` fields clean
- `safe_backend_response()` sanitizes nested `controlled_response.text`
- Internal proof fields (`proof_status`, `scenario_id`, `packet_id`, `audit_id`) preserved unchanged
- F36 module-level scan active without route layer

---

### F47.4 — Legacy Boundary Isolation

**Files:** `apps/obsidia_api/routes/periphery_ops.py`  
**Status:** PASS  

Annotated `_BOUNDARY` (4 of 15 canonical flags) with `# F47.4 — LEGACY_BOUNDARY_TRUNCATED` comment block. Confirmed V1 Brody routes (F33/F35/F36/F38) do not use `_BOUNDARY` — they use the full 15-flag `BOUNDARY` dict from their respective modules.

**Resolves:** F1_boundary_truncated (CONFIRMED_LEGACY_ONLY → RESOLVED_LEGACY_ISOLATED)

---

### F47.5 — Documentation Wording Corrections

**Files:**
- `docs/demo/OBSIDIA_BRODY_GPT_V1_RELEASE_NOTES.md`
- `docs/demo/OBSIDIA_BRODY_GPT_V1_FINAL_README.md`
- `docs/demo/OBSIDIA_F43_LIVE_SERVER_RUNBOOK.md`
- `apps/obsidia_api/routes/periphery_ops.py`
- `docs/demo/OBSIDIA_F41_PUBLIC_INVESTOR_PITCH.md`

**Status:** PASS · 5 files corrected  

Corrections applied:
- **F6 (KERNEL_TRACE):** Replaced "all generated text" scan claims with specific scope: `controlled_response.text` + `response`/`response_text` fields. Added note that `KERNEL_TRACE` stderr tokens are internal computation only, not API response emissions.
- **F3 (surfaces_ready):** Added "nominal configuration" qualifier to domain tables and pitch text. Added explanatory note that value is dynamically computed at runtime.
- **F7 (proof_links):** Added `# F47.5 — F7 STATIC_PROOF_LINKS_SNAPSHOT` comment above hardcoded proof paths, with pointer to F40 release candidate index for current proof inventory.

**Resolves:** F5/F6/F3/F7 (all DOC_ONLY — wording corrected)

---

### F47.6 — Regression and Smoke Verification

**Status:** PASS  

| Check | Result |
|-------|--------|
| Baseline tests | **103/103 PASS** |
| F47.1 sovereignty script | **13/13 PASS** |
| F47.2 sanitizer script | **42/42 PASS** |
| F47.3 nested scan script | **9/9 PASS** |
| Cumulative smoke (V1) | **474/474 PASS** |
| Forbidden tokens in cr.text | **0** |
| Sovereignty flags blocked | **13/13** |

---

## Findings Resolution Table

| Finding | Pre-F47 Classification | Post-F47 Status |
|---------|----------------------|-----------------|
| F2 — controlled_response.text unsanitized | CONFIRMED_PARTIAL | RESOLVED (F47.2) |
| F4 — base.update override risk | CONFIRMED_ARCHITECTURAL | RESOLVED (F47.1) |
| F5 — token scan scope | CONFIRMED_LEGACY_SCOPE | RESOLVED — docs corrected (F47.5) |
| F1 — _BOUNDARY truncated | CONFIRMED_LEGACY_ONLY | RESOLVED_LEGACY_ISOLATED (F47.4) |
| F6 — KERNEL_TRACE forbidden tokens | DOC_ONLY | CLARIFIED (F47.5) |
| F3 — surfaces_ready env-dependent | DOC_ONLY | CLARIFIED (F47.5) |
| F7 — hardcoded proof_links | DOC_ONLY | ANNOTATED (F47.5) |

**CONFIRMED findings remaining: 0**

---

## Proof Chain

```
F44_AUDIT → F45_TERMINAL_TEST → F46_HARDENING_PLAN → F47_PATCH_SEQUENCE
```

SHA256 of this artifact (JSON):  
`C3F2F523F1A919091A6524AAAA20C8688DD1EFE4C368D38A2DF0A18AF8B31ADA`

---

## Upgrade Path (F50+)

- KX108 kernel full integration and decision handoff
- Formal Lean proof of boundary enforcement
- Adversarial hardening (red-teaming, fuzzing)
- Multi-instance deployment and performance testing
- Full Graphiti/Brody deep memory binding
- Cloud deployment artifacts
- Expand legacy `_BOUNDARY` to 15 flags or deprecate legacy routes

---

*F47 · READONLY · KX108_ONLY · Sealed 2026-05-29*
