# RECONCILE V1 REGISTER — obsidia-x108-proofs

Branch: `reconcile/obsidia-x108-proofs-v1`
Date: 2026-10-13
Status: **IN PROGRESS — stack A integrated, stack B not started.** No closure tag yet.

This branch is an organizational reconciliation. **It is not a runtime freeze, not a seal and not a certified state.** Nothing was merged into `main`. No source branch, tag or PR was modified. Nothing was deleted, rebased, squashed or force-pushed. No other repository and no local clone was touched. No physical or live test was run.

## 1. Governance check (phase 0)

| Text | Where | Scope found |
|---|---|---|
| HOLD of PR #149 (closed, draft) | `docs/audits/V01_C2_01_48_READONLY_FREEZE_20261008.md` @ `83e7736b` | "Keep C2.1–C2.48 PRs DRAFT and do not merge to main or trigger real CSSA Gmail/CRM/calendar sends." Repair gate 2 asks to "choose integration approach rather than merging 48 PRs blindly"; gate 3 asks for a consolidated one-SHA run |
| CSSA active branch policy | `docs/runtime/CSSA_ACTIVE_BRANCH_POLICY_V01.md` (stack A) | `main`: no change or merge without explicit request; CSSA stays in HOLD/BLOCK simulation; integration to main only on explicit instruction |
| `AGENTS.md` / `CLAUDE.md` / `PROTECTED_SCOPE.md` | `main` | default read-only, no push without the owner's request, protected files (proofs, formal, seals, anchors, sealed kernel) not to be edited |
| Branch protection / rulesets | GitHub settings | none |

No text forbids a reconciliation branch distinct from `main`. The HOLD targets promotion to `main` and real dispatch; both remain untouched.

## 2. Base and reference state

- Base: `main` @ `48f0c2fbcfe097c213b2783bc7b4d0fba78e6621`.
- Reference commit `3d7c16f4b9de0c0234309552ab66f1c3a33c559e`: adds the `reconcile/**` push trigger to `verify.yml` and `verify-proofs.yml` (jobs unchanged).
- Reference CI on `3d7c16f4`: `verify.yml` success, `verify-proofs.yml` success, X108 Periphery CI failure with **11 failed, 12 443 passed, 46 skipped** (same as `main`).

## 3. Integrated — stack A (World Action → Enterprise → V0.1 → CSSA → Universal)

All merges are two-parent merge commits (Git Data API); original commits keep their SHA. For each merge the files changed on both sides since the merge base were computed first: 0 every time.

| Lot | Source | Source SHA | Commits | Merge commit | Pushed with |
|---|---|---|---|---|---|
| 1a | `feat/world-action-multidomain-conformance-v0` | `b99bab752a5109d1f48a8e2a8f39265ac1fb0765` | 54 | `f29e1d3ed95c713e944a75890725dcf6a6aa7826` | itself |
| 1b | `feat/v01-c42-offline-interrepo-conformance-v0` | `314542254be27e252e866547826d21a05f7c3378` | 142 | `85de6c764520bd2f5058342d0e605527fb9f3b98` | itself |
| 1c | `feat/v01-c248-worker-ipc-correlation-v0` | `befa51cc87f0a216566bb14c07615f9cf30dfa7b` | 220 | `a62b7b7923dc49f5b6b3cf02a92862a38187c4cf` | 1d |
| 1d | `feat/cssa-v01-active` | `234ad83ca765502f7fa208677169805445f8bbce` | 100 | `eded1f8f5a479a2fef03dd7819ef3b2bac467b34` | itself |
| 1e | `feat/universal-cross-domain-conformance-v0` | `b69cfcbc7424c842f62895a918b849ff7882ca2c` | 10 | `0f56598b55ac162ed3db31294a9652db9711ccdf` | 1f |
| 1f | `audit/v01-c2-01-48-freeze-20261008` | `83e7736bdc125fb1b1ffdf7526eac46318e0cf18` | 1 | `714e711cb676e85b59f089794db386050d37eba4` | itself |

Lot 1c (known red at its own tip: malformed C2.28 test) was pushed together with lot 1d, which carries the fix `c80ec3ab4dfbe5087f66f4bcc6bf5807798a219a`.

Ancestry verified through the compare API (behind = 0) for every source SHA and every previous merge commit.

Tree at `714e711c`: 7 729 files (7 281 on `main`): 448 added, 10 modified, 0 deleted. It equals the tree of `b69cfcbc` plus exactly 4 files: the audit report and the three reconciliation workflow files.

## 4. Reconciliation-only commits

| SHA | Purpose |
|---|---|
| `3d7c16f4b9de0c0234309552ab66f1c3a33c559e` | `reconcile/**` push trigger on `verify.yml` and `verify-proofs.yml` |
| `6bb62e1d38bd96ef4f70035da3e5d1255a723c3d` | new `.github/workflows/reconcile-v1-full-suite.yml`: the `main` version of the periphery job, on `reconcile/**` only (see §6) |

## 5. Contracts

Protected scope (`proofs/**`, `formal/**`, `sigma/**`, `merkle_seal.json`, `merkle_root.json`, RFC3161 anchor, `server.kernel.sealed.cjs`, vendored files): **0 file changed** between `main` and `714e711c`. No seal regenerated.

Existing files of `main` changed by stack A (7), all additive:

