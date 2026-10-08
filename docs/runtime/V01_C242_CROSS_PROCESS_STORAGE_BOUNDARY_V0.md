# C2.42 — Cross-process SQLite storage boundary audit

Status: DRAFT / FAIL-CLOSED / OFFLINE FIXTURE ONLY.

Parent C2.41 HEAD 24cd3acc1a17956d7c5e99e6c1b53eebb541ef4b; both C2.41 targeted CI runs #37811158491 and #37811147040 completed SUCCESS.

Adds a deny-only local SQLite storage boundary inspector that validates the seven canonical triggers under BEGIN IMMEDIATE. If another process holds a write transaction, inspection returns BLOCK:C242_STORAGE_LOCKED_OR_UNAVAILABLE (1-second busy timeout). A successful check still returns BLOCK:C242_LOCAL_GUARDS_PRESENT_NOT_PROCESS_ISOLATED, never permission to act.

Tests launch a separate multiprocessing worker holding BEGIN IMMEDIATE to demonstrate cross-process contention, verify unchanged local trigger catalog, drop a trigger, and demonstrate that direct SQL can add scopes without going through the guarded facade. CI also includes C2.41 regression tests.

**Security boundary:** SQLite locking coordinates ordinary connections on the same local filesystem but is not process isolation, authentication, immutable evidence or filesystem tamper protection. A privileged actor with raw database access can write scopes, drop triggers or replace database files. Further isolation would require operating system access separation and a dedicated storage service, with independently anchored receipts. No external execution, provider connector, main merge, kernel or Monde changes.
