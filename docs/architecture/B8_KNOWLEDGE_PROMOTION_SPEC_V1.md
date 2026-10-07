# B8 — Knowledge Promotion State Machine (V1 specification)

```
STATUS=B8_SPEC_V1 / DRAFT_FOR_AUDIT / NO_RUNTIME_IMPLEMENTATION
WRITTEN_ON=2026-10-07
BASE_HEAD=c5af4138 (B7 runtime CLOSED 44b0391e, security epoch 1 ; Sentinel V0 c5af4138)
FORENSIC_BASIS=B8 forensic (HOLD) + human doctrine decision D-1..D-5 (2026-10-07)
DECISION_AUTHORITY=KX108_ONLY (actions) ; KX108_KNOWLEDGE_PROMOTION_ROLE=NONE
PROMOTION_AUTHORITY=B8_CANONICAL_TRANSITION_GATE
MEMORY_WRITE=False  EMITS_ACT=False  KERNEL_MUTATION=False (for every B8 element)
```

B8 defines **how a claim's epistemic status may change** and what each change requires. It does
not persist anything durably (B10), does not authorize any action (KX108), and does not decide
truth: PROMOTED means *admissible current knowledge under the recorded scope, evidence and
version*.

## 1. Human doctrine decision (2026-10-07, resolves forensic HOLD D-1..D-5)

| Item | Decision |
|---|---|
| D-1 promotion authority | `B8_CANONICAL_TRANSITION_GATE`: a deterministic state-transition gate. Not Brody, not an LLM, not a provider, not a human alone, not KX108. |
| D-2 KX108 | `KX108_KNOWLEDGE_PROMOTION_ROLE=NONE`. KX108 stays action/effect authority. B8 authorizes epistemic transition; B10 may request persistence; Binder/KX108 may govern the actual write. |
| D-3 verification | `VERIFICATION_AUTHORITY=TYPED_VERIFIER_BY_CLAIM_CLASS`. A verifier produces a typed `VerificationRecord`; it never changes state. Invalidation and supersession authority = the B8 gate (explicit transitions, no silent overwrite). |
| D-4 human approval | `HUMAN_APPROVAL != TRUTH`. Default role: ATTESTATION or REVIEW_AUTHORIZATION (satisfies a review precondition). Exception: when the source of truth is the human declaration itself (preference, consent, operator approval, organizational policy), a typed `HumanAttestation` may be primary evidence, with identity and provenance preserved. |
| D-5 legacy manual writes | `NEO4J_MANUAL_APPLY_PATH=SUPERSEDE_BEFORE_CANONICAL_RUNTIME_WRITE`. The CLI apply scripts stay isolated operator / migration artifacts; never a canonical route; static in-source tokens are not authority. |

Future canonical durable route (B8 covers steps 1–4 only):
`candidate → B8 transition → verification → promoted knowledge state → B10 persistence request →
governed write authorization → durable write → receipt / replay`.

## 2. Frozen laws

B7_ACCEPT != DURABLE_KNOWLEDGE · VALIDATED_WORKING_CONTEXT != MEMORY · BELIEF != KNOWLEDGE ·
REPORT != VERIFIED · OBSERVED != VERIFIED · CONFIDENCE != TRUTH · CONFIDENCE != AUTHORITY ·
CANDIDATE != PROMOTED · COGNITIVE_PROPOSAL != MEMORY_AUTHORITY · HUMAN_APPROVAL != TRUTH ·
VERIFIER != PROMOTION_AUTHORITY · PROMOTION_AUTHORITY != ACTION_AUTHORITY ·
KNOWLEDGE_PROMOTION != ACTION_AUTHORIZATION · KNOWLEDGE_STATUS != WRITE_PERMISSION ·
PROMOTED != ABSOLUTE_TRUTH · MEMORY != TRUTH · UNKNOWN != FALSE ·
CONTRADICTION != AUTOMATIC_RESOLUTION · NO_SILENT_PROMOTION · NO_SILENT_OVERWRITE ·
DECISION_AUTHORITY=KX108_ONLY.

## 3. Typed objects

All objects are frozen, strict-JSON, size-bounded, with 256-bit SHA-256 identities over canonical
JSON (same discipline as B7). No object carries `memory_write`, `emits_act`, `kernel_mutation` or
decision authority.

