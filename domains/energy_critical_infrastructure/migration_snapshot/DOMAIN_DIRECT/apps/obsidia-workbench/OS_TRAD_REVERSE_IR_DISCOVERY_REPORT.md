# OS Trad / OS Reverse / IR Discovery Report

**Date:** 2026-05-19
**Scope:** `obsidia-x108-proofs/periphery/` — full audit for OS Trad, OS Reverse, IR, Alphabet, Language Router modules

---

## Summary

| Category | Count |
|----------|-------|
| FOUND_LIVE_MODULE | 10 |
| FOUND_DOC_ONLY | 0 |
| FOUND_TEST_ONLY | 2 |
| MISSING | 3 |
| MOCK_NEEDED | 3 |
| FUTURE_BACKEND_ROUTE | 6 |

---

## FOUND_LIVE_MODULE

| Path | Module | Key exports |
|------|--------|-------------|
| `periphery/language/language_router.py` | Language Router | `detect_language()`, `has_authority_claim()`, `route_language()` |
| `periphery/language/__init__.py` | Language package init | — |
| `periphery/brody/brody_language_router.py` | Brody Language Router | `BrodyLanguageRoute`, `route_brody_language()` |
| `periphery/brody/brody_runtime_readonly.py` | Brody Runtime (readonly) | brody response contract |
| `periphery/brody/brody_context_query.py` | Brody Context Query | context read functions |
| `periphery/reverse_os/action_projection_readonly.py` | OS Reverse (action) | `ActionProjection`, `project_action_readonly()` |
| `periphery/reverse_os/audience_projection.py` | OS Reverse (audience) | audience-based projection |
| `periphery/reverse_os/format_projection.py` | OS Reverse (format) | format-based projection |
| `periphery/context/context_packet_builder_v2.py` | Context Packet V2 | `build_context_packet_v2()` |
| `periphery/mcp/mcp_permission_matrix.py` | MCP Permission Matrix | permission read gate |

### Key findings from live modules

**`periphery/language/language_router.py`:**
```python
def detect_language(text: str) -> str   # basic fr/en detection
def has_authority_claim(text: str) -> bool  # checks for authority markers
def route_language(text: str) -> dict   # routes with claim detection
```

**`periphery/brody/brody_language_router.py`:**
```python
class BrodyLanguageRoute: detected_language, routed_to, is_supported, memory_write=False
def route_brody_language(query_id: str, language_code: str) -> BrodyLanguageRoute
```
Supports: `{"en", "fr", "es", "de", "pt", "it"}`

**`periphery/reverse_os/action_projection_readonly.py`:**
```python
_FORBIDDEN_TOKENS = {"ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT"}
class ActionProjection: advisory_only=True, real_action_taken=False, can_emit_act=False
def project_action_readonly(projection_id, intent, context) -> ActionProjection
```

---

## FOUND_TEST_ONLY

| Test file | What it tests |
|-----------|---------------|
| `tests/non_sovereignty/test_brody_no_decision.py` | Tests that Brody cannot emit decision (IR-adjacent logic) |
| `tests/non_sovereignty/test_brody_no_act.py` | Tests that Brody cannot emit ACT (similar to IR constraint) |

---

## MISSING

| Module | Status | Notes |
|--------|--------|-------|
| `periphery/os_trad/` | **MISSING** | No OS Trad module exists. Language router is the closest proxy. |
| `periphery/ir/` | **MISSING** | No IR (Intermediate Representation) module exists. Frontend mock covers this. |
| `periphery/alphabet/` | **MISSING** | No symbolic alphabet module exists. Frontend mock covers this. |

---

## MOCK_NEEDED (frontend-only coverage)

| Function | Frontend mock | Backend status |
|----------|--------------|----------------|
| OS Trad pipeline | `src/lib/osTradPipeline.ts` | MOCK_ONLY |
| IR Candidate builder | `src/lib/irCandidateBuilder.ts` | MOCK_ONLY |
| Symbolic alphabet | `src/lib/symbolicAlphabet.ts` | MOCK_ONLY |
| OS Reverse projection | `src/lib/osReverseProjection.ts` | MOCK_ONLY (maps to `reverse_os/action_projection_readonly.py` semantics) |

---

## FUTURE_BACKEND_ROUTE

| Future endpoint | Maps to | Status |
|----------------|---------|--------|
| `POST /api/os-trad/translate` | `periphery/language/language_router.py` + new os_trad module | NEEDS_FASTAPI_ROUTE |
| `POST /api/ir/candidate` | New periphery/ir module needed | NEEDS_FASTAPI_ROUTE |
| `POST /api/os-reverse/project` | `periphery/reverse_os/action_projection_readonly.py` | NEEDS_FASTAPI_ROUTE |
| `GET /api/alphabet/units` | New periphery/alphabet module needed | NEEDS_FASTAPI_ROUTE |
| `POST /api/context/from-ir` | `periphery/context/context_packet_builder_v2.py` | NEEDS_FASTAPI_ROUTE |
| `GET /api/brody/language-route` | `periphery/brody/brody_language_router.py` | NEEDS_FASTAPI_ROUTE |

---

## Non-sovereignty constraint (all above modules)

None of these modules decide. All are advisory/projection/structural.

| Invariant | Status |
|-----------|--------|
| OS Trad does not decide | ✓ |
| OS Reverse does not decide | ✓ (advisory_only=True in action_projection_readonly.py) |
| IR Candidate ≠ action | ✓ |
| Translation trace ≠ proof | ✓ |
| Context packet ≠ decision | ✓ |
| X-108 remains sole authority | ✓ |
