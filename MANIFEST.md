# MANIFEST — Obsidia X-108 Claude Code Configuration Package

> **Status**: package generated in `/mnt/outputs/claude-config/`. **NOT installed** in any real repo.
> **Target repo**: `obsidia-x108-proofs` (and its demo, by reuse).
> **Generation date**: 2026-05-05.
> **Build philosophy**: minimal, conservative, no aggressive hooks, no auto-install, no auto-format.

---

## 0. What this package is

A complete project-local guidance layer for Claude Code: doctrine (`CLAUDE.md`), context files (`.claude/context/`), skills (`.claude/skills/`), subagents (`.claude/agents/`), slash commands (`.claude/commands/`), memory templates (`.claude/memory/`), hook scripts (`.claude/hooks/`), and minimal `settings.json`.

**Total package files: 46**
- Root files: 2
- .claude files: 44

Across 7 sub-areas. No source-of-the-repo file is touched.

---

## 1. Full file tree

```
claude-config/
├── CLAUDE.md                                       index + entrypoint (no detailed doctrine)
├── MANIFEST.md                                     this file
└── .claude/
    ├── settings.json                               permissions + env, NO active hooks
    │
    ├── context/                                    deep doctrine (read on demand)
    │   ├── OBSIDIA_IDENTITY.md
    │   ├── CURRENT_FOCUS.md
    │   ├── MODULE_MAP.md
    │   ├── PROTECTED_SCOPE.md
    │   ├── TOKEN_POLICY.md
    │   ├── FRACTAL_INFERENCE.md
    │   ├── AGENTIC_ROUTING.md
    │   ├── WORKFLOW.md
    │   └── EXTERNAL_TOOLS_POLICY.md
    │
    ├── skills/                                     activatable behaviors
    │   ├── read-only-inspector/SKILL.md
    │   ├── terminal-builder/SKILL.md
    │   ├── proof-sentinel/SKILL.md
    │   ├── freeze-guardian/SKILL.md
    │   ├── sigma-surgeon/SKILL.md
    │   ├── agent-router-obsidia/SKILL.md
    │   ├── graph-calibrator-obsidia/SKILL.md
    │   ├── context-keeper/SKILL.md
    │   ├── token-guard/SKILL.md
    │   ├── module-mapper/SKILL.md
    │   └── wiki-brain-bridge/SKILL.md
    │
    ├── agents/                                     subagents (isolated context)
    │   ├── explorer.md
    │   ├── proof-checker.md
    │   ├── tla-validator.md
    │   ├── sigma-checker.md
    │   ├── context-keeper.md
    │   └── risk-reviewer.md
    │
    ├── commands/                                   slash commands
    │   ├── inspect.md
    │   ├── focus.md
    │   ├── update-focus.md
    │   ├── proofcheck.md
    │   ├── sigmacheck.md
    │   ├── route.md
    │   ├── tokencheck.md
    │   ├── protected.md
    │   ├── freeze-check.md
    │   └── recap.md
    │
    ├── memory/                                     templates + working state
    │   ├── SCRATCH.md            (TEMPLATE — fill in at runtime)
    │   ├── RISKS.md              (from inspection report)
    │   ├── P1_FREEZE.md          (some entries TO_VERIFY)
    │   └── snapshots/            (empty, populated by pre-compact-snapshot.sh)
    │
    └── hooks/                                      scripts only — NOT wired by default
        ├── session-start.sh
        ├── pre-edit-protected-warn.sh
        ├── pre-compact-snapshot.sh
        └── EXAMPLES.md           (how to opt-in via settings.local.json)
```

---

## 2. Purpose of each file (one line)

### Root

| File | Purpose |
|---|---|
| `CLAUDE.md` | Index + entrypoint. Points to `.claude/context/*` for deep rules. |
| `MANIFEST.md` | This file. Install / verify / scope. |

### `.claude/settings.json`

Minimal permissions + env. **No active hooks.** Denies `npm/pip/winget install`, `git push`, `git reset --hard`, edits to protected globs.

### `.claude/context/` (9 files)

