# C2.38 — same-transaction guard verification and offline writes

Status: DRAFT / FAIL-CLOSED / no external action. Parent C2.37 SHA b7faa478c2706de9d69af7e1b33110f46e3b6477, CI #37808727098 SUCCESS.

Introduces TransactionGuardedReservationV0 as a subclass of the local atomic reservation journal. Under each local BEGIN IMMEDIATE write transaction, it checks the C2.30 legacy trigger catalog plus canonical C2.32/C2.34 trigger definitions before insert, close or revoke. Enrollment is also checked within a locked transaction. The existing C2.36 façade now routes its reservation operations through this subclass. Tests verify normal logged reserve/close, refusal without DB mutation after guard removal, refused revoke after guard removal, and façade routing.

This removes the separate check/write TOCTOU *within these opted-in write paths* against other ordinary SQLite connections, since BEGIN IMMEDIATE serializes competing writers. It is not a global enforcement mechanism: the unguarded base-class API and direct SQLite access remain possible. Trigger names/bodies can be replaced by a privileged DB actor, who can also rewrite the database file; legacy trigger validation is structural, not canonical. No trusted independent signer, provider receipts, distributed fence or execution permission. No kernel/Main/Monde changes.

Next: deny direct lower-layer access in the production-facing entrypoint, strengthen canonical trigger inspections, then review queued dependent PR CI before any merge.
