# M39 Point-in-Time --- Doctrine V1

## 1. Status and authority

- Chapter: M39 --- Point-in-Time. Layer: cognition / pre-forge.
- Form: `M39_FORM=DOCTRINE_ONLY`. This document is the whole of M39 V1.
- Base: `COGNITIVE_FOUNDATION_V1=SEALED`, `FOUNDATION_REOPEN=NO`; M33, M34, M36, M37, M38 CLOSED; M35 DEFERRED (evidence incomplete) and not a dependency.
- Basis: an independently certified M39 forensic (verdict: READY_FOR_DOCTRINE) followed by independent forensic certification (verdict: PASS_WITH_NONBLOCKING_FINDINGS, three nonblocking findings NF-1/NF-2/NF-3 integrated), followed by explicit project-owner decisions (scope = historical epistemic semantics for B8 KnowledgeClaims; form = doctrine-only; V1 direct subject = KnowledgeClaim epistemic state at logical cutoff; no runtime, no tests, no state machine).
- Normative hierarchy: `FOUNDATION_SEAL > CURRENT_CANONICAL_ARCHITECTURE > THIS_DOCTRINE > HISTORICAL_GENEALOGY`. Historical material never overrides this doctrine or anything above it.

M39 V1 does not implement point-in-time queries. Its mission is to define the semantic laws and architectural boundaries governing how the historical epistemic state of a B8 KnowledgeSlot is reconstructed at a logical cutoff, using only information that existed by that cutoff, without future-knowledge leakage.

## 2. Historical problem

Several distinct notions have clustered under "point-in-time" and "historical state" across the Obsidia architecture:

- what was true in the world at time T --- owned by SENS / World Model, not by M39;
- what the system believed / represented at logical revision R --- M39 V1 direct subject (epistemic only);
- durable storage of history for large-scale replay --- owned by B10;
- ordering of events across slots by a global clock --- explicitly forbidden (B8 SS5.3);
- which version was current at historical time T --- owned by M38 (versioning semantics);
- which transform was admissible at T --- TemporalTransform / deferred M39 consumer;
- the core residual: semantic laws governing what epistemic state a B8 slot represented at a specific logical cutoff R, derived solely from records committed by or before R.

M39 V1 owns exactly this last residual. Every other meaning is owned elsewhere, deferred, or excluded (see boundary sections below).

## 3. Evidence levels

| Source | Evidence level | Use in M39 |
|---|---|---|
| B8 spec SS4.1 (claim_version, record_version), SS4.2 (temporal fields), SS5.2 (append-only), SS5.3 (slot_revision, CROSS_SLOT_REVISION_NUMERIC_ORDERING=FORBIDDEN), SS10 (KNOWLEDGE_STATE_AS_OF_REVISION, LATEST_EPISTEMIC_STATE, CURRENT_KNOWLEDGE), SS10.1 (CURRENT_EPISTEMIC_VIEW, NOT_KNOWN, NO_ASSERTION, MIXED_SLOT_SNAPSHOT_ALLOWED=NO), SS11 (KX108 boundary) | DIRECT / SPEC-DEFINED | primary V1 reference for cutoff semantics, as-of query contract, unknown/absence categories |
| `app/knowledge/b8/core.py` --- `SlotSnapshot` (frozen dataclass, append-only `records` tuple), `evaluate_transition` (immutable snapshot replace), `current_records` (section 10 LATEST_EPISTEMIC_STATE, no as_of parameter), T9 bundle (atomic slot_revision+1) | DIRECT / CURRENTLY_IMPLEMENTED_DATA_MODEL | confirms immutable append-only record history; **no as_of query function in code** |
| `app/knowledge/b8/artifacts.py` --- `KnowledgeClaim` (frozen dataclass, lineage_id, claim_version, valid_time, source_refs, origin_refs), `VerificationRecord` (bound to claim_id + claim_version) | DIRECT / CURRENTLY_IMPLEMENTED_DATA_MODEL | confirms version-specific evidence binding and valid_time field separation |
| `TEMPORAL_ORDER_AND_TRANSFORM_HOLD_V1.md` (FROZEN 2026-10-07) sections 1, 5 | DIRECT / ARCHITECTURE_FREEZE | provides CURRENT_TRANSFORM != HISTORICAL_TRANSFORM, LATEST_TRANSFORM_MUST_NOT_REWRITE_HISTORY, names Point-in-Time explicitly as responsible for transform admissibility at T |
| M38 doctrine section 23 (CLOSED) | CURRENT_CANONICAL | establishes M38_IS_PREREQUISITE_FOR_M39=PARTIAL; M38 provides version/supersession semantics M39 navigates |
| M37 doctrine sections 22-23 (CLOSED) | CURRENT_CANONICAL | M37_DOES_NOT_OWN_POINT_IN_TIME=YES; explicit M37/M39 boundary |
| `SENS_PRE_FORGE_CANONICAL_ROADMAP.md` blocks 21-22 | CURRENT_CANONICAL | EVENT_TIME != REPORT_TIME != KNOWLEDGE_TIME; REPORTED != TRUE; OBSERVED != AUTHORIZED |
| M39 forensic (independently certified 2026-10-13) | INTERNAL_FORENSIC | confirms residual and owner decisions; no primary source of its own |

