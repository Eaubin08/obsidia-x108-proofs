# OBSIDIA F23A1 — MEMORY REFLEX / ORCHESTRATOR SOURCE AUDIT

Date: 20260528_083733
Mode: SOURCE_AUDIT_NO_PATCH
Patch: NO
Commit: NO

## Git

- HEAD: 3faaa0e
- TAG: BRODY_F23BC_CONTEXT_AUTOMATION_VALIDATION_20260528
```text
## main...origin/main
?? scripts/f23a1_memory_reflex_orchestrator_source_audit.py
```

## Candidate count: 471

## Compile

- compile_ok: True
- compiled_files: 43

## Family coverage

### reflex
- `apps/obsidia_api/brody_automation_orchestrator.py`
- `periphery/brody_memory_readonly/memory_pipeline_freeze_v2_readonly/brody_memory_pipeline_freeze_v2_readonly.py`
- `scripts/f23a_to_f27_reflex_automation_protocol_audit.py`
- `periphery/brody_memory_readonly/memory_pipeline_freeze_v2_readonly/BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_MANIFEST.json`
- `periphery/brody_memory_readonly/session_close_human_validation_gate_readonly/brody_session_close_human_validation_gate_readonly_v1.py`
- `periphery/brody_memory_readonly/auto_triage_memory_intake_readonly/BRODY_AUTO_TRIAGE_MEMORY_INTAKE_READONLY_MANIFEST.json`
- `periphery/brody_memory_readonly/auto_triage_memory_intake_readonly/README_BOUNDARY.md`
- `periphery/brody_memory_readonly/auto_triage_memory_intake_readonly/brody_auto_triage_memory_intake_readonly_v1.py`
- `periphery/brody_memory_readonly/candidate_export_for_graphiti_readonly/brody_candidate_export_for_graphiti_readonly_v1.py`
- `periphery/brody_memory_readonly/graphiti_review_decision_apply_readonly/brody_graphiti_review_decision_apply_readonly_v1.py`
- `periphery/brody_memory_readonly/graphiti_review_gate_from_post_human_dry_run_readonly/brody_graphiti_review_gate_from_post_human_dry_run_readonly_v1.py`
- `periphery/brody_memory_readonly/memory_pipeline_freeze_v2_readonly/README_BOUNDARY.md`
- `periphery/brody_memory_readonly/post_human_review_memory_triage_readonly/brody_post_human_review_memory_triage_readonly_v1.py`
- `periphery/brody_memory_readonly/session_close_decision_apply_readonly/brody_session_close_decision_apply_readonly_v1.py`
- `apps/obsidia_api/brody_domain_raccord_adapter.py`
- `periphery/brody_memory_readonly/post_human_review_memory_triage_readonly/README_BOUNDARY.md`
- `scripts/f22a3_document_source_traceability_audit.py`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/03_MEMOIRE_MONDE_COSMOS_REFLEX/COSMOS_CONSTRAINT_LAYER.md`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/03_MEMOIRE_MONDE_COSMOS_REFLEX/Event.schema.json`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/03_MEMOIRE_MONDE_COSMOS_REFLEX/Mmonde_FORMAL_SPEC.md`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/03_MEMOIRE_MONDE_COSMOS_REFLEX/NodeContinuum.schema.json`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/03_MEMOIRE_MONDE_COSMOS_REFLEX/README.md`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/03_MEMOIRE_MONDE_COSMOS_REFLEX/REFLEX_REDUCER_SPEC.md`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/03_MEMOIRE_MONDE_COSMOS_REFLEX/Timeline.schema.json`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/03_MEMOIRE_MONDE_COSMOS_REFLEX/__init__.py`

### automation_orchestrator
- `apps/obsidia_api/brody_automation_orchestrator.py`
- `apps/obsidia_api/brody_full_runtime_orchestrator.py`
- `apps/obsidia_api/routes/brody.py`
- `scripts/f23a_to_f27_reflex_automation_protocol_audit.py`
- `scripts/f22a3_document_source_traceability_audit.py`
- `periphery/OBSIDIA_V4_STRUCTURED_FULL/07_AGENTS_ET_ROLES/CANONIQUES/ROLE_013__Orchestrator.md`
- `periphery/OBSIDIA_V4_STRUCTURED_FULL/14_REGROUPEMENTS_COHERENCE/GROUPE_05__Agents_Infrastructure_Tools/06_AGENT_ROLE__Orchestrator.md`
- `periphery/OBSIDIA_V4_STRUCTURED_FULL/14_REGROUPEMENTS_COHERENCE/GROUPE_07__Ops_CI_CD_Validation_continue/06_AGENT_ROLE__Orchestrator.md`
- `periphery/agents/v4_roles/CANONIQUES/ROLE_013__Orchestrator.md`
- `periphery/OBSIDIA_V4_STRUCTURED_FULL/00_SOURCES/CHECKLIST_V4.md`
- `periphery/OBSIDIA_V4_STRUCTURED_FULL/00_INDEX/ARBORESCENCE_COMPLETE.md`
- `periphery/OBSIDIA_V4_STRUCTURED_FULL/00_INDEX/MANIFEST_SHA256.json`
- `periphery/OBSIDIA_V4_STRUCTURED_FULL/01_REGISTRES_JSON/regroupements_fichiers_copies.json`
- `periphery/OBSIDIA_V4_STRUCTURED_FULL/01_REGISTRES_JSON/agents_canoniques.json`
- `periphery/OBSIDIA_V4_STRUCTURED_FULL/01_REGISTRES_JSON/groupes_coherence.json`
- `periphery/OBSIDIA_V4_STRUCTURED_FULL/07_AGENTS_ET_ROLES/AGENTS_CANONIQUES_ET_GARDIENS.md`
- `periphery/OBSIDIA_V4_STRUCTURED_FULL/14_REGROUPEMENTS_COHERENCE/GROUPE_05__Agents_Infrastructure_Tools/00_GUIDE_GROUPE.md`
- `periphery/OBSIDIA_V4_STRUCTURED_FULL/14_REGROUPEMENTS_COHERENCE/GROUPE_07__Ops_CI_CD_Validation_continue/00_GUIDE_GROUPE.md`
- `periphery/agents/v4_roles/AGENTS_CANONIQUES_ET_GARDIENS.md`

### avdr_phase
- `scripts/f23a_to_f27_reflex_automation_protocol_audit.py`
- `apps/obsidia_api/brody_cognitive_modules_adapter.py`
- `apps/obsidia_api/brody_semantic_query_router.py`
- `apps/obsidia_api/brody_temporal_context_adapter.py`
- `apps/obsidia_api/brody_true_voice_adapter.py`
- `periphery/brody_memory_readonly/brody_api_memory_operator_replay_api_fix_v2_readonly/api_endpoints/context_canon.json`
- `periphery/brody_memory_readonly/brody_api_memory_operator_replay_api_fix_v2_readonly/api_endpoints/context_x108.json`
- `periphery/brody_memory_readonly/brody_memory_context_operator_interaction_test_readonly_freeze_v1/api_endpoints/context_canon.json`
- `periphery/brody_memory_readonly/brody_memory_context_operator_interaction_test_readonly_freeze_v1/api_endpoints/context_kernel.json`
- `periphery/brody_memory_readonly/brody_memory_context_operator_interaction_test_readonly_freeze_v1/api_endpoints/context_x108.json`
- `periphery/brody_memory_readonly/brody_api_memory_operator_replay_api_fix_v2_readonly/api_endpoints/search_x108.json`
- `periphery/brody_memory_readonly/brody_memory_context_operator_interaction_test_readonly_freeze_v1/api_endpoints/search_canon.json`
- `periphery/brody_memory_readonly/brody_memory_context_operator_interaction_test_readonly_freeze_v1/api_endpoints/search_freeze.json`
- `periphery/brody_memory_readonly/brody_memory_context_operator_interaction_test_readonly_freeze_v1/api_endpoints/search_x108.json`
- `scripts/f22a3_document_source_traceability_audit.py`
- `apps/obsidia_api/routes/periphery_ops.py`
- `periphery/core_registry.py`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/12_FRICTION_AVDR_CONTINUUM/AVDR.schema.json`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/12_FRICTION_AVDR_CONTINUUM/FrictionSymbolique.schema.json`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/12_FRICTION_AVDR_CONTINUUM/OBAN.schema.json`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/12_FRICTION_AVDR_CONTINUUM/README.md`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/12_FRICTION_AVDR_CONTINUUM/__init__.py`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/12_FRICTION_AVDR_CONTINUUM/avdr.py`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/12_FRICTION_AVDR_CONTINUUM/check_incoherence.py`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/12_FRICTION_AVDR_CONTINUUM/compress_nodes.py`

