# V0.1 C2.25 — offline reservation recovery audit

Status: DRAFT / FAIL-CLOSED / NO PROVIDER EGRESS.

Parent C2.24 HEAD f5b5c45518388b0faa791ac19432a27e7bbce50e. Previous C2.23/C2.24 CI runs #37732701504, #37732814155, #37732808841 were still queued when this work started and are not claimed green.

A read-only recovery inspector checks durable SQLite lifecycle state and the deterministic SHA-256 fixture receipt. Unknown or RESERVED_NO_EXECUTION reservations require manual review (never auto-retry); INVALIDATED records remain blocked. CLOSED_NO_EXECUTION and ABANDONED_NO_EXECUTION must have matching receipt hash and exact status; missing/tampered receipts are rejected. All outcomes are BLOCK with egress_allowed=False and automatic_retry=False.

Tests exercise restart with unfinished reservation, persisted closure, corrupted/missing receipt, and revocation before recovery.

Limitation: receipt hash is not an independent signature or live provider delivery confirmation. Direct modifications to the same SQLite database can replace both status and hash. There is no remote trusted identity, shared distributed revocation/dispatch fence, atomic provider delivery, permission or recovery job. This is a local, deny-only forensic audit. No main merge, kernel, Monde or connector calls.