Do not collapse evidence levels. The B8 SS10 as-of query contract is **spec-defined but not code-implemented**. Architectural evidence for deferred consumers does not carry the authority of direct implemented evidence.

## 4. Canonical mission

M39 V1 defines the semantic laws and architectural boundaries governing the reconstruction of what epistemic state a B8 KnowledgeSlot represented at a specific logical historical cutoff R, using only records that existed at or before R.

M39 does not implement queries, does not reconstruct world state, does not select the currently valid claim, does not persist history, and does not authorize actions.

## 5. Canonical V1 subject and scope

```
M39_V1_DIRECT_SUBJECT=KNOWLEDGE_CLAIM_EPISTEMIC_STATE_AT_LOGICAL_CUTOFF
M39_V1_DIRECT_SCOPE=KNOWLEDGE_CLAIM_B8
M39_RECONSTRUCTS_WORLD_STATE=NO
```

M39 V1 asks:

> "What epistemic state did this B8 KnowledgeSlot represent at logical revision R?"

It does NOT ask:

> "What was absolute world truth at T?"

The B8 KnowledgeSlot (with its immutable append-only `SlotSnapshot.records` tuple) is the only directly certified V1 instance.

M39 V1 does not yet govern:

- TemporalTransform historical admissibility --- `TEMPORAL_TRANSFORM_POINT_IN_TIME=DEFERRED_PLAUSIBLE_CONSUMER`;
- SENS historical event-state queries --- `SENS_POINT_IN_TIME=DEFERRED`;
- generic cognitive objects --- `GENERIC_COGNITIVE_OBJECT_POINT_IN_TIME=DEFERRED` (requires future forensic + owner decision);
- World Model historical state --- `WORLD_MODEL_HISTORICAL_STATE=DEFERRED`;
- hindsight query (AS_NOW_KNOWN_ABOUT_HISTORICAL_TIME) --- `AS_NOW_KNOWN_ABOUT_HISTORICAL_TIME=DEFERRED`.

Any extension beyond B8 KnowledgeClaims requires a new forensic and explicit owner decision.

## 6. valid_time is a separate dimension

`valid_time` means: when a claim applies in the modeled world/domain.

Freeze:

```
VALID_TIME != KNOWLEDGE_TIME
VALID_TIME != SLOT_REVISION
VALID_TIME != EPISTEMIC_STATE
VALID_AT_T != KNOWN_AT_T
```

M39 may use `valid_time` as a query or filter dimension. B8 `CURRENT_KNOWLEDGE` already combines `valid_time` containment with PROMOTED epistemic state and `as_of_slot_revision` cutoff (see section 19 below).

Using `valid_time` as a filter dimension does NOT convert M39 into a World Model state reconstruction layer. The primary epistemic cutoff remains `as_of_slot_revision` (section 7 below), not world time.

## 7. Primary cutoff and cutoff scope