### memory_pipeline
- `apps/obsidia_api/brody_automation_orchestrator.py`
- `periphery/brody_memory_readonly/memory_pipeline_freeze_v2_readonly/brody_memory_pipeline_freeze_v2_readonly.py`
- `scripts/f23a_to_f27_reflex_automation_protocol_audit.py`
- `apps/obsidia_api/brody_freeze_metrics_snapshot.py`
- `apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py`
- `periphery/brody_memory_readonly/memory_pipeline_freeze_v2_readonly/BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_MANIFEST.json`
- `periphery/brody_memory_readonly/memory_pipeline_v2_close_report_readonly/README_BOUNDARY.md`
- `periphery/brody_memory_readonly/memory_pipeline_v2_close_report_readonly/brody_memory_pipeline_v2_close_report_readonly.py`
- `periphery/brody_memory_readonly/memory_readonly_micro_smoke/brody_memory_readonly_micro_smoke_v1.py`
- `periphery/brody_memory_readonly/memory_scheduler_readonly/brody_memory_scheduler_readonly_v1.py`
- `periphery/brody_memory_readonly/readonly_session_test/brody_readonly_session_test_v1.py`
- `periphery/brody_memory_readonly/session_close_human_validation_gate_readonly/brody_session_close_human_validation_gate_readonly_v1.py`
- `periphery/brody_memory_readonly/session_presave_buffer_readonly/brody_session_presave_buffer_readonly_v1.py`
- `periphery/brody_memory_readonly/session_reopen_loop_readonly/brody_session_reopen_loop_readonly_v1.py`
- `periphery/brody_memory_readonly/memory_pipeline_freeze_report_readonly/BRODY_MEMORY_PIPELINE_FREEZE_REPORT_READONLY_MANIFEST.json`
- `periphery/brody_memory_readonly/memory_pipeline_freeze_report_readonly/README_BOUNDARY.md`
- `periphery/brody_memory_readonly/memory_pipeline_freeze_report_readonly/brody_memory_pipeline_freeze_report_readonly_v1.py`
- `periphery/brody_memory_readonly/memory_pipeline_freeze_v2_readonly/README_BOUNDARY.md`
- `periphery/brody_memory_readonly/memory_pipeline_v2_close_report_readonly/BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_MANIFEST.json`
- `periphery/brody_memory_readonly/post_graphiti_replay_query_regression_readonly/brody_post_graphiti_replay_query_regression_readonly_v1.py`
- `periphery/brody_memory_readonly/memory_pipeline_freeze_report_readonly/__init__.py`
- `periphery/brody_memory_readonly/memory_pipeline_freeze_v2_readonly/__init__.py`
- `periphery/brody_memory_readonly/memory_pipeline_v2_close_report_readonly/__init__.py`
- `periphery/brody_memory_readonly/post_graphiti_replay_query_regression_readonly/README_BOUNDARY.md`
- `periphery/brody_memory_readonly/session_close_human_validation_gate_readonly/README_BOUNDARY.md`

### memory_promotion_guard
- `apps/obsidia_api/routes/brody.py`
- `apps/obsidia_api/brody_memory_promotion_guard.py`
- `scripts/f23a_to_f27_reflex_automation_protocol_audit.py`
- `apps/obsidia_api/brody_operator_view_packet.py`
- `apps/obsidia_api/routes/runtime_freeze.py`
- `scripts/f21a_runtime_freeze_dashboard_global_audit.py`
- `scripts/f20a_gencoin_cognitive_value_ledger_audit.py`

### readonly_context
- `scripts/f23a_to_f27_reflex_automation_protocol_audit.py`
- `apps/obsidia_api/brody_machination_composer.py`
- `apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py`
- `periphery/brody_memory_readonly/brody_api_bridge_contract_readonly/README_BOUNDARY.md`
- `periphery/brody_memory_readonly/brody_api_bridge_readiness_readonly/README_BOUNDARY.md`
- `periphery/brody_memory_readonly/brody_api_memory_operator_replay_api_fix_v2_readonly/api_endpoints/context_canon.json`
- `periphery/brody_memory_readonly/brody_api_memory_operator_replay_api_fix_v2_readonly/api_endpoints/context_x108.json`
- `periphery/brody_memory_readonly/brody_api_memory_operator_replay_readonly/reports/api_memory_operator_replay_report.json`
- `periphery/brody_memory_readonly/brody_memory_context_operator_interaction_test_readonly_freeze_v1/api_endpoints/context_canon.json`
- `periphery/brody_memory_readonly/brody_memory_context_operator_interaction_test_readonly_freeze_v1/api_endpoints/context_kernel.json`
- `periphery/brody_memory_readonly/brody_memory_context_operator_interaction_test_readonly_freeze_v1/api_endpoints/context_x108.json`
- `periphery/brody_memory_readonly/memory_layer_authority_model_readonly/MEMORY_LAYER_AUTHORITY_MODEL_READONLY_MANIFEST.json`
- `periphery/brody_memory_readonly/memory_layer_authority_model_readonly/README_BOUNDARY.md`
- `periphery/brody_memory_readonly/session_reopen_loop_readonly/README_BOUNDARY.md`
- `apps/obsidia_api/brody_contracts_packet.py`
- `apps/obsidia_api/brody_gencoin_transverse_interface.py`
- `periphery/brody_memory_readonly/brody_api_memory_operator_replay_api_fix_v2_readonly/api_endpoints/evidence.json`
- `periphery/brody_memory_readonly/brody_api_memory_operator_replay_api_fix_v2_readonly/api_endpoints/readiness.json`
- `periphery/brody_memory_readonly/brody_memory_context_operator_interaction_test_readonly_freeze_v1/api_endpoints/context_brody.json`
- `periphery/brody_memory_readonly/brody_memory_context_operator_interaction_test_readonly_freeze_v1/api_endpoints/evidence.json`
- `periphery/brody_memory_readonly/brody_memory_context_operator_interaction_test_readonly_freeze_v1/api_endpoints/readiness.json`
- `periphery/brody_memory_readonly/brody_x108_native_runbook_readonly/README_RUNBOOK.md`
- `periphery/brody_memory_readonly/context_packet_consumer_readonly/README_BOUNDARY.md`
- `scripts/f22a3_document_source_traceability_audit.py`
- `apps/obsidia_api/routes/periphery_ops.py`

### candidate_memory
- `apps/obsidia_api/routes/brody.py`
- `apps/obsidia_api/brody_candidate_memory_adapter.py`
- `apps/obsidia_api/brody_memory_promotion_guard.py`
- `apps/obsidia_api/brody_machination_composer.py`
- `apps/obsidia_api/brody_cognitive_modules_adapter.py`
- `apps/obsidia_api/brody_runtime_context_adapter.py`
- `apps/obsidia_api/brody_temporal_context_adapter.py`
- `scripts/f22a3_document_source_traceability_audit.py`

### session_buffer
- `apps/obsidia_api/brody_automation_orchestrator.py`
- `apps/obsidia_api/brody_full_runtime_orchestrator.py`
- `periphery/brody_memory_readonly/memory_pipeline_freeze_v2_readonly/brody_memory_pipeline_freeze_v2_readonly.py`
- `apps/obsidia_api/brody_candidate_memory_adapter.py`
- `apps/obsidia_api/brody_freeze_metrics_snapshot.py`
- `periphery/brody_memory_readonly/memory_pipeline_v2_close_report_readonly/README_BOUNDARY.md`
- `periphery/brody_memory_readonly/memory_pipeline_v2_close_report_readonly/brody_memory_pipeline_v2_close_report_readonly.py`
- `periphery/brody_memory_readonly/memory_readonly_micro_smoke/brody_memory_readonly_micro_smoke_v1.py`
- `periphery/brody_memory_readonly/memory_scheduler_readonly/brody_memory_scheduler_readonly_v1.py`
- `periphery/brody_memory_readonly/readonly_session_test/brody_readonly_session_test_v1.py`
- `periphery/brody_memory_readonly/session_presave_buffer_readonly/brody_session_presave_buffer_readonly_v1.py`
- `periphery/brody_memory_readonly/session_reopen_loop_readonly/brody_session_reopen_loop_readonly_v1.py`
- `apps/obsidia_api/brody_session_memory_adapter.py`
- `periphery/brody_memory_readonly/brody_agent_readonly_session_test_packet/brody_agent_readonly_session_test_packet_v1.py`
- `periphery/brody_memory_readonly/project_intake_capture_buffer_readonly/brody_project_intake_capture_buffer_readonly_v1.py`
- `periphery/brody_memory_readonly/session_presave_buffer_readonly/BRODY_SESSION_PRESAVE_BUFFER_READONLY_MANIFEST.json`
- `periphery/brody_memory_readonly/session_reopen_loop_readonly/BRODY_SESSION_REOPEN_LOOP_READONLY_MANIFEST.json`
- `periphery/brody_memory_readonly/session_reopen_loop_readonly/README_BOUNDARY.md`
- `periphery/brody_memory_readonly/memory_readonly_micro_smoke/README_BOUNDARY.md`
- `periphery/brody_memory_readonly/session_presave_buffer_readonly/README_BOUNDARY.md`
- `periphery/brody_memory_readonly/session_presave_buffer_readonly/__init__.py`
- `periphery/brody_memory_readonly/session_reopen_loop_readonly/__init__.py`
- `periphery/core_registry.py`

