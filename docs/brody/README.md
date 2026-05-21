# Brody Module

**Status:** FIRST_CLASS_X108_MODULE — READONLY / ADVISORY ONLY
**Source:** `periphery/brody/` (5 modules)
**Tests:** `tests/periphery/test_brody_*.py` + `tests/non_sovereignty/test_brody_*.py`

## Modules

| Module | Role | Authority |
|--------|------|-----------|
| `brody_runtime_readonly.py` | Read-only query responder | ADVISORY_ONLY |
| `brody_response_contract.py` | Invariant enforcement contract | KX108_ONLY |
| `brody_context_query.py` | Context-aware query processor | ADVISORY_ONLY |
| `brody_response_sanitizer.py` | Response output sanitization | ADVISORY_ONLY |
| `brody_language_router.py` | Multi-language routing | ADVISORY_ONLY |

## Sovereignty Invariants

- `decision_authority = "KX108_ONLY"` — Brody never decides
- `advisory_only = True` — responses are informational only
- `memory_write = False` — Brody cannot write to memory
- `emits_act = False` — Brody never emits ACT
- `emits_verdict = False` — Brody never emits verdict
- `kernel_mutation = False` — Brody cannot mutate kernel state
- `readonly = True` — all operations are read-only

## Relation to X108

Brody responds. X108 decides. Brody provides context, analysis, and advisory output — never a binding decision. Every Brody response carries the BRODY_CONTRACT asserting these invariants.

## Canonical Rules

- Brody répond mais ne décide pas
- Brody = contexte, contexte = signal, signal ≠ décision
- X108 seul décide. OS3 prouve. Sigma agrège.