| File | Purpose |
|---|---|
| `OBSIDIA_IDENTITY.md` | What Obsidia / X-108 is. Layer hierarchy. Why web-dev defaults don't apply. |
| `CURRENT_FOCUS.md` | Live working state — phase, branch, known issues, next mission. |
| `MODULE_MAP.md` | Compact map of repo folders + canonical build/test commands. |
| `PROTECTED_SCOPE.md` | Glob list of files that must not be edited / reformatted / renamed. |
| `TOKEN_POLICY.md` | 8-step context loading order; never broad-recursive. |
| `FRACTAL_INFERENCE.md` | Zoom strategy per layer; link calibration (type/strength/evidence). |
| `AGENTIC_ROUTING.md` | 52 agents / 9 families; Vertex AI vs Local; 10 local modes. |
| `WORKFLOW.md` | 10-step default workflow + mandatory response header + git discipline + proof scale 0–6. |
| `EXTERNAL_TOOLS_POLICY.md` | autoskills NO; Graphify NEEDS sandbox; MCP NEEDS approval; never fetch token URLs. |

### `.claude/skills/` (11 skills)

| Skill | Purpose |
|---|---|
| `read-only-inspector` | Inspect without modifying. Always step 1. |
| `terminal-builder` | Generate safe PowerShell / Bash commands with verification + rollback. |
| `proof-sentinel` | Diagnose Lean / TLA / Merkle / seal / RFC3161 issues, read-only, classify cause. |
| `freeze-guardian` | YES / NO / ONLY_WITH_APPROVAL verdict on edit-safety. |
| `sigma-surgeon` | Surgical Sigma edits; preserve BLOCK > HOLD > ALLOW; no kernel contamination. |
| `agent-router-obsidia` | Detect intent → one primary layer + one active mode. |
| `graph-calibrator-obsidia` | Reject vague links; require type/strength/evidence/layer. |
| `context-keeper` | Maintains `SCRATCH.md` / `CURRENT_FOCUS.md` (via approval). |
| `token-guard` | Justify any broad read; propose cheaper plan; cost estimates. |
| `module-mapper` | Maintains compact `MODULE_MAP.md` (via diff + approval). |
| `wiki-brain-bridge` | Documents Graphify policy. **Does NOT install**. Sandbox-only eval procedure. |

### `.claude/agents/` (6 subagents)

| Agent | Purpose |
|---|---|
| `explorer` | Read-only discovery. Returns paths + 1-line findings. Isolated context. |
| `proof-checker` | `lake build` Lean diagnosis, read-only, with `sorry` inventory. |
| `tla-validator` | TLC + drift check between `proofs/tla/` and `formal/tla/`. |
| `sigma-checker` | Sigma pytest diagnosis, single test file, layer impact check. |
| `context-keeper` | Proposes deltas for `SCRATCH.md` / `CURRENT_FOCUS.md`. Never writes. |
| `risk-reviewer` | Patch reviewer. APPROVE / BLOCK / NEEDS_USER_APPROVAL. |

### `.claude/commands/` (10 slash commands)

| Command | Purpose |
|---|---|
| `/inspect` | Read-only targeted inspection. |
| `/focus` | Show current state from `SCRATCH.md` + `CURRENT_FOCUS.md`. |
| `/update-focus` | Propose + apply (after approval) deltas to memory files. |
| `/proofcheck` | Read-only proof / Merkle / seal / RFC3161 diagnosis. |
| `/sigmacheck` | Read-only Sigma / QA diagnosis. |
| `/route` | Classify request → layer + mode. |
| `/tokencheck` | Justify broad read; propose cheaper plan. |
| `/protected` | List protected globs + rules. |
| `/freeze-check <path>` | YES / NO / ONLY_WITH_APPROVAL on a specific path. |
| `/recap` | Session digest for handoff. |

### `.claude/memory/` (3 files)

| File | Purpose |
|---|---|
| `SCRATCH.md` | Per-session scratch. **Template only** — fill in at runtime. |
| `RISKS.md` | Compiled from the inspection report. 9 risks with treatment. |
| `P1_FREEZE.md` | Frozen folders / tag / commit. Entries with uncertainty marked `TO_VERIFY`. |

