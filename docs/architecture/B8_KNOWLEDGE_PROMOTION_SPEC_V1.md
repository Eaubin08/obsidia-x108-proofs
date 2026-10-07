# B8 — Knowledge Promotion State Machine (V1 specification)

```
STATUS=B8_SPEC_V1 / DRAFT_FOR_AUDIT / NO_RUNTIME_IMPLEMENTATION
B8_SPEC_STATUS=DRAFT_FOR_AUDIT
B8_SPEC_INDEPENDENTLY_CERTIFIED=NO
B8_RUNTIME_STATUS=NOT_IMPLEMENTED
SAFE_FOR_B8_RED_TESTS=NO
SAFE_FOR_B8_RUNTIME_IMPLEMENTATION=NO
BASE=B7 runtime closure document 44b0391e (B7 security epoch 1) ; Sentinel V0 c5af4138
FORENSIC_BASIS=B8 forensic (HOLD) + human doctrine D-1..D-5 + O-1..O-5 decisions (2026-10-07)
PROMOTION_AUTHORITY=B8_CANONICAL_TRANSITION_GATE
VERIFICATION_AUTHORITY=TYPED_VERIFIER_BY_CLAIM_CLASS (records only)
KX108_KNOWLEDGE_PROMOTION_ROLE=NONE ; DECISION_AUTHORITY=KX108_ONLY (actions / effects)
MEMORY_WRITE=False  EMITS_ACT=False  KERNEL_MUTATION=False (every B8 element)
```

B8 defines **how a claim's epistemic status may change** and what each change requires. It does
not persist anything durably (B10), does not authorize any action (KX108), and does not decide
truth.

## 1. Human doctrine (2026-10-07)

| Item | Decision |
|---|---|
| D-1 promotion authority | `B8_CANONICAL_TRANSITION_GATE`: deterministic state-transition gate. Not Brody, not an LLM, not a provider, not a human alone, not KX108. |
| D-2 KX108 | `KX108_KNOWLEDGE_PROMOTION_ROLE=NONE`. B8 authorizes epistemic transition; B10 may request persistence; Binder/KX108 may govern the actual write. |
| D-3 verification | Typed verifier per claim class produces a `VerificationRecord`; it never changes state. Invalidation and supersession = explicit B8 gate transitions. |
| D-4 human approval | `HUMAN_APPROVAL != TRUTH`. Default role ATTESTATION / REVIEW_AUTHORIZATION. Primary evidence only when the source of truth is the human declaration itself (preference, consent, operator approval, organizational policy), identity and provenance preserved. |
| D-5 legacy manual writes | `NEO4J_MANUAL_APPLY_PATH=SUPERSEDE_BEFORE_CANONICAL_RUNTIME_WRITE`; static in-source tokens are never authority. |

Canonical durable route (B8 = steps 1–4): `candidate → B8 transition → verification → promoted
knowledge state → B10 persistence request → governed write authorization → durable write →
receipt / replay`.

## 2. Frozen laws

B7_ACCEPT != DURABLE_KNOWLEDGE · VALIDATED_WORKING_CONTEXT != MEMORY · BELIEF != KNOWLEDGE ·
REPORT != VERIFIED · OBSERVED != VERIFIED · CONFIDENCE != TRUTH · CONFIDENCE != AUTHORITY ·
CANDIDATE != PROMOTED · COGNITIVE_PROPOSAL != MEMORY_AUTHORITY · HUMAN_APPROVAL != TRUTH ·
SELF_ASSERTED_DISPLAY_NAME != VERIFIED_HUMAN_IDENTITY · VERIFIER != PROMOTION_AUTHORITY ·
PROMOTION_AUTHORITY != ACTION_AUTHORITY · KNOWLEDGE_PROMOTION != ACTION_AUTHORIZATION ·
KNOWLEDGE_STATUS != WRITE_PERMISSION · PROMOTED != ABSOLUTE_TRUTH · MEMORY != TRUTH ·
UNKNOWN != FALSE · UNKNOWN != VERIFIED · STALE != INVALIDATED != SUPERSEDED != FALSE ·
CONTENT != SCOPE != PROVENANCE · CLAIM_VERSION != RECORD_VERSION ·
HISTORICAL_PROMOTED != CURRENT_PROMOTED · CONTRADICTION != AUTOMATIC_RESOLUTION ·
EPISTEMIC_STATUS != MEMORY_LIFECYCLE_STATUS · NO_SILENT_PROMOTION · NO_SILENT_OVERWRITE ·
DECISION_AUTHORITY=KX108_ONLY · TIME_VALUE != TEMPORAL_ORDER · TIMESTAMP != CAUSALITY ·
RECORDED_AT != WORLD_TIME · SOURCE_TIME != RECORDED_AT · ONE_SYSTEM != ONE_CLOCK ·
ONE_IDENTITY != ONE_TEMPORALITY · LOGICAL_ORDER != PHYSICAL_TIME · TIME_VALUE != TEMPORAL_FRAME ·
VALID_TIME != RECORDED_AT · SOURCE_TIME != VALID_TIME · OBSERVED_TIME != RECORDED_AT ·
SERIALIZATION_ORDER != CAUSAL_ORDER · SERIALIZATION_ORDER != PHYSICAL_TIME ·
SAME_KNOWLEDGE_SLOT != SAME_TEMPORAL_FRAME · UNKNOWN_VALUE != TEMPORAL_RELATION_UNKNOWN ·
ONE_OBJECT, MANY_TEMPORAL_PROJECTIONS, NO_AUTOMATIC_FUSION · RECEIVED_ORDER != WORLD_ORDER ·
RECORDED_ORDER != WORLD_ORDER · SERIALIZATION_ORDER != WORLD_ORDER · TRANSFORM_EXISTS !=
TRANSFORM_ADMISSIBLE · TEMPORALLY_INDETERMINATE != UNKNOWN != FALSE != NO_ASSERTION != CONTESTED.

## 3. Identities and bounds (O-6)

Every identity = prefix + full SHA-256 hex (64 hex, 256 bits) over strict canonical JSON
(`app.harness.state_explicit.contracts.canonical_json`), same discipline as B7 (`full_digest`).
Prefixes namespace only: `IDENTITY_COLLISION_REDUCTION=NONE`.

