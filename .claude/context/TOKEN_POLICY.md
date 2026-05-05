# Token Policy

> Goal: keep per-session token cost low without losing context coherence.
> Strategy: load minimal stable context, zoom into the active layer only.

## Default context loading order

```
1.  CLAUDE.md                         (small index)
2.  .claude/memory/SCRATCH.md         (live state, ≤ 300 tokens)
3.  .claude/context/CURRENT_FOCUS.md  (≤ 300 tokens)
4.  .claude/context/MODULE_MAP.md     (≤ 200 lines)
5.  ONE context file matching task layer (e.g. PROTECTED_SCOPE before any edit)
6.  Targeted Glob / Grep (no broad recursive scan)
7.  Read smallest relevant files (use offset/limit, never full reads of files > 300 lines)
8.  Summarize findings in chat; ASK before any broad scan
```

## Hard prohibitions

- ❌ Broad recursive `Read` of any folder
- ❌ Reading all docs / all proofs / all artifacts
- ❌ Dumping a > 300-line file into context "just to see"
- ❌ Re-auditing the repo unless explicitly requested
- ❌ Loading context for a layer that is not the active layer
- ❌ Quoting back > 15 words from a protected file

## When the context approaches 60%

- Update `CURRENT_FOCUS.md` with a delta (3–5 lines).
- Suggest `/compact` to the user.
- Resume from `CURRENT_FOCUS.md`, not from re-reading.

## Cost rule of thumb

- Whole-repo cold read for a 50k-LOC repo: ~80k tokens.
- Targeted read with `MODULE_MAP.md` routing + `explorer` subagent + 3 small files: ~10–15k tokens.
- Therefore: **always route through `MODULE_MAP.md` first**.

## When a broad read seems necessary

Run the `token-guard` skill first. It will:

1. Ask the question more precisely.
2. Propose a 3-step targeted alternative.
3. Estimate the token cost of both options.
4. Surface the cheaper plan for user approval.

## Subagent delegation

For any discovery task ("where is X", "how is Y wired"), delegate to the `explorer` subagent. It opens its **own context window**, reads what it needs, and returns a 5–10 line summary. The parent agent never sees the raw files.

## Persistent memory

- `SCRATCH.md` is the per-session scratch.
- `CURRENT_FOCUS.md` is the per-week working state.
- `RISKS.md` and `P1_FREEZE.md` are stable references.
- Optional: `wiki-brain-bridge` skill for a project-wide knowledge graph (NOT auto-installed; sandbox eval first).
