---
description: Update CURRENT_FOCUS.md and SCRATCH.md after a session step. Always shows the diff first and waits for approval.
allowed-tools: Read, Edit, Write, Glob, Grep, Task, Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git branch --show-current)
---

Delegate to the `context-keeper` subagent (isolated context).

It will:
1. Gather session evidence: `git status --short`, `git diff --stat`, `git log -5 --oneline`, last few user / assistant exchanges.
2. Propose a delta to `.claude/memory/SCRATCH.md`.
3. Propose a delta to `.claude/context/CURRENT_FOCUS.md`.
4. Return both deltas in the format defined in `.claude/agents/context-keeper.md`.

After the subagent returns:

- Show both proposed deltas to the user.
- Wait for the user's explicit "Approved." before any `Edit` / `Write`.
- On approval, apply the deltas (one `Edit` per file).
- After write, run `git status --short` and confirm only memory / context files changed.

Rules:
- Never write either file without showing the diff first.
- Never quote protected file content.
- Never auto-commit.
- If either file would exceed its budget (300 tokens for SCRATCH, 80 lines for FOCUS), propose archiving the oldest section to `.claude/memory/snapshots/`.

Optional argument: $ARGUMENTS (a short tag for the FOCUS delta entry, e.g. `v18-3-1-diagnosis-step-1`).
