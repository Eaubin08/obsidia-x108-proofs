# B7 Cognitive Role Spec — Closure (2026-10-07)

```
B7_SPEC_PATH=docs/architecture/B7_COGNITIVE_ROLE_SPEC_V1.md
B7_SPEC_COMMIT=e7e74f01
B7_SPEC_STATUS=CLOSED (PASS_WITH_DEFERRED — precision items below, no contradiction, no authority conflict)
RUNTIME_STATUS=NOT_IMPLEMENTED

SENS_STATUS=CLOSED   (093c90ac)
B6_STATUS=CLOSED     (19925074)

KX108_ONLY
memory_write=False
emits_act=False
kernel_mutation=False

B6_10=FROZEN_DEFERRED_RUNTIME_HARDENING (spec closes the design gap only)

NEXT=B7 Runtime Implementation Planning / RED-test contract
```

Only the B7 SPEC is closed. B7 runtime is not implemented and not closed.

## Independent audit results (B7-C, read-only, at e7e74f01)

- Role matrix: no DECIDE / ACT / WRITE_DURABLE_MEMORY = YES, AUTHORITY = NONE for all 7 roles;
  the validation gate is not a role and is non-sovereign.
- ROLE != PROVIDER holds; CG9 stays provider governance (identity, execution, receipts) — no
  parallel registry; Brody / Obsidure appear as eligible providers, not role identities.
- F07 composes: B7 extends the F07 advisory boundary (fail-closed on ACT, ALLOW/HOLD/BLOCK, memory
  write, X108 override) to unresolved-state resolution; the gate writes only a NEW in-memory B6
  working entry (not a "Brody write" nor a memory write).
- SENS / B6: B7 starts from explicit unresolved state only, never rewrites the SENS frame or
  replaces deterministic SENS resolution; requests derive from B6 StateEntry fields
  (state_id, content_digest, provenance, uncertainty, status, semantic_frame); ACCEPT creates a new
  B6-compatible entry.
- Gate verdicts ACCEPT_AS_STRUCTURED_CONTEXT / REJECT / STILL_UNRESOLVED are cognitive validation
  results, not sovereign verdicts and not a new truth state; no duplication of KX108, Semantic
  Closure, ReviewJoin or B8 guards.
- Multi-candidate: no winner by confidence, vote or provider priority; confidence descriptive only.
- OTHER_EXPLICIT_UNRESOLVED fails closed (only UNDERSTANDER + CRITIC, neither proposes; no ACCEPT
  path in V1). WORLD_OR_PHYSICAL_REFERENCE cannot establish physical truth.
- B8 / B9 leakage: none.

## Deferred precision items (must be fixed in the B7 runtime planning / RED-test contract)

1. `candidate_status` vocabulary undefined — define a closed cognitive lifecycle set that cannot
   carry ALLOW / HOLD / BLOCK / ACT / EXECUTE / DECIDE.
2. `required_candidate_kind` and `forbidden_operations` vocabularies undefined — define them as
   closed descriptive sets (contract restrictions, never KX108 decisions).
3. Mechanical detector table not written — define the exact explicit-marker → UnresolvedKind
   mapping (e.g. unresolved_references, detached_source_of, conditional_protasis, ambiguities,
   contradictions, D1–D5 markers); unmapped markers → OTHER_EXPLICIT_UNRESOLVED.
4. TEMPORAL_REFERENCE: state explicitly that linguistic temporal interpretation ("hier", "à ce
   moment-là") never produces sensor / world / physical chronology; INVESTIGATOR may be added for
   context evidence.
5. Brody roles: mark which eligible roles are currently implemented capabilities versus future
   eligibility (no linguistic RESOLVER capability is implemented today).
6. Missing critical future tests: request / origin / digest mismatch → REJECT; ineligible role or
   provider → REJECT; OTHER_EXPLICIT_UNRESOLVED never ACCEPT; quoted "ALLOW/HOLD/BLOCK/ACT" text is
   not authority; candidate strict-JSON / bounds; TRANSLATOR invalid output → REJECT; ACCEPT twice
   for one request / duplicate derived state id fails closed.

These items refine the frozen contract; none changes a role right, a law or a boundary.
