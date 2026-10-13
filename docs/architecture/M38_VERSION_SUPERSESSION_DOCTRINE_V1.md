# M38 Version / Supersession --- Doctrine V1

## 1. Status and authority

- Chapter: M38 --- Version / Supersession. Layer: cognition / pre-forge.
- Form: `M38_FORM=DOCTRINE_ONLY`. This document is the whole of M38 V1.
- Base: `COGNITIVE_FOUNDATION_V1=SEALED`, `FOUNDATION_REOPEN=NO`; M33, M34, M36, M37 CLOSED; M35 DEFERRED (evidence incomplete) and not a dependency.
- Basis: an independently certified M38 forensic followed by independent forensic certification (verdict: PASS_WITH_NONBLOCKING_FINDINGS), followed by explicit project-owner decisions (scope = version and supersession semantics for cognitive representation lineages; form = doctrine-only; V1 direct subject = KnowledgeClaim lineage; no runtime, no tests, no state machine).
- Normative hierarchy: `FOUNDATION_SEAL > CURRENT_CANONICAL_ARCHITECTURE > THIS_DOCTRINE > HISTORICAL_GENEALOGY`. Historical material never overrides this doctrine or anything above it.

M38 V1 does not implement versioning. Its mission is to define the semantic laws and architectural boundaries governing how versions and supersession relations are understood across the system, using KnowledgeClaim lineage as the only certified V1 instance.

## 2. Historical problem

Several distinct notions have clustered under "versioning" and "supersession" across the Obsidia history:

- epistemic state transitions (PROMOTED, SUPERSEDED, STALE, INVALIDATED) --- owned by B8;
- durable persistence of version history --- owned by B10;
- point-in-time reconstruction (what was valid at historical cutoff T) --- owned by M39;
- long-lived identity of persons and living entities --- closed by M37;
- technical file/code versioning (Git, semantic versioning) --- excluded;
- the core unresolved boundary: the semantic laws governing how one representation succeeds another in a cognitive lineage, independently of who persists it, who selects it, or when it was recorded.

M38 V1 owns exactly this last residual. Every other meaning is owned elsewhere or excluded (see boundary sections below).

The residual is not an unsolved problem in the same sense as M37. The B8 KnowledgeClaim lineage model demonstrates the core mechanics directly. M38 V1 canonicalizes the governing laws and marks the open structural questions that V1 cannot yet resolve.

## 3. Evidence levels

| Source | Evidence level | Use in M38 |
|---|---|---|
| B8 spec SS2 frozen laws, SS4.1 version model, SS8 states, SS9.2-SS9.4 T9, SS10 point-in-time contract, SS11 boundaries (STATUS=CLOSED) | DIRECT / CURRENTLY_IMPLEMENTED | primary V1 reference; governs KnowledgeClaim lineage only |
| `app/knowledge/b8/artifacts.py` --- KnowledgeClaim (frozen dataclass, lineage_id, claim_version, previous_claim_id) | DIRECT / CURRENTLY_IMPLEMENTED | confirms immutability and lineage structure |
| `app/knowledge/b8/core.py` --- T9 bundle, append-only records, supersedes/superseded_by links | DIRECT / CURRENTLY_IMPLEMENTED | confirms supersession mechanics |
| M37 doctrine SS22-SS23 (CLOSED) | CURRENT_CANONICAL | establishes M37/M38/M39 boundary explicitly |
| M33 ARM spec SS35 (CLOSED) | CURRENT_CANONICAL | "version/supersession" explicitly excluded from M33 |
| `TEMPORAL_ORDER_AND_TRANSFORM_HOLD_V1.md` --- "Identity + version + supersession --- identifies a transform and its revisions" | ARCHITECTURALLY_EXPECTED | TemporalTransform is a DEFERRED plausible consumer; not yet implemented |
| B9 CognitivePath SS3 --- "Corrections/supersession must produce new objects/relations rather than historical mutation" | CURRENT_CANONICAL | corroborates immutability law; local B9 rule, not M38 runtime |
| `CODEX_FORENSIC_AUDIT` line 193 --- "Version/supersession: SHARE; missing from this implementation" | INDIRECT / FUTURE | confirms version/supersession as a shareable primitive to be designed |
| `MEMORY_LANGUAGE_CONVERGENCE_V0.md` line 82 --- "Supersession / versions: absente (M0) --- A concevoir" | INDIRECT / FUTURE | confirms M38 not yet present in semantic/memory layers |
| `app/semantic/lattice/flow_validators.py` --- SUPERSEDED, SUPERSEDED_MEMORY in state frozensets | INDIRECT | not a wired M38 consumer; no M38 API called |
| M38 forensic (independently certified 2026-10-13) | INTERNAL_FORENSIC | confirms residual and boundaries; no primary source of its own |

