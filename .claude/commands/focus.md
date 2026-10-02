---
description: Show the current working state from .claude/context/CURRENT_FOCUS.md and .claude/memory/SCRATCH.md.
allowed-tools: Read, Bash(git status:*), Bash(git branch --show-current)
---

Read these two files and produce a concise status briefing:

1. `.claude/memory/SCRATCH.md`
2. `.claude/context/CURRENT_FOCUS.md`

Also run:

```
git branch --show-current
git status --short
```

Output format:

```
Mode: READ_ONLY
Layer: AGENTIC
Files touched: none

Live Git branch:        <current branch from git>
Live working tree:      clean | dirty (<N changed files>)

From SCRATCH.md (live state):
  Currently building: <one line>
  Files touched this session: <list or "none">
  Next: <one line>

From CURRENT_FOCUS.md (working focus, not Git authority):
  Phase: <one line>
  WIP / decisions: <one line>
  Next mission: <one line>

Suggested next command:
<one concrete suggestion based on the above>
```

Rules:
- Read-only.
- Treat branch and working-tree output as live Git evidence only; do not copy it into memory as durable truth.
- If `SCRATCH.md` or `CURRENT_FOCUS.md` is missing, say so and suggest creating from template.
- Do not quote > 15 words verbatim from either file.
