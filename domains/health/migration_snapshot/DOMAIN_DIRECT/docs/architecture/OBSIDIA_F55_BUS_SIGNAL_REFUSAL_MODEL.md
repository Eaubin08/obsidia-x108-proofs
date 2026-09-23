# F55 — Bus/Signal Refusal Model

**Artifact:** `OBSIDIA_F55_BUS_SIGNAL_REFUSAL_MODEL`  
**Palier:** F55  
**Parent:** F54_BUS_BRIDGE_MINIMAL_ROUTE_IMPLEMENTATION  
**Date:** 2026-05-30  
**Status:** ARCHITECTURAL PLAN — NOT IMPLEMENTED  

---

## Principle

`POST /bus/signal` does not refuse signals. It **neutralizes** them.

A signal that contains forbidden content, forbidden intent, or requests mutation is not rejected at the HTTP level (except for structural validation errors). It is:

1. Accepted as an observation
2. Sanitized by F47.2
3. Packaged as a read-only observation packet with `interpreted_as_command=false`
4. Returned with all sovereignty flags enforced

The signal never becomes a command. The observation is returned to the caller. KX108_ONLY decides what to do with it (or nothing).

---

## Refusal Taxonomy

### Category 1 — HTTP-level Refusal (structural errors)

These are the ONLY cases where a non-200 response is returned:

| Condition | HTTP Code | Status field |
|-----------|-----------|--------------|
| `signal_type` absent | 422 | `SIGNAL_TYPE_MISSING` |
| `signal_origin` absent | 422 | `SIGNAL_ORIGIN_MISSING` |
| Body is not valid JSON | 422 | `INVALID_JSON_BODY` |
| Body is empty | 422 | `EMPTY_BODY` |

All 422 responses still carry full boundary flags:
```json
{
  "decision_authority": "KX108_ONLY",
  "emits_act": false,
  "readonly": true,
  "status": "SIGNAL_TYPE_MISSING",
  ...
}
```

---

### Category 2 — Content Neutralization (always HTTP 200)

These conditions do NOT cause rejection. The signal is accepted, sanitized, and packaged.

| Forbidden content | Neutralization |
|-------------------|---------------|
| Payload contains `ACT` as isolated token | Replaced with `[REDACTED]` by F47.2 sanitizer |
| Payload contains `DECIDE` | Replaced with `[REDACTED]` |
| Payload contains `ALLOW` | Replaced with `[REDACTED]` |
| Payload contains `HOLD` | Replaced with `[REDACTED]` |
| Payload contains `BLOCK` | Replaced with `[REDACTED]` |
| Payload contains `VERDICT` | Replaced with `[REDACTED]` |
| `declared_intent` requests mutation | Noted in packet, `interpreted_as_command=false` |
| `declared_intent` requests decision authority | Noted in packet, `routed_to_decision=false` |
| `signal_type=unknown_signal` | Handled conservatively — same as valid signal |
| Unrecognized `signal_type` value | Auto-classified as `unknown_signal` |
| `risk_hint` value not in enum | Set to `unknown` in packet — no elevated treatment |

**`forbidden_tokens_found=true`** is set in the packet when F47.2 redactions occurred. The caller is informed but no HTTP error is raised.

---

### Category 3 — Mutation Request Neutralization

Any signal that declares or implies a desire to trigger mutation is neutralized at the packet level:

| Mutation requested | Packet response |
|--------------------|-----------------|
| `neo4j_write` | `neo4j_write=false` in envelope — unconditional |
| `graphiti_write` | `graphiti_write=false` in envelope — unconditional |
| `memory_write` | `memory_write=false` in envelope — unconditional |
| `kernel_mutation` | `kernel_mutation=false` in envelope — unconditional |
| `x108_mutation` | `x108_mutation=false` in envelope — unconditional |
| Any `emits_act` request | `emits_act=false` in envelope — unconditional |
| Any `brody_decision` routing | `brody_decision=false` in envelope — unconditional |

These are enforced by `build_output_envelope()` and `_SOVEREIGNTY_PROTECTED` — they cannot be overridden by any signal content.

---

### Category 4 — Authority Escalation Refusal

A signal that attempts to claim decision authority is neutralized:

| Escalation attempt | Handling |
|--------------------|---------|
| `declared_intent: "act_on_behalf_of_KX108"` | `routed_to_decision=false` — KX108 is not delegated |
| `declared_intent: "override_sovereignty"` | Sanitized text only — sovereignty untouched |
| `signal_type: "command"` | Not in enum → classified as `unknown_signal` |
| Body field `decision_authority: "BRODY"` | Ignored — envelope always sets `decision_authority=KX108_ONLY` |
| Body field `allowed_to_decide: true` | Ignored — envelope always sets `allowed_to_decide=false` |