Do not collapse evidence levels. Architectural and indirect evidence does not carry the authority of direct B8 evidence.

## 4. Canonical mission

M38 V1 defines the semantic laws and architectural boundaries governing version and supersession relations in Obsidia cognitive representations: how a representation in a lineage is succeeded by another, what the succeeded representation status means, and what properties are preserved.

M38 does not implement versioning, does not resolve the current version, does not select what is valid at a given time, does not persist version history, and does not authorize actions.

## 5. Canonical V1 subject

`M38_V1_DIRECT_SUBJECT=KNOWLEDGE_CLAIM_LINEAGE`

The KnowledgeClaim lineage model (B8) is the only directly certified V1 instance:

- `lineage_id` --- identifies the lineage to which a claim belongs (stable across revisions);
- `claim_version` --- semantic revision number within one lineage (monotone integer);
- `claim_id` --- content-hash identity of a specific claim instance (unique per version);
- `previous_claim_id` --- backward link to predecessor in the lineage;
- `record_version` --- epistemic-state counter for one claim_id (distinct from claim_version).

M38 V1 does not yet govern:

- TemporalTransforms --- `TEMPORAL_TRANSFORM_VERSIONING=DEFERRED_PLAUSIBLE_CONSUMER`;
- generic semantic representations --- `GENERIC_SEMANTIC_REPRESENTATION_VERSIONING=DEFERRED`;
- events --- `M38_EVENT_VERSIONING=DEFERRED`;
- typed relations --- `M38_RELATION_VERSIONING=DEFERRED`;
- Obsidia concepts --- `M38_CONCEPT_VERSIONING=GENEALOGY_ONLY`;
- a generic version-lineage primitive across all cognitive objects --- `GENERIC_VERSION_LINEAGE_PRIMITIVE=NOT_CLAIMED_IN_V1`.

Any extension beyond KnowledgeClaim lineage requires a new forensic and explicit owner decision.

## 6. Version model

A **version** is a semantically distinct instance within a lineage. In the certified V1 case (KnowledgeClaim):

- a semantic revision creates a new `KnowledgeClaim` with `claim_version = previous + 1`, the same `lineage_id`, a new `claim_id`, and `previous_claim_id` set;
- the new claim starts its own independent epistemic history;
- independent competing claims on the same slot are separate lineages --- they are never silent revisions of each other.

Freeze:

```
SEMANTIC_REVISION != IN_PLACE_MUTATION
CLAIM_VERSION != RECORD_VERSION
```

The claim_version counter counts semantic content changes. The record_version counter counts epistemic state transitions (T1-T12) for a fixed claim_id. They are wholly distinct dimensions.

Version objects are immutable once created. `KnowledgeClaim` is a frozen dataclass; historical records are append-only (`RECORDED_HISTORY_IS_APPEND_ONLY_IN_LOGICAL_ORDER` --- B8 SS5.3).

## 7. Lineage structure

A **lineage** is the set of all versions sharing a `lineage_id`.

The structural shape of a lineage is:

`M38_LINEAGE_SHAPE=UNDEFINED`

Reason (NB-1 from independent certification): B8 T9 guarantees that only one claim per slot can be PROMOTED at a time (T6 uniqueness constraint). This produces linear behaviour in the promoted state. However, B8 does not explicitly forbid two child versions sharing the same `previous_claim_id` (a structural fork within the lineage). The linear behavior of promoted history is a consequence of the epistemic state machine, not a declared structural invariant of the lineage data model itself.

Freeze as explicitly undefined:

```
M38_INTRA_LINEAGE_FORK_MODEL=UNDEFINED
M38_VERSION_MERGE_MODEL=UNDEFINED
```

B8 V1 does not define intra-lineage forks. B8 V1 does not define multi-parent version merges. Neither is forbidden nor supported in M38 V1. These are open structural questions that will require owner decisions if they become necessary.

## 8. Supersession

A **supersession** is an explicit, directional, functional replacement of an older version by a newer version within a lineage, where the history of the older version is preserved.

`SUPERSESSION=EXPLICIT_DIRECTIONAL_FUNCTIONAL_REPLACEMENT_WITH_HISTORY_PRESERVED`

