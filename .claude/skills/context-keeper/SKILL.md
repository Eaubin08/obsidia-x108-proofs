---
name: context-keeper
description: Use this skill at the END of any session — or when the user says "save state", "update focus", "what changed today", "before /compact", or asks for a recap. It maintains .claude/memory/SCRATCH.md and .claude/context/CURRENT_FOCUS.md so that the next session starts informed, without re-reading the repo.
obsidia_mapping_type: behavior
obsidia_agents: []
obsidia_reduction: local Claude Code behavior for SCRATCH/CURRENT_FOCUS maintenance
---

# Context Keeper

## Purpose

Keep the project's working state compact and current. After every meaningful step, update:

- `.claude/memory/SCRATCH.md` — per-session scratch (what's being built right now)
- `.claude/context/CURRENT_FOCUS.md` — per-week working state (active branch, known issues, next mission)

## When to use

- End of session (before `/compact` or before user closes Claude Code)
- After any modification was applied
- When the user says "save state", "checkpoint", "update focus", "recap"
- When `SCRATCH.md` becomes stale (older than the current task)

## When NOT to use

- During active inspection (let `read-only-inspector` finish first)
- During patch application (let `sigma-surgeon` finish first)
- For pure conversation that doesn't change the repo state

## Operating rules

1. Always show the **proposed delta** before writing — wait for user approval.
2. Keep `SCRATCH.md` ≤ 300 tokens. If it grows, archive oldest entries to `.claude/memory/snapshots/`.
3. Keep `CURRENT_FOCUS.md` ≤ 80 lines. Same archiving rule.
4. Never quote protected file content in either file. Reference paths only.
5. Never commit these files automatically.

## Required output format

```
Mode: PROPOSE
Layer: AGENTIC (memory)
Files touched: <none until approved>

Proposed delta to .claude/memory/SCRATCH.md:
---
## Currently building
<one paragraph max>

## Files touched this session
- <path>: <one-line change>

## Decisions
- <one line>

## Open questions
- <one line>

## Next
<one concrete next step>
---

Proposed delta to .claude/context/CURRENT_FOCUS.md:
---
## YYYY-MM-DD <short tag>
- branch: <name>
- did: <one line>
- next: <one line>
- blocked on: <one line or "nothing">
---

Approval required: YES — wait for user "Approved."
```

## Forbidden actions

- Writing to `SCRATCH.md` or `CURRENT_FOCUS.md` without showing the diff first.
- Committing memory files automatically.
- Including > 15 words quoted from any protected file.
- Inflating `SCRATCH.md` beyond 300 tokens.

## Verification checklist

- [ ] Diff was shown to the user.
- [ ] User explicitly approved.
- [ ] File length is within budget (300 tokens for SCRATCH, 80 lines for FOCUS).
- [ ] No protected content quoted.
- [ ] Snapshots archived if file overflowed.
