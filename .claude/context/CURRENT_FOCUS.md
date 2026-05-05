# Current Focus

> **Read this every session start.** Update at session end with a short delta.
> Keep ≤ 300 tokens. If it grows, move stale entries to `.claude/memory/snapshots/`.

---

## Current phase

Configuring Claude Code for Obsidia-safe local operation (project-local guidance layer).

## Active branch (as of last inspection)

- Branch: `ci-strict-sigma-qa-no-false-error_20260502_235213`
- Working tree: clean
- Ahead of `origin/main`: 2 commits, NOT pushed
- Recent theme: CI hardening — Sigma QA false-positive reduction, RFC3161 cross-platform skip when no tests collect

## Known issues

- `proofs/PROOFKIT_REPORT.json` reports **FAIL** on `V18_3_1_root_hash_verify` (hash mismatch). **Do not silently fix.** Diagnose first.

## Next technical mission (after configuration is complete)

**Investigate the V18_3_1 root hash mismatch in read-only mode before any repair.**

Determine which of these is the cause:

- [ ] Stale manifest
- [ ] Content corruption
- [ ] Encoding drift (UTF-8 BOM, etc.)
- [ ] Line-ending drift (CRLF vs LF)
- [ ] Wrong working directory at hash time
- [ ] Root file mismatch (which file is the "root"?)
- [ ] `aggregation_stable.py` hash changed between freeze and current
- [ ] Generated root artifact mismatch

**Do not repair yet.** Diagnosis first, then propose, then approve, then patch surgically.

## Open questions

- (none recorded yet — add as they come up)

## What changed last session

- 2026-05-05 settings-cleanup: removed invalid Claude hooks placeholder from `.claude/settings.json` (4ea9de5). Configuration layer closed. V18_3_1 hash investigation queued.

## 2026-05-05 settings-cleanup
- branch: ci-strict-sigma-qa-no-false-error_20260502_235213
- did: removed invalid `hooks._disabled_by_default` key from `.claude/settings.json`; committed as 4ea9de5
- next: begin read-only PROOF_SENTINEL diagnosis of V18_3_1 root hash mismatch
- blocked on: nothing

---

## Update protocol

At session end, the user (or `context-keeper` skill, with approval) appends a 3–5 line delta:

```
## YYYY-MM-DD <short tag>
- branch: <name>
- did: <one line>
- next: <one line>
- blocked on: <one line or "nothing">
```

When this file passes ~80 lines, oldest deltas move to `.claude/memory/snapshots/CURRENT_FOCUS-<date>.md`.
