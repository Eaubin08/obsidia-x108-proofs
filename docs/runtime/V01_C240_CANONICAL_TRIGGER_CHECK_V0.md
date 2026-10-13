# C2.40 — Canonical legacy SQLite trigger definitions within locked writes

DRAFT / OFFLINE / FAIL-CLOSED. Parent C2.39 HEAD 2a702c2f8b93ccf81192586bb9a0178c8e8ba335, targeted CI #37809442452 SUCCESS.

C2.38 TransactionGuardedReservationV0 now compares normalized definitions of all five C2.30 legacy journal/receipt triggers against their canonical SQL, under the same BEGIN IMMEDIATE transaction as local fixture writes. Previously, the check merely searched for an expected table/verb/ABORT token and could be bypassed by a trigger with extra SQL instructions. C2.32/C2.34 full trigger checks are retained.

Adversarial tests replace each legacy trigger with a keyword-preserving body containing an extra statement and require BLOCK without scope enrollment. Dedicated CI also runs C2.38/C2.39 regressions. Status remains BLOCK/no-execution regardless of trigger consistency.

Limitation: normalized SQL text comparison is not a complete SQL parser and relies on application code as the reference. The storage owner may replace both database and application, and alternative raw SQLite/base API paths remain accessible. No external attestation, permission grant, provider dispatch, kernel, Monde or main change.

Next: ensure full trigger catalog inspection is reused consistently by all gated entrypoints and verify cross-process/trigger-swap race behavior under locked local transactions.