In the certified V1 case (B8 T9):

- the new claim transitions from VERIFIED to PROMOTED;
- the predecessor claim transitions from PROMOTED to SUPERSEDED;
- this is an atomic bundle --- both transitions occur together or not at all;
- the new claim `supersedes` link points to the old claim `claim_id`;
- the old claim `superseded_by` link points to the new claim `claim_id`;
- T9 requires valid_time containment; partial overlap is rejected; no implicit claim split in V1.

`OLD_VERSION_HISTORY_PRESERVED=YES`

The superseded version is not deleted. Its record remains in the append-only history with its terminal SUPERSEDED state and all links intact.

Supersession direction is always old to new (the new supersedes the old). No reverse direction exists.

## 9. Supersession and cycle policy

For the B8 epistemic state machine:

`B8_SUPERSEDED_STATE_CYCLE_POLICY=TERMINAL_FOR_CLAIM_STATE`

SUPERSEDED is a terminal state for a given `claim_id`. No transition exits SUPERSEDED (B8 SS9.4: "SUPERSEDED -> any (never current again; a new claim_version is required)"). A state cycle through SUPERSEDED is therefore structurally impossible within B8.

For a generic M38 lineage supersession relation:

`M38_GENERIC_SUPERSESSION_CYCLE_POLICY=UNDEFINED`

Reason (NB-2 from independent certification): the B8 terminal-state rule applies to the epistemic state of a specific `claim_id`. It does not constitute a formally declared general law prohibiting cycles in M38 supersession lineages. Cycle prohibition at the M38 doctrine level is not derived from a direct source and is left undefined in V1. A future M38 revision may declare this explicitly if a consumer requires it.

## 10. Supersession relation retroactivity

Historical supersession links (`supersedes`, `superseded_by`) are written into immutable KnowledgeRecord instances in the append-only history. They cannot be retroactively corrected or removed.

`SUPERSESSION_RELATION_RETROACTIVE_MUTATION=NO`

A later T10 (INVALIDATION) applied to the new claim can alter the current epistemic state (the new claim becomes INVALIDATED and the slot has no current PROMOTED claim), but the historical supersession links remain unchanged. The supersession relation is not "undone" --- it is historically permanent.

`SUPERSESSION_RELATION_CORRECTION_MODEL=UNDEFINED`

Reason (NB-4 from independent certification): no model exists in V1 for correcting a supersession relation. This is an open question for future owner decision.

## 11. Preservation and immutability

Freeze:

```
DESTRUCTIVE_OVERWRITE=NO
IN_PLACE_SEMANTIC_REVISION=NO
OLD_VERSION_HISTORY_PRESERVED=YES
```

Historical version content is never modified in place. A semantic change produces a new version. The B8 append-only history (`RECORDED_HISTORY_IS_APPEND_ONLY_IN_LOGICAL_ORDER`) and frozen dataclass (`KnowledgeClaim`, `KnowledgeRecord`) provide the direct V1 evidence.

Durable storage of this history is B10. M38 V1 requires preservation semantically; B10 owns the persistence contract.

## 12. Version order

`M38_VERSION_ORDER=LOGICAL_REVISION_ORDER`

For KnowledgeClaim (V1 direct case): version order is determined by `claim_version` (semantic revision number within a lineage), `slot_revision` (canonical slot mutation order), and logical append order of records.

`WALL_CLOCK_IS_VERSION_AUTHORITY=NO`

Freeze:

```
SERIALIZATION_ORDER != WORLD_ORDER
RECEIVED_ORDER != WORLD_ORDER
RECORDED_FIRST != HAPPENED_FIRST
```

Wall-clock timestamps record when a fact was ingested, not its semantic order in the lineage. Version ordering is always logical, not temporal.

## 13. Valid time

Valid time and version order are distinct dimensions.

```
VALID_TIME != VERSION_ORDER
VALID_TIME != EPISTEMIC_STATE
```

A claim `valid_time` records when the claim content applies in the modelled world. Its `claim_version` records its position in the semantic revision sequence. Its epistemic state (PROMOTED, SUPERSEDED, etc.) records its current standing in the knowledge base. These three dimensions are independent.

M38 V1 does not implement M39 (Point-in-Time). Valid time navigation at a historical cutoff belongs to M39.

## 14. Partial supersession

In B8 V1, partial valid_time overlap is rejected by T9 (`containment_not_satisfied`). There is no implicit claim split.

This is recorded as B8-local evidence.

