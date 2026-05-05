---
name: graph-calibrator-obsidia
description: Use this skill any time the user is doing conceptual / mapping / knowledge-graph work — drawing relationships between ideas, modules, agents, or proofs. Triggers include "map", "graph", "relate", "connect", "link", "wiki", "knowledge", "concept map", "mind map", "how does X relate to Y". Output rejects vague links and forces every connection to carry type / strength / direction / evidence / layer.
obsidia_mapping_type: composite
obsidia_agents:
  - GRAPH_BUILDER
  - CALIBRATION_PROCEDURALE
obsidia_reduction: graph calibration only, prevents everything-connects-to-everything
---

# Graph Calibrator (Obsidia)

## Purpose

Prevent "everything connects to everything" in conceptual mapping. Every link must be **typed, scored, evidenced, and layer-tagged** — or it gets rejected.

## When to use

- Building a knowledge graph or concept map
- Linking Obsidia concepts (kernel, sigma, surfaces, agents)
- Drafting wiki notes that cross-reference
- Any "how does X relate to Y?" question with multiple plausible answers

## When NOT to use

- The user wants a code edit — use `sigma-surgeon` or `read-only-inspector`.
- The user wants a command — use `terminal-builder`.

## Operating rules

### Every link has 7 attributes

| Attribute | Allowed values |
|---|---|
| `source` | A specific file / symbol / concept |
| `target` | A specific file / symbol / concept |
| `type` | `DIRECT` `INDIRECT` `HYPOTHETICAL` `CONFLICT` `TEMPORAL` `HIERARCHICAL` `ANALOGICAL` |
| `strength` | `STRONG` `MEDIUM` `WEAK` `UNCERTAIN` |
| `direction` | `→` (one-way) or `↔` (bidirectional) |
| `evidence` | `file:line` reference, doc citation, or "none" |
| `layer` | `KERNEL` `SIGMA` `SURFACES` `DOCS` `TOOLING` `AGENTIC` (or `cross` if cross-layer) |

### Hard rules

- Maximum **5 primary structural links** unless exhaustive mapping is explicitly requested.
- If `evidence = none`, the link is `HYPOTHETICAL` with `UNCERTAIN` strength — or rejected.
- Distinguish **analogy** from **causality**.
- Distinguish layers: `memory`, `canon`, `proof`, `kernel`, `Sigma`, `terrain`, `vision`.
- Cross-layer links require `STRONG` evidence.
- Reject vague phrasings like "X is related to Y", "X has to do with Y", "X is connected to Y".

## Required output format

```
Mode: PROPOSE
Layer: AGENTIC (mapping)
Files touched: none

Nodes:
- <node 1>: <one line>
- <node 2>: <one line>

Proposed links:
1. <source> → <target>  type=<TYPE>  strength=<STRENGTH>  direction=<→|↔>
   evidence: <file:line | doc | "none">
   layer: <KERNEL|SIGMA|SURFACES|DOCS|TOOLING|AGENTIC|cross>

Rejected links:
- <source> ?? <target>: <why rejected — usually "no evidence" or "vague">

Top 5 structural links (priority):
1. ...
2. ...
3. ...
4. ...
5. ...

Uncertain links (kept but flagged):
- <source> ⇢ <target>  HYPOTHETICAL  UNCERTAIN — <reason>

Layer contamination warnings:
- <e.g. "KERNEL → SURFACES direct link missing intermediate Sigma — likely analogy not causality">

Canon risk:
- <e.g. "this link would imply changing a frozen artifact — escalate to freeze-guardian">
```

## Forbidden actions

- Producing `>5` primary links without explicit user request for exhaustive mapping.
- Creating links without evidence and without flagging them as `HYPOTHETICAL`.
- Mixing analogies and causalities in the same list.
- Linking conceptual nodes directly to frozen / sealed / anchored files without escalation.
- Implicit cross-layer links (must be marked `cross`).

## Verification checklist

- [ ] Every link has all 7 attributes.
- [ ] Top 5 list is explicit and ranked.
- [ ] Rejected links list is non-empty (if it is, justify why nothing was rejected).
- [ ] No file was edited.
- [ ] No protected file appears as a `target` of a structural change.

## Example

```
User: "How does X-108 relate to Sigma?"

Nodes:
- X-108 (KERNEL): ex-ante governance kernel; decides BLOCK > HOLD > ALLOW
- Sigma (SIGMA): orchestration layer; aggregates inputs, applies contracts, emits decisions

Proposed links:
1. X-108 → Sigma  type=HIERARCHICAL  strength=STRONG  direction=→
   evidence: docs/SIGMA.md (cited authoritative doc)
   layer: cross
2. Sigma → X-108  type=DIRECT  strength=STRONG  direction=→
   evidence: sigma/aggregation_stable.py imports x108_core (citation needed if not verified)
   layer: cross

Rejected links:
- Sigma ?? proofs/V18_3_1: vague — proofs are referenced, not "linked"; the relation is verification, not dependency.

Top 5: 1, 2 (only two structural links justified at this depth)
Uncertain: none
Layer contamination warnings: KERNEL → SIGMA is allowed (one-way authority); SIGMA → KERNEL only via verification, never modification.
Canon risk: none for this question.
```
