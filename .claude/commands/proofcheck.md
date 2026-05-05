---
description: Read-only investigation of a proof / kernel / seal / Merkle / RFC3161 issue. Never edits.
allowed-tools: Read, Glob, Grep, Task, Bash(git status:*), Bash(git log:*), Bash(git diff:*), Bash(git show:*)
---

Activate the `proof-sentinel` skill.

Target: $ARGUMENTS

If `$ARGUMENTS` is empty, default to: investigate the current `proofs/PROOFKIT_REPORT.json` FAIL on `V18_3_1_root_hash_verify`.

Procedure:
1. Read `.claude/context/PROTECTED_SCOPE.md` first to confirm read-only posture.
2. Localize via `MODULE_MAP.md` and `Glob` — never broad-read `proofs/`.
3. Read `proofs/PROOFKIT_REPORT.json` (this file is regenerated, not protected for read).
4. Use `git log --oneline -- <relevant path>` to spot recent changes.
5. Classify the failure into one of:
   - REAL_RUPTURE
   - CI_FALSE_RED
   - STALE_MANIFEST
   - ENCODING_DRIFT
   - LINE_ENDING_DRIFT
   - WRONG_CWD
   - CONTENT_CORRUPTION
6. For diagnosis only, optionally delegate to:
   - `proof-checker` agent (Lean / `lake build`)
   - `tla-validator` agent (TLA+ / TLC + drift between `proofs/tla/` and `formal/tla/`)
7. Produce the output defined in `.claude/skills/proof-sentinel/SKILL.md`.

Rules:
- READ ONLY. No `Edit`, no `Write`.
- Never run `verify_all.py`, `verify_merkle.py`, `lake build`, `tla2tools.jar`, or `pytest` without showing the command first as PREPARED and getting explicit user approval.
- Never propose a repair without first eliminating CI_FALSE_RED, STALE_MANIFEST, ENCODING_DRIFT, LINE_ENDING_DRIFT, WRONG_CWD.
- All repair plans require the user's explicit "Approved." in this session before any subsequent edit.
