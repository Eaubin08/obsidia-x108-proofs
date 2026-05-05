---
description: List protected files & rules before any sensitive edit. Read-only.
allowed-tools: Read, Glob
---

Read `.claude/context/PROTECTED_SCOPE.md` and produce a compact summary:

```
Mode: READ_ONLY
Layer: AGENTIC
Files touched: none

Protected globs (high-risk):
- proofs/V18_*/**           freeze bundles
- proofs/lean/**            Lean 4 sources
- proofs/tla/**             TLA+ reference
- formal/tla/**             TLA+ CI
- proofs/merkle_*.json      crypto anchors
- merkle_*.json             crypto anchors (root)
- proofs/rfc3161_anchor.json TSA anchor
- server.kernel.sealed.cjs  sealed bridge
- RECUPE_SCORING/*_stable.py frozen scoring
- sigma/contracts.broken-ragnarok.py  intentional fixture
- P1_FREEZE_NOTE.md, PUBLIC_STATUS.md  status docs
- vendor/wheels/**, System.*/, Google.Protobuf.*/  vendored deps
- .env*, secrets/**, *.pem, audit/local/**  secrets / local-only

Rules:
- Read-only by default
- No edit / no rename / no reformat / no normalize / no regenerate
- Modification requires explicit user "Approved." + verification plan + rollback path

Use `/freeze-check <path>` to test a specific path.
```

If the user passed `$ARGUMENTS` (a path), run `/freeze-check $ARGUMENTS` instead.