`M38_GENERIC_PARTIAL_SUPERSESSION_MODEL=UNDEFINED`

No generic M38 rule is derived from this B8-local constraint. Whether partial supersession semantics become possible for other subjects is an open owner decision.

## 15. Contradiction and supersession

`CONTRADICTION != SUPERSESSION`

In B8, CONTESTED (T7) and SUPERSEDED (T9) are distinct epistemic transitions. A contested claim --- one contradicted by another active claim on the same slot --- does not automatically become superseded. Contradiction represents an unresolved conflict. Supersession represents an explicit, gated functional replacement.

These transitions require different gate conditions and produce different epistemic states. Conflating them would produce silent, ungated semantic revision.

## 16. Retraction and invalidation

```
RETRACTION != VERSION
INVALIDATION != SUPERSESSION
```

B8 T10 (INVALIDATED) is the terminal epistemic state for an explicitly withdrawn claim. INVALIDATED does not advance `claim_version`. The claim identity is unchanged. The retraction is an epistemic act on the existing claim, not a new version in the lineage.

INVALIDATED records are appended to the history with reasons. The historical record is preserved.

## 17. Correction

A semantic correction may require a new `claim_version` when the corrected content changes the claim material (B8 SS6: fields that are "part of the claim" require a new claim_version).

`CORRECTION != AUTOMATIC_SUPERSESSION`

A correction that produces a new claim_version does not automatically supersede the previous version. T9 supersession additionally requires: overlapping `valid_time`, T9 gate preconditions, and valid_time containment. If these are not met (for example, if the valid_time windows do not overlap), the correction produces a new version that coexists historically without superseding the old one.

## 18. Provenance

In B8, verification provenance attaches to individual claim versions. A VerificationRecord binds to a specific `(claim_id, claim_version)` pair and does not carry over to another claim version.

`VERSION_PROVENANCE_IS_VERSION_SPECIFIC=YES`

M38 V1 does not create a new provenance schema. This is recorded as a B8-local semantic property.

## 19. Identity and concept distinctions

Preserve the following as distinct concepts:

- `claim_id` --- content-hash identity of a specific claim instance;
- `claim_version` --- semantic revision number within a lineage;
- `lineage_id` --- identifier of the lineage as a whole (stable across revisions);
- `record_version` --- epistemic state counter for one `claim_id`.

Freeze:

```
CONTENT_ID != VERSION_NUMBER
VERSION_NUMBER != LINEAGE_ID
CLAIM_VERSION != RECORD_VERSION
```

Do not conflate these. Do not introduce generic VersionId or LineageId runtime types in M38 V1.

## 20. Safety laws

The following laws are frozen for M38 V1. All are supported by direct or strong evidence in the certified sources:

```
VERSION != IDENTITY
NEW_VERSION != NEW_IDENTITY
SEMANTIC_REVISION != IN_PLACE_MUTATION
SUPERSEDED != DELETED
SUPERSEDED != FALSE
SUPERSEDED != INVALIDATED
CURRENT != ABSOLUTE_TRUTH
PROMOTION != VERSIONING
CLAIM_VERSION != RECORD_VERSION
CONTRADICTION != SUPERSESSION
CORRECTION != AUTOMATIC_SUPERSESSION
RETRACTION != VERSION
MEMORY != TRUTH
VERSIONING != AUTHORITY
SUPERSESSION_CLAIM != ESTABLISHED_TRUTH
```

Evidence notes:

- `SUPERSEDED != DELETED` --- B8 SS8: "(terminal, history kept)"; SS10: "No destructive overwrite." --- DIRECT.
- `SUPERSEDED != FALSE` and `SUPERSEDED != INVALIDATED` --- B8 SS2 frozen law: "STALE != INVALIDATED != SUPERSEDED != FALSE" --- DIRECT.
- `CURRENT != ABSOLUTE_TRUTH` --- B8 SS2 frozen law: "PROMOTED != ABSOLUTE_TRUTH" --- DIRECT.
- `MEMORY != TRUTH` --- B8 SS2 frozen law: "MEMORY != TRUTH" --- DIRECT.
- `CLAIM_VERSION != RECORD_VERSION` --- B8 SS2 frozen law --- DIRECT.
- `PROMOTION != VERSIONING` --- B8 SS4.1 distinct dimensions: claim_version vs record_version --- DIRECT.
- `CONTRADICTION != SUPERSESSION` --- B8 SS9.2 T7 vs T9 as distinct transitions --- DIRECT.
- `RETRACTION != VERSION` --- B8 SS9.2 T10 INVALIDATED does not advance claim_version --- DIRECT.
- `VERSIONING != AUTHORITY` and `SUPERSESSION_CLAIM != ESTABLISHED_TRUTH` --- strong inference from B8 T9 fallibility and KX108_ONLY=UNCHANGED --- SUPPORTED.
- `CORRECTION != AUTOMATIC_SUPERSESSION` --- structural inference from B8 T9 gate conditions --- SUPPORTED.
- `SEMANTIC_REVISION != IN_PLACE_MUTATION` --- B9 SS3, B8 frozen dataclass, append-only --- DIRECT.