| Object | Prefix | Preimage (all canonical fields) |
|---|---|---|
| KnowledgeSlot | `b8slot_` | canonical slot tuple (§5) |
| KnowledgeClaim | `b8claim_` | lineage_id, claim_version, previous_claim_id, claim_class, slot_id, valid_time, content |
| EvidenceRef | `b8ev_` | every field |
| VerificationRecord | `b8ver_` | every field |
| HumanAttestation | `b8att_` | every field |
| KnowledgeRecord | `b8rec_` | claim_id, claim_version, record_version, state, every ref field, supersedes / superseded_by, recorded_at, previous_record_id |
| TransitionRequest | `b8treq_` | every field |
| TransitionReceipt | `b8rcpt_` | every field |
| SupersessionTransitionBundle | `b8bundle_` | every field except bundle_digest |
| GapPartitionBundle | `b8gpart_` | every field except bundle_digest |
| EpistemicGap record | `b8gap_` | gap_id lineage fields, gap_version, state, refs, recorded_at, previous_gap_record_id |
| GapTransitionRequest / Receipt | `b8greq_` / `b8grcpt_` | every field |

Bounds (V1, reused from B7, no new number):

```
OBJECT_TOTAL_BOUND=MAX_CANDIDATE_CHARS=32768 canonical JSON characters per B8 object
OBJECT_TOTAL_SERIALIZED_BOUND=YES ; UNBOUNDED_TOTAL_OBJECT_SIZE=NO
OVERSIZE_BEHAVIOR=REJECT ; TRUNCATION_ALLOWED=NO
PER_FIELD_TEXT_BOUNDS=NONE_EXPLICIT_V1
PER_COLLECTION_CARDINALITY_BOUNDS=NONE_EXPLICIT_V1
```

The total-object bound limits the total quantity of nested text and collection content
indirectly; V1 defines no independent per-field length or per-collection cardinality limit.
Requests carry references, not embedded evidence bodies. Per-claim history length is
append-only log size, a B10 persistence concern.

## 4. Typed objects

| Object | Content |
|---|---|
| `KnowledgeClaim` | `lineage_id`, `claim_version`, `previous_claim_id` (null for version 1), `claim_class`, `slot_id` (§5), `valid_time`, structured `content`, `source_refs`, `origin_refs` (e.g. B7 derived state id) |
| `ClaimClass` (closed enum, O-2) | FORMAL_CLAIM, CODE_BUILD_CLAIM, PHYSICAL_CLAIM, DOCUMENTARY_CLAIM, DOMAIN_CLAIM, HUMAN_DECLARATION, ORGANIZATIONAL_POLICY |
| `EvidenceRef` | kind, source ref, content digest, captured_at, provenance refs, optional descriptive confidence |
| `VerificationRecord` | verifier_family, claim_id, claim_version, verdict SATISFIED / NOT_SATISFIED / INCONCLUSIVE, evidence_refs, method ref, produced_at |
| `HumanAttestation` (O-5) | attestation_id, actor_id, identity_source, auth_context_ref, issued_at, claim_id, claim_version, attestation_kind (ATTESTATION / REVIEW_AUTHORIZATION / PRIMARY_DECLARATION), scope, optional proof/signature ref |
| `KnowledgeRecord` | claim_id, claim_version, record_version, state, evidence / verification / attestation refs, supersedes / superseded_by, contested_by, recorded_at, previous_record_id |
| `TransitionRequest` | claim_id, expected_claim_version, expected_state, expected_record_version, slot_id, expected_slot_revision, target_state, refs, (T9 only) supersedes_claim_id + supersedes_record_id, requester ref, reason |
| `TransitionReceipt` | request id, verdict APPLIED / REJECTED / NO_OP_DUPLICATE, claim_id, claim_version, from / to state, from / to record_version, from / to record id, reasons, gate contract version, recorded_at |
| `SupersessionTransitionBundle` | §9.3 |
| `EpistemicGap` (O-1) | gap_id (lineage), gap_version, slot_id, valid_time, reason knowledge is unavailable, missing evidence, contradiction refs, provenance, state OPEN / RESOLVED / SUPERSEDED, recorded_at |

### 4.1 Version model (D-B8-S2)

- **claim_version**: semantic revision number inside one claim lineage (`lineage_id`). It
  changes only when semantic claim material changes (content, scope, valid_time, predicate,
  subjects / contexts): a new `KnowledgeClaim` with `claim_version = previous + 1` and
  `previous_claim_id` set; the new claim has a new `claim_id` and starts its own epistemic
  history at T1. Version 1 has no predecessor. Independent competing claims on the same slot are
  separate lineages, never silent revisions of each other.
- **record_version**: monotonic epistemic-transition counter for one `claim_id`; every applied
  transition creates one immutable `KnowledgeRecord` with `record_version = previous + 1`
  (T1 → 1). State-only changes never change `claim_version`.
  Example (claim X, claim_version 1): rv1 CANDIDATE, rv2 SUPPORTED, rv3 VERIFIED, rv4 PROMOTED,
  rv5 CONTESTED.
- **Verification binding**: a `VerificationRecord` / `HumanAttestation` binds to
  `(claim_id, claim_version)`; it never carries over to another claim version.
- **Record identity**: `b8rec_` over claim_id, claim_version, record_version, state, refs,
  links, recorded_at, previous_record_id — unique per immutable record.

Temporal fields are separate and never conflated: `valid_time` (when the claim applies in the
modeled world / domain), `source_time` / `observed_time` (time reported by the source or observer,
when available), `recorded_at` (when one Obsidia recorder recorded the artifact), each timestamp
carrying a `clock_domain` / `temporal_frame_ref` (the reference in which it is meaningful),
`record_version` / `gap_version` (logical order inside one object), `slot_revision` (canonical
logical order of B8 mutations on one slot) and `proof_time` / `anchor_time` (future external
receipt timestamp, out of B8 scope). Timestamps are inputs supplied to the gate, never read by
it: the gate stays deterministic. B8 assumes no universal clock; these fields must remain
mappable later onto the MMonde / F12 TimeEnvelope temporal reference structures (not implemented
in B8, and no competing global clock abstraction is introduced). Confidence is descriptive data inside evidence; it is never a
sufficient precondition and never part of a policy decision.

## 5. Scope and slots (O-4, D-B8-S4)

`CONTENT != SCOPE != PROVENANCE`. Scope = `KnowledgeScope{subject_refs, context_refs, domain_id,
valid_time}`; sources and evidence are provenance, never scope.

Slot canonicalization (applied before hashing; any violation → REJECT):

1. Every textual component (domain_id, predicate_ref, each subject / context ref) must be a
   string, normalized to Unicode NFC; empty or whitespace-only strings and non-strings are
   rejected. No other normalization (no case folding, no trimming beyond the rejection rule).
2. `subject_refs` and `context_refs` are **unordered sets**: normalize each, reject empty
   elements, deduplicate exact normalized values, sort by code point. `subject_refs` must contain
   at least one element (`EMPTY_SUBJECT_REFS=REJECT`: a subjectless slot is too broad for V1;
   global knowledge needs a future audited contract with a typed canonical subject).
   `context_refs` may be empty (`EMPTY_CONTEXT_REFS=ALLOWED`: no extra discriminator).
