# C2.47 — IPC reply correlation fixture

Status: DRAFT / FAIL-CLOSED / NO PROVIDER EGRESS.

Parent C2.46 head f5995ff739780da00779e9afca3eabd12addb1a8. C2.46 targeted CI #37813012060 completed SUCCESS.

OfflineIPCReplyCorrelatorV0 tracks pending and completed request IDs in memory. It matches results by exact request ID, accepts out-of-order completion of two distinct IDs, rejects unknown or repeated replies, and refuses unrecognized result strings without clearing the pending request. Tests cover the correlation, duplicate/refused replay, and invalid execution result. C2.46 crash-injection tests are included in targeted CI.

**Limitations:** This is an isolated in-memory fixture, NOT yet wired into the C2.44 worker's multiprocessing queues; it is not a proof of production IPC behavior or simultaneous worker crash recovery. In-memory pending/completed IDs are lost after restart, and the legacy worker still reads the next response without a correlation inbox. IPC messages are not authenticated, and process concurrency is not globally coordinated. No automatic retry, durable response journal, external connector, permission to ACT, main merge, kernel or Monde changes.

Next: integrate matching into the actual IPC client with a safe response inbox and explicit timeout recovery; test multiple in-flight requests and worker failures.
