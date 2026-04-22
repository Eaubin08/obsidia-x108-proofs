# P2 Bank Scale Scope

## Status

P2 BANK / SCALE / STRESS PACK

## Purpose

This layer measures public bank runner behavior under larger synthetic workloads.

Validated public tier:
- 1k cases

Ready-to-run tiers:
- 10k cases
- 100k cases

## Metrics

- total runtime
- mean latency
- throughput
- failures
- gate distribution
- no-softer drift
- family distribution

## Reading rule

The 1k tier is the public validation tier.
10k and 100k are stress tiers and may be long on a local sequential/subprocess runner.
