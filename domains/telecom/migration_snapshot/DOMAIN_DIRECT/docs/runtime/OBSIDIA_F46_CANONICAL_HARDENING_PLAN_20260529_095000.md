# OBSIDIA F46 — Canonical Hardening Plan

**Plan ID:** F46_CANONICAL_HARDENING_PLAN  
**Timestamp:** 20260529_095000  
**Mode:** PLAN_ONLY · READONLY · KX108_ONLY · emits_act=false  
**HEAD:** 9f59eeb  
**Parent:** F45_CANONICAL_OBSERVATION_TERMINAL_TEST_BATTERY  
**PATCH_RUNTIME:** NO · **COMMIT:** NO · **TAG:** NO · **PUSH:** NO

---

## PUBLIC RELEASE GATE

```
PUBLIC_RELEASE_GATE=BLOCKED_UNTIL_F47_HARDENING
```

**Reason:** F2 (controlled_response.text unsanitized) and F4 (sovereignty override gap) are confirmed by terminal tests. These must be hardened before any public or production release.

V1 seal (`BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME_FINAL_20260529`) remains valid. The architectural contracts are correct in V1 modules. The hardening closes implementation gaps in the safety wrapper layer.

---

## EXECUTIVE STATUS

| Item | Status |
|------|--------|
| V1 sealed | ✅ `BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME_FINAL_20260529` |
| F44 canonical audit | ✅ PASS_WITH_OBSERVATIONS |
| F45 terminal test battery | ✅ PASS_WITH_CONFIRMED_FINDINGS |
| Confirmed findings | 4 (F2, F4, F5, F1) |
| Doc-only findings | 3 (F6, F3, F7) |
| Public release | ❌ BLOCKED_UNTIL_F47_HARDENING |
| Baseline tests | ✅ 103/103 PASS (unchanged) |
| KX108_ONLY preserved | ✅ |
| No actual mutations | ✅ |

---

## FINDINGS MAP

### F2 — CONFIRMED — controlled_response.text unsanitized

**F44 severity:** MEDIUM  
**F45 classification:** CONFIRMED  
**Evidence:** 11/20 injection cases reproduced word-boundary forbidden tokens in `controlled_response.text`. All 6 tokens confirmed. `safe_backend_response()` does not sanitize nested fields.

**Mechanism:**
```python
# f36_user_scenario_controlled_response.py
f"Demande reçue : « {user_input} »\n"
# user_input="ALLOW" → "Demande reçue : « ALLOW »" → in controlled_response.text
# safe_backend_response() only sanitizes response / response_text — not nested
```

**Risk:** User-facing token contamination via `user_input`. Real injection vector reproduced in F45.

**Target files:**
- `apps/obsidia_api/safe_response.py`
- `periphery/brody_runtime/f36_user_scenario_controlled_response.py`

**Planned action (F47.2):**
1. Extend `safe_backend_response()` to apply `strip_forbidden_tokens()` on `controlled_response.text`
2. Add `_has_forbidden_token()` guard in `_build_controlled_response_text()` — replace with `[REDACTED]` if match

**Stop condition:** 0 word-boundary forbidden tokens for all F45 injection cases  
**No-touch:** KX108 kernel, BOUNDARY constants, route Pydantic schema, F33/F38 routes

---

### F4 — CONFIRMED — base.update(data) sovereignty override gap

**F44 severity:** MEDIUM  
**F45 classification:** CONFIRMED  
**Evidence:** All 8 sovereignty flags survive `base.update(data)` merge. Pydantic HTTP schema blocks direct HTTP injection (V1 safe). Architectural gap: compromised module payload propagates without resistance.

**Mechanism:**
```python
# safe_response.py — CURRENT (unsafe)
base = {"decision_authority": "KX108_ONLY", "allowed_to_decide": False, ...}
base.update(data)   # data CAN override base — any key in data wins
return base

# PLANNED (safe)
data.update(base)   # base ALWAYS wins — sovereignty flags protected
return data
```