```
M39_V1_PRIMARY_CUTOFF=AS_OF_SLOT_REVISION
M39_CUTOFF_SCOPE=PER_KNOWLEDGE_SLOT
```

`slot_revision` is (B8 SS5.3): a canonical logical mutation serialization revision for one `KnowledgeSlot`. It is the authoritative ordering dimension within that slot.

`slot_revision` is NOT:

- world time or event time;
- universal / global time;
- a global revision ordering across slots;
- a causal clock across disjoint slots.

`slot_revision` is strictly local to one slot. See section 22 (global snapshot) for the cross-slot prohibition.

## 8. Timestamp cutoff

```
TIMESTAMP_CUTOFF=DERIVED_CONVENIENCE_WITHIN_DECLARED_CLOCK_DOMAIN
RECORDED_AT_CANONICAL_ORDER_AUTHORITY=NO
WALL_CLOCK_IS_POINT_IN_TIME_AUTHORITY=NO
```

Source (B8 SS5.3): "Canonical B8 history order is never the numerical order of `recorded_at`." A `recorded_at` wall-clock value must not override logical `slot_revision` history order. A timestamp-based cutoff is admissible only as a derived convenience within one explicitly declared `clock_domain`, and only where `slot_revision` is unavailable or not applicable.

## 9. No universal clock

Preserve from TEMPORAL_ORDER_AND_TRANSFORM_HOLD_V1 (FROZEN):

```
ONE_SYSTEM != ONE_CLOCK
SERIALIZATION_ORDER != WORLD_ORDER
RECEIVED_ORDER != WORLD_ORDER
RECORDED_FIRST != HAPPENED_FIRST
SINGLE_TIMESTAMP_POINT_IN_TIME_MODEL=NO
```

M39 inherits these frozen invariants. No universal clock, no global `slot_revision`, no single timestamp model.

## 10. Future-knowledge prohibition

```
FUTURE_KNOWLEDGE_MUST_NOT_LEAK_INTO_PAST_VIEW=YES
```

Any claim, record, gap record, or evidence artifact created at `slot_revision > R` must not appear in an `AS_KNOWN_AT_R` view. The B8 `SlotSnapshot.records` append-only tuple and the spec-defined `LATEST_EPISTEMIC_STATE(claim_id, as_of_slot_revision)` filter (`slot_revision <= as_of_slot_revision`) provide the structural guarantee.

## 11. Backdated valid_time does not backdate knowledge

```
BACKDATED_VALID_TIME_DOES_NOT_BACKDATE_KNOWLEDGE=YES
```

Example: a claim created at `slot_revision = R10` with `valid_time` referring to a world period before `slot_revision = R5`. At `AS_KNOWN_AT_R5`, this claim does not exist in the historical epistemic view --- it had not yet been recorded. World applicability time does not rewrite knowledge history.

## 12. Future supersession

```
FUTURE_SUPERSESSION_MUST_NOT_REWRITE_PAST=YES
```

If claim `v1` was PROMOTED at `R5` and the T9 supersession bundle (v1 -> SUPERSEDED, v2 -> PROMOTED) occurred at `R8`, then `AS_KNOWN_AT_R6` must reconstruct `v1` as PROMOTED. The `R8` bundle is invisible at cutoff `R6`.

## 13. Future invalidation

```
FUTURE_INVALIDATION_MUST_NOT_REWRITE_PAST=YES
```

A T10 INVALIDATION applied at `slot_revision > R` does not retroactively alter the epistemic state visible at cutoff `R`. The claim remains in its last state known at or before `R`.

## 14. Future verification and future promotion

```
FUTURE_VERIFICATION_MUST_NOT_REWRITE_PAST=YES
FUTURE_PROMOTION_MUST_NOT_REWRITE_PAST=YES
```

A `VerificationRecord` produced after cutoff `R` does not exist in the `AS_KNOWN_AT_R` view. A T6 PROMOTION at `slot_revision > R` is absent; the claim remains in its pre-promotion state at cutoff `R`.

## 15. Query mode

V1 freeze:

```
M39_V1_QUERY_MODE=AS_KNOWN_AT_REVISION
```

Meaning: "What epistemic state did the system represent at revision R?" --- using only what was recorded by or before R.

