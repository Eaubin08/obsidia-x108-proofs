# Agentic Routing

> **Reference**: `OBSIDIA_TOUS_LES_AGENTS.docx` is the **source-of-truth draft for the Obsidia agent registry** (current reference registry for the Obsidia agentic layer).
> It is a routing reference — **not** a kernel/canon proof artifact.
> Full extraction is deferred. This file is the **operational projection** of that registry into the local Claude Code layer.

---

## 1. The Obsidia agent registry (current reference)

- **Status**: source-of-truth **draft** for the Obsidia agentic layer.
- **Location**: `OBSIDIA_TOUS_LES_AGENTS.docx` (uploaded by user; not committed in repo).
- **Total**: 52 agents in 9 families.
- **Surfaces**:
  - **Vertex AI** = accelerator (non-sovereign agent work)
  - **Local** = memory sovereignty (proof, kernel, secrets, client data)

### Known family set (from the dashboard)

```
1. À créer en premier / Top 5 founders
2. Code / Repo / CI
3. Documentation / Théorie / Freeze
4. Données / Logs / Audit
5. Sécurité / Pare-feu
6. Terrain / Produit / Communication
7. Frise / Arbres / Monde humain
8. Atlas Obsidia
9. Pour Étienne directement
```

Per-family agent rosters, system prompts, and deployment notes are in the docx and will be extracted later.

## 2. Top 5 founding agents (must exist first)

| # | Agent | Role |
|---|---|---|
| 1 | `OBSIDIA_ATLAS_INGESTOR` | Analyste-cartographe profond — transforms raw material into structured memory cards. |
| 2 | `CANON_GUARDIAN` | Protects canon status and detects contradictions / collisions. |
| 3 | `GRAPH_BUILDER` | Builds node / link graph with relation type and force. |
| 4 | `TERMINAL_BUILDER` | Produces PowerShell / Bash command blocks with expected execution evidence. |
| 5 | `PROOF_SENTINEL` | Monitors ProofKit / Lean / TLA / root / seal — distinguishes real proof rupture from CI / environment issue. |

## 3. Operational doctrine (Claude Code as local builder/operator)

- Claude Code is **NOT** a replacement for the Obsidia agent registry.
- Claude Code is the **local builder / operator layer** for these agents inside `obsidia-x108-proofs`.
- Claude Code does **NOT** pretend to run all 52 agents.
- Claude Code selects **exactly one active mode per task**.
- Claude Code's local skills are a **reduced operational subset** of the Obsidia registry.
- Full registry extraction (prompts, families, deployment notes) will be done later from `OBSIDIA_TOUS_LES_AGENTS.docx`. **Not done automatically.**

## 4. Skill ↔ Obsidia agent mapping

Every Claude Code local skill MUST declare its Obsidia mapping in its `SKILL.md` frontmatter (schema below).

| Local Claude skill | Mapping type | Obsidia agent(s) | Reduction / scope |
|---|---|---|---|
| `read-only-inspector` | reduced | `OBSIDIA_ATLAS_INGESTOR` | Repo discovery only — no full memory-card extraction, no canon judgment |
| `terminal-builder` | direct | `TERMINAL_BUILDER` | Direct mapping (PowerShell-first) |
| `proof-sentinel` | direct | `PROOF_SENTINEL` | Direct mapping (Lean / TLA / Merkle / seal / RFC3161) |
| `freeze-guardian` | reduced | `CANON_GUARDIAN` | Protected-file / canon-safety checks only — no full canon ruling |
| `sigma-surgeon` | composite | `CO_PILOTE_CODE` + `CI_REPO_SURGEON` | Sigma / periphery only — no kernel / proof / seal edits |
| `graph-calibrator-obsidia` | composite | `GRAPH_BUILDER` + `CALIBRATION_PROCEDURALE` | Graph calibration only — prevents "everything connects to everything" |
| `token-guard` | composite | `ANTI_DISPERSION` | Token discipline + anti-broad-read; CONTEXT_KEEPER is local behavior, not a registry agent |
| `context-keeper` | behavior | _(none)_ | Local Claude Code behavior for `SCRATCH.md` / `CURRENT_FOCUS.md` maintenance |
| `agent-router-obsidia` | to_verify | _(pending extraction)_ | Local routing layer |
| `module-mapper` | to_verify | _(pending extraction — likely Atlas / Cartographe family)_ | Maintains `MODULE_MAP.md` |
| `wiki-brain-bridge` | policy | _(none)_ | Policy bridge for Graphify / wiki-brain — sandbox-only, not an Obsidia agent |

**`CONTEXT_KEEPER`** is **confirmed absent** from the 52-agent registry. It is kept as a **local Claude Code behavior only** — `TO_VERIFY` if a future registry expansion adds it.

## 5. Subagent (Task tool) ↔ Obsidia agent mapping

| Local subagent | Mapping type | Obsidia agent(s) | Notes |
|---|---|---|---|
| `explorer` | reduced | `OBSIDIA_ATLAS_INGESTOR` | Discovery only (lighter form) |
| `proof-checker` | reduced | `PROOF_SENTINEL` (Lean half) | `lake build` runner |
| `tla-validator` | reduced | `PROOF_SENTINEL` (TLA half) | TLC + drift check between `proofs/tla/` and `formal/tla/` |
| `sigma-checker` | composite | `CO_PILOTE_CODE` + `CI_REPO_SURGEON` | Pytest single-file runner |
| `context-keeper` | behavior | _(none)_ | Local memory-file delta proposer |
| `risk-reviewer` | to_verify | _(pending extraction)_ | Patch reviewer; possibly close to `ADVERSARIAL_RED_TEAM` (lite) |

