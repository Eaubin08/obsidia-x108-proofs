# C2.43 — Offline storage-service API boundary fixture

Status: DRAFT / FAIL-CLOSED / NO EXTERNAL ACTION. Parent C2.42 head eb1469bd2189cab67fdc9f182f19e9b2e8b385c0; CI #37811578105 SUCCESS.

Adds an explicit operation and field allowlist for a storage-facing Python wrapper around the C2.36 guarded offline reservation façade. Supported fixture methods: enroll, reserve, close, revoke and inspect. Rejects unknown methods, raw SQL requests, extra fields and malformed payloads. Tests verify startup refusal, no-execution reservation/restart/closure and denied arbitrary operations. C2.42 cross-process storage tests remain in targeted CI.

CRITICAL LIMITATION: this is only an in-process Python API contract. It does NOT isolate the SQLite file, use a separate service process, restrict OS/file permissions, authenticate clients, or prevent callers with Python/filesystem access from reaching the backend. No enforceable least-privilege boundary is established. Future milestone: separate OS process with restrictive database ownership and authenticated local IPC, test permission denial and crash/restart; an independent anchoring mechanism would still be required for tamper resistance. No merge to main, kernel/Monde mutation or provider dispatch.
