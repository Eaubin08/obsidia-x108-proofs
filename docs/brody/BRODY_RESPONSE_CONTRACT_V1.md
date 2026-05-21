# Brody Response Contract V1

**Status:** ABSOLUTE INVARIANT
**Role:** Defines and enforces sovereignty constraints on every Brody response.
**Module:** `periphery/brody/brody_response_contract.py`

## Contract Fields

```python
decision_authority: str = "KX108_ONLY"   # Brody never decides
advisory_only: bool = True               # Responses are informational
memory_write: bool = False               # Brody cannot write memory
kernel_mutation: bool = False            # Brody cannot mutate kernel
emits_act: bool = False                  # Brody never emits ACT
emits_verdict: bool = False              # Brody never emits verdict
readonly: bool = True                    # All operations read-only
context_signal_only: bool = True         # Brody provides context, not decisions
```

## Validation

The contract's `validate()` method asserts all invariants. A violation of any field raises `BRODY_CONTRACT_VIOLATION`.

## Forbidden Actions

| Violation | Raises |
|-----------|--------|
| decision_authority != "KX108_ONLY" | BRODY_CONTRACT_VIOLATION:decision_authority |
| memory_write = True | BRODY_CONTRACT_VIOLATION:memory_write |
| kernel_mutation = True | BRODY_CONTRACT_VIOLATION:kernel_mutation |

## Canonical Rule

**Brody répond. X108 décide. Context ≠ Decision.**

## Tests

- `tests/periphery/test_brody_response_contract.py`
- `tests/non_sovereignty/test_brody_no_decision.py`

## Status

**ABSOLUTE INVARIANT** — Never broken. Never bypassed.
