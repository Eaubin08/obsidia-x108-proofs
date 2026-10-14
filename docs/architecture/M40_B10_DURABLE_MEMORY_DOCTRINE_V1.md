# M40 --- B10 Durable Memory Doctrine V1

**Status**: DOCTRINE_AUTHORED - Awaiting Independent Certification
**Chapter**: M40 / B10 Durable Memory
**Phase**: DOCTRINE V1 --- Semantic and authority boundaries only
**Prerequisite doctrines**: M38 (CLOSED) - M39 (CLOSED)
**Foundation**: COGNITIVE_FOUNDATION_V1=SEALED - FOUNDATION_REOPEN=NO
**Date**: 2026-10-13
**Lifecycle**: forensic -> independent forensic certification -> owner decisions -> **doctrine** -> independent doctrine certification -> spec-readiness forensic -> spec -> runtime -> CLOSED

---

## 0. Scope and non-scope

This document defines the semantic and authority boundaries of B10 Durable Memory.

B10 V1 doctrine defines WHAT durable persistence means for B8 epistemic history. It does not implement persistence.

**This document does NOT create:**

- B10 runtime
- B10 storage adapter
- B10 spec
- B10 tests
- Write receipt type
- Revision ledger type
- Backend selection

**This document does NOT modify:**

- B8 (CLOSED)
- M38 (CLOSED)
- M39 (CLOSED)
- Native Memory (READ_ONLY)
- memory_write (remains False)

---

## 1. B10 Residual Core

```
B10_RESIDUAL_CORE=
GOVERNED_DURABLE_PERSISTENCE_CONTRACT_FOR_B8_EPISTEMIC_HISTORY
```

B10 owns durable persistence semantics for B8 epistemic history.

B10 does NOT own:

- epistemic promotion (B8)
- version/supersession semantics (M38)
- historical-query semantics (M39)
- truth resolution (no layer owns this --- MEMORY != TRUTH)
- conflict resolution (B8)
- calibration (B11)
- selection / admissibility (B12)
- action authority (KX108 / Binder)
- World Model (M41 --- DEFERRED)
- execution replay (distinct layer)

---

## 2. Safety laws

These laws apply to every B10 implementation.

| Law | Evidence level | Source |
|---|---|---|
| MEMORY != TRUTH | DIRECT | COGNITIVE_FOUNDATION_V1_SEAL s3 l.24 |
| PERSISTED != TRUE | SUPPORTED | Deduction from MEMORY != TRUTH |
| RETRIEVED != TRUE | SUPPORTED | Deduction from MEMORY != TRUTH |
| PROMOTED != ABSOLUTE_TRUTH | DIRECT | COGNITIVE_FOUNDATION_V1_SEAL s3 l.27 |
| PROMOTED != DURABLE_WRITE | DIRECT | B8 s11 l.677-679 |
| MEMORY_WRITE_INTENT != MEMORY_WRITE_AUTHORIZATION | DIRECT | B8 s11 l.679 + contracts.py |
| MEMORY_ARTIFACT_CANDIDATE != DURABLE_WRITE | DIRECT | B8 s12 l.689 + s11 |
| WRITE_NEW != AUTOMATIC_SUPERSESSION | DIRECT | M38 versioning != memory |
| INVALIDATED != DELETED | OWNER_DOCTRINE | s12 |
| SUPERSEDED != DELETED | OWNER_DOCTRINE | s12 |
| WORKING_STATE != DURABLE_MEMORY | DIRECT | contracts.py docstring |
| MEMORY != WORLD_MODEL | OWNER_BOUNDARY | s27 |
| MEMORY != AUTHORITY | DIRECT | COGNITIVE_FOUNDATION_V1_SEAL |
| MEMORY_WRITE != ACTION_AUTHORITY | DIRECT | contracts.py BOUNDARY dict |
| POINT_IN_TIME != MEMORY | DIRECT | M39 s31 |
| VERSIONING != MEMORY | DIRECT | M38 s24 |
| EPISTEMIC_STATUS != MEMORY_LIFECYCLE_STATUS | DIRECT | B8 s2 l.50 |

