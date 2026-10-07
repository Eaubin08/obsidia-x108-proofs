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
DECISION_AUTHORITY=KX108_ONLY.

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
| `TransitionRequest` | claim_id, expected_claim_version, expected_state, expected_record_version, target_state, refs, (T9 only) supersedes_claim_id + supersedes_record_id, requester ref, reason |
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

`recorded_at` is an input supplied to the gate (injected clock), never read by the gate itself:
the gate stays deterministic. Confidence is descriptive data inside evidence; it is never a
sufficient precondition and never part of a policy decision.

## 5. Scope and slots (O-4, D-B8-S4)

`CONTENT != SCOPE != PROVENANCE`. Scope = `KnowledgeScope{subject_refs, context_refs, domain_id,
valid_time}`; sources and evidence are provenance, never scope.

Slot canonicalization (applied before hashing; any violation → REJECT):

1. Every textual component (domain_id, predicate_ref, each subject / context ref) must be a
   string, normalized to Unicode NFC; empty or whitespace-only strings and non-strings are
   rejected. No other normalization (no case folding, no trimming beyond the rejection rule).
2. `subject_refs` and `context_refs` are **unordered sets**: normalize each, reject empty,
   deduplicate exact normalized values, sort by code point.
3. `KnowledgeSlot` = `b8slot_` + SHA-256(canonical_json([claim_class, domain_id,
   subject_set, context_set, predicate_ref])) — full 256 bits.

Hence ref order, duplicates and Unicode-equivalent forms never change the slot id. A domain that
needs ordered participants puts that order in typed claim content, never in the slot sets.

`valid_time` stays outside the slot:

- same slot, non-overlapping valid_time → historical coexistence;
- same slot, overlapping valid_time, different admissible successor → T9 supersession only;
- different context / domain → different slot, never fused.

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
transition that requires it → the claim stays HELD. B8 does not implement IAM.

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
| G2 | OPEN → RESOLVED | `promoted_claim_id` + `promoted_record_id` whose latest state (§10) is PROMOTED, same slot_id, valid_time overlapping the gap's, reason |
| G3 | OPEN → SUPERSEDED | `successor_gap_id` of an OPEN gap on the same slot_id with overlapping valid_time, reason |

Every gap transition uses `GapTransitionRequest` (gap_id, expected_gap_state, expected_gap_version,
target_state, refs, reason) → new immutable gap record + `GapTransitionReceipt`; CAS, idempotency
(NO_OP_DUPLICATE), stale request rejection and append-only history as in §9.1. Every other pair
fails closed; RESOLVED and SUPERSEDED are terminal; no gap state is a claim state.

## 9. Legal transitions (the only ones)

### 9.1 Common contract

Every request binds claim_id, expected_claim_version, expected_state, expected_record_version and
target_state (compare-and-set against the latest record; mismatch → REJECTED `stale_request`), a
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
| T6 | VERIFIED → PROMOTED (free slot) | no claim whose latest state is PROMOTED on the same slot with overlapping valid_time; no open contradiction; REVIEW_AUTHORIZATION attestation admissible when `requires_human_review` |
| T7 | SUPPORTED / VERIFIED / PROMOTED → CONTESTED | admissible contradicting evidence or claim recorded with refs |
| T8 | CONTESTED → SUPPORTED | contradiction explicitly resolved (contradicting side INVALIDATED / REJECTED or new verification refs); never by confidence or recency; T5 and T6 required again |
| T9 | compound: new VERIFIED → PROMOTED **and** predecessor PROMOTED → SUPERSEDED | request carries `supersedes_claim_id` + `supersedes_record_id` identifying exactly the predecessor whose latest state is PROMOTED on the same slot with overlapping valid_time; the new claim meets every T6 condition except the free-slot one; atomic bundle (§9.3) |
| T10 | CANDIDATE / HELD / SUPPORTED / VERIFIED / PROMOTED / CONTESTED / STALE → INVALIDATED | explicit reason + evidence ref |
| T11 | PROMOTED → STALE | staleness trigger evidence per class mechanism (§6) |
| T12 | STALE → VERIFIED | fresh SATISFIED VerificationRecord for the same (claim_id, claim_version); T6 / T9 again to PROMOTED |

`LEGAL_TRANSITION_COUNT=12` claim rules (T9 compound) + 3 gap rules (G1–G3).
Claim (from, to) pairs: 22 (T9 contributes VERIFIED → PROMOTED on the new claim and PROMOTED →
SUPERSEDED on the predecessor, both only inside one bundle) ; gap pairs: 3.

### 9.3 SupersessionTransitionBundle (T9 atomic result)

Fields: bundle_id, request_id, old_claim_id, old_from_record_id, old_to_record_id, new_claim_id,
new_from_record_id, new_to_record_id, old_transition_receipt, new_transition_receipt,
supersedes_link (new → old), superseded_by_link (old → new), recorded_at, gate_contract_version,
bundle_digest.

All-or-nothing: the gate either returns the complete bundle (both new records, both receipts, both
links) or REJECTED with no new record. No valid outcome exposes two claims whose latest state is
PROMOTED on the same slot / overlapping time, nor a SUPERSEDED predecessor without a PROMOTED
successor, nor a one-way link. Idempotency and replay apply to the whole bundle.

### 9.4 Forbidden complement (fail closed)

Every (from, to) pair not listed above, in particular: CANDIDATE → VERIFIED / PROMOTED, HELD →
VERIFIED / PROMOTED, SUPPORTED → PROMOTED, REJECTED → any, STALE → PROMOTED, INVALIDATED → any,
SUPERSEDED → any (never current again; a new claim_version is required), CONTESTED → VERIFIED /
PROMOTED, VERIFIED → PROMOTED on an occupied slot outside a T9 bundle, PROMOTED → SUPERSEDED
outside a T9 bundle, any gap state → any claim state, any transition caused by confidence,
majority, provider priority, recency or a human approval alone on an objective class, any direct
`record.state = …` outside construction, any overwrite.

## 10. Point-in-time contract (D-B8-S1)

History is append-only: records, receipts and bundles are immutable, linked by
`previous_record_id` and supersedes / superseded_by. Two time dimensions:
`valid_time` (when the claim applies to the world / domain) and `recorded_at` (when Obsidia
recorded the transition).

- `LATEST_EPISTEMIC_STATE(claim_id, as_of_recorded_time)` = state of the record with the highest
  record_version among that claim's records with `recorded_at ≤ as_of_recorded_time`.
- `KNOWLEDGE_STATE_AS_RECORDED_AT(T)` = for each claim, `LATEST_EPISTEMIC_STATE(claim_id, T)`
  (historical replay: "what did Obsidia hold at T").
- `CURRENT_KNOWLEDGE(slot, world_time, as_of_recorded_time)` = claims such that the slot matches,
  `valid_time` contains `world_time`, and `LATEST_EPISTEMIC_STATE(claim_id, as_of_recorded_time)
  = PROMOTED`. By construction a later CONTESTED / STALE / INVALIDATED / SUPERSEDED record removes
  the claim; historical PROMOTED records are never scanned as independently current.
- "Current now" uses `as_of_recorded_time` = latest available history, passed explicitly to the
  deterministic core.

No destructive overwrite. Durable storage of this history is B10.

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
| Block 3D human validation gate (dry run) | ADAPT | outcomes become HELD / REJECTED reasons; never promotion, never attestation |
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
- Normalization (docs only, no semantic change): history line moved out of the active status
  block into this record; header BASE line reworded so the active block carries no CLOSED token.
