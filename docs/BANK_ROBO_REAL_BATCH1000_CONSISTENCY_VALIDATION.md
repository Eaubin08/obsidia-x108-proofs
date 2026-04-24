# BANK_ROBO_REAL_BATCH1000_CONSISTENCY_VALIDATION

## Freeze date

2026-04-24 10:54:28

## Scope

Nominal bank-robo real batch 1000 only.
Fault injection is explicitly out of scope for this freeze.

## Evidence

RunDir: C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\artifacts\bank_robo_real\batch_probe\20260424-014052
Summary: C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\artifacts\bank_robo_real\batch_probe\20260424-014052\consistency_summary.json
Rows: C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\artifacts\bank_robo_real\batch_probe\20260424-014052\consistency_rows.jsonl

## Observed summary

status: ok
db_status.ok: True
db_status.count: 3251
total: 1000
match: 1000
mismatch: 0
classes.MATCH: 1000
recent_route_available: True

## Proven at this stage

- processTransaction is coherent with getRecentTransactions on this batch.
- getRecentTransactions is coherent with the real DB on this batch.
- No mismatch was detected across 1000 nominal calls.
- Runtime / recent route / DB tell the same story on this run.

## Explicitly not frozen here

- DB_MISSING_ENV
- DB_INVALID_URL
- OAUTH_MISSING
- GEMINI_MISSING
- fault injection interpretation

## Verdict

Bank-robo real nominal batch 1000 consistency validated.