| Object | Content | Identity |
|---|---|---|
| `KnowledgeClaim` | claim text/structure, `claim_class`, `scope` (subject, context, validity window), `source_refs`, `origin_refs` (e.g. B7 derived state id, candidate id) | `b8claim_` + SHA-256(class, canonical content, scope) |
| `ClaimClass` (closed enum) | FORMAL, CODE, PHYSICAL, DOMAIN, HUMAN_DECLARATION, DOCUMENTARY | — |
| `EvidenceRef` | typed pointer to evidence (source, digest, captured_at, provenance) | `b8ev_` + SHA-256 |
| `VerificationRecord` | verifier_type, claim_id, claim_version, verdict (SATISFIED / NOT_SATISFIED / INCONCLUSIVE), evidence_refs, method, produced_at | `b8ver_` + SHA-256 |
| `HumanAttestation` | attester identity ref, role, attestation kind (ATTESTATION / REVIEW_AUTHORIZATION / PRIMARY_DECLARATION), claim_id, claim_version, statement, provenance | `b8att_` + SHA-256 |
| `KnowledgeRecord` | claim_id, `version` (int ≥ 1), `state`, evidence / verification / attestation refs, `supersedes` / `superseded_by`, `contradicted_by`, state history pointer | `b8rec_` + SHA-256(claim_id, version) |
| `TransitionRequest` | claim_id, `expected_state`, `expected_version`, `target_state`, supplied refs, requester ref, reason | `b8treq_` + SHA-256 of all fields |
| `TransitionReceipt` | request id, verdict (APPLIED / REJECTED / NO_OP_DUPLICATE), from / to state, from / to version, reasons, gate contract version | `b8rcpt_` + SHA-256 |

Confidence may be recorded inside evidence as descriptive data; it is never a sufficient
precondition for any transition.

## 4. States

| State | Meaning | Adapts (forensic) |
|---|---|---|
| CANDIDATE | captured proposal, no epistemic standing | periphery CAPTURED / HASHED / CANDIDATE_ONLY / NEEDS_REVIEW ; Block 3B candidates |
| HELD | review / edit / missing proof pending; nothing promoted | FROZEN ; Block 3D hold_review / edit_required / pending_review |
| REJECTED | refused with reasons (terminal for that version) | REJECTED ; reject_adversarial |
| SUPPORTED | has admissible typed evidence, not yet verified | — (new) |
| VERIFIED | a `VerificationRecord` of the verifier type required by the claim class is SATISFIED for this version | PROMOTION_READY (re-scoped: verification, not permission) |
| PROMOTED | admissible current knowledge for the recorded scope / version | replaces PROMOTED_MANUAL_ONLY |
| CONTESTED | a contradicting admissible evidence or claim is open; no automatic resolution | Block 3 contradiction_tags (new state) |
| SUPERSEDED | replaced by a newer PROMOTED version; history kept | — (new) |
| INVALIDATED | explicitly withdrawn with reasons; history kept | — (new) |
| STALE | validity window elapsed or evidence aged out per claim-class rule | — (new) |

OBSERVED is a property of evidence, not a claim state. UNKNOWN is not a state: an unresolved
question stays out of B8 (B7 / HOLD), and UNKNOWN never becomes any state above PROMOTION by
default. Whether "we do not know X" may itself become a recorded claim is open item O-1.

## 5. Legal transitions (the only ones)

| # | From → To | Required preconditions (gate-checked) |
|---|---|---|
| T1 | ∅ → CANDIDATE | well-formed claim, class, scope, source/origin refs; idempotent on claim id |
| T2 | CANDIDATE → HELD | explicit hold reason (missing evidence, review requested, edit required) |
| T3 | CANDIDATE / HELD → REJECTED | explicit reasons (adversarial, secret, malformed, unsupported) |
| T4 | CANDIDATE / HELD → SUPPORTED | ≥1 admissible `EvidenceRef` with complete provenance for the claim class |
| T5 | SUPPORTED → VERIFIED | `VerificationRecord` SATISFIED by a verifier type admissible for the class, bound to this claim id and version; HUMAN_DECLARATION class: `HumanAttestation` PRIMARY_DECLARATION with identity |
| T6 | VERIFIED → PROMOTED | no open contradiction; required review precondition met (class policy; a REVIEW_AUTHORIZATION attestation where the class requires one); scope and version recorded |
| T7 | SUPPORTED / VERIFIED / PROMOTED → CONTESTED | admissible contradicting evidence or claim recorded with refs |
| T8 | CONTESTED → SUPPORTED | contradiction explicitly resolved by new verification / invalidation of the contradicting side, with refs (never by confidence or recency) |
| T9 | PROMOTED → SUPERSEDED | a newer version of the same claim reaches PROMOTED in the same gate step; links both ways |
| T10 | any non-terminal → INVALIDATED | explicit reason + evidence ref (e.g. failed re-verification, source retracted) |
| T11 | PROMOTED → STALE | class rule (validity window / evidence age) evaluated deterministically |
| T12 | STALE → VERIFIED | fresh SATISFIED `VerificationRecord` for the current version |

