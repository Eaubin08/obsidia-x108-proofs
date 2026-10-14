# RECONCILE OPENJARVIS PORTABLE REGISTER — obsidia-x108-proofs

Branch: `work/portable-openjarvis-r12`
Date: 2026-10-14
Status: **WORK BRANCH — LINEAGES REUNITED, NOT CERTIFIED.** No closure tag. No PR.

This branch reunites the three OpenJarvis lineages of `build/openjarvis-full-install` that had diverged between GitHub and the laptop. It is an organizational work branch. **It is not a runtime freeze, not a seal and not a certified state.** Nothing was merged into `main`. No source branch, tag or PR was modified. Nothing was deleted, rebased, squashed or force-pushed.

It is independent from `reconcile/obsidia-x108-proofs-v1`, which is driven by another mission and was not touched. That branch's register lists `57d9bdc1` and `codex/obsidure-f7-r10-isolated` as excluded from its V1.

## 1. Sources and merges

| Item | Value |
|---|---|
| Base (first parent) | `build/openjarvis-full-install` @ `57d9bdc159368c1464ddae7ae64de41f16876614` |
| Lineage A | `backup/portable-20261013/build/openjarvis-full-install` @ `8aef3e13c0ac6f45a73cdbb19b44673ad178b416` |
| Lineage B | `backup/portable-20261013/r12-e2e/build/openjarvis-full-install` @ `4d8448b45b9866fe11ce0cbc01bd836c73f17a46` |
| Common ancestor of the three | `6331f4c7d8e596a21cf3528eb12936e3b8528121` |
| Common ancestor of A and B | `5ce4c802e6bda9c3a349e8708f5b98818af524cf` |
| Merge 1 (base + A) | `9444dcf850d75ef0e0ff1cbee6fca5141465eb9e`, tree `86e755ad5330fc59fd0c02fe5a731b6ed37d65cd` |
| Merge 2 (merge 1 + B) | `0fd9c3246eca3bd93ef0144ca9a829ff001909d7`, tree `76528061801ed2fadfc74766a3ec16663c709a7d` |
| Method | two `git merge --no-ff`, two parents each, no squash, no rebase, built in a throwaway clone |
| Conflicts | none. Both trees are identical to the trees simulated beforehand with `git merge-tree`; merging B before A gives the same final tree |

## 2. Commits carried by each lineage

All original commits are preserved with their SHA. No two of them are duplicates (compared by patch-id).

**Base, 1 own commit**

| SHA | Subject |
|---|---|
| `57d9bdc159368c1464ddae7ae64de41f16876614` | feat(openjarvis): add governed browser API bridge |

**Shared trunk `6331f4c7..5ce4c802`, 7 commits** — brought in by merge 1; already on GitHub through `codex/obsidure-f7-r10-isolated`.

| SHA | Subject |
|---|---|
| `b0cd200c7` | feat(obsidure): expose supervised mission prepare ingress |
| `5b93cc526` | fix(obsidure): sanitize prepare ingress response boundary |
| `637345d9d` | test(r12): reproduce prepare-only mappingproxy serialization |
| `9800ed64f` | fix(r12): sanitize prepare-only response projection |
| `c1d194a1d` | feat(api): add supervised authorization handoff |
| `5a247d96c` | feat(api): expose supervised verification projection |
| `5ce4c802e6bda9c3a349e8708f5b98818af524cf` | R12-F6-D3-D: reconstruct KX108 pre-ACT decision in R8 replay; bind kx108 record id in F5 outcome |

**Lineage A, 2 own commits** — made on the laptop on 2026-10-12, published unchanged on 2026-10-13 as a backup branch.

| SHA | Subject |
|---|---|
| `a08ff1d89` | test(r12): reproduce local model evidence truncation |
| `8aef3e13c0ac6f45a73cdbb19b44673ad178b416` | fix(r12): complete bounded local model evidence response |

**Lineage B, 1 own commit** — made on the laptop on 2026-10-10 in a separate clone, published unchanged on 2026-10-13 as a backup branch.

| SHA | Subject |
|---|---|
| `4d8448b45b9866fe11ce0cbc01bd836c73f17a46` | ignore runtime_data |

## 3. Functional content

| Lineage | Content |
|---|---|
| Base | `scripts/obsidia_openjarvis_native_web_bridge_v0.py` (74 lines): serves the OpenJarvis FastAPI surface behind the Obsidia bridge |
| Trunk | supervised missions API: prepare ingress, authorization handoff, verification projection, KX108 pre-ACT decision reconstruction (8 files) |
| A | compact-evidence instruction added to the local Qwen evidence request (`scripts/providers/obsidia_qwen_local_evidence_v0.py`, 5 lines) and its truncation test |
| B | one line `runtime_data/` in `.gitignore`. No file is tracked under `runtime_data/` |

## 4. Authority boundaries

- `AUTHORITY = "NONE"` and `DECISION_AUTHORITY = "KX108_ONLY"` are defined in `scripts/obsidia_openjarvis_native_cli_bridge_v0.py`, which is byte-identical on the base, A, B and this branch. The web bridge imports these constants and does not redefine them.
- The trunk adds a hold `MISSION_AUTHORITY_NOT_KX108_ONLY` and keeps `supervisor_authority: NONE`. A changes an instruction text only. B does not touch code.
- Identical on the base, A and this branch: `sigma/guard.py`, `sigma/contracts.py`, `sigma/protocols.py`, `sigma/aggregation.py`, `proofs/lean/`, `formal/tla/`, `merkle_seal.json`, `scripts/kernel/`, `server.kernel.sealed.cjs`, `_FREEZE/`, `freeze/`, `.runtime_freezes/`.

