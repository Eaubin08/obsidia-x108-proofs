# Memory Security Boundary V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Security boundary protecting memory from unauthorized writes and automatic promotion.
**Modules:** `memory_governor.py`, `memory_promotion_policy.py`

## The Boundary

The Memory Security Boundary is a defense-in-depth layer that:
1. Blocks all automatic memory writes
2. Blocks all automatic memory promotion
3. Requires human review for any promotion
4. Ensures memory is context-only, never truth
5. Prevents memory from becoming an authority source

## Enforcement Points

### Memory Governor (`periphery/memory_governor.py`)
- Runs as part of control plane for every action
- Returns `PeripheralSignalPacket` with memory governance flags
- `can_emit_act = False` — memory governance cannot authorize actions

### Memory Promotion Policy (`periphery/memory/memory_promotion_policy.py`)
- `auto_promotion_blocked = True` — absolute
- `requires_human_review = True` — absolute
- `promotion_allowed = False` — default

## Forbidden Actions

| Action | Status |
|--------|--------|
| Memory write without human review | BLOCKED |
| Auto-promotion | BLOCKED — absolute |
| Memory as decision authority | BLOCKED — KX108_ONLY |
| Memory as truth | BLOCKED — memory=context, context=signal |

## Tests

- `tests/periphery/test_memory_governor.py`
- `tests/non_sovereignty/test_memory_promotion_not_automatic.py`
- `tests/non_sovereignty/test_memory_cannot_decide.py`
- `tests/non_sovereignty/test_feedback_memory_no_write_v3.py`

## Status

**MEMORY_SECURITY_BOUNDARY_PASS** — Defense-in-depth. Memory is context-only.
