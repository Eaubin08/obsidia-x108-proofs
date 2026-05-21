# DeepSeek Test Results — Obsidia X-108 V3/V4

**Date:** 2026-05-19
**Python:** 3.13.3
**pytest:** 9.0.3
**Platform:** Windows (win32)

---

## Summary

| Suite | Count | Passed | Failed | Duration |
|-------|-------|--------|--------|----------|
| tests/periphery | 303 | 303 | 0 | 1.30s |
| tests/non_sovereignty | 67 | 67 | 0 | 0.26s |
| tests/integration | 27 | 27 | 0 | 0.31s |
| **Total** | **397** | **397** | **0** | **2.09s** |

---

## Periphery Tests (303 passed)

### Core Governance
- test_action_lifecycle.py
- test_action_sequence_governor.py
- test_agent_contracts.py
- test_agent_registry.py
- test_agent_registry_v3_v4.py
- test_data_gate.py
- test_operational_constance.py
- test_permission_economic.py
- test_provenance_gate.py

### OS3 / ProofOfGovernance
- test_os3_ticket.py
- test_os3_replay_runner.py
- test_proof_of_governance.py
- test_multi_agent_consensus_priority.py
- test_lyapunov_governance_function.py

### Gencoin
- test_gencoin.py
- test_gencoin_debt_model.py
- test_gencoin_distribution_human_priority.py
- test_gencoin_ledger_append_only.py
- test_gencoin_not_token_policy.py
- test_gencoin_sandbox_engine.py
- test_false_on_blocks_gencoin.py
- test_balance_operator.py

### WorldCall / Gateway
- test_world_action_gateway.py
- test_world_action_controlled_runtime_stub.py
- test_world_call_classifier.py
- test_no_ticket_no_world_call.py
- test_gateway_dryrun_only.py

### Blockchain
- test_blockchain_action_classifier.py
- test_wallet_security_gate.py
- test_transaction_simulator_dryrun.py
- test_smart_contract_risk_gate.py
- test_token_policy.py
- test_oracle_freshness_gate.py
- test_bridge_risk_gate.py
- test_signature_boundary_no_signing.py

### Number / Encoding
- test_radix_systems.py
- test_symbolic_number_encoder.py
- test_entropy_estimator.py
- test_compression_score.py
- test_crypto_boundary_no_security_claim.py
- test_diffusion_cost_model.py

### Symbolic Physics
- test_dimensional_hygiene.py
- test_frequency_tag_mapper.py
- test_symbolic_physics_claim_gate.py
- test_unit_consistency_checker.py

### Cognitive Trees
- test_tree_activation_vector.py
- test_dominant_trees_threshold.py
- test_shazam_cognitif_context_only.py

### Reverse OS / BDF / HexaFlux
- test_reverse_os_projection_readonly.py
- test_bdf_router_no_act.py
- test_hexaflux_transition_no_authority.py

### Consciousness
- test_consciousness_regime_classifier.py
- test_consciousness_no_claim_policy.py
- test_collective_sandbox_summary.py

### Memory / Brody / Graphiti
- test_memory_governor.py
- test_memory_source_registry.py
- test_brody_response_contract.py
- test_brody_runtime_readonly.py
- test_graphiti_readonly_bridge.py
- test_interface_state_packet.py
- test_x108_readonly_context_ingress_no_act.py
- test_feedback_memory_bridge_readonly.py
- test_feedback_memory_candidate.py

### Miscellaneous
- test_eml_compression.py
- test_energy_thermo.py
- test_timeverse.py
- test_ocs_generation.py
- test_avdr_phase_mapper.py
- test_benchmark_case_schema.py
- test_bias_gate_blocks_unvalidated_bias.py
- test_document_ingestion_requires_hash.py
- test_education_score.py
- test_github_no_auto_merge.py
- test_language_router_boundary_preserved.py
- test_mcp_tool_access_not_permission.py
- test_hackathon_failure_mapping.py

---

## Non-Sovereignty Tests (67 passed)

**Verified invariants — each test asserts a periphery module CANNOT claim sovereign authority:**

