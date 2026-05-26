# Capability Is Not Authority — V1

**Classification:** DOCS  
**Layer:** AGENTIC  
**Status:** STABLE  
**Date:** 2026-05-19

---

## The Core Principle

A system capable of generating an output is not authorized to act on that capability unless a governance chain explicitly permits it.

This principle is the foundation of every sovereignty invariant in the Obsidia X-108 periphery.

---

## Why This Matters

Modern AI systems can:
- Generate ALLOW/BLOCK/HOLD decisions
- Write to memory systems
- Emit transaction instructions
- Draft smart contracts
- Produce wallet operations

All of these are **capabilities** — not **authorities**. Without the X-108 governance chain, they are forbidden outputs.

---

## Invariant Encoding in Code

Every periphery module encodes this principle as a hard invariant:

```python
can_decide: bool = False
can_emit_act: bool = False
memory_write_allowed: bool = False
auto_promotion_allowed: bool = False
decision_authority: str = "KX108_ONLY"
```

These are not configurable. They are enforced at construction time.

---

## The Authority Chain

Capability (signal exists) → Advisory output (signal emitted) → Candidate (signal qualified) → Proof (OS3 proves) → SovereignTicket (authorized) → Gateway (egress controlled) → **Act** (executed only here)

No shortcut. No bypass. No autonomous execution at any earlier stage.

---

## Forbidden Patterns

| Pattern | Why Forbidden |
|---------|---------------|
| Brody emitting ACT | Brody is advisory — decision_authority=KX108_ONLY |
| Memory auto-promoting candidate | Requires human review — auto_promotion_allowed=False |
| Periphery emitting BLOCK/ALLOW | Sovereign tokens reserved for kernel output |
| Blockchain action without SovereignTicket | Gateway blocks without ticket |
| Gencoin minting | Not a real token — ledger only |

---

## Test Coverage

Every forbidden pattern above is tested in `tests/non_sovereignty/`. These tests are non-negotiable and must remain green.
