# B8 — Knowledge Promotion State Machine (V1 specification)

```
STATUS=B8_SPEC_V1 / CLOSED / NO_RUNTIME_IMPLEMENTATION
B8_SPEC_STATUS=CLOSED
B8_RUNTIME_STATUS=NOT_IMPLEMENTED
SAFE_FOR_B8_RED_TESTS=YES
SAFE_FOR_B8_RUNTIME_IMPLEMENTATION=NO
DRAFT=2e2fbf6f ; CLOSED_AFTER_AUDIT=2026-10-07
BASE=B7 runtime CLOSED 44b0391e (security epoch 1) ; Sentinel V0 c5af4138
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
CONTENT != SCOPE != PROVENANCE · CONTRADICTION != AUTOMATIC_RESOLUTION ·
EPISTEMIC_STATUS != MEMORY_LIFECYCLE_STATUS · NO_SILENT_PROMOTION · NO_SILENT_OVERWRITE ·
DECISION_AUTHORITY=KX108_ONLY.

## 3. Identities and bounds (O-6)

- Every identity = prefix + full SHA-256 hex (64 hex, 256 bits) over strict canonical JSON
  (`app.harness.state_explicit.contracts.canonical_json`), same discipline as B7
  (`full_digest`). Prefixes namespace only; `IDENTITY_COLLISION_REDUCTION=NONE`.

| Object | Prefix | Preimage |
|---|---|---|
| KnowledgeClaim | `b8claim_` | claim_class, slot, valid_time, content |
| EvidenceRef | `b8ev_` | every evidence field |
| VerificationRecord | `b8ver_` | every field |
| HumanAttestation | `b8att_` | every field |
| KnowledgeRecord | `b8rec_` | claim_id, version, state, every ref field, recorded_at |
| TransitionRequest | `b8treq_` | every field |
| TransitionReceipt | `b8rcpt_` | every field |
| EpistemicGap | `b8gap_` | slot, valid_time, reason, missing evidence, contradiction refs, provenance |
| KnowledgeSlot | `b8slot_` | see §5 |

- Bounds reuse existing canonical values (no new numbers): every B8 object's canonical JSON
  ≤ `MAX_CANDIDATE_CHARS` = 32 768 (B7, same serialization layer); this bounds every nested list,
  mapping and string, so `UNBOUNDED_USER_CONTROLLED_COLLECTIONS=0` and
  `UNBOUNDED_USER_CONTROLLED_TEXT=0`. Overflow → reject (fail closed, never truncated, as B6
  `MAX_QUERY_CHARS`). A transition request carries references, not embedded evidence bodies.
  Per-claim history length is not a request bound: it is append-only log size, a B10
  persistence concern.

## 4. Typed objects

| Object | Content |
|---|---|
| `KnowledgeClaim` | `claim_class`, `slot` (§5), `valid_time`, structured `content`, `source_refs`, `origin_refs` (e.g. B7 derived state id) |
| `ClaimClass` (closed enum, O-2) | FORMAL_CLAIM, CODE_BUILD_CLAIM, PHYSICAL_CLAIM, DOCUMENTARY_CLAIM, DOMAIN_CLAIM, HUMAN_DECLARATION, ORGANIZATIONAL_POLICY |
| `EvidenceRef` | kind, source ref, content digest, captured_at, provenance refs, optional descriptive confidence |
| `VerificationRecord` | verifier_family, claim_id, claim_version, verdict SATISFIED / NOT_SATISFIED / INCONCLUSIVE, evidence_refs, method ref, produced_at |
| `HumanAttestation` (O-5) | attestation_id, actor_id, identity_source, auth_context_ref, issued_at, claim_id, attestation_kind (ATTESTATION / REVIEW_AUTHORIZATION / PRIMARY_DECLARATION), scope, optional proof/signature ref |
| `KnowledgeRecord` | claim_id, version, state, evidence / verification / attestation refs, supersedes / superseded_by, contested_by, recorded_at, previous_record_id |
| `TransitionRequest` | claim_id, expected_state, expected_version, target_state, refs, requester ref, reason |
| `TransitionReceipt` | request id, verdict APPLIED / REJECTED / NO_OP_DUPLICATE, from / to state and version, reasons, gate contract version, recorded_at |
| `EpistemicGap` (O-1) | slot, valid_time, reason knowledge is unavailable, missing evidence, contradiction refs, provenance, recorded_at, gap state |

`recorded_at` is an input supplied to the gate (injected clock), never read by the gate itself:
the gate stays deterministic. Confidence is descriptive data inside evidence; it is never a
sufficient precondition and never part of a policy decision.

## 5. Scope and slots (O-4)

`CONTENT != SCOPE != PROVENANCE`. Scope = `KnowledgeScope{subject_refs, context_refs, domain_id,
valid_time}`; sources and evidence are provenance, never scope.

`KnowledgeSlot` = `b8slot_` + SHA-256(claim_class, domain_id, sorted subject_refs, sorted
context_refs, predicate_ref) — the "question" a claim answers, without its value and without
time.

- Same slot, different `valid_time` → distinct current entries; coexist historically.
- Different context or domain → different slot; never fused.
- Same slot and same / overlapping `valid_time` with a newer admissible claim → explicit T9
  SUPERSEDE only. Supersession across slots or across non-overlapping valid_time is forbidden.
- CURRENT_KNOWLEDGE(slot, t) != KNOWLEDGE_AT_RECORDED_TIME(slot, T): both are derived from the
  append-only history (§8).

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
- A human attestation never verifies an objective class (FORMAL, CODE_BUILD, PHYSICAL,
  DOCUMENTARY, DOMAIN): for those it may only satisfy a REVIEW_AUTHORIZATION precondition.
- New claim classes / domains extend the registry only through an explicit audited contract.
- Staleness mechanisms (closed set): NEVER_BY_TIME, TTL, SOURCE_VERSION_CHANGE, VALID_UNTIL,
  CONDITION_TRIGGER, DOMAIN_POLICY. No generic duration is encoded in B8; TTL values come only from
  an audited domain contract. STALE requires an explicit trigger evidence.

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
| VERIFIED | SATISFIED record of an admissible verifier family for this claim version | no (not yet promoted) |
| PROMOTED | admissible current knowledge under scope, evidence, verification policy, version, provenance, history | **yes** |
| CONTESTED | admissible contradiction open | **no** — consumers receive it as explicit uncertainty with both sides' refs; never as trusted knowledge, never with a winner |
| SUPERSEDED | replaced by a newer claim on the same slot / time (terminal, history kept) | no (historical) |
| INVALIDATED | explicitly withdrawn with reasons (terminal, history kept) | no |
| STALE | staleness trigger fired; needs re-verification | no — exposed as stale |

Memory lifecycle states (ACTIVE, SEMI_ACTIVE, COLD, GHOST…) are retrieval / storage concerns
(B9 / B10) and are never B8 states: `EPISTEMIC_STATUS_MEMORY_STATUS_COLLAPSE=0`.

**EpistemicGap (O-1)** is a separate object with its own states OPEN → RESOLVED | SUPERSEDED. It
records "we do not currently know X" (UNKNOWN(X) != FALSE(X) != VERIFIED(X) != PROMOTED(X)). It is
never a `KnowledgeClaim`, never enters T1–T12, and never becomes positive knowledge: a gap is
RESOLVED only by linking to a claim on the same slot that reached PROMOTED through the normal
chain; the gap itself stays reconstructible historically.

## 9. Legal transitions (the only ones)

Every transition requires: matching `expected_state` and `expected_version` (compare-and-set),
a reason, all refs re-hashed and bound to claim id + version, and produces a new immutable
`KnowledgeRecord` + `TransitionReceipt`. Identical request already applied → NO_OP_DUPLICATE with
the original receipt. Different request on a stale state / version → REJECTED `stale_request`.

| # | From → To | Preconditions |
|---|---|---|
| T1 | ∅ → CANDIDATE | well-formed claim (class, slot, valid_time, content, source/origin refs); idempotent on claim id |
| T2 | CANDIDATE → HELD | explicit hold reason |
| T3 | CANDIDATE / HELD → REJECTED | explicit reasons |
| T4 | CANDIDATE / HELD → SUPPORTED | ≥1 admissible EvidenceRef with complete provenance |
| T5 | SUPPORTED → VERIFIED | VerificationRecord SATISFIED, verifier family admissible for the class (§6), bound to claim id + version; human classes: admissible PRIMARY_DECLARATION attestation (§7) |
| T6 | VERIFIED → PROMOTED | no open contradiction on the slot / time; REVIEW_AUTHORIZATION attestation admissible when `requires_human_review`; no other PROMOTED claim on the same slot / overlapping valid_time (else T9) |
| T7 | SUPPORTED / VERIFIED / PROMOTED → CONTESTED | admissible contradicting evidence or claim recorded with refs |
| T8 | CONTESTED → SUPPORTED | contradiction explicitly resolved (contradicting side INVALIDATED / REJECTED or new verification refs); never by confidence or recency; re-verification then required (T5, T6) |
| T9 | PROMOTED → SUPERSEDED | in the same gate step a newer claim on the same slot and overlapping valid_time passes T6; links supersedes / superseded_by both ways |
| T10 | CANDIDATE / HELD / SUPPORTED / VERIFIED / PROMOTED / CONTESTED / STALE → INVALIDATED | explicit reason + evidence ref |
| T11 | PROMOTED → STALE | staleness trigger evidence per class mechanism (§6) |
| T12 | STALE → VERIFIED | fresh SATISFIED VerificationRecord for the current version; T6 again to PROMOTED |

**Forbidden complement (fail closed): every (from, to) pair not listed above**, in particular
CANDIDATE → VERIFIED / PROMOTED, HELD → VERIFIED / PROMOTED, SUPPORTED → PROMOTED, REJECTED → any,
STALE → PROMOTED, INVALIDATED → any, SUPERSEDED → any (a superseded record never becomes current
again; a new claim is required), CONTESTED → VERIFIED / PROMOTED, EpistemicGap → any claim state,
any transition caused by confidence, majority, provider priority, recency or a human approval
alone on an objective class, any direct `record.state = …` outside construction, any overwrite.

## 10. Point-in-time contract

History is append-only: records and receipts are immutable and linked by `previous_record_id`,
`supersedes` / `superseded_by`. `recorded_at` (when the system recorded it) is distinct from
`valid_time` (when the claim holds). "What did the system hold at T" = replay of receipts with
`recorded_at ≤ T`; "what is current for slot s at time t" = PROMOTED records on s whose
valid_time contains t. No destructive overwrite. Durable storage of this history is B10.

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
| `periphery/memory` status enum | ADAPT | CAPTURED / HASHED / CANDIDATE_ONLY → CANDIDATE ; NEEDS_REVIEW / FROZEN → HELD ; REJECTED → REJECTED ; **PROMOTION_READY → HELD** (legacy status set by direct assignment with no verification record: not VERIFIED) ; **PROMOTED_MANUAL_ONLY → no canonical equivalent** (superseded by PROMOTED via the gate) |
| `MemoryCandidate.status` free assignment | SUPERSEDE | gate transitions only |
| `memory_promotion_policy.evaluate_promotion_policy` | SUPERSEDE | the B8 gate is the only promotion engine |
| `memory_candidate_ledger` | ADAPT | T1 capture log, idempotent on claim id |
| Brody V3 Block 3A–3C (trace, candidate, education, replay) | ADAPT | proposal inputs to T1 only |
| Block 3D human validation gate (dry run) | ADAPT | outcomes become HELD / REJECTED reasons; never promotion, never attestation |
| `brody_memory_promotion_guard` | ADAPT | advisory readiness only, outside policy decisions |
| native memory reader | KEEP | read path, no state authority |
| Neo4j CLI manual apply (2 modules) | SUPERSEDE_BEFORE_CANONICAL_RUNTIME_WRITE | D-5 |
| native index migration script | HOLD | operator migration artifact; not a promotion route |
| Brody answer templates citing GATE_001..006 | SUPERSEDE | describe nonexistent gates |

No duplicate promotion engine survives canonical B8.

## 13. Audit record (2026-10-07)

Draft 2e2fbf6f corrected before closure: no numeric bounds (now reused B7 bound), PROMOTION_READY
mapped by name to VERIFIED (now HELD), CONTESTED consumption undefined (now explicit), no slot
identity / valid_time (now §5), human-review policy implicit (now §6), recorded_at source
undefined (now injected). Spec transition-policy matrix: see the B8 spec audit report.
