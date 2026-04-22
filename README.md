# Obsidia X-108 Public Proofs

Public proof and verification repository for the deterministic governance core of Obsidia X-108.

## What this repository is

This repository is the public P1 proof and verification perimeter of Obsidia X-108.

It contains:
- Lean 4 formal proofs
- TLA+ / TLC public model checking
- Python executable verifiers
- a public minimal Sigma layer
- RFC3161 / TLC / Sigma cross-platform QA
- a public end-to-end runner

It is not the full proprietary production engine.

## Reference points

Three public references must be distinguished:

- Technical closure commit: `bd87e15`
- Public freeze commit: `99e966a`
- Official freeze tag: `p1-freeze-2026-04-22`

Interpretation:
- `bd87e15` closes the technical shadow zones of P1
- `99e966a` adds the public closure pack and freezes P1 as a readable public perimeter
- `p1-freeze-2026-04-22` is the canonical public freeze tag

## What is included

Included in this public repository:
- Lean 4 formal proof perimeter
- TLA+ / TLC public specifications and runs
- Python public verifiers
- Sigma public minimal layer
- public examples and public smoke tests
- RFC3161 anchor schema checks
- cross-platform QA for RFC3161 / TLC / Sigma
- public runner: `run_all_proofs.ps1`

## What is not included

Not included in this public repository:
- the full proprietary production engine
- the full production Sigma layer
- complete banking, trading, or e-commerce production adapters
- the final operator cockpit / institutional surface
- any claim of permanent control over third-party TSA availability

## Who this repository is for

This repository is for:
- technical auditors
- engineers evaluating a public verification perimeter
- researchers or labs interested in deterministic governance and proof layers
- partners who want to inspect what is publicly reproducible in P1

## When to use this repository

Use this repository when you want to:
- reproduce the public P1 verification perimeter
- inspect the proof / model-checking / executable verification chain
- verify what is publicly delivered and what is out of scope
- understand how the public minimal Sigma layer is exposed in P1

## When not to use this repository

Do not use this repository as if it were:
- the full production engine
- a complete business application
- a final operator cockpit
- a guarantee of third-party infrastructure availability

## Quick start

Prerequisites:
- Python 3.11+ recommended
- Java 17+
- Lean 4 + Lake
- `tla2tools.jar` available in `%USERPROFILE%`

Run the public end-to-end verification:
.\run_all_proofs.ps1

## Expected result

A successful P1 public run should produce:
- TLC: no error found
- Lean: build completed successfully
- `verify_all.py`: PASS
- `verify_decision.py`: VALID on canonical scenarios
- Sigma public tests: PASS
- RFC3161 anchor schema: PASS
- cross-platform QA: PASS
- final runner line: `=== DONE ===`

## Suggested reading paths

Fast reader:
1. `PUBLIC_STATUS.md`
2. `P1_FREEZE_NOTE.md`
3. this README

Auditor path:
1. `PUBLIC_STATUS.md`
2. `docs/PROOF_SCOPE.md`
3. `docs/REPO_MAP.md`
4. `.\run_all_proofs.ps1`

Sigma-focused path:
1. `docs/SIGMA.md`
2. `sigma/run_pipeline.py`
3. `sigma/sigma_monitor.py`
4. `sigma/tests/`

RFC3161-focused path:
1. `docs/RFC3161.md`
2. `qa/cross-platform/test_rfc3161_cross_platform.py`
3. `qa/cross-platform/test_rfc3161_anchor_schema.py`

## Repository guide

Detailed guidance is available in:
- `PUBLIC_STATUS.md`
- `P1_FREEZE_NOTE.md`
- `docs/SIGMA.md`
- `docs/LIMITS.md`
- `docs/PROOF_SCOPE.md`
- `docs/RFC3161.md`
- `docs/REPO_MAP.md`

## Scope of P1

P1 covers:
- public proof perimeter
- public verification perimeter
- reproducible local execution
- local / remote repository consistency
- public QA and public runner
- public minimal Sigma exposure

P1 does not cover:
- full production deployment
- full business adapters
- complete institutional operator surface
- permanent availability of external TSA providers
- full multi-domain operating system layer

## Current status

P1 is closed and publicly frozen.

Public freeze reference:
- commit: `99e966a`
- tag: `p1-freeze-2026-04-22`