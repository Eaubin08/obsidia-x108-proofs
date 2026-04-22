# P2 Bank Scenario Benchmark Scope

## Status

P2 BANK / BANK-ROBO SCENARIO BENCHMARK

## Purpose

This layer imports the 23 public business scenarios from `bank-robo`
and replays them through the public X-108 bank perimeter.

The benchmark is not a claim of strict production equivalence between:
- bank-robo business scenarios
- obsidia-x108-proofs public bank pipeline

It is an annotated comparison layer.

## Output columns

Each replayed case records:
- scenario_name
- business_expected_decision
- x108_gate_observed
- severity
- reason_code
- gap_status

## Gap status meaning

- MATCH
- HARDER_THAN_BUSINESS
- SOFTER_THAN_BUSINESS
- UNKNOWN_MAPPING

## What this benchmark proves

It proves that:
- the 23 business scenarios are imported as raw source material
- they can be replayed through the public bank pipeline
- the public X-108 perimeter can be compared against business expectations
- the comparison is batchable, reproducible and auditable

## What this benchmark does not prove

It does not prove:
- exact equivalence between bank-robo and X-108 internals
- regulatory approval
- production deployment readiness