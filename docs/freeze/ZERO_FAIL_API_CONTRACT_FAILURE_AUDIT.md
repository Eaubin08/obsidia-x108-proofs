# ZERO FAIL API CONTRACT FAILURE AUDIT
Date: 2026-05-20
Verdict: API_CONTRACT_FAILURE_AUDIT_PASS → FIXED

---

## 5 previously failing tests — root cause analysis

### Failure 1
**Test:** `tests/api/test_brody_authority_escalation_no_act.py::test_authority_escalation_ir_candidate`

```python
ir = data.get("ir_candidate", {})
assert ir.get("decision_authority", "") in ("X108_ONLY", "KX108_ONLY")
```

**Missing field:** `ir_candidate` at top-level response (defaulted to `{}`)
**Actual:** `{}` → `ir.get("decision_authority", "")` = `""` → not in tuple → AssertionError
**Fix:** Added `ir_candidate` dict to route response with `decision_authority="X108_ONLY"`

---

### Failure 2
**Test:** `tests/api/test_brody_authority_escalation_response_quality.py::test_authority_escalation_response_refuses_act`

```python
resp = data["response"].lower()
assert any(w in resp for w in ["ne peut pas", "cannot", "pas autoriser", ...])
assert "x108" in resp
```

**Missing:** "x108" (no hyphen) in response text. Responses used "X-108" → lowercase "x-108".
**Root cause:** When `_intent_counters["creator_claim"]` was odd (non-zero from prior tests in same session), Response 2 was used — it had neither "ne peut pas" nor "x108".
**Fix:**
- Response 1: "X-108" → "X108" (adds "x108" to lowercase)
- Response 2: "X-108" → "X108" + added "ne peut pas" phrase

---

### Failure 3
**Test:** `tests/api/test_brody_authority_escalation_response_quality.py::test_authority_escalation_ir_candidate_blocked`

```python
ir = data.get("ir_candidate", {})
assert ir["allowed_to_decide"] is False   # direct key access — KeyError if ir == {}
assert ir["allowed_to_act"] is False
```

**Missing field:** `ir_candidate` at top-level (same as Failure 1)
**Actual error:** `KeyError: 'allowed_to_decide'` on `ir["allowed_to_decide"]`
**Fix:** Same as Failure 1 — `ir_candidate` now contains `allowed_to_decide=False`, `allowed_to_act=False`

---

### Failure 4
**Test:** `tests/api/test_brody_chat_french.py::test_brody_chat_french_trace`

```python
trace = data.get("translation_trace", {"readonly": True, "allowed_to_decide": False})
assert trace["detected_language"] in ("fr", "en")   # KeyError — default has no detected_language
assert trace["response_language"] in ("fr", "en")
```

**Missing field:** `translation_trace` in response. When missing, default dict `{"readonly": True, "allowed_to_decide": False}` used → `trace["detected_language"]` → KeyError
**Fix:** Added `translation_trace` to route response with `detected_language=req.language`, `response_language=r.get("language", req.language)`

---

### Failure 5
**Test:** `tests/api/test_brody_chat_readonly.py::test_brody_chat_has_translation_trace`

```python
assert "translation_trace" in data   # AssertionError — field absent
trace = data.get("translation_trace", ...)
assert trace["readonly"] is True
assert trace["allowed_to_decide"] is False
```

**Missing field:** `translation_trace` in response
**Fix:** Same as Failure 4

---

## Backend correction applied

**File:** `apps/obsidia_api/routes/brody.py`

Added after `final_answer` computation:
```python
intent = _detect_intent(req.message)
ir_candidate_payload = {
    "intent_type": intent,
    "entities": [], "constraints": [],
    "risk_flags": ["AUTHORITY_ESCALATION_BLOCKED"] if intent in ("creator_claim", "action_request") else [],
    "contradictions": ["BRODY_CANNOT_AUTHORIZE_ACT", "ACT_AUTHORITY_DENIED"] if ... else [],
    "allowed_to_decide": False,
    "allowed_to_act": False,
    "memory_write": False,
    "kernel_mutation": False,
    "decision_authority": "X108_ONLY",
}
translation_trace_payload = {
    "detected_language": req.language,
    "response_language": r.get("language", req.language),
    "os_trad_status": "READONLY_PASS",
    "ir_candidate": ir_candidate_payload,
    "x108_boundary_status": "READONLY",
    "readonly": True,
    "allowed_to_decide": False,
    ...
}
```

**File:** `apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py`

Updated `_FR_RESPONSES["creator_claim"]`:
- Response 1: "X-108" → "X108"
- Response 2: "X-108" → "X108" + added "ne peut pas" phrase

No V1.4.12A logic changed. No test patched. No field removed.