Explicitly deferred:

```
AS_NOW_KNOWN_ABOUT_HISTORICAL_TIME=DEFERRED
```

Hindsight semantics ("what do we know NOW about what was happening THEN") are architecturally distinct and require a separate owner decision. M39 V1 does not define or implement them.

## 16. Historical view is not current view

```
AS_OF_STATE != CURRENT_STATE
```

The current state of a slot (all records to date) must not be silently projected backward to represent a historical cutoff view. `AS_KNOWN_AT_R` and `CURRENT_STATE` are distinct query results whenever `R` is less than the current `slot_revision`.

## 17. Historical view is not truth

```
POINT_IN_TIME_VIEW != ABSOLUTE_TRUTH
PROMOTED != ABSOLUTE_TRUTH
MEMORY != TRUTH
```

What the system believed or represented at revision R is a record of its epistemic state, not an assertion of absolute world truth. This is a direct law of the B8 epistemic model (B8 SS2 frozen laws, referenced in M38 section 20).

## 18. Representation, not selection

```
M39_SELECTS_AUTHORITATIVE_VERSION=NO
M39_SELECTS_TRUTH=NO
```

M39 represents historical epistemic categories. It does not choose the correct claim, the authoritative claim, the true world state, or the action to execute. B8 `CURRENT_EPISTEMIC_VIEW` returns `promoted_coverage`, `unknown_coverage`, `contested_refs`, `stale_refs`, `gap_refs`, and `temporal_indeterminate_refs` --- a set of categorical view components, not a single authoritative selection.

## 19. World and epistemic dimensions in B8

B8 `CURRENT_KNOWLEDGE(slot, query_time, as_of_slot_revision)` combines three dimensions simultaneously (B8 SS10):

1. `valid_time` containment (world applicability);
2. `LATEST_EPISTEMIC_STATE(claim_id, as_of_slot_revision) = PROMOTED` (epistemic state);
3. `as_of_slot_revision` cutoff (historical position).

This B8 combination is recorded as direct evidence that the world-query and epistemic-query dimensions coexist in the B8 data model.

```
M39_WORLD_QUERY_RUNTIME=NONE
```

M39 V1 does NOT conclude from this that it owns world-state reconstruction. The presence of `valid_time` as a filter dimension in B8 does not make M39 a World Model history engine. `M39_RECONSTRUCTS_WORLD_STATE=NO` is unchanged.

## 20. Unknown and absence semantics

Critical NF-2 correction (integrated from independent forensic certification).

```
FALSE_UNKNOWN_NOASSERTION_RELATION=DISTINCT_CATEGORIES_NOT_ORDERED
CLOSED_WORLD_ASSUMPTION=NO
```

There is NO ordering relation `FALSE < UNKNOWN < NO_ASSERTION`. These are three distinct semantic categories (B8 SS10.1):

- `NO_ASSERTION` --- no applicable knowledge and no explicit gap lineage in the view; a view result, not an epistemic state stored in a record;
- `KNOWN_UNKNOWN` --- an explicit EpistemicGap / known lack of knowledge is present in the record history;
- `PROMOTED` --- a knowledge claim is in the PROMOTED state at the cutoff.

Freeze (B8 SS10.1):

```
NOT_KNOWN != KNOWN_UNKNOWN
NO_ASSERTION != KNOWN_UNKNOWN
ABSENCE != FALSE
ABSENCE != KNOWN_UNKNOWN
CURRENT_UNKNOWN_COVERAGE != UNIVERSE_MINUS_CURRENT_KNOWN
```

No closed-world assumption: the absence of a promoted claim does not imply falsehood. An absence without gap lineage is `NO_ASSERTION`. An explicit gap is `KNOWN_UNKNOWN`. These are neither ordered nor interchangeable.

## 21. EpistemicGap

`EpistemicGap` (B8 SS4.2) represents a known lack of evidence or knowledge --- a "known unknown." It does NOT represent proven falsehood or negation of a proposition.

```
EPISTEMIC_GAP != FALSE
KNOWN_UNKNOWN != NEGATIVE_FACT
```

