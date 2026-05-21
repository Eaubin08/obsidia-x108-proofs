# Agentic Constitutional Civilization Stack — V1

**Classification:** DOCS  
**Layer:** AGENTIC  
**Status:** STABLE  
**Date:** 2026-05-19

---

## Overview

The Agentic Constitutional Civilization Stack describes how a deterministic governance kernel (Obsidia X-108) anchors a layered system of agentic components into a constitutionally coherent whole. Each layer has a defined authority boundary. No layer can exceed its boundary.

---

## Stack Layers (bottom to top)

| Layer | Component | Authority |
|-------|-----------|-----------|
| 0 | Obsidia X-108 Kernel | Sole sovereign — decides |
| 1 | OS3 Proof Layer | Proves kernel decisions |
| 2 | ProofOfGovernance | Qualifies proof outcomes |
| 3 | SovereignTicket | Authorizes controlled passage |
| 4 | Gateway / WorldActionBus | Controls egress, traces intent |
| 5 | Gencoin Ledger | Values after proof — ledger only, never token |
| 6 | Brody Runtime | Responds — never decides |
| 7 | Memory / Graphiti | Contextualizes — never decides |
| 8 | Periphery (all modules) | Signals — never decides |

---

## Constitutional Invariants

1. **X-108 is the sole authority.** No periphery component, no agentic layer, no AI model can override or replace the kernel decision.
2. **Capability is not authority.** A component capable of generating an ACT signal is not authorized to emit one without kernel approval.
3. **Memory contextualizes; it does not govern.** Memory promotion requires human review. Auto-promotion is invariant-violation.
4. **Proof precedes action.** No ACT can be emitted without a qualified proof path through OS3 → PoG → SovereignTicket → Gateway.
5. **Advisory output is not a decision.** Brody, Graphiti, and all periphery layers produce context signals, not decisions.

---

## Layer Communication Rules

- Periphery → Context Packet → X-108 ingress (read-only)
- X-108 → SovereignTicket → Gateway (controlled egress only)
- Gateway → WorldActionBus (audit trace only)
- Gencoin → receives proof reference (no mint, no deploy, no real token)

---

## What This Stack Is Not

- Not a voting system
- Not a consensus mechanism
- Not a DAO
- Not a smart contract platform
- Not a replacement for human governance

This stack is an **advisory, audit-traceable, proof-qualified** infrastructure for human-governed agentic operations.
