# OBSIDIA — Infrastructure Brief (Non-technical)

## One sentence
Obsidia is an infrastructure layer that **governs actions before they execute**, producing auditable decisions.

## Why it matters
Most systems validate after execution. Regulated environments require proof, traceability, and refusal capability **before** irreversible effects.

## How it works (high level)
A request enters a secured gateway, is authenticated and integrity-checked, then flows through a deterministic kernel.
The kernel outputs one of:
- **BLOCK**: forbidden trajectory
- **HOLD**: frozen until resolved (human gate or clarification)
- **ACT**: authorized execution path

## Audit & proof
Every path generates:
- append-only audit log
- hash chain for tamper detection
- optional WORM snapshots
- daily attestations (optionally signed)

## What you can do with it
- Govern agentic systems
- Control irreversible operations (finance, infrastructure, industry)
- Build compliance-by-design pipelines