True propositional-negation semantics ("the system knows X is false") are outside M39 V1. `EpistemicGap` encodes "the system knows that it lacks evidence on this point," nothing stronger.

## 22. Global snapshot --- NF-1

Critical NF-1 correction (integrated from independent forensic certification).

```
GLOBAL_POINT_IN_TIME_SNAPSHOT_SUPPORTED=UNDEFINED
GLOBAL_REVISION=NONE
GLOBAL_CUTOFF=NONE
CONSISTENT_CUT_MODEL=NONE
CROSS_SLOT_REVISION_NUMERIC_ORDERING=FORBIDDEN
```

Source (B8 SS5.3): "It is local to one slot: revisions of different slots are never compared and no global latest revision exists." `CROSS_SLOT_REVISION_NUMERIC_ORDERING=FORBIDDEN`.

Per-slot historical reconstruction (`KNOWLEDGE_STATE_AS_OF_REVISION(R)` for one slot) exists as a spec contract (B8 SS10). That does NOT imply, and does NOT partially support, a global coherent multi-slot snapshot. Cross-slot revision comparison is not merely undefined --- it is FORBIDDEN. `GLOBAL_POINT_IN_TIME_SNAPSHOT_SUPPORTED=PARTIAL` would be incorrect; the correct value is `UNDEFINED`.

## 23. Cross-slot ordering

```
M39_CROSS_SLOT_ORDER_MODEL=UNDEFINED
SERIALIZATION_IMPLIES_CAUSATION=NO
```

Source (B8 SS5.3): "SERIALIZATION_IMPLIES_CAUSATION=NO --- two events committed in sequence may be causally incomparable." Only explicitly typed causal relations establish inter-object ordering.

M39 V1 does NOT invent:

- Lamport clocks;
- vector clocks;
- global transaction revisions;
- global event sequences;
- consistent cuts.

## 24. Mixed cutoffs within one slot

B8-local law (B8 SS10.1):

```
MIXED_SLOT_SNAPSHOT_ALLOWED=NO
```

Meaning: one composed epistemic view for one slot must derive from a single coherent `as_of_slot_revision`. All components of `CURRENT_EPISTEMIC_VIEW` for one slot share the same cutoff.

This rule is local to one slot. It does not constitute a multi-slot global snapshot rule and must not be reinterpreted as one.

## 25. B8 boundary

B8 owns:

- epistemic state transitions T1-T12;
- `KnowledgeRecord` creation and field structure;
- `slot_revision` mutation (append-only);
- `KnowledgeClaim` runtime representation.

M39 owns:

- semantic laws governing historical as-of reconstruction from B8 records.

```
M39_REEXECUTES_B8_TRANSITIONS=NO
```

M39 does not re-execute T1-T12 to derive historical state. It reads the existing immutable record history.

## 26. B8 as-of capability --- NF-3

Critical NF-3 integration:

```
B8_POINT_IN_TIME_CAPABILITY=SPEC_DEFINED_PARTIAL_PROTOTYPE
AS_OF_QUERY_FUNCTION_IMPLEMENTED=NO
```

The B8 spec (SS10) defines the contractual interface:

- `LATEST_EPISTEMIC_STATE(claim_id, as_of_slot_revision)` --- state of the last record (highest `record_version`) among records committed at `slot_revision <= as_of_slot_revision`;
- `KNOWLEDGE_STATE_AS_OF_REVISION(R)` --- for each claim of the slot, `LATEST_EPISTEMIC_STATE(claim_id, R)`;
- `CURRENT_KNOWLEDGE(slot, query_time, as_of_slot_revision)`;
- `CURRENT_EPISTEMIC_VIEW(slot_id, query_time, as_of_slot_revision)`.

These contracts are spec-level only. In `app/knowledge/b8/core.py`:

- `current_records()` (section 10) returns the max `record_version` per `claim_id` **without** an `as_of` parameter;
- `KnowledgeRecord` does not store a `slot_revision` field;
- no function named `knowledge_state_as_of_revision` or equivalent exists in the codebase.

The data model (append-only `SlotSnapshot.records` tuple) structurally supports future as-of reconstruction. The query function does not yet exist. M39 V1 does not implement it.

