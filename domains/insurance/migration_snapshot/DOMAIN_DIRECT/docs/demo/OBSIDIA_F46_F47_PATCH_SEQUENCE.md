# Brody GPT V1 — F47 Patch Sequence

**Prepared by:** F46 Canonical Hardening Plan  
**Date:** 2026-05-29  
**Mode:** PLAN_ONLY — no patches applied in F46

---

## Overview

F47 is the canonical hardening patch sequence for Brody GPT V1. It closes the confirmed findings from F44/F45 without modifying the V1 architectural contracts (BOUNDARY, KX108_ONLY, READONLY, no mutation).

**Total phases:** 7  
**Estimated files modified:** 3–4 (safe_response.py, f36_*.py, periphery_ops.py, docs)  
**Estimated new tests:** 1 (test_f47_safe_response_sovereignty_enforcement.py)  
**Baseline regression:** 103/103 must pass at every phase

---

## Phase F47.1 — Protected Response Envelope Hardening

**Finding:** F4 (CONFIRMED)  
**Priority:** HIGH — patch first, independent of other phases  
**Target file:** `apps/obsidia_api/safe_response.py`

### Current code (unsafe)
```python
def safe_backend_response(data, source="REAL_BACKEND"):
    base = {
        "readonly": True,
        "advisory_only": True,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        ...
    }
    if data:
        base.update(data)   # DATA OVERRIDES BASE — sovereignty flags not protected
    return base
```

### Planned patch
```python
def safe_backend_response(data, source="REAL_BACKEND"):
    sovereignty_base = {
        "readonly": True,
        "advisory_only": True,
        "emits_act": False,
        "emits_verdict": False,
        "decision_authority": "KX108_ONLY",
        "memory_write": False,
        "kernel_mutation": False,
        "real_action": False,
        "source": source,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    merged = dict(data) if data else {}
    merged.update(sovereignty_base)   # BASE WINS — sovereignty flags always enforced
    # ... sanitize response/response_text ...
    return merged
```

### Acceptance criteria
- `safe_backend_response({"decision_authority": "BRODY_OVERRIDE"})["decision_authority"]` == `"KX108_ONLY"`
- `safe_backend_response({"allowed_to_decide": True}).get("allowed_to_decide", False)` == `False`
- All 8 sovereignty injection cases from F45 blocked
- 103/103 baseline tests still pass

### No-touch
- BOUNDARY constants in modules
- Route Pydantic models
- Module implementations

---

## Phase F47.2 — controlled_response Text Sanitizer

**Finding:** F2 (CONFIRMED)  
**Priority:** HIGH — depends on F47.1  
**Target files:** `apps/obsidia_api/safe_response.py` + `periphery/brody_runtime/f36_user_scenario_controlled_response.py`

### What to add in safe_response.py
```python
# After sanitizing response/response_text, also sanitize controlled_response.text:
if "controlled_response" in base and isinstance(base["controlled_response"], dict):
    cr = base["controlled_response"]
    if "text" in cr and isinstance(cr["text"], str):
        cr["text"] = strip_forbidden_tokens(cr["text"])
```

### What to add in f36_user_scenario_controlled_response.py
```python
# In _build_controlled_response_text(), before returning:
if _has_forbidden_word_boundary(text):
    # Replace user_input echo with [REDACTED] if it contains forbidden tokens
    # (handled by safe_backend_response at route level — belt and suspenders)
    pass
```

### Note on strip_forbidden_tokens vs _has_forbidden_token
- `strip_forbidden_tokens()` uses narrow French emission-pattern regex — it will NOT catch `"ALLOW"` as a standalone word in `"Demande reçue : « ALLOW »"`
- The sanitizer must also apply word-boundary replacement for all tokens in `controlled_response.text`
- Proposed: extend `strip_forbidden_tokens()` to also apply `re.sub(r"\b(ALLOW|HOLD|BLOCK|ACT|DECIDE|VERDICT)\b", "[REDACTED]", text, flags=re.IGNORECASE)` as a second pass

### Acceptance criteria
- F45 battery: 0 word-boundary forbidden tokens in controlled_response.text for all 11 confirmed injection cases
- No false positives on trap words (transaction, action, react, interaction, artifact, ACTOR, BLOCK_CHAIN)
- 103/103 baseline tests still pass
- smoke_f36 (60/60), smoke_f36b (61/61) still pass

### No-touch
- BOUNDARY constant in f36 module
- F33/F38 route handlers
- F37 multi-domain orchestrator

---

## Phase F47.3 — Nested Forbidden-Token Scan Scope Extension

**Finding:** F5 (CONFIRMED_LEGACY_SCOPE)  
**Priority:** MEDIUM — depends on F47.2  
**Target file:** `apps/obsidia_api/safe_response.py`

### Action
After F47.2, verify:
1. F36 standalone call with `user_input="ALLOW"` → `controlled_response.text` clean
2. F37 multi-domain packet → `forbidden_tokens_found=False` for all standard scenarios
3. Optionally add recursive walk for any nested dict/string field in `safe_backend_response()`

### Acceptance criteria
- F45 F5 test: `f36_runtime_scans_own_output` or `safe_backend_response_sanitizes_nested` = True
- F45 battery F5 classification = `FALSE_POSITIVE` or `DOC_ONLY`

