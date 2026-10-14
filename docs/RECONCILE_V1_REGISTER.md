# RECONCILE V1 REGISTER — obsidia-x108-proofs

Branch: `reconcile/obsidia-x108-proofs-v1`
Dates: 2026-10-13 (phase 0, stack A), 2026-10-14 (phases 2 and 3)
Status: **IN PROGRESS — stack A, phase 2 (repair, ontology), stack B trunk (3a) and GPS capture line (3b) integrated.** No closure tag yet (owner instruction).

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

## 3. Integrated

All merges are two-parent merge commits (Git Data API); original commits keep their SHA. Before each merge the files changed on both sides since the merge base were computed: 0 every time. The resulting tree was checked against the expected three-way result before the commit was created.

### 3.1 Stack A — World Action → Enterprise → V0.1 → CSSA → Universal

| Lot | Source | Source SHA | Commits | Merge commit | Pushed with |
|---|---|---|---|---|---|
| 1a | `feat/world-action-multidomain-conformance-v0` | `b99bab752a5109d1f48a8e2a8f39265ac1fb0765` | 54 | `f29e1d3ed95c713e944a75890725dcf6a6aa7826` | itself |
| 1b | `feat/v01-c42-offline-interrepo-conformance-v0` | `314542254be27e252e866547826d21a05f7c3378` | 142 | `85de6c764520bd2f5058342d0e605527fb9f3b98` | itself |
| 1c | `feat/v01-c248-worker-ipc-correlation-v0` | `befa51cc87f0a216566bb14c07615f9cf30dfa7b` | 220 | `a62b7b7923dc49f5b6b3cf02a92862a38187c4cf` | 1d |
| 1d | `feat/cssa-v01-active` | `234ad83ca765502f7fa208677169805445f8bbce` | 100 | `eded1f8f5a479a2fef03dd7819ef3b2bac467b34` | itself |
| 1e | `feat/universal-cross-domain-conformance-v0` | `b69cfcbc7424c842f62895a918b849ff7882ca2c` | 10 | `0f56598b55ac162ed3db31294a9652db9711ccdf` | 1f |
| 1f | `audit/v01-c2-01-48-freeze-20261008` | `83e7736bdc125fb1b1ffdf7526eac46318e0cf18` | 1 | `714e711cb676e85b59f089794db386050d37eba4` | itself |

Lot 1c (known red at its own tip: malformed C2.28 test) was pushed together with lot 1d, which carries the fix `c80ec3ab4dfbe5087f66f4bcc6bf5807798a219a`.

### 3.2 Phase 2 — runtime truth repair and ontology contracts

| Lot | Source | Source SHA | Merge base | Commits | Merge commit | Pushed with |
|---|---|---|---|---|---|---|
| 2a | `repair/brody-native-memory-cleanup-20261008` | `4f1a02be835caf9f58f7940ec188ce154c05a939` | `48f0c2fb` (`main`) | 8 | `b6d6e1c9fb14fd713496ff2e646778c8b15c2c16` | 2b |
| 2b | `docs/obsidia-ontology-layer-contracts-v0` | `f62c1a43f6972646403ad74e4a48062a1fb17cca` | `553df13d` | 1 | `e366d49934d40e4995fb9c6142b8df3715debf8f` | itself |

9 files: 5 modified (`apps/obsidia_api/routes/brody.py`, `periphery/agents/agent_obsidure.py`, `scripts/obsidia_cli.py`, `scripts/obsidia_registry.yaml`, `tests/gates/test_obsidia_runtime_service_map_v1.py`), 4 added (2 tests, 2 documents). No unexpected file.

### 3.3 Phase 3a — stack B trunk (Première mise au monde → governed world → GPS defense P4–P6 → R6 Brody bridge)

| Lot | Source | Source SHA | Merge base | Commits | Merge commit |
|---|---|---|---|---|---|
| 3a | `feat/gps-defense-brody-cognitive-bridge-v0` | `4db17fb584a2fc8792cc73f839afef0056f64e54` | `553df13d7bc8746ba582649d08a07a7f1478d081` (8 commits before `main`) | 179 | `b7049b5982504a371f96fecb65bf3bead83fedaf` |