3. `KnowledgeSlot` = `b8slot_` + SHA-256(canonical_json([claim_class, domain_id,
   subject_set, context_set, predicate_ref])) — full 256 bits.

Hence ref order, duplicates and Unicode-equivalent forms never change the slot id. A domain that
needs ordered participants puts that order in typed claim content, never in the slot sets.

`valid_time` stays outside the slot:

- same slot, non-overlapping valid_time → historical coexistence;
- same slot, overlapping valid_time, different admissible successor → T9 supersession only;
- different context / domain → different slot, never fused.

### 5.1 Temporal frames and valid-time algebra (D-B8-R4-1, D-B8-R4-2)

- `TemporalFrameRef`: opaque typed reference to the temporal frame / domain in which a time value is
  meaningful (domain clock, source clock, simulation timeline, physical standard, process
  timeline, future MMonde reference…). It is not a clock, a timestamp, a source of truth, an
  authority, nor a claim that the frame is fundamental.
- `ValidTimeInterval{temporal_frame_ref, start, end, boundary_semantics}` (V1 boundary semantics:
  half-open `[start, end)`, `start` may be −∞, `end` may be +∞). `start` / `end` mean nothing
  outside their frame (`VALID_TIME_HAS_TEMPORAL_REFERENCE=YES`). Every gap scope and claim
  `valid_time` is a ValidTimeInterval; `TemporalPoint{temporal_frame_ref, value}` is the query form.
  Source / observed / recorded / proof timestamps also carry their frame.
- The frame is **not** part of KnowledgeSlot identity: one semantic question may have several
  temporal projections (`SAME_KNOWLEDGE_SLOT != SAME_TEMPORAL_FRAME`).
- **V1 rule (D-B8-R5-1..R5-3, human doctrine 2026-10-07): `TEMPORALLY_COMPARABLE(A, B) =
  (A.temporal_frame_ref == B.temporal_frame_ref)`** — no second branch
  (`B8_V1_CROSS_FRAME_COMPARISON_SUPPORTED=NO`). Frame identity is explicit identity, never inferred
  from names, labels, clock similarity, recency, source identity or similar values; no implicit
  conversion (`CROSS_FRAME_RAW_TIME_COMPARISON=FORBIDDEN`, `IMPLICIT_TEMPORAL_FRAME_CONVERSION=0`).
- `TemporalTransformRef{source_frame, target_frame, transform_id, transform_version, provenance,
  validity_scope, exactness}` is `RESERVED_FOR_FUTURE_TEMPORAL_LAYER` with **no normative effect in
  V1**: `TEMPORAL_TRANSFORM_ADMISSION_AUTHORITY_V1=NONE`,
  `TEMPORAL_TRANSFORM_STATE_CHANGE_AUTHORITY_V1=NONE`, `TEMPORAL_TRANSFORM_QUERY_FUSION_V1=FORBIDDEN`,
  `TRANSFORM_REF_CAN_ENABLE_V1_TRANSITION=NO`. Its presence in a request (or as provenance metadata)
  never makes two frames comparable and never affects T6, T9, G2, G3, G4, CURRENT_KNOWLEDGE,
  CURRENT_UNKNOWN or CURRENT_EPISTEMIC_VIEW; no human approval, confidence, source reputation,
  registry presence, name matching or clock similarity activates a transform. Consequently, by
  construction: no inversion (A → B never implies B → A), no composition / chained search / graph
  closure (A → B, B → C never imply A → C), no frame equivalence from cycles, no boundary
  reinterpretation, and no dependency on a transform version (`IMPLICIT_TRANSFORM_INVERSION=0`,
  `IMPLICIT_TRANSFORM_COMPOSITION=0`, `TRANSFORM_CYCLE_IMPLIES_FRAME_IDENTITY=NO`,
  `TRANSFORM_VERSION_SILENT_SUBSTITUTION=0`, `V1_REPLAY_DEPENDS_ON_TRANSFORM_VERSION=NO`).
- Receipts record the temporal comparison basis of each relation they rely on as `SAME_FRAME` or
  `TEMPORALLY_INDETERMINATE`; `CROSS_FRAME_TRANSFORMED` is never a successful V1 basis. Replay applies
  the same rule (frame ids equal, or indeterminate).
- Interval relations — `overlaps(a, b)` = a.start < b.end ∧ b.start < a.end; `contains(a, b)` =
  a.start ≤ b.start ∧ b.end ≤ a.end; `difference(a, b)` = the 0, 1 or 2 exact half-open remainders;
  intersection, coverage, ordering — are defined **only** inside one frame (V1: same frame id),
  with V1 half-open `[start, end)` boundaries (`BOUNDARY_SEMANTICS_AMBIGUITY=0`). Otherwise the relation
  is `TEMPORALLY_INDETERMINATE` and every state-changing operation depending on it fails closed with
  verdict REJECTED, reason `temporal_relation_indeterminate`, no state change (§9.1). In particular T6
  with a current PROMOTED claim on the slot in another frame cannot prove the slot temporally free →
  REJECTED `temporal_relation_indeterminate`; the candidate stays VERIFIED, the occupant stays PROMOTED
  (`INCOMPARABLE_TEMPORAL_OCCUPANCY_CAUSES_UNSAFE_PROMOTION=0`); T9, G2, G3 and G4 across frames →
  REJECTED `temporal_relation_indeterminate`; no cross-frame subtraction, clipping, approximation or
  conversion (`CROSS_FRAME_INTERVAL_DIFFERENCE=FORBIDDEN`).
- `TEMPORALLY_INDETERMINATE` means only that B8 cannot establish the required temporal relation under
  V1 contracts; it is not UNKNOWN, FALSE, NO_ASSERTION or CONTESTED.
- Claims or gaps in incomparable frames on one slot are `TEMPORALLY_INCOMPARABLE`: neither
  overlapping, nor disjoint, nor conflicting, nor superseding (`UNRELATED_TEMPORAL_FRAMES_CAN_COEXIST
  =YES`, `INCOMPARABLE_FRAME_CLAIMS_AUTO_CONFLICT=NO`). Under T6 this means a slot carries current
  PROMOTED claims in at most one frame at a time.
- `CLOCK_DOMAIN != TEMPORAL_FRAME_REF`: `clock_domain` qualifies recorded / source / observed
  timestamps; `temporal_frame_ref` qualifies valid_time and query time. A shared clock_domain proves
  neither valid-time / world-time comparability nor causality.
- In V1 a gap scope is partitioned only along `valid_time` (the slot is fixed); no exact comparable
  difference → the partition request is REJECTED `temporal_relation_indeterminate` (no approximation).
- `UNKNOWN_VALUE != TEMPORAL_RELATION_UNKNOWN`: knowing claims A and B while their temporal relation is
  indeterminate is a temporal indeterminacy, not an EpistemicGap about A or B (none is created
  unless explicitly recorded).