---

## Phase F47.4 — Legacy Boundary Isolation

**Finding:** F1 (CONFIRMED_LEGACY_ONLY)  
**Priority:** LOW — independent of other phases  
**Target file:** `apps/obsidia_api/routes/periphery_ops.py`

### Action
```python
# BEFORE (current)
_BOUNDARY: dict[str, Any] = {
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
    "decision_authority": "KX108_ONLY",
}

# AFTER (planned)
# LEGACY_BOUNDARY_TRUNCATED — 4 of 15 canonical flags.
# Used by pre-F32 pipeline/governance routes only.
# V1 Brody routes (F33/F35/F36/F38) use full 15-flag BOUNDARY from their modules.
# Expand to 15 flags in F50+ or deprecate legacy routes.
_BOUNDARY: dict[str, Any] = {
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
    "decision_authority": "KX108_ONLY",
}
```

### Acceptance criteria
- `_BOUNDARY` annotated with deprecation/scope note
- No V1 route regression
- 103/103 still pass

---

## Phase F47.5 — Documentation Wording Corrections

**Findings:** F5, F6, F3, F7  
**Priority:** LOW — after code phases complete  
**Target files:**

| File | Correction |
|------|-----------|
| `docs/demo/OBSIDIA_F43_LIVE_SERVER_RUNBOOK.md` | Add KERNEL_TRACE scope note; correct "all generated text" scan claim |
| `docs/demo/OBSIDIA_BRODY_GPT_V1_FINAL_README.md` | Add "nominal configuration" qualifier on "7 surfaces" |
| `docs/demo/OBSIDIA_F41_PUBLIC_INVESTOR_PITCH.md` | Add "nominal configuration" qualifier |
| `apps/obsidia_api/routes/periphery_ops.py` | Add static proof_links comment (F7) |

### Acceptance criteria
- No documentation overclaims scan coverage
- KERNEL_TRACE scope documented
- surfaces_ready qualifier present
- proof_links annotated as V1 snapshot

---

## Phase F47.6 — Regression + Live Smoke

**Depends on:** F47.1–F47.5 complete  
**Action:**

```powershell
# Baseline tests
python -m pytest tests\api\test_f38_multi_domain_live_api_route_readonly.py `
  tests\api\test_f37_multi_domain_user_scenarios_readonly.py `
  tests\api\test_f36_user_scenario_brody_workbench_controlled_response.py `
  tests\api\test_f35_1_operator_demo_workbench_surfaces.py `
  tests\api\test_f34_live_route_contract_readonly.py `
  tests\api\test_f33_brody_runtime_entrypoint_readonly.py `
  tests\api\test_f32_brody_full_runtime_integration_readonly_packet.py `
  tests\api\test_f29_1_neo4j_manual_write_surface_guard.py -q
# Expected: 103 passed

# Smoke scripts
python scripts\smoke_f37_multi_domain_user_scenarios_readonly.py
python scripts\smoke_f34_live_route_contract_readonly.py
python scripts\smoke_f36_user_scenario_controlled_response.py
# If server available:
# python scripts\smoke_f36b_true_live_uvicorn_user_scenario.py
# python scripts\smoke_f38_multi_domain_live_uvicorn_api.py
# Expected: 474/474

# Re-run F45 battery — must show 0 CONFIRMED findings
python scripts\audit_f45_canonical_observation_terminal_test_battery.py
# Expected: F2=FALSE_POSITIVE/DOC_ONLY, F4=FALSE_POSITIVE/DOC_ONLY
```

### Acceptance criteria
- 103/103 tests pass
- 474/474 smoke checks pass (or 333/333 without live server)
- F45 battery: CONFIRMED_FINDINGS=0

---

## Phase F47.7 — Commit / Tag Hardening Patch

**Depends on:** F47.6 PASS  
**Action:**
```powershell
git add apps\obsidia_api\safe_response.py `
        periphery\brody_runtime\f36_user_scenario_controlled_response.py `
        apps\obsidia_api\routes\periphery_ops.py `
        docs\demo\*.md
git commit -m "feat: F47 canonical hardening patch — sanitize controlled_response.text, protect sovereignty flags"
git tag BRODY_F47_CANONICAL_HARDENING_PATCH_PALIER_20260530
```

**Gate lifted:**
```
PUBLIC_RELEASE_GATE=OPEN
```

---

## Summary Table

| Phase | Finding | File(s) | Type | Priority |
|-------|---------|---------|------|----------|
| F47.1 | F4 | safe_response.py | Code | HIGH |
| F47.2 | F2 | safe_response.py, f36_*.py | Code | HIGH |
| F47.3 | F5 | safe_response.py | Code verify | MEDIUM |
| F47.4 | F1 | periphery_ops.py | Comment | LOW |
| F47.5 | F5,F6,F3,F7 | docs/*.md | Docs | LOW |
| F47.6 | all | full suite | Tests | REQUIRED |
| F47.7 | all | git | Commit/tag | REQUIRED |

---

*F46 F47 Patch Sequence · PLAN_ONLY · READONLY · KX108_ONLY · 2026-05-29*
