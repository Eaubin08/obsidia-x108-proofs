# Test Results — V3+V4 Patch

**Date:** 2026-05-19
**Total:** 194 passed, 0 failed, 0 errors

## By Suite

### tests/periphery/ — 147 tests PASS

| File | Tests |
|---|---|
| test_agent_registry_v3_v4.py | 6 |
| test_os3_replay_runner.py | 4 |
| test_gencoin_ledger_append_only.py | 3 |
| test_gencoin_debt_model.py | 5 |
| test_gencoin_distribution_human_priority.py | 5 |
| test_feedback_memory_bridge_readonly.py | 5 |
| test_world_action_controlled_runtime_stub.py | 5 |
| test_gencoin_sandbox_engine.py | 6 |
| test_false_on_blocks_gencoin.py | 6 |
| test_balance_operator.py | 4 |
| test_avdr_phase_mapper.py | 5 |
| test_world_call_classifier.py | 6 |
| test_no_ticket_no_world_call.py | 4 |
| test_gateway_dryrun_only.py | 5 |
| test_lyapunov_governance_function.py | 4 |
| test_proof_of_governance.py | 3 |
| test_multi_agent_consensus_priority.py | 4 |
| test_language_router_boundary_preserved.py | 4 |
| test_document_ingestion_requires_hash.py | 4 |
| test_x108_readonly_context_ingress_no_act.py | 4 |
| test_education_score.py | 4 |
| test_bias_gate_blocks_unvalidated_bias.py | 5 |
| test_mcp_tool_access_not_permission.py | 5 |
| test_github_no_auto_merge.py | 6 |
| test_benchmark_case_schema.py | 5 |

### tests/non_sovereignty/ — 20 tests PASS

| File | Tests |
|---|---|
| test_agents_cannot_emit_act.py | 5 |
| test_feedback_memory_no_write_v3.py | 2 |
| test_gencoin_no_authority_v3.py | 4 |
| test_world_action_no_real_act_v4.py | 5 |
| test_agent_no_direct_internet.py | 3 |

### tests/integration/ — 27 tests PASS

| File | Tests |
|---|---|
| test_v3_full_pipeline_bank.py | 3 |
| test_v3_full_pipeline_trading.py | 3 |
| test_v3_full_pipeline_gps.py | 3 |
| test_v4_controlled_runtime_pipeline.py | 3 |
| test_v4_world_call_gateway_pipeline.py | 6 |
| test_v4_sovereign_ticket_os3_pog_chain.py | 5 |
| test_v4_gencoin_world_action_bus_chain.py | 5 |
| test_v4_controlled_runtime_pipeline (prev) | 3 |

## Key Invariants Tested

- `can_emit_act=False` — all peripheral agents (5 direct tests)
- `dry_run_only=True` — world action stub (5 tests)
- `egress_allowed=False` — gateway (6 integration tests)
- `memory_write_allowed=False` — feedback bridge (5 tests)
- `mint_allowed=False` — gencoin no authority (4 tests)
- `FALSE_ON` blocks gencoin — regime truth gate (6 tests)
- No ticket → no world call — gateway (4+6 tests)