- These structures are provisional contract-level forms that must stay mappable to the future
  MMonde / F12 TimeEnvelope; B8 implements neither TimeEnvelope nor transform admission and creates no
  universal clock (`TEMPORAL_FRAME_COMPATIBILITY_WITH_MMONDE=YES`, `B8_COMPETING_GLOBAL_TIME_SUBSYSTEM=NO`).
- **B8-DT01 TEMPORAL_TRANSFORM_ADMISSION** (DEFERRED_NON_BLOCKING): a future temporal layer / MMonde may
  define transform authority, typed verifier, direction, invertibility, composition, versioning,
  validity, uncertainty, revocation and receipts; only after that contract is independently proven
  may a future B8 version consume cross-frame temporal relations.

### 5.2 Slot state and concurrency (D-B8-R2-3, D-B8-R3-3)

Each KnowledgeSlot has exactly one logical `SlotState{slot_id, slot_revision}`,
initial revision 0, shared by **claim and gap** transitions on that slot (no separate claim / gap
revision). Every APPLIED operation changing canonical B8 state on the slot — T1–T12 and G1–G4 —
increments `slot_revision` by exactly 1; a T9 bundle and a G4 bundle each increment it exactly
once; REJECTED, NO_OP_DUPLICATE and read-only queries never increment
(`GAP_TRANSITION_SLOT_REVISION_EFFECT=INCREMENT_ON_APPLIED`). Every mutating request (claim or
gap) binds `slot_id` + `expected_slot_revision`; the gate checks the object versions / states and
the slot revision against one canonical snapshot and applies atomically; any mismatch → REJECTED
`stale_request`. A claim request and a gap request prepared on the same revision can never both
apply (`CLAIM_GAP_SAME_REVISION_DOUBLE_APPLY=0`). Locks, transactions,
database CAS or a single writer are implementation mechanisms; the semantic contract is the
expected slot revision. Two requests prepared on the same revision can never both apply:
`CONCURRENT_T6_DOUBLE_PROMOTION=0`, `T6_T9_RACE_DOUBLE_PROMOTION=0`,
`CONCURRENT_T9_CONFLICT_ACCEPTED=0`.

### 5.3 Logical ordering and anti-backdating (D-B8-R2-2, D-B8-R3-3, temporal doctrine 2026-10-07)

`ONE_SHARED_SLOT_REVISION=YES` · `ONE_SHARED_CLOCK=NO` · `RECORDED_AT_CANONICAL_ORDER_AUTHORITY=NO`.

- `slot_revision` = per-KnowledgeSlot canonical mutation serialization revision + optimistic
  concurrency token. It answers only "which B8 mutation on this slot was committed before another
  on the same slot". It is not a clock, physical or world time, causality, confidence, truth score
  or authority (`SLOT_REVISION_IS_CLOCK=NO`, `SLOT_REVISION_IS_PHYSICAL_TIME=NO`,
  `SLOT_REVISION_IS_CAUSALITY=NO`, `SLOT_REVISION_GRANTS_EPISTEMIC_WEIGHT=NO`). It is local to one
  slot: revisions of different slots are never compared and no global "latest revision" exists
  (`CROSS_SLOT_REVISION_NUMERIC_ORDERING=FORBIDDEN`).
- `record_version` / `gap_version` = local immutable history order of one claim / one gap lineage;
  neither global logical time nor causality.
- Record links (`previous_record_id`, `previous_gap_record_id`, supersedes, resolution links) are
  history / lineage links, not causal claims. Causality exists only through an explicit typed causal
  relation (or a future causal verifier), never through slot_revision, versions, recorded_at,
  source_time or valid_time (`SERIALIZATION_IMPLIES_CAUSATION=NO`); two events committed in
  sequence may be `INCOMPARABLE_CAUSALLY` (valid). An explicit admissible causal relation X → Y is
  never discarded because raw timestamps from other frames look reversed
  (`TIMESTAMP_OVERRIDES_CAUSAL_LINK=NO`); such an inconsistency may be recorded separately.
- Canonical B8 history order is never the numerical order of `recorded_at`, and the order in which
  Obsidia receives, records or commits information never implies world order or causal order.
- Backdating = attempting to insert or rewrite a logical transition before an already committed
  causal / revision predecessor. It is prevented structurally: every mutating request binds
  `expected_slot_revision` and its object's expected version / state (§5.2, §9.1), so a request can
  only append after the current revision; any other request → REJECTED `stale_request`. A history is
  append-only in revision order (`RECORDED_HISTORY_IS_APPEND_ONLY_IN_LOGICAL_ORDER`).