On B8 and authority:

```
B8_CANONICAL_EPISTEMIC_GATE=YES
B10_CANONICAL_DURABLE_HISTORY_ROLE=YES
```

Canonical != true. Never use SOURCE_OF_TRUTH for B8 or B10.

---

## 3. B10 V1 direct subject

```
B10_V1_DIRECT_SUBJECT=B8_EPISTEMIC_HISTORY_ARTIFACTS
```

The direct historical core for V1 persistence:

- KnowledgeRecord --- epistemic claim state transitions
- EpistemicGap historical records --- unknown/absence history
- TransitionReceipt --- B8 transition proof artifacts
- GapTransitionReceipt --- gap transition proof artifacts
- SupersessionTransitionBundle --- supersession history
- GapPartitionBundle --- gap partition history

**KnowledgeClaim:**

```
KNOWLEDGE_CLAIM_ROLE=REFERENCED_IMMUTABLE_CLAIM_ANCHOR
```

Whether B10 stores complete claim payload or canonical claim reference is SPEC-owned. Doctrine does not decide.

**VerificationRecord / HumanAttestation:**

```
PROVENANCE_DEPENDENCY_SUPPORTED
DIRECT_PERSISTENCE_SCOPE=UNRESOLVED
```

**TransitionRequest:**

```
B10_V1_TRANSITION_REQUEST_HISTORY=EXCLUDED
```

TransitionRequest is a B8-internal gate artifact, not an epistemic history artifact.

---

## 4. Excluded V1 subjects

```
B9_PATH_HISTORY_B10_V1=NO
FAILED_PATH_B10_V1=NO

SENS_ARTIFACTS_B10_V1=NO
ARM_ARTIFACTS_B10_V1=NO

TEMPORAL_TRANSFORM_B10_V1=NO
WORLD_MODEL_STATE_B10_V1=NO

GENERIC_COGNITIVE_OBJECT_STORE=NO
GENERIC_ARBITRARY_OBJECT_STORE=NO
```

B10 V1 is not a general-purpose cognitive object store.

---

## 5. Persistence decision

```
B8_EMITS_PERSISTENCE_ELIGIBLE_ARTIFACTS=YES
B10_DECIDES_PERSISTENCE=YES
EVERY_B8_TRANSITION_TRIGGERS_B10_WRITE=NO
B10_WRITE_TRIGGER_POLICY=UNDEFINED_PENDING_SPEC
```

B8 emits epistemic history artifacts eligible for durable persistence. B10 decides persistence.

The canonical durable route (B8 s1 ll.35-37):

```
candidate
-> B8 transition
-> verification
-> promoted knowledge state
-> B10 persistence request
-> governed write authorization (Binder / KX108)
-> durable write
-> receipt / replay
```

The route contains a promotion step before the B10 persistence request. This does not imply promotion alone triggers a durable write, nor that every transition necessarily produces one. Trigger granularity is SPEC-owned.

---

## 6. Write authorization chain

Three distinct roles:

```
PERSISTENCE_DECISION_OWNER   = B10
WRITE_AUTHORIZATION_BOUNDARY = BINDER_KX108
WRITE_EXECUTION_OWNER        = PERSISTENCE_ADAPTER (future spec)
```

Every actual durable write must cross the governed Binder/KX108 action boundary (B8 s11 l.679).

```
ONE_NEW_KX108_DECISION_PER_PHYSICAL_STORAGE_OPERATION=UNDEFINED
```

Batching, per-object or per-transaction authorization granularity is SPEC-owned.

---

## 7. memory_write

```
MEMORY_WRITE_CURRENT=FALSE
ENTERING_B10_REOPENS_MEMORY_WRITE=NO
B10_DOCTRINE_AUTHORIZES_WRITES=NO
B10_SPEC_WILL_NOT_AUTOMATICALLY_AUTHORIZE_WRITES=YES
```

memory_write remains False until a later explicit runtime APPLY phase and independent certification of the write/authorization contract.

---

## 8. Backend

**Owner decision:**

