---
description: Read-only targeted inspection of a path or topic. Never modifies anything.
allowed-tools: Read, Glob, Grep, Task, Bash(git status:*), Bash(git log:*), Bash(git show:*), Bash(git diff:*)
---

Activate the `read-only-inspector` skill.

Inspect: $ARGUMENTS

Rules:
- Read-only. No `Write`, no `Edit`, no destructive `Bash`.
- Targeted reads only. Never load the whole repo.
- If more than 5 files would be needed, delegate to the `explorer` subagent.
- If the topic touches `proofs/`, `formal/tla/`, Merkle, seal, RFC3161, or sealed files, also activate `proof-sentinel` (still read-only).

Output the structured report defined in `.claude/skills/read-only-inspector/SKILL.md` (Mode / Layer / Scope / Files touched: none / Findings / Risks / Next safest step / Suggested commands).
