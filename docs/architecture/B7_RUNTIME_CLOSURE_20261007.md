# B7 Cognitive Resolution Runtime — Closure (2026-10-07)

```
B7_SPEC_STATUS=CLOSED
B7_RUNTIME_STATUS=CLOSED
B7_RUNTIME_HEAD=756a6ba7
B7_SECURITY_EPOCH=1
B7_SECURITY_STATUS=SAFE (epoch 1, assumptions below)
SECURITY_SENTINEL_HARDENING=HOLD_FUTURE
PF_FREEZE_REVISIT_REQUIRED=YES
MEMORY_WRITE=False
EMITS_ACT=False
KERNEL_MUTATION=False
DECISION_AUTHORITY=KX108_ONLY
```

Runtime: `app/cognition/b7/` (contracts, detector, router, translator, validation). Tests: `tests/b7/`.
Spec: `B7_COGNITIVE_ROLE_SPEC_V1.md`, `B7_RUNTIME_DETERMINISM_CONTRACT_V1.md`,
`B7_STRUCTURED_REFERENT_ONLY_AMENDMENT_20261007.md`.

## Semantic statements (frozen)

- B7_ACCEPT != DURABLE_KNOWLEDGE
- VALIDATED_WORKING_CONTEXT != MEMORY
- COGNITIVE_RESOLUTION != AUTHORITY
- TRUSTED_TYPED_OBJECT != TRUSTED_GATE_OUTPUT
- MEMORY != TRUTH
- CONFIDENCE != AUTHORITY
- DECISION_AUTHORITY = KX108_ONLY

## 1. Chronology

| Step | Content |
|---|---|
| B7-A/B/C | role spec V1 frozen and closed |
| B7-D | runtime determinism contract (M1–M10, canonical order, verdicts) |
| B7-E/F | RED contract tests, then runtime implementation |
| B7-G/H/J | referent remediation (substring, uncertainty, determiner fallbacks) |
| B7-K | human option A: STRUCTURED_REFERENT_ONLY (textual fallback removed) |
| B7-M | STRUCTURED_TEMPORAL_REFERENCE_ONLY (deixis); `validated` / `unverified_descriptive` split |
| B7-O | contradiction and provenance isolation |
| B7-Q | candidate identity bound to content (shared `candidate_identity`) |
| B7-R | full-width SHA-256 request / candidate identities |
| B7-S | full-width origin binding (`origin_full_digest`) |
| B7-T | typed participants/sources/times; canonical full request equality |
| B7-U | typed relations; runtime-issued trusted result; raw B6 packet no longer trusted |
| B7-V | issued-only `register_derived`; all trust sinks guarded; same-process threat audit |

## 2. Request field policy (`CognitiveResolutionRequest`)

| Class | Fields |
|---|---|
| IDENTITY | request_id, original_state_digest, origin_full_digest |
| DERIVED_FROM_ORIGIN | origin_state_id, origin_state_type, source_refs, uncertainty |
| DERIVED_FROM_MARKER | problem_refs (exactly one), unresolved_kind, why_resolution_needed |
| DERIVED_FROM_ROUTING_POLICY | allowed_role_ids, forbidden_operations, required_candidate_kind |
| DERIVED_FROM_PROVENANCE | provenance_refs |
| STATIC_CONTRACT | context_refs (= ()) |

Gate law: the received request must be equal, field for field, to one request of
`detect_unresolved(origin)` (VALID REQUEST_ID != VALID REQUEST BODY).

## 3. Candidate field policy (`CognitiveResolutionCandidate`)

| Class | Fields |
|---|---|
| LINEAGE_BOUND | candidate_id, candidate_digest, request_id, origin_state_id, original_state_digest, candidate_kind, proposer_role, provider_ref, resolves |
| VALIDATED_STRUCTURE | proposed_resolution keys mention, antecedent, participants, sources, anchor, times, relations |
| UNVERIFIED_DESCRIPTIVE | quoted_text, characterization, hypothesis (strings only), evidence_refs, context_refs, assumptions, confidence_class, provenance_refs additions, contradiction additions |
| FAIL_CLOSED_UNCERTAINTY | remaining_unknowns (may only add; derived state stays OPEN) |
| REJECT_ONLY | forbidden claims (physical_chronology_established, world_fact_established, emits_act, memory_write, kernel_mutation, allowed_to_act, allowed_to_decide, decision_authority) and every other key |
| LIFECYCLE | candidate_status |

