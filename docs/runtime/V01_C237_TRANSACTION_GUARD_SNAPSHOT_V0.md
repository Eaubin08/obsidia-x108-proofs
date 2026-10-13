# C2.37 — Transaction-locked guard inspection and reservation snapshot

Status: DRAFT / FAIL-CLOSED / LOCAL FIXTURE. Parent C2.36 HEAD deb73efe0262a828726a686b98ada21175667cbf; its workflow #37808353926 is SUCCESS.

Adds a readonly inspection of installed C2.30/32/34 SQLite triggers plus the reservation status under one BEGIN IMMEDIATE connection, preventing concurrent SQLite writers during that snapshot. Missing or modified triggers, missing reservations, DB errors and lock contention all return BLOCK; a successful snapshot also returns BLOCK and never grants authority. Tests cover normal snapshot, trigger loss, unknown reservation and concurrent lock contention. C2.36 regression included in CI.

LIMIT: C2.37 is NOT yet a transactional **guard-check + reservation write**. The method commits immediately after read; C2.36 operations still use independent guard-check and update transactions, so their TOCTOU gap remains. C2.30 legacy trigger validation here is structural, not full authenticated SQL validation. The SQLite owner can drop triggers or replace DB. No independent attestation, provider egress, main merge, kernel or Monde modification.

Next: integrate guard validation inside the same BEGIN IMMEDIATE transaction as an actual local reservation/close/revoke state change, rather than calling two separate routines.
