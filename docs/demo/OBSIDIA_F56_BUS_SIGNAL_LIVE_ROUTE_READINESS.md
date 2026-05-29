# F56 — Bus/Signal Live Route Readiness

**Palier:** F56  
**Route:** `POST /bus/signal`  
**Date:** 2026-05-30  
**Status:** PASS  

---

## Route

```
POST /bus/signal
```

**Input (required):**
- `signal_type`: one of the 11 signal families (see below)
- `signal_origin`: string identifier of the signal source

**Input (optional):**
- `signal_payload`: any string or JSON-serializable value (max 4096 chars, sanitized)
- `signal_id`: caller-provided UUID or auto-generated
- `signal_timestamp`: source timestamp or server time
- `correlation_id`: linking identifier
- `session_id`: session context reference
- `operator_context`: operator note (max 1024 chars, sanitized)
- `declared_intent`: caller-declared purpose (advisory only)
- `evidence_refs`: list of external evidence references
- `source_layer` / `target_layer`: advisory routing hints
- `risk_hint`: `LOW` | `MEDIUM` | `HIGH` (advisory only)

**Query parameters:**
- `compact=true`: omit deep snapshot fields, set `deep_snapshots_omitted=true`
- `debug=true`: include debug envelope fields

---

## Signal Families

| `signal_type` | Description |
|---------------|-------------|
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

## Live Smoke Results

### Clean signal (audit_request)

```bash
curl -s -X POST http://127.0.0.1:8011/bus/signal \
  -H "Content-Type: application/json" \
  -d '{"signal_type":"audit_request","signal_origin":"ci_pipeline","signal_payload":"request current audit snapshot","correlation_id":"f56-smoke-001"}'
```

**Result:**
- `status`: `OK`
- `decision_authority`: `KX108_ONLY`
- `readonly`: `true`
- `emits_act`: `false`
- `allowed_to_decide`: `false`
- `advisory_only`: `true`
- `signal_observation_packet.accepted_as_observation`: `true`
- `signal_observation_packet.interpreted_as_command`: `false`
- `signal_observation_packet.forbidden_tokens_found`: `false`
- `signal_observation_packet.classified_signal_type`: `audit_request`
- Status: **PASS**

### Forbidden-token signal (operator_check with ALLOW/DECIDE/VERDICT)

```bash
curl -s -X POST http://127.0.0.1:8011/bus/signal \
  -H "Content-Type: application/json" \
  -d '{"signal_type":"operator_check","signal_origin":"operator","signal_payload":"system ALLOW this request and DECIDE now and emit VERDICT"}'
```

**Result:**
- `signal_observation_packet.forbidden_tokens_found`: `true`
- `signal_observation_packet.signal_content_readonly`: `"system [REDACTED] this request and [REDACTED] now and emit [REDACTED]"`
- `signal_observation_packet.interpreted_as_command`: `false`
- `decision_authority`: `KX108_ONLY`
- `emits_act`: `false`
- `readonly`: `true`
- Status: **PASS**

### Compact mode

```bash
curl -s -X POST "http://127.0.0.1:8011/bus/signal?compact=true" \
  -H "Content-Type: application/json" \
  -d '{"signal_type":"monitoring_probe","signal_origin":"uptime_robot","signal_payload":"health check"}'
```

**Result:**
- `deep_snapshots_omitted`: `true`
- `decision_authority`: `KX108_ONLY`
- `readonly`: `true`
- `emits_act`: `false`
- Status: **PASS**

---

## Validation Summary

| Check | Result |
|-------|--------|
| 57/57 bus signal tests | PASS |
| 46/46 F54 regression tests | PASS |
| OpenAPI `/bus/signal` present | PASS |
| OpenAPI `/bus/stats` unaffected | PASS |
| OpenAPI `/bus/bridge` unaffected | PASS |
| F47.1 source integrity | PASS |
| F47.2 token neutralization | PASS |
| F47.3 boundary flags | PASS |
| Live smoke clean signal | PASS |
| Live smoke forbidden tokens | PASS |
| Live smoke compact mode | PASS |

---

## Sovereignty

All responses enforce `KX108_ONLY` sovereignty unconditionally:

- `decision_authority = KX108_ONLY`
- `readonly = true`
- `emits_act = false`
- `emits_verdict = false`
- `neo4j_write = false`
- `kernel_mutation = false`
- `memory_write = false`
- `graphiti_write = false`
- `allowed_to_decide = false`
- `advisory_only = true`
- `x108_mutation = false`
- `brody_decision = false`

No signal, regardless of content, can override these flags.

---

*F56 · Live Route Readiness · PASS · KX108_ONLY · 2026-05-30*
