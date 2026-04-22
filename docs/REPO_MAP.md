# Detailed Repository Map

## Purpose

This file helps an external reader navigate the public P1 repository.

## Root facade

- `README.md` - landing page for the public repository
- `PUBLIC_STATUS.md` - public PASS / scope matrix
- `P1_FREEZE_NOTE.md` - freeze reference for P1

## Public proof perimeter

- `proofs/lean/` - Lean 4 formal proof perimeter
- `formal/tla/` - TLA+ specifications and TLC runs
- `proofs/` - public executable verifiers and public proof report

## Public Sigma perimeter

- `sigma/run_pipeline.py` - public Sigma pipeline entry
- `sigma/sigma_monitor.py` - public Sigma monitor entry
- `sigma/examples/` - public example inputs
- `sigma/tests/` - public Sigma smoke and structure tests

## Public QA perimeter

- `qa/cross-platform/test_rfc3161_cross_platform.py` - public RFC3161 / TLC / Sigma QA
- `qa/cross-platform/test_rfc3161_anchor_schema.py` - RFC3161 public anchor schema checks

## Documentation perimeter

- `docs/SIGMA.md` - Sigma public P1 vs production scope
- `docs/LIMITS.md` - structural limits of P1
- `docs/PROOF_SCOPE.md` - proof scope taxonomy
- `docs/RFC3161.md` - RFC3161 interpretation guide
- `docs/REPO_MAP.md` - this file

## Reading paths by profile

Fast reader:
1. `README.md`
2. `PUBLIC_STATUS.md`
3. `P1_FREEZE_NOTE.md`

Auditor:
1. `PUBLIC_STATUS.md`
2. `docs/PROOF_SCOPE.md`
3. `docs/RFC3161.md`
4. run `.\run_all_proofs.ps1`

Sigma reader:
1. `docs/SIGMA.md`
2. `sigma/run_pipeline.py`
3. `sigma/sigma_monitor.py`
4. `sigma/tests/`

Proof-oriented reader:
1. `proofs/lean/`
2. `formal/tla/`
3. `proofs/verify_all.py`