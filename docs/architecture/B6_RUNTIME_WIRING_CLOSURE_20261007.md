# B6 — Runtime Wiring (State-Explicit Harness) — Closure (2026-10-07)

Block 27 of `docs/semantic/SENS_PRE_FORGE_CANONICAL_ROADMAP.md`. B6 is the explicit runtime seam
SENS → working state → query-aware projection → bounded context assembly → optional Brody consumer.
It is not cognition: it never decides, authorizes, acts, writes memory or mutates the kernel.

```
SENS_STATUS=CLOSED
SENS_CLOSING_HEAD=093c90ac

B6_BASE_HEAD=093c90ac
B6_INITIAL_IMPLEMENTATION_HEAD=badb196a
B6_FINAL_IMPLEMENTATION_HEAD=b7473a92

IMPLEMENTATION_COMMITS=
  5806212b feat(b6): add state-explicit working state contracts
  bd1269de feat(b6): add deterministic context projection and assembly
  56462e15 feat(b6): connect SENS and readonly context adapters
  badb196a feat(b6): expose optional Brody consumer seam
  6bb65fe7 fix(b6): preserve complete SENS frame state
  b7473a92 fix(b6): isolate instruction conditions, enforce hard bounds, canonical strict-JSON replay

CORE_PACKAGE=app/harness/state_explicit/
CANONICAL_BRODY_CONSUMER_SEAM=apps/obsidia_api/brody_real_response_pipeline.py::run_brody_real_response_pipeline
  (optional state_context_packet=None; omitted / None identical to pre-B6)

R1 complete SENS frame         PASS  (21/21 canonical frame fields in payload["semantic_frame"], walked dynamically; SEMANTIC_FIELD_LOSS=0)
R2 trusted instruction trigger PASS  (state metadata tags only; query text never activates state instructions)
R3 hard bounds                 PASS  (HARD_BOUNDED)
R4 canonical replay            PASS  (insertion-order independent packet; packet_id = sha256 of canonical strict JSON)
R5 strict JSON                 PASS  (finite numbers, string keys, no cycles, allow_nan=False)

BOUNDS:
  MAX_QUERY_CHARS=4096      (over: ContextBoundError, never truncated)
  MAX_STATE_ENTRIES=64      (over: omitted reason=ENTRY_LIMIT)
  MAX_PACKET_BYTES=262144   (over: reduce to SHORT "PACKET_SIZE_LIMIT:reduced_to_SHORT", then omit
                             "PACKET_SIZE_LIMIT"; mandatory metadata alone too large: ContextBoundError)
  MAX_PAYLOAD_CHARS=65536, MAX_ENTRY_CHARS=81920, LONG_PREVIEW_CHARS=2048

B6-01 Working State Registry          PASS
B6-02 Typed Addressable State         PASS
B6-03 Query-aware Projection          PASS
B6-04 Visibility Policy               PASS
B6-05 Conditional Instructions        PASS
B6-06 Tiered Capability Disclosure    PASS
B6-07 Context Assembly                PASS
B6-08 SENS → State Wiring             PASS
B6-09 Native Memory Readonly Seam     PASS
B6-10 Brody Consumer Seam             PASS_WITH_DEFERRED
B6-11 Provenance Conservation         PASS
B6-12 Replay / Inspectability         PASS
B6-13 Fail-closed Unknown State       PASS
B6-14 Authority Isolation             PASS

TESTS (final audit at b7473a92):
  tests/test_b6_*.py                      67 passed
  Brody readonly / authority (9 files)    122 passed, 1 skipped
  SENS certification (ReviewJoin, Closure) 50 passed
  touched surface (pipeline importers)    42 passed, 2 failed, 1 error — identical to 093c90ac

KNOWN_DEFERRED:
  B6-10: state_context_packet accepts an arbitrary mapping, attached verbatim as inert descriptive
         data (no reader; pipeline authority flags unaffected, verified with decision_authority=SELF,
         emits_act/memory_write/kernel_mutation=True). Future hardening item: validate an external
         state_context_packet against the B6 ContextPacket schema before ANY component is allowed to
         consume it semantically.

KNOWN_UNRELATED_PREEXISTING_FAILURES (not B6, reproduced on 093c90ac):
  tests/api/test_f17b_graphiti_v20_frozen_reconnect.py — 2 failures
  tests/api/test_f17c_brody_source_label.py — collection error

NON_BLOCKING_NOTES:
  - B6-D committed context_assembly.py, projection.py, sens_adapter.py and tests/test_b6_context_assembly.py
    with CRLF line endings (other B6 files are LF): cosmetic only, no content change.
  - A context made of many OPEN/UNKNOWN states with very large uncertainty lists fails closed
    (ContextBoundError) rather than degrading, because unknowns are mandatory metadata.

CONSTITUTIONAL_STATE:
  KX108_ONLY
  memory_write=False
  emits_act=False
  kernel_mutation=False
  allowed_to_decide=False
  allowed_to_act=False
  GRAPHITI_RUNTIME_CALLS=0
  NEO4J_RUNTIME_CALLS=0

B6_STATUS=CLOSED

NEXT_BLOCK=B7 CognitiveRoleSpec (forensic / specification first)
```
