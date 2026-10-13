# C2.41 — Unified canonical SQL guard verification

Status: DRAFT / FAIL-CLOSED / LOCAL FIXTURE ONLY.
Parent C2.40 HEAD dabb5d24656f16956574fca795f102efa003b023. Both targeted C2.40 workflows #37810267122 and #37810258772 are SUCCESS.

The canonical SQL trigger catalog is now centralized and reused by C2.38 guarded reservation mutations, C2.35 unified guard inspection, and C2.37 transaction-locked snapshot. The check runs on the caller's existing SQLite connection for guarded writes/snapshots; the unified audit also uses a single BEGIN IMMEDIATE transaction. The catalog requires all seven local triggers' normalized definitions, not merely keywords. Tests verify keyword-preserving trigger replacement is refused by every guarded interface, and 12 concurrent duplicate reservation attempts yield exactly one no-execution reservation.

This is local textual SQL normalization, NOT cryptographic attestation or a complete SQL parser. Concurrent ordinary SQLite writers are serialized on the guarded write connection, but privileged file replacement, raw SQL/base-class entrypoints and database-owner tampering remain possible. The exposed APIs are offline test fixtures; status BLOCK and no external action permission. No merge to main, kernel, Monde or connector changes.

Next: assess process-isolated storage boundary and negative cross-process tamper tests. Ensure dependent DRAFT CI green before promotion.
