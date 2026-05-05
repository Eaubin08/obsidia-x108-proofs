# Workflow

> The default workflow for any task touching the repo.

## 10-step default workflow

```
1.  CLASSIFY            → one layer, one mode (agent-router-obsidia)
2.  INSPECT             → read-only, targeted (read-only-inspector)
3.  DIAGNOSE            → state the problem with file:line evidence
4.  PROPOSE             → minimal plan: files, reason, risk, verification, rollback
5.  WAIT FOR APPROVAL   → explicit "Approved." from user (in this session)
6.  PATCH               → minimal change, no opportunistic edits
7.  VERIFY              → run the verification command, capture output
8.  REPORT              → what changed, what didn't, what to watch
9.  SHOW GIT STATUS     → git status --short, git diff --stat, git diff --check
10. UPDATE CURRENT_FOCUS.md   → if task state changed
```

If any step would require editing a protected file (see `PROTECTED_SCOPE.md`), insert a `freeze-guardian` check between steps 4 and 5.

## Mandatory response header

For any task touching the repo, the FIRST lines of the response are:

```
Mode:  READ_ONLY | PROPOSE | APPLY
Layer: KERNEL | SIGMA | CONNECTORS | DOCS | TOOLING | AGENTIC
Scope: <one line>
Risk:  NONE | LOW | MEDIUM | HIGH
Files touched: <list, or "none">
```

If `Files touched != none`:
- `Mode = APPLY` requires user approval already given OR the user explicitly asked to apply.
- The verification command and rollback path must appear before any `Edit` / `Write`.

## Modification template

When proposing any modification:

```
Patch plan
----------
Layer:                <KERNEL | SIGMA | ...>
Files:                <list>
Reason:               <one paragraph>
Risk:                 <NONE | LOW | MEDIUM | HIGH> — <why>
Verification command: <exact command>
Expected output:      <what success looks like>
Rollback path:        <git restore <file> OR git revert <commit>>
Approval needed?      YES | NO (if NO, explain why)
```

## Git discipline

### Before any edit
- `git status`
- Identify branch and uncommitted changes
- If uncommitted changes exist, ASK the user before adding more

### After any edit
- `git status --short`
- `git diff --stat`
- `git diff --check`
- List verification commands and their results

### Never auto
- Auto-commit
- Auto-push
- Auto-rebase
- `git push --force` of any kind
- `git reset --hard` of any kind

## When something goes wrong

1. Stop. Do not attempt a "fix the fix".
2. Report the failure with full output.
3. Propose a rollback (`git restore`, `git checkout HEAD --`, etc.).
4. Wait for the user's decision.

## Proof discipline (evidence levels)

Never call something "proven" without specifying the evidence level:

| Level | Name | Meaning |
|---|---|---|
| 0 | VISION | Conceptual idea |
| 1 | BROUILLON | Draft / sketch |
| 2 | TEST_LOCAL | Passes locally |
| 3 | CI_VERT | Passes CI |
| 4 | AUDIT_HUMAIN | Reviewed by a human auditor |
| 5 | PROOF_FORMEL | Formal proof (Lean, TLA+/TLC, signed Merkle) |
| 6 | TERRAIN | Validated in real domain operation |

Lean / TLA / Merkle / seal / RFC3161 artifacts are **always** at level 5 or 6.
A formatting change can invalidate them.