| Invariant | Test File | Tests |
|-----------|-----------|-------|
| Periphery cannot emit ACT | test_periphery_cannot_emit_act.py | 1 |
| Agents cannot emit ACT | test_agents_cannot_emit_act.py | 1 |
| ControlPlane cannot emit ACT | test_control_plane_cannot_emit_act.py | 1 |
| Brody no ACT | test_brody_no_act.py | 1 |
| Brody no decision | test_brody_no_decision.py | 4 |
| Cognitive trees no decision | test_cognitive_trees_no_decision.py | 1 |
| Memory cannot decide | test_memory_cannot_decide.py | 1 |
| Memory promotion not automatic | test_memory_promotion_not_automatic.py | 5 |
| Feedback memory no write | test_feedback_memory_no_write_v3.py | 1 |
| Gencoin cannot authorize | test_gencoin_cannot_authorize.py | 1 |
| Gencoin no authority | test_gencoin_no_authority_v3.py | 1 |
| Sigma cannot bypass X108 | test_sigma_cannot_bypass_x108.py | 1 |
| Energy cannot authorize | test_energy_cannot_authorize.py | 1 |
| Timeverse cannot authorize | test_timeverse_cannot_authorize.py | 1 |
| OC cannot authorize | test_oc_cannot_authorize.py | 1 |
| Graphiti no write | test_graphiti_no_write.py | 5 |
| No private key access | test_no_private_key_access.py | 1 |
| No wallet connection | test_no_wallet_connection.py | 3 |
| No real chain tx | test_no_real_chain_tx.py | 3 |
| No smart contract deploy | test_no_smart_contract_deploy.py | 1 |
| No token mint | test_no_token_mint.py | 1 |
| WorldAction dry-run only | test_world_action_gateway_dry_run.py | 1 |
| WorldAction no real act | test_world_action_no_real_act_v4.py | 1 |
| Agent no direct internet | test_agent_no_direct_internet.py | 1 |

**Key non-sovereignty assertions verified (24-spot-check run):**
```
test_non_sovereign (periphery_cannot_emit_act)   PASSED
test_brody_cannot_decide                         PASSED
test_brody_not_sovereign                         PASSED
test_brody_contract_decision_authority_fixed     PASSED
test_brody_advisory_only                         PASSED
test_non_sovereign (gencoin_cannot_authorize)    PASSED
test_query_no_neo4j_write                        PASSED
test_query_no_graphiti_write                     PASSED
test_assert_no_write_invariant                   PASSED
test_context_adapter_no_write                    PASSED
test_freeze_snapshot_readonly                    PASSED
test_non_sovereign (memory_cannot_decide)        PASSED
test_non_sovereign (sigma_cannot_bypass_x108)    PASSED
test_wallet_connect_blocked                      PASSED
test_walletconnect_variant_blocked               PASSED
test_connect_wallet_blocked                      PASSED
test_simulate_never_broadcasts                   PASSED
test_simulate_testnet_no_broadcast               PASSED
test_simulate_any_chain_no_real_tx               PASSED
test_auto_promotion_blocked                      PASSED
test_auto_promotion_allowed_invariant_violated   PASSED
test_candidate_memory_write_false                PASSED
test_candidate_auto_promotion_false              PASSED
test_promoted_manual_only_needs_human            PASSED
```

---

## Integration Tests (27 passed)

### V3 Full Pipeline (scenario-based)
- test_v3_full_pipeline_bank.py
- test_v3_full_pipeline_gps.py
- test_v3_full_pipeline_trading.py

### V4 Controlled Runtime
- test_v4_controlled_runtime_pipeline.py
- test_v4_sovereign_ticket_os3_pog_chain.py
- test_v4_world_call_gateway_pipeline.py
- test_v4_gencoin_world_action_bus_chain.py

### Sigma Bridges
- test_sigma_bridge_bank.py
- test_sigma_bridge_gps.py
- test_sigma_bridge_trading.py

### Full Stack Static
- test_full_stack_static_bank.py
- test_full_stack_static_gps.py
- test_full_stack_static_trading.py

### Chain Tests
- test_os3_gencoin_chain.py

---

## Syntax Check

`python -m compileall periphery -q` → **no output = zero errors.**

---

## Conclusion

**DEEPSEEK_TEST_RESULTS_PASS** — All 397 tests pass. Zero failures. Zero errors.