```
B10_SEMANTICS_BACKEND_AGNOSTIC=YES
STORAGE_BACKEND != MEMORY_SEMANTICS
```

Classification: OWNER_DOCTRINE. This is not recovered from direct historical evidence --- it is an explicit architectural principle decided here.

No V1 backend selected. Backend selection is SPEC-owned.

---

## 9. Native Memory

```
NATIVE_MEMORY_CURRENT_ROLE=READ_ONLY_RETRIEVAL_INDEX
NATIVE_MEMORY_IS_CANONICAL_B10_BACKEND=NO
NATIVE_MEMORY_FUTURE_B10_ROLE=DEFERRED
```

The Native Memory index (status=MATERIALIZED_READONLY, 3267 records) is a read-only retrieval index. B10 doctrine does not modify or write it.

---

## 10. Graphiti / Neo4j

```
GRAPHITI_RUNTIME_CALLS=0
NEO4J_RUNTIME_CALLS=0

GRAPHITI_B10_STATUS=DEFERRED_LEGACY_CANDIDATE
NEO4J_B10_STATUS=DEFERRED_LEGACY_CANDIDATE
```

Historical existence in the codebase does not make either system canonical, optional-supported, or active. Both remain deferred pending explicit future decisions.

---

## 11. Logical history

**Owner decision:**

```
B10_V1_LOGICAL_HISTORY_APPEND_ONLY=YES
B10_V1_NO_DESTRUCTIVE_OVERWRITE=YES
B10_V1_IN_PLACE_HISTORICAL_MUTATION=NO
```

Source: B8 s10 l.621 --- no destructive overwrite. Durable storage of this history is B10.

Scope: B8 epistemic history persisted by B10 V1. This decision does not generalize to all future memory object classes.

---

## 12. Retention / deletion

```
B10_PHYSICAL_RETENTION_POLICY=UNDEFINED
B10_PHYSICAL_DELETION_POLICY=UNDEFINED
B10_FORGETTING_MODEL=UNDEFINED
```

Semantic distinctions preserved:

```
SUPERSEDED != DELETED
INVALIDATED != DELETED
```

B10 does not infer infinite physical retention. Retention, deletion, and forgetting models are SPEC/owner decisions.

---

## 13. Slot_revision structural gap (CRITICAL)

```
KNOWLEDGE_RECORD_STORES_SLOT_REVISION=NO
SLOT_SNAPSHOT_STORES_SLOT_REVISION=YES
B10_M39_REVISION_ASSOCIATION_REQUIRED=YES
```

Confirmed in app/knowledge/b8/core.py:

- KnowledgeRecord (ll.47-81): no slot_revision field
- SlotSnapshot (ll.194-206): carries slot_revision: int

The association between a logical slot revision and the set of KnowledgeRecord artifacts committed at that revision exists only in SlotSnapshot at runtime. It does not survive restart unless explicitly persisted by B10.

Future B10 must durably preserve enough metadata to reconstruct:

```
B10_MINIMUM_FOR_M39_RUNTIME=
  persistent ordered B8 epistemic history
+ per-slot logical-revision association
+ ability to recover artifacts committed at or before R
```

KnowledgeRecord alone is not sufficient for M39 KNOWLEDGE_STATE_AS_OF_REVISION(R).

Implementation is SPEC-owned. Do not define RevisionEnvelope, HistoryLedger, RevisionRecord, CommitBundle, or GlobalRevision here.

---

## 14. Write receipt

```
B10_WRITE_RECEIPT_REQUIRED=YES_AT_CONTRACT_LEVEL
```

A durable state-changing write must be provable and auditable. Exact receipt type and schema are SPEC-owned.

KX108 action receipts are not automatically B10 history artifacts.

---

## 15. Idempotence

Direct B8 evidence preserved:

- T1 capture: idempotent on claim_id (B8 s12 l.689)
- G1 gap: idempotent on gap_id (B8 s6 table)
- Duplicate request: NO_OP_DUPLICATE behavior (B8 l.417)

