---
description: Before any broad read or "load everything" operation, justify it and propose a cheaper targeted plan.
allowed-tools: Read, Glob, Grep
---

Activate the `token-guard` skill.

Proposed broad operation: $ARGUMENTS

If `$ARGUMENTS` is empty, infer from the most recent user request: what would the broadest possible read look like?

Output (per `.claude/skills/token-guard/SKILL.md`):

```
Detected intent:    <one sentence>

Broad read estimate:
  files:  ~<N>
  tokens: ~<estimate, in thousands>
  cost:   <HIGH | VERY_HIGH>

Targeted alternative:
  step 1: <Glob / Grep with exact pattern>
  step 2: <Read N lines from M files>
  step 3: <delegate to explorer subagent if > 5 files>
  files:  ~<N>
  tokens: ~<estimate, in thousands>
  cost:   <LOW | MEDIUM>

Why the alternative works:
<one paragraph>

Decision:
[ ] Proceed with broad read (user must say "broad read approved")
[X] Proceed with targeted alternative (default)

Next action: <concrete>
```

Rules:
- Always show both costs.
- Default decision is targeted.
- If user picks broad, log the choice in `SCRATCH.md` so it's not repeated next session.
- Never silently perform a broad read.
