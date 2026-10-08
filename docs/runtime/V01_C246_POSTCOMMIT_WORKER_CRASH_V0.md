# C2.46 — Deterministic post-commit IPC crash injection

Status: DRAFT / FAIL-CLOSED / OFFLINE FIXTURE ONLY.

Parent C2.45 HEAD 2ffe096c741a75ad88a84dfa1c7b352b2aa22825; run #37812495453 was in progress at first inspection.

A dedicated local test-only worker handles reserve_then_crash: it commits the reservation through the existing guarded storage API, then immediately exits the process with os._exit(87) before it can send an IPC response. The client reports BLOCK:C246_AMBIGUOUS_IPC_RESPONSE. The test checks exit code 87, durable key reconciliation to RESERVED_NO_EXECUTION, automatic_retry=False and duplicate reservation BLOCK on a restarted worker. An uninitialized-worker case verifies fail-closed behavior. No provider action, dispatch or ACT state is reachable.

The crash hook fires after the reserve API reports successful commit; it is controlled fault injection, not arbitrary-time crash fuzzing. The IPC queue protocol remains unauthenticated; no exactly-once responses or durable response journal. Parent still knows SQLite path, and both processes share OS permissions. External anchoring and OS privilege isolation are not implemented. No main merge, KX108 or Monde changes.
