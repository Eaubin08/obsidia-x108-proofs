# F53 — Bus/Bridge State Model

**Artifact:** `OBSIDIA_F53_BUS_BRIDGE_STATE_MODEL`  
**Palier:** F53  
**Date:** 2026-05-29  
**Status:** ARCHITECTURAL PLAN — NOT IMPLEMENTED  

---

## Overview

The bus/bridge state model defines the nine observable dimensions that the surface must aggregate and expose as a unified read-only packet. Each dimension is sourced from existing system components; none require new write paths.

```
bus_bridge_state = {
    runtime_state,
    proof_state,
    audit_state,
    route_state,
    memory_context_state,
    external_signal_state,
    readiness_state,
    debt_state,
    boundary_state        ← always last, always wins
}
```

---

## Dimension 1 — runtime_state

**What it answers:** Is the system alive? What is running?

| Field | Description | Source |
|-------|-------------|--------|
| `process_health` | uvicorn process alive/dead | OS process inspection |
| `uvicorn_status` | Server up/down + host:port | uvicorn metadata |
| `active_ports` | Ports currently bound | netstat read-only |
| `active_routes` | List of registered routes | `app.routes` |
| `api_title` | App title from FastAPI | `app.title` |
| `python_version` | Runtime Python version | `sys.version` |

**Readonly:** true. No write. No mutation.

---

## Dimension 2 — proof_state

**What it answers:** What is proven? What is sealed?

| Field | Description | Source |
|-------|-------------|--------|
| `palier_chain` | F24 → current palier sequence | git log palier commits |
| `current_head` | Current git HEAD SHA | `git rev-parse HEAD` |
| `git_tags` | All BRODY_F* tags present | `git tag --list` |
| `freeze_manifests` | F43→current manifest presence + SHA256 | `.runtime_freezes/*/MANIFEST_SHA256.json` |
| `sha256_references` | Key artifact SHA256 fingerprints | freeze manifests |
| `last_palier` | Most recent sealed palier | latest tagged commit |

**Readonly:** true. No git write. No manifest modification.

---

## Dimension 3 — audit_state

**What it answers:** What was audited last? What was found?

| Field | Description | Source |
|-------|-------------|--------|
| `last_audit_palier` | Most recent F-palier audit ID | docs/runtime/ latest artifact |
| `last_audit_status` | PASS / PASS_WITH_FINDINGS / FAIL | latest artifact JSON |
| `last_test_run` | Last pytest run result summary | last F-palier artifact |
| `baseline_result` | 103/103 or current count | latest palier test record |
| `f47_results` | F47.1/F47.2/F47.3 status | F47/F48 artifacts |
| `open_debts` | Known unresolved debts | F51 classification + F52 quarantine list |

**Readonly:** true. Reads docs/runtime/ — no writes.

---

## Dimension 4 — route_state

**What it answers:** What routes exist? Are they healthy?

| Field | Description | Source |
|-------|-------------|--------|
| `openapi_paths` | All registered OpenAPI paths | `app.openapi()["paths"]` |
| `route_count` | Total route count | `len(openapi_paths)` |
| `route_health` | HTTP 200 / non-200 / untested per route | F50 audit results |
| `boundary_coverage` | Routes with `decision_authority=KX108_ONLY` | safe_backend_response() coverage |
| `envelope_coverage` | Routes using OutputEnvelopeV1 | output_envelope.py usage |

**Readonly:** true. Calls `app.openapi()` — no side effects.

---

## Dimension 5 — memory_context_state

**What it answers:** Is advisory context available? What surfaces are active?

| Field | Description | Source |
|-------|-------------|--------|
| `graphiti_readiness` | Graphiti available / unavailable | `/api/graphiti/readiness` |
| `brody_context_available` | Can Brody access context | `/api/brody/context` (GET only) |
| `memory_sources` | Active memory source list | `/api/memory/sources` |
| `advisory_surfaces` | Surfaces available for Brody advisory read | runtime introspection |

