# C2.29 — Route legacy fixture writers through journal

Status: DRAFT / FAIL-CLOSED / NO EGRESS.

Parent C2.28 commit 2794bba3373e71c4e83f6ee5b24fc7cb7cc92e92. Its targeted CI #37733270389 was queued when this milestone began.

Overrides the inherited reserve_fixture and close_fixture entrypoints of AtomicOfflineReservationJournalV0 so they call their logged atomic counterparts. A duplicate insert is caught as a deterministic BLOCK with rollback (no additional journal event). Tests verify inherited calls are journaled, duplicate attempts blocked, forbidden execution disposition rejected, and existing C2.28 tests updated to the new interface.

Limit: direct SQLite writes, deliberate calls to base-class methods or arbitrary custom code are not prevented by Python method overrides. Therefore this is an API-level fixture hardening step, not a storage-level append-only or database-trigger enforcement. Journal integrity remains locally recomputable by a malicious writer. Does not grant organization authority, alter kernel, deploy Monde, touch main, or dispatch provider calls.
