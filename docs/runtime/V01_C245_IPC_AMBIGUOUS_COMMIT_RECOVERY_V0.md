# C2.45 — IPC ambiguous commit reconciliation (offline fixture)

Status: DRAFT / FAIL-CLOSED / NO EXTERNAL EXECUTION.

Parent C2.44 head 491eb8f774a3d92aa8639127074dbf5f38d30935. Targeted C2.44 CI #37812271891 SUCCESS; #37812281038 still queued at start.

The read-only reconciliation function looks up a reservation idempotency key through the C2.43 guarded storage API. It returns a deny-only explanation for known reserved, terminal, unknown and unavailable states, with automatic_retry=False in every outcome. Tests simulate the client losing a response after reservation commit by discarding the successful response, restarting its worker, reconciling, and confirming the same key cannot be reserved twice. Uninitialized storage also fails closed. C2.44 worker regression runs in the workflow.

IMPORTANT: this is a simulated lost reply, NOT fault injection that kills the worker between COMMIT and sending the IPC response. The C2.44 worker still has no durable request/response journal, authenticated OS IPC or exactly-once delivery. Reconciliation by key does not authorize action and an UNKNOWN result never automatically resends. The parent process still has DB path access and shared permissions. OS principal/file permission separation remains a separate follow-up, not implemented in this milestone. No main, kernel, Monde or provider connector changes.
