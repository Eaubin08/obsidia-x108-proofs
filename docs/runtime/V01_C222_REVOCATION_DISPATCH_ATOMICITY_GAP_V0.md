# V0.1 C2.22 — Revocation / dispatch atomicity gap

Status: DRAFT / FAIL-CLOSED / NO LIVE CONNECTOR.

Parent C2.21 HEAD `93e4e330a28e8513fa135ec46e4b05a41c7aecdf`; targeted CI #37732365524 SUCCESS.

C2.22 isolates a temporal boundary: even if `DurableDelegationLedgerV0.check_and_consume_fixture` reports `CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY`, another transaction may revoke the delegate before a provider call. Therefore that observation must never be elevated into a dispatch permit.

The deny-only inspector always returns BLOCK with `egress_allowed=False` and `dispatch_attempted=False`. It refuses caller-supplied hooks. Tests demonstrate a check followed by revocation, already revoked credentials, and refusal to invoke a caller hook. These are local deterministic simulations, NOT distributed race certification.

Production requirements: real issuer/organization identity verification, canonical KX108 record and authenticated SovereignTicket, shared atomic dispatch reservation and revocation fence, idempotency receipts, failure recovery and external provider contract tests. None are implemented here. No merge to main; no kernel, Monde, or real connector changes.