Collections: participants / sources / times = `list[str]`; relations = `list[{kind:str, source:str,
target:str}]` existing exactly in the origin. Empty lists allowed; any other type → REJECT.

## 4. Identity chain

- `origin_full_digest` = `b7orig_` + SHA-256(canonical_json(origin.to_dict())) — 256 bits; its first
  16 hex equal the B6 legacy 64-bit `content_digest`.
- `request_id` = `b7req_` + SHA-256([origin_state_id, origin_full_digest, field, marker]) — 256 bits.
- `candidate_digest` / `candidate_id` = SHA-256 of the typed candidate content — 256 bits; one
  implementation path (`candidate_identity`), recomputed at the gate.
- B6 short digest and non-unique `state_id` ("sens:frame") can no longer alias a B7 origin.

## 5. Semantic gates

Structured referents only; temporal values only from origin `semantic_frame.deixis`; relations only as
existing structured relations; closed proposal schema; descriptive content string-only and
non-authoritative; root contradictions = origin contradictions; structural provenance = request
provenance + `app.cognition.b7.validation`; exact uncertainty conservation; no winner among
multiple candidates; CHARACTERIZATION_ONLY / WORLD_REFERENCE_HYPOTHESIS never ACCEPT
(WORLD guard: DEFENSIVE_UNREACHABLE — no M1–M10 marker yields it).

## 6. Trust boundary

- Trust sinks (complete inventory at 756a6ba7): `admit_trusted_context`, `register_derived`.
- Both require `_is_issued(result)` AND verdict ACCEPT AND a `StateEntry` derived state.
- Issuance: process-local `weakref.WeakValueDictionary` keyed by `id(result)`, written only by the
  ACCEPT path of `validate_candidate`. Not serialized, not in any payload. `_issue` has 0 external
  callers and is not re-exported.
- Raw B6 `ContextPacket` admission (old spec §21 rule): SUPERSEDED_BY_B7_U. A raw B6 typed object is
  not proof of B7 validation. The B6 typed-object boundary itself is NON_BLOCKING_DEFERRED_B6_BOUNDARY.

Threat model: TRUST_MECHANISM_PROCESS_LOCAL=YES, TRUST_MECHANISM_CRYPTOGRAPHIC=NO. It protects the
current runtime against forged data, forged / reconstructed / copied / deep-copied / replaced /
pickled objects and modified results. It does NOT resist hostile Python code already executing in
the B7 interpreter.

## 7. Frozen B7 security law — epoch 1

`B7_SECURITY_EPOCH=1` holds under these assumptions:

1. The B7 interpreter executes trusted application code only.
2. Provider / model / user / untrusted content is DATA, never executable Python.
3. No arbitrary same-process code execution is part of the certified B7 runtime
   (audit: 40 modules in the B7 transitive closure, 0 dynamic-execution sites; no production
   importer of `app.cognition`; SAME_PROCESS_UNTRUSTED_CODE=NO_PROVEN_REACHABLE_PATH).
4. All B7 trust sinks require runtime-issued successful validation results.
5. Raw B6 typed objects are not proof of B7 validation.
6. MEMORY_WRITE=False
7. EMITS_ACT=False
8. KERNEL_MUTATION=False
9. DECISION_AUTHORITY=KX108_ONLY

### Automatic re-audit triggers

Any future change introducing or activating: same-process provider code execution, plugin
execution, generated-code execution, tool callbacks executing arbitrary code, arbitrary callable
injection, dynamic untrusted imports, a new trust sink, a new `_issue` caller, raw B6 trusted
admission, LIVE_PROVIDER_WIRING affecting this boundary, memory-write capability, ACT capability,
kernel mutation, or non-KX108 decision authority **invalidates the applicability of epoch 1**:
`B7_SECURITY_STATUS=REAUDIT_REQUIRED` until a new audit establishes a new epoch. The epoch is never
bumped silently. A stronger boundary (separate trusted process, typed IPC, sandbox, remote
validation) is required before trusting such a runtime; module-private names, `__all__`, closures,
in-process secrets or HMAC keys are not a boundary against same-process code.

### Sentinel V0 baseline seed

