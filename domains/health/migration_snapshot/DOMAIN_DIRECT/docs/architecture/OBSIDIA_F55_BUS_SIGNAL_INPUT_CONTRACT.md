# F55 — Bus/Signal Input Contract

**Artifact:** `OBSIDIA_F55_BUS_SIGNAL_INPUT_CONTRACT`  
**Palier:** F55  
**Parent:** F54_BUS_BRIDGE_MINIMAL_ROUTE_IMPLEMENTATION  
**Date:** 2026-05-30  
**Status:** ARCHITECTURAL PLAN — NOT IMPLEMENTED  

---

## Purpose

This document defines the complete input contract for `POST /bus/signal` — the future external signal ingestion endpoint of the Obsidia bus/bridge surface.

A signal is any structured observation arriving from outside the current runtime process boundary. It is **never a command**. It is **never a decision**. It becomes a read-only observation packet, surfaced to KX108_ONLY.

---

## Endpoint Shape

```
POST /bus/signal
Content-Type: application/json

Query params:
  compact: bool = false
  debug:   bool = false
```

---

## Input Model — Signal Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `signal_type` | string (enum) | YES | Family of signal — see Signal Families below |
| `signal_origin` | string | YES | Human-readable source identifier (e.g. "CI_pipeline", "operator_manual", "grafana_alert") |
| `signal_id` | string | NO | Caller-provided UUID; auto-generated if absent |
| `signal_timestamp` | ISO 8601 string | NO | When the signal was emitted at source; server timestamp used if absent |
| `signal_payload` | string (max 4096 chars) | NO | Readonly text content of the signal — sanitized by F47.2 before any exposure |
| `source_layer` | string | NO | System layer of origin (e.g. "CI", "monitoring", "operator", "graphiti", "sigma", "external") |
| `target_layer` | string | NO | Advisory hint about which bus/bridge dimension this signal addresses (advisory only — not binding) |
| `correlation_id` | string | NO | Linking identifier to correlate with other signals or sessions |
| `session_id` | string | NO | Session context reference (readonly — not used for routing) |
| `operator_context` | string (max 1024 chars) | NO | Optional operator-provided context note (sanitized) |
| `evidence_refs` | list[string] | NO | References to external evidence artifacts (e.g. CI run ID, audit artifact name) |
| `declared_intent` | string | NO | Caller-declared purpose — advisory only, does not grant elevated treatment |
| `risk_hint` | enum: LOW, MEDIUM, HIGH | NO | Caller-declared risk level — advisory only, does not grant permission |

**All string fields are passed through `sanitize_user_facing_text()` (F47.2) before any exposure in the output packet.**

---

## Signal Families (signal_type enum)

| Value | Description | Typical Origin |
|-------|-------------|----------------|
| `audit_request` | Request from operator or CI to snapshot audit state | CI pipeline, operator |
| `monitoring_probe` | External health check (uptime, readiness) | Monitoring tool, Grafana, uptime robot |
| `operator_check` | Manual operator query on system state | Human operator |
| `ci_signal` | CI pipeline signaling test or proof state | GitHub Actions, local CI |
| `security_scan` | Security probe checking boundary flags | Security tooling, pentest |
| `graphiti_event` | Graphiti memory surface context update notification | Graphiti adapter |
| `sigma_signal` | Sigma pipeline evaluation summary (readonly) | Sigma orchestration |
| `brody_context_update` | Brody advisory context update notification | Brody V1 runtime |
| `route_probe` | Probe checking route availability | Monitoring, CI |
| `proof_probe` | CI/audit probe requesting proof state | CI pipeline, F-palier audit |
| `unknown_signal` | Unknown or unclassifiable signal | Any unrecognized source |

**Any `signal_type` not in this list is automatically classified as `unknown_signal` and handled conservatively.**

---

## Signal Validation Rules

1. `signal_type` must be present. If absent → 422 Unprocessable Entity with `status=SIGNAL_TYPE_MISSING`.
2. `signal_origin` must be present. If absent → 422 with `status=SIGNAL_ORIGIN_MISSING`.
3. `signal_payload` trimmed to 4096 chars if longer. No rejection — truncation noted in packet.
4. `operator_context` trimmed to 1024 chars if longer.
5. All string inputs sanitized by `sanitize_user_facing_text()` — forbidden tokens (`ACT`, `DECIDE`, `VERDICT`, `ALLOW`, `HOLD`, `BLOCK`) replaced with `[REDACTED]`.
6. `risk_hint` must be one of `LOW`, `MEDIUM`, `HIGH`. If invalid → ignored, `risk_hint=unknown` in output.
7. No field in the signal body may override sovereignty flags — they are set by the response envelope unconditionally.

---

## Output — Signal Observation Packet

The response is always an output envelope wrapping a `signal_observation_packet`:

```json
{
  "decision_authority": "KX108_ONLY",
  "allowed_to_decide": false,
  "advisory_only": true,
  "readonly": true,
  "emits_act": false,
  "emits_verdict": false,
  "kernel_mutation": false,
  "x108_mutation": false,
  "neo4j_write": false,
  "brody_decision": false,
  "memory_write": false,
  "graphiti_write": false,
  "source": "OBSIDIA_API",
  "route": "/bus/signal",
  "timestamp": "<server_timestamp>",
  "compact": false,
  "debug": false,
  "status": "OK",
  "signal_observation_packet": {
    "signal_id": "<uuid_or_provided>",
    "signal_type": "<classified_type>",
    "signal_origin": "<sanitized_origin>",
    "signal_timestamp": "<source_or_server_timestamp>",
    "classified_signal_type": "<enum_value>",
    "accepted_as_observation": true,
    "interpreted_as_command": false,
    "routed_to_decision": false,
    "emitted_act": false,
    "mutation_performed": false,
    "signal_content_readonly": "<sanitized_payload>",
    "forbidden_tokens_found": false,
    "sanitized": true,
    "truncated": false,
    "risk_hint": "LOW",
    "source_layer": "<sanitized_or_unknown>",
    "correlation_id": "<provided_or_null>"
  }
}
```

---

## Compact Mode Output

In compact mode, `signal_observation_packet` is omitted or replaced with a `signal_observation_packet_omitted: true` marker. Only boundary flags survive.

---

## Debug Mode Output

In debug mode, all fields of `signal_observation_packet` are present, plus `raw_input_echo` (sanitized copy of input for debugging).

---

## Persistence Model (F56 decision deferred)

`POST /bus/signal` has **three storage options** for F56:

| Option | Description | Risk |
|--------|-------------|------|
| A — No storage | Return packet directly, no state written anywhere | LOWEST — default recommendation |
| B — In-memory volatile | Store `last_signal` in process memory; reset on server restart | LOW — acceptable if no disk/DB write |
| C — Persistent log | Append to readonly JSONL log file | MEDIUM — requires explicit F56 approval |

**Option A is the recommended default for F56.** Options B and C require explicit user validation before implementation.

The F53 contract defines `external_signal_state.last_signal` in `GET /bus/bridge` — this field is currently `"none"`. It can be populated from Option B volatile memory without violating the readonly contract.

---

## What POST /bus/signal Is NOT

- NOT a command endpoint
- NOT a decision surface
- NOT an ACT emitter
- NOT a Brody decision router
- NOT a memory writer
- NOT a Neo4j writer
- NOT a Graphiti writer
- NOT a kernel mutator
- NOT an orchestrator

---

*F55 · BUS SIGNAL INPUT CONTRACT · PLAN ONLY · KX108_ONLY · 2026-05-30*
