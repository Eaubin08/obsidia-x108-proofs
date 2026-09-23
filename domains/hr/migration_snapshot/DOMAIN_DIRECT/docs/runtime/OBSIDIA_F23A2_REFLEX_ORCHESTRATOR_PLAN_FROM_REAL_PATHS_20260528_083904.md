# OBSIDIA F23A2 — REFLEX ORCHESTRATOR PLAN FROM REAL PATHS

Date: 20260528_083904
Mode: PLAN_NO_PATCH
Patch: NO
Commit: NO

## Git

- HEAD: 3faaa0e
- TAG: BRODY_F23BC_CONTEXT_AUTOMATION_VALIDATION_20260528
```text
## main...origin/main
?? docs/runtime/OBSIDIA_F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT_20260528_083733.json
?? docs/runtime/OBSIDIA_F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT_20260528_083733.md
?? scripts/f23a1_memory_reflex_orchestrator_source_audit.py
?? scripts/f23a2_reflex_orchestrator_plan_from_real_paths.py
```

## Source audit

- source: `C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\docs\runtime\OBSIDIA_F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT_20260528_083733.json`
- candidates: 471
- compile_ok: True
- risky_write_hits: 7

## Safe core candidates

- `apps/obsidia_api/brody_automation_orchestrator.py`
- `apps/obsidia_api/brody_memory_promotion_guard.py`
- `apps/obsidia_api/brody_candidate_memory_adapter.py`
- `apps/obsidia_api/brody_runtime_context_adapter.py`
- `apps/obsidia_api/brody_temporal_context_adapter.py`
- `apps/obsidia_api/brody_operator_view_packet.py`
- `apps/obsidia_api/brody_operator_loop_adapter.py`
- `periphery/brody_memory_readonly/memory_pipeline_freeze_v2_readonly/brody_memory_pipeline_freeze_v2_readonly.py`
- `periphery/brody_memory_readonly/session_presave_buffer_readonly/brody_session_presave_buffer_readonly_v1.py`
- `periphery/brody_memory_readonly/session_reopen_loop_readonly/brody_session_reopen_loop_readonly_v1.py`
- `periphery/brody_memory_readonly/session_close_human_validation_gate_readonly/brody_session_close_human_validation_gate_readonly_v1.py`
- `periphery/brody_memory_readonly/auto_triage_memory_intake_readonly/brody_auto_triage_memory_intake_readonly_v1.py`

## Quarantine / do-not-wire patterns

- `graphiti_guarded_manual_apply`
- `graphiti_import_apply`
- `graphiti_import_dry_run`
- `neo4j_brody_guide_bridge`
- `brody_memory_intake_gate.py`

## Risky write hits from F23A1

### periphery/brody_memory_readonly/graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only/brody_graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only_v1.py
- forbidden_write_hits: ['MERGE ']

### periphery/brody_memory_readonly/graphiti_import_apply_guarded_manual_only/brody_graphiti_import_apply_guarded_manual_only_v1.py
- forbidden_write_hits: ['MERGE ', 'SET ']

### periphery/brody_memory_readonly/graphiti_import_dry_run_from_post_human_prep_readonly/brody_graphiti_import_dry_run_from_post_human_prep_readonly_v1.py
- forbidden_write_hits: ['MERGE ', 'SET ']

### periphery/brody_memory_readonly/neo4j_brody_guide_bridge_readonly/brody_neo4j_guide_bridge_readonly_v1.py
- forbidden_write_hits: ['MERGE ', 'CREATE ', 'SET ']

### scripts/brody_memory_intake_gate.py
- forbidden_write_hits: ['DELETE ', 'DETACH DELETE']

### scripts/f23b1_1_focused_context_packet_discovery.py
- forbidden_write_hits: ['session.write_transaction', 'execute_write', 'MERGE ', 'CREATE ', 'SET ', 'DELETE ', 'DETACH DELETE', 'git commit', 'git push', 'os.system(']

### scripts/f23b2_f23c_real_path_validation.py
- forbidden_write_hits: ['session.write_transaction', 'execute_write', 'MERGE ', 'CREATE ', 'SET ', 'DELETE ', 'DETACH DELETE', 'git commit', 'git push', 'os.system(']

## Test patterns for future F23A4

- port fermé / backend unavailable
- fallback Graphiti
- READ/WRITE confusion
- stale server / wrong port
- Neo4j mapping mismatch
- UI/backend mismatch
- memory material low
- action request disguised as memory reflex

## Recommended ladder

### F23A3 — Reflex Orchestrator Boundary Validation
- patch: NO
- goal: Validate safe candidates compile and expose readonly/KX108 invariants.
- allowed: ['source validation', 'tests', 'reports']
- forbidden: ['memory write', 'Graphiti write', 'automation execute', 'kernel mutation', 'x108 mutation']
- pass: ['all safe candidates compile', 'risky files quarantined', 'boundary invariants present']

### F23A4 — Memory Reflex Diagnostic Packet Minimal
- patch: MAYBE_LATER
- goal: Create a readonly diagnostic packet that recognizes failure patterns but emits no action.
- allowed: ['advisory packet', 'pattern labels', 'readonly scoring']
- forbidden: ['routing into automation', 'write memory', 'Graphiti write', 'ACT/ALLOW/BLOCK decision']
- pass: ['pattern recognized', 'KX108_ONLY', 'emits_act=false', 'automation_execute=false']

### F23A5 — Orchestrator Dry-Run Adapter
- patch: DEFERRED
- goal: Expose orchestrator as dry-run-only surface after F23A3/F23A4.
- allowed: ['dry_run=true', 'no execution', 'operator-visible explanation']
- forbidden: ['job execution', 'scheduler activation', 'memory commit', 'Graphiti mutation']
- pass: ['dry_run only', 'no side effects', 'human review required']

## Status

F23A2_REFLEX_ORCHESTRATOR_PLAN_FROM_REAL_PATHS_DONE
NEXT=F23A3_REFLEX_ORCHESTRATOR_BOUNDARY_VALIDATION
PATCH=NO
COMMIT=NO