## 27. Reconstruction method

```
M39_RECONSTRUCTION_METHOD=REPLAY_IMMUTABLE_RECORD_HISTORY
```

Historical epistemic state is derived by selecting, from the immutable append-only record history, all records committed at `slot_revision <= R`, then applying `LATEST_EPISTEMIC_STATE` per claim.

This is a read operation over existing immutable records. It does NOT:

- recompute history by re-executing current rules on past inputs;
- filter current state backward to infer past state;
- mutate historical records.

## 28. Historical rules must not rewrite state

Preserve from TEMPORAL_ORDER_AND_TRANSFORM_HOLD_V1 (FROZEN, section 5):

```
CURRENT_TRANSFORM != HISTORICAL_TRANSFORM
LATEST_TRANSFORM_MUST_NOT_REWRITE_HISTORY
M39_CURRENT_RULES_MUST_NOT_REWRITE_HISTORICAL_STATE=YES
```

A later rule or transform version must not retroactively alter what the historical record shows for cutoff R. This law applies at the level of semantic architecture; it does not constitute an implementation algorithm.

## 29. TemporalTransform boundary

Source (TEMPORAL_ORDER_AND_TRANSFORM_HOLD_V1, section 5): "Point-in-Time must later answer which transform Obsidia considered admissible at revision / time T without rewriting historical knowledge with the newest transform."

```
TEMPORAL_TRANSFORM_POINT_IN_TIME=DEFERRED_PLAUSIBLE_CONSUMER
M39_TEMPORAL_TRANSFORM_RUNTIME_INTERFACE=NONE
```

M39 V1 records this as an architecturally expected future consumer. No runtime interface, no transform history implementation in V1.

## 30. M38 boundary

M38 remains CLOSED. Its subject is version/supersession semantics; the M39 subject domain is historical as-of reconstruction.

```
POINT_IN_TIME != VERSIONING
M38_IS_PREREQUISITE_FOR_M39=PARTIAL
```

M38 defines the version and supersession semantics that M39 navigates when reconstructing what version was PROMOTED at a historical cutoff. B8 already provides limited as-of behavior for KnowledgeClaims. A generic M39 spanning future versioned cognitive objects requires M38 semantic boundaries to be formally defined for those objects first.

## 31. B10 boundary

```
M39_IS_PREREQUISITE_FOR_B10=PARTIAL
B10_IS_PREREQUISITE_FOR_M39=PARTIAL
M39_MEMORY_WRITE=NO
M39_DURABLE_STORAGE=NONE
```

M39 defines historical-query semantics. B10 owns durable persistence of history. M39 V1 doctrine exists without B10. Large-scale persistent M39 runtime may later depend on B10 for the persistence and efficient query of historical records. B10 may later depend on M39 semantics to know what must be stored to support historical views.

## 32. SENS boundary

SENS owns: `OccurrenceClaim`, `EventCandidate`, `EventRef`, occurrence semantics, and event extraction logic.

```
M39_SENS_RUNTIME_INTERFACE=NONE
```

M39 does not redefine SENS structures. SENS historical queries (what events were known at logical cutoff R) remain deferred.

Source (SENS canonical roadmap, block 22): `EVENT_TIME != REPORT_TIME; REPORT_TIME != KNOWLEDGE_TIME` --- this three-way distinction is a precondition for SENS historical queries, confirming the conceptual gap that M39 must later bridge with SENS.

## 33. M33 / ARM boundary

```
ARM_RECONSTRUCTION != POINT_IN_TIME_RECONSTRUCTION
```

M33 ARM reconstructs candidate structure (entities, relations) from fragmentary evidence. M39 reconstructs historical epistemic state from the immutable record history of a known slot. Different inputs, different methods, different outputs.

## 34. M37 boundary

M37 remains CLOSED.

```
M39_DOES_NOT_OWN_LONG_LIVED_IDENTITY=YES
```

Source (M37 sections 22-23, CLOSED): "M37 does not reconstruct what was observed, known, believed or valid at historical time T." `M37_DOES_NOT_OWN_POINT_IN_TIME=YES`. Boundary is explicit in M37.

