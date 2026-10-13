# C2.44 — Separate offline storage worker process (IPC fixture)

Status: DRAFT / FAIL-CLOSED / NO PROVIDER EGRESS.

Parent C2.43 HEAD 36902cf5fae2e00292120ef694eb0ca2bb88f17e. Its targeted CI #37811968910 was still QUEUED when C2.44 started.

OfflineStorageWorkerV0 runs OfflineStorageServiceV0 in a separate multiprocessing.Process with local request and response queues. The client supports only initialize_fixture, enroll, reserve, close, revoke and inspect. Unknown methods are rejected; the worker delegates field allowlisting to C2.43 and transaction-guarded SQL writes to C2.38+. Startup without a worker, forced termination and communication timeout fail closed. Tests cover process restart with persisted reservation, abnormal shutdown, disallowed SQL and extra fields. CI includes C2.43 regressions.

Critical limitations: multiprocessing IPC queues are not authenticated, do not enforce OS principal separation and are not a privilege boundary. The parent knows the SQLite path and can still access it directly. Calls have no durable request IDs, exactly-once delivery, crash-consistent response association or replay journal; IPC timeouts can leave a completed reservation with a lost response. Do not use for production execution. There is no network listener, external provider call, production credential, trusted issuer or permission to ACT. No main merge, kernel or Monde modification.

Next: test ambiguous IPC crash windows, idempotent recovery and permissions boundary via a restricted OS service account, without granting egress.