### operator_loop
- `apps/obsidia_api/brody_automation_orchestrator.py`
- `apps/obsidia_api/routes/brody.py`
- `apps/obsidia_api/brody_freeze_metrics_snapshot.py`
- `apps/obsidia_api/brody_machination_composer.py`
- `apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py`
- `apps/obsidia_api/brody_operator_view_packet.py`
- `apps/obsidia_api/brody_runtime_context_adapter.py`
- `apps/obsidia_api/brody_semantic_query_router.py`
- `apps/obsidia_api/brody_true_voice_adapter.py`
- `apps/obsidia_api/brody_operator_loop_adapter.py`
- `apps/obsidia_api/brody_rights_authority_matrix.py`
- `scripts/f22a3_document_source_traceability_audit.py`
- `apps/obsidia_api/routes/runtime_freeze.py`
- `scripts/f11a_live_brody_chat_smoke.py`
- `scripts/f21a_runtime_freeze_dashboard_global_audit.py`
- `scripts/f12a_terminal_visible_assert.py`
- `scripts/f13a_live_ui_source_assert.py`

### kx108_boundary
- `apps/obsidia_api/brody_automation_orchestrator.py`
- `apps/obsidia_api/brody_full_runtime_orchestrator.py`
- `apps/obsidia_api/routes/brody.py`
- `periphery/brody_memory_readonly/memory_pipeline_freeze_v2_readonly/brody_memory_pipeline_freeze_v2_readonly.py`
- `apps/obsidia_api/brody_candidate_memory_adapter.py`
- `apps/obsidia_api/brody_memory_promotion_guard.py`
- `scripts/f23a_to_f27_reflex_automation_protocol_audit.py`
- `apps/obsidia_api/brody_freeze_metrics_snapshot.py`
- `apps/obsidia_api/brody_machination_composer.py`
- `apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py`
- `periphery/brody_memory_readonly/memory_pipeline_freeze_v2_readonly/BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_MANIFEST.json`
- `periphery/brody_memory_readonly/memory_pipeline_v2_close_report_readonly/README_BOUNDARY.md`
- `periphery/brody_memory_readonly/memory_pipeline_v2_close_report_readonly/brody_memory_pipeline_v2_close_report_readonly.py`
- `periphery/brody_memory_readonly/memory_readonly_micro_smoke/brody_memory_readonly_micro_smoke_v1.py`
- `periphery/brody_memory_readonly/memory_scheduler_readonly/brody_memory_scheduler_readonly_v1.py`
- `periphery/brody_memory_readonly/readonly_session_test/brody_readonly_session_test_v1.py`
- `periphery/brody_memory_readonly/session_close_human_validation_gate_readonly/brody_session_close_human_validation_gate_readonly_v1.py`
- `periphery/brody_memory_readonly/session_presave_buffer_readonly/brody_session_presave_buffer_readonly_v1.py`
- `periphery/brody_memory_readonly/session_reopen_loop_readonly/brody_session_reopen_loop_readonly_v1.py`
- `apps/obsidia_api/brody_session_memory_adapter.py`
- `apps/obsidia_api/brody_cognitive_modules_adapter.py`
- `apps/obsidia_api/brody_operator_view_packet.py`
- `apps/obsidia_api/brody_runtime_context_adapter.py`
- `apps/obsidia_api/brody_semantic_query_router.py`
- `apps/obsidia_api/brody_temporal_context_adapter.py`

## Risky write hits

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

## Top candidates

### apps/obsidia_api/brody_automation_orchestrator.py
- families: ['automation_orchestrator', 'kx108_boundary', 'memory_pipeline', 'operator_loop', 'reflex', 'session_buffer']
- hit_count: 42
- forbidden_write_hits: []
  - L2 [orchestrator] Brody Automation Layer Orchestrator — Readonly
  - L16 [memory_write]   readonly=True, memory_write=False, graphiti_write=False,
  - L17 [KX108_ONLY]   neo4j_write=False, emits_act=False, decision_authority=KX108_ONLY
  - L37 [memory_write]     "memory_write": False,
  - L38 [graphiti_write]     "graphiti_write": False,
  - L40 [kernel_mutation]     "kernel_mutation": False,
  - L41 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L54 [fallback] # ── Module imports — graceful fallback if unavailable ───────────────────────

### apps/obsidia_api/brody_full_runtime_orchestrator.py
- families: ['automation_orchestrator', 'kx108_boundary', 'session_buffer']
- hit_count: 14
- forbidden_write_hits: []
  - L2 [orchestrator] BRODY FULL RUNTIME ORCHESTRATOR — V5B+
  - L5 [KX108_ONLY] Never emits ACT. KX108_ONLY always.
  - L46 [session_presave]     _PRESAVE = _PRESAVE or _si(P + "session_presave_buffer_readonly.brody_session_presave_buffer_readonly_v1")
  - L74 [KX108_ONLY]         "decision_authority": "KX108_ONLY",
  - L75 [graphiti_write]         "graphiti_write": False,
  - L76 [memory_write]         "memory_write": False,
  - L79 [kernel_mutation]         "kernel_mutation": False,
  - L80 [x108_mutation]         "x108_mutation": False,

