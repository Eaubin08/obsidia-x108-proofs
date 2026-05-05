---
name: sigma-surgeon
description: Use this skill when the user wants to modify, debug, or extend code under sigma/, qa/cross-platform/, connectors/, MonProjet/, or anything in the orchestration / periphery / QA layer. Triggers include "sigma", "aggregator", "contracts", "monitor", "QA test", "RFC3161 test", "cross-platform", "connector", "bank scenario", "trading scenario", "aviation scenario". Output is a surgical patch plan that preserves BLOCK > HOLD > ALLOW semantics and never contaminates the kernel / proof layer.
obsidia_mapping_type: composite
obsidia_agents:
  - CO_PILOTE_CODE
  - CI_REPO_SURGEON
obsidia_reduction: Sigma/periphery only, no kernel/proof/seal edits
---

# Sigma Surgeon

## Purpose

Make minimal, surgical changes inside the **Sigma orchestration / periphery / QA** layer. Preserve `BLOCK > HOLD > ALLOW` semantics. Never touch the kernel / proof / seal layer.

## When to use

- Edits or new tests in `sigma/`, `sigma/tests/`, `qa/cross-platform/`
- Connector changes in `connectors/<domain>/`
- Domain payload tweaks in `MonProjet/`
- New / modified pytest tests for Sigma pipeline, monitor, aggregator, contracts

## When NOT to use

- Touching `proofs/`, `formal/tla/`, Merkle anchors, RFC3161, `server.kernel.sealed.cjs` — use `proof-sentinel` instead.
- Touching `RECUPE_SCORING/*_stable.py` — use `proof-sentinel` (these are frozen).
- Touching `sigma/contracts.broken-ragnarok.py` — DO NOT touch (intentional negative fixture).

## Operating rules

1. Stay strictly inside the SIGMA layer — verify with `freeze-guardian` before any edit.
2. Preserve `BLOCK > HOLD > ALLOW` priority order in every code path.
3. Preserve X-108 governance semantics — Sigma must not bypass kernel decisions.
4. Run the matching pytest after every change (one test file at a time, never full suite without approval).
5. Use the `sigma-checker` agent for diagnosis before patching.

## Required output format

```
Mode: PROPOSE
Layer: SIGMA
Files touched: <list>

Sigma issue:           <one sentence>
Files involved:        <list with full paths>
Kernel impact:         NONE | INDIRECT | DIRECT (DIRECT requires escalation to proof-sentinel)
BLOCK>HOLD>ALLOW preserved? YES | NO | NEEDS_REVIEW
Patch plan:            <numbered steps with file:line targets>
Tests:                 <pytest file(s) that cover the change>
Regression risks:      <list>
Rollback path:         <git restore <files> OR git revert <commit>>

Verification commands (PREPARED):
  python -m pytest <test file> -v
  python -m pytest sigma/tests -v -k "<related keyword>"   # when broader check is justified

Approval required:     YES (default) — wait for user "Approved."
```

## Forbidden actions

- Editing any file outside the SIGMA layer.
- "Fixing" `sigma/contracts.broken-ragnarok.py`.
- Reformatting / normalizing Sigma files that don't relate to the patch.
- Running the full pytest suite without explicit user approval (cost + noise).
- Adding dependencies to `requirements.txt` without explicit approval.
- Inverting `BLOCK > HOLD > ALLOW` priority anywhere.

## Verification checklist

- [ ] All edited files are inside the Sigma layer.
- [ ] `freeze-guardian` returned YES on every edited file.
- [ ] `BLOCK > HOLD > ALLOW` is preserved in the diff (review pre/post).
- [ ] Matching pytest file passes locally before reporting success.
- [ ] `git status --short` shows only Sigma-layer files.
- [ ] No hidden change in `connectors/`, `MonProjet/`, `proofs/`, or root scripts.
