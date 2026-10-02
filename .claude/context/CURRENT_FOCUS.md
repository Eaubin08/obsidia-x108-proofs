# Current Focus

> Read this every session start. Keep this file short.
> Git branch, HEAD, and working-tree cleanliness are not durable memory:
> verify them with `git branch --show-current`, `git rev-parse --short HEAD`,
> and `git status --short` at session start.

---

## Current phase

Claude configuration concordance cleanup is in progress. The target is a light
default Claude session with MCP `obsidia` disabled unless explicitly requested
for a mission.

## Current WIP

- Update Claude memory so it no longer presents branch, HEAD, or "clean" state
  as durable truth.
- Keep `.claude/settings.json` as the versioned conservative baseline.
- Keep `.claude/settings.local.json` as local operator configuration.
- Inspect and remove only confirmed nested `.claude/` config copies.
- Do not touch protected proof/seal files, including `merkle_seal.json`.

## Operating rule

Before acting on any remembered state, re-measure live Git state. Memory may
name the current objective and known WIP, but Git is the authority for branch,
HEAD, staged changes, unstaged changes, and untracked files.

## Session modes

- `LIGHT_SESSION`: default. MCP `obsidia` disabled; use targeted file reads,
  grep, and read-only Git commands.
- `MCP_SESSION`: explicit opt-in when the mission needs the local Obsidia MCP
  bridge. MCP output is advisory tooling, not project authority.
- `LOOP_SESSION`: long-running Claude work. Keep normal safety gates; stop on
  edits, protected files, doctrine choices, push, merge, or broad commands.
- `AUDIT_SESSION`: read-only concordance or repo audit. Produce evidence and a
  decision matrix; do not patch unless the user switches to APPLY.

## Next

Finish this Claude configuration cleanup, show the diff, and then prepare a
separate divergence matrix for `.claude/skills` versus `.agents/skills`.

---

## Update protocol

At session end, append only short objective/WIP deltas. Do not store branch,
HEAD, or "clean" status as durable truth; store the command to verify them
instead.