| File | Change | Source commits |
|---|---|---|
| `scripts/obsidia_kx108_decision_store.py` | new decision phase `WORLD_ACTION_PRE_EXECUTION` and its persistence function; accepts only a kernel dataclass envelope, caller cannot supply `x108_gate`; "does NOT authorize egress by itself" | `8240e0a1`, `3c90122d` |
| `scripts/kernel/kx108_runtime_link_facts_v1.py` | new presence facts (world action rail, native tasks/CRM, native sources); presence is stated as not being activation | `32eba23b` … `161577a7` |
| `scripts/obsidia_governed_runtime_cycle_v1.py` | domain extension seam: an extension may only build a `DomainAggregate`; the decision is still rendered by `GuardX108().decide()` | `a8cc1592`, `9ba764f8`, `fc47df1f` |
| `.github/workflows/x108-periphery-ci.yml` | Lean provisioning step (see §6) | `765e3044` |
| `.gitattributes`, 3 test files | test and attribute adjustments | — |

**Correction to the plan:** the plan announced one sensitive file for stack A (`scripts/kernel/…`). There are three authority-adjacent files (the three scripts above). They were read before integration; they add to the KX108 rail and do not replace or bypass it.

| Contract | Evidence at `714e711c` |
|---|---|
| KX108_ONLY | `sigma/guard.py`, `sigma/contracts.py` byte-identical to `main`; decision-store and runtime-cycle tests pass in the full suite |
| HOLD / BLOCK / ACT | sigma tests (`verify.yml`) green; CSSA remains HOLD/BLOCK simulation by its own policy |
| Fail-closed, receipts, replay | 30 C2 workflows green (identity, revocation, reservation ledger, journal, SQLite guards, worker IPC, recovery, replay) |
| Proofs | Lean, TLA and strict Python verifiers green on every lot |

## 6. CI by lot

| State | SHA | `verify.yml` | `verify-proofs.yml` | Full test suite | Other workflows |
|---|---|---|---|---|---|
| Reference | `3d7c16f4` | success | success | 11 failed, 12 443 passed | — |
| 1a | `f29e1d3e` | success | success | 11 failed, 12 517 passed | — |
| 1b | `85de6c76` | success | success | 11 failed, 12 790 passed | — |
| 1c+1d | `eded1f8f` / `6bb62e1d` | success | success | 8 failed, 13 222 passed, 77 skipped | 28 C2 workflows: all success |
| 1e+1f | `714e711c` | success | success | attempt 1: 9 failed, 13 274 passed; attempt 2: 8 failed, 13 275 passed | 28 C2 workflows: all success |

**Inherited periphery workflow.** From lot 1d on, `x108-periphery-ci.yml` fails at the step "Verify Lean toolchain" (`error: no default toolchain configured`) before any test runs. The step comes from source commit `765e3044` and fails the same way on the source branches (`feat/cssa-v01-active`, `feat/universal-cross-domain-conformance-v0`) since 2026-10-08. It was left unchanged. To keep the full suite running, `reconcile-v1-full-suite.yml` replays the `main` version of the job; its results are the "Full test suite" column from 1c+1d on. OPEN_TECHNICAL_ITEM.

**Failures vs reference.** No new stable failure. Three reference failures are fixed by stack A (`test_f67_no_new_sigma_or_bus_routes_beyond_expected`, `test_identity_cross_cwd_real_cli`, `test_clone_with_same_content_imported_as_new_commit_still_rejected`). The 8 remaining ones are all in the reference set:

- `tests/api/test_brody_routes_registered.py::test_brody_routes_registered` (Brody/memory/graphiti routes absent)
- `tests/cli/test_mission_authority_conformance_v0.py` ×2 (`lake` not installed in this job)
- `tests/test_batch_execution_v0.py` ×5 (CLI batch execution and real pilot batch refusal)

**Unstable test.** `tests/test_batch_execution_v0.py::TestApprovalConcurrency::test_concurrent_identical_content_idempotent` failed on attempt 1 at `714e711c` (`FileNotFoundError` in `os.link` inside `scripts/obsidia_batch_execution.py::store_approval_artifact`, two threads racing) and passed on attempt 2 of the same run. `scripts/obsidia_batch_execution.py` and the test are byte-identical to `main`; lots 1e/1f add only documents, one periphery module, one script and three tests. Recorded as a pre-existing race in approval storage, not introduced by the reconciliation. OPEN_TECHNICAL_ITEM (it concerns approval idempotency and deserves a fix in its own mission).

Branch-filtered workflows of stack A (World Action, Enterprise, C0–C4.2, Universal: 48 files) do not trigger on `reconcile/**`; their tests are part of `tests/` and run in the full suite.

## 7. Not integrated yet

Stack B (`feat/gps-defense-brody-cognitive-bridge-v0` @ `4db17fb5`, then `feat/gps-p2-rtltcp-live-path-v0` @ `1a930c5c`), repair and ontology branches: planned, not started.

Excluded from V1, kept as they are (details to be completed at closure): Jarvis advanced lineage (`dc548725`, `57d9bdc1`, `f8b4304a`), `codex/obsidure-f7-r10-isolated` (active work, tip `59138c89` when last read), UDIP (`c15249aa`) and stack launcher (`13964f05`), GPS passive capture #53 (`b1bbb2d1`), GPS P4/P5 #89 (`cb5ff76f`), router/SENS independent history (`85d55e35`), `archive/2026-09/campaign-4353-v1`, `reorg/docs-v1`, dependabot #30. None is abandoned.

## 8. Integrity of existing references (checked after lot 1f)

- `main` still at `48f0c2fbcfe097c213b2783bc7b4d0fba78e6621`.
- 175 tags and 149 PRs identical to the pre-write snapshot.
- 143 pre-existing branches unchanged. `codex/obsidure-f7-r10-isolated` moved from `094db54c` to `59138c89` (owner's active work, not this mission).
- 13 branches `backup/portable-20261013/*` appeared during the work; they were not created by this mission.
