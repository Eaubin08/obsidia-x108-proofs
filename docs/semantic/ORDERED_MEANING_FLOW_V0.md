# OrderedMeaningFlow V0

## Status

This document defines a V0 contract only. It does not implement a runtime, a new engine, a Native Memory integration, or a KX108 authority path.

The goal is to represent ordered meaning flows around one cognitive object while keeping order families separate. A temporal path may be transitive as temporal order. It must not become causal proof, epistemic verification, memory consolidation, or governance authorization by implication.

## Non-negotiable Separations

- temporal order is not causal order
- observation is not knowledge
- knowledge is not memory
- memory is not truth
- confidence is not evidence
- evidence is not authority
- request is not permission
- permission is not execution
- semantic similarity is not a proven relation

## A. Cognitive Object Identity

A cognitive object is the stable referent used by multiple projections. In the current language lattice, an existing `PredicateUnit.id` can act as the object reference for V0. Future cognitive objects may use a richer identifier, but the flow must reference the object rather than copy the semantic payload.

Minimum identity contract:

- `object_id`: stable local identifier, for example `u1` or a future content-addressed id.
- `object_type`: current values may include `PredicateUnit`; future values may include memory node, observation node, receipt, or external claim.
- `source_frame`: optional utterance or trace id that introduced the object.
- `predicate_ref`: optional reference to the semantic predicate when the object is language-derived.
- `span_ref`: optional source span. This supports audit and replay without duplicating the object.

The same object may participate in semantic, agentive, temporal, causal, epistemic, memory, and governance flows. The flow stores relation and state metadata; it does not own or rewrite the object.

## B. Flow Family Record

A flow family record must contain at least:

| Field | Meaning |
| --- | --- |
| `family` | One of the initial V0 families: `temporal_order`, `causal_claim`, `epistemic_state`, `memory_lifecycle`, `governance_state`. |
| `source_object` | Cognitive object reference that starts the relation or carries the state. |
| `target_object` OR `state` | Relation target for edge-like flows, or state value for state-like flows. One may be absent depending on family. |
| `relation_type` | Family-local relation label, never globally overloaded. |
| `direction` | `source_to_target`, `target_to_source`, `bidirectional`, or `state_on_source`. |
| `scope` | Scope of validity: utterance, clause, session, trace, memory candidate, governance transaction, or receipt. |
| `provenance` | Evidence of where the flow came from: parser, user utterance, log, observation, report, receipt, or human decision. |
| `confidence` | Calibrated or uncalibrated confidence value with source. Confidence is not evidence and does not imply authority. |
| `status` | Draft, asserted, disputed, validated, superseded, rejected, or unknown. |
| `metadata` | Extensible family-specific fields; must remain auditable and serializable. |

No Python API is frozen by this document. The shape is a contract for tests and later implementation.

## C. Initial Families

### TEMPORAL_ORDER

Temporal order captures time coordinates and temporal relations only.

Time coordinate types:

- `UTTERANCE_TIME`: time at which the utterance or trace is produced.
- `EVENT_TIME`: time at which the represented event occurs.
- `OBSERVATION_TIME`: time at which something is observed.
- `KNOWLEDGE_ACQUISITION_TIME`: time at which an agent learns or receives knowledge.
- `MEMORY_STORAGE_TIME`: time at which a memory trace is stored.
- `VALID_FROM`: start of a validity interval.
- `VALID_TO`: end of a validity interval.

Temporal relation types:

- `BEFORE`
- `AFTER`
- `SIMULTANEOUS`
- `OVERLAPS`
- `STARTS`
- `ENDS`

Temporal coordinates and temporal relations are not causal relations. `A BEFORE B` and `B BEFORE C` may support `A BEFORE C` inside the temporal family, but it must not imply `A CAUSES C`.

### CAUSAL_CLAIM

Causal flows represent claimed, reported, inferred, observed, physical, or validated causal structure. V0 must distinguish at least:

- `LINGUISTIC_CAUSAL_CLAIM`: the speaker states a causal relation, for example `A parce que B`.
- `REPORTED_CAUSAL_CLAIM`: a reported speaker states a causal relation.
- `INFERRED_CAUSAL_RELATION`: a system or analyst infers causality from a model or pattern.
- `OBSERVED_DEPENDENCY`: repeated observation of dependence without physical proof.
- `PHYSICAL_CAUSAL_EVIDENCE`: instrumented or physical evidence supporting causality.
- `VALIDATED_CAUSAL_PROOF`: validated causal proof under an accepted authority process.

Causal relation types may include:

- `CAUSES`
- `ENABLES`
- `PREVENTS`
- `CONDITIONS`
- `CONTRIBUTES_TO`

Initial rule: `A parce que B` creates only `LINGUISTIC_CAUSAL_CLAIM`, not `VALIDATED_CAUSAL_PROOF`. A temporal sequence such as `A apres B` does not create `CAUSES`.

### EPISTEMIC_STATE

Epistemic flows describe the state of knowledge or belief about an object. The state set must include:

- `UNKNOWN`
- `UNCERTAIN`
- `HYPOTHESIS`
- `CLAIMED`
- `REPORTED`
- `BELIEVED`
- `OBSERVED`
- `SUPPORTED`
- `VERIFIED`
- `CONTRADICTED`
- `SUPERSEDED`

This is not a single strict ladder. `REPORTED`, `BELIEVED`, `OBSERVED`, and `SUPPORTED` can be incomparable until a separate authority or validation process relates them. Contradiction must preserve the prior state and the newer evidence; it must not destructively overwrite history.

### MEMORY_LIFECYCLE

