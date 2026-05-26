---
name: "source-command-focus"
description: "Show the current working state from .Codex/context/CURRENT_FOCUS.md and .Codex/memory/SCRATCH.md."
---

# source-command-focus

Use this skill when the user asks to run the migrated source command `focus`.

## Command Template

Read these two files and produce a concise status briefing:

1. `.Codex/memory/SCRATCH.md`
2. `.Codex/context/CURRENT_FOCUS.md`

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

Branch:        <current branch>
Working tree:  clean | dirty (<N changed files>)

From SCRATCH.md (live state):
  Currently building: <one line>
  Files touched this session: <list or "none">
  Next: <one line>

From CURRENT_FOCUS.md (week state):
  Phase: <one line>
  Known issues: <one line>
  Next mission: <one line>

Suggested next command:
<one concrete suggestion based on the above>
```

Rules:
- Read-only.
- If `SCRATCH.md` or `CURRENT_FOCUS.md` is missing, say so and suggest creating from template.
- Do not quote > 15 words verbatim from either file.
