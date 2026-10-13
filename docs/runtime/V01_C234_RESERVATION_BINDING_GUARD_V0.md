# C2.34 — Immutable reservation bindings (offline SQLite fixture)

Status: DRAFT / FAIL-CLOSED / NO REAL EXECUTION.

Base: C2.33 fixed HEAD 5bdeaa38a9479323e82a5f18f7df6f51352502f2. Original C2.33 targeted workflow #37734218578 FAILED (3 failing tests) from SQLite trigger SQL string normalization; C2.33 branch was amended to normalize whitespace and IF NOT EXISTS during comparison. Fixed CI must be checked independently.

A new opt-in local BEFORE UPDATE OF trigger forbids direct changes to seven structural reservation fields: idempotency_key, organization, delegate, connector, capability, generation and nonce. This addresses the direct generation-column bypass observed in C2.33 **when the C2.34 trigger is installed**. Tests verify refusal for every field, legitimate no-execution logged close/revoke, and detection of dropped or modified trigger definitions. Workflow executes C2.34 and C2.33/C2.32 regressions.

Limitations: trigger installation remains explicit/fixture-only, not universal, and owners can remove triggers, replace database files or rewrite events. The control is not an independent attestation or tamper-proof ledger. No external provider egress, no real organizational authority, no kernel/main/Monde changes. Next: unify hardened fixture initialization and test against privileged storage bypass with independent evidence/checkpoints.
