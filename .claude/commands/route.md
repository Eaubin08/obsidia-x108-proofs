---
description: Classify a request into one primary layer and one active mode before any other action.
allowed-tools: Read, Glob, Grep
---

Activate the `agent-router-obsidia` skill.

Request to classify: $ARGUMENTS

Output (per `.claude/skills/agent-router-obsidia/SKILL.md`):

```
Mode: PROPOSE
Layer: AGENTIC
Files touched: none

Detected intent:    <one sentence>
Primary layer:      <KERNEL | SIGMA | CONNECTORS | DOCS | TOOLING | AGENTIC>
Active mode:        <READ_ONLY_INSPECTOR | TERMINAL_BUILDER | PROOF_SENTINEL | FREEZE_GUARDIAN | SIGMA_SURGEON | GRAPH_CALIBRATOR | CONTEXT_KEEPER | MODULE_MAPPER | TOKEN_GUARD | AGENT_ROUTER>
Excluded modes:     <list with one-line reasons>
Reason:             <one paragraph>
Next action:        <concrete next step — usually a slash command or skill activation>
```

Rules:
- One layer, one mode. No multi-mode unless the user explicitly asked.
- Default to `READ_ONLY_INSPECTOR` when unsure.
- Never invoke `Edit` / `Write` during routing.
- If the request mixes layers (e.g. "fix the test and update the docs"), pick the most restrictive layer first and inform the user that we'll handle the other layer in a separate step.
