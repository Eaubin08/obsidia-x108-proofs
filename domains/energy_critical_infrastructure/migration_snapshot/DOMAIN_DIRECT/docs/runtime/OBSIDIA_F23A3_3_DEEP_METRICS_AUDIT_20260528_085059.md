# OBSIDIA F23A3.3 — DEEP METRICS AUDIT

Date: 20260528_085059
Mode: DEEP_METRICS_NO_PATCH
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
?? docs/runtime/OBSIDIA_F23A3_2_VALIDATE_SYNTHESIZED_MATRIX_20260528_084822.json
?? docs/runtime/OBSIDIA_F23A3_2_VALIDATE_SYNTHESIZED_MATRIX_20260528_084822.md
?? scripts/f23a1_memory_reflex_orchestrator_source_audit.py
?? scripts/f23a2_reflex_orchestrator_plan_from_real_paths.py
?? scripts/f23a3_0_existing_rights_contracts_flow_audit.py
?? scripts/f23a3_1_synthesize_existing_contract_matrix.py
?? scripts/f23a3_2_validate_synthesized_matrix.py
?? scripts/f23a3_3_deep_metrics_audit.py
```

## Result

- PASS: True
- deep_audit_score: 1.0
- actor_count: 6
- actor_file_count: 18
- errors: 0

## Score components

- validation_pass: 1.0
- compile_pass: 1.0
- actor_file_integrity: 1.0
- no_actor_write_hits: 1.0
- allowed_flow_clean: 1.0
- quarantine_present: 1.0

## Actor metrics

### KX108
- evidence_files_count: 4
- existing_files_count: 4
- missing_files_count: 0
- observed_contract_fields_count: 17/20
- contract_field_coverage_pct: 0.85
- evidence_hits_count: 38
- evidence_density_per_file: 9.5
- forbidden_write_tokens_rescan: []

### BRODY
- evidence_files_count: 5
- existing_files_count: 5
- missing_files_count: 0
- observed_contract_fields_count: 17/20
- contract_field_coverage_pct: 0.85
- evidence_hits_count: 80
- evidence_density_per_file: 16.0
- forbidden_write_tokens_rescan: []

### MEMORY_REFLEX
- evidence_files_count: 4
- existing_files_count: 4
- missing_files_count: 0
- observed_contract_fields_count: 13/20
- contract_field_coverage_pct: 0.65
- evidence_hits_count: 54
- evidence_density_per_file: 13.5
- forbidden_write_tokens_rescan: []

### AUTOMATION_ORCHESTRATOR
- evidence_files_count: 4
- existing_files_count: 4
- missing_files_count: 0
- observed_contract_fields_count: 12/20
- contract_field_coverage_pct: 0.6
- evidence_hits_count: 80
- evidence_density_per_file: 20.0
- forbidden_write_tokens_rescan: []

### GRAPHITI_MEMORY
- evidence_files_count: 4
- existing_files_count: 4
- missing_files_count: 0
- observed_contract_fields_count: 14/20
- contract_field_coverage_pct: 0.7
- evidence_hits_count: 53
- evidence_density_per_file: 13.25
- forbidden_write_tokens_rescan: []

### OPERATOR_HUMAN
- evidence_files_count: 4
- existing_files_count: 4
- missing_files_count: 0
- observed_contract_fields_count: 13/20
- contract_field_coverage_pct: 0.65
- evidence_hits_count: 56
- evidence_density_per_file: 14.0
- forbidden_write_tokens_rescan: []

## Rights metrics

### KX108
- true_capabilities: ['may_decide', 'may_authorize_act']
- false_boundaries: ['may_be_mutated_by_brody']
- negative_assertions_count: 0
- basis: KX108_ONLY / decision_authority / x108_mutation boundary evidence

### BRODY
- true_capabilities: ['may_read', 'may_structure', 'may_explain', 'may_emit_advisory_packet']
- false_boundaries: ['may_decide', 'may_act', 'may_write_memory', 'may_write_graphiti', 'may_execute_automation']
- negative_assertions_count: 5
- basis: contracts packet + rights matrix + route boundary fields

### MEMORY_REFLEX
- true_capabilities: ['may_detect_pattern', 'may_emit_candidate_diagnostic']
- false_boundaries: ['may_commit_memory', 'may_write_graphiti', 'may_decide']
- negative_assertions_count: 3
- basis: candidate memory + promotion guard + readonly context boundaries

### AUTOMATION_ORCHESTRATOR
- true_capabilities: ['may_prepare_dry_run', 'requires_human_review']
- false_boundaries: ['may_execute', 'may_schedule', 'may_write_memory', 'may_write_graphiti']
- negative_assertions_count: 4
- basis: orchestrator/dry_run/human_review/boundary evidence

### GRAPHITI_MEMORY
- true_capabilities: ['may_provide_context']
- false_boundaries: ['may_be_written_by_f23a', 'may_decide']
- negative_assertions_count: 2
- basis: Graphiti readonly client + write token quarantine findings

### OPERATOR_HUMAN
- true_capabilities: ['may_review', 'may_validate_manual_future_phase', 'may_commit_freeze_push', 'automation_still_forbidden_without_explicit_gate']
- false_boundaries: []
- negative_assertions_count: 0
- basis: operator view/loop + human_review + freeze route evidence

## Flow metrics

- allowed_flow_count: 3
- forbidden_flow_count: 10
- allowed_flows_no_writes: True
- allowed_flows_no_executes: True
- allowed_flows_kx108_only: True
- forbidden_flow_names: ['BRODY_TO_AUTOMATION_EXECUTE', 'BRODY_TO_GRAPHITI_WRITE', 'BRODY_TO_MEMORY_COMMIT', 'BRODY_TO_NEO4J_WRITE', 'GRAPHITI_TO_DECISION', 'MEMORY_REFLEX_TO_ACT', 'MEMORY_REFLEX_TO_DECISION', 'ORCHESTRATOR_TO_REAL_JOB', 'ORCHESTRATOR_TO_SCHEDULER', 'SCORE_TO_RUNTIME_VERDICT']

## Quarantine metrics

- risky_write_hits_count: 7
- quarantine_patterns_count: 5
- safe_core_candidates_count: 12
- risky_write_paths: ['periphery/brody_memory_readonly/graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only/brody_graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only_v1.py', 'periphery/brody_memory_readonly/graphiti_import_apply_guarded_manual_only/brody_graphiti_import_apply_guarded_manual_only_v1.py', 'periphery/brody_memory_readonly/graphiti_import_dry_run_from_post_human_prep_readonly/brody_graphiti_import_dry_run_from_post_human_prep_readonly_v1.py', 'periphery/brody_memory_readonly/neo4j_brody_guide_bridge_readonly/brody_neo4j_guide_bridge_readonly_v1.py', 'scripts/brody_memory_intake_gate.py', 'scripts/f23b1_1_focused_context_packet_discovery.py', 'scripts/f23b2_f23c_real_path_validation.py']
- quarantine_patterns: ['graphiti_guarded_manual_apply', 'graphiti_import_apply', 'graphiti_import_dry_run', 'neo4j_brody_guide_bridge', 'brody_memory_intake_gate.py']
- safe_core_candidates: ['apps/obsidia_api/brody_automation_orchestrator.py', 'apps/obsidia_api/brody_memory_promotion_guard.py', 'apps/obsidia_api/brody_candidate_memory_adapter.py', 'apps/obsidia_api/brody_runtime_context_adapter.py', 'apps/obsidia_api/brody_temporal_context_adapter.py', 'apps/obsidia_api/brody_operator_view_packet.py', 'apps/obsidia_api/brody_operator_loop_adapter.py', 'periphery/brody_memory_readonly/memory_pipeline_freeze_v2_readonly/brody_memory_pipeline_freeze_v2_readonly.py', 'periphery/brody_memory_readonly/session_presave_buffer_readonly/brody_session_presave_buffer_readonly_v1.py', 'periphery/brody_memory_readonly/session_reopen_loop_readonly/brody_session_reopen_loop_readonly_v1.py', 'periphery/brody_memory_readonly/session_close_human_validation_gate_readonly/brody_session_close_human_validation_gate_readonly_v1.py', 'periphery/brody_memory_readonly/auto_triage_memory_intake_readonly/brody_auto_triage_memory_intake_readonly_v1.py']

## Errors

No errors.

## Status

F23A3_3_DEEP_METRICS_AUDIT_PASS
NEXT=F23A3_FREEZE_AUDIT_PLAN_MATRIX
PATCH=NO
COMMIT=NO