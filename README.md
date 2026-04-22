# Obsidia X-108 Public Proofs

Public proof and verification repository for the deterministic governance core of Obsidia.

## What this repository is
This repository contains the public verification perimeter of Obsidia X-108:
- Lean 4 formal proofs
- TLA+ / TLC model checking
- Python verifiers
- public Sigma minimal layer
- RFC3161 / TLC / Sigma cross-platform QA
- public runner: run_all_proofs.ps1

This is a public verification repository, not the full proprietary production engine.

## What is verified
- Lean 4 builds successfully
- TLC runs complete on the public specs
- verify_all.py passes
- verify_decision.py passes on canonical scenarios
- Sigma public smoke tests pass
- RFC3161 anchor schema tests pass
- cross-platform QA passes
- run_all_proofs.ps1 completes end-to-end

## Quick start
Prerequisites:
- Python 3.11+ recommended
- Java 17+
- Lean 4 + Lake
- tla2tools.jar available in %USERPROFILE%

Run all public proofs:
.\run_all_proofs.ps1

Expected result:
- TLC: no error found
- Lean: build completed successfully
- verify_all: PASS
- verify_decision: VALID
- Sigma tests: PASS
- RFC3161 anchor tests: PASS
- final runner line: === DONE ===

## Repository map
- proofs/lean/             Lean 4 formal proof perimeter
- formal/tla/              TLA+ specifications and TLC logs
- proofs/                  Python verifiers and proof report
- sigma/                   public Sigma minimal layer and tests
- qa/cross-platform/       RFC3161 / TLC / Sigma QA
- run_all_proofs.ps1       public end-to-end runner

See also:
- P1_FREEZE_NOTE.md
- PUBLIC_STATUS.md
- REPO_MAP.md
- KNOWN_LIMITS.md

## Scope of P1
P1 covers:
- public proof perimeter
- public verification perimeter
- reproducible local execution
- local/remote repository consistency
- public QA and public runner

P1 does not cover:
- full production deployment
- full business adapters
- complete institutional operator surface
- permanent availability of external TSA providers
- full multi-domain operating system layer

## Current status
P1 is closed.

Reference:
- branch: main
- canonical technical closure commit: bd87e15