# Obsidia X-108 Proofs — AGENTS.md (entrypoint)

> **This file is an index, not a manual.** The real doctrine lives in `.Codex/context/`.
> Read this once per session, then load only the context file matching your active layer.

---

## Identity

`obsidia-x108-proofs` is the public proof / audit perimeter of the Obsidia X-108 deterministic governance kernel. It is **not** a generic software project.

Detail → `.Codex/context/OBSIDIA_IDENTITY.md`

---

## Mandatory response header

Every response touching the repo starts with:

```
Mode:  READ_ONLY | PROPOSE | APPLY
Layer: KERNEL | SIGMA | CONNECTORS | DOCS | TOOLING | AGENTIC
Scope: <one line>
Risk:  NONE | LOW | MEDIUM | HIGH
Files touched: <list, or "none">
```

Detail → `.Codex/context/WORKFLOW.md`

---

## Default mode

**READ-ONLY INSPECTION.** Always. Modifications require: classify → inspect → diagnose → propose → wait for approval → patch → verify → report → show git status.

Detail → `.Codex/context/WORKFLOW.md`

---

## Layer routing

Every task picks **one** primary layer before action. Never mix layers without explicit user request.

Detail → `.Codex/context/AGENTIC_ROUTING.md`

---

## Protected files

Crypto-anchored, sealed, frozen, vendored, and intentionally-broken files MUST NOT be edited / reformatted / renamed / regenerated without explicit user approval and a verification plan.

Full list and rules → `.Codex/context/PROTECTED_SCOPE.md`

---

## Token discipline

Never read the whole repo. Default loading order: this file → `CURRENT_FOCUS.md` → `MODULE_MAP.md` → only the context file matching the layer → targeted Glob/Grep → smallest relevant files.

Detail → `.Codex/context/TOKEN_POLICY.md` and `.Codex/context/FRACTAL_INFERENCE.md`

---

## Hard prohibitions

- No `autoskills`, no `/ultrareview`.
- No `npm install`, `pip install`, `winget install`, `lake build`, `pytest` without explicit user request.
- No push, no force-push, no auto-commit.
- No reading or fetching of personal / token-bearing URLs.
- No editing of protected files (see PROTECTED_SCOPE.md).
- No "everything connects to everything" graph work — see `.Codex/context/FRACTAL_INFERENCE.md`.
- Do NOT create new Obsidia agents unless the existing registry (`OBSIDIA_TOUS_LES_AGENTS.docx`) does not cover the need. Use `agents/proposals/<NAME>.md` (root-level, not inside `.Codex/`) for user-approved proposals first. See `.Codex/context/AGENTIC_ROUTING.md`.
- Every new Codex skill MUST declare its Obsidia mapping in `SKILL.md` frontmatter (`obsidia_mapping_type`, `obsidia_agents`, `obsidia_reduction`). Skills without a mapping are rejected, or carry `obsidia_mapping_type: to_verify` pending registry extraction. See `.Codex/context/AGENTIC_ROUTING.md` §7.

Detail → `.Codex/context/EXTERNAL_TOOLS_POLICY.md`

---

## Live state

- Live working state → `.Codex/memory/SCRATCH.md` (read every session, update at end)
- Known risks → `.Codex/memory/RISKS.md`
- Freeze inventory → `.Codex/memory/P1_FREEZE.md` (some entries marked `TO_VERIFY`)

---

## Skills available locally

Skills live in `.Codex/skills/<name>/SKILL.md`. They activate when their description matches the user request.

| Skill | Use for | Maps to (Obsidia) |
|---|---|---|
| `read-only-inspector` | Inspect without modifying. Always step 1. | `OBSIDIA_ATLAS_INGESTOR` (reduced) |
| `terminal-builder` | Generate safe PowerShell / Bash commands. | `TERMINAL_BUILDER` (direct) |
| `proof-sentinel` | Diagnose Lean / TLA / Merkle / seal / RFC3161 issues. | `PROOF_SENTINEL` (direct) |
| `freeze-guardian` | Block edits on V18, Merkle, seal, RFC3161, stable files. | `CANON_GUARDIAN` (reduced) |
| `sigma-surgeon` | Surgical work on `sigma/` only. | `CO_PILOTE_CODE` + `CI_REPO_SURGEON` (composite) |
| `agent-router-obsidia` | Route a request to the correct mode/layer. | _to_verify_ |
| `graph-calibrator-obsidia` | Prevent "everything connects to everything". | `GRAPH_BUILDER` + `CALIBRATION_PROCEDURALE` (composite) |
| `context-keeper` | Maintain `CURRENT_FOCUS.md` and `SCRATCH.md`. | _local behavior_ |
| `token-guard` | Justify any broad read; propose cheaper plan. | `ANTI_DISPERSION` (composite); CONTEXT_KEEPER is local behavior |
| `module-mapper` | Maintain compact `MODULE_MAP.md`. | _to_verify_ (likely Atlas/Cartographe family) |
| `wiki-brain-bridge` | Bridge to Graphify/wiki-brain (NOT auto-install). | _policy file — not an agent_ |

Mapping schema and reasoning → `.Codex/context/AGENTIC_ROUTING.md` §4 and §7. The Obsidia source-of-truth draft is `OBSIDIA_TOUS_LES_AGENTS.docx` (52 agents, 9 families).

---

## Subagents available

Subagents (`.Codex/agents/`) execute in their **own context window** and return summaries. Use them for any discovery / verification step.

| Agent | Use for |
|---|---|
| `explorer` | Read-only discovery, returns file paths + 1-line findings |
| `proof-checker` | `lake build` Lean diagnosis, read-only |
| `tla-validator` | TLC + drift check between `proofs/tla/` and `formal/tla/` |
| `sigma-checker` | Sigma QA / pipeline diagnosis, no kernel edits |
| `context-keeper` | Updates `CURRENT_FOCUS.md` after user approval |
| `risk-reviewer` | Reviews any proposed patch before apply |

---

## Slash commands

Detail and full command files in `.Codex/commands/`.

```
/inspect         Read-only targeted inspection
/focus           Show CURRENT_FOCUS.md
/update-focus    Update CURRENT_FOCUS.md (after approval)
/proofcheck      Read-only proof issue investigation
/sigmacheck      Read-only Sigma layer diagnosis
/route           Classify task → layer + mode
/tokencheck      Justify a broad read, propose cheaper plan
/protected       List protected files & rules
/freeze-check    Check whether a path is in protected scope
/recap           Digest from SCRATCH for handoff
```

---

## Where to look next

- New session → `.Codex/memory/SCRATCH.md`, then `.Codex/context/CURRENT_FOCUS.md`
- About to edit anything → `.Codex/context/PROTECTED_SCOPE.md`
- Asked to inspect → `.Codex/skills/read-only-inspector/SKILL.md`
- Asked for a command → `.Codex/skills/terminal-builder/SKILL.md`
- Touching `proofs/`, `formal/tla/`, `merkle*`, `seal*`, `rfc3161*` → `.Codex/skills/proof-sentinel/SKILL.md`
- Touching `sigma/` → `.Codex/skills/sigma-surgeon/SKILL.md`
- Conceptual / mapping work → `.Codex/skills/graph-calibrator-obsidia/SKILL.md`
