# C2.35 — Unified SQLite guard initialization (offline fixture)

Status: DRAFT / FAIL-CLOSED / NO PROVIDER EGRESS.

Parent C2.34 HEAD cef51ec789263e93c98760755bf7df15bb88cd85 at branch creation, with subsequent fixes reaching cef51ec789263e93c98760755bf7df15bb88cd85. The target CI C2.34 #37807644863 and C2.33 #37807645159 were still queued at start; do not claim success without verification.

UnifiedOfflineSqliteGuardsV0 offers one explicit fixture installer that installs C2.30 journal/receipt triggers, C2.32 reservation status-update trigger, and C2.34 immutable binding trigger, then checks the C2.31, C2.32 and C2.34 definition inspectors. Missing or modified guards return BLOCK; local consistency is reported as BLOCK with no execution authority. Tests cover missing-guard startup, repeated installation, trigger deletion detection, and no-execution logged closure.

Caveats: this is an opt-in initializer; it does not yet automatically intercept all repository runtime callers or prevent direct writes before initialization. The installation consists of multiple database connections rather than one atomic migration. Privileged database owners can drop triggers or rewrite database files; no independent attestation or external cryptographic anchor exists. Trigger presence alone must never be interpreted as authorization. No merge to main, kernel changes, Monde changes or live connectors.

Next: fail-closed pre-operation initialization boundary, crash-safe migration and negative startup/concurrent installer tests.
