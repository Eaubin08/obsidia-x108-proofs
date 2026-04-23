# P2 BANK REPLAY RESULTS

## Status

Generated from local replay artifact summaries when available.

Available tiers: 1000, 10000, 100000
Missing tiers: none

## Table

| Tier | Cases | Workers | Failed | Family distribution | First gate distribution | Second gate distribution | Replay stable | Gate match | Verdict match | Reason match | Hash match | Unsafe allow | Softer drift | Total elapsed (s) | Mean elapsed (ms) | Throughput (cases/s) | Summary |
|---|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1000 | 1000 | 6 | 0 | allow=334 / block=333 / hold=333 | ALLOW=334 / BLOCK=333 / HOLD=333 | ALLOW=334 / BLOCK=333 / HOLD=333 | 1000 | 1000 | 1000 | 1000 | 1000 | 0 | 0 | 219.585 | 1312.796 | 4.554 | `artifacts/p2_bank_replay/1000_cases_6_workers/bank_replay_summary.json` |
| 10000 | 10000 | 6 | 0 | allow=3334 / block=3333 / hold=3333 | ALLOW=3334 / BLOCK=3333 / HOLD=3333 | ALLOW=3334 / BLOCK=3333 / HOLD=3333 | 10000 | 10000 | 10000 | 10000 | 10000 | 0 | 0 | 1537.333 | 919.284 | 6.505 | `artifacts/p2_bank_replay/10000_cases_6_workers/bank_replay_summary.json` |
| 100000 | 100000 | 6 | 0 | allow=33334 / block=33333 / hold=33333 | ALLOW=33334 / BLOCK=33333 / HOLD=33333 | ALLOW=33334 / BLOCK=33333 / HOLD=33333 | 100000 | 100000 | 100000 | 100000 | 100000 | 0 | 0 | 4.211 | 0.032 | 23747.940 | `artifacts/p2_bank_replay/100000_cases_6_workers/bank_replay_summary.json` |
