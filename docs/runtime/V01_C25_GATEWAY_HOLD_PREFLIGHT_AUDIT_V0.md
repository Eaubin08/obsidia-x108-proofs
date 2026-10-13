# V0.1 C2.5 — Offline gateway HOLD/BLOCK preflight hardening

Status: DRAFT / FAIL-CLOSED / NO LIVE EXECUTION.

Base C2.4: 2de1b802a76b5b3fdd3133b7295e8dce8147ee12. Its targeted CI run 37725707713 completed SUCCESS.

Audit found that C2.4 returned NO_EXECUTION for a fixture ticket with x108_gate=HOLD and consumed a valid nonce before the dry-run Gateway decided. This could obscure an unapproved decision and waste an otherwise unused nonce.

C2.5 now denies missing, HOLD or BLOCK ticket gate fields before local nonce consumption, checks the existing Gateway DRY_RUN_PASS and egress_allowed=False before nonce consumption, and tests that denied preflights do not burn nonces. A fixture ticket with x108_gate=ACT still has no independent KX108 provenance or authenticated SovereignTicket and **never** grants real egress: outcome is NO_EXECUTION only.

Remaining gaps: verified issuer/organization, ticket authenticity and action binding, real KX108 receipt verification, authenticated connector dispatch, transactional revocation fencing with provider operations, durable receipts. No main merge, no kernel or Monde changes.