- A numerically smaller `recorded_at` is not backdating by itself
  (`CROSS_CLOCK_NUMERIC_COMPARISON_FORBIDDEN=YES`): timestamps from different clock domains are
  not compared. Only when the request and the predecessor carry the same trusted `clock_domain` may
  a monotonic check (`recorded_at ≥` predecessor's `recorded_at` in that domain) be applied as an
  additional consistency invariant → REJECTED `backdated_record`; it never defines canonical order.
- `valid_time` may lie anywhere (a past world fact recorded today is admissible).
- A bundle (T9, G4) is one logical step: one slot_revision increment; its timestamps follow the
  same rules.

## 6. Claim classes and verifier policy (O-2)

| ClaimClass | Admissible verifier family | requires_human_review (T6) | Staleness mechanism (O-3) |
|---|---|---|---|
| FORMAL_CLAIM | FORMAL_PROOF_VERIFIER | false | NEVER_BY_TIME (+ SOURCE_VERSION_CHANGE of assumptions) |
| CODE_BUILD_CLAIM | TEST_BUILD_PROOF_VERIFIER | false | SOURCE_VERSION_CHANGE |
| PHYSICAL_CLAIM | PROVENANCE_PLUS_REALITY_VERIFIER | false | DOMAIN_POLICY / VALID_UNTIL |
| DOCUMENTARY_CLAIM | SOURCE_PROVENANCE_VERIFIER | false | SOURCE_VERSION_CHANGE / VALID_UNTIL |
| DOMAIN_CLAIM | TYPED_DOMAIN_VERIFIER (per domain contract) | per domain contract | DOMAIN_POLICY |
| HUMAN_DECLARATION | HumanAttestation PRIMARY_DECLARATION | true | CONDITION_TRIGGER (revocation) / VALID_UNTIL |
| ORGANIZATIONAL_POLICY | authorized HumanAttestation PRIMARY_DECLARATION | true | CONDITION_TRIGGER / VALID_UNTIL |

- `requires_human_review` is explicit policy data per class (or per audited domain contract). It
  never derives from confidence, majority, LLM recommendation, recency or provider identity.
- PRIMARY_DECLARATION (evidence, T5) and REVIEW_AUTHORIZATION (T6) are distinct attestation
  kinds: one attestation never satisfies both.
- A human attestation never verifies an objective class (FORMAL, CODE_BUILD, PHYSICAL,
  DOCUMENTARY, DOMAIN): for those it may only satisfy a REVIEW_AUTHORIZATION precondition.
- New claim classes / domains extend the registry only through an explicit audited contract.
- Staleness mechanisms (closed set): NEVER_BY_TIME, TTL, SOURCE_VERSION_CHANGE, VALID_UNTIL,
  CONDITION_TRIGGER, DOMAIN_POLICY. No generic duration is encoded in B8; TTL values come only from
  an audited domain contract. STALE requires explicit trigger evidence. Re-verification (T12)
  never changes scope or valid_time: those are part of the claim and require a new claim_version.

## 7. Human identity (O-5)

An attestation is admissible only if `identity_source` is a trusted identity / auth boundary
recorded by reference (`auth_context_ref`). A display name or any candidate-supplied identity is
never sufficient. Until such a boundary is wired, every attestation is inadmissible for a
transition that requires it → that transition is REJECTED `attestation_inadmissible` and the claim
keeps its current state (e.g. stays VERIFIED). B8 does not implement IAM.

## 8. States (epistemic only)

| State | Meaning | Current admissible knowledge? |
|---|---|---|
| CANDIDATE | captured proposal, no standing | no |
| HELD | review / edit / evidence / identity pending | no |
| REJECTED | refused with reasons (terminal for this claim) | no |
| SUPPORTED | admissible typed evidence, not verified | no |
| VERIFIED | SATISFIED record of an admissible verifier family for this (claim_id, claim_version) | no (not yet promoted) |
| PROMOTED | admissible current knowledge under scope, evidence, verification policy, version, provenance, history — only while it is the latest state (§10) | **yes** |
| CONTESTED | admissible contradiction open | **no** — consumers receive it as explicit uncertainty with both sides' refs; never as trusted knowledge, never with a winner |
| SUPERSEDED | replaced by a newer claim on the same slot / overlapping time (terminal, history kept) | no (historical) |
| INVALIDATED | explicitly withdrawn with reasons (terminal, history kept) | no |
| STALE | staleness trigger fired; needs re-verification | no — exposed as stale |

Memory lifecycle states (ACTIVE, SEMI_ACTIVE, COLD, GHOST…) are retrieval / storage concerns
(B9 / B10) and are never B8 states: `EPISTEMIC_STATUS_MEMORY_STATUS_COLLAPSE=0`.

### 8.1 EpistemicGap (O-1, D-B8-S5)

Records "we do not currently know X": UNKNOWN(X) != FALSE(X) != VERIFIED(X) != PROMOTED(X). It is
never a `KnowledgeClaim`, never enters T1–T12, and never becomes positive knowledge.
Authority: `B8_CANONICAL_TRANSITION_GATE` only (no agent, human or LLM authority).

| # | From → To | Preconditions |
|---|---|---|
| G1 | ∅ → OPEN | well-formed gap (slot, valid_time, reason, provenance) ; idempotent on gap_id |
| G2 | OPEN → RESOLVED (full coverage) | `promoted_claim_id` + `promoted_record_id` whose latest state (§10) is PROMOTED, same slot_id, typed resolution relation, claim valid_time **contains** the gap valid_time, expected_slot_revision, reason; every temporal relation used here requires `TEMPORALLY_COMPARABLE` (§5.1), else REJECTED `temporal_relation_indeterminate` (state unchanged) |
| G3 | OPEN → SUPERSEDED, reason GAP_REFRAMED | `successor_gap_id` of an OPEN gap on the same slot_id and the same `temporal_frame_ref` (V1) whose valid_time **contains** the old gap's, reason; every temporal relation used here requires `TEMPORALLY_COMPARABLE` (§5.1), else REJECTED `temporal_relation_indeterminate` (state unchanged) |
| G4 | compound GapPartitionBundle, reason PARTIAL_RESOLUTION | PROMOTED claim (latest state, same slot, typed resolution relation, expected_slot_revision) whose valid_time overlaps but does not contain the gap's: old gap OPEN → SUPERSEDED, resolved sub-interval (gap ∩ claim) linked to the claim, residual gaps = `difference(gap, claim)` created OPEN (§5.1); every temporal relation used here requires `TEMPORALLY_COMPARABLE` (§5.1), else REJECTED `temporal_relation_indeterminate` (state unchanged) |

Every gap transition uses `GapTransitionRequest` (gap_id, expected_gap_state, expected_gap_version,
target_state, refs, reason, slot_id, expected_slot_revision — G1–G4 alike) → new immutable gap
record(s) + `GapTransitionReceipt`(s) (verdict enum identical to claims: APPLIED / REJECTED /
NO_OP_DUPLICATE); CAS, idempotency (NO_OP_DUPLICATE with the original
receipt / bundle), stale request rejection, logical anti-backdating (§5.3) and append-only history as in
§9.1. Every other pair fails closed; RESOLVED and SUPERSEDED are terminal; no gap state is a claim
state. A partial resolution never marks the whole gap RESOLVED
(`PARTIAL_COVERAGE_CAN_FULLY_RESOLVE_GAP=NO`); the receipt reason distinguishes GAP_REFRAMED from
PARTIAL_RESOLUTION.

**GapPartitionBundle (G4, atomic)**: original_gap_id, original_gap_record_id, resolving_claim_id,
resolving_promoted_record_id, resolved_scope, residual_gap_records[], old_gap_transition_receipt,
new_gap_receipts[], recorded_at, gate_contract_version, bundle_digest. Invariants: original scope =
resolved scope ∪ residual scopes; resolved ∩ residuals = ∅; residuals pairwise disjoint. All or
nothing: never the old gap SUPERSEDED without its residuals, residuals while the old gap stays OPEN,
a linked resolved segment without the partition, or residuals that do not rebuild the original
scope (`GAP_PARTITION_ATOMIC=YES`, `UNCERTAINTY_COVERAGE_LOSS=0`). Example: gap [0,10) and PROMOTED
claim [5,6) → old gap SUPERSEDED, [5,6) linked to the claim, new OPEN gaps [0,5) and [6,10).

Intentional asymmetry: unknown space is partitioned (uncertainty must be preserved); positive claims
are never auto-partitioned (that would manufacture knowledge artifacts) — T9 fails closed instead.

## 9. Legal transitions (the only ones)

### 9.1 Common contract

**Verdict vs state (D-B8-SA2-1).** `TRANSITION_VERDICT_ENUM = APPLIED | REJECTED | NO_OP_DUPLICATE`
for claim and gap receipts alike. HELD is a claim **state** only (reached through T2), never a verdict
(`HELD_IS_TRANSITION_VERDICT=NO`; VERDICT != STATE != REASON; FAIL_CLOSED_REQUEST !=
STATE_TRANSITION_TO_HELD). Only APPLIED mutates canonical state. A REJECTED request carries a canonical
reason (e.g. `stale_request`, `temporal_relation_indeterminate`, `attestation_inadmissible`,
`MULTIPLE_PREDECESSORS_UNSUPPORTED`) and leaves claim / gap state, record_version, gap_version and
slot_revision unchanged; it writes no record.

Every request binds claim_id, expected_claim_version, expected_state, expected_record_version,
slot_id, expected_slot_revision and target_state (compare-and-set against one canonical snapshot,
§5.2; mismatch → REJECTED `stale_request`; same-clock-domain monotonic violation → REJECTED
`backdated_record`, §5.3), a
reason, and refs re-hashed and bound to `(claim_id, claim_version)`. An applied transition
produces exactly one new immutable `KnowledgeRecord` (`record_version + 1`) and one
`TransitionReceipt` (T9: one bundle, §9.3). An identical request already applied →
NO_OP_DUPLICATE with the original receipt / bundle; an old receipt never re-applies.

### 9.2 Rules

| # | From → To | Preconditions |
|---|---|---|
| T1 | ∅ → CANDIDATE | well-formed claim (§4, §5); idempotent on claim_id |
| T2 | CANDIDATE → HELD | explicit hold reason |
| T3 | CANDIDATE / HELD → REJECTED | explicit reasons |
| T4 | CANDIDATE / HELD → SUPPORTED | ≥1 admissible EvidenceRef with complete provenance |
| T5 | SUPPORTED → VERIFIED | VerificationRecord SATISFIED, verifier family admissible for the class (§6), bound to (claim_id, claim_version); human classes: admissible PRIMARY_DECLARATION attestation (§7) |
| T6 | VERIFIED → PROMOTED (free slot) | expected_slot_revision current; no claim whose latest state is PROMOTED on the same slot with overlapping valid_time; no open contradiction; REVIEW_AUTHORIZATION attestation admissible when `requires_human_review`; every temporal relation used here requires `TEMPORALLY_COMPARABLE` (§5.1), else REJECTED `temporal_relation_indeterminate` (state unchanged) |
| T7 | SUPPORTED / VERIFIED / PROMOTED → CONTESTED | admissible contradicting evidence or claim recorded with refs; a claim in another temporal frame may be referenced (`CROSS_FRAME_REFERENCE_ALLOWED=YES`) but a contradiction that depends on temporal overlap / order across frames is never inferred (`CROSS_FRAME_TEMPORAL_CONTRADICTION_INFERRED=NO`) |
| T8 | CONTESTED → SUPPORTED | contradiction explicitly resolved (contradicting side INVALIDATED / REJECTED or new verification refs); never by confidence or recency; T5 and T6 required again |
| T9 | compound: new VERIFIED → PROMOTED **and** predecessor PROMOTED → SUPERSEDED | request carries `supersedes_claim_id` + `supersedes_record_id` + expected_slot_revision identifying exactly the predecessor whose latest state is PROMOTED on the same slot; it is the **only** PROMOTED claim on the slot overlapping the new valid_time (else REJECTED `MULTIPLE_PREDECESSORS_UNSUPPORTED`: no winner, no repeated T9); the new valid_time **contains** the predecessor's (partial overlap → REJECTED; no implicit claim split in V1); the new claim meets every T6 condition except the free-slot one; atomic bundle (§9.3), slot_revision +1 once; every temporal relation used here requires `TEMPORALLY_COMPARABLE` (§5.1), else REJECTED `temporal_relation_indeterminate` (state unchanged) |
| T10 | CANDIDATE / HELD / SUPPORTED / VERIFIED / PROMOTED / CONTESTED / STALE → INVALIDATED | explicit reason + evidence ref |
| T11 | PROMOTED → STALE | staleness trigger evidence per class mechanism (§6) |
| T12 | STALE → VERIFIED | fresh SATISFIED VerificationRecord for the same (claim_id, claim_version); T6 / T9 again to PROMOTED |

`LEGAL_TRANSITION_COUNT=12` claim rules (T9 compound) + 4 gap rules (G1–G3, G4 compound).
Claim (from, to) pairs: 22 (T9 contributes VERIFIED → PROMOTED on the new claim and PROMOTED →
SUPERSEDED on the predecessor, both only inside one bundle) ; gap pairs: 3 (∅ → OPEN, OPEN → RESOLVED,
OPEN → SUPERSEDED; G4 = OPEN → SUPERSEDED + ∅ → OPEN residuals inside one bundle).

### 9.3 SupersessionTransitionBundle (T9 atomic result)

Fields: bundle_id, request_id, old_claim_id, old_from_record_id, old_to_record_id, new_claim_id,
new_from_record_id, new_to_record_id, old_transition_receipt, new_transition_receipt,
supersedes_link (new → old), superseded_by_link (old → new), recorded_at, gate_contract_version,
bundle_digest.

All-or-nothing: the gate either returns the complete bundle (both new records, both receipts, both
links) or REJECTED with no new record. No valid outcome exposes two claims whose latest state is
PROMOTED on the same slot / overlapping time, nor a SUPERSEDED predecessor without a PROMOTED
successor, nor a one-way link. Idempotency and replay apply to the whole bundle.

**Current uniqueness**: with slot-revision CAS, T6 free-slot, atomic single-predecessor T9 and full
predecessor coverage, for every (slot, query frame, query_time, as_of_slot_revision) at most one claim **temporally comparable to the query frame** is current
PROMOTED (`CURRENT_PROMOTED_CARDINALITY_PER_SLOT_TIME ≤ 1`); zero means explicitly not known. Never
chosen by confidence, recency, majority or provider priority.

### 9.4 Forbidden complement (fail closed)

Every (from, to) pair not listed above, in particular: CANDIDATE → VERIFIED / PROMOTED, HELD →
VERIFIED / PROMOTED, SUPPORTED → PROMOTED, REJECTED → any, STALE → PROMOTED, INVALIDATED → any,
SUPERSEDED → any (never current again; a new claim_version is required), CONTESTED → VERIFIED /
PROMOTED, VERIFIED → PROMOTED on an occupied slot outside a T9 bundle, PROMOTED → SUPERSEDED
outside a T9 bundle, any gap state → any claim state, any transition caused by confidence,
majority, provider priority, recency or a human approval alone on an objective class, any direct
`record.state = …` outside construction, any overwrite.

## 10. Point-in-time contract (D-B8-S1)

History is append-only in logical order: records, receipts and bundles are immutable, linked by
`previous_record_id`, `previous_gap_record_id`, supersedes / superseded_by and resolution links.
World time (`valid_time`) and history position are separate dimensions; history position is the
logical cutoff `as_of_slot_revision`, not a timestamp.

- `LATEST_EPISTEMIC_STATE(claim_id, as_of_slot_revision)` = state of the claim's last record (highest
  record_version) among records committed at slot_revision ≤ `as_of_slot_revision`.
