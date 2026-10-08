# V0.1 C2.7 — canonical KX108 world-action record boundary

Status: DRAFT / WIP / READ-ONLY PROOF / NO EGRESS.

C2.6 CI #37726628921 finished SUCCESS. Audit located the real legacy canonical path:
`scripts/kernel/kx108_proof_canonical_decision_boundary_v1.py` (CG62)
→ `scripts/kernel/kx108_proof_decision_authority_boundary_v1.py` (CG53)
→ `scripts/obsidia_kx108_decision_store.py::verify_kx108_decision_record`.

The decision store explicitly defines `WORLD_ACTION_PRE_EXECUTION` and its binding fields: request hash, connector call hash, human approval hash, target prestate hash, scope, idempotency key, domain, action ID. The new adapter calls CG62 instead of inventing another KX108 verifier. It refuses missing/forged records, wrong phase, binding mismatch and non-ALLOW. Even if CG62 validates an ALLOW, its result is `VERIFIED_RECORD_ONLY_NO_EXECUTION_AUTHORITY`: no ticket authentication, organizational identity, provider egress, or live connector authority.

Current tests are negative/adversarial; a positive canonical WORLD_ACTION_PRE record fixture with a provenance chain must still be executed before this gate is marked closed. Never treat caller-produced hashes or a valid data structure as KX108 authorization. No changes to kernel, main, Monde or real provider.

## Positive pipeline fixture extension

The existing `tests/integration/test_world_action_pre_execution_v0.py` provides an executed local KX108 WorldAction PRE pipeline and persisted decision record. New C2.7 tests reuse that fixture for real local `ALLOW`, `HOLD`, `BLOCK` records, load them through the canonical decision store, verify their hashes and check exact binding with CG62. This is a genuine local kernel-generated test artifact, not a production-attested remote decision, organizational authority proof, or live execution permission. Positive CI must pass before declaring this subgate verified.
