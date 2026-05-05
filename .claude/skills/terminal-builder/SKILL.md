---
name: terminal-builder
description: Use this skill when the user asks for a shell command, a script, a runner, or a sequence of terminal steps. Triggers include "give me the command", "how do I run", "PowerShell", "bash", "script to", "one-liner", or any request whose deliverable is a copy-pasteable command. Output is always a command block with description, expected output, possible errors, verification, and rollback. Defaults to PowerShell 7 on Windows.
obsidia_mapping_type: direct
obsidia_agents:
  - TERMINAL_BUILDER
obsidia_reduction: direct mapping
---

# Terminal Builder

## Purpose

Generate **safe, verifiable, copy-pasteable** terminal commands. PowerShell-first on Windows, Bash on Linux/macOS.

## When to use

- User asks for a command, a script, a one-liner.
- User wants to run a Python verifier, a Lean build, a TLC model-check, a PowerShell runner.
- User wants to inspect via CLI rather than via Claude Code reads.

## When NOT to use

- The user wants Claude to **directly modify files** — use `sigma-surgeon` or another action skill.
- The user is asking a conceptual question — use `read-only-inspector`.

## Operating rules

1. PowerShell 7 by default on Windows (user is on Ardennes, FR / Windows).
2. Use **absolute or repo-relative** paths — no `~/`, no implicit cwd assumptions.
3. Every command block ships with: description, expected output, error patterns, verification, rollback.
4. Tag each block with **PREPARED** (not run), **EXECUTED** (run, output captured), or **PROVED** (verification confirmed).
5. Never instruct the user to "open the file in an editor". Use `code`, `notepad`, or a Claude Code edit instead.
6. Destructive commands (rm, git reset, force push) require an explicit "Approved." from the user before execution.

## Required output format

```
Mode: PROPOSE
Layer: TOOLING
Files touched: none (commands are PREPARED until user runs them)

Command block:
  <verbatim command>

What it does:
  <one paragraph max>

Expected proof / output:
  <what success looks like>

Possible errors:
  - <error pattern> → <cause + fix>
  - <error pattern> → <cause + fix>

Verification command:
  <command to confirm the action took effect>

Rollback path:
  <how to undo>

Status: PREPARED
```

## PowerShell template

```powershell
#Requires -Version 7
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# <description>
<command>

# Verification
<verification>
```

## Bash template

```bash
#!/usr/bin/env bash
set -euo pipefail

# <description>
<command>

# Verification
<verification>
```

## Forbidden actions

- Producing commands that download from arbitrary URLs (`curl http://...`).
- `npm install`, `pip install`, `winget install` without explicit user request.
- `git push --force` without explicit "Approved." from user.
- `rm -rf` on anything outside an opt-in scratch path.
- Suggesting commands that bypass `freeze-guardian` checks.

## Verification checklist

- [ ] Every command has its verification line.
- [ ] Every command has its rollback path.
- [ ] No protected path is the target of a write.
- [ ] PowerShell scripts include `#Requires -Version 7` and `Set-StrictMode`.
- [ ] Bash scripts include `set -euo pipefail`.
- [ ] Status tag is one of PREPARED / EXECUTED / PROVED.