- `KNOWLEDGE_STATE_AS_OF_REVISION(R)` = for each claim of the slot, `LATEST_EPISTEMIC_STATE(claim_id,
  R)` (historical replay: "what did the slot hold after revision R").
- A timestamp cutoff ("as recorded at T") is a derived convenience, admissible only inside one
  declared `clock_domain`: it maps T to the last revision whose `recorded_at` in that domain is ≤ T,
  and is never compared across clock domains.
- `CURRENT_KNOWLEDGE(slot, query_time, as_of_slot_revision)` (query_time = `TemporalPoint`; no naked
  scalar world time, `WORLD_TIME_REQUIRES_TEMPORAL_FRAME=YES`) = claims such that the slot matches,
  `valid_time` is temporally comparable to query_time and contains it, and `LATEST_EPISTEMIC_STATE(claim_id, as_of_slot_revision)
  = PROMOTED`. A later CONTESTED / STALE / INVALIDATED / SUPERSEDED record removes the claim;
  historical PROMOTED records are never scanned as independently current.
- "Current now" uses `as_of_slot_revision` = the slot's current revision, passed explicitly to the
  deterministic core.

No destructive overwrite. Durable storage of this history is B10.

### 10.1 Current epistemic view (D-B8-R3-1, D-B8-R3-2)

