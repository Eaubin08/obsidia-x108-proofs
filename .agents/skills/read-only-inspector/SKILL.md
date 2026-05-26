---
name: read-only-inspector
description: Use this skill any time the user asks Codex to inspect, audit, examine, look at, analyze, review, understand, or explore the repository without changing anything. This is also the default first step before any modification — when in doubt, route here. Triggers include "inspect", "look at", "what's in", "tell me about this repo", "diagnose", "audit", "examine", "review", or any verb that implies observation rather than action. Output is always a structured report with findings, risks, and the next safest step.
obsidia_mapping_type: reduced
obsidia_agents:
  - OBSIDIA_ATLAS_INGESTOR
obsidia_reduction: repo discovery only, no full memory-card extraction
---

# Read-Only Inspector

## Purpose

Inspect the repository without modifying anything. Produce a structured report so the user can decide the next move.

## When to use

- User says "inspect", "look at", "audit", "diagnose", "examine", "review the code".
- Any task whose stated goal is observation rather than change.
- As the **mandatory first step** before any modification on KERNEL, SIGMA, or protected files.

## When NOT to use

- The user has already explicitly asked for a change to be applied.
- The task is purely conceptual (no repo content involved).
- Use `terminal-builder` instead when the user asks specifically for a command.

## Operating rules

1. Read-only. No `Write`, no `Edit`, no `Bash` that modifies state.
2. Targeted reads only. Never load the whole repo.
3. Always go through `.Codex/context/MODULE_MAP.md` first to localize.
4. If a question requires opening more than 5 files, delegate to the `explorer` subagent.
5. Always end with `Next safest step` — a single, concrete next action.

## Required output format

```
Mode: READ_ONLY
Layer: <KERNEL | SIGMA | CONNECTORS | DOCS | TOOLING | AGENTIC>
Scope: <one line>
Files touched: none

Findings:
- <fact>: <evidence file:line>
- <fact>: <evidence file:line>

Risks:
- <risk>: <why>

Next safest step:
<one concrete sentence — usually a command to run or a question to ask>

Suggested commands (PREPARED, not executed):
<command 1>
<command 2>
```

## Forbidden actions

- Editing, creating, deleting, or moving any file.
- Installing packages.
- Running `autoskills`, `/ultrareview`, `npm install`, `pip install`.
- Loading the whole repository contents.
- Opening protected files (see AGENTS.md §4).

## Verification checklist

- [ ] No `Write` / `Edit` calls were made.
- [ ] `git status --short` was clean before and after.
- [ ] All findings cite file:line evidence.
- [ ] At least one `Next safest step` is given.
- [ ] No protected file was opened.