**Risk:** Latent in V1 (all modules return correct BOUNDARY). Architectural: `safe_backend_response()` is not a true sovereignty enforcement layer.

**Target file:** `apps/obsidia_api/safe_response.py`

**Planned action (F47.1):**
- Change merge order: `data.update(base)` instead of `base.update(data)`
- Add post-merge assertion for `decision_authority == "KX108_ONLY"` and critical flags

**Stop condition:** All 8 sovereignty injection cases blocked. 103/103 tests still pass.  
**No-touch:** BOUNDARY constants in modules, route handlers, Pydantic models

---

### F5 — CONFIRMED_LEGACY_SCOPE — token scan scope imprecise

**F44 severity:** LOW  
**F45 classification:** CONFIRMED_LEGACY_SCOPE  
**Evidence:** F36 does not call `_has_forbidden_token()` on own output. F37 scans `controlled_response.text` only. Regex behavior correct (8/8 trap cases pass). Documentation claim "word-boundary regex on all generated text" is imprecise.

**Mechanism:** Scan enforcement is single-layer (F37 module) and field-scoped (`text` field only). `safe_backend_response()` covers `response`/`response_text` only.

**Risk:** Documentation overstates coverage. F36 standalone path has no runtime scan (static template reliance). F47.2 will partially fix this as side-effect.

**Target files:**
- `periphery/brody_runtime/f36_user_scenario_controlled_response.py` (code — F47.2)
- `docs/demo/OBSIDIA_F43_LIVE_SERVER_RUNBOOK.md` (docs — F47.5)

**Planned action (F47.3 + F47.5):**
- Code: verify F47.2 patch makes F36 standalone clean
- Docs: correct all "all generated text" claims to specify exact scan scope

**Stop condition:** F36 standalone clean for all F45 injection cases. Docs corrected.

---

### F1 — CONFIRMED_LEGACY_ONLY — _BOUNDARY truncated

**F44 severity:** LOW  
**F45 classification:** CONFIRMED_LEGACY_ONLY  
**Evidence:** `_BOUNDARY` in `periphery_ops.py` = 4 flags. V1 modules = 15 flags. Used 70 times in periphery_ops.py. V1 Brody routes (F33/F36/F38) never use `_BOUNDARY` — they use full module BOUNDARY.

**Risk:** Legacy pipeline/governance routes expose incomplete boundary contract. V1 Brody routes unaffected.

**Target file:** `apps/obsidia_api/routes/periphery_ops.py`

**Planned action (F47.4):**
- Annotate `_BOUNDARY` with `# LEGACY_BOUNDARY_TRUNCATED — 4 of 15 flags — V1 Brody routes do not use this`
- Optionally expand to 15 flags (non-breaking)

**Stop condition:** `_BOUNDARY` annotated or expanded. No V1 regression.

---

### F6 — DOC_ONLY — KERNEL_TRACE internal tokens

**F44 severity:** LOW-MEDIUM  
**F45 classification:** DOC_ONLY  
**Evidence:** 1178 bytes KERNEL_TRACE stderr captured containing ALLOW/BLOCK/VERDICT. Zero forbidden tokens in API response JSON.

**Planned action (F47.5):** Add scope note to BOUNDARY contract docs:  
*"KERNEL_TRACE stderr tokens are internal computation results from sigma/evaluate. NOT Brody API response emissions. Token scan scope = API response JSON payloads only."*

---

### F3 — DOC_ONLY — surfaces_ready env-dependent

**F44 severity:** LOW  
**F45 classification:** DOC_ONLY  
**Evidence:** `surfaces_ready` dynamically computed. Value 7 = nominal. Not hardcoded.

**Planned action (F47.5):** Add qualifier: *"7 surfaces ready in nominal configuration; degrades gracefully if upstream unavailable."*

---

### F7 — DOC_ONLY — hardcoded proof_links

**F44 severity:** LOW  
**F45 classification:** DOC_ONLY  
**Evidence:** All 3 hardcoded proof_links exist. Maintenance debt only.

**Planned action (F47.5):** Add comment `# STATIC_PROOF_LINKS — V1 snapshot. Replace with dynamic scan in F50+.`