```
B10_WRITE_IDEMPOTENCE_CONTRACT=REQUIRED_IN_PRINCIPLE_BUT_SPEC_UNDEFINED
B10_DEDUPLICATION_MODEL=UNDEFINED
```

Canonical IDs do not by themselves prove backend deduplication. Deduplication implementation is SPEC-owned.

---

## 16. Artifact identity and determinism

```
B8_ARTIFACT_IDENTITY_DETERMINISTIC=YES
B10_STORAGE_EXECUTION_DETERMINISM=UNDEFINED
```

B8 canonical artifact identities are deterministic (hash of canonical fields). Physical storage I/O determinism is a separate SPEC/runtime question.

---

## 17. Provenance metadata

When present in artifacts, preserve:

- canonical artifact IDs (b8rec_, b8claim_, b8gap_, b8rcpt_, b8grcpt_, b8bundle_, b8gpart_)
- claim_id, claim_version, record_version
- gap lineage/version
- previous_record_id / previous artifact IDs
- refs, staleness_trigger_refs
- recorded_at, clock domain
- supersedes, superseded_by, contested_by

Not every field exists on every artifact. Exact presence is artifact-type specific.

B10/M39 additional requirement:

```
PER_SLOT_LOGICAL_REVISION_ASSOCIATION=REQUIRED
```

Physical representation deferred to spec. See s13.

---

## 18. Artifact integrity

```
B10_MUST_PRESERVE_CANONICAL_ARTIFACT_IDENTITY=YES
```

Distinct concerns not conflated in V1 doctrine:

- artifact SHA identity
- manifest hash
- backend corruption detection
- transaction atomicity
- partial-write recovery

These remain SPEC/runtime questions.

---

## 19. Unknown / gap history

```
UNKNOWN != FALSE
UNKNOWN != DROP_FROM_HISTORY
EPISTEMIC_GAP != FALSE
```

EpistemicGap history is in V1 durable historical scope. Persisting a gap record does not resolve the gap. Unknown history must be preserved as unknown.

---

## 20. Conflicts

```
B10_CONFLICT_RESOLUTION=NONE
```

B8 owns epistemic conflict semantics. B10 may persist contradictory or CONTESTED historical artifacts without resolving them.

---

## 21. Working state

```
WORKING_STATE != DURABLE_MEMORY
```

Source: contracts.py docstring. B10 is not ContextPacket construction.

---

## 22. M38 relationship

M38 remains CLOSED.

```
M38_IS_PREREQUISITE_FOR_B10=PARTIAL
VERSIONING != MEMORY
WRITE_NEW != AUTOMATIC_SUPERSESSION
```

M38 defines version/supersession semantics. B10 persists historical artifacts carrying those relations. M38 V1 has no storage interface (M38 s24 l.361).

---

## 23. M39 relationship

M39 remains CLOSED.

```
M39_IS_PREREQUISITE_FOR_B10=PARTIAL
B10_IS_PREREQUISITE_FOR_M39=PARTIAL
POINT_IN_TIME != MEMORY
```

M39 defines historical-query semantics. B10 owns durable history required by future M39 runtime. M39 V1 doctrine exists without B10 (M39 s31 l.420). See s13 for the slot_revision structural gap.

---

## 24. B9 relationship

```
B9_DURABLE_MEMORY_WRITE=NO
B9_NATIVE_MEMORY_WRITE=NO
B9_GRAPHITI_WRITE=NO
B9_PATH_HISTORY_B10_V1=NO
```

Source: B9 s8. B9 path history is a future question outside V1 scope.

---

## 25. B11 / B12 / B13

```
B10_CALIBRATION=NONE
B10_COMPETENCE=NONE
B10_CAPABILITY_SELECTION=NONE
B10_ADMISSIBILITY_SELECTION=NONE
B10_AUTHORITY=NONE
B10_REALIZED_STATE_RECONCILIATION=NONE
```

---

## 26. Retrieval

```
B10_V1_ROLE=PERSISTENCE
B10_RETRIEVAL_RANKING=NO
B10_MEMORY_SELECTION=NO
B10_CONTEXT_ASSEMBLY=NO
```