`RECORDED_GAP_STATE != EFFECTIVE_CURRENT_UNCERTAINTY`. Gap and claim records are history; the
current view is a deterministic projection, never a write.

`CURRENT_EPISTEMIC_VIEW(slot_id, query_time, as_of_slot_revision)` (query_time frame-qualified)
returns `current_promoted_coverage`, `current_unknown_coverage`, `current_contested_refs`,
`current_stale_refs`, `current_gap_refs`, `temporal_indeterminate_refs` (query output only, no
state effect), `snapshot_revision`, all derived from one slot history
cutoff `as_of_slot_revision` (`MIXED_SLOT_SNAPSHOT_ALLOWED=NO`).

- Claims / gaps whose valid_time is not temporally comparable to the query frame are neither known
  nor unknown nor ignored: they are listed under `temporal_indeterminate_refs`
  (TEMPORALLY_INDETERMINATE_FOR_QUERY). All coverage arithmetic below happens in the query frame only
  (`CURRENT_VIEW_CROSS_FRAME_FUSION=0`).
- `CURRENT_PROMOTED_COVERAGE` = union of valid_time of comparable claims whose latest state at the cutoff is
  PROMOTED (≤ 1 claim per instant, §9.3).
- Resolution links (G2: whole gap; G4: resolved sub-interval) keep their exact support (gap
  lineage / segment, claim_id, promoted_record_id, resolved scope); they are immutable history.
- `EXPLICIT_UNKNOWN_BASE` = union over the slot's gap lineages of: OPEN gap scopes (residuals of
  G4 included) and RESOLVED / partition-resolved segments. Excluded: gap scopes SUPERSEDED by a
  successor lineage that represents them (G3 successor, G4 residuals + resolved segment), so no
  ancestor coverage is counted twice.
- `CURRENT_UNKNOWN_COVERAGE = EXPLICIT_UNKNOWN_BASE − CURRENT_PROMOTED_COVERAGE` (exact interval
  difference, §5.1; if not exactly derivable → the query reports TEMPORALLY_INDETERMINATE, never a
  guess). A resolved segment is therefore unknown again exactly when no current PROMOTED claim
  covers it (support INVALIDATED / STALE / CONTESTED), and stays known when a valid successor
  covers it (supersession does not recreate unknown).
- Invariant: `CURRENT_PROMOTED_COVERAGE ∩ CURRENT_UNKNOWN_COVERAGE = ∅`
  (`KNOWN_UNKNOWN_EFFECTIVE_OVERLAP=0`) for one snapshot. Precedence is a projection: current
  admissible PROMOTED knowledge masks explicit gap uncertainty only over the coverage it supports.
- `NOT_KNOWN != KNOWN_UNKNOWN` (no closed-world assumption): unknown coverage comes only from an
  explicit gap lineage. No gap lineage and no knowledge → `NO_ASSERTION` (view result only, not a
  state). `CURRENT_UNKNOWN_COVERAGE != UNIVERSE − CURRENT_KNOWN`.
- `CONTESTED != UNKNOWN`: a contested claim stays visible in `current_contested_refs`; its scope
  may also appear in `current_unknown_coverage` when an explicit gap lineage covers it.
- No automatic cross-object write: a claim state change never creates or mutates a gap record
  (`SUPPORT_STATE_CHANGE_MUTATES_GAP=NO`); gap history changes only through explicit G1–G4 with
  receipts. Gap artifacts and PROMOTED claims may coexist on overlapping scope
  (`ARTIFACT_GAP_PROMOTED_COEXISTENCE=ALLOWED`); G2 / G4 are explicit normalizations that change
  recorded representation, not current meaning
  (`G4_NORMALIZATION_CHANGES_CURRENT_EPISTEMIC_MEANING=NO`).

Examples: gap [0,10) G2-resolved by C [0,10) → KNOWN [0,10), UNKNOWN ∅; C later INVALIDATED (no
gap write) → KNOWN ∅, UNKNOWN [0,10); C superseded by PROMOTED C2 [0,10) → KNOWN [0,10), UNKNOWN ∅.
OPEN gap [0,10) + PROMOTED [4,6) → KNOWN [4,6), UNKNOWN [0,4) ∪ [6,10), identical before and after
an explicit G4.

## 11. Boundaries

- **B7 → B8**: a B7 ACCEPT may only seed a T1 CANDIDATE through a future typed B8 intake that
  consumes an issued result (`admit_trusted_context`); never SUPPORTED / VERIFIED / PROMOTED. That
  implementation imports `app.cognition` → Sentinel `NEW_B7_IMPORTER` / `NEW_TRUST_SINK_CALLER`
  → B7 security epoch-1 re-audit required (the baseline is not changed by this spec).
- **B8 → B10**: PROMOTED != durable write; B8 emits epistemic state and transition artifacts
  only. B10 decides persistence; the actual write is a state-changing operation governed through
  the Binder / KX108 action boundary.
- **KX108**: no role in B8 transitions. **Verifiers**: records only, no state change, no authority.

## 12. Existing mechanisms (forensic → decision)

