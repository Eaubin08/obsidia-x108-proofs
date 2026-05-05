---
name: token-guard
description: Use this skill before any broad read, recursive scan, or "load everything" operation. Triggers automatically when a request would imply reading more than 5 files, or when the user says "look at everything", "scan the repo", "read all the docs", "audit the whole codebase". Output is a justification + a cheaper targeted plan with token-cost estimates.
obsidia_mapping_type: composite
obsidia_agents:
  - ANTI_DISPERSION
obsidia_reduction: token discipline and anti-broad-read behavior; CONTEXT_KEEPER is local behavior, not registry agent
---

# Token Guard

## Purpose

Stop broad reads before they happen. Force every "read a lot" intent to justify itself or downgrade to a targeted plan.

## When to use

- A request would read > 5 files
- A request implies recursive scan ("the whole repo", "all the proofs", "every doc")
- The user has not specified a target file
- Before any `/ultrareview`-style operation (which is forbidden anyway, see EXTERNAL_TOOLS_POLICY)
- When the active context is already > 50 % full and the next step would be a broad read

## When NOT to use

- The user explicitly named a single file to read
- The user explicitly approved a broad scan in this session
- A targeted Glob / Grep returns < 5 hits

## Operating rules

1. Estimate the token cost of the broad option.
2. Estimate the token cost of a targeted alternative.
3. Always offer the targeted alternative first.
4. The broad scan only happens if the user explicitly chooses it.
5. When in doubt, defer to `read-only-inspector` (read-only) or `explorer` subagent (isolated context).

## Required output format

```
Mode: PROPOSE
Layer: AGENTIC
Files touched: none

Detected intent:    <one sentence rephrasing the user's request>
Broad read estimate:
  files:  ~<N>
  tokens: ~<estimate, in thousands>
  cost:   <relative — HIGH | VERY_HIGH>

Targeted alternative:
  step 1: <Glob / Grep with exact pattern>
  step 2: <Read N lines from M files>
  step 3: <delegate to explorer subagent if > 5 files>
  files:  ~<N> (much smaller)
  tokens: ~<estimate, in thousands>
  cost:   <LOW | MEDIUM>

Why the alternative works:
<one paragraph>

Decision:
[ ] Proceed with broad read (user must say "broad read approved")
[X] Proceed with targeted alternative (default)

Next action: <concrete next step>
```

## Estimation heuristics (rough)

| File type | Avg tokens / file |
|---|---|
| Markdown doc | 1 500 |
| Python module | 2 000 |
| Lean / TLA spec | 1 500 |
| JSON manifest | 500 |
| Test file | 1 000 |
| PowerShell script | 800 |

A "scan all docs" of `docs/` (assume 30 files) ≈ 45 000 tokens.
A targeted Grep + 3 file Reads ≈ 5 000 tokens. Order-of-magnitude savings.

## Forbidden actions

- Performing a broad read silently to "save the user from the question".
- Hiding the cost estimate.
- Skipping the targeted alternative.
- Pretending a broad scan was the only option.

## Verification checklist

- [ ] Both costs (broad vs targeted) were shown.
- [ ] Targeted alternative is concrete (specific Glob / Grep / Read calls).
- [ ] User decision is captured before the read happens.
- [ ] If user picked broad, this is logged in `SCRATCH.md` so it's not repeated next session.
