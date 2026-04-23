# P2 Bank Shadow Mode Scope

## Status

P2 BANK / SHADOW MODE / PRE-REAL

## Purpose

This layer connects the bank decision membrane to real observed inputs without allowing any real execution.

## Rule

No real action is ever executed in shadow mode.

The engine may:
- ingest real observed bank inputs
- compute verdicts
- emit x108 gates
- emit reason codes
- emit traces
- compare against real-world downstream outcomes

The engine may not:
- authorize execution
- trigger transfer
- call external action endpoints
- mutate production state

## Outputs

For each observed real case:
- timestamp
- input snapshot reference
- market verdict
- x108 gate
- reason code
- severity
- trace id
- decision id
- attestation ref if available
- observed real-world downstream label if available

## Metrics

- total observed cases
- allow / hold / block distribution
- false permissive count
- false block count
- false hold count
- unknown / incomplete input count
- replayable trace coverage
- no execution guarantee

## Acceptance before real branch

- no real execution path enabled
- full trace generation
- replayable decision logs
- explicit separation between observed reality and engine verdict
- manual review path on every case
- switchable ON/OFF shadow mode
