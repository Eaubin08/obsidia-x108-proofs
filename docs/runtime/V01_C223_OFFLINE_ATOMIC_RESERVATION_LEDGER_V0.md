# V0.1 C2.23 — offline atomic reservation ledger

Status: DRAFT / FIXTURE ONLY / FAIL-CLOSED / NO PROVIDER EGRESS.

Parent C2.22 HEAD `c1072c2dfbe8284de02a9c98afec8957b16893fb`. CI #37732569195 completed SUCCESS; #37732574088 remained queued on initial check.

This isolated SQLite ledger uses `BEGIN IMMEDIATE` to check a fixture scope, revocation status and generation, and store a unique nonce and globally unique idempotency key in the same local transaction. A revoke transaction updates scope generation and invalidates outstanding local reservations in the same database. Tests cover restart persistence, duplicate requests under 24 concurrent threads, nonce/idempotency reuse, revocation and cross-tenant/incorrect generation.

A successful local reservation returns `RESERVED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY` and persists `RESERVED_NO_EXECUTION`, **never** an authorization to act or an execution attempt. Scope enrollment is fixture-controlled but not independent organizational authentication. This ledger does not coordinate multiple hosts or a real provider. It does not implement an atomic side-effect commit, cancellation acknowledgment or execution receipt. The caller must never convert a stored reservation into egress authority.

Still required: authenticated organization/issuer consent; immutable KX108 decision and ticket binding; a distributed revocation/dispatch fence; idempotency tied to actual provider state and durable receipts; failure recovery and execution-policy approval. No main merge, KX108 kernel, Monde or live connectors changed.
