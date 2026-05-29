# Brody GPT V1 — F45 Canonical Observation Findings

**Source:** F45 Terminal Test Battery  
**Date:** 2026-05-29  
**Mode:** AUDIT_ONLY · READONLY

---

## What F45 Tests

F45 takes each F44 observation and runs a concrete terminal test to classify it:

| Code | Meaning |
|------|---------|
| `CONFIRMED` | Risk is real and reproduced by test |
| `CONFIRMED_ARCHITECTURAL` | Risk is real by design but not exploitable in V1 |
| `CONFIRMED_LEGACY_ONLY` | Confirmed but affects only legacy routes, not V1 Brody routes |
| `CONFIRMED_PARTIAL` | Partially confirmed — scope narrower than F44 stated |
| `CONFIRMED_LEGACY_SCOPE` | Confirmed scope gap in legacy code path |
| `FALSE_POSITIVE` | Test shows risk does not exist |
| `DOC_ONLY` | Risk is a documentation precision gap, no code risk |
| `NEEDS_PATCH` | Risk requires code correction |
| `NEEDS_MORE_REVIEW` | Inconclusive |

---

## Results

| Finding | F44 Severity | F45 Classification | Action |
|---------|-------------|-------------------|--------|
| `F2_controlled_response_text_unsanitized` | MEDIUM | **CONFIRMED** | F50+ patch required |
| `F4_base_update_override` | MEDIUM | **CONFIRMED** | F50+ patch required |
| `F6_kernel_trace_forbidden_tokens` | LOW-MEDIUM | **DOC_ONLY** | F50+ documentation update only |
| `F1_boundary_truncated` | LOW | **CONFIRMED_LEGACY_ONLY** | F50+ cleanup, low urgency |
| `F3_surfaces_ready_env_dependent` | LOW | **DOC_ONLY** | F50+ documentation update only |
| `F5_token_scan_scope` | LOW | **CONFIRMED_LEGACY_SCOPE** | F50+ documentation + optional scan extension |
| `F7_hardcoded_proof_links` | LOW | **DOC_ONLY** | F50+ documentation update only |

---

## V1 Integrity

```
KX108_ONLY_PRESERVED=true
BRODY_DECISION=false
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
BASELINE_TESTS=103/103
V1_SEAL_INTACT=true
```

No F45 finding requires rollback or invalidates the V1 seal.
All CONFIRMED findings are documented for F50+ hardening.

---

*F45 Findings · AUDIT_ONLY · READONLY · KX108_ONLY · 2026-05-29*