Memory lifecycle flows describe a trace status. They do not grant write authority.

States:

- `EPHEMERAL_TRACE`
- `SESSION_TRACE`
- `CANDIDATE_MEMORY`
- `PROMOTED_MEMORY`
- `CONSOLIDATED_MEMORY`
- `SUPERSEDED_MEMORY`
- `REJECTED_MEMORY`

`MEMORY_WRITE_AUTHORITY` is false in this contract. Any promotion is descriptive unless a separate approved Native Memory authority path exists. Native Memory must not be written by V0 tests.

### GOVERNANCE_STATE

Governance flows describe action-control state around an object. They are not linguistic meaning and they are not authority by themselves.

States:

- `MENTIONED`
- `PROPOSED`
- `REQUESTED`
- `QUALIFIED`
- `HOLD`
- `BLOCK`
- `AUTHORIZED`
- `EXECUTED`
- `RECEIPTED`

Examples:

- `lance le test` may produce a semantic request and a governance progression `MENTIONED -> REQUESTED -> HOLD`.
- `le test a ete lance hier` may be mentioned or asserted, but must not become `REQUESTED`.
- `tu peux lancer le test ?` may remain semantically ambiguous while the governance flow becomes `REQUESTED_CANDIDATE -> HOLD`.

KX108 remains the sole decision authority. `AUTHORIZED` and `EXECUTED` require external authority and receipts; they cannot be inferred from semantics alone.

## Flow Properties

`DIRECT RELATION`: a family-local relation explicitly asserted or extracted between two objects.

`INDIRECT PATH`: a path discovered through multiple family-local relations. It inherits only the family rules that produced it.

`SHARED ANCESTOR`: two objects derive from the same prior object, frame, event, memory, or source.

`SHARED CAUSE`: two objects are linked to a common causal source within the causal family. A shared cause claim is not a shared validated cause unless its causal claim type is validated.

`TEMPORAL RELATION`: a relation over time coordinates or temporal order only.

`SEMANTIC SIMILARITY`: resemblance between objects or meanings. Similarity is not provenance, causality, evidence, or authority.

`PROVENANCE RELATION`: a relation between object and source, such as utterance, report, parser extraction, log, observation, receipt, or human decision.

`NO_PROVEN_CONNECTION`: explicit absence of a known path or relation under the queried family and scope.

A path through one family must never silently imply a path through another family. Family crossing is allowed only through shared object identity and explicit conversion rules.

## Representation Options

### Option A: One Generic OrderedMeaningFlow Dataclass

A single dataclass with `family`, source/target/state, relation, provenance, confidence, status, and metadata.

| Dimension | Evaluation |
| --- | --- |
| Type safety | Low to medium; family rules mostly runtime-validated. |
| Cross-family leakage risk | Medium to high if callers treat relation labels globally. |
| Runtime simplicity | High; one storage and traversal structure. |
| Auditability | Good if every record is explicit and serializable. |
| Replayability | Good if deterministic metadata and provenance are mandatory. |
| Current `LatticeRelation` compatibility | Good; it can wrap or generalize existing relation records. |
| Future Native Memory compatibility | Medium; memory authority boundaries need validators. |
| Receipts compatibility | Medium; receipt fields can fit metadata but may need stronger schema. |
| 34-tree / point-cloud compatibility | Good as a common edge envelope. |

### Option B: Typed Family-specific Flow Subclasses

Separate classes such as `TemporalOrderFlow`, `CausalClaimFlow`, `EpistemicStateFlow`, `MemoryLifecycleFlow`, and `GovernanceStateFlow`.

| Dimension | Evaluation |
| --- | --- |
| Type safety | High; family-local enums and required fields are explicit. |
| Cross-family leakage risk | Low; illegal transitions are harder to encode. |
| Runtime simplicity | Medium to low; more classes and converters. |
| Auditability | Good, but reports must normalize across families. |
| Replayability | Good if schemas are versioned. |
| Current `LatticeRelation` compatibility | Medium; adapter needed. |
| Future Native Memory compatibility | Good for memory lifecycle boundaries. |
| Receipts compatibility | Good when receipt-bearing families define strict fields. |
| 34-tree / point-cloud compatibility | Medium; projection needs a common export shape. |

### Option C: Generic Relation Core + Family-specific Validators

A generic immutable flow record stores common fields. Each family supplies validators, enums, transitivity rules, allowed state transitions, and cross-family conversion guards.

| Dimension | Evaluation |
| --- | --- |
| Type safety | Medium to high; core stays generic while validators enforce family rules. |
| Cross-family leakage risk | Low if every traversal and inference requires a family validator. |
| Runtime simplicity | Medium; one storage model, several rule modules. |
| Auditability | High; common report shape plus explicit family verdicts. |
| Replayability | High; deterministic validation and inference can be versioned. |
| Current `LatticeRelation` compatibility | High; existing lattice relations can be adapted into the core envelope. |
| Future Native Memory compatibility | Good; memory validators can keep authority false by default. |
| Receipts compatibility | Good; receipt validators can require hashes, signatures, or authority references. |
| 34-tree / point-cloud compatibility | Good; common core exports edges while validators prevent vague links. |

Preferred V0 direction: Option C. It best balances compatibility with the current lattice and future typed safety. The first implementation should introduce minimal primitives and validators, not a new engine.

## V0 Implementation Boundary

Allowed next step: implement minimal OrderedMeaningFlow primitives and validators sufficient to satisfy the frozen contract tests.

Disallowed in V0 spec pass:

- no runtime engine
- no Native Memory write
- no KX108 change
- no gate or router change
- no authority shortcut
- no causal proof inferred from language or temporal succession
