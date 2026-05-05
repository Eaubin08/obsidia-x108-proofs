---
description: Check whether a path is in the protected scope. Returns YES / NO / ONLY_WITH_APPROVAL with the matching rule.
allowed-tools: Read, Glob
---

Activate the `freeze-guardian` skill.

Path to check: $ARGUMENTS

Output (per `.claude/skills/freeze-guardian/SKILL.md`):

```
Path checked:              <verbatim path from $ARGUMENTS>
Protected scope:           <which glob(s) matched, or "none">
Canonical / freeze status: <FROZEN | SEALED | ANCHORED | VENDORED | INTENTIONAL_FIXTURE | NONE>
Modification allowed?      YES | NO | ONLY_WITH_APPROVAL
Risk:                      NONE | LOW | MEDIUM | HIGH
Required approval:         <none | "user must reply 'Approved.'">
Safe alternative:          <where to put a draft / patch instead>
Verification:              <command sequence to confirm the change is correctly applied>
```

If `$ARGUMENTS` is empty, ask the user for the exact path before proceeding.

Rules:
- Read-only.
- Never return `YES` for a protected glob match.
- Always cite the matching glob.
- Always provide a safe alternative.
