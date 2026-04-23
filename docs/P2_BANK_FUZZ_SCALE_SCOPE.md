# P2 Bank Fuzz Scale Scope

## Status

P2 BANK / FUZZ SCALE PACK

## Purpose

This layer measures hostile-input bank behavior under larger synthetic fuzz workloads.

Validated public tier:
- 1k cases

Ready-to-run tiers:
- 10k cases
- 100k cases

## Invariants

- unsafe allow count
- softer drift count
- clean rejection count
- safe non-allow count
- failures
- throughput
- family coverage
- gate distribution

## Reading rule

The 1k tier is the public validation tier.
10k and 100k are stress tiers and may be long on a local subprocess runner.
