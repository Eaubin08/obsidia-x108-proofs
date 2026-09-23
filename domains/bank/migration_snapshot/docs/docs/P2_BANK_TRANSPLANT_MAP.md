# P2 Bank Transplant Map

## Purpose

This file records the raw source files transplanted into `obsidia-x108-proofs`
before adaptation for P2 Bank.

## Raw source imports

### 1. Standard / canon
Source repo:
- `Eaubin08/Obsidia-lab-trad`

Source file:
- `docs/standards/X108_STANDARD.md`

Imported to:
- `docs/sources/Obsidia-lab-trad/X108_STANDARD.md`

Role:
- canonical X-108 standard
- decision taxonomy
- fail-closed reading
- audit / conformance vocabulary

### 2. Real bank cases
Source repo:
- `Eaubin08/obsidia-engine-proof-core`

Source file:
- `REAL_CASES.md`

Imported to:
- `docs/sources/obsidia-engine-proof-core/REAL_CASES.md`

Role:
- reproducible real cases
- bank suspicious / hold
- guard / block logic
- reproduction commands

### 3. Bank business facade
Source repo:
- `Eaubin08/bank-robo`

Source files:
- `README.md`
- `server/bankingEngine.ts`

Imported to:
- `docs/sources/bank-robo/README.md`
- `docs/sources/bank-robo/bankingEngine.ts`

Role:
- bank business grammar
- readable output facade
- business metrics and decision framing

## Reading rule

These imported files are raw source material.

They are not yet the final canonical P2 Bank public layer.

The next step is:
- extract
- adapt
- freeze