Forbidden (silent promotion): any skip of T4/T5/T6 (CANDIDATE → VERIFIED / PROMOTED, HELD →
PROMOTED, SUPPORTED → PROMOTED), any transition triggered by confidence, majority, provider
priority, recency or a human approval alone (outside HUMAN_DECLARATION primary evidence), any
in-place state edit without a `TransitionReceipt`, any overwrite of a PROMOTED record (use T9 / T10).

## 6. Gate contract

- Input: `TransitionRequest` + the current `KnowledgeRecord` (or none for T1) + referenced
  evidence / verification / attestation objects.
- Compare-and-set: `expected_state` and `expected_version` must equal the current record, else
  REJECTED `stale_request` (replay protection; an old request or receipt never re-applies).
- Idempotency: an identical request already applied returns NO_OP_DUPLICATE with the original
  receipt; never a second transition.
- Every referenced object is re-hashed and must be bound to the claim id and version.
- Output: a new immutable `KnowledgeRecord` version (or state) + `TransitionReceipt`; the previous
  record is never mutated. Append-only transition log ⇒ "state as of T" is derivable (point-in-time
  read is specified here; durable history is B10).
- Deterministic, no provider / LLM / network; `MEMORY_WRITE=False`, `EMITS_ACT=False`,
  `KERNEL_MUTATION=False`.

## 7. Boundaries

- **B7 → B8**: a B7 ACCEPT may only become the *source* of a T1 CANDIDATE, through an issued
  result (`admit_trusted_context`). It never skips T4–T6. Any B8 import of `app.cognition` triggers
  Sentinel `NEW_B7_IMPORTER` / `NEW_TRUST_SINK_CALLER` → a B7 security epoch-2 re-audit is part of
  B8 implementation.
- **B8 → B10**: PROMOTED is a precondition for a B10 persistence request, not a write permission.
- **KX108**: no role in B8 transitions; governs effects only.
- **Verifiers**: produce records only; no state change, no action authority.

## 8. Existing mechanisms (forensic → decision)

| Mechanism | Decision |
|---|---|
| `periphery/memory` status enum, candidate, policy | ADAPT: statuses mapped in §4; `MemoryCandidate.status` free assignment superseded by gate transitions |
| `periphery/memory/memory_candidate_ledger` | ADAPT: becomes a T1 capture log; add idempotency on claim id |
| Brody V3 Block 3A–3E packets | ADAPT: trace / candidate / education / replay remain proposal inputs; Block 3D outcomes become HELD / REJECTED reasons, never promotion |
| `brody_memory_promotion_guard` | ADAPT: advisory readiness only (confidence never a precondition) |
| native memory reader | KEEP (read path) |
| Neo4j CLI manual apply (2 modules), native index migration | SUPERSEDE_BEFORE_CANONICAL_RUNTIME_WRITE (D-5) |
| Brody answer templates citing GATE_001..006 | SUPERSEDE (text describes nonexistent gates) |

## 9. Open items (must be closed before spec freeze)

- O-1 Known-unknown records ("we do not know X"): allowed as a claim class or excluded.
- O-2 Per-class verifier table: which verifier types are admissible for each `ClaimClass`, and
  which classes require a REVIEW_AUTHORIZATION attestation for T6.
- O-3 STALE rules per class (validity windows, evidence age).
- O-4 Scope model granularity (subject / context / time) for "current" knowledge and supersession.
- O-5 Attester identity model (what identifies a human attester) — needed for D-4.
- O-6 Size bounds and identity prefixes (proposed above) to confirm.

Next: audit of this draft, close O-1..O-6, freeze B8 spec V1; RED tests; runtime only after spec
closure.
