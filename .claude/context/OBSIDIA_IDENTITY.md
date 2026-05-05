# Obsidia Identity

## What Obsidia is

Obsidia is **not** a chatbot, a SaaS, a generic AI app, or a web project.

Obsidia is a **deterministic governance, proof, audit, and agentic orchestration architecture**.

## Core terms

| Term | Meaning |
|---|---|
| **Obsidia** | The umbrella architecture: governance + proof + audit + agentic orchestration |
| **X-108** | The ex-ante governance kernel — decides whether an action is allowed before it happens |
| **Core semantics** | `BLOCK > HOLD > ALLOW` — priority order that must never be inverted |
| **Kernel / proof layer** | Sovereign, small, auditable, protected. Lean + TLA+ + Merkle + seal + RFC3161 |
| **Sigma** | Orchestration / periphery / QA layer — wraps the kernel without modifying it |
| **Domain surfaces** | bank, trading, aviation, connectors, field POCs |
| **Proof stack** | ProofKit, Lean 4, TLA+, Merkle root + seal, RFC3161 timestamp anchor |
| **Goal** | Auditable, reproducible, structurally aligned decision governance |

## What Obsidia is NOT

- A generic AI chatbot
- A SaaS product with a marketing site
- A monolithic web application
- A research notebook

## Why this matters for Claude

Default web-dev assumptions (auto-format, auto-lint, regenerate, refactor, "fix the broken file", "tidy up the imports") **do not apply** to this repo. A formatting change inside a sealed or anchored file silently invalidates cryptographic proofs.

Treat every file as **load-bearing** unless `MODULE_MAP.md` explicitly says it's a working draft.

## Layer hierarchy (top = most sovereign)

```
KERNEL   ← X-108, Lean, TLA+, Merkle, seal, RFC3161, V18 bundles
SIGMA    ← orchestration, aggregation, contracts, monitors, QA
SURFACES ← bank / trading / aviation / connectors / field POCs
DOCS     ← documentation, audit reports, evidence boards
TOOLING  ← PowerShell runners, CI, scripts
AGENTIC  ← .claude/, agent registry, prompts, skills, memory
```

A change in a higher layer can invalidate everything below; a change in a lower layer must never modify a higher layer.