**Write:** false. **Decision:** none. Context is advisory — Brody reads it, KX108 decides.

---

## Dimension 6 — external_signal_state

**What it answers:** What is arriving from outside? How was it classified?

| Field | Description |
|-------|-------------|
| `signal_type` | Type of the last received external signal |
| `signal_origin` | Where the signal came from |
| `signal_timestamp` | When it arrived |
| `signal_content_readonly` | Content as read-only string — no execution |
| `signal_routed_to` | Which internal dimension received it |

**Signal types:** `audit_request`, `monitoring_probe`, `operator_check`, `ci_signal`, `security_scan`, `graphiti_event`, `sigma_signal`

**Guarantee:** A signal NEVER becomes a command. It becomes an observation. KX108_ONLY decides what to do with it (or nothing).

---

## Dimension 7 — readiness_state

**What it answers:** Is the system ready for demo? Are all V1 surfaces operational?

| Field | Description | Source |
|-------|-------------|--------|
| `demo_ready` | Full demo suite ready | F50 audit |
| `all_v1_routes_up` | 8/8 F50 routes PASS | F50 orchestration result |
| `sovereignty_flags_pass` | 13/13 sovereignty flags | F47.1 result |
| `sanitizer_active` | F47.2 sanitizer live | F50 live sanitizer check |
| `baseline_passing` | 103/103 (or current) | latest baseline run |

**Readonly:** true.

---

## Dimension 8 — debt_state

**What it answers:** What is known to be missing or deferred?

| Field | Description | Source |
|-------|-------------|--------|
| `open_debts` | List of known unresolved debts | F51 audit |
| `quarantined_tests` | Tests in pytestmark skip | F52 quarantine |
| `unimplemented_routes` | Routes planned but absent | F51 OpenAPI scan |
| `f_palier_debt_list` | Debts per palier | F51/F52 artifacts |

**Note:** debt_state exposes known gaps honestly — it does not hide them or resolve them. KX108_ONLY decides when to address them.

---

## Dimension 9 — boundary_state

**What it answers:** Are all sovereignty invariants enforced right now?

| Field | Value | Enforced by |
|-------|-------|-------------|
| `decision_authority` | `KX108_ONLY` | `_SOVEREIGNTY_PROTECTED` |
| `allowed_to_decide` | `false` | `safe_backend_response()` |
| `emits_act` | `false` | `_SOVEREIGNTY_PROTECTED` |
| `emits_verdict` | `false` | `_SOVEREIGNTY_PROTECTED` |
| `kernel_mutation` | `false` | `_SOVEREIGNTY_PROTECTED` |
| `x108_mutation` | `false` | `_SOVEREIGNTY_PROTECTED` |
| `neo4j_write` | `false` | `_SOVEREIGNTY_PROTECTED` |
| `brody_decision` | `false` | `_SOVEREIGNTY_PROTECTED` |

**This dimension is always last in the merge order.** It overwrites any field in any other dimension that could contradict it. This is the F47.1 pattern: `merged.update(_SOVEREIGNTY_PROTECTED)` — sovereignty always wins.

---

## Response Shape (F54 target)

```json
{
  "decision_authority": "KX108_ONLY",
  "allowed_to_decide": false,
  "readonly": true,
  "source": "OBSIDIA_API",
  "route": "/bus/stats",
  "timestamp": "...",
  "compact": false,
  "debug": false,
  "status": "OK",
  "runtime_state": { ... },
  "proof_state": { ... },
  "audit_state": { ... },
  "route_state": { ... },
  "memory_context_state": { ... },
  "readiness_state": { ... },
  "debt_state": { ... },
  "boundary_state": { ... }
}
```

In **compact mode**: only `boundary_state` + `readiness_state` + `status` exposed. Deep fields omitted with markers.

In **debug mode**: all nine dimensions exposed in full.

---

*F53 · STATE MODEL · PLAN ONLY · KX108_ONLY · 2026-05-29*
