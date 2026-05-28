# OBSIDIA F23A3.2 — VALIDATE SYNTHESIZED MATRIX AGAINST SOURCE FIELDS

Date: 20260528_084822
Mode: VALIDATION_NO_PATCH
Patch: NO
Commit: NO

## Git

- HEAD: 3faaa0e
- TAG: BRODY_F23BC_CONTEXT_AUTOMATION_VALIDATION_20260528
```text
## main...origin/main
?? docs/runtime/OBSIDIA_F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT_20260528_083733.json
?? docs/runtime/OBSIDIA_F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT_20260528_083733.md
?? docs/runtime/OBSIDIA_F23A2_REFLEX_ORCHESTRATOR_PLAN_FROM_REAL_PATHS_20260528_083904.json
?? docs/runtime/OBSIDIA_F23A2_REFLEX_ORCHESTRATOR_PLAN_FROM_REAL_PATHS_20260528_083904.md
?? docs/runtime/OBSIDIA_F23A3_0_EXISTING_RIGHTS_CONTRACTS_FLOW_AUDIT_20260528_084215.json
?? docs/runtime/OBSIDIA_F23A3_0_EXISTING_RIGHTS_CONTRACTS_FLOW_AUDIT_20260528_084215.md
?? docs/runtime/OBSIDIA_F23A3_1_EXISTING_CONTRACT_MATRIX_SYNTHESIS_20260528_084552.json
?? docs/runtime/OBSIDIA_F23A3_1_EXISTING_CONTRACT_MATRIX_SYNTHESIS_20260528_084552.md
?? scripts/f23a1_memory_reflex_orchestrator_source_audit.py
?? scripts/f23a2_reflex_orchestrator_plan_from_real_paths.py
?? scripts/f23a3_0_existing_rights_contracts_flow_audit.py
?? scripts/f23a3_1_synthesize_existing_contract_matrix.py
?? scripts/f23a3_2_validate_synthesized_matrix.py
```

## Source

- source matrix: `C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\docs\runtime\OBSIDIA_F23A3_1_EXISTING_CONTRACT_MATRIX_SYNTHESIS_20260528_084552.json`

## Result

- PASS: True
- errors: 0
- warnings: 0
- compile_ok: True

## Errors

No errors.

## Actor evidence files

- `apps/obsidia_api/brody_automation_orchestrator.py`
- `apps/obsidia_api/brody_candidate_memory_adapter.py`
- `apps/obsidia_api/brody_contracts_packet.py`
- `apps/obsidia_api/brody_full_runtime_orchestrator.py`
- `apps/obsidia_api/brody_memory_promotion_guard.py`
- `apps/obsidia_api/brody_operator_loop_adapter.py`
- `apps/obsidia_api/brody_operator_view_packet.py`
- `apps/obsidia_api/brody_rights_authority_matrix.py`
- `apps/obsidia_api/brody_runtime_context_adapter.py`
- `apps/obsidia_api/brody_temporal_context_adapter.py`
- `apps/obsidia_api/brody_true_voice_adapter.py`
- `apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py`
- `apps/obsidia_api/graphiti_v20_readonly_client.py`
- `apps/obsidia_api/routes/brody.py`
- `apps/obsidia_api/routes/periphery_ops.py`
- `apps/obsidia_api/routes/runtime_freeze.py`
- `apps/obsidia_api/routes/worldcalls.py`
- `apps/obsidia_api/routes/x108.py`

## Allowed flow names

- candidate_memory_to_operator_review
- orchestrator_dry_run_to_operator
- prompt_to_readonly_diagnostic

## Forbidden flow names

- BRODY_TO_AUTOMATION_EXECUTE
- BRODY_TO_GRAPHITI_WRITE
- BRODY_TO_MEMORY_COMMIT
- BRODY_TO_NEO4J_WRITE
- GRAPHITI_TO_DECISION
- MEMORY_REFLEX_TO_ACT
- MEMORY_REFLEX_TO_DECISION
- ORCHESTRATOR_TO_REAL_JOB
- ORCHESTRATOR_TO_SCHEDULER
- SCORE_TO_RUNTIME_VERDICT

## Status

F23A3_2_VALIDATE_SYNTHESIZED_MATRIX_PASS
NEXT=F23A3_FREEZE_AUDIT_PLAN_MATRIX
PATCH=NO
COMMIT=NO