---
name: agent-router-obsidia
description: Use this skill at the START of any task to classify the user's request into exactly one primary layer and one active mode before any other action. Triggers automatically when a request is ambiguous or could span multiple layers. Output is a routing decision: detected intent, primary layer, active mode, excluded modes, reason, and next action.
obsidia_mapping_type: to_verify
obsidia_agents: []
obsidia_reduction: local routing layer pending full registry extraction
---

# Agent Router (Obsidia)

## Purpose

Detect intent. Pick **one** primary layer. Pick **one** active mode. Reject multi-mode activation unless genuinely required. This is the gatekeeper before any other skill or agent activates.

## When to use

- The user's request is ambiguous ("can you look at this?", "what's wrong here?").
- The request could span multiple layers (e.g. "fix the failing test" — Sigma test or proof verifier?).
- Before invoking any other skill / agent / `Edit` call.
- When unsure which mode applies.

## When NOT to use

- The user's request is unambiguous and the active mode is obvious (e.g. "give me the PowerShell command to run all proofs" → directly `terminal-builder`).

## Operating rules

1. Classify into exactly **one** primary layer.
2. Pick exactly **one** active mode.
3. List the modes that were excluded (so the user can override).
4. Justify the choice in one line.
5. Default to `READ_ONLY_INSPECTOR` when unsure.
6. Never activate multiple modes simultaneously without user approval.

## Layers and modes

### Primary layers

| Layer | Triggers |
|---|---|
| `KERNEL` | Lean, TLA+, ProofKit, Merkle, root, seal, RFC3161, V18_*, formal proof, invariant |
| `SIGMA` | sigma/, aggregator, contracts, monitor, QA, cross-platform, BLOCK/HOLD/ALLOW |
| `CONNECTORS` | bank, trading, aviation, MonProjet, scenario payload |
| `DOCS` | docs/, README, audit guide, kernel overview, CI policy |
| `TOOLING` | run_*.ps1, .github/workflows/, package.json, requirements.txt |
| `AGENTIC` | .Codex/, AGENTS.md, skills, agents, memory |

### Active modes

```
READ_ONLY_INSPECTOR    Inspect, no modify
TERMINAL_BUILDER       Generate safe commands
PROOF_SENTINEL         Lean / TLA / Merkle / seal / RFC3161 diagnosis (read-only)
FREEZE_GUARDIAN        Verdict on edit-safety for protected paths
SIGMA_SURGEON          Surgical Sigma edits
GRAPH_CALIBRATOR       Conceptual / mapping work
CONTEXT_KEEPER         Update CURRENT_FOCUS.md / SCRATCH.md
MODULE_MAPPER          Maintain MODULE_MAP.md
TOKEN_GUARD            Justify broad reads, propose cheaper plan
AGENT_ROUTER           This mode (when unsure)
```

## Required output format

```
Mode: PROPOSE
Layer: AGENTIC
Files touched: none

Detected intent:    <one sentence rephrasing the user's request>
Primary layer:      <one of KERNEL | SIGMA | CONNECTORS | DOCS | TOOLING | AGENTIC>
Active mode:        <one of the modes above>
Excluded modes:     <list, with one-line reason for each>
Reason:             <one paragraph>
Next action:        <concrete next step, usually a command or skill activation>
```

## Forbidden actions

- Activating more than one mode without explicit user approval.
- Routing conceptual / mapping work into code edits.
- Routing proof work into Sigma edits.
- Routing memory / canon work into kernel changes.
- Skipping the routing step on ambiguous requests.

## Verification checklist

- [ ] Exactly one layer chosen.
- [ ] Exactly one mode chosen.
- [ ] Excluded modes listed with reasons.
- [ ] Next action is concrete (skill name, command, or "ask user").
- [ ] No `Edit` / `Write` was called during routing.

## Routing examples

```
User: "fix the proof"
→ Layer: KERNEL
→ Mode: PROOF_SENTINEL (read-only diagnosis first)
→ Excluded: SIGMA_SURGEON (different layer), TERMINAL_BUILDER (no command requested yet)
→ Next: invoke proof-sentinel skill, then proof-checker subagent if needed.

User: "the bank test is failing"
→ Layer: SIGMA
→ Mode: SIGMA_SURGEON (after diagnosis)
→ Excluded: PROOF_SENTINEL (test is in sigma/tests/, not in proofs/)
→ Next: read-only-inspector first to localize, then sigma-checker subagent.

User: "tidy up the Lean files"
→ Layer: KERNEL
→ Mode: FREEZE_GUARDIAN (this is a protected scope)
→ Excluded: anything that edits.
→ Next: emit a freeze verdict (NO / ONLY_WITH_APPROVAL).
```
