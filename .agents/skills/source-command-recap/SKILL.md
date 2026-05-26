---
name: "source-command-recap"
description: "Produce a session digest from SCRATCH.md and CURRENT_FOCUS.md for handoff or before /compact."
---

# source-command-recap

Use this skill when the user asks to run the migrated source command `recap`.

## Command Template

Read `.Codex/memory/SCRATCH.md` and `.Codex/context/CURRENT_FOCUS.md`, plus run:

```
git branch --show-current
git status --short
git log --oneline -10
git diff --stat
```

Produce a compact handoff digest:

```
Mode: READ_ONLY
Layer: AGENTIC
Files touched: none

Session recap
=============
Branch:        <name>
Working tree:  clean | <N changed files>
Recent commits (last 10):
  <oneline 1>
  <oneline 2>
  ...

What we did this session:
- <bullet>
- <bullet>

Files touched:
- <path>: <one line>

Current state of mind:
<one paragraph: what's done, what's pending, what's blocked>

Next mission (from CURRENT_FOCUS.md):
<one line>

Suggested next move:
<one concrete action>

Compact suggested? YES | NO
  (YES if context > 60 % full or session > 2 hours)
```

Rules:
- Read-only.
- Never quote > 15 words from any protected file.
- Suggest `/update-focus` if the recap reveals state drift between SCRATCH and CURRENT_FOCUS.
- Suggest `/compact` if the session is long.