## 35. World Model boundary

```
M39_IS_PREREQUISITE_FOR_WORLD_MODEL=PARTIAL
GENERIC_WORLD_MODEL_HISTORICAL_QUERY=DEFERRED
```

M39 V1 does not reconstruct absolute world state. World Model may later consume Point-in-Time epistemic semantics when building historical world views. The precise boundary is deferred until World Model is specified.

## 36. Provenance

```
POINT_IN_TIME_PROVENANCE_USES_EXISTING_B8_ARTIFACTS=YES
```

B8 artifacts already preserve: `KnowledgeClaim.source_refs`, `KnowledgeClaim.origin_refs`, and version-specific `VerificationRecord` bindings (bound to `claim_id` + `claim_version`). A `VerificationRecord` created after cutoff `R` is absent from the `AS_KNOWN_AT_R` view. No new provenance schema is introduced in M39 V1.

## 37. Evidence availability

```
EVIDENCE_AVAILABLE_NOW != EVIDENCE_AVAILABLE_AT_CUTOFF
```

Evidence artifacts (verifications, attestations, referenced records) created after cutoff `R` are absent from the `AS_KNOWN_AT_R` view by the same mechanism as claims and records. This is a direct consequence of the immutable append-only record history and the `slot_revision <= R` filter.

## 38. Replay boundary

```
M39_REPLAY_KIND=EPISTEMIC_RECORD_HISTORY_REPLAY
M39_EXECUTION_REPLAY=NO
M39_RECEIPT_EXECUTION_REPLAY=NO
```

M39 replay is: reading the existing immutable record history (KnowledgeRecord, EpistemicGap records) up to cutoff R. It is NOT re-execution of B8 transitions T1-T12, not replay of `TransitionReceipt` sequences, and not action or execution replay. Execution/action replay belongs elsewhere.

## 39. Authority

```
M39_AUTHORITY=NONE
POINT_IN_TIME != AUTHORITY
HISTORICAL_PROMOTED_STATE != ACTION_AUTHORIZATION
COGNITION != AUTHORITY
KX108_ONLY=UNCHANGED
```

Reconstructing what was PROMOTED at a historical cutoff does not authorize any current or future action. The separation of epistemic state from authorization authority (B8 SS11: KX108 only) is unchanged and extends to historical views.

## 40. No runtime

```
M39_FORM=DOCTRINE_ONLY
M39_RUNTIME=NONE
M39_TESTS=NONE
M39_STATE=NONE
M39_EXECUTION=NONE
M39_RUNTIME_INPUT=NONE
M39_RUNTIME_OUTPUT=NONE
```

M39 V1 defines semantic laws only. Do NOT create:

- `PointInTimeQuery`;
- `HistoricalKnowledgeView`;
- `AsOfResolver`;
- `GlobalSnapshot`;
- `GlobalRevision`;
- `HistoryStore`.

## 41. Direct vs. future consumers

**DIRECT V1 (B8 data model, currently implemented):**

- `KnowledgeClaim` (frozen dataclass, `lineage_id`, `claim_version`, `valid_time`, immutable);
- `KnowledgeRecord` (frozen dataclass, append-only in `SlotSnapshot.records` tuple);
- `SlotSnapshot` (immutable, frozen at each `slot_revision`);
- `claim_version`, `record_version`, `slot_revision`, `valid_time`, `recorded_at` --- all separate fields.

**SPEC-DEFINED / NOT CODE-IMPLEMENTED (B8 SS10 query contract):**

- `LATEST_EPISTEMIC_STATE(claim_id, as_of_slot_revision)`;
- `KNOWLEDGE_STATE_AS_OF_REVISION(R)`;
- `CURRENT_KNOWLEDGE(slot, query_time, as_of_slot_revision)`;
- `CURRENT_EPISTEMIC_VIEW(slot_id, query_time, as_of_slot_revision)`.

**ARCHITECTURALLY EXPECTED / DEFERRED:**

- TemporalTransform historical admissibility;
- SENS historical event-state queries;
- World Model historical state queries.

**EXCLUDED:**

