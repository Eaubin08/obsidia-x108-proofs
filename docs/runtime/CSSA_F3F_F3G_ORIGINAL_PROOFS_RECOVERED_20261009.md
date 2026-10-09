# CSSA × Universal — F3F/F3G original source recovery (confirmed)

Date 2026-10-09. READONLY audit of *different repository* `Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-`; write here only, branch `feat/cssa-v01-active`. Historical GitHub proof artifacts **found**, without replaying their tests.

## Original source repo

https://github.com/Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-

The earlier search for F3F/F3G branches in `obsidia-x108-proofs` failed because **the phases reside in a separate CSSA repository**. Original branches found:
- `feat/f3f-cssa-organizational-stress-v0`
- `feat/f3g-f-cssa-announced-role-coverage-v0`
- `feat/f3g-g-cssa-contract-compliance-lifecycle-v0`
- `feat/f3g-h-cssa-institutional-relations-v0`
- `feat/f3g-i-cssa-root-cause-recurrence-v0`
- `feat/f3g-j-cssa-matchday-buvette-restauration-v0`.

## Exact original proof evidence

| Phase | Original receipt file | Blob SHA verified by fetch | Historical proof |
|---|---|---|---|
| F3F | `evidence/audits/F3F_CSSA_ORGANIZATIONAL_STRESS_RECEIPT.md` | `0695bcfe45ddda3169684e18173180fe8e74a7d0` | run `37559251006`, 217 PASS; 904 synthetic events, 12 collision scenarios, 2 ALLOW / 5 HOLD / 5 BLOCK; priority **SAFETY > REGULATORY > DEADLINE** |
| F3G-F | `evidence/audits/F3G_F_CSSA_ANNOUNCED_ROLE_COVERAGE_RECEIPT.md` | `b8d2f20a9211359bd2dd8f63061acc54326e9626` | run `37568479749`, 291 PASS; 11 requirements, initial 5 covered / 4 partial / 2 gaps |
| F3G-G | `evidence/audits/F3G_G_CSSA_CONTRACT_COMPLIANCE_LIFECYCLE_RECEIPT.md` | `b52b2a38deeb0a3c1023940f02ccc74b3d398f2c` | run `37569361100`, 308 PASS; contract and generic compliance lifecycle |
| F3G-H | `evidence/audits/F3G_H_CSSA_INSTITUTIONAL_RELATIONS_RECEIPT.md` | `87f4ca8f2dfa7906dd483b6bd324aadbae665d6c` | final frozen run `37570923893`, 325 PASS; institutional relations, ACKNOWLEDGED != APPROVED |
| F3G-I | `evidence/audits/F3G_I_CSSA_ROOT_CAUSE_RECURRENCE_RECEIPT.md` | `cb283249e228096d637ea70289f019f22a6afe00` | run `37589585121`, 343 PASS; RCA and recurrence |
| F3G-J | `evidence/audits/F3G_J_CSSA_MATCHDAY_BUVETTE_RESTAURATION_RECEIPT.md` | `68a12c171e5605c9c323878507e7e5b925a0fdb4` | run `37591139747`, 368 PASS; 16 mock cases, 6 ALLOW / 4 HOLD / 6 BLOCK |

**Important discrepancy:** previous historical chat reports F3G-F final run `37568642321` (291 PASS), whereas original F3G-F *receipt* references `37568479749` (291 PASS). Do not collapse the two run IDs or select one as the definitive latest without inspection of GitHub Actions. The table above reflects the original receipt verbatim.

## Concrete code and fixture paths in the historical repository

F3F:
- `organizations/cssa/season_simulation/full_season_v0.py`
- `organizations/cssa/stress/organizational_stress_v0.py`
- `organizations/cssa/stress/resources_v0.json`
- `organizations/cssa/stress/stress_scenarios_v0.json`
- `tests/test_f3f_cssa_organizational_stress_v0.py`
- `reports/F3F_CSSA_ORGANIZATIONAL_STRESS_BILAN.md`.

F3G:
- `organizations/cssa/coverage/announced_manager_role_coverage_v0.json` (blob SHA `440f00cb98e48c6340eebb045d93f4b5a1fd3627`), the **actual authoritative list of 11 requirement identifiers**. Its field boundaries explicitly say `PUBLIC_ROLE_DESCRIPTION_NOT_INTERNAL_FIELD_EVIDENCE`.
- `organizations/cssa/coverage/announced_role_coverage_v0.py`
- `organizations/cssa/compliance/contract_compliance_v0.py`, `.../contract_compliance_cases_v0.json`
- `organizations/cssa/institutions/institutional_relations_v0.py`, `.../institutional_cases_v0.json`
- `organizations/cssa/root_cause/root_cause_recurrence_v0.py`, `.../root_cause_cases_v0.json`
- `organizations/cssa/matchday_food/buvette_restauration_v0.py`, `.../buvette_restauration_cases_v0.json`
- dedicated `tests/test_f3g_{f,g,h,i,j}_*.py` and GitHub workflows per phase.

## Corrected matrix and next material task

1. **Do not reimplement F3F season stress**, contracts/compliance, institutions, root cause, buvette. Files and receipts **exist** in the historical repo.
2. Obtain exact historical HEAD commits, full 11-item JSON mapping, code inputs/outputs, test fixture expectations and worktree-compatible references for F3F-F3G.
3. Compare historical CSSA types and semantics with current `obsidia-x108-proofs` CSSA Lot A and Universal `ActionCandidate`, native CASE/TASK/FOLLOW-UP and governed execution. Categorize each as `SAME / ADAPTER_REQUIRED / HOLD / EXPLICIT_UNVERIFIED`.
4. Prefer CSSA-only adapter and integration tests. No wholesale merge of CSSA repo, no edits in old repo, no kernel/shared-runtime changes or `main` push.
5. Re-run exact historical suites on their **own** isolated checkout before asserting CURRENT PASS; historical successful receipts are not today's verification.
6. Gate any live CSSA pilot on real authority, consent, privacy, provenance and independent controls; sources remain public/synthetic until otherwise validated.

## Current separately verified targeted baseline

The user ran `152 passed, 1 skipped, 0 failed` in 3.83 s on CSSA branch in `obsidia-x108-proofs`, covering new 12-event Lot A, 2 E2E sovereign sandbox paths. This does **not** replace the historical 904-event F3F stress evidence or prove all 11 roles operationally.

**Verdict: `F3F_F3G_ORIGINAL_REPOSITORY_AND_RECEIPTS_RECOVERED — CROSS_REPO_CONTRACT_MAPPING_NEXT`.**
