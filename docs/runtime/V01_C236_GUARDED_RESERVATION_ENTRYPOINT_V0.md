# C2.36 — Guarded offline reservation entrypoint

Status: DRAFT / FAIL-CLOSED / NO PROVIDER EGRESS.

Parent C2.35 head cc90fe7049a75c3ad3dc2275fd3feb6f17714940. The targeted C2.35 run #37807975120 was QUEUED when work began, so no green status is assumed.

GuardedOfflineReservationV0 is an opt-in façade around the atomic local reservation journal and the C2.35 unified SQLite guard verifier. Prior to enroll, reserve, close, revoke and inspect it verifies presence of C2.30, C2.32 and C2.34 triggers. Missing/altered trigger definitions lead to BLOCK:C236_GUARDS_NOT_READY without exercising the requested fixture operation. Fixture initialization is explicit, and startup without initialization blocks. Tests exercise startup, restart, trigger removal and concurrent install attempts.

Limitations: this is a best-effort local fixture façade, not a mandatory kernel/runtime boundary. Callers can bypass it by accessing lower layers or SQLite directly. Verification and operation use separate DB transactions, so a privileged actor can modify/drop triggers after verification (TOCTOU). Concurrent initialization is covered by a targeted test but requires successful CI before being claimed reliable. C2.35 installation uses multiple DB connections and is not one atomic migration. No independent attestation, external trusted identity, provider dispatch or action authority. No main merge, kernel or Monde changes.

Next: unify inspection and operation in one SQLite transaction and enforce a crash-safe installer, without widening permissions.
