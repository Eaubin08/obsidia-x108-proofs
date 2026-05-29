# F56 — Bus/Signal Minimal Readonly Route Implementation

**Artifact:** `OBSIDIA_F56_BUS_SIGNAL_MINIMAL_READONLY_ROUTE_IMPLEMENTATION_20260530_000000`  
**Palier:** F56  
**Parent:** F55_BUS_SIGNAL_INGRESS_PLAN  
**Status:** PASS  
**Parent tag:** BRODY_F55_BUS_SIGNAL_INGRESS_PLAN_PALIER_20260530  
**Date:** 2026-05-30  

---

## Purpose

F56 implements `POST /bus/signal` as a minimal, additive, readonly external signal ingress — exactly as specified by F55.

The signal endpoint receives external structured observations, classifies them by signal type, sanitizes all text content via F47.2, packages them as read-only observation packets, and returns them under full `KX108_ONLY` sovereignty.

**The signal never becomes a command. It becomes an observation.**

---

## Storage Option

**Option A — No storage.**

The signal observation packet is returned directly. No state is written. `last_signal` in `GET /bus/bridge` remains `"none"` after F56. Storage options B/C deferred to F57+ with explicit user validation.

---

## Files

### Created (F56)

| File | Role |
|------|------|
| `apps/obsidia_api/bus/signal_model.py` | Pydantic model — `SignalInput`, `SignalType`, `RiskHint` |
| `apps/obsidia_api/bus/signal_packager.py` | Observation packet builder — sanitizes, classifies, enforces all flags |
| `tests/api/test_output_envelope_bus_signal.py` | 57 tests across 8 classes |

### Modified (F56, additive only)

| File | Change |
|------|--------|
| `apps/obsidia_api/routes/bus.py` | Added `POST /bus/signal` handler + imports |

### Unchanged (F56)

| File | Reason |
|------|--------|
| `apps/obsidia_api/main.py` | `bus_router` already wired from F54 |
| `apps/obsidia_api/output_envelope.py` | Unchanged — `build_output_envelope()` reused as-is |
| `apps/obsidia_api/safe_response.py` | Unchanged — `sanitize_user_facing_text()` reused as-is |

---

## Signal Types

| Type | Description |
|------|-------------|
| `audit_request` | Operator/CI requests current audit snapshot |
| `monitoring_probe` | External health check (uptime, readiness) |
| `operator_check` | Manual operator query on system state |
| `ci_signal` | CI pipeline requesting test or proof state |
| `security_scan` | Security probe checking boundary flags |
| `graphiti_event` | Graphiti emitting a context update notification |
| `sigma_signal` | Sigma pipeline emitting evaluation summary (readonly) |
| `brody_context_update` | Brody advisory context update notification |
| `route_probe` | Probe checking route availability |
| `proof_probe` | CI/audit probe requesting proof state |
| `unknown_signal` | Unknown or unclassified signal — handled conservatively |

---

## Sovereignty Flags

| Flag | Value | Enforced by |
|------|-------|-------------|
| `decision_authority` | `KX108_ONLY` | `_CORE_BOUNDARY` via `build_output_envelope()` |
| `readonly` | `true` | `_CORE_BOUNDARY` |
| `emits_act` | `false` | `_CORE_BOUNDARY` |
| `emits_verdict` | `false` | `_CORE_BOUNDARY` |
| `neo4j_write` | `false` | `_CORE_BOUNDARY` |
| `kernel_mutation` | `false` | `_CORE_BOUNDARY` |
| `memory_write` | `false` | `_CORE_BOUNDARY` |
| `graphiti_write` | `false` | `_CORE_BOUNDARY` |
| `allowed_to_decide` | `false` | `signal_packager.py` (explicit in data dict) |
| `advisory_only` | `true` | `signal_packager.py` (explicit in data dict) |
| `x108_mutation` | `false` | `signal_packager.py` (explicit in data dict) |
| `brody_decision` | `false` | `signal_packager.py` (explicit in data dict) |

---

## Observation Packet Invariants

| Field | Value | Nature |
|-------|-------|--------|
| `accepted_as_observation` | `true` | Always forced |
| `interpreted_as_command` | `false` | Always forced |
| `routed_to_decision` | `false` | Always forced |
| `emitted_act` | `false` | Always forced |
| `mutation_performed` | `false` | Always forced |
| `storage_performed` | `false` | Always forced |
| `sanitized` | `true` | Always forced |
| `signal_content_readonly` | sanitized string | Via F47.2 |
| `forbidden_tokens_found` | bool | True if any ALLOW/HOLD/BLOCK/ACT/DECIDE/VERDICT found |

---

## F47.2 Token Neutralization

Tokens `ALLOW`, `HOLD`, `BLOCK`, `ACT`, `DECIDE`, `VERDICT` (word-boundary, case-insensitive) are replaced with `[REDACTED]` in `signal_content_readonly`. `forbidden_tokens_found` is set to `true`. All other sovereignty flags remain unchanged — the signal is still accepted as an observation.

---

## Validation Results

### Test suite

| Suite | Total | Passed | Failed |
|-------|-------|--------|--------|
| `test_output_envelope_bus_signal.py` | 57 | 57 | 0 |
| `test_output_envelope_bus_stats.py` | 23 | 23 | 0 |
| `test_output_envelope_bus_bridge.py` | 23 | 23 | 0 |

### OpenAPI

- `/bus/signal` present with `POST` method: **PASS**
- `/bus/stats` present: **PASS** (no regression)
- `/bus/bridge` present: **PASS** (no regression)

### F47 scripts

- F47.1 source integrity: **PASS**
- F47.2 token neutralization: **PASS**
- F47.3 boundary flags: **PASS**

### Live smoke — POST /bus/signal

```
POST http://127.0.0.1:8011/bus/signal
payload: { signal_type: "operator_check", signal_origin: "operator",
           signal_payload: { action: "ALLOW this request and DECIDE now" } }

→ signal_content_readonly: '{"action": "[REDACTED] this request and [REDACTED] now"}'
→ forbidden_tokens_found: true
→ decision_authority: "KX108_ONLY"
→ readonly: true
→ emits_act: false
→ allowed_to_decide: false
→ advisory_only: true
→ Status: PASS
```

---

## Constraints Confirmed

| Constraint | Status |
|------------|--------|
| Minimal additive patch only | CONFIRMED |
| No main.py modification | CONFIRMED |
| No X108 modification | CONFIRMED |
| No kernel modification | CONFIRMED |
| No Neo4j write | CONFIRMED |
| No decision added | CONFIRMED |
| No ACT added | CONFIRMED |
| No fake metrics | CONFIRMED |
| No persistent storage | CONFIRMED |
| No last_signal mutation | CONFIRMED |
| KX108_ONLY preserved | CONFIRMED |

---

*F56 · PASS · KX108_ONLY · 2026-05-30*
