# BRODY X108 NATIVE RUNBOOK READONLY V1

STATUS=BRODY_X108_NATIVE_RUNBOOK_READONLY_V1_PASS

BUILD_TARGET=obsidia-x108-proofs
CANDIDATE_BUILD_TARGET=false
FIX_FORWARD_AFTER_COMMIT=e66a642
CURRENT_HEAD_BEFORE_REPAIR=e66a642

## Role

Official X108-side readonly runbook for Brody / LLM Obsidien.

## What it verifies

- Brody proof-side pointers exist.
- Runtime freeze pointer is present with its real status.
- Memory authority pointer is present with its real status.
- External access remains frozen.
- Local command gate repair lineage is clean.
- X108 remains final authority.
- verify_all.py stays PASS.

## Non-smoothed lineage

- 44edf4e: initial local command gate commit with smoke weakness.
- 2b504ca: incomplete repair.
- 8d89ae9: strict smoke repair still needed alignment.
- 458ae96: destructive smoke aligned.
- ee6113c: clean close of local command gate lineage.
- e66a642: runbook committed with wrong expected memory_authority status.
- current repair: aligns runbook to actual pointer statuses.

## Authority

- X108: final decision authority.
- Brody: readonly context / guide.
- Graphiti: readonly context or manual memory-only apply.
- Memory: no final decision authority.
- Human operator: required for command execution, promotion, apply, runtime binding, external access.

## Forbidden

- Brody executes commands.
- Brody authorizes commands.
- Brody emits ACT.
- Brody emits verdict.
- Brody writes Graphiti automatically.
- Brody performs memory intake automatically.
- Brody binds X108 runtime.
- Brody mutates kernel.
- Brody merges X108.

## Checked pointers

- x108_only_build_mode: BRODY_X108_ONLY_BUILD_MODE_READONLY_V1_PASS
- runtime_freeze: BRODY_RUNTIME_FREEZE_V1_4_12A_READONLY_READY
- native_terminal_session: BRODY_NATIVE_TERMINAL_SESSION_TEST_READONLY_READY
- detector_patch: BRODY_NATIVE_TERMINAL_DETECTOR_PATCH_READONLY_READY
- memory_authority: MEMORY_LAYER_AUTHORITY_MODEL_READONLY_READY


- 3145fdb: runbook repair still expected proof_state_freeze PASS while real pointer was READY.

- current repair V2: aligns proof_state_freeze expected status to BRODY_X108_PROOF_STATE_FREEZE_V1_READY.

