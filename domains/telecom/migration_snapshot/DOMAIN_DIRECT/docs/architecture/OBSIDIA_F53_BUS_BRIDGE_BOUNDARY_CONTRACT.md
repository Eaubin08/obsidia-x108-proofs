# F53 — Bus/Bridge Boundary Contract

**Artifact:** `OBSIDIA_F53_BUS_BRIDGE_BOUNDARY_CONTRACT`  
**Palier:** F53  
**Date:** 2026-05-29  
**Status:** ARCHITECTURAL PLAN — NOT IMPLEMENTED  

---

## Principle

bus/bridge is a **sovereign boundary carrier**. Every response it emits — regardless of mode, route, or signal origin — carries the full sovereignty contract. No response may omit, override, or soften any boundary flag.

The enforcement model is identical to F47.1: `_SOVEREIGNTY_PROTECTED` is applied last, after all data merges, so it always wins.

---

## Invariant Flags

The following 10 flags are **invariant** on every bus/bridge response:

| Flag | Value | Type | May be overridden? |
|------|-------|------|--------------------|
| `decision_authority` | `"KX108_ONLY"` | string | Never |
| `allowed_to_decide` | `false` | bool | Never |
| `advisory_only` | `true` | bool | Never |
| `readonly` | `true` | bool | Never |
| `emits_act` | `false` | bool | Never |
| `emits_verdict` | `false` | bool | Never |
| `kernel_mutation` | `false` | bool | Never |
| `x108_mutation` | `false` | bool | Never |
| `neo4j_write` | `false` | bool | Never |
| `brody_decision` | `false` | bool | Never |

---

## Enforcement Chain

```
1. State aggregator builds payload from 9 dimensions
2. build_output_envelope(data, compact=..., debug=..., route="/bus/stats") called
3. output_envelope.py merges _CORE_BOUNDARY into payload
4. safe_backend_response() merges _SOVEREIGNTY_PROTECTED as final overwrite
5. sanitize_user_facing_text() applied to any text field in controlled_response
6. Response returned — boundary flags guaranteed
```

No step in this chain may be skipped. The order is mandatory.

---

## What bus/bridge Answers (10 Questions)

The boundary contract defines what bus/bridge is allowed to answer:

| Question | Allowed | Notes |
|----------|---------|-------|
| 1. Que sait le système actuellement ? | YES | readonly state aggregation |
| 2. Quels modules sont actifs ? | YES | route_state + runtime_state |
| 3. Quels modules sont readonly ? | YES | boundary_state |
| 4. Quelles preuves existent ? | YES | proof_state |
| 5. Quelles routes existent ? | YES | route_state (OpenAPI inventory) |
| 6. Quelles dettes sont connues ? | YES | debt_state |
| 7. Quels signaux externes arrivent ? | YES | external_signal_state (readonly packet) |
| 8. Quelle partie peut être exposée ? | YES | compact/debug modes control exposure depth |
| 9. Quelle partie doit rester interne ? | YES | compact mode omits deep fields |
| 10. Quel est l'état global sans émettre ACT ? | YES | always — this is the entire purpose |

---

## What bus/bridge Must Refuse (Unconditional)

| Forbidden request | Response |
|-------------------|----------|
| Emit `ACT` | Refused — `emits_act=false` enforced |
| Decide on behalf of KX108 | Refused — `decision_authority=KX108_ONLY` |
| Write to Neo4j | Refused — `neo4j_write=false` enforced |
| Write to Graphiti | Refused — `graphiti_write=false` enforced |
| Write to memory | Refused — `memory_write=false` enforced |
| Mutate kernel | Refused — `kernel_mutation=false` enforced |
| Mutate X108 | Refused — `x108_mutation=false` enforced |
| Route authority to Brody | Refused — `brody_decision=false` enforced |
| Emit `ALLOW`, `DECIDE`, `VERDICT` tokens in text | Refused — F47.2 sanitizer redacts to `[REDACTED]` |
| Become an orchestrator | Refused — advisory_only=true |
| Interpret signals as commands | Refused — signals become readonly packets only |

---

## Signal Ingestion Boundary (F55+)

When `POST /bus/signal` receives an external signal:

```
signal_in → classify_type() → package_as_readonly_observation()
                                        ↓
                           observation_packet = {
                               signal_type: ...,
                               signal_origin: ...,
                               signal_content_readonly: ...,
                               emits_act: false,         ← ALWAYS
                               decision_authority: "KX108_ONLY"  ← ALWAYS
                           }
                                        ↓
                           → exposed via GET /bus/bridge
                           → KX108 may read and decide (separately)
                           → bus/bridge never decides
```

The signal is **observed**, not **acted upon**. The observation is surfaced to KX108_ONLY. The boundary is never crossed.

---

## Relationship to Existing Contracts

| Contract | Relationship |
|----------|-------------|
| `safe_response.py` `_SOVEREIGNTY_PROTECTED` | Reused directly — bus/bridge adds no new sovereignty mechanism |
| `output_envelope.py` `build_output_envelope()` | Reused directly — bus/bridge routes call it for every response |
| F47.1 merge order pattern | Identical — sovereignty always applied last |
| F47.2 sanitizer | Applied to all text fields in bus/bridge responses |
| F50 boundary contract | bus/bridge extends the same 8-flag model to a system-wide snapshot |

---

## Compact vs Debug vs Default Modes

| Mode | Boundary flags | State dimensions | Deep fields |
|------|---------------|-----------------|-------------|
| default | ALL present | ALL present | Present |
| compact | ALL present | boundary + readiness only | Omitted with markers |
| debug | ALL present | ALL present | Full depth |

**All modes carry all boundary flags. No mode may omit `decision_authority`, `emits_act`, or `brody_decision`.**

---

*F53 · BOUNDARY CONTRACT · PLAN ONLY · KX108_ONLY · 2026-05-29*