---

## METRICS

### Current state (pre-F47)

```
BOUNDARY_INTEGRITY             = CONFIRMED (V1 modules only)
FORBIDDEN_TOKENS_IN_CR_TEXT    = NOT_ZERO (11 confirmed injection cases)
SAFE_BACKEND_RESPONSE_ENFORCES = false (data overrides base)
SCAN_COVERAGE_CLAIM_ACCURATE   = false (F5 confirmed)
INTERNAL_TRACE_SEPARATED       = true (F6 DOC_ONLY)
SURFACES_READY_DYNAMIC         = true (F3 DOC_ONLY)
PROOF_LINKS_VALID              = true (F7 DOC_ONLY, maintenance debt)
```

### Target state (post-F47)

```
FORBIDDEN_TOKENS_IN_CR_TEXT    = 0
SAFE_BACKEND_RESPONSE_ENFORCES = true (base wins)
CONTROLLED_RESPONSE_SANITIZED  = true
NESTED_SCAN_DEFINED            = true
SOVEREIGNTY_OVERRIDE_POSSIBLE  = false
HTTP_SCHEMA_INJECTION_BLOCKED  = true (already)
SCAN_COVERAGE_CLAIM_ACCURATE   = true
DOCS_CORRECTED                 = true
```

---

## F47 PATCH SEQUENCE

| Phase | Title | Target | Dependency |
|-------|-------|--------|------------|
| F47.1 | Protected response envelope hardening | `safe_response.py` | none |
| F47.2 | controlled_response text sanitizer | `safe_response.py`, `f36_*.py` | F47.1 |
| F47.3 | Nested scan scope extension | `safe_response.py` | F47.2 |
| F47.4 | Legacy boundary isolation | `periphery_ops.py` | none |
| F47.5 | Documentation wording correction | `docs/demo/*.md` | F47.1–F47.4 |
| F47.6 | Regression + live smoke | full suite | F47.1–F47.5 |
| F47.7 | Commit / tag hardening patch | git | F47.6 |

**F47.1 and F47.4 are independent and can run in parallel.**

---

## NO-TOUCH CONSTRAINTS

The following MUST NOT be modified during F47 hardening:

| Item | Reason |
|------|--------|
| KX108 kernel | Sovereign authority — outside V1 patch scope |
| BOUNDARY constants in F32/F36/F37 modules | Source of truth — correct as-is |
| Route Pydantic models (F36UserScenarioPayload, etc.) | HTTP schema injection already blocked |
| F33/F38 route handler logic | Not affected by confirmed findings |
| Neo4j / Graphiti | No findings touch these |
| `proof_status = RUNTIME_SMOKE_ONLY_NOT_LEAN_PROVEN` | Honest marker — must not be removed |
| Test files for F32–F38 | 103/103 must pass after patch |

---

## TERMINAL FINAL

```
F46_CANONICAL_HARDENING_PLAN_STATUS=PASS
HEAD=9f59eeb
PARENT=F45_CANONICAL_OBSERVATION_TERMINAL_TEST_BATTERY
PUBLIC_RELEASE_GATE=BLOCKED_UNTIL_F47_HARDENING
F2_ACTION=sanitize controlled_response.text (F47.2)
F4_ACTION=data.update(base) — protect sovereignty fields (F47.1)
F5_ACTION=verify F36 standalone clean + correct doc claim (F47.3+F47.5)
F1_ACTION=annotate legacy _BOUNDARY (F47.4)
F6_ACTION=document KERNEL_TRACE scope only (F47.5)
F3_ACTION=no runtime patch — doc qualifier only (F47.5)
F7_ACTION=static snapshot comment + future dynamic index (F47.5)
F47_SEQUENCE_READY=true
PATCH=NO
COMMIT=NO
TAG=NO
PUSH=NO
NEXT=F47_CANONICAL_HARDENING_PATCH_SEQUENCE
```

---

*F46 Canonical Hardening Plan · PLAN_ONLY · READONLY · KX108_ONLY · Generated 2026-05-29*
