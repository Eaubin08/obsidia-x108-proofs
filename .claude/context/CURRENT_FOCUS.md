# Current Focus

> **Read this every session start.** Update at session end with a short delta.
> Keep ≤ 300 tokens. If it grows, move stale entries to `.claude/memory/snapshots/`.

---

## Current phase

Public repo cleanup completed. Canonical repo established. Next mission: choose next technical phase from roadmap.

## Active branch (as of last inspection)

- Branch: `main`
- Working tree: clean
- HEAD: `5c5c2ef` (aligned with origin/main)
- Canonical repo: `obsidia-x108-proofs_REMOTE_A5F21C6B`
- Old repo (`obsidia-x108-proofs`): `.git/config` corrupted — kept local, not canonical

## Known issues

- V18_3_1 root hash mismatch: **RESOLVED** (PROOFKIT_REPORT.json regenerated 2026-05-21, all checks PASS)
- Old repo `.git/config` corruption: NOT fixed — circumvented by using REMOTE clone as canonical

## Next technical mission

Choose next mission from `docs/roadmap/NOT_YET_IMPLEMENTED_AFTER_V2.md`:

- [ ] Runtime ACT réel
- [ ] Graphiti/Brody feedback loop
- [ ] Ledger Gencoin persistant
- [ ] Tests adversariaux
- [ ] Seuils par domaine
- [ ] Vue régulateur
- [ ] Machine-checking

## Open questions

- (none)

## 2026-05-05 settings-cleanup
- branch: ci-strict-sigma-qa-no-false-error_20260502_235213
- did: removed invalid `hooks._disabled_by_default` key from `.claude/settings.json`; committed as 4ea9de5
- next: begin read-only PROOF_SENTINEL diagnosis of V18_3_1 root hash mismatch
- blocked on: nothing

## 2026-05-26 public-cleanup-freeze
- branch: main (canonical: obsidia-x108-proofs_REMOTE_A5F21C6B)
- did: phases 1-4 public repo cleanup completed + 4 git tags pushed (HEAD 5c5c2ef)
- next: choose next technical mission from NOT_YET_IMPLEMENTED_AFTER_V2.md
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
