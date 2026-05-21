# Memory Module

**Status:** FIRST_CLASS_X108_MODULE — CANDIDATE ONLY / MANUAL PROMOTION
**Source:** `periphery/memory/` (5 modules)
**Tests:** `tests/periphery/test_memory_*.py` + `tests/non_sovereignty/test_memory_*.py`

## Modules

| Module | Role | Write |
|--------|------|-------|
| `memory_source_types.py` | Defines memory source types and statuses | — |
| `memory_source_registry.py` | Registers and validates memory sources | — |
| `memory_candidate.py` | Creates memory candidates (capture only) | READONLY |
| `memory_candidate_ledger.py` | Append-only candidate ledger | APPEND |
| `memory_promotion_policy.py` | Manual-only promotion policy | VALIDATOR |

## Sovereignty Invariants

- `memory_write_allowed = False` — memory candidates are capture-only
- `auto_promotion_allowed = False` — promotion requires human review
- `auto_promotion_blocked = True` — absolute block on automatic promotion
- No module emits ACT
- No module decides

## Canonical Rules

- Mémoire = contexte. Contexte = signal.
- La mémoire n'est pas vérité.
- La mémoire candidate est capturée, pas promue automatiquement.
- La promotion nécessite une review humaine.
