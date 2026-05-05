---
description: Read-only diagnosis of a Sigma / QA / pipeline / connector issue. Never edits.
allowed-tools: Read, Glob, Grep, Task, Bash(git status:*), Bash(git log:*), Bash(git diff:*)
---

Target: $ARGUMENTS

Procedure:
1. Activate the `sigma-surgeon` skill (read-only mode for diagnosis).
2. Localize via `MODULE_MAP.md`. The Sigma layer is: `sigma/`, `sigma/tests/`, `qa/cross-platform/`, `connectors/`, `MonProjet/`.
3. Use `Glob` and `Grep` to find the failing test or module.
4. Delegate to the `sigma-checker` subagent (isolated context) to:
   - Run pytest on a single matching test file (PREPARED → wait for user approval before EXECUTED).
   - Parse the assertion failure.
   - Identify the smallest fix area.
   - Confirm the failure stays in the SIGMA layer.
5. If the failure references kernel symbols (`x108_core`, `Merkle`, `seal`, `RFC3161`), STOP and route to `/proofcheck` instead.

Output:
- The structured Sigma report defined in `.claude/skills/sigma-surgeon/SKILL.md`.
- Plus `Layer impact: SIGMA-only | crosses into KERNEL`.
- Plus `BLOCK > HOLD > ALLOW preserved? YES | NO | NEEDS_REVIEW`.

Rules:
- READ ONLY for diagnosis. Any patch requires explicit user "Approved." after the proposal.
- Never run the full Sigma test suite without explicit user approval.
- Never touch `RECUPE_SCORING/*_stable.py` or `sigma/contracts.broken-ragnarok.py`.
- Never normalize / reformat Sigma files outside the patch scope.
