# C2.6 — Sovereign proof boundary audit

Status: WIP / DRAFT / FAIL-CLOSED / NO LIVE EGRESS.

Base C2.5 `8f5c5db40d1886e5b089cda6d78a25b016a37d68`; targeted C2.5 CI #37725982770 succeeded.

## Actual source audit
- `proofs/verify_decision.py` verifies required envelope fields and gate enumeration; this is a structural test, not signed KX108 provenance.
- `scripts/kernel/canonical_decision_envelope_v1.py` constructs candidate-only envelopes without decision or execution authority.
- `periphery/world_calls/sovereign_ticket.py` issues local tickets and hashes selected fields but does not authenticate an independent sovereign issuer. A caller with the constructor can create a plausible ticket.
- `periphery/world_calls/obsidia_gateway.py` remains dry-run-only and `egress_allowed=False`.

## New block
`enterprise_sovereign_proof_boundary_audit_v0.py` explicitly refuses HOLD/BLOCK, absent or mismatched action/scope/ticket, and ultimately returns `BLOCK:C26_INDEPENDENT_SOVEREIGN_ATTESTATION_UNAVAILABLE` even for seemingly valid structural ALLOW and local tickets.

This component is an audit denial surface, not an attestation verifier. It does not authorize any action.

## Next proof needed
Find and validate actual authoritative KX108 decision source, authenticated issuer identity, canonical action/ticket binding, time and revocation state, reproducible offline fixtures, and guarded dispatch with provider receipts. Do not implement a second KX108 authority or infer production authorization from C2.6 tests. No main/kernel/Monde mutation.