- global snapshot;
- global revision;
- execution replay;
- durable memory (B10);
- action authority.

## 42. Safety laws

```
FUTURE_KNOWLEDGE_MUST_NOT_LEAK_INTO_PAST_VIEW
BACKDATED_VALID_TIME_DOES_NOT_BACKDATE_KNOWLEDGE
FUTURE_SUPERSESSION_MUST_NOT_REWRITE_PAST
FUTURE_INVALIDATION_MUST_NOT_REWRITE_PAST
FUTURE_VERIFICATION_MUST_NOT_REWRITE_PAST
FUTURE_PROMOTION_MUST_NOT_REWRITE_PAST
AS_OF_STATE != CURRENT_STATE
VALID_AT_T != KNOWN_AT_T
RECORDED_BY_T != OCCURRED_BY_T
OBSERVED != TRUE
NO_ASSERTION != KNOWN_UNKNOWN
UNKNOWN != FALSE
POINT_IN_TIME_VIEW != ABSOLUTE_TRUTH
POINT_IN_TIME != MEMORY
POINT_IN_TIME != VERSIONING
POINT_IN_TIME != AUTHORITY
LATEST_TRANSFORM_MUST_NOT_REWRITE_HISTORY
```

Sources: B8 SS2 frozen laws, B8 SS4.2, B8 SS5.3, B8 SS10, B8 SS10.1, B8 SS11, TEMPORAL_ORDER_AND_TRANSFORM_HOLD_V1 sections 1 and 5, SENS canonical roadmap blocks 21-22, M37 doctrine sections 22-23, M38 doctrine sections 20 and 23.

## 43. Explicit deferrals

The following are explicitly excluded from M39 V1 and require a new owner decision and/or forensic before inclusion:

- `AS_NOW_KNOWN_ABOUT_HISTORICAL_TIME` (hindsight query mode);
- global revision;
- global cutoff;
- global snapshot;
- consistent cut;
- cross-slot ordering model;
- generic cognitive-object Point-in-Time (beyond B8 KnowledgeClaims);
- SENS Point-in-Time runtime;
- TemporalTransform Point-in-Time runtime;
- World Model historical query;
- typed `PointInTimeQuery`;
- typed `HistoricalKnowledgeView`;
- runtime `AsOfResolver`;
- durable `HistoryStore`.

## 44. Reopen conditions

M39 may reopen when:

- a concrete runtime consumer requires as-of queries (triggers B8 as-of code implementation);
- the B8 SS10 as-of contract is implemented as a runtime API (`AS_OF_QUERY_FUNCTION_IMPLEMENTED=NO` -> YES);
- TemporalTransform requires historical admissibility runtime;
- SENS requires historical event-state queries;
- World Model requires historical state queries;
- B10 provides durable history requiring query integration;
- cross-slot coherent snapshot semantics are formally defined;
- hindsight query semantics (`AS_NOW_KNOWN_ABOUT_HISTORICAL_TIME`) become required.

No silent doctrine -> runtime expansion. No silent per-slot -> global expansion.

## 45. Closure model

```
M39_CLOSURE_MODEL=DOCTRINE_ONLY_V1
```

Lifecycle:

```
forensic
-> independent forensic certification (PASS_WITH_NONBLOCKING_FINDINGS)
-> owner decisions
-> doctrine (this document)
-> independent doctrine certification
-> CLOSED
```

No RED/GREEN/runtime phase in V1.

## 46. Self-audit

```
M39_RUNTIME_SEMANTICS=0
M39_AS_OF_RUNTIME_CREATED=0
M39_GLOBAL_REVISION_CREATED=0
M39_GLOBAL_SNAPSHOT_CREATED=0
M39_CROSS_SLOT_ORDER_CREATED=0
M39_WORLD_STATE_SCOPE_LEAKS=0
M39_HINDSIGHT_MODE_CREATED=0
M39_FALSE_UNKNOWN_ORDERING_CREATED=0
M39_B10_LEAKS=0
M39_SENS_LEAKS=0
M39_EXECUTION_REPLAY_LEAKS=0
M39_AUTHORITY_LEAKS=0
```
