# P2 Bank Scope

## Status

P2 BANK OPENING

## Purpose

P2 Bank opens the first governed business world on top of the closed public P1 perimeter.

The source material for this opening is explicitly transplanted in:
- `docs/sources/Obsidia-lab-trad/X108_STANDARD.md`
- `docs/sources/obsidia-engine-proof-core/REAL_CASES.md`
- `docs/sources/bank-robo/README.md`
- `docs/sources/bank-robo/bankingEngine.ts`

## What P2 Bank shows

P2 Bank shows that the public perimeter can expose a first governed banking world with:
- structured bank inputs
- governed outputs
- X-108 gate reading
- trace and attestation fields
- public Sigma interpretation

## What P2 Bank does not claim

P2 Bank does not claim:
- a full production banking system
- a licensed banking platform
- a final institutional cockpit
- full proprietary engine publication
- complete business deployment

## Canonical reading rule

Read P2 Bank in this order:
1. business context
2. `x108_gate`
3. `severity`
4. `reason_code`
5. trace / attestation
6. Sigma stability

The sovereign field is:
- `x108_gate`

The business-facing field is:
- `market_verdict`

If the two appear softer/harder than each other, the sovereign reading remains `x108_gate`.

## Public entry points

- `python .\sigma\run_pipeline.py bank .\sigma\examples\bank_normal.json`
- `python .\sigma\run_pipeline.py bank .\sigma\examples\bank_suspicious.json`
- `python .\sigma\run_pipeline.py bank .\sigma\examples\bank_blocked.json`
- `python -W ignore -m pytest .\sigma\tests\test_bank_world.py -v`

## Files added by P2 Bank opening

- `docs/P2_BANK_SCOPE.md`
- `docs/BANK_SCENARIOS.md`
- `docs/BANK_OUTPUTS.md`
- `sigma/examples/bank_blocked.json`
- `sigma/tests/test_bank_world.py`

## Closure target

P2 Bank is structurally open when:
- 3 canonical bank scenarios exist
- the reader can understand the outputs
- the reader can reproduce the scenarios locally
- the world is readable without oral explanation
