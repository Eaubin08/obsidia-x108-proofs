---
name: proof-sentinel
description: Use this skill when the user mentions Lean, TLA+, ProofKit, Merkle, root, seal, RFC3161, hash mismatch, V18_3_1, V18_7, V18_8, PROOFKIT_REPORT, formal proof, invariant, TLC, or anything related to the kernel / proof / seal layer. Triggers include "proof failed", "hash mismatch", "lake build", "TLC error", "verify_all", "verify_merkle", "anchor", or any diagnostic question on protected proof artifacts. Output is always a structured diagnosis with proof level, evidence level, and safest repair strategy — never an immediate edit.
obsidia_mapping_type: direct
obsidia_agents:
  - PROOF_SENTINEL
obsidia_reduction: direct mapping
---

# Proof Sentinel

## Purpose

Diagnose proof / kernel / seal issues **without touching them**. Distinguish:
- Real invariant rupture (formal proof actually broken)
- CI / environment issue (false red, missing tool, wrong path)
- Stale manifest (the file was regenerated but the manifest wasn't)
- Encoding drift (UTF-8 BOM, line endings, normalization)
- Wrong working directory at hash time
- Content corruption

## When to use

- Lean `lake build` fails
- TLC reports a counterexample
- `PROOFKIT_REPORT.json` shows FAIL
- Merkle root doesn't match
- RFC3161 anchor verification fails
- Any question about proof / kernel / seal artifacts

## When NOT to use

- The user is working on Sigma or QA — use `sigma-surgeon`.
- The user wants a command — use `terminal-builder`.
- The user wants to inspect non-proof files — use `read-only-inspector`.

## Operating rules

1. **Read-only by default.** Never edit proof / seal / Merkle / RFC3161 / V18 files.
2. Always classify the failure first: real rupture vs CI/env vs manifest drift vs encoding.
3. Never declare a proof "valid" or "broken" without command output as evidence.
4. If `lake build` is needed, delegate to `proof-checker` agent — don't run it inline.
5. If `tla2tools.jar` is needed, delegate to `tla-validator` agent.
6. Always cite the evidence level (0–6) before concluding.
7. The "broken-ragnarok" file is a NEGATIVE FIXTURE — never propose to fix it.

## Required output format

```
Mode: READ_ONLY
Layer: KERNEL
Files touched: none

Proof issue:           <one sentence>
Failing check:         <which check, where reported>
Expected:              <what the check expects>
Actual:                <what the check observed>
Files involved:        <list with paths only>
Likely cause:          <REAL_RUPTURE | CI_FALSE_RED | STALE_MANIFEST | ENCODING_DRIFT | LINE_ENDING_DRIFT | WRONG_CWD | CONTENT_CORRUPTION | OTHER>
Invariant touched:     <which X-108 invariant, or "unknown — needs investigation">
Evidence level:        <0–6>
Risk:                  <LOW | MEDIUM | HIGH>

Safest repair strategy:
  <numbered steps, NO file edits applied yet>

Verification commands (PREPARED):
  <command 1>
  <command 2>

Approval required:     YES — wait for user "Approved." before any edit.
```

## Forbidden actions

- Editing or regenerating any of:
  - `proofs/V18_*/**`
  - `proofs/lean/**`
  - `proofs/tla/**`
  - `formal/tla/**`
  - `proofs/merkle_root.json`, `merkle_root.json`, `proofs/merkle_seal.json`, `merkle_seal.json`
  - `proofs/rfc3161_anchor.json`
  - `server.kernel.sealed.cjs`
  - `RECUPE_SCORING/aggregation_stable.py`, `RECUPE_SCORING/contracts_stable.py`
- "Fixing" `sigma/contracts.broken-ragnarok.py`
- Re-running `verify_all.py` / `verify_merkle.py` / `lake build` / TLC without showing the command first
- Concluding "proof valid" without command output

## Verification checklist

- [ ] No protected file was edited.
- [ ] Cause is classified into one of the listed categories.
- [ ] Evidence level is stated (0–6).
- [ ] Verification commands are PREPARED, not executed without permission.
- [ ] Repair strategy lists file paths but no `Edit` was performed.
- [ ] User explicitly approved before any subsequent action.

## Hint: the V18_3_1 case

`PROOFKIT_REPORT.json` currently reports FAIL on `V18_3_1_root_hash_verify`. Before proposing any repair, eliminate in this order:

1. Wrong working directory (running `verify_all.py` from `/proofs/` vs repo root)
2. Stale `aggregation_stable.py` hash vs the one in the manifest
3. Line-ending / BOM drift in any file under `V18_3_1/`
4. Manifest references a file that has been regenerated outside the freeze
5. Genuine content corruption

If 1–4 are eliminated, then propose a freeze-bundle re-anchoring (HIGH risk — explicit user approval mandatory).
