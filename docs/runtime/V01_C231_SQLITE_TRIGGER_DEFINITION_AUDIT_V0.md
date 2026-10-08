# C2.31 — SQLite trigger definition integrity audit

Parent C2.30: 4723db58d147af40183df434655266da58aa966c. Its workflows #37733567028 and #37733562490 were queued at first check; no green claim.

The read-only C2.31 check inspects sqlite_master trigger SQL for expected target tables, UPDATE/DELETE verbs and RAISE(ABORT) rules, and reports missing or altered trigger definitions. Tests compare the unmodified trigger set against an altered trigger and a dropped trigger. All outcomes remain BLOCK and forbid egress.

Security limitation: this is structural SQL inspection, not a canonical SQL AST comparison or tamper-proof external attestation. Unexpected additional clauses may pass; a privileged database administrator can rewrite both data and trigger definitions. Direct UPDATE of reservation status is still not guarded at write time; introduce an audited storage-level write path and explicit transaction-scoped enforcement before a stronger guarantee. No kernel, main, Monde or connector changes.
