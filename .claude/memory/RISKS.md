# RISKS — known dangers before any edit

> Compiled from the read-only inspection report provided to Claude on this repo.
> Update only when a new risk is positively identified (not on speculation).

---

## 1. PROOFKIT_REPORT.json reports FAIL

`proofs/PROOFKIT_REPORT.json` reports **overall: FAIL** because `V18_3_1_root_hash_verify` shows a hash mismatch between expected and observed.

**Why it matters:** Any edit under `proofs/V18_3_1/**` risks deepening or masking this known failure without a clear fix path.

**Treatment:** Do not auto-repair. Diagnose first via `/proofcheck` (read-only). Eliminate stale-manifest / encoding / line-ending / wrong-cwd hypotheses before touching any file.

---

## 2. server.kernel.sealed.cjs is sealed

The `.sealed` naming signals tamper-evidence. Editing it would silently break integrity checks that may not be visible at runtime.

**Treatment:** Treat as read-only. Never edit. If a change is needed, it must go through a separate sealing process — out of scope for Claude Code.

---

## 3. Merkle-anchored files

`merkle_seal.json`, `proofs/merkle_root.json`, and `proofs/rfc3161_anchor.json` are cryptographic anchors. **Any change to a tracked file recomputes the Merkle root, invalidating the existing seal.**

Re-anchoring via RFC3161 requires an external TSA call and is HIGH risk.

**Treatment:** Never edit anchors directly. Never reformat anchored content.

---

## 4. Two TLA+ trees can drift

`formal/tla/` is what CI actually runs.
`proofs/tla/` is the richer reference copy.

They can drift over time. Editing one without mirroring the other risks proof divergence.

**Treatment:** When working on TLA+, always check both. Use the `tla-validator` subagent's drift-check.

---

## 5. RECUPE_SCORING/*_stable.py are frozen but CI does py_compile only

`RECUPE_SCORING/aggregation_stable.py` and `RECUPE_SCORING/contracts_stable.py` are deliberately frozen.

The CI workflow only runs `python -m py_compile` on them — **logic regressions would not be caught**.

**Treatment:** Treat as protected. Logic changes require explicit user approval and a manual verification plan beyond CI.

---

## 6. sigma/contracts.broken-ragnarok.py is intentionally broken

The "broken" naming is deliberate — likely a negative fixture used by a test that asserts the failure mode.

**Treatment:** Do NOT attempt to fix it. If asked, escalate to the user with a `freeze-guardian` verdict.

---

## 7. P1_FREEZE_NOTE.md exists

A deliberate code freeze marker on certain content. Always check this file before editing anything in scope of Phase 1.

**Treatment:** Cross-reference any proposed edit against `P1_FREEZE_NOTE.md` and `.claude/memory/P1_FREEZE.md`. If overlap → `freeze-guardian` ruling.

---

## 8. Vendored .NET packages at root

`System.*/` and `Google.Protobuf.*/` folders at the repo root are vendored .NET dependencies. Deleting or moving them could break C# tooling silently.

**Treatment:** Never move, rename, or delete. Treat as `VENDORED` per `PROTECTED_SCOPE.md`.

---

## 9. Branch is unmerged and ahead of origin/main

The current branch is 2 commits ahead of `origin/main`, not yet pushed/merged. Any merge to `main` triggers CI against all proof jobs.

**Treatment:** Do NOT push without explicit user approval. Run `/recap` before any merge attempt.

---

## How to add a new risk

A risk is added here only when:

1. It is positively identified from inspection or test output (not speculation).
2. It has at least one piece of evidence (file:line, command output, log line).
3. The "Treatment" section gives a concrete protective rule.

If unsure, file the candidate risk in `SCRATCH.md` under "Open questions" and bring it up with the user.
