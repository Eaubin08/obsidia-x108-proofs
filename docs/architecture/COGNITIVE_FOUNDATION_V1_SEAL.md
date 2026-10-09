# COGNITIVE FOUNDATION V1 SEAL

## 1. Sealed Scope
This manifest establishes a strict, canonical non-regression boundary around the certified SENS/Cognition foundation:
- **SENS Semantic Closure** (`app/semantic/`, `tests/test_semantic_closure*.py`)
- **B6 Runtime Wiring** (`app/harness/state_explicit/`, `tests/test_pre_execution_context_v0.py`)
- **B7 Cognitive Role** (`app/cognition/b7/`, `tests/b7/`)
- **B8 Knowledge Promotion** (`app/knowledge/b8/`, `tests/b8/`)
- **B9 Cognitive Path** (`app/cognition/b9/`, `tests/b9/`)

## 2. Closure Status
**Status:** SEALED
**Checkpoint HEAD:** 5d35cdd361c8bb27f1bf2193309e4b84d7017ba4

## 3. Core Invariants
The following principles are absolute and frozen:
- `COGNITION != AUTHORITY`
- `MEMORY != TRUTH`
- `CONFIDENCE != AUTHORITY`
- `COMPETENCE != AUTHORITY`
- `VERIFICATION != ACTION_AUTHORITY`
- `PROMOTED != ABSOLUTE_TRUTH`
- `UNKNOWN != FALSE`
- `FRESH != RECENT`
- `TIME_VALUE != TEMPORAL_ORDER`
- `TIMESTAMP != CAUSALITY`
- `SERIALIZATION_ORDER != CAUSAL_ORDER`
- `SLOT_REVISION_IS_CLOCK=NO`
- `SLOT_REVISION_IS_CAUSALITY=NO`
- `ONE_SHARED_CLOCK=NO`
- `CROSS_CLOCK_NUMERIC_COMPARISON_FORBIDDEN=YES`
- `B7_ACCEPT != DURABLE_KNOWLEDGE`
- `PATH_HISTORY != TRUTH`
- `FAILED_PATH != FORBIDDEN_FOREVER`
- `PAST_SUCCESS != CURRENT_AUTHORITY`

*KX108_ONLY remains the sovereign decision/action authority.*

## 4. Protected Components
- **PROTECTED_CONTRACT**: Core interfaces defining B7 roles and B8/B9 knowledge states.
- **PROTECTED_RUNTIME_CORE**: `app/cognition/`, `app/knowledge/b8/`, `app/harness/state_explicit/`.
- **PROTECTED_TEST_SENTINEL**: Regression suite (`scripts/foundation_sentinel.py`).

## 5. Reopen Protocol
Any intentional semantic change to the sealed foundation requires explicit reopening (`FOUNDATION_REOPEN=YES`) and must provide:
- Reason
- Affected layer
- Exact invariant changed
- Compatibility impact
- Migration requirement
- RED reproducer
- Focused recertification
- Downstream regression analysis

Without this explicit reopen protocol, semantic changes are forbidden. Bug fixes, test improvements, and optimizations that do NOT change semantics are allowed.

## 6. Extension Rule
`NEW_LAYER_SHOULD_EXTEND_BEFORE_MODIFYING_FOUNDATION=YES`
Milestones 32+ should preferentially compose, adapt, wrap, reference, or consume B6/B7/B8/B9 rather than alter them. If a primitive or layer can be built outside the seal, it MUST stay outside.

## 7. Deferred Items
The seal does NOT claim finality for:
- Durable Memory
- World Model
- Competence / Calibration
- ARM / Cross-domain transfer / Bio / COMOS
These layers may freely evolve as long as they respect the sealed boundary.

## 8. Next Milestone
**Next:** MILESTONE 32 (Common Cognitive Primitives)