| Mechanism | Decision | Mapping |
|---|---|---|
| `periphery/memory` status enum | ADAPT | CAPTURED / HASHED / CANDIDATE_ONLY → CANDIDATE ; NEEDS_REVIEW / FROZEN → HELD ; REJECTED → REJECTED ; PROMOTION_READY → HELD (legacy status set by direct assignment with no VerificationRecord: behaviorally not VERIFIED) ; PROMOTED_MANUAL_ONLY → no canonical equivalent (superseded by PROMOTED via the gate) |
| `MemoryCandidate.status` free assignment | SUPERSEDE | gate transitions only |
| `memory_promotion_policy.evaluate_promotion_policy` | SUPERSEDE | the B8 gate is the only promotion engine |
| `memory_candidate_ledger` | ADAPT | T1 capture log, idempotent on claim_id |
| Brody V3 Block 3A–3C (trace, candidate, education, replay) | ADAPT | proposal inputs to T1 only |
| Block 3D human validation gate (dry run) | ADAPT | outcomes map to claim states HELD (via T2) or REJECTED (via T3) with their reasons; never promotion, never attestation |
| `brody_memory_promotion_guard` | ADAPT | advisory readiness only, outside policy decisions |
| native memory reader | KEEP | read path, no state authority |
| Neo4j CLI manual apply (2 modules) | SUPERSEDE_BEFORE_CANONICAL_RUNTIME_WRITE | D-5 |
| native index migration script | HOLD | operator migration artifact; not a promotion route |
| Brody answer templates citing GATE_001..006 | SUPERSEDE | describe nonexistent gates |

No duplicate promotion engine survives canonical B8.

## 13. Audit record

- 2026-10-07 draft 2e2fbf6f, self-review corrections, self-closed cc22638b.
- Independent certification of cc22638b: REMEDIATE_SPEC — D-B8-S1 current query scanned historical
  PROMOTED records; D-B8-S2 claim / record version undefined; D-B8-S3 T6 free-slot rule
  contradicted T9 and T9 had no atomic result; D-B8-S4 slot canonicalization incomplete
  (duplicates, Unicode, empty refs); D-B8-S5 gap transitions without actor / receipt; bounds
  wording overstated.
- Remediation 02ec2c64: §10 latest-state queries; §4.1 version model and CAS fields; T6
  free-slot + T9 compound rule with §9.3 bundle; §5 canonicalization; §8.1 gap rules G1–G3;
  §3 bounds wording. Status back to DRAFT_FOR_AUDIT pending independent re-certification.
- Normalization 17730492 (docs only, no semantic change): history line moved out of the active status
  block into this record; header BASE line reworded so the active block carries no CLOSED token.
- Independent certification R2 of 17730492: S1–S5 confirmed fixed; REMEDIATE_SPEC for D-B8-R2-1
  (gap resolved by partial overlap), D-B8-R2-2 (backdatable recorded_at), D-B8-R2-3 (no slot-level
  CAS). Remediation: §5.1 interval algebra, §5.2 slot_revision CAS, §5.3 non-backdating, G2 / G3
  containment + G4 GapPartitionBundle, T9 single predecessor + full predecessor coverage,
  empty-collection policy, current-uniqueness invariant. Status stays DRAFT_FOR_AUDIT.
- Independent certification R3 of 49db9da1: S1–S5, R2-1..R2-3 confirmed; REMEDIATE_SPEC for
  D-B8-R3-1 (uncertainty vanished when a resolving claim left PROMOTED), D-B8-R3-2 (known and unknown
  overlapping with no view rule), D-B8-R3-3 (gap transitions did not advance the slot clock /
  revision). Remediation (human doctrine: derived current-unknown view, no automatic gap reopen;
  artifact coexistence with view masking; one shared slot revision and clock): §5.2, §5.3, §8.1
  request fields, §10.1 current epistemic view. Status stays DRAFT_FOR_AUDIT.
- Doctrine correction (human, 2026-10-07, temporal model): no universal / shared physical clock.
  `ONE_SHARED_SLOT_REVISION=YES`, `ONE_SHARED_CLOCK=NO`, `RECORDED_AT_CANONICAL_ORDER_AUTHORITY=NO`,
  `CROSS_CLOCK_NUMERIC_COMPARISON_FORBIDDEN=YES`; logical order = slot_revision / record_version /
  causal predecessor; temporal fields separated (valid, source / observed, recorded, clock_domain,
  proof / anchor) and kept mappable to MMonde / F12 TimeEnvelope. SlotState no longer carries
  last_recorded_at; point-in-time queries use as_of_slot_revision; recorded_at monotonicity is only an
  optional same-clock-domain consistency check. Status stays DRAFT_FOR_AUDIT.
- Independent temporal certification R4 of 29038af0: REMEDIATE_SPEC for D-B8-R4-1 (valid_time on an
  implicit universal scale), D-B8-R4-2 (frame-less world_time queries), D-B8-R4-3 (serialization /
  version order not separated from causality; cross-slot revision comparison not forbidden).
  Remediation: §2 temporal laws, §5.1 TemporalFrameRef / ValidTimeInterval / TemporalTransformRef /
  TEMPORALLY_COMPARABLE with INDETERMINATE fail-closed, frame outside slot identity, T6 / T9 / G2 /
  G3 / G4 comparability guards, §5.3 serialization vs causality, §9.3 / §10 / §10.1 frame-qualified
  queries and view. Status stays DRAFT_FOR_AUDIT.
- Independent temporal certification R5 of 03c31d48: REMEDIATE_SPEC for D-B8-R5-1 (transform direction /
  composition / cycles undefined), D-B8-R5-2 (transform version not bound to transitions / replay),
  D-B8-R5-3 (transform admissibility authority undefined). Human doctrine: B8 V1 admits no cross-frame
  transform; same-frame comparisons only; TemporalTransformRef reserved (B8-DT01 deferred). Remediation:
  §2 world-order laws, §5.1 V1 comparability rule, reserved transform, receipt comparison basis,
  indeterminacy semantics, §5.3 reception / commit order != world order. Status stays DRAFT_FOR_AUDIT.
- Second independent audit (separate agent, own oracle 14680 cases) of a52990a9: REMEDIATE_SPEC for
  D-B8-SA2-1 — "HELD" used as a fail-closed outcome while the verdict enum had no HELD and VERIFIED →
  HELD was illegal (773 ambiguous T6 cases). Remediation: §9.1 verdict vs state, all fail-closed
  outcomes = REJECTED with canonical reason and no state change, gap receipt enum aligned, view field
  `temporal_indeterminate_refs`, G3 same-frame successor, CLOCK_DOMAIN != TEMPORAL_FRAME_REF, T7
  cross-frame reference without inferred temporal contradiction, one-frame-per-slot consequence of T6
  stated. Status stays DRAFT_FOR_AUDIT.
