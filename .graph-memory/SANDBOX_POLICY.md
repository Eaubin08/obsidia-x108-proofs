# Graph Memory Sandbox — Policy

## Operating mode

Default mode: DRY-RUN.

Graph memory tooling may inspect allowlisted files only.
It must not modify repo source files.
It must not index denied files.
It must not send indexed content to cloud services without explicit approval.

## Boundary

Graph memory is a navigation and retrieval aid.
It is not a proof system.
It is not the canon.
It is not X-108.
It does not decide ALLOW / HOLD / BLOCK.

## Required behavior

Before indexing:
1. list candidate files
2. show allowlist matches
3. show denylist matches
4. show rejected files
5. estimate token / file count
6. wait for explicit approval

## Output locations

Allowed generated output locations:

- .graph-memory/out/
- .graph-memory/reports/

No generated graph files may be written outside `.graph-memory/`.

## First safe test

Index only:

- agents/
- .claude/context/
- .claude/skills/
- docs/*.md

Then produce:

- .graph-memory/reports/dry_run_candidates.md
- .graph-memory/reports/denylist_hits.md
- .graph-memory/reports/token_budget_estimate.md
