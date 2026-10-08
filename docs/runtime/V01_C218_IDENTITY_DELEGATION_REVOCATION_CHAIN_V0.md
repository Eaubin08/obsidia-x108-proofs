# V0.1 C2.18 — Offline identity / scoped delegation / revocation composition

Status: DRAFT / FAIL-CLOSED / NO LIVE EXECUTION.

C2.17 parent HEAD: `2777af2c3e6533f9e06a93152224ab805a826941`. Its targeted CI runs 37730877663 and 37730873316 completed SUCCESS.

C2.18 composes three existing fixture components without changing KX108: C2.17 signed Ed25519 identity and pinned-key revocation, C2.2 signed scoped delegation binding organization/principal/delegate/connector/capability/action hash/expiry, and C2.3 local SQLite durable revocation and nonce replay. The check rejects missing or altered identity, mismatched delegation scope, expired delegation, revoked delegation and replay. Even when all fixture checks match, the final result is always `BLOCK:C218_ORGANIZATION_DELEGATION_AUTHORITY_UNVERIFIED`, with egress and execution authority false.

These test keys and fixture registration procedures are not independent legal organizational authentication. This adapter does not verify a canonical KX108 record, authenticate a SovereignTicket issuer, or execute a provider call. Consuming a nonce in the fixture ledger is a local demonstration, not cross-host atomic dispatch. Remaining: independent organization trust-root enrollment and authentically signed delegation from a trusted organization controller, KX108 record/ticket linkage, live connector gateway fencing, receipts. No merge to main, kernel/Monde edits, or real external action.
