# F55 — Bus/Signal Ingress Plan

**Artifact:** `OBSIDIA_F55_BUS_SIGNAL_INGRESS_PLAN_20260530_000000`  
**Palier:** F55  
**Parent:** F54_BUS_BRIDGE_MINIMAL_ROUTE_IMPLEMENTATION  
**Status:** PASS  
**Parent tag:** BRODY_F54_BUS_BRIDGE_MINIMAL_ROUTE_IMPLEMENTATION_PALIER_20260529  
**Date:** 2026-05-30  

---

## Purpose

F55 defines the complete ingestion contract for `POST /bus/signal` — the external signal endpoint of the Obsidia bus/bridge surface.

F55 is a **PLAN palier only**. No route is created. No runtime is modified. No main.py is touched.

F55 answers: *What must POST /bus/signal be, completely and correctly, before F56 implements it?*

---

## What POST /bus/signal Is

An **external signal ingress** — a read-only surface that:

1. Receives any structured observation arriving from outside the current runtime process boundary
2. Classifies it by signal type
3. Sanitizes all text content via F47.2 (`sanitize_user_facing_text()`)
4. Packages it as a read-only observation packet
5. Returns it under full `KX108_ONLY` sovereignty

**The signal never becomes a command. It becomes an observation.**

---

## What POST /bus/signal Is NOT

| Is NOT | Reason |
|--------|--------|
| Command endpoint | No signal is interpreted as a command |
| Decision surface | `routed_to_decision=false` always |
| ACT emitter | `emits_act=false` always |
| Brody decision router | `brody_decision=false` always |
| Memory writer | `memory_write=false` always |
| Neo4j writer | `neo4j_write=false` always |
| Graphiti writer | `graphiti_write=false` always |
| Kernel mutator | `kernel_mutation=false` always |
| Orchestrator | `advisory_only=true` always |

---

## Signal Families

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

## Input Model

| Field | Required | Description |
|-------|----------|-------------|
| `signal_type` | YES | Signal family (see above) |
| `signal_origin` | YES | Source identifier string |
| `signal_payload` | NO | Readonly text content (max 4096 chars, sanitized) |
| `signal_id` | NO | Caller-provided UUID or auto-generated |
| `signal_timestamp` | NO | Source timestamp or server time |
| `source_layer` | NO | System layer of origin |
| `target_layer` | NO | Advisory hint — not binding |
| `correlation_id` | NO | Linking identifier |
| `session_id` | NO | Session context reference |
| `operator_context` | NO | Operator note (max 1024 chars, sanitized) |
| `evidence_refs` | NO | List of external evidence references |
| `declared_intent` | NO | Caller-declared purpose (advisory only) |
| `risk_hint` | NO | LOW / MEDIUM / HIGH (advisory only) |

**All string fields sanitized via F47.2 before exposure.**

---

## Output — Signal Observation Packet

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
  "status": "OK",
  "signal_observation_packet": {
    "signal_id": "...",
    "signal_type": "audit_request",
    "classified_signal_type": "audit_request",
    "signal_origin": "CI_pipeline",
    "accepted_as_observation": true,
    "interpreted_as_command": false,
    "routed_to_decision": false,
    "emitted_act": false,
    "mutation_performed": false,
    "signal_content_readonly": "...",
    "forbidden_tokens_found": false,
    "sanitized": true,
    "risk_hint": "LOW"
  }
}
```

---

## Refusal Model Summary

| Condition | Action |
|-----------|--------|
| `signal_type` absent | HTTP 422 — `SIGNAL_TYPE_MISSING` |
| `signal_origin` absent | HTTP 422 — `SIGNAL_ORIGIN_MISSING` |
| Payload contains `ACT/DECIDE/VERDICT/ALLOW/HOLD/BLOCK` | `[REDACTED]` via F47.2, `forbidden_tokens_found=true` |
| Unrecognized `signal_type` | Classified as `unknown_signal` |
| Request implies mutation | `interpreted_as_command=false`, mutation flags false |
| Request implies decision authority | `routed_to_decision=false` — KX108_ONLY preserved |

Full refusal model: `docs/architecture/OBSIDIA_F55_BUS_SIGNAL_REFUSAL_MODEL.md`

---

## Storage Decision for F56

**Option A — No storage (recommended default).**

The signal observation packet is returned directly. No state is written. `last_signal` in `GET /bus/bridge` remains `"none"` after F56.

Storage options B (in-memory volatile) and C (persistent log) are deferred to F57+ with explicit user validation required.

---

## F56 Scope

| Action | Fichier | Type |
|--------|---------|------|
| Créer le modèle Pydantic signal | `apps/obsidia_api/bus/signal_model.py` | Nouveau |
| Créer le signal packager | `apps/obsidia_api/bus/signal_packager.py` | Nouveau |
| Ajouter POST /bus/signal | `apps/obsidia_api/routes/bus.py` | Modifié (additive) |
| Créer les tests F56 | `tests/api/test_output_envelope_bus_signal.py` | Nouveau |

`main.py` : **inchangé** — `bus_router` déjà inclus depuis F54.

**Risque F56 : FAIBLE** — uniquement additif.

---

## F55 Constraints

| Constraint | Status |
|------------|--------|
| No routes created | CONFIRMED |
| No runtime modified | CONFIRMED |
| No main.py modified | CONFIRMED |
| No kernel mutation | CONFIRMED |
| No X108 mutation | CONFIRMED |
| No Neo4j write | CONFIRMED |
| PLAN ONLY | CONFIRMED |

---

## JSON Artifact

`docs/runtime/OBSIDIA_F55_BUS_SIGNAL_INGRESS_PLAN_20260530_000000.json`

---

*F55 · PLAN ONLY · PASS · KX108_ONLY · 2026-05-30*