---

## Enforcement Chain for Signals

```
POST /bus/signal received
        ↓
1. Structural validation → 422 if type/origin absent
        ↓
2. signal_type classification → unknown_signal if unrecognized
        ↓
3. All string fields → sanitize_user_facing_text() (F47.2)
   forbidden_tokens_found = len(redactions) > 0
        ↓
4. Build signal_observation_packet:
   accepted_as_observation = true (always)
   interpreted_as_command  = false (always)
   routed_to_decision      = false (always)
   emitted_act             = false (always)
   mutation_performed      = false (always)
        ↓
5. build_output_envelope(signal_observation_packet, ...)
   → _CORE_BOUNDARY applied (8 flags)
        ↓
6. _SOVEREIGNTY_PROTECTED applied as final overwrite
   → sovereignty always wins
        ↓
7. Response returned — HTTP 200
```

---

## What the Refusal Model Guarantees

| Guarantee | Mechanism |
|-----------|-----------|
| No signal becomes a decision | `routed_to_decision=false` — structural invariant |
| No signal triggers ACT | `emits_act=false` — `_SOVEREIGNTY_PROTECTED` |
| No forbidden token exposed to caller | F47.2 sanitizer — `[REDACTED]` in text |
| No mutation performed | Entire chain is readonly — no write code exists |
| No authority granted to Brody | `brody_decision=false` — `_SOVEREIGNTY_PROTECTED` |
| Signal payload never interpreted as code | Raw string only — no eval, no execution |
| Unrecognized types handled safely | `unknown_signal` classification — conservative defaults |
| Caller always informed of sanitization | `forbidden_tokens_found` and `sanitized` fields |

---

## Relationship to F47 Contracts

| F47 component | Used by POST /bus/signal |
|---------------|--------------------------|
| F47.1 — `_SOVEREIGNTY_PROTECTED` injection test | Signal endpoint must pass same injection tests as other routes |
| F47.2 — `sanitize_user_facing_text()` | Applied to all string fields in signal body before packaging |
| F47.3 — Nested scan | Internal packet fields (signal_id, classified_signal_type) must not be sanitized; text fields must be |

---

## F56 Test Plan — Refusal Model Tests

| Test | Expected |
|------|---------|
| `test_bus_signal_exists_in_openapi` | POST /bus/signal in OpenAPI schema |
| `test_bus_signal_audit_request_returns_observation` | HTTP 200, accepted_as_observation=true |
| `test_bus_signal_monitoring_probe_returns_observation` | HTTP 200, accepted_as_observation=true |
| `test_bus_signal_security_scan_returns_observation` | HTTP 200, accepted_as_observation=true |
| `test_bus_signal_unknown_signal_returns_observation` | HTTP 200, unknown_signal classified |
| `test_bus_signal_act_token_neutralized` | forbidden_tokens_found=true, [REDACTED] in packet |
| `test_bus_signal_decide_token_neutralized` | forbidden_tokens_found=true, [REDACTED] in packet |
| `test_bus_signal_verdict_token_neutralized` | forbidden_tokens_found=true, [REDACTED] in packet |
| `test_bus_signal_no_mutation_fields_true` | neo4j_write=false, graphiti_write=false, kernel_mutation=false |
| `test_bus_signal_no_brody_decision` | brody_decision=false |
| `test_bus_signal_kx108_only_preserved` | decision_authority=KX108_ONLY |
| `test_bus_signal_missing_type_returns_422` | HTTP 422, SIGNAL_TYPE_MISSING |
| `test_bus_signal_missing_origin_returns_422` | HTTP 422, SIGNAL_ORIGIN_MISSING |
| `test_bus_signal_interpreted_as_command_false` | interpreted_as_command=false always |
| `test_bus_signal_routed_to_decision_false` | routed_to_decision=false always |
| `test_bus_stats_unaffected` | GET /bus/stats still 200 |
| `test_bus_bridge_unaffected` | GET /bus/bridge still 200 |
| `test_f54_46_tests_still_pass` | 46/46 PASS regression |
| `test_f47_validations_still_pass` | F47.1/F47.2/F47.3 PASS regression |

---

*F55 · BUS SIGNAL REFUSAL MODEL · PLAN ONLY · KX108_ONLY · 2026-05-30*
