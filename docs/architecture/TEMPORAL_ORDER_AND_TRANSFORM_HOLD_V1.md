# Temporal Order Invariant and Temporal Transform Hold (V1)

```
STATUS=ARCHITECTURE_FREEZE / DOCS_ONLY
FROZEN_ON=2026-10-07
ORIGIN=B8 V1 temporal certification (R4, R5) — docs/architecture/B8_KNOWLEDGE_PROMOTION_SPEC_V1.md
TEMPORAL_ORDER_INVARIANT=FROZEN
B8_DT01_STATUS=HOLD
B8_DT01_BLOCKS_B8_V1=NO
B8_DT01_IMPLEMENTED=NO
CROSS_FRAME_B8_V1=FORBIDDEN
```

This document is not a new B8 requirement. It records an architectural finding made while
certifying B8 V1: the deferred cross-frame temporal-transform work, the transversal
order / time / causality invariant, and the conditions under which the deferred work may reopen.
Registry choice: no cross-cutting deferred registry existed (`docs/semantic/SENS_DEFERRED_LIMITS_REGISTRY.md`
and `docs/semantic/SENS_PRE_FORGE_CANONICAL_ROADMAP.md` are SENS-scoped), so this single file holds
the freeze; the roadmap is referenced, not renumbered.

## 1. Transversal invariant (frozen)

```
RECEIVED_ORDER != WORLD_ORDER
RECORDED_ORDER != WORLD_ORDER
SERIALIZATION_ORDER != WORLD_ORDER
SERIALIZATION_ORDER != CAUSAL_ORDER
TIME_VALUE != TEMPORAL_ORDER
TIMESTAMP != CAUSALITY
ONE_SYSTEM != ONE_CLOCK
ONE_IDENTITY != ONE_TEMPORALITY
ONE_OBJECT → MANY_TEMPORAL_PROJECTIONS → NO_AUTOMATIC_FUSION
```

Obsidia never turns the order in which it receives, records, serializes or learns information into
the order of the world. A system history and a world history are related objects, not
automatically identical histories.

## 2. Distinct orders

| Order | Meaning | Example |
|---|---|---|
| SERIALIZATION ORDER | protocol / revision ordering | B8 `slot_revision` |
| OBJECT HISTORY ORDER | local history of one object | `record_version`, `gap_version`, future object versions |
| TEMPORAL ORDER | time situated inside a TemporalFrameRef / future TimeEnvelope | `valid_time` in one frame |
| CAUSAL ORDER | explicit typed causal relations only | typed X → Y relation |
| LEARNING ORDER | order in which the system discovers / acquires hypotheses | candidate capture |
| PROOF / ADMISSION ORDER | order in which hypotheses become verified / admissible | B8 T5 / T6 receipts |

These orders may correlate; they are never automatically fused.

## 3. B8-DT01 — TEMPORAL_TRANSFORM_ADMISSION

```
ID=B8-DT01
NAME=TEMPORAL_TRANSFORM_ADMISSION
STATUS=HOLD
BLOCKS_B8_V1=NO
```

B8 V1 policy: same temporal frame → temporal reasoning allowed; different frames →
`TEMPORALLY_INDETERMINATE`. No cross-frame transform is admissible in B8 V1
(`TemporalTransformRef` is reserved, without normative effect). B8 V1 stays intentionally narrower
(SAME_FRAME_ONLY) and is not reopened because this hold exists.

### Why HOLD

A temporal transformation is not timestamp conversion. An admissible transform needs contracts for
frame identity, direction, invertibility, composition, validity scope, precision / uncertainty,
calibration, provenance, verification, versioning, supersession, staleness, invalidation,
revocation, historical replay and proof / receipts. It must not be improvised inside B8 V1.

### Likely dependency family

| Layer | Role |
|---|---|
| Learning / education | may discover / propose temporal-relation candidates |
| Verification / truth | decides whether a candidate relation is admissible |
| Calibration | measures drift, error, stability, uncertainty |
| Identity + version + supersession | identifies a transform and its revisions |
| Point-in-Time | reconstructs which transform was admissible at a historical cutoff |
| Chronological durable memory | preserves transform history and provenance |
| World model / MMonde / TimeEnvelope | represents frames, situated time, trajectories, transforms |
| B8 | may later **consume** an already governed admissible relation — never invents the transform |

Future flow (conceptual): experience / observation → candidate temporal relation → learning /
education → calibration → typed verification → admissibility → versioned TemporalTransform →
chronological history → World / TimeEnvelope relation → a future B8 version may consume.

## 4. Authority laws (frozen)

```
LEARNING != VERIFICATION
VERIFICATION != ADMISSIBILITY
ADMISSIBILITY != KNOWLEDGE_PROMOTION
TRANSFORM_EXISTS != TRANSFORM_ADMISSIBLE
CONFIDENCE != TRANSFORM_AUTHORITY
MEMORY != TRUTH
RECORDED_FIRST != HAPPENED_FIRST
LEARNED_FIRST != EXISTED_FIRST
LATEST_LEARNED != LATEST_IN_WORLD
```

## 5. Chronological memory consequence

A TemporalTransform has its own history, e.g. Transform X v1 admissible under scope S → calibration
drift detected → STALE / INVALIDATED → X v2 verified → new admissibility scope. Point-in-Time must
later answer "which transform did Obsidia consider admissible at revision / time T" without
rewriting historical knowledge with the newest transform.

```
CURRENT_TRANSFORM != HISTORICAL_TRANSFORM
LATEST_TRANSFORM_MUST_NOT_REWRITE_HISTORY
```

## 6. Reopen conditions

B8-DT01 stays HOLD until enough of these exist:

```
TEMPORAL_WORLD_FRAMES_CANONICAL=YES
TEMPORAL_TRANSFORM_IDENTITY=DEFINED
TRANSFORM_VERSION_SUPERSESSION=DEFINED
POINT_IN_TIME=AVAILABLE
CHRONOLOGICAL_HISTORY=AVAILABLE
TYPED_TRANSFORM_VERIFICATION=AVAILABLE
CALIBRATION_UNCERTAINTY_CONTRACT=AVAILABLE
PROVENANCE=AVAILABLE
REVOCATION_INVALIDATION=AVAILABLE
MMONDE_TIMEENVELOPE_RELATION=DEFINED
```

Only then may B8-DT01 enter a READ_ONLY forensic; it is never implemented automatically when
dependencies appear.

## 7. Roadmap relation (dependency guidance, not scheduling)

Reconnect points (canonical roadmap `docs/semantic/SENS_PRE_FORGE_CANONICAL_ROADMAP.md` not
renumbered):

- B9 / CognitivePath — preserve discovery / path history, not transform authority.
- Long-lived identity / version / supersession — transform identity and history prerequisites.
- Point-in-Time — historical admissibility.
- Durable memory (B10) — chronological persistence.
- World model / MMonde — temporal frames / TimeEnvelope.
- Competence / calibration — measured transform quality.
- Learning / education — candidate discovery.

## 8. Status

```
TEMPORAL_ORDER_INVARIANT=FROZEN
B8_DT01_STATUS=HOLD
B8_DT01_BLOCKS_B8_V1=NO
B8_DT01_IMPLEMENTED=NO
CROSS_FRAME_B8_V1=FORBIDDEN
RECEIVED_ORDER_EQUALS_WORLD_ORDER=NO
RECORDED_ORDER_EQUALS_WORLD_ORDER=NO
SERIALIZATION_ORDER_EQUALS_WORLD_ORDER=NO
SERIALIZATION_ORDER_EQUALS_CAUSAL_ORDER=NO
```
