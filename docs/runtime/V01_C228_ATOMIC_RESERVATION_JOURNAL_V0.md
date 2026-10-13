# C2.28 — atomic local reservation + hash-journal fixture

Status: DRAFT, fail-closed, no external calls.

Parent C2.27 HEAD e8cbfc1d9145b0b3662c8213d8384ebde08c332d. C2.27 CI runs 37733144873/37733140341 were still queued when build began.

Adds AtomicOfflineReservationJournalV0 backed by one SQLite file. Each *logged* reservation, no-execution closure and revocation invalidation updates reservation state and appends a hash-chained event within the same BEGIN IMMEDIATE transaction. Tests check persistence after restart, revocation journaling, direct unjournaled mutation, inherited unjournaled closure detection, and duplicate rollback. Verification compares the latest logged state with the reservation state and always returns BLOCK.

Caveats: inherited public fixture methods such as close_fixture remain accessible and can mutate state without appending an event (detected in a later audit, not blocked at write time). This is not yet a universal enforced API for all writes. The journal remains locally rewritable: coordinated rewriting of both tables and hashes cannot be detected without an independent trusted anchor. No trusted organizational identity, external dispatch fence, kernel mutation, provider receipts or connector calls. No merge to main or Monde changes.
