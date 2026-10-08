# C2.39 — guarded boundary and SQLite bypass audit

Status: DRAFT / FAIL-CLOSED / fixture only.

Parent C2.38 HEAD 3c41fd86ef0cbcc550f0742af04ea9dd61daf780, targeted CI #37809160919 SUCCESS.

Tests establish that the C2.36 facade routes normal reservations through the C2.38 transaction-guarded subclass, drops of a required SQLite trigger are flagged and operations blocked, but arbitrary direct SQLite access to the same database still bypasses the facade. The new read-only C2.39 inspector returns BLOCK even for locally consistent guards. Its checks use separate connections and are not an atomic proof. The guarded C2.38 write path remains the narrower same-transaction gate.

No universal prevention of lower-layer Python calls, raw SQL, privileged trigger deletion, direct file replacement or coordinated event rehashing is claimed. Structural legacy trigger checks still need canonical hardening. For production use, isolate the database behind a process boundary with restricted OS credentials, and independently anchor proofs. There is no real connector, execution authority, main merge, KX108 or Monde modification.

Next: add a canonical trigger definition check within the C2.38 transaction and negative tests for malicious trigger-body replacement. Treat lower-layer bypass separately as a deployment trust-boundary issue, not something Python subclassing can solve.