## 6. Hard rules

1. **Do NOT create new Obsidia agents** unless the existing registry does not cover the need.
   When that happens: write a proposal in `agents/proposals/<NAME>.md` (root-level, not inside `.claude/`) for **user review before adding** to any registry file.

2. **Every new Claude Code skill MUST declare its Obsidia mapping** in its `SKILL.md` frontmatter using the schema in §7. Skills without a mapping are rejected (or carry `obsidia_mapping_type: to_verify` pending registry extraction).

3. Claude Code activates **one mode per task**. Multi-mode requires explicit user request.

4. The full registry extraction is **NOT** done by Claude Code automatically. It happens only when the user explicitly approves an extraction pass and points Claude at `OBSIDIA_TOUS_LES_AGENTS.docx`.

5. `.claude/agents/` is reserved for **Claude Code subagents** (Task tool delegations). It is **not** the Obsidia registry. The Obsidia registry lives outside `.claude/`.

## 7. Frontmatter schema for Claude Code skills

Every `SKILL.md` carries:

```yaml
---
name: <skill-name>
description: <when to use>
obsidia_mapping_type: direct | reduced | composite | behavior | policy | to_verify
obsidia_agents:
  - AGENT_NAME              # zero or more — empty list for behavior / policy / to_verify
obsidia_reduction: <one-line explanation of the reduction or scope>
---
```

| `obsidia_mapping_type` | When |
|---|---|
| `direct` | The skill is the local 1:1 implementation of an Obsidia agent |
| `reduced` | The skill is a narrowed scope of one Obsidia agent |
| `composite` | The skill combines two or more Obsidia agents |
| `behavior` | Local Claude Code behavior — not an Obsidia agent |
| `policy` | Policy / bridge file — not an Obsidia agent |
| `to_verify` | Mapping pending full registry extraction |

## 8. Future target files (DO NOT CREATE without approval)

These will be created **only after full registry extraction is approved**, and they live at the **repo root under `agents/`** — NOT inside `.claude/agents/`:

```
agents/registry.json                Machine-readable index of all 52 agents (extracted from docx)
agents/registry.md                  Human-readable index, mirrors registry.json
agents/prompts/<AGENT_NAME>.md      One file per agent — system prompt + role + outputs
agents/bootstrap/top5_bootstrap.md  How to instantiate the top 5 founders first
agents/routing/routing_rules.md     Detailed routing rules per family
agents/proposals/<NAME>.md          New-agent proposals (user-approved before registry update)
```

**None of these is created in the current package.** The `wiki-brain-bridge` policy still applies: never index the docx into a cloud graph.

## 9. Local Claude Code modes (operational subset)

For convenience, the modes Claude Code can activate locally:

| Mode | Implemented as | Maps to |
|---|---|---|
| `READ_ONLY_INSPECTOR` | `read-only-inspector` skill | `OBSIDIA_ATLAS_INGESTOR` (reduced) |
| `TERMINAL_BUILDER` | `terminal-builder` skill | `TERMINAL_BUILDER` (direct) |
| `PROOF_SENTINEL` | `proof-sentinel` skill + `proof-checker` / `tla-validator` agents | `PROOF_SENTINEL` (direct) |
| `FREEZE_GUARDIAN` | `freeze-guardian` skill | `CANON_GUARDIAN` (reduced) |
| `SIGMA_SURGEON` | `sigma-surgeon` skill + `sigma-checker` agent | `CO_PILOTE_CODE` + `CI_REPO_SURGEON` (composite) |
| `GRAPH_CALIBRATOR` | `graph-calibrator-obsidia` skill | `GRAPH_BUILDER` + `CALIBRATION_PROCEDURALE` (composite) |
| `TOKEN_GUARD` | `token-guard` skill | `ANTI_DISPERSION` (composite); CONTEXT_KEEPER is local behavior |
| `CONTEXT_KEEPER` (local) | `context-keeper` skill + agent | local behavior — TO_VERIFY if future registry expansion |
| `MODULE_MAPPER` (local) | `module-mapper` skill | TO_VERIFY pending extraction |
| `AGENT_ROUTER` (local) | `agent-router-obsidia` skill | TO_VERIFY pending extraction |

## 10. Routing protocol

For every user request:

1. The `agent-router-obsidia` skill (or Claude internally) classifies:
   - Detected intent
   - Primary layer (KERNEL / SIGMA / CONNECTORS / DOCS / TOOLING / AGENTIC)
   - Active mode (one of §9)
   - Excluded modes
   - Reason
   - Next action

2. The chosen mode handles the task with its own output contract.

3. If the task spans multiple modes, the router picks the **most restrictive** one first (usually `READ_ONLY_INSPECTOR`).

## 11. Hard prohibitions (recap)

- Select **one** primary mode per task.
- Do not pretend to run all 52 agents.
- Do not activate multiple modes unless the task genuinely requires it.
- Default to `READ_ONLY_INSPECTOR` when unsure.
- Never route conceptual work into code edits.
- Never route proof work into Sigma edits.
- Never route memory / canon work into kernel changes.
- Never extract the full registry without explicit user approval.
