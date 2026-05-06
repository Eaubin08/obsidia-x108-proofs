# Graph Memory Sandbox — First Dry Run Plan

## Step 1 — enumerate candidates

Use Git-tracked files only.

Candidate roots:

- agents/
- .claude/context/
- .claude/skills/
- docs/

## Step 2 — apply denylist

Any match against DENYLIST.md is rejected.

## Step 3 — produce dry-run reports

Reports only, no graph database yet:

- .graph-memory/reports/dry_run_candidates.md
- .graph-memory/reports/denylist_hits.md
- .graph-memory/reports/token_budget_estimate.md

## Step 4 — review

No indexing happens until dry-run reports are reviewed.