## 5. Dependencies

- `openjarvis` Python package: required by the web bridge and by `tests/cli/test_openjarvis_native_cli_bridge_v0.py` and `tests/cli/test_cognitive_ingress_final_surface_v0.py`. It is not installed by the CI job.
- `app.knowledge.b8.serialization`: imported by `tests/b8/test_b8_r12_prepare_only_serialization_red.py` (trunk commit `637345d9d`); this module is not in this tree.
- `Jarvis-iron-obsidia-`: the governed browser executors called by the X-108 Jarjar browser bridge are on `reconcile/jarvis-iron-obsidia-v1-portable` of that repository.
- A local llama.cpp Qwen server is needed for any live check of lineage A; none was run.

## 6. Tests

### 6.1 Local run before publication

Windows 11, Python 3.13.3 (the CI job uses 3.12), on the merge tree `76528061`. No physical or live test.

| Check | Result |
|---|---|
| `tests/cli/test_r12_qwen_evidence_truncation.py`, `tests/api/test_supervised_mission_authorization_handoff_api.py`, `tests/api/test_supervised_mission_prepare_ingress_api.py`, `tests/api/test_supervised_mission_verification_operator_api.py`, `tests/api/test_supervised_missions_readonly_api.py`, `tests/test_r12_f6_d3_binder_reconstruction.py` | 29 passed |
| `tests/b8/test_b8_r12_prepare_only_serialization_red.py` | collection error, `No module named 'app.knowledge'` |
| `python scripts/check_forbidden_content.py` | `FORBIDDEN_CONTENT_PASS` |

The full suite was not run locally.

### 6.2 GitHub CI before this branch

Only "X108 Periphery CI" runs on pushes outside `main`. On the four heads below it fails at the step "Run all tests" during collection, so no test executes.

| Head | Run | Collection errors |
|---|---|---|
| `build/openjarvis-full-install` @ `57d9bdc1` | `37916396865` | 3 |
| backup A @ `8aef3e13` | `38437037735` | 4 |
| backup B @ `4d8448b4` | `38437078591` | 4 |
| `codex/obsidure-f7-r10-isolated` @ `59138c89` | `38398563880` | 4 |

The four collection errors:

| Test module | Error |
|---|---|
| `tests/api/test_f17c_brody_source_label.py` | `ImportError: cannot import name '_source_label_from_graphiti_probe' from 'apps.obsidia_api.brody_real_response_pipeline'` |
| `tests/cli/test_cognitive_ingress_final_surface_v0.py` | `ModuleNotFoundError: No module named 'openjarvis'` |
| `tests/cli/test_openjarvis_native_cli_bridge_v0.py` | `ModuleNotFoundError: No module named 'openjarvis'` |
| `tests/b8/test_b8_r12_prepare_only_serialization_red.py` | `ModuleNotFoundError: No module named 'app.knowledge'` (absent from the base, present from the trunk onwards) |

None was fixed here.

### 6.3 GitHub CI on this branch

Run `38500998521` of "X108 Periphery CI" on `d37ed822b573ff91fc4dc2a9408a9518580d0616` (push). Conclusion: failure.

| Job | Result |
|---|---|
| `verify` | FAILURE at step "Run all tests" — `Interrupted: 4 errors during collection`, `208 deselected, 1 warning, 4 errors` |

The four collection errors are exactly those of section 6.2, the same as on backup A, backup B and `codex/obsidure-f7-r10-isolated`. No test executed. The later steps (protected files check, forbidden content check, manifest verification) did not run. The merges add no new CI error and remove none. Nothing was fixed.

This commit of the register changes a Markdown file only; the workflow ignores such pushes, so no further run is expected for it.

## 7. Limits of validation

| Item | Status |
|---|---|
| GitHub CI | executes no test on this lineage (collection interrupted) |
| Web bridge `obsidia_openjarvis_native_web_bridge_v0.py` | no test in the tree; not run |
| Lineage A fix against a real local model | described as proven live on 2026-10-12 in its test docstring; not replayed here. **PENDING** |
| Physical and live validations | **PENDING** |
| History below `6331f4c7` | 541 commits of the Obsidure lineage are in neither `main` nor `reconcile/obsidia-x108-proofs-v1`; this branch inherits them as they are and claims nothing about them |

## 8. Work kept separate

| Item | Where | Status |
|---|---|---|
| `codex/obsidure-f7-r10-isolated` @ `59138c89762266e2b64ddc40d869f761b20e097e` (F7/R10, 11 commits above `5ce4c802`) | GitHub | active work, NOT merged here. Simulated merge with this branch: no conflict |
| `codex/r12-f6-d3e-f9-evidence-convergence` @ `0dbf8d73898c2e1a7719bfa5e1e692939afef9a1` (D3E, 1 commit above A) | laptop | active work, NOT merged here. Simulated merge with this branch: no conflict |
| F7/R10 and D3E together | — | NOT merged with each other. A simulated merge conflicts on `periphery/agents/agent_obsidure.py` |
| Uncommitted work in the laptop worktrees | laptop | not published; includes a different, uncommitted variant of the lineage A provider change |
| `build/openjarvis-full-install` and the two backup branches | GitHub | unchanged |

## 9. Guarantees

- `main` is still at `48f0c2fbcfe097c213b2783bc7b4d0fba78e6621`.
- `build/openjarvis-full-install`, the two `backup/portable-20261013/*` source branches and `codex/obsidure-f7-r10-isolated` are at the SHA listed above.
- `reconcile/obsidia-x108-proofs-v1` was read only, never written.
- No tag was created or moved. No PR was opened, closed or merged.
- Every commit reachable from this branch was already on GitHub, except the two merge commits and the register commits.
