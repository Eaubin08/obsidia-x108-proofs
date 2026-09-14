# Canonical C2 Conformance Pilot — `CANONICAL_C2_CONFORMANCE_PILOT_V0`

**This is a conformance fixture, not a business remediation.**

Its sole purpose is to exercise the committed governed remediation rail
(`A1 -> C1 -> C2 -> D1 -> D2`, HEAD `7f40160`) end-to-end against an actual
tracked file in the canonical repository, before the rail is used on a real
Family Wiring remediation.

## Files

| File | Role |
|---|---|
| `pilot_target_v0.txt` | **Target A** -- initial canonical state (`state: UNREMEDIATED`). The file the governed C2 apply replaces. |
| `pilot_source_v0.txt` | **Source B** -- the exact intended post-state (`state: GOVERNED_C2_PILOT_APPLIED`). Referenced at Event 2 as a committed **GIT_BLOB** source of truth. |
| `.gitattributes` | Scoped byte-pin (`-text`) so checkout normalization can never alter the SHA256 / blob bytes. Affects only this directory. |
| `README.md` | This file. **No execution authority.** |

## Event 2 (governed pilot) -- separately human-authorized

Canonical path: `Ledger register_git_blob_source -> BatchProposal (propose_batch)
-> prepare_execution -> PreExecutionContext -> HumanApproval -> KX108_PRE ->
governed C2 apply -> TestContractResult -> sealed-bound KX108_POST -> KEEP | D2 rollback`.

- `source_kind = GIT_BLOB`, `operation_type = UPDATE_TARGET_FROM_SOURCE` (REPLACE, single child).
- Runs in a dedicated **clean isolated git worktree**; expected `git diff --name-only`
  scope = this target only.
- Recommended sequence: **negative run first** (forced HOLD -> D2 restores exact A),
  then **positive run** (ALLOW -> KEEP, target ends at B) -- unless later stack proof
  changes that recommendation.

## Retention

`PERMANENT_CONFORMANCE_FIXTURE`. After a successful positive pilot the target stays
at B as a proof baseline. Any re-exercise uses a fresh `vN` A/B pair or a
separately-governed reset -- never ad-hoc edits.
