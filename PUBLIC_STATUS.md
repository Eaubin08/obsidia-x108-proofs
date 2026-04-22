# Public Status

## Global status

P1 CLOSED

## Canonical references

- Technical closure commit: `bd87e15`
- Public freeze commit: `99e966a`
- Official freeze tag: `p1-freeze-2026-04-22`

## Verification matrix

| Area | Status | Meaning in P1 |
|---|---|---|
| Lean 4 formal proofs | PASS | Public formal proof perimeter builds successfully |
| TLC model checking | PASS | Public model-checking runs complete without detected violation in the validated run set |
| `verify_all.py` | PASS | Public executable verification passes |
| `verify_decision.py` | PASS | Canonical public scenarios validate |
| Sigma public minimal layer | PASS | Public Sigma entry points, examples and smoke tests pass |
| RFC3161 anchor schema | PASS | Public anchor schema checks pass |
| Cross-platform QA | PASS | RFC3161 / TLC / Sigma QA passes in the validated environment |
| TSA endpoint probing | PASS | Public QA probe is robust and currently validates reachability in the validated environment |
| Public runner | PASS | `run_all_proofs.ps1` completes end-to-end |

## Interpretation rule

A PASS in this repository means:
- the public P1 verification perimeter is reproducible and closed

A PASS in this repository does not automatically mean:
- full production readiness
- full proprietary engine publication
- full business deployment completeness
- sovereign control over external TSA providers

## Out of scope

Out of scope for P1:
- production deployment readiness
- full proprietary engine publication
- final banking / trading / e-commerce production systems
- final operator cockpit / institutional surface
- permanent availability of external TSA providers

## Reading discipline

Use the following order:
1. `P1_FREEZE_NOTE.md`
2. `PUBLIC_STATUS.md`
3. `README.md`
4. `docs/PROOF_SCOPE.md`
5. `docs/SIGMA.md`
6. `docs/RFC3161.md`
7. actual scripts and tests