## 21. Boundary: M37 (Long-lived Identity)

M37 is CLOSED. It must not be reopened.

M37 owns: continuity/identity of a person or living entity through transformation.

M38 owns: version/supersession of a semantic or cognitive representation lineage.

`M38_DOES_NOT_DECIDE_LONG_LIVED_IDENTITY=YES`

M38 does not need to resolve whether a subject is the same entity across transformations in order to operate on a versioned lineage. Slot identity (M32/SENS technical identifiers) is sufficient for lineage operations. M37 subject is outside M38 scope.

## 22. Boundary: B8 (Knowledge Promotion)

`B8_RELATION=EXISTING_PARTIAL_INSTANTIATION_FOR_KNOWLEDGE_CLAIMS`

B8 implements versioning and supersession for KnowledgeClaims. M38 is not a replacement for B8. M38 V1 defines the semantic doctrine that B8 partially instantiates.

B8 owns:
- the promotion state machine (T1-T12);
- gate transition execution;
- T9 atomic supersession bundle;
- T10 invalidation;
- append-only record history.

M38 V1 owns doctrine and semantic boundaries only. M38 does not re-execute, wrap, or replace any B8 gate.

`PROMOTION != VERSIONING`

Promotion is the epistemic act of elevating a claim to PROMOTED state. Versioning is the act of creating a semantic revision in a lineage. T9 combines both in an atomic bundle, but they remain distinct dimensions. A claim can be promoted without being a revision of a prior claim (T1 first-promotion), and a semantic revision exists as a new claim_version regardless of whether it is currently PROMOTED.

## 23. Boundary: M39 (Point-in-Time)

M39 owns: reconstruction of which information, version, or state was observable, admissible, or valid at a specific historical cutoff T.

`M38_IS_PREREQUISITE_FOR_M39=PARTIAL`

Reason (NB-3 from independent certification): B8 already provides limited as-of-revision behavior for KnowledgeClaims (`KNOWLEDGE_STATE_AS_OF_REVISION(R)` --- B8 SS10). A proto-M39 for KnowledgeClaims is operable using B8 alone. However, a generic M39 spanning future versioned cognitive objects (TemporalTransforms, semantic representations) requires M38 semantic boundaries to be formally defined for those objects first.

M38 does not implement Point-in-Time. M38 defines the version/supersession semantics that M39 navigates.

## 24. Boundary: B10 (Durable Memory)

B10 owns: durable persistence of epistemic history.

`M38_IS_PREREQUISITE_FOR_B10=PARTIAL`

B10 may store opaque B8 history records without requiring full M38 formalization. A complete semantic version-history persistence contract --- one that understands lineage semantics across objects --- would require M38 boundaries to be defined. That contract is not yet in scope.

Freeze:

```
M38_MEMORY_WRITE=NO
M38_DURABLE_STORAGE=NONE
```

M38 V1 has no storage interface. It defines what version/supersession means; B10 decides what and how to persist.

## 25. Boundary: SENS

M38 operates over semantic representations and their lineages. It does not redefine semantic content, does not modify SENS data structures, and does not add a SENS runtime interface.

`M38_SENS_RUNTIME_INTERFACE=NONE`

Generic integration of version/supersession as a shared SENS relation is DEFERRED. The `CODEX_FORENSIC_AUDIT` identifies version/supersession as a "SHARE" primitive that is "missing from this implementation" --- this remains future work.

## 26. Boundary: TemporalTransform

TemporalTransform is a plausible future consumer of M38 semantics. `TEMPORAL_ORDER_AND_TRANSFORM_HOLD_V1` references "Identity + version + supersession" as prerequisites for TemporalTransform. This is architecturally expected but not implemented.

```
TEMPORAL_TRANSFORM_VERSIONING=DEFERRED_PLAUSIBLE_CONSUMER
M38_TEMPORAL_TRANSFORM_RUNTIME_INTERFACE=NONE
```

