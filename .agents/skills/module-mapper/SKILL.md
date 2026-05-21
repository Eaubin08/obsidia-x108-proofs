---
name: module-mapper
description: Use this skill when the repo structure changes (new top-level folder, removed module, renamed area, new versioned proof bundle) or when the user says "update the map", "the map is stale", "what's in this repo now". Output is a proposed diff to .Codex/context/MODULE_MAP.md — never written without approval.
obsidia_mapping_type: to_verify
obsidia_agents: []
obsidia_reduction: likely linked to Atlas/Cartographe family, pending full extraction
---

# Module Mapper

## Purpose

Keep `.Codex/context/MODULE_MAP.md` accurate and compact. The map is the routing index used by every other skill — if it lies, every downstream decision degrades.

## When to use

- A new top-level folder appeared
- A module was renamed or removed
- A new versioned bundle was added under `proofs/` (e.g. `V18_9/`)
- The user says "update the map", "the map is wrong", "what's new in the repo structure"
- After a merge from `origin/main` that includes structural changes

## When NOT to use

- The change is purely inside an existing module (file added inside `sigma/tests/`) — too granular for the map.
- The user is asking for a code change — wrong skill, route to `agent-router-obsidia`.

## Operating rules

1. Always **read** `.Codex/context/MODULE_MAP.md` first to know what's already documented.
2. Use `Glob` + `git status --short` + `git diff --stat HEAD~5..HEAD` to spot structural changes.
3. Keep the map ≤ 200 lines. If it grows, archive older sections to `.Codex/memory/snapshots/MODULE_MAP-<date>.md`.
4. Never include file content — paths and one-line role descriptions only.
5. Never write the map; **propose a diff** and wait for approval.

## Required output format

```
Mode: PROPOSE
Layer: AGENTIC
Files touched: none until approved

Map drift detected:
- <new folder/file>: <where it appeared>
- <removed/renamed item>: <where>

Proposed diff to .Codex/context/MODULE_MAP.md:
```diff
@@ section <name> @@
+ <new line>
- <removed line>
  ...
```

Justification:
<one paragraph: why these changes preserve routing accuracy>

Resulting size: <N lines> (budget: 200)
Approval required: YES
```

## Forbidden actions

- Writing the map without showing the diff.
- Adding file-by-file detail (this is not a tree, it's a routing map).
- Quoting file contents.
- Removing the canonical "Build / test / verify commands" section without explicit user approval.

## Verification checklist

- [ ] `MODULE_MAP.md` was read first.
- [ ] Diff was shown.
- [ ] Resulting size ≤ 200 lines.
- [ ] No content quoted from any file.
- [ ] User approved before write.
