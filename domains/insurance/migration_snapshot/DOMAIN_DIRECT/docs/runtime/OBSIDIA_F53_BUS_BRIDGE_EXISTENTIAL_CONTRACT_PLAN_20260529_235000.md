# F53 — Bus/Bridge Existential Contract Plan

**Artifact:** `OBSIDIA_F53_BUS_BRIDGE_EXISTENTIAL_CONTRACT_PLAN_20260529_235000`  
**Palier:** F53  
**Parent:** F52_BUS_BRIDGE_QUARANTINE  
**Status:** PASS  
**Head:** 6d2fe96  
**Parent tag:** BRODY_F52_BUS_BRIDGE_QUARANTINE_PALIER_20260529  
**Date:** 2026-05-29  

---

## Purpose

F53 defines the complete existential contract of the bus/bridge surface. This is a PLAN palier — no implementation, no routes created, no runtime modified.

F53 answers the question: *What must bus/bridge be, completely and correctly, before F54 implements it?*

---

## Conceptual Model

**bus/bridge is the epistemic surface of the Obsidia system.**

It is the single interface through which the system answers:

> *"What does the system know right now, without deciding anything?"*

It aggregates observable state from all layers — runtime, proofs, audit, routes, memory, Graphiti, Brody context, external signals — and exposes it as a read-only packet under `KX108_ONLY` sovereignty.

| bus/bridge IS | bus/bridge IS NOT |
|--------------|------------------|
| Readonly state aggregator | Decision authority |
| Observable system snapshot | Orchestrator |
| External signal ingress (readonly) | ACT emitter |
| Sovereign boundary carrier | Kernel mutator |
| Audit and proof mirror | Memory writer |
|  | Brody decider |

---

## State Model

See `docs/architecture/OBSIDIA_F53_BUS_BRIDGE_STATE_MODEL.md` for full specification.

### Nine dimensions

| Dimension | Source | Readonly |
|-----------|--------|----------|
| `runtime_state` | uvicorn introspection + OpenAPI | true |
| `proof_state` | git log + .runtime_freezes/ manifests | true |
| `audit_state` | docs/runtime/ audit artifacts | true |
| `route_state` | app.openapi() + safe_backend_response() coverage | true |
| `memory_context_state` | /api/graphiti/readiness + /api/memory/status | true |
| `external_signal_state` | /bus/signal ingress (F55+) | true |
| `readiness_state` | /api/periphery/demo/runtime-readiness + F50 | true |
| `debt_state` | F51/F52 audit artifacts | true |
| `boundary_state` | _SOVEREIGNTY_PROTECTED always wins | true |

---

## Boundary Contract

See `docs/architecture/OBSIDIA_F53_BUS_BRIDGE_BOUNDARY_CONTRACT.md` for full specification.

| Flag | Value | Enforced by |
|------|-------|-------------|
| `decision_authority` | `KX108_ONLY` | `_SOVEREIGNTY_PROTECTED` overwrite |
| `allowed_to_decide` | `false` | `safe_backend_response()` |
| `advisory_only` | `true` | `safe_backend_response()` |
| `readonly` | `true` | `safe_backend_response()` |
| `emits_act` | `false` | `_SOVEREIGNTY_PROTECTED` |
| `emits_verdict` | `false` | `_SOVEREIGNTY_PROTECTED` |
| `kernel_mutation` | `false` | `_SOVEREIGNTY_PROTECTED` |
| `x108_mutation` | `false` | `_SOVEREIGNTY_PROTECTED` |
| `neo4j_write` | `false` | `_SOVEREIGNTY_PROTECTED` |
| `brody_decision` | `false` | `_SOVEREIGNTY_PROTECTED` |

---

## Future Routes Plan

| Route | Status | Palier | Description |
|-------|--------|--------|-------------|
| `GET /bus/stats` | PLANNED | F54 | Synthetic readonly state snapshot of the entire system |
| `GET /bus/bridge` | PLANNED | F54 | Connective state: signals, memory, Graphiti, debt |
| `POST /bus/signal` | OPTIONAL_LATER | F55+ | Ingest external signal as readonly observation packet |

### Implementation prerequisites for F54

| Component | Status |
|-----------|--------|
| `apps/obsidia_api/output_envelope.py` | EXISTS — ready to use |
| `apps/obsidia_api/bus/state_aggregator.py` | NEEDS CREATION |
| `apps/obsidia_api/routes/bus.py` | NEEDS CREATION |
| `apps/obsidia_api/main.py` include_router | NEEDS UPDATE |

Risk: **LOW** — additive only; existing routes unaffected.

---

## External Signal Model

An external signal is any input arriving from outside the current runtime process boundary.

| Signal type | Description |
|-------------|-------------|
| `audit_request` | Operator/CI requests current audit snapshot |
| `monitoring_probe` | External health check (uptime, readiness) |
| `operator_check` | Manual operator query on system state |
| `ci_signal` | CI pipeline requesting test or proof state |
| `security_scan` | Probe checking boundary flags |
| `graphiti_event` | Graphiti emitting a context update notification |
| `sigma_signal` | Sigma pipeline emitting evaluation summary (readonly) |

**Ingestion protocol (future F55+):**

1. Signal received by `POST /bus/signal`
2. Classified by type — no interpretation
3. Packaged as read-only observation packet
4. Exposed via `/bus/bridge` response
5. **No ACT emitted. No mutation. KX108_ONLY decides.**

---

## Refusal Model

bus/bridge must refuse unconditionally:

- Any request to emit `ACT`
- Any request to decide on behalf of KX108
- Any write to Neo4j, Graphiti, or memory
- Any kernel or X108 mutation
- Any routing of authority to Brody
- Any transformation into an orchestrator
- Any interpretation of signals as commands
- Any response text containing `ALLOW`, `DECIDE`, `VERDICT` tokens

**Enforcement:** `safe_backend_response()` + `_SOVEREIGNTY_PROTECTED` overwrite after every data merge (F47.1 pattern).

---

## Test Strategy for F54

**Quarantine reactivation:**  
Remove `pytestmark = pytest.mark.skip(...)` from `test_output_envelope_bus_stats.py` and `test_output_envelope_bus_bridge.py` after F54 implementation. Expected: 46 tests pass cleanly.

**New tests needed in F54:**

- `test_bus_stats_route_exists_in_openapi`
- `test_bus_stats_boundary_all_flags`
- `test_bus_stats_compact_mode_omits_deep_fields`
- `test_bus_stats_debug_mode_exposes_all`
- `test_bus_bridge_route_exists_in_openapi`
- `test_bus_bridge_external_signal_state_readonly`
- `test_bus_bridge_memory_context_advisory_only`
- `test_bus_bridge_no_write_fields`
- `test_bus_bridge_boundary_KX108_ONLY`
- `test_bus_signal_post_returns_readonly_packet` (F55+)
- `test_bus_signal_never_emits_act` (F55+)
- `test_bus_signal_forbidden_tokens_absent_in_response` (F55+)

**Regression requirement:** All F50 baseline routes must pass after F54.

---

## F53 Constraints

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

`docs/runtime/OBSIDIA_F53_BUS_BRIDGE_EXISTENTIAL_CONTRACT_PLAN_20260529_235000.json`  
SHA256: `9B682EA0A928289887F16B229FEE0CA34FFA28240BB1E41B1CED867FA9509562`

---

*F53 · PLAN ONLY · PASS · KX108_ONLY · 2026-05-29*
