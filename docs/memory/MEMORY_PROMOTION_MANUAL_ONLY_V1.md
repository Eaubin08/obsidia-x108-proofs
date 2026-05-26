# Memory Promotion — Manual Only V1

**Status:** ABSOLUTE INVARIANT
**Role:** Memory promotion requires human review. Automatic promotion is absolutely blocked.
**Module:** `periphery/memory/memory_promotion_policy.py`
**Gate:** BLOCK (auto-promotion), HOLD (requires human review)

## The Invariant

**La promotion mémoire est exclusivement manuelle.** Aucun agent, module, ou processus ne peut promouvoir automatiquement un memory candidate. Chaque promotion nécessite une revue humaine explicite.

## Enforcement

- `auto_promotion_blocked = True` — absolute block
- `requires_human_review = True` — always required
- `promotion_allowed = False` — default for all candidates
- `evaluate_promotion_policy(candidate)` → `PromotionDecision`

## Promotion Decision Fields

| Field | Value for all candidates |
|-------|--------------------------|
| promotion_allowed | False |
| auto_promotion_blocked | True |
| requires_human_review | True |
| reason | "AUTO_PROMOTION_INVARIANT_VIOLATED" or "HUMAN_REVIEW_REQUIRED_BEFORE_PROMOTION" |

## Why Manual Only

Automatic memory promotion would:
- Allow periphery to shape the kernel's knowledge base
- Create ungoverned memory state changes
- Bypass the X108 authority gate
- Violate "memory is context, context is signal" invariant

## What Memory CAN Do

- Capture candidates
- Hash content
- Store in append-only ledger
- Flag for human review

## What Memory CANNOT Do

- Auto-promote candidates
- Write to persistent memory
- Decide what becomes truth
- Override human review

## Tests

- `tests/non_sovereignty/test_memory_promotion_not_automatic.py` (5 assertions)
- `tests/non_sovereignty/test_memory_cannot_decide.py`

## Status

**MEMORY_PROMOTION_MANUAL_ONLY_PASS** — Absolute invariant.
