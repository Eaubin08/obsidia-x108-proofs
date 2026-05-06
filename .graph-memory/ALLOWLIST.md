# Graph Memory Sandbox — ALLOWLIST

Only these paths are allowed for initial graph-memory indexing.

## Phase 0 allowlist

- agents/registry.md
- agents/registry.json
- agents/prompts/*.md
- agents/bootstrap/*.md
- agents/routing/*.md
- CLAUDE.md
- MANIFEST.md
- .claude/context/*.md
- .claude/skills/*/SKILL.md
- docs/*.md

## Conditional allowlist

These may be indexed only after explicit approval:

- sigma/*.py
- sigma/tests/*.py
- connectors/**/*.py
- qa/**/*.py
- .github/workflows/*.yml

## Rule

If a file is not explicitly allowed, it is denied by default.