120 files: 109 added, 11 modified, 0 deleted. The heads of 23 open PRs are ancestors of `4db17fb5` (#31–#51, #77, #87); those PRs are unchanged.

### 3.4 Ancestry

Verified through the compare API (behind = 0) for every source SHA and every previous merge commit, after each push.

Tree at `b7049b59`: 7 843 files (7 281 on `main`): 562 added, 26 modified, 0 deleted.

### 3.5 Phase 3b — GPS P2 capture line (integrated 2026-10-14, owner GO)

| Lot | Source | Source SHA | Merge base | Commits | Merge commit |
|---|---|---|---|---|---|
| 3b | `feat/gps-p2-rtltcp-live-path-v0` | `1a930c5c5ab002a0cd18786999c3f43e2c0bb11a` | `2a6766ee76780d9c311b866cc895848ff7cab3aa` | 86 | `a2cdb8bcd8a52e0a5b8913ed6cd72aff22088613` |

Parents: `8571a8fb2c1f338fa23a3dd3685ceac9b4f57f77` (this branch) and `1a930c5c` (source). Tree `8a6d6bd1c686898de6503aaa76a21721624abd3b`, 7 888 files.

49 files brought: 45 added, 4 modified, 0 deleted. The modified files (`OBSIDIA_PREMIERE_MISE_AU_MONDE_MASTER_V2.md`, `physical_signal_periphery.py`, `test_gps_physical_signal_periphery.py`, `test_gps_x108_reality_authenticity_gate.py`) were changed only by the source since the merge base.

Conflict resolution (owner decision): `domains/gps/gps_x108_gate.py` keeps the trunk blob `59118a48015b98436a09c5e2c7861c941107aae6` unchanged (§4: identical AST, presentation-only conflict). The capture-line history, including `b089b0ca`, enters through the second parent.

Authority review of the added code: the new GPS modules declare `decision_authority: KX108_ONLY`, `emits_verdict: False` and `allowed_to_decide/act: False` (with a constructor check). The live capture paths (`rtl_tcp`, Docker, GNSS-SDR, passive reception only) stay blocked until a capture is actually observed and bound to a receiver identity. The tests replace `subprocess`, `shutil.which` and the kernel HTTP post with stubs; hardware detection reads only `PATH` and environment variables.

Pre-publication checks, in an isolated temporary tree built from the same SHAs (tree identical to the merge tree, register excepted):
- 13 targeted 3b test files: 48 passed.
- All GPS tests (`tests/test_gps_*`, integration, periphery, R6, spoofing stress): 105 passed.
- Full suite on Windows: 2 failed, 13 545 passed, 1 collection error. All three are reproduced identically on the trunk `e5d36111`: `test_wb_060_all_sha256_valid` (§8.3), the Windows-only import error of `tests/integration/test_interpretation_to_intake_policy_native_v0.py`, and `tests/api/test_f22b_readonly_intent_guard.py::test_8000_8012_parity_runtime_state_intent` (§8.5).

## 4. Lot 3b — conflict analysis (resolved in §3.5)

`feat/gps-p2-rtltcp-live-path-v0` @ `1a930c5c5ab002a0cd18786999c3f43e2c0bb11a` — 86 commits beyond the merge base `2a6766ee76780d9c311b866cc895848ff7cab3aa`, 53 files (48 added, 5 modified).

**Initially not merged (state before the owner's GO): the merge is not clean.** `domains/gps/gps_x108_gate.py` was changed on both sides; a three-way merge of the file (`git merge-file` on the three blobs) gives **2 conflict hunks**. Nothing was written.

Diagnosis: both sides add the same P4 temporal-integrity delta (`temporal_integrity_ok`, reason `TEMPORAL_INTEGRITY_ANOMALY`, four `temporal_integrity_*` payload fields). The trunk version (commit `2e7565e3`, "port frozen P4 temporal integrity gate delta") wraps the expressions over several lines; the capture-line version keeps them on one line. Token for token the logic is the same; only line wrapping differs. Three other files changed on both sides are byte-identical on both sides.

Options for arbitration (none applied): keep the trunk version already on this branch, or keep the capture-line version. Either choice gives the same behavior; a manual two-parent merge would then be needed, as done for OBSIDIA_TRADING.

**Owner decision 2026-10-14: HOLD on any merge of 3b.** Detailed comparison (read-only):

| Version | Commit | Blob of `gps_x108_gate.py` | Lines |
|---|---|---|---|
| Common ancestor | `2a6766ee76780d9c311b866cc895848ff7cab3aa` | `2318e241b023e9e365b4eb13a4558d621397c9da` | 405 |
| Trunk (this branch, from `2e7565e367d297864cbd8ab6376d63642342c6df`) | `e5d361119767e31dd58081fb232d0993cdf28199` | `59118a48015b98436a09c5e2c7861c941107aae6` | 425 |
| Lot 3b (from `b089b0ca8188250f7498a35aae0a510cc60cbb08`) | `1a930c5c5ab002a0cd18786999c3f43e2c0bb11a` | `96e86e70b2eed16a5394252a684694a6d94b1910` | 415 |

- Conflict hunks: `evaluate_reality_authenticity` (computation of `temporal_classification` / `temporal_integrity_ok`) and `build_kernel_state_payload` (four `temporal_integrity_*` fields). The two non-conflicting hunks (dataclass field, reason `TEMPORAL_INTEGRITY_ANOMALY`, constructor argument) are identical on both sides.
- **The Python ASTs of the two versions are identical** (`ast.dump` equality): no semantic difference. Imports, functions, return values, `fail_closed`, HOLD paths, `KX108_ONLY` and the kernel call are the same.
- The 3b source commit changes only this file; so does the trunk commit.
- Lot 3b also brings 11 new GPS P2/P4/P5 test files and modifies `tests/test_gps_x108_reality_authenticity_gate.py` and `tests/test_gps_physical_signal_periphery.py`; these are the targeted tests for any later resolution.

## 5. Reconciliation-only commits

| SHA | Purpose |
|---|---|
| `3d7c16f4b9de0c0234309552ab66f1c3a33c559e` | `reconcile/**` push trigger on `verify.yml` and `verify-proofs.yml` |
| `6bb62e1d38bd96ef4f70035da3e5d1255a723c3d` | new `.github/workflows/reconcile-v1-full-suite.yml`: the `main` version of the periphery job, on `reconcile/**` only (see §8.1) |
| `5823c4c3460001a416a0c915d42aa47779102fe5` | first version of this register (`[skip ci]`) |
| (this commit) | register update after phases 2 and 3 (`[skip ci]`) |

## 6. Contracts

Protected scope of `PROTECTED_SCOPE.md` (`proofs/V18_*`, `proofs/lean/**`, `proofs/tla/**`, `formal/tla/**`, Merkle roots and seals, RFC3161 anchor, `server.kernel.sealed.cjs`, frozen and vendored files): **0 file changed** between `main` and `b7049b59`. `sigma/**`: 0 file changed. No existing file whose name contains root/seal/hash/anchor/freeze was modified. No seal regenerated. One file added under `proofs/`: `proofs/governed_world_decision_proof_v0.py` (stack B, new file).

### 6.1 Authority-adjacent files changed by stack A (all additive)

| File | Change | Source commits |
|---|---|---|
| `scripts/obsidia_kx108_decision_store.py` | new decision phase `WORLD_ACTION_PRE_EXECUTION` and its persistence function; accepts only a kernel dataclass envelope, caller cannot supply `x108_gate`; "does NOT authorize egress by itself" | `8240e0a1`, `3c90122d` |
| `scripts/kernel/kx108_runtime_link_facts_v1.py` | new presence facts (world action rail, native tasks/CRM, native sources); presence is stated as not being activation | `32eba23b` … `161577a7` |
| `scripts/obsidia_governed_runtime_cycle_v1.py` | domain extension seam: an extension may only build a `DomainAggregate`; the decision is still rendered by `GuardX108().decide()` | `a8cc1592`, `9ba764f8`, `fc47df1f` |

**Correction to the plan:** the plan announced one sensitive file for stack A. There are three authority-adjacent files. They were read before integration; they add to the KX108 rail and do not replace or bypass it.

### 6.2 Authority-adjacent files changed by stack B trunk (all additive, all more restrictive)

| File | Change | Source commit |
|---|---|---|
| `runtime_wiring/x108_admission_stub.py` | an upstream X108 BLOCK is preserved as BLOCK, an upstream HOLD as HOLD; an upstream ALLOW "is observational only and never promotes authority"; invalid value raises; still never returns ACT | `cabc2ef9` |
| `periphery/context/cognitive_x108_admission.py` | passes the upstream constraint through; "does not grant authority to cognition" | `d991b476` |
| `domains/gps/gps_x108_gate.py` | new failure reason `TEMPORAL_INTEGRITY_ANOMALY` in the reality/authenticity check | `2e7565e3` |

### 6.3 Evidence at `b7049b59`

| Contract | Evidence |
|---|---|
| KX108_ONLY | `sigma/guard.py`, `sigma/contracts.py` and the whole `sigma/` tree byte-identical to `main`; repair states `decision_authority = KX108_ONLY`; decision-store, runtime-cycle and cognitive-admission tests pass |
| HOLD / BLOCK / ACT | sigma tests green in both `Verify proofs` workflows; admission stub keeps BLOCK > HOLD > ALLOW_CONTEXT_ONLY; CSSA remains HOLD/BLOCK simulation |
| Fail-closed, receipts, replay | 28 C2 workflows green (identity, revocation, reservation ledger, journal, SQLite guards, worker IPC, recovery, replay) on every state since lot 1d |
| Proofs | Lean build, TLA model check and strict Python verifiers green on every lot (`verify.yml`, `verify-proofs.yml`) |

## 7. CI by state

| State | SHA | `verify.yml` | `verify-proofs.yml` | Full test suite | C2 workflows |
|---|---|---|---|---|---|
| Reference | `3d7c16f4` | success | success | 11 failed, 12 443 passed | — |
| 1a | `f29e1d3e` | success | success | 11 failed, 12 517 passed | — |
| 1b | `85de6c76` | success | success | 11 failed, 12 790 passed | — |
| 1c+1d | `eded1f8f` / `6bb62e1d` | success | success | 8 failed, 13 222 passed, 77 skipped | 28 success |
| 1e+1f (end of stack A) | `714e711c` | success | success | attempt 1: 9 failed, 13 274 passed; attempt 2: 8 failed, 13 275 passed | 28 success |
| Phase 2 | `e366d499` | success | success | 9 failed, 13 282 passed, 77 skipped | 28 success |
| Phase 3a | `b7049b59` | success | success | 9 failed, 13 488 passed, 77 skipped | 28 success |
| Phase 3b | `a2cdb8bc` | success | success | 9 failed (same 9 as 3a), 13 525 passed, 77 skipped | 28 success |

Full test suite = `x108-periphery-ci.yml` up to lot 1b, `reconcile-v1-full-suite.yml` afterwards (see §8.1).

Failures at `b7049b59` (9), by origin:

| Test | Origin | Kind |
|---|---|---|
| `tests/api/test_brody_routes_registered.py::test_brody_routes_registered` | reference (`main`) | historical — Brody/memory/graphiti routes absent |
| `tests/cli/test_mission_authority_conformance_v0.py::test_lean_runtime_canonical_conformance` | reference (`main`) | configuration — `lake` not installed in this job (§8.1) |
| `tests/cli/test_mission_authority_conformance_v0.py::test_scope_le_conformance` | reference (`main`) | configuration — same |
| `tests/test_batch_execution_v0.py` ×5 (CLI batch execution, real pilot batch refusal) | reference (`main`) | historical |
| `tests/periphery/test_brody_integration_runtime_api_system.py::test_wb_060_all_sha256_valid` | **new in phase 2**, extended in phase 3a | inherited from the sources (§8.3) |

Three reference failures were fixed by stack A (`test_f67_no_new_sigma_or_bus_routes_beyond_expected`, `test_identity_cross_cwd_real_cli`, `test_clone_with_same_content_imported_as_new_commit_still_rejected`). No failure concerns decision authority, fail-closed behavior, receipts, replay or proofs.

Branch-filtered workflows of stack A (World Action, Enterprise, C0–C4.2, Universal: 48 files) do not trigger on `reconcile/**`; their tests are part of `tests/` and run in the full suite.

## 8. Open technical items

### 8.1 Inherited Lean step — formal conformance not executed in the test suite

From lot 1d on, the inherited `x108-periphery-ci.yml` fails at the step "Verify Lean toolchain" (`error: no default toolchain configured`) before any test runs. The step comes from source commit `765e3044` ("ci: provision declared Lean 4 toolchain for formal conformance tests") and fails the same way on the source branches since 2026-10-08. It was left unchanged. `reconcile-v1-full-suite.yml` replays the `main` version of the job so the suite keeps running.

Consequence: the two Lean conformance tests (`test_lean_runtime_canonical_conformance`, `test_scope_le_conformance`) **have never been executed** on this branch, nor on `main` (`lake` absent). The Lean proofs themselves are built (`lake build` in `proofs/lean`) and green in `verify.yml` and `verify-proofs.yml`. Status: **FORMAL_CONFORMANCE_TESTS_NOT_EXECUTED — OPEN_TECHNICAL_ITEM**.

### 8.2 Intermittent approval idempotency defect

`tests/test_batch_execution_v0.py::TestApprovalConcurrency::test_concurrent_identical_content_idempotent` failed once (attempt 1 at `714e711c`) and passed on attempt 2 of the same run, on the four earlier states and on the two later ones (`e366d499`, `b7049b59`): 1 failure in 8 executions of the full suite.

Observed: two threads store the same approval; one raises `FileNotFoundError` in `os.link(tmp, p)` inside `scripts/obsidia_batch_execution.py::store_approval_artifact` (line 422), so the test gets `['STORED']` instead of `['IDEMPOTENT_ALREADY_EXISTS', 'STORED']`. The script and the test are byte-identical to `main`; no integrated lot touches them. Recorded as a pre-existing race in approval storage. It concerns approval idempotency and should be fixed in its own mission. Status: **OPEN_TECHNICAL_ITEM — not caused by the reconciliation**.

### 8.3 Stale Brody inventory index

`periphery/agents/brody_integration_runtime_api_system.index.json` stores a SHA256 per indexed file. Two entries no longer match:

| File | Changed by | Index refreshed by the source? |
|---|---|---|
| `apps/obsidia_api/routes/brody.py` | repair branch (`1f2309a7`, legacy Graphiti activation removed) | no — the repair branch never ran in CI; its own report asks for a broader regression |
| `apps/obsidia_api/brody_semantic_query_router.py` | stack B (`0c58da39`), after the index refresh `5b9b7245` | no — the mismatch exists at the stack B tip `4db17fb5` itself |

The index declares `authority: NON_SOVEREIGN`, `can_decide: false`, `runtime_consumed: false`. It is an inventory, not a seal. The index was **not regenerated**. Status: **OPEN_TECHNICAL_ITEM — inherited from the sources**.

Owner qualification (2026-10-14): **DOCUMENTARY_INDEX_STALE — NON_BLOCKING_FOR_ORGANIZATIONAL_RECONCILIATION.** Checked: `brody.py` here is the repair branch blob; the index is consumed only by its own tests; it is absent from `merkle_seal.json` and `proofs/verify_all.py`; repair and ontology bypass neither `KX108_ONLY`, HOLD/BLOCK/ACT, fail-closed nor receipts/replay.

### 8.5 Live smoke test against local services (observed during the 3b pre-check)

`tests/api/test_f22b_readonly_intent_guard.py::test_8000_8012_parity_runtime_state_intent` sends `POST /api/brody/chat` to `127.0.0.1:8000` and `127.0.0.1:8012` and skips if they are unreachable (always the case in CI). During the local full-suite run it reached the Obsidia services running on the owner's PC; their response lacks the `graphiti_write` field, so the test failed. The route is read-only by contract (`readonly`, `emits_act: False`, `memory_write: False`). It fails the same way on the trunk; not caused by 3b. Recorded so that the owner knows these local services were contacted.

### 8.4 Verification limits

- Lean conformance tests never executed (§8.1); Lean proofs built only in `verify*.yml`.
- Consumers of the Brody index in unchanged `main` code were checked with GitHub code search, not an exhaustive read.
- No physical, live or hardware test was run; GPS capture paths are not exercised.
- The 3b conflict was checked by AST comparison, then by the 3b and GPS tests on the merged tree; GPS capture paths were run only against stubs, never with a receiver.

## 9. Kept separate

Excluded from V1, kept as they are (functional detail to be completed at closure): Jarvis advanced lineage (`feat/jarvis-advanced-obsidia-integration-v0` `dc548725`, `build/openjarvis-full-install` `57d9bdc1`, `work/jarjar-g7-contract-unification` `f8b4304a`), `codex/obsidure-f7-r10-isolated` (active work, tip `59138c89`), UDIP (`c15249aa`) and stack launcher (`13964f05`), GPS passive capture #53 (`b1bbb2d1`), GPS P4/P5 #89 (`cb5ff76f`), router/SENS independent history (`85d55e35`), `archive/2026-09/campaign-4353-v1`, `reorg/docs-v1`, dependabot #30. None is abandoned.

## 10. External references — not part of this mission

Created on purpose by another session dedicated to auditing and backing up the laptop. Not modified, not merged, not analysed here.

| Branch | SHA |
|---|---|
| `backup/portable-20261013/archive/legacy/feat/terminal-session-simulate-v0` | `9f7e4e7e9b47c96f7f84058bb11002acd6ad1778` |
| `backup/portable-20261013/archive/legacy/fix/brody-terminal-enriched-utf8` | `8fe4583c1c2c41ba3fe7b46375f87917e275d768` |
| `backup/portable-20261013/archive/legacy/source/f29-ledger-idempotent-20260901` | `ac09f22b4fbee89cd6fc496ab05e57e8b6f71904` |
| `backup/portable-20261013/archive/legacy/source/f29-ledger-idempotent-clean-20260901` | `b03eeb78ceaf122a91d8b5b5ee24e38bb7bc5f93` |
| `backup/portable-20261013/archive/legacy/source/p3-f20-20260831` | `0bf5f6c449095adadf922cbb5e01e0299f7297b2` |
| `backup/portable-20261013/archive/local-history-only-runtime-20260720_125701` | `cb4e33ebb011f8ff3b8fe9059dce9718b1d7eae9` |
| `backup/portable-20261013/backup/bad-v07-25d5d09` | `25d5d090318aa7ecb3e3d39e83e2316361b3432c` |
| `backup/portable-20261013/backup/freeze-a-before-docs-consolidation-20260719_070142` | `768e7bd760a5a3c03751a762b9c72f9dfc561cec` |
| `backup/portable-20261013/build/openjarvis-full-install` | `8aef3e13c0ac6f45a73cdbb19b44673ad178b416` |
| `backup/portable-20261013/feat/jarvis-advanced-obsidia-integration-v0` | `bc88b042d1090aca584c6dccba0ae17fd62ad33f` |
| `backup/portable-20261013/feat/jarvis-v0-readonly-relay-ingress` | `823829829ae3ba08bc369c8f5a983a9d450f7cc4` |
| `backup/portable-20261013/obsidia-clean-wt` | `7ff4365592e220a1c7254e3bde08d85e78997691` |
| `backup/portable-20261013/pilot/acd02-isolated-real-v0` | `53f44ae57b12bd47857df795d1b0f688e6dcd2b9` |
| `backup/portable-20261013/preserve/freeze-a-local-candidates-20260717` | `92fb803b58e8a9216d48d1cf68c37fb1196cf773` |
| `backup/portable-20261013/r12-e2e/build/openjarvis-full-install` | `4d8448b45b9866fe11ce0cbc01bd836c73f17a46` |
| `backup/portable-20261013/recovery/preserve-final-local-20260719_160038` | `8698a4e978ac2e49ce216a9d427e99d7bb3c8cea` |

Also appeared during phase 3, origin confirmed by the owner on 2026-10-14 (laptop session), out of scope, not modified, not merged: `backup/portable-20261014/codex/r12-f6-d3e-f9-evidence-convergence` @ `0dbf8d73898c2e1a7719bfa5e1e692939afef9a1`, `backup/portable-20261014/feat/jarvis-advanced-obsidia-integration-v0` @ `5a6a2acd5c2eb649a0d966d1689bc9be856f602b`.

`work/portable-openjarvis-r12` @ `740954d8a414cb937cb7078c3b3a77d2fa28d99d`: origin confirmed by the owner on 2026-10-14 (laptop session); out of scope, not modified, not merged.

## 11. Integrity of existing references (checked after lot 3a)

- `main` still at `48f0c2fbcfe097c213b2783bc7b4d0fba78e6621`.
- 175 tags and 149 PRs (64 open) identical to the pre-write snapshot: same state, head SHA, base and `updated_at`.
- The 143 branches of the initial inventory are unchanged. `codex/obsidure-f7-r10-isolated` moved from `094db54c` to `59138c89` on 2026-10-13 (owner's active work, not this mission).
- The only branch written by this mission is `reconcile/obsidia-x108-proofs-v1`.
