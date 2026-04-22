# P2 Bank Enterprise Scope

## Status

P2 BANK ENTERPRISE TEST PACK OPEN

## Purpose

This pack extends the first governed bank world into a wider enterprise-oriented validation layer.

It adds:
- 60 structured bank cases
- family distribution: 20 normal / 20 suspicious / 20 blocked
- expected minimum sovereign gate by case
- replayable batch execution
- JSON / CSV report outputs
- enterprise-oriented reproducibility

## What this pack proves

This pack publicly proves:
- the bank world is not limited to 3 showcase cases
- the sovereign gate stays coherent across larger batches
- risky profiles do not soften into direct permission
- hard blocked profiles remain blocked
- outputs stay traceable and attestable
- batch execution remains reproducible

## What this pack does not prove

This pack does not prove:
- regulatory approval
- legal AI Act compliance
- licensed banking deployment
- production deployment readiness
- validation on real customer production data

## Pack files

- `sigma/batches/bank_enterprise_pack.json`
- `sigma/tools/run_bank_enterprise_pack.py`
- `sigma/tests/test_bank_enterprise_pack.py`
- `run_bank_enterprise_pack.ps1`
- `docs/P2_BANK_ENTERPRISE_SCOPE.md`