Minimal storage read/recovery primitives may be required in spec. Retrieval, ranking, and context selection are not B10 V1 semantic authority.

---

## 27. World Model

```
MEMORY != WORLD_MODEL
M41_B10_CONSUMPTION=DEFERRED
WORLD_MODEL_STATE_B10_V1=NO
```

M41 owns structured world representation. B10 V1 does not expand its persisted subject to anticipate M41.

---

## 28. Runtime status

```
B10_RUNTIME_IMPLEMENTED=NO
B10_STORAGE_ADAPTER_IMPLEMENTED=NO
B10_WRITE_PATH_IMPLEMENTED=NO
B10_EVENTUAL_RUNTIME_NEEDED=YES
B10_FINAL_IMPLEMENTATION_CLOSURE_REQUIRES_RUNTIME_PROOF=YES
```

Source: B8 s14 ll.805-806 (deferred), COGNITIVE_FOUNDATION_V1_SEAL s7 (deferred).

Doctrine certification alone does not mark B10 CLOSED.

---

## 29. Reopen conditions

The following require explicit reopen and independent certification before activation:

- memory_write=True
- Native Memory writes
- Graphiti runtime activation
- Neo4j runtime activation
- B9 path history persistence
- SENS event persistence
- Generic cognitive object persistence
- World Model integration
- Retention/deletion semantics
- Retrieval ownership
- Cross-domain memory sharing

---

## 30. Spec and runtime deferrals

Explicitly deferred to spec/runtime:

- write failure handling
- read failure handling
- partial write recovery
- backend unavailable handling
- corruption detection
- transaction atomicity
- retry semantics
- deduplication implementation
- physical deletion mechanics
- retention duration
- forgetting
- schema migration
- storage lifecycle
- backend selection and wiring

---

## 31. Lifecycle

```
M40_B10_LIFECYCLE=
  forensic
  -> independent forensic certification
  -> owner decisions
  -> doctrine                         <- CURRENT POSITION
  -> independent doctrine certification
  -> spec-readiness forensic
  -> owner spec decisions
  -> spec
  -> independent spec certification
  -> RED
  -> GREEN runtime
  -> restart/durability/replay/integrity tests
  -> final independent runtime certification
  -> CLOSED
```

---

## 32. Self-audit

```
B10_RUNTIME_CREATED               = 0
B10_SPEC_CREATED                  = 0
B10_TESTS_CREATED                 = 0
MEMORY_WRITE_ENABLED              = 0
NATIVE_MEMORY_WRITES_CREATED      = 0
GRAPHITI_RUNTIME_CREATED          = 0
NEO4J_RUNTIME_CREATED             = 0
B8_MODIFIED                       = 0
M38_MODIFIED                      = 0
M39_MODIFIED                      = 0
B9_SCOPE_LEAKS                    = 0
SENS_SCOPE_LEAKS                  = 0
WORLD_MODEL_SCOPE_LEAKS           = 0
TRUTH_AUTHORITY_LEAKS             = 0
SLOT_REVISION_FALSE_CLAIMS        = 0
BACKEND_CANONIZATION_LEAKS        = 0
RETENTION_POLICY_INVENTED         = 0
```

---

## 33. Status

```
B10_DOCTRINE_AUTHORED               = YES
B10_DOCTRINE_INDEPENDENTLY_CERTIFIED = NO

B10_RUNTIME_IMPLEMENTED             = NO

M40_STATUS                          =
DOCTRINE_AUTHORED_AWAITING_INDEPENDENT_CERTIFICATION

B10_CLOSED                          = NO

MEMORY_WRITE                        = FALSE

PUSH                                = NO
MERGE                               = NO
```

**NEXT_STEP**: fresh independent READ_ONLY certification of M40/B10 doctrine.

If certification passes:

- B10_DOCTRINE_INDEPENDENTLY_CERTIFIED=YES
- M40_STATUS=DOCTRINE_CERTIFIED_AWAITING_SPEC_READINESS_FORENSIC
- B10_CLOSED=NO

Do NOT author spec automatically.
