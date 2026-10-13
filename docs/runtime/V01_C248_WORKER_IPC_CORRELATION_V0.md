# C2.48 — actual offline worker IPC reply correlation

DRAFT, fail-closed, fixture only. Parent C2.47 CI #37813905100 SUCCESS.

The C2.44 OfflineStorageWorkerV0 client now serializes requests across concurrent callers with a per-client mutex and matches the received IPC response sequence to the current request. Replies with a different ID are discarded instead of incorrectly returned. Timeout remains BLOCK, with no automatic retries. Tests inject a stale response and run eight simultaneous reserve calls using a shared worker client: one reservation should succeed and seven should be rejected as duplicates. Crash regression for C2.46 and isolated C2.47 correlator tests are in the CI workflow.

Security limitations: per-client serialization reduces concurrency, and correlation IDs are not durable or authenticated. A timed-out request can still commit; manual idempotency-key reconciliation remains necessary. The client knows the SQLite path, both processes share OS permissions, and the transport provides no globally authenticated or isolated boundary. Malicious responses carrying the *same* sequence are not detected. No direct provider calls, no external execution authority, no kernel, Monde or main changes. Next: durable request/response journal, authenticated IPC and real OS permission separation, followed by consolidated PR/CI audit.