### `.claude/hooks/` (3 scripts + EXAMPLES)

| File | Purpose | Wired? |
|---|---|---|
| `session-start.sh` | Print branch / status / reminders. Read-only. | NO (opt-in via EXAMPLES) |
| `pre-edit-protected-warn.sh` | Warn (do NOT block) when target matches protected glob. | NO |
| `pre-compact-snapshot.sh` | Snapshot `SCRATCH.md` / `CURRENT_FOCUS.md` before `/compact`. | NO |
| `EXAMPLES.md` | How to wire any of the above into `settings.local.json`. | — |

---

## 3. What is safe to copy as-is

These files are **safe** to copy directly into the real repo without modification:

- `CLAUDE.md`
- `.claude/context/OBSIDIA_IDENTITY.md`
- `.claude/context/MODULE_MAP.md`
- `.claude/context/PROTECTED_SCOPE.md`
- `.claude/context/TOKEN_POLICY.md`
- `.claude/context/FRACTAL_INFERENCE.md`
- `.claude/context/AGENTIC_ROUTING.md`
- `.claude/context/WORKFLOW.md`
- `.claude/context/EXTERNAL_TOOLS_POLICY.md`
- All files in `.claude/skills/`
- All files in `.claude/agents/`
- All files in `.claude/commands/`
- `.claude/memory/SCRATCH.md` (template — fill in once, do not commit)
- `.claude/memory/RISKS.md`
- `.claude/hooks/*.sh`, `.claude/hooks/EXAMPLES.md`
- `MANIFEST.md` (optional — useful for team onboarding)

## 4. What MUST be reviewed before copying

| File | Why |
|---|---|
| `.claude/settings.json` | Review the `allow` and `deny` lists against your shell habits and actual workflow. Some users prefer a stricter `allow` list. |
| `.claude/context/CURRENT_FOCUS.md` | Includes a snapshot of the branch state at generation time. **Re-verify the branch name and commit ahead-count match your local repo right now.** |
| `.claude/memory/P1_FREEZE.md` | Several entries are flagged `TO_VERIFY`. Run the verification commands in section 6 below before relying on this file. |
| `.claude/skills/wiki-brain-bridge/SKILL.md` | Confirm the exclusion list matches your actual protected paths if your repo has additional sensitive folders. |

## 5. Install commands (PowerShell, Windows)

> Run from the parent folder of `obsidia-x108-proofs` (i.e. the folder that contains `obsidia-x108-proofs/` and where Claude wrote `claude-config/`).

```powershell
# 1. Set source and target
$src  = ".\claude-config"
$dst  = ".\obsidia-x108-proofs"

# 2. Sanity: target is a real git repo
if (-not (Test-Path "$dst\.git")) {
    throw "Target $dst is not a git repo."
}

# 3. Show what would be added (DRY RUN)
$srcRoot = Resolve-Path $src
Get-ChildItem -Path $srcRoot -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($srcRoot.Path.Length + 1)
    "[ADD] $dst\$rel"
}

# 4. If happy with the dry-run, copy:
Copy-Item -Path "$src\CLAUDE.md"   -Destination "$dst\CLAUDE.md"   -Force
Copy-Item -Path "$src\MANIFEST.md" -Destination "$dst\MANIFEST.md" -Force
Copy-Item -Path "$src\.claude"     -Destination "$dst\.claude"     -Recurse -Force

# 5. Make sure hook scripts are executable on Linux/WSL (no-op on pure Windows)
# In WSL or Git Bash:
#   chmod +x obsidia-x108-proofs/.claude/hooks/*.sh

# 6. Stage and review (DO NOT auto-commit)
Push-Location $dst
git status --short
git diff --stat
Pop-Location
```

> **Do NOT** run `git commit` or `git push` from the install script. Review first, then commit manually with a clear message such as `agentic: add Claude Code project-local guidance layer (no source files touched)`.

## 6. Verification commands (run AFTER install, before commit)