```
B7_SECURITY_EPOCH=1
CERTIFIED_TRUST_SINKS=admit_trusted_context,register_derived
CERTIFIED_EXTERNAL_ISSUE_CALLERS=0
CERTIFIED_SAME_PROCESS_UNTRUSTED_CODE=NO_PROVEN_REACHABLE_PATH
CERTIFIED_MEMORY_WRITE=False
CERTIFIED_EMITS_ACT=False
CERTIFIED_KERNEL_MUTATION=False
CERTIFIED_DECISION_AUTHORITY=KX108_ONLY
LIVE_PROVIDER_WIRING=NOT_IMPLEMENTED
SECURITY_SENTINEL_HARDENING=HOLD_FUTURE
PF_FREEZE_REVISIT_REQUIRED=YES
```

## 8. Certification evidence (HEAD 756a6ba7)

| Suite | Result |
|---|---|
| tests/b7 | 360 passed |
| B6 (tests/test_b6_*.py) | 67 passed |
| B6 Brody seam + related | 17 passed |
| SENS broad regression | 2483 passed |
| Brody boundary | 66 passed |

Fresh final adversarial matrix: 148176 cases (7 request mutations × 3 origins (canonical, foreign,
with contradictions) × 21 proposal shapes × 8 candidate overrides × 3 candidate-identity mutations ×
7 result wrappers (real, manual, deepcopy, replace, pickle, public reconstruction, raw B6 packet) ×
2 trust sinks). 21 ACCEPT, all canonical; 7 of them carry candidate-added contradictions, verified
to stay in `unverified_descriptive.candidate_contradictions` with root contradictions = origin. 42
trusted admissions, all real issued ACCEPT results; 0 forged / copied / reconstructed / packet
admissions. Independent hashlib recomputation of origin, request and candidate identities: PASS.
Simulated legacy 64-bit collision: requests distinct, foreign replay 0. Issuance registry 1 → 0
after drop + gc. Network / subprocess calls: 0.

All hard metrics 0: semantic invention, false / unstructured referents, invented participants,
sources, relations, times, anchors, unknown proposal keys, descriptive smuggling, unverified
promotion, invented root contradictions, provenance promotion, silent uncertainty loss, role /
provider bypass, lineage spoof, forged request body, request scope expansion, forged results,
authority leaks, world / physical truth fabrication.

## 9. Deferred limits (each classified)

| Item | Status |
|---|---|
| B6_ORDER_DIGEST (64-bit) | NON_BLOCKING_DEFERRED (B6 frozen; B7 binds 256-bit origin) |
| B6_TYPED_OBJECT_TRUST_BOUNDARY | NON_BLOCKING_DEFERRED (B6 boundary; B7 no longer trusts raw B6 objects) |
| DERIVED_KNOWN_SEMANTICS | NON_BLOCKING_DEFERRED (KNOWN = no remaining unknowns, never truth) |
| DUPLICATE_CANDIDATE_STILL_UNRESOLVED | NON_BLOCKING_DEFERRED (fails closed) |
| candidate-added remaining_unknowns | NON_BLOCKING_DEFERRED (only make the derived state OPEN) |
| candidate-kind ↔ semantic-field coupling | NON_BLOCKING_DEFERRED (each field gated independently) |
| B6_10 | FROZEN_DEFERRED |
| LIVE_PROVIDER_WIRING | NOT_IMPLEMENTED — REQUIRES_B7_TRUST_BOUNDARY_REAUDIT_BEFORE_ACTIVATION |
| FUTURE_SAME_PROCESS_CODE_EXECUTION | NON_BLOCKING_DEFERRED — REQUIRES_B7_TRUST_BOUNDARY_REAUDIT_BEFORE_ACTIVATION |
| MERKLE_PROOF_LINKAGE | PROOF_LAYER_DEFERRED (Merkle exists: `proofs/verifiers/verify_merkle.py`, `audit_merkle.py`; B7 origin digest / derived receipt not in the chain; no B7 contract requires it) |
| WORLD_REFERENCE_HYPOTHESIS guard | DEFENSIVE_UNREACHABLE (non-blocking) |
| SECURITY_SENTINEL_HARDENING | HOLD_FUTURE — must be RESOLVED or ACCEPTED_HOLD_WITH_DEFINED_POST_FREEZE_GATE at PF-FREEZE |

Next: Security Boundary Sentinel V0 (baseline above), then B8 READ_ONLY forensic audit.
