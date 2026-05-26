---
name: freeze-guardian
description: Use this skill any time a user request implies editing, renaming, deleting, reformatting, or regenerating a file. Triggers include "edit", "modify", "fix", "update", "rename", "regenerate", "reformat", "tidy up", "clean up", "lint" applied to any file. The skill checks whether the target path is in the protected scope and returns YES / NO / ONLY_WITH_APPROVAL plus the matching rule.
obsidia_mapping_type: reduced
obsidia_agents:
  - CANON_GUARDIAN
obsidia_reduction: protected-file and canon-safety checks only
---

# Freeze Guardian

## Purpose

Block accidental edits on frozen / sealed / canonical files. Provide a clear YES / NO / ONLY_WITH_APPROVAL verdict with reasoning before any modification.

## When to use

- User asks to "edit" / "modify" / "fix" / "update" / "rename" / "regenerate" / "reformat" any file.
- A skill or agent is about to call `Edit` / `Write` on any file.
- User asks "is it safe to change X?".

## When NOT to use

- The user is asking purely conceptual questions — use `read-only-inspector`.
- The target is clearly in a non-protected, non-sensitive folder (e.g. `docs/notes/`, `staging/draft.md`) — quick verdict OK, no full output template needed.

## Operating rules

1. Match the target path against the glob list in `.Codex/context/PROTECTED_SCOPE.md`.
2. If matched: emit `NO` or `ONLY_WITH_APPROVAL`, never `YES`.
3. Files containing `root`, `seal`, `hash`, `anchor`, `freeze` in their name → default to `ONLY_WITH_APPROVAL`.
4. Suggest a **safe alternative** for every blocked edit.
5. Never silently approve. Always emit a verdict.

## Required output format

```
Protected scope:           <which glob(s) matched, or "none">
Canonical / freeze status: <FROZEN | SEALED | ANCHORED | VENDORED | INTENTIONAL_FIXTURE | NONE>
Modification allowed?      YES | NO | ONLY_WITH_APPROVAL
Risk:                      NONE | LOW | MEDIUM | HIGH
Required approval:         <none | "user must reply 'Approved.'">
Safe alternative:          <e.g., "write a patch into staging/", "open a new V18 bundle", "use a verifier override flag", or "edit a copy in audit/local/">
Verification:              <command sequence to confirm the change is correctly applied>
```

## Decision matrix

| Path matches | Verdict | Risk |
|---|---|---|
| `proofs/V18_*/**`, `proofs/lean/**`, `proofs/tla/**`, `formal/tla/**` | ONLY_WITH_APPROVAL | HIGH |
| `proofs/merkle_*.json`, `proofs/rfc3161_anchor.json`, `merkle_*.json` | ONLY_WITH_APPROVAL | HIGH |
| `server.kernel.sealed.cjs` | NO | HIGH |
| `RECUPE_SCORING/*_stable.py` | ONLY_WITH_APPROVAL | HIGH |
| `sigma/contracts.broken-ragnarok.py` | NO | HIGH (intentional fixture) |
| `P1_FREEZE_NOTE.md`, `PUBLIC_STATUS.md` | ONLY_WITH_APPROVAL | MEDIUM |
| `vendor/wheels/**`, `System.*/`, `Google.Protobuf.*/` | NO | MEDIUM |
| `.env*`, `secrets/**`, `*.pem`, `audit/local/**` | NO | HIGH |
| Anything else not protected | YES | NONE / LOW / MEDIUM (case-by-case) |

## Forbidden actions

- Returning `YES` for any path matching the protected list.
- Skipping the verdict to "save time".
- Approving on behalf of the user.
- Suggesting unsafe alternatives (e.g., "just edit it and we'll regenerate the seal").

## Verification checklist

- [ ] Verdict was rendered before any `Edit` / `Write` call.
- [ ] Matched glob is cited.
- [ ] Safe alternative is provided.
- [ ] Approval requirement is explicit.
- [ ] Verification command is provided.
