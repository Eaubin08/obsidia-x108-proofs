# Fractal Inference

> Keep a stable global map. Zoom only into the active layer. Never flatten the project.

## The pattern

```
[ stable global map ]   ← MODULE_MAP.md, OBSIDIA_IDENTITY.md (read once, kept in mind)
        ↓
[ active layer zoom ]   ← only the context file matching the current task
        ↓
[ minimal file read ]   ← only the smallest relevant files, with offset/limit
        ↓
[ summarize + act ]     ← summary in SCRATCH.md, no file dumping
```

The agent stays at the top level (the map) by default. It zooms only when the task requires evidence. After the task, it returns to the top.

## Layer zoom rules

| Task | Zoom into |
|---|---|
| Lean / TLA / ProofKit / Merkle / seal / RFC3161 | `PROTECTED_SCOPE.md` + `proof-sentinel` skill |
| Sigma / aggregation / contracts / monitor / QA | `sigma/` and matching tests only |
| Bank / trading / aviation | `connectors/<domain>/` + matching `MonProjet/*.json` |
| Docs / audit / reports | `docs/` and `audit/` only |
| Agentic config | `.claude/` and `AGENTIC_ROUTING.md` only |
| Tooling / PowerShell / CI | root `*.ps1` + `.github/workflows/` |

**Cross-layer reads require explicit user approval.**

## No "everything is connected"

Conceptual / mapping work (graphs, wiki notes, knowledge bases) MUST follow these rules:

### Every link has 7 attributes

| Attribute | Allowed values |
|---|---|
| `source` | A specific file/symbol/concept |
| `target` | A specific file/symbol/concept |
| `type` | `DIRECT` `INDIRECT` `HYPOTHETICAL` `CONFLICT` `TEMPORAL` `HIERARCHICAL` `ANALOGICAL` |
| `strength` | `STRONG` `MEDIUM` `WEAK` `UNCERTAIN` |
| `direction` | `→` (one-way) or `↔` (bidirectional) |
| `evidence` | `file:line` reference or "none" — if none, link is rejected |
| `layer` | `KERNEL` `SIGMA` `SURFACES` `DOCS` `TOOLING` `AGENTIC` |

### Hard rules

- Maximum **5 primary structural links** unless exhaustive mapping is explicitly requested.
- Distinguish **analogy** from **causality**.
- Distinguish **memory**, **canon**, **proof**, **kernel**, **Sigma**, **terrain**, **vision**.
- Reject vague "X is related to Y".
- Mark uncertain links as `HYPOTHETICAL` with `UNCERTAIN` strength.
- Cross-layer links must have `STRONG` evidence.

### Bad vs good

```
BAD:  "X108 is connected to Sigma"
GOOD: "X108 (KERNEL) → Sigma.Aggregator (SIGMA), type=DIRECT, strength=STRONG,
       direction=→, evidence=sigma/aggregation_stable.py:42 imports x108_core,
       layer=cross"
```

## Why this matters

Without graph calibration, every conceptual session balloons into a "everything explains everything" map. That's:

- Token-expensive (reading wide and shallow)
- Cognitively useless (no priority, no causality)
- Risk for proof work (analogies leaking into formal layers)

The `graph-calibrator-obsidia` skill enforces these rules.
