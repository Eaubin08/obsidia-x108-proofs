# V5B+ Brody Response Module Audit

**Date:** 2026-05-19
**Status:** AUDIT_COMPLETE

---

## Module Classification

| Module | Status | Use for Response |
|--------|--------|-----------------|
| `brody_runtime_readonly.brody_respond()` | REAL_RESPONSE_MODULE | Returns BrodyResponse dataclass with response_text field |
| `brody_response_contract.BrodyResponseContract` | REAL_CONTRACT_ONLY | Validates invariants, does not compose text |
| `brody_response_sanitizer.sanitize_brody_response()` | REAL_RESPONSE_MODULE | Strips forbidden tokens |
| `brody_language_router.route_brody_language()` | REAL_RESPONSE_MODULE | Routes by language |
| `language_router.detect_language()` | REAL_RESPONSE_MODULE | Detects FR/EN |
| `language_router.has_authority_claim()` | REAL_RESPONSE_MODULE | Detects authority escalation |
| `reverse_os.action_projection_readonly.project_action_readonly()` | REAL_RESPONSE_MODULE | Returns projection but requires structured IR |
| `context_packet_builder_v2.build_context_packet_v2()` | REAL_RESPONSE_MODULE | Builds context packet |
| `x108_context_boundary.check_x108_context_boundary()` | REAL_RESPONSE_MODULE | Validates boundary |

## Gap

`brody_respond()` returns a response_text but it's minimal/generic — just acknowledges the query. The natural language composition (intent detection, situation-aware responses) that exists in frontend `brodyResponseComposer.ts` has no Python equivalent.

**Solution:** Create `brody_backend_response_composer.py` that composes natural FR/EN responses based on pipeline data (intent, risk flags, language, IR candidate, context packet).

This keeps the backend as the response source — no fallback to frontend composer needed.