### apps/obsidia_api/routes/brody.py
- families: ['automation_orchestrator', 'candidate_memory', 'kx108_boundary', 'memory_promotion_guard', 'operator_loop']
- hit_count: 41
- forbidden_write_hits: []
  - L14 [candidate_memory] from apps.obsidia_api.brody_candidate_memory_adapter import build_candidate_memory_snapshot
  - L15 [operator_loop] from apps.obsidia_api.brody_operator_loop_adapter import build_operator_loop_snapshot
  - L24 [automation_orchestrator] from apps.obsidia_api.brody_automation_orchestrator import run_brody_automation_layer
  - L40 [memory_promotion_guard] from apps.obsidia_api.brody_memory_promotion_guard import build_memory_promotion_guard_packet
  - L47 [pattern] FOLLOWUP_PATTERNS = [
  - L58 [pattern]     if any(p in msg_lower for p in FOLLOWUP_PATTERNS):
  - L150 [KX108_ONLY]         raw_final_answer = v1412a_final or response_md or "Brody - reponse structurelle indisponible. KX108_ONLY."
  - L159 [candidate_memory]     cand_snap = safe_call_snapshot("candidate_memory", build_candidate_memory_snapshot)

### periphery/brody_memory_readonly/memory_pipeline_freeze_v2_readonly/brody_memory_pipeline_freeze_v2_readonly.py
- families: ['kx108_boundary', 'memory_pipeline', 'reflex', 'session_buffer']
- hit_count: 25
- forbidden_write_hits: []
  - L18 [kernel_mutation]     "kernel_mutation": False,
  - L21 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L23 [memory_pipeline]     "brody_role": "MEMORY_PIPELINE_FREEZE_V2_READONLY",
  - L28 [memory_pipeline]     "CURRENT_BRODY_MEMORY_PIPELINE_READONLY_FREEZE_REPORT_V1_VALIDATE.txt",
  - L30 [session_presave]     "CURRENT_BRODY_SESSION_PRESAVE_BUFFER_READONLY.txt",
  - L47 [memory_pipeline]     "BRODY_MEMORY_PIPELINE_READONLY_FREEZE_REPORT_V1_VALIDATE",
  - L49 [session_presave]     "BRODY_SESSION_PRESAVE_BUFFER_READONLY",
  - L149 [reflex]                 "historical_reflex_trace": r["name"] in ALLOWED_HISTORICAL_FAILED_POINTERS,

### apps/obsidia_api/brody_candidate_memory_adapter.py
- families: ['candidate_memory', 'kx108_boundary', 'session_buffer']
- hit_count: 12
- forbidden_write_hits: []
  - L4 [candidate_memory] Wraps existing freeze-sourced modules into a candidate_memory_snapshot.
  - L7 [session_presave]   - session_presave_buffer_readonly V1
  - L13 [memory_write] All writes disabled: CANDIDATE_ONLY, memory_write=false.
  - L14 [KX108_ONLY] Boundary: readonly, KX108_ONLY.
  - L28 [candidate_memory] def build_candidate_memory_snapshot(
  - L31 [candidate_memory]     """Build candidate_memory_snapshot from existing freeze sources."""
  - L35 [session_presave]     presave_ptr = workspace / "CURRENT_BRODY_SESSION_PRESAVE_BUFFER_READONLY.txt"
  - L80 [candidate_memory]         "status": "CANDIDATE_MEMORY_READY" if all_ready else "CANDIDATE_MEMORY_PARTIAL",

### apps/obsidia_api/brody_memory_promotion_guard.py
- families: ['candidate_memory', 'kx108_boundary', 'memory_promotion_guard']
- hit_count: 12
- forbidden_write_hits: []
  - L7 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L13 [memory_write]     "memory_write": False,
  - L14 [graphiti_write]     "graphiti_write": False,
  - L18 [kernel_mutation]     "kernel_mutation": False,
  - L19 [x108_mutation]     "x108_mutation": False,
  - L57 [memory_promotion_guard] def build_memory_promotion_guard_packet(
  - L66 [candidate_memory]     candidate_memory: dict[str, Any] | None = None,
  - L74 [candidate_memory]     cand = candidate_memory if isinstance(candidate_memory, dict) else {}

### scripts/f23a_to_f27_reflex_automation_protocol_audit.py
- families: ['automation_orchestrator', 'avdr_phase', 'kx108_boundary', 'memory_pipeline', 'memory_promotion_guard', 'readonly_context', 'reflex']
- hit_count: 66
- forbidden_write_hits: []
  - L1 [reflex] """F23A→F27 — Memory Reflex / Automation / Dormant Protocol Audit.
  - L4 [reflex]   F23A  Memory Reflex / Automation / Dormant Protocol
  - L5 [reflex]   F23B  Memory Reflex Context Pack Readiness
  - L13 [KX108_ONLY] Constraint: KX108_ONLY / readonly / emits_act=False / emits_verdict=False
  - L14 [memory_write]             memory_write=False / graphiti_write=False
  - L15 [kernel_mutation]             kernel_mutation=False / x108_mutation=False
  - L18 [reflex]     python scripts/f23a_to_f27_reflex_automation_protocol_audit.py
  - L21 [reflex]     OBSIDIA_F23A_TO_F27_REFLEX_AUTOMATION_PROTOCOL_AUDIT_<timestamp>.md

### apps/obsidia_api/brody_freeze_metrics_snapshot.py
- families: ['kx108_boundary', 'memory_pipeline', 'operator_loop', 'session_buffer']
- hit_count: 22
- forbidden_write_hits: []
  - L17 [KX108_ONLY] Boundary: readonly, KX108_ONLY, no write, no decision.
  - L102 [memory_pipeline]     context_packet_chain, memory_pipeline, operator_loop, x108_boundary,
  - L117 [pattern]     for pattern in ["CURRENT_X108_*.txt", "CURRENT_GRAPHITI_*.txt", "CURRENT_MEMORY_*.txt"]:
  - L118 [pattern]         for p in sorted(workspace.glob(pattern)):
  - L146 [session_presave]     presave_buffer_status = _metric_value(parsed, "SESSION_PRESAVE_BUFFER", "STATUS", "NOT_FOUND")
  - L152 [memory_write]     memory_write_val = _metric_value(parsed, "SESSION_MEMORY_LEDGER", "MEMORY_INTAKE", False)
  - L153 [graphiti_write]     graphiti_write_val = _metric_value(parsed, "AUTO_TRIAGE", "GRAPHITI_INDEX_WRITE", False)
  - L156 [memory_pipeline]     memory_pipeline: dict[str, Any] = {

### apps/obsidia_api/brody_machination_composer.py
- families: ['candidate_memory', 'kx108_boundary', 'operator_loop', 'readonly_context']
- hit_count: 20
- forbidden_write_hits: []
  - L96 [memory_write]     if any(flag in flags for flag in ("write_request", "memory_write_request", "graphiti_write_request", "canon_promotion_request")):
  - L117 [memory_write]         "NO_MEMORY_WRITE",
  - L118 [graphiti_write]         "NO_GRAPHITI_WRITE",
  - L119 [kernel_mutation]         "NO_KERNEL_MUTATION",
  - L120 [x108_mutation]         "NO_X108_MUTATION",
  - L121 [KX108_ONLY]         "DECISION_AUTHORITY_KX108_ONLY",
  - L123 [memory_write]     if any(flag in flags for flag in ("action_request", "mutation_request", "write_request", "memory_write_request", "graphiti_write_request", "canon_promotion_request")):
  - L137 [KX108_ONLY]         {"kind": "boundary", "value": "KX108_ONLY", "source": "BRODY_NATIVE_COMPOSER"},

### apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py
- families: ['kx108_boundary', 'memory_pipeline', 'operator_loop', 'readonly_context']
- hit_count: 62
- forbidden_write_hits: []
  - L15 [memory_write]   memory_write=False, kernel_mutation=False,
  - L16 [KX108_ONLY]   decision_authority=KX108_ONLY
  - L29 [memory_write]     MEMORY_WRITE_REQUEST,
  - L57 [fallback] # ── Fallback detectors (ported from V1.4.12A source) ────────────────────────
  - L90 [fallback]     # Fallback: inline port
  - L166 [KX108_ONLY]         "- DECISION_AUTHORITY=KX108_ONLY\n"
  - L194 [kernel_mutation]         "- KERNEL_MUTATION=false\n"
  - L195 [KX108_ONLY]         "- DECISION_AUTHORITY=KX108_ONLY\n"

### periphery/brody_memory_readonly/memory_pipeline_freeze_v2_readonly/BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_MANIFEST.json
- families: ['kx108_boundary', 'memory_pipeline', 'reflex']
- hit_count: 9
- forbidden_write_hits: []
  - L2 [memory_pipeline]     "name":  "BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY",
  - L3 [reflex]     "version":  "v2_1_reflex_failed_pointer_allowlist",
  - L6 [memory_pipeline]     "script":  "C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\periphery\\brody_memory_readonly\\memory_pipeline_freeze_v2_readonly\\brody_memory_pipeline_freeze_v2_readonly.py",
  - L7 [memory_pipeline]     "runner":  "C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\periphery\\brody_memory_readonly\\memory_pipeline_freeze_v2_readonly\\run_brody_memory_pipeline_freeze_v2_readonly.ps1",
  - L8 [memory_pipeline]     "readme":  "C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\periphery\\brody_memory_readonly\\memory_pipeline_freeze_v2_readonly\\README_BOUNDARY.md",
  - L17 [KX108_ONLY]     "decision_authority":  "KX108_ONLY",
  - L18 [kernel_mutation]     "kernel_mutation":  false,
  - L22 [memory_pipeline]     "next":  "VALIDATE_BRODY_MEMORY_PIPELINE_FREEZE_V2_1_READONLY",

### periphery/brody_memory_readonly/memory_pipeline_v2_close_report_readonly/README_BOUNDARY.md
- families: ['kx108_boundary', 'memory_pipeline', 'session_buffer']
- hit_count: 2
- forbidden_write_hits: []
  - L28 [KX108_ONLY] - Decision authority: KX108_ONLY
  - L32 [session_reopen] MICRO_SMOKE_BRODY_MEMORY_READONLY_THEN_BUILD_SESSION_REOPEN_LOOP

### periphery/brody_memory_readonly/memory_pipeline_v2_close_report_readonly/brody_memory_pipeline_v2_close_report_readonly.py
- families: ['kx108_boundary', 'memory_pipeline', 'session_buffer']
- hit_count: 19
- forbidden_write_hits: []
  - L20 [kernel_mutation]     "kernel_mutation": False,
  - L23 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L25 [memory_pipeline]     "brody_role": "MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY",
  - L30 [memory_pipeline]     "CURRENT_BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_VALIDATE.txt",
  - L42 [memory_pipeline]     "CURRENT_BRODY_MEMORY_PIPELINE_READONLY_FREEZE_REPORT_V1_VALIDATE.txt",
  - L46 [memory_pipeline]     "CURRENT_BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_VALIDATE.txt": "BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_VALIDATE_PASS",
  - L57 [memory_pipeline]     "CURRENT_BRODY_MEMORY_PIPELINE_READONLY_FREEZE_REPORT_V1_VALIDATE.txt": "BRODY_MEMORY_PIPELINE_READONLY_FREEZE_REPORT_V1_VALIDATE_PASS",
  - L158 [memory_pipeline]     freeze_v2 = loaded_summaries.get("CURRENT_BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_VALIDATE.txt", {})

### periphery/brody_memory_readonly/memory_readonly_micro_smoke/brody_memory_readonly_micro_smoke_v1.py
- families: ['kx108_boundary', 'memory_pipeline', 'session_buffer']
- hit_count: 5
- forbidden_write_hits: []
  - L20 [kernel_mutation]     "kernel_mutation": False,
  - L23 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L111 [kernel_mutation]             "kernel_mutation": props.get("kernel_mutation"),
  - L127 [memory_pipeline]     close_ptr = workspace_root / "CURRENT_BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_VALIDATE.txt"
  - L261 [session_reopen]         "next": "BUILD_BRODY_SESSION_REOPEN_LOOP_READONLY_V1",

### periphery/brody_memory_readonly/memory_scheduler_readonly/brody_memory_scheduler_readonly_v1.py
- families: ['kx108_boundary', 'memory_pipeline', 'session_buffer']
- hit_count: 31
- forbidden_write_hits: []
  - L23 [kernel_mutation]     "kernel_mutation": False,
  - L26 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L68 [session_reopen]             "source": "BRODY_SESSION_REOPEN_LOOP_READONLY_V1",
  - L69 [session_reopen]             "required_pointer": "CURRENT_BRODY_SESSION_REOPEN_LOOP_READONLY_V1_VALIDATE.txt",
  - L70 [session_reopen]             "required_status": "BRODY_SESSION_REOPEN_LOOP_READONLY_V1_PASS",
  - L85 [session_reopen]             "id": "BRODY_SCHEDULER_STEP_03_SESSION_REOPEN_LOOP",
  - L86 [session_reopen]             "trigger": "MANUAL_NEW_SESSION_REOPEN",
  - L88 [session_reopen]             "source": "BRODY_SESSION_REOPEN_LOOP_READONLY_V1",

### periphery/brody_memory_readonly/readonly_session_test/brody_readonly_session_test_v1.py
- families: ['kx108_boundary', 'memory_pipeline', 'session_buffer']
- hit_count: 10
- forbidden_write_hits: []
  - L20 [kernel_mutation]     "kernel_mutation": False,
  - L23 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L59 [session_reopen]     reopen_ptr = workspace_root / "CURRENT_BRODY_SESSION_REOPEN_LOOP_READONLY_V1_VALIDATE.txt"
  - L61 [memory_pipeline]     close_ptr = workspace_root / "CURRENT_BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_VALIDATE.txt"
  - L149 [session_reopen]         reopen_summary.get("status") == "BRODY_SESSION_REOPEN_LOOP_READONLY_V1_PASS",
  - L164 [memory_pipeline]         close_summary.get("status") == "BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_PASS",
  - L174 [KX108_ONLY]         "DECISION_AUTHORITY=KX108_ONLY" in scheduler_prompt_text,
  - L175 [KX108_ONLY]         "DECISION_AUTHORITY=KX108_ONLY",

### periphery/brody_memory_readonly/session_close_human_validation_gate_readonly/brody_session_close_human_validation_gate_readonly_v1.py
- families: ['kx108_boundary', 'memory_pipeline', 'reflex']
- hit_count: 15
- forbidden_write_hits: []
  - L15 [fallback]     "support_pointer_fallback": True,
  - L22 [kernel_mutation]     "kernel_mutation": False,
  - L25 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L74 [reflex]         return "REFLEX_REVIEW"
  - L79 [memory_pipeline]     if "CURRENT_BRODY_MEMORY_PIPELINE" in name or "FREEZE" in name:
  - L90 [reflex]     if role == "REFLEX_REVIEW":
  - L91 [reflex]         return "REFLEX"
  - L136 [memory_pipeline]         "canonical_source": "BRODY_MEMORY_PIPELINE_POINTER_RECORDS",

### periphery/brody_memory_readonly/session_presave_buffer_readonly/brody_session_presave_buffer_readonly_v1.py
- families: ['kx108_boundary', 'memory_pipeline', 'session_buffer']
- hit_count: 11
- forbidden_write_hits: []
  - L18 [kernel_mutation]     "kernel_mutation": False,
  - L21 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L23 [session_presave]     "brody_role": "SESSION_PRESAVE_BUFFER_READONLY",
  - L38 [memory_pipeline]     "CURRENT_BRODY_MEMORY_PIPELINE_READONLY_FREEZE_REPORT_V1_VALIDATE.txt",
  - L39 [memory_pipeline]     "CURRENT_BRODY_MEMORY_PIPELINE_FREEZE_REPORT_READONLY.txt",
  - L169 [session_presave]     prev = "GENESIS_BRODY_SESSION_PRESAVE_BUFFER_READONLY_V1"
  - L175 [session_presave]     records_jsonl = out_dir / "BRODY_SESSION_PRESAVE_BUFFER_RECORDS.jsonl"
  - L176 [session_presave]     records_json = out_dir / "BRODY_SESSION_PRESAVE_BUFFER_RECORDS.json"

### periphery/brody_memory_readonly/session_reopen_loop_readonly/brody_session_reopen_loop_readonly_v1.py
- families: ['kx108_boundary', 'memory_pipeline', 'session_buffer']
- hit_count: 19
- forbidden_write_hits: []
  - L11 [session_reopen]     "session_reopen_loop": True,
  - L20 [kernel_mutation]     "kernel_mutation": False,
  - L23 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L25 [session_reopen]     "brody_role": "SESSION_REOPEN_LOOP_READONLY",
  - L85 [kernel_mutation]             "kernel_mutation": props.get("kernel_mutation"),
  - L113 [kernel_mutation]             "kernel_mutation": props.get("kernel_mutation"),
  - L129 [memory_pipeline]     close_ptr = workspace_root / "CURRENT_BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_VALIDATE.txt"
  - L190 [session_reopen]         prev = "GENESIS_BRODY_SESSION_REOPEN_LOOP_READONLY_V1"

### apps/obsidia_api/brody_session_memory_adapter.py
- families: ['kx108_boundary', 'session_buffer']
- hit_count: 8
- forbidden_write_hits: []
  - L15 [KX108_ONLY] Boundary: readonly, KX108_ONLY, no write, no Graphiti.
  - L39 [pattern]     patterns = [
  - L47 [pattern]     return any(p in msg for p in patterns)
  - L130 [session_presave]     presave_ptr = workspace / "CURRENT_BRODY_SESSION_PRESAVE_BUFFER_READONLY.txt"
  - L167 [memory_write]         "memory_write": False,
  - L168 [graphiti_write]         "graphiti_write": False,
  - L172 [kernel_mutation]         "kernel_mutation": False,
  - L173 [KX108_ONLY]         "decision_authority": "KX108_ONLY",

### apps/obsidia_api/brody_cognitive_modules_adapter.py
- families: ['avdr_phase', 'candidate_memory', 'kx108_boundary']
- hit_count: 8
- forbidden_write_hits: []
  - L24 [avdr]     {"name": "AVDR", "resolution": "EXACT_FOUND", "covered_by": "avdr_phase_mapper.py", "branchable": True, "active": False},
  - L32 [candidate_memory]     {"name": "Capsule_Evolution", "resolution": "COVERED_BY_EXISTING_MODULE", "covered_by": "temporal_context.future_context, candidate_memory_snapshot", "branchable": True, "active": True},
  - L35 [candidate_memory]     {"name": "Collecteur_Epiphanies", "resolution": "COVERED_BY_EXISTING_MODULE", "covered_by": "candidate_memory_snapshot, presave_buffer, auto_triage", "branchable": True, "active": True},
  - L41 [avdr] _FUTURE_MODULES = ["AVDR", "Capsule_Evolution", "Simulateur_Memoires"]
  - L72 [memory_write]         "memory_write": False,
  - L73 [graphiti_write]         "graphiti_write": False,
  - L77 [kernel_mutation]         "kernel_mutation": False,
  - L78 [KX108_ONLY]         "decision_authority": "KX108_ONLY",

### apps/obsidia_api/brody_operator_view_packet.py
- families: ['kx108_boundary', 'memory_promotion_guard', 'operator_loop']
- hit_count: 10
- forbidden_write_hits: []
  - L7 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L13 [memory_write]     "memory_write": False,
  - L14 [graphiti_write]     "graphiti_write": False,
  - L18 [kernel_mutation]     "kernel_mutation": False,
  - L19 [x108_mutation]     "x108_mutation": False,
  - L50 [memory_promotion_guard]     memory_promotion_guard_packet: dict[str, Any] | None = None,
  - L58 [memory_promotion_guard]     mgp = memory_promotion_guard_packet if isinstance(memory_promotion_guard_packet, dict) else {}
  - L65 [memory_promotion_guard]     memory_guard_ready = mgp.get("version") == "MEMORY_PROMOTION_GUARD_V1"

### apps/obsidia_api/brody_runtime_context_adapter.py
- families: ['candidate_memory', 'kx108_boundary', 'operator_loop']
- hit_count: 14
- forbidden_write_hits: []
  - L10 [KX108_ONLY] Boundary: readonly, KX108_ONLY.
  - L24 [memory_write]     "memory_write": False,
  - L25 [graphiti_write]     "graphiti_write": False,
  - L29 [kernel_mutation]     "kernel_mutation": False,
  - L30 [x108_mutation]     "x108_mutation": False,
  - L31 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L43 [candidate_memory]     candidate_memory_snapshot: dict[str, Any] | None = None,
  - L44 [operator_loop]     operator_loop_snapshot: dict[str, Any] | None = None,

### apps/obsidia_api/brody_semantic_query_router.py
- families: ['avdr_phase', 'kx108_boundary', 'operator_loop']
- hit_count: 18
- forbidden_write_hits: []
  - L12 [KX108_ONLY] Boundary: readonly, KX108_ONLY.
  - L39 [pattern]     """Repair known UTF-8 mojibake patterns before routing."""
  - L54 [fallback]     # (triggers, topic, semantic_query, primary_query, fallback_queries)
  - L106 [operator_loop]         "OPERATOR_LOOP",
  - L149 [avdr]         "Brody cognitive modules AVDR Continuum Verbatia",
  - L151 [avdr]         ["avdr", "verbatia", "memzum", "cognitive_layers"],
  - L176 [pattern]       2. Match against known topic patterns (first match wins)
  - L177 [fallback]       3. Fallback: extract first 3 meaningful words

### apps/obsidia_api/brody_temporal_context_adapter.py
- families: ['avdr_phase', 'candidate_memory', 'kx108_boundary']
- hit_count: 17
- forbidden_write_hits: []
  - L7 [avdr]   - Candidate memory + AVDR phase (future)
  - L11 [KX108_ONLY] Boundary: readonly, KX108_ONLY.
  - L27 [candidate_memory]     candidate_memory: dict[str, Any] | None = None,
  - L35 [candidate_memory]     cm = candidate_memory or {}
  - L62 [candidate_memory]         "candidate_pipeline_available": cm.get("status", "").startswith("CANDIDATE_MEMORY"),
  - L66 [avdr]         "avdr_phase_available": False,  # AVDR phase mapper requires gencoin sandbox
  - L77 [KX108_ONLY]         "decision_authority": "KX108_ONLY",
  - L80 [memory_write]         "memory_write": False,

### apps/obsidia_api/brody_true_voice_adapter.py
- families: ['avdr_phase', 'kx108_boundary', 'operator_loop']
- hit_count: 40
- forbidden_write_hits: []
  - L24 [KX108_ONLY]   - KX108_ONLY always
  - L34 [memory_write]     MEMORY_WRITE_REQUEST,
  - L120 [fallback]     chain_local_fallback_partial = chain.get("status") == "LOCAL_INDEX_FALLBACK_PARTIAL"
  - L187 [memory_write]     if request_type in (ACTION_OR_ACT_REQUEST, MEMORY_WRITE_REQUEST):
  - L206 [memory_write]     action_boundary_already = request_type in (ACTION_OR_ACT_REQUEST, MEMORY_WRITE_REQUEST)
  - L219 [KX108_ONLY]                 "Je peux seulement exposer la demande comme signal readonly et maintenir KX108_ONLY. "
  - L224 [KX108_ONLY]                 "I can only expose this as a readonly signal and keep KX108_ONLY. "
  - L238 [memory_write]     if project_has_material and request_type not in (ACTION_OR_ACT_REQUEST, MEMORY_WRITE_REQUEST):

### periphery/brody_memory_readonly/auto_triage_memory_intake_readonly/BRODY_AUTO_TRIAGE_MEMORY_INTAKE_READONLY_MANIFEST.json
- families: ['kx108_boundary', 'reflex']
- hit_count: 4
- forbidden_write_hits: []
  - L2 [kernel_mutation]     "kernel_mutation":  false,
  - L17 [reflex]                           "BLOCK_IMMEDIATE":  "forbidden_replaced_by_REFLEX_ALERT_ONLY",
  - L23 [KX108_ONLY]     "decision_authority":  "KX108_ONLY",
  - L31 [reflex]                            "ReflexReducer.py"

### periphery/brody_memory_readonly/auto_triage_memory_intake_readonly/README_BOUNDARY.md
- families: ['kx108_boundary', 'reflex']
- hit_count: 3
- forbidden_write_hits: []
  - L9 [KX108_ONLY] - decision_authority: KX108_ONLY
  - L10 [kernel_mutation] - kernel_mutation: false
  - L23 [reflex] - ReflexReducer -> REFLEX_ALERT_ONLY, never BLOCK authority

### periphery/brody_memory_readonly/auto_triage_memory_intake_readonly/brody_auto_triage_memory_intake_readonly_v1.py
- families: ['kx108_boundary', 'reflex']
- hit_count: 22
- forbidden_write_hits: []
  - L9 [KX108_ONLY] # STANDARD X-108 : Autorité absolue KX108_ONLY renforcée
  - L19 [kernel_mutation]     "kernel_mutation": False,
  - L20 [x108_mutation]     "x108_mutation": False,
  - L25 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L76 [reflex] class ReflexReducer:
  - L79 [kernel_mutation]             "kernel_mutation",
  - L80 [x108_mutation]             "x108_mutation",
  - L85 [graphiti_write]             "graphiti_write",

### periphery/brody_memory_readonly/brody_agent_readonly_session_test_packet/brody_agent_readonly_session_test_packet_v1.py
- families: ['kx108_boundary', 'session_buffer']
- hit_count: 6
- forbidden_write_hits: []
  - L20 [kernel_mutation]     "kernel_mutation": False,
  - L23 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L56 [session_reopen]     reopen_ptr = workspace_root / "CURRENT_BRODY_SESSION_REOPEN_LOOP_READONLY_V1_VALIDATE.txt"
  - L106 [session_reopen]     add_check("reopen_status", reopen.get("status") == "BRODY_SESSION_REOPEN_LOOP_READONLY_V1_PASS", "BRODY_SESSION_REOPEN_LOOP_READONLY_V1_PASS", reopen.get("status"))
  - L156 [kernel_mutation] NO_KERNEL_MUTATION=<true/false>
  - L171 [kernel_mutation]             "NO_KERNEL_MUTATION",

### periphery/brody_memory_readonly/brody_api_bridge_contract_readonly/README_BOUNDARY.md
- families: ['kx108_boundary', 'readonly_context']
- hit_count: 1
- forbidden_write_hits: []
  - L30 [KX108_ONLY] - Decision authority: KX108_ONLY

### periphery/brody_memory_readonly/brody_api_bridge_readiness_readonly/README_BOUNDARY.md
- families: ['kx108_boundary', 'readonly_context']
- hit_count: 1
- forbidden_write_hits: []
  - L19 [KX108_ONLY] - decision_authority: KX108_ONLY

### periphery/brody_memory_readonly/brody_api_memory_operator_replay_api_fix_v2_readonly/api_endpoints/context_canon.json
- families: ['avdr_phase', 'readonly_context']
- hit_count: 9
- forbidden_write_hits: []
  - L21 [avdr]                                          "AVDR: CANON_GUARDIAN verifies name collisions for AVDR.",
  - L38 [avdr]                                                 "name":  "AVDR",
  - L39 [avdr]                                                 "summary":  "CANON_GUARDIAN verifies name collisions for AVDR."
  - L76 [avdr]                          "name":  "AVDR",
  - L77 [avdr]                          "summary":  "CANON_GUARDIAN verifies name collisions for AVDR."
  - L112 [avdr]                                  "name":  "AVDR",
  - L113 [avdr]                                  "summary":  "CANON_GUARDIAN verifies name collisions for AVDR."
  - L159 [avdr]                                                     "name":  "AVDR",

### periphery/brody_memory_readonly/brody_api_memory_operator_replay_api_fix_v2_readonly/api_endpoints/context_x108.json
- families: ['avdr_phase', 'readonly_context']
- hit_count: 5
- forbidden_write_hits: []
  - L17 [avdr]                                          "CANON_GUARDIAN: CANON_GUARDIAN has Vertex AI as a deployment option.\nCANON_GUARDIAN belongs to the \u0027Ã crÃ©er en premier / Top 5 founders\u0027 family of agents.\nCANON_GUARDIAN is deployed on Vertex AI or locally.\nCANON_GUARDIAN has the Claude Code skill \u0027freeze-guardian (reduced)\u0027.\nThe freeze-guar
  - L26 [avdr]                                                 "summary":  "CANON_GUARDIAN has Vertex AI as a deployment option.\nCANON_GUARDIAN belongs to the \u0027Ã crÃ©er en premier / Top 5 founders\u0027 family of agents.\nCANON_GUARDIAN is deployed on Vertex AI or locally.\nCANON_GUARDIAN has the Claude Code skill \u0027freeze-guardian (reduced)\u0027.\nThe freeze-g
  - L37 [avdr]                          "summary":  "CANON_GUARDIAN has Vertex AI as a deployment option.\nCANON_GUARDIAN belongs to the \u0027Ã crÃ©er en premier / Top 5 founders\u0027 family of agents.\nCANON_GUARDIAN is deployed on Vertex AI or locally.\nCANON_GUARDIAN has the Claude Code skill \u0027freeze-guardian (reduced)\u0027.\nThe freeze-guardian Claude Code ski
  - L46 [avdr]                                  "summary":  "CANON_GUARDIAN has Vertex AI as a deployment option.\nCANON_GUARDIAN belongs to the \u0027Ã crÃ©er en premier / Top 5 founders\u0027 family of agents.\nCANON_GUARDIAN is deployed on Vertex AI or locally.\nCANON_GUARDIAN has the Claude Code skill \u0027freeze-guardian (reduced)\u0027.\nThe freeze-guardian Claude 
  - L66 [avdr]                                                     "summary":  "CANON_GUARDIAN has Vertex AI as a deployment option.\nCANON_GUARDIAN belongs to the \u0027Ã crÃ©er en premier / Top 5 founders\u0027 family of agents.\nCANON_GUARDIAN is deployed on Vertex AI or locally.\nCANON_GUARDIAN has the Claude Code skill \u0027freeze-guardian (reduced)\u0027.\nThe free

### periphery/brody_memory_readonly/brody_api_memory_operator_replay_readonly/reports/api_memory_operator_replay_report.json
- families: ['kx108_boundary', 'readonly_context']
- hit_count: 3
- forbidden_write_hits: []
  - L17 [graphiti_write]     "graphiti_write":  false,
  - L25 [KX108_ONLY]     "decision_authority":  "KX108_ONLY",
  - L26 [kernel_mutation]     "kernel_mutation":  false,

### periphery/brody_memory_readonly/brody_memory_context_operator_interaction_test_readonly_freeze_v1/api_endpoints/context_canon.json
- families: ['avdr_phase', 'readonly_context']
- hit_count: 9
- forbidden_write_hits: []
  - L21 [avdr]                                          "AVDR: CANON_GUARDIAN verifies name collisions for AVDR.",
  - L38 [avdr]                                                 "name":  "AVDR",
  - L39 [avdr]                                                 "summary":  "CANON_GUARDIAN verifies name collisions for AVDR."
  - L76 [avdr]                          "name":  "AVDR",
  - L77 [avdr]                          "summary":  "CANON_GUARDIAN verifies name collisions for AVDR."
  - L112 [avdr]                                  "name":  "AVDR",
  - L113 [avdr]                                  "summary":  "CANON_GUARDIAN verifies name collisions for AVDR."
  - L159 [avdr]                                                     "name":  "AVDR",

### periphery/brody_memory_readonly/brody_memory_context_operator_interaction_test_readonly_freeze_v1/api_endpoints/context_kernel.json
- families: ['avdr_phase', 'readonly_context']
- hit_count: 5
- forbidden_write_hits: []
  - L17 [avdr]                                          "CANON_GUARDIAN: CANON_GUARDIAN has Vertex AI as a deployment option.\nCANON_GUARDIAN belongs to the \u0027Ã crÃ©er en premier / Top 5 founders\u0027 family of agents.\nCANON_GUARDIAN is deployed on Vertex AI or locally.\nCANON_GUARDIAN has the Claude Code skill \u0027freeze-guardian (reduced)\u0027.\nThe freeze-guar
  - L29 [avdr]                                                 "summary":  "CANON_GUARDIAN has Vertex AI as a deployment option.\nCANON_GUARDIAN belongs to the \u0027Ã crÃ©er en premier / Top 5 founders\u0027 family of agents.\nCANON_GUARDIAN is deployed on Vertex AI or locally.\nCANON_GUARDIAN has the Claude Code skill \u0027freeze-guardian (reduced)\u0027.\nThe freeze-g
  - L56 [avdr]                          "summary":  "CANON_GUARDIAN has Vertex AI as a deployment option.\nCANON_GUARDIAN belongs to the \u0027Ã crÃ©er en premier / Top 5 founders\u0027 family of agents.\nCANON_GUARDIAN is deployed on Vertex AI or locally.\nCANON_GUARDIAN has the Claude Code skill \u0027freeze-guardian (reduced)\u0027.\nThe freeze-guardian Claude Code ski
  - L81 [avdr]                                  "summary":  "CANON_GUARDIAN has Vertex AI as a deployment option.\nCANON_GUARDIAN belongs to the \u0027Ã crÃ©er en premier / Top 5 founders\u0027 family of agents.\nCANON_GUARDIAN is deployed on Vertex AI or locally.\nCANON_GUARDIAN has the Claude Code skill \u0027freeze-guardian (reduced)\u0027.\nThe freeze-guardian Claude 
  - L117 [avdr]                                                     "summary":  "CANON_GUARDIAN has Vertex AI as a deployment option.\nCANON_GUARDIAN belongs to the \u0027Ã crÃ©er en premier / Top 5 founders\u0027 family of agents.\nCANON_GUARDIAN is deployed on Vertex AI or locally.\nCANON_GUARDIAN has the Claude Code skill \u0027freeze-guardian (reduced)\u0027.\nThe free

### periphery/brody_memory_readonly/brody_memory_context_operator_interaction_test_readonly_freeze_v1/api_endpoints/context_x108.json
- families: ['avdr_phase', 'readonly_context']
- hit_count: 5
- forbidden_write_hits: []
  - L17 [avdr]                                          "CANON_GUARDIAN: CANON_GUARDIAN has Vertex AI as a deployment option.\nCANON_GUARDIAN belongs to the \u0027Ã crÃ©er en premier / Top 5 founders\u0027 family of agents.\nCANON_GUARDIAN is deployed on Vertex AI or locally.\nCANON_GUARDIAN has the Claude Code skill \u0027freeze-guardian (reduced)\u0027.\nThe freeze-guar
  - L26 [avdr]                                                 "summary":  "CANON_GUARDIAN has Vertex AI as a deployment option.\nCANON_GUARDIAN belongs to the \u0027Ã crÃ©er en premier / Top 5 founders\u0027 family of agents.\nCANON_GUARDIAN is deployed on Vertex AI or locally.\nCANON_GUARDIAN has the Claude Code skill \u0027freeze-guardian (reduced)\u0027.\nThe freeze-g
  - L37 [avdr]                          "summary":  "CANON_GUARDIAN has Vertex AI as a deployment option.\nCANON_GUARDIAN belongs to the \u0027Ã crÃ©er en premier / Top 5 founders\u0027 family of agents.\nCANON_GUARDIAN is deployed on Vertex AI or locally.\nCANON_GUARDIAN has the Claude Code skill \u0027freeze-guardian (reduced)\u0027.\nThe freeze-guardian Claude Code ski
  - L46 [avdr]                                  "summary":  "CANON_GUARDIAN has Vertex AI as a deployment option.\nCANON_GUARDIAN belongs to the \u0027Ã crÃ©er en premier / Top 5 founders\u0027 family of agents.\nCANON_GUARDIAN is deployed on Vertex AI or locally.\nCANON_GUARDIAN has the Claude Code skill \u0027freeze-guardian (reduced)\u0027.\nThe freeze-guardian Claude 
  - L66 [avdr]                                                     "summary":  "CANON_GUARDIAN has Vertex AI as a deployment option.\nCANON_GUARDIAN belongs to the \u0027Ã crÃ©er en premier / Top 5 founders\u0027 family of agents.\nCANON_GUARDIAN is deployed on Vertex AI or locally.\nCANON_GUARDIAN has the Claude Code skill \u0027freeze-guardian (reduced)\u0027.\nThe free

### periphery/brody_memory_readonly/candidate_export_for_graphiti_readonly/brody_candidate_export_for_graphiti_readonly_v1.py
- families: ['kx108_boundary', 'reflex']
- hit_count: 11
- forbidden_write_hits: []
  - L18 [kernel_mutation]     "kernel_mutation": False,
  - L19 [x108_mutation]     "x108_mutation": False,
  - L24 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L76 [reflex]             if "REFLEX" in up or "RÉFLEX" in up:
  - L77 [reflex]                 return "REFLEX"
  - L86 [reflex]     if "REFLEX" in raw or "RÉFLEX" in raw:
  - L87 [reflex]         return "REFLEX"
  - L178 [KX108_ONLY]         "decision_authority": "KX108_ONLY",

### periphery/brody_memory_readonly/graphiti_review_decision_apply_readonly/brody_graphiti_review_decision_apply_readonly_v1.py
- families: ['kx108_boundary', 'reflex']
- hit_count: 11
- forbidden_write_hits: []
  - L19 [kernel_mutation]     "kernel_mutation": False,
  - L22 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L28 [reflex] VALID_DECISIONS = {"KEEP", "TRANSITION", "NEANT", "REFLEX"}
  - L102 [reflex]     if decision == "REFLEX":
  - L103 [reflex]         return "REFLEX_ALERT_IMPORT_TRACE"
  - L220 [reflex]     reflex = [r for r in records if r["human_decision"] == "REFLEX"]
  - L227 [reflex]     reflex_jsonl = out_dir / "BRODY_GRAPHITI_REVIEW_REFLEX_RECORDS.jsonl"
  - L239 [reflex]     write_jsonl(reflex_jsonl, reflex)

### periphery/brody_memory_readonly/graphiti_review_gate_from_post_human_dry_run_readonly/brody_graphiti_review_gate_from_post_human_dry_run_readonly_v1.py
- families: ['kx108_boundary', 'reflex']
- hit_count: 5
- forbidden_write_hits: []
  - L22 [kernel_mutation]     "kernel_mutation": False,
  - L25 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L245 [reflex]         "- REFLEX = alert / weak signal",
  - L261 [reflex]             "- question: **KEEP / TRANSITION / NEANT / REFLEX ?**",
  - L262 [reflex]             "- decision: `[ ] KEEP  [ ] TRANSITION  [ ] NEANT  [ ] REFLEX`",

### periphery/brody_memory_readonly/memory_layer_authority_model_readonly/MEMORY_LAYER_AUTHORITY_MODEL_READONLY_MANIFEST.json
- families: ['kx108_boundary', 'readonly_context']
- hit_count: 2
- forbidden_write_hits: []
  - L30 [KX108_ONLY]     "decision_authority":  "KX108_ONLY",
  - L31 [kernel_mutation]     "kernel_mutation":  false,

### periphery/brody_memory_readonly/memory_layer_authority_model_readonly/README_BOUNDARY.md
- families: ['kx108_boundary', 'readonly_context']
- hit_count: 3
- forbidden_write_hits: []
  - L58 [KX108_ONLY] - Final decision authority: KX108_ONLY
  - L67 [KX108_ONLY] - DECISION_AUTHORITY=KX108_ONLY
  - L68 [kernel_mutation] - KERNEL_MUTATION=false

### periphery/brody_memory_readonly/memory_pipeline_freeze_report_readonly/BRODY_MEMORY_PIPELINE_FREEZE_REPORT_READONLY_MANIFEST.json
- families: ['kx108_boundary', 'memory_pipeline']
- hit_count: 3
- forbidden_write_hits: []
  - L2 [memory_pipeline]   "status": "BRODY_MEMORY_PIPELINE_FREEZE_REPORT_READONLY_READY",
  - L10 [KX108_ONLY]   "decision_authority": "KX108_ONLY",
  - L11 [kernel_mutation]   "kernel_mutation": false,

### periphery/brody_memory_readonly/memory_pipeline_freeze_report_readonly/README_BOUNDARY.md
- families: ['kx108_boundary', 'memory_pipeline']
- hit_count: 1
- forbidden_write_hits: []
  - L13 [KX108_ONLY] Autorité décisionnelle : KX108_ONLY.

### periphery/brody_memory_readonly/memory_pipeline_freeze_report_readonly/brody_memory_pipeline_freeze_report_readonly_v1.py
- families: ['kx108_boundary', 'memory_pipeline']
- hit_count: 8
- forbidden_write_hits: []
  - L18 [kernel_mutation]     "kernel_mutation": False,
  - L19 [x108_mutation]     "x108_mutation": False,
  - L26 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L27 [memory_pipeline]     "brody_role": "MEMORY_PIPELINE_FREEZE_REPORT_READONLY",
  - L145 [memory_pipeline]         "status": "BRODY_MEMORY_PIPELINE_FREEZE_REPORT_READONLY_PASS",
  - L162 [memory_pipeline]     json_path = out_dir / "BRODY_MEMORY_PIPELINE_FREEZE_REPORT_SUMMARY.json"
  - L163 [memory_pipeline]     records_path = out_dir / "BRODY_MEMORY_PIPELINE_POINTER_RECORDS.json"
  - L164 [memory_pipeline]     md_path = out_dir / "BRODY_MEMORY_PIPELINE_FREEZE_REPORT.md"

### periphery/brody_memory_readonly/memory_pipeline_freeze_v2_readonly/README_BOUNDARY.md
- families: ['memory_pipeline', 'reflex']
- hit_count: 3
- forbidden_write_hits: []
  - L44 [memory_pipeline] REVIEW_THEN_COMMIT_BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY
  - L46 [reflex] ## V2_1_REFLEX_FAILED_POINTER_ALLOWLIST
  - L48 [reflex] The following old Neo4j smoke failure pointers are preserved as historical reflex traces:

### periphery/brody_memory_readonly/memory_pipeline_v2_close_report_readonly/BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_MANIFEST.json
- families: ['kx108_boundary', 'memory_pipeline']
- hit_count: 7
- forbidden_write_hits: []
  - L2 [memory_pipeline]     "name":  "BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY",
  - L6 [memory_pipeline]     "script":  "C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\periphery\\brody_memory_readonly\\memory_pipeline_v2_close_report_readonly\\brody_memory_pipeline_v2_close_report_readonly.py",
  - L7 [memory_pipeline]     "runner":  "C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\periphery\\brody_memory_readonly\\memory_pipeline_v2_close_report_readonly\\run_brody_memory_pipeline_v2_close_report_readonly.ps1",
  - L8 [memory_pipeline]     "readme":  "C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\periphery\\brody_memory_readonly\\memory_pipeline_v2_close_report_readonly\\README_BOUNDARY.md",
  - L18 [KX108_ONLY]     "decision_authority":  "KX108_ONLY",
  - L19 [kernel_mutation]     "kernel_mutation":  false,
  - L23 [memory_pipeline]     "next":  "VALIDATE_BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_V1_1",

### periphery/brody_memory_readonly/post_graphiti_replay_query_regression_readonly/brody_post_graphiti_replay_query_regression_readonly_v1.py
- families: ['kx108_boundary', 'memory_pipeline']
- hit_count: 6
- forbidden_write_hits: []
  - L21 [kernel_mutation]     "kernel_mutation": False,
  - L24 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L109 [kernel_mutation]             "kernel_mutation": props.get("kernel_mutation"),
  - L155 [graphiti_write]     if verify_summary.get("verified_previous_graphiti_write") is not True:
  - L156 [graphiti_write]         raise RuntimeError("PREVIOUS_GRAPHITI_WRITE_NOT_VERIFIED")
  - L261 [memory_pipeline]         "next": "BUILD_BRODY_MEMORY_PIPELINE_FREEZE_V2",

### periphery/brody_memory_readonly/post_human_review_memory_triage_readonly/brody_post_human_review_memory_triage_readonly_v1.py
- families: ['kx108_boundary', 'reflex']
- hit_count: 16
- forbidden_write_hits: []
  - L19 [kernel_mutation]     "kernel_mutation": False,
  - L22 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L173 [reflex]     reflex_jsonl = Path(kv.get("REFLEX_JSONL", ""))
  - L177 [reflex]     required = [decisions_jsonl, keep_jsonl, transition_jsonl, reflex_jsonl, neant_jsonl, source_summary_json]
  - L187 [fallback]     if source_summary.get("gate_patch") != "V1_3_CANONICAL_POINTER_RECORDS_SUPPORT_FALLBACK":
  - L193 [reflex]     reflex_rows = read_jsonl(reflex_jsonl)
  - L213 [reflex]     reflex_records = []
  - L214 [reflex]     for idx, row in enumerate(reflex_rows, start=1):

## Status

F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT_DONE
NEXT=F23A2_REFLEX_ORCHESTRATOR_PLAN_FROM_REAL_PATHS