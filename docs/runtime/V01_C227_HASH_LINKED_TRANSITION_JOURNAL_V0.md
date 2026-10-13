# C2.27 — local hash-linked transition journal

Status: DRAFT / OFFLINE FIXTURE / FAIL-CLOSED / NO EGRESS.

Parent C2.26 HEAD 7267120ae88c6c20192617445302d589bb28c595. At the start of this step C2.25 #37732908021 and C2.26 #37733038703/#37733033550 remained queued, so no successful result is claimed for them.

The SQLite event journal appends monotonic sequence numbers and SHA-256 links between locally declared reservation lifecycle events. Tests cover restart, direct modification of an event, removal of a middle event, and exclusion of an EXECUTED event kind. The verifier always BLOCKS; a consistent journal returns C227_LOCAL_CHAIN_CONSISTENT_NOT_ATTESTED.

This is deliberately a standalone fixture journal, not yet integrated atomically with the C2.23/C2.24 reservation lifecycle or verified against actual reservation tables. A malicious writer can erase the journal or rewrite every event and recompute the hash chain; the local head hash has no independent trusted anchor or signer. A missing suffix of the journal may be indistinguishable from a genuinely shorter history without an external anchor. Future work requires atomic append with reservation transitions, external signed checkpoints, independent clock/issuer, rollback protection and retention policies. No main, kernel, Monde or provider connector changes.
