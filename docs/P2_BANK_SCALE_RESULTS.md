# P2 Bank Scale Results

## Status

Snapshot generated from local scale artifact summaries.

Available tiers: 1000, 10000, 100000
Missing tiers: none

## Results

| Tier | Cases | Workers | Failed | Family distribution | Gate distribution | Gap distribution | Total elapsed (s) | Mean elapsed (ms) | Throughput (cases/s) | Summary |
|---|---:|---:|---:|---|---|---|---:|---:|---:|---|
| 1000 | 1000 | 6 | 0 | allow=334 / hold=333 / block=333 | ALLOW=334 / HOLD=333 / BLOCK=333 / ERROR=0 | MATCH=1000 / HARDER_THAN_BUSINESS=0 / SOFTER_THAN_BUSINESS=0 / UNKNOWN=0 | 49.375 | 294.739 | 20.253 | `artifacts/p2_bank_scale/1000_cases_6_workers/bank_scale_summary.json` |
| 10000 | 10000 | 6 | 0 | allow=3334 / hold=3333 / block=3333 | ALLOW=3334 / HOLD=3333 / BLOCK=3333 / ERROR=0 | MATCH=10000 / HARDER_THAN_BUSINESS=0 / SOFTER_THAN_BUSINESS=0 / UNKNOWN=0 | 516.334 | 308.456 | 19.367 | `artifacts/p2_bank_scale/10000_cases_6_workers/bank_scale_summary.json` |
| 100000 | 100000 | 6 | 0 | allow=33334 / hold=33333 / block=33333 | ALLOW=33334 / HOLD=33333 / BLOCK=33333 / ERROR=0 | MATCH=100000 / HARDER_THAN_BUSINESS=0 / SOFTER_THAN_BUSINESS=0 / UNKNOWN=0 | 6205.048 | 370.919 | 16.116 | `artifacts/p2_bank_scale/100000_cases_6_workers/bank_scale_summary.json` |

## Reading rule

- 1k = public validation tier
- 10k = local auto-validation tier
- 100k = execution/stress tier

## Artifact pointers

- 1000 → summary: `artifacts/p2_bank_scale/1000_cases_6_workers/bank_scale_summary.json`
  - report_json: `artifacts/p2_bank_scale/1000_cases_6_workers/bank_scale_report.json`
  - report_csv: `artifacts/p2_bank_scale/1000_cases_6_workers/bank_scale_report.csv`
- 10000 → summary: `artifacts/p2_bank_scale/10000_cases_6_workers/bank_scale_summary.json`
  - report_json: `artifacts/p2_bank_scale/10000_cases_6_workers/bank_scale_report.json`
  - report_csv: `artifacts/p2_bank_scale/10000_cases_6_workers/bank_scale_report.csv`
- 100000 → summary: `artifacts/p2_bank_scale/100000_cases_6_workers/bank_scale_summary.json`
  - report_json: `artifacts/p2_bank_scale/100000_cases_6_workers/bank_scale_report.json`
  - report_csv: `artifacts/p2_bank_scale/100000_cases_6_workers/bank_scale_report.csv`