No TemporalTransform runtime must be created here.

## 27. No runtime

`M38_FORM=DOCTRINE_ONLY`

Freeze:

```
M38_RUNTIME=NONE
M38_TESTS=NONE
M38_STATE=NONE
M38_EXECUTION=NONE
M38_RUNTIME_INPUT=NONE
M38_RUNTIME_OUTPUT=NONE
```

The following must not be created in M38 V1:

- VersionRecord --- not created;
- VersionRelation --- not created;
- SupersessionRelation --- not created;
- LineageGraph --- not created;
- CurrentVersionResolver --- not created;
- VersionStore --- not created;
- SupersessionEngine --- not created;
- tests/m38 --- not created.

## 28. No authority

Freeze:

```
M38_AUTHORITY=NONE
VERSIONING != AUTHORITY
COGNITION != AUTHORITY
KX108_ONLY=UNCHANGED
```

M38 cannot authorize any action. The version or supersession status of a claim does not constitute authorization. KX108_ONLY is unchanged.

## 29. Current version resolution

`M38_RESOLVES_CURRENT_VERSION=NO`

M38 does not select which version is currently preferred, in use, or admissible. Current-version behavior for KnowledgeClaims is governed by B8 (PROMOTED state via T9). Historical reconstruction belongs to M39. Capability selection may involve other consumers. M38 represents versioning semantics only.

## 30. Explicitly undefined and deferred items

The following are explicitly undefined in M38 V1 and require future owner decisions before any doctrine extension:

```
M38_LINEAGE_SHAPE=UNDEFINED
M38_INTRA_LINEAGE_FORK_MODEL=UNDEFINED
M38_VERSION_MERGE_MODEL=UNDEFINED
M38_GENERIC_SUPERSESSION_CYCLE_POLICY=UNDEFINED
M38_GENERIC_PARTIAL_SUPERSESSION_MODEL=UNDEFINED
SUPERSESSION_RELATION_CORRECTION_MODEL=UNDEFINED
```

The following subjects are deferred to future work:

- TemporalTransform versioning and supersession runtime (DEFERRED_PLAUSIBLE_CONSUMER);
- generic semantic representation versioning (DEFERRED);
- event versioning (DEFERRED);
- typed-relation versioning (DEFERRED);
- generic concept runtime versioning (DEFERRED);
- typed generic supersession relation primitive (DEFERRED);
- generic immutable VersionRecord model (DEFERRED);
- runtime lineage engine (DEFERRED);
- current-version resolver (DEFERRED).

## 31. Reopen conditions

M38 may reopen for a new revision or runtime spec if:

- an actual consumer requires a shared typed supersession relation that B8 internal T9 cannot provide;
- TemporalTransform becomes implemented and requires an explicit M38 versioning contract;
- B10 requires a generic durable version-history type beyond opaque B8 record storage;
- SENS requires a shared version/supersession relation;
- M39 requires functionality beyond B8 existing as-of-revision history;
- fork or merge semantics within a lineage become necessary;
- a generic lineage model is formally defined and requires M38 governance.

No silent doctrine-to-runtime expansion. Every reopen requires a new forensic and explicit owner decision.

## 32. Self-audit

```
M38_RUNTIME_SEMANTICS=0
M38_GENERIC_RUNTIME_TYPES_CREATED=0
M38_LINEAGE_SHAPE_INVENTED=0
M38_FORK_MODEL_INVENTED=0
M38_MERGE_MODEL_INVENTED=0
M38_GENERIC_CYCLE_POLICY_INVENTED=0
M38_PARTIAL_SUPERSESSION_MODEL_INVENTED=0
M38_CURRENT_VERSION_SELECTION_LEAKS=0
M38_M39_LEAKS=0
M38_B10_LEAKS=0
M38_PROMOTION_LEAKS=0
M38_AUTHORITY_LEAKS=0
```

M38 V1 defines semantic laws and boundaries. It does not implement, extend, or generalize any runtime component.

## 33. Closure model

`M38_CLOSURE_MODEL=DOCTRINE_ONLY_V1`

Lifecycle:

```
forensic
-> independent forensic certification
-> owner decisions
-> doctrine  <- current position
-> independent doctrine certification
-> CLOSED
```

```
M38_DOCTRINE_AUTHORED=YES
M38_DOCTRINE_INDEPENDENTLY_CERTIFIED=NO
M38_CLOSED=NO
```