```powershell
Push-Location .\obsidia-x108-proofs

# A. Confirm only Claude config files were added
git status --short
git diff --stat

# B. Confirm NO protected file was touched
git diff --name-only HEAD |
  Select-String -Pattern '(merkle|seal|rfc3161|sealed\.cjs|V18_|stable\.py|P1_FREEZE|PUBLIC_STATUS|broken-ragnarok)'
# Expected: (empty)

# C. settings.json is valid JSON
Get-Content .\.claude\settings.json | ConvertFrom-Json | Out-Null; "settings.json OK"

# D. settings.json has NO active hooks
$cfg = Get-Content .\.claude\settings.json | ConvertFrom-Json
if ($cfg.hooks.SessionStart -or $cfg.hooks.PreToolUse -or $cfg.hooks.PostToolUse -or $cfg.hooks.PreCompact -or $cfg.hooks.UserPromptSubmit -or $cfg.hooks.Stop) {
    Write-Warning "settings.json HAS active hooks — review before commit."
} else {
    "settings.json hooks: NONE active (expected)."
}

# E. Verify P1 freeze tag if relevant
git tag -l 'p1-freeze*'
git rev-parse p1-freeze-2026-04-22 2>$null

# F. Confirm Claude Code finds the new structure
# (open Claude Code in the repo and run /focus — it should print branch + reminders)

Pop-Location
```

## 7. What is intentionally left disabled

- All **hooks** in `settings.json` are **inactive**. Hook scripts exist under `.claude/hooks/` but are not referenced. To opt-in, copy a block from `.claude/hooks/EXAMPLES.md` into `.claude/settings.local.json`.
- No `mcpServers` block. Add only via explicit `EXTERNAL_TOOLS_POLICY` review.
- No `npm install` / `pip install` / `winget install` is allowed by `settings.json`. Re-enable per-task only.
- No `Edit` / `Write` permission on protected globs.

## 8. Risks of installing this package

| Risk | Severity | Mitigation |
|---|---|---|
| `CURRENT_FOCUS.md` snapshot becomes stale immediately | LOW | Run `/update-focus` at first session. |
| Subagent format may differ across Claude Code versions | LOW | Frontmatter follows current docs (`name`, `description`, `tools`, `model`). If your version differs, agents simply won't activate — they don't break anything. |
| User opts to wire hooks aggressively | MEDIUM | `EXAMPLES.md` recommends only read-only / warn-only / snapshot. Anything more requires explicit user action. |
| Skill descriptions trigger on unrelated tasks | LOW | Each description is scoped to specific Obsidia/X-108 keywords. Generic web-dev tasks should not match. |
| `wiki-brain-bridge/SKILL.md` is misread as install instruction | LOW | Skill content is explicit: "DO NOT auto-install". |

## 9. Post-install first session checklist

In the real repo, after copying:

1. `/focus` — confirms `CURRENT_FOCUS.md` is read.
2. `/protected` — confirms `PROTECTED_SCOPE.md` is reachable.
3. `/route "investigate the V18_3_1 root hash mismatch"` — confirms routing returns `Layer: KERNEL`, `Mode: PROOF_SENTINEL`.
4. `/freeze-check proofs/V18_3_1/manifest.json` — confirms `Modification allowed? ONLY_WITH_APPROVAL`.
5. `/freeze-check sigma/tests/test_pipeline.py` — confirms `Modification allowed? YES`.
6. `/tokencheck "read all docs"` — confirms a cheaper targeted plan is proposed.
7. `/update-focus first-claude-config-session` — confirms `context-keeper` agent activates.

If any of these returns the wrong layer/verdict, **do not commit the package**. Re-inspect the relevant file and fix before merging.

---

## 10. Confirmation of scope

- **Generated in**: `/mnt/outputs/claude-config/`
- **Real repo touched**: NONE
- **Auto-installed packages**: NONE
- **External services contacted**: NONE
- **Personal token URLs fetched**: NONE
- **Protected files modified**: NONE
- **Active hooks**: NONE in `settings.json` (scripts available, opt-in only)

This package is **inert** until you copy it into the real repo and review. No side effects.
