# BFCL Brody Full Runtime — Simple Python 0 Report

**Date**: 2026-05-20
**Status**: BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME_BLOCKED_WITH_REASON

## Pipeline

| Step | Result |
|------|--------|
| Load BFCL simple_python_0 | PASS |
| Call /api/brody/chat (TestClient) | BRODY_FULL_RUNTIME_CALL_ON_BFCL_SIMPLE_PYTHON_0_PASS |
| Three Foundations present | ALL PRESENT |
| Normalize candidate | BFCL_BRODY_FULL_RUNTIME_NORMALIZATION_V2_NO_CANDIDATE |
| Match result | BLOCKED_NO_CANDIDATE |

## Comparison

| Field | Expected | Candidate | Match |
|-------|----------|-----------|-------|
| function | calculate_triangle_area | null | ✗ |
| base | 10 | null | ✗ |
| height | 5 | null | ✗ |
| unit | units | null | ✗ |

## Candidate

```json
null
```

## Boundary invariants

```
OFFLINE_PATH=false
NEO4J_PASSWORD_NOT_SET_BYPASS=false
NO_EXTERNAL_LLM=true
BRODY_DECISION=false
BRODY_TOOL_AUTHORITY=false
DECISION_AUTHORITY=KX108_ONLY
MEMORY_WRITE=false
GRAPHITI_WRITE=false
NEO4J_WRITE=false
EMITS_ACT=false
EMITS_VERDICT=false
KERNEL_MUTATION=false
SIGMA_STATUS=RUNNING_EXTERNAL_LOCAL_LONGRUN
KERNEL_UNTOUCHED_PASS=true
```

## Honest classification

```
GRAPHITI_LIVE_FULL_READY=false
NEO4J_MEMORY_READY=false
MMONDE_34TREES_READY=false
PROJECT_MEMORY_FULL_GRAPH_READY=false
GRAPHITI_LIVE_BLOCKED=true
GRAPHITI_BLOCKER=NEO4J_PASSWORD_NOT_SET
```

## Blocked reason

> Brody true voice adapter generates conversational template responses. None of the allowed output fields (final_answer, response_md, true_voice_snapshot.final_answer, response) contained a structured CANDIDATE_TOOL_CALL JSON block or function-arg text pattern. A dedicated BFCL tool-calling layer is needed in the Brody runtime.

## Next step

> Add a dedicated BFCL tool-calling layer to Brody's true voice adapter.

---

**BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME_BLOCKED_WITH_REASON**