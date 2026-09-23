# F73.1 ? Blocking Risk Classification

- Status: FAIL_RUNTIME_BLOCKERS_REMAIN
- Source audit: `C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\docs\runtime\F73_ADVERSARIAL_HARDENING_ADVANCED_AUDIT_20260530_041156.json`
- Source blocking count: 19
- Runtime blocking count: 1
- Test false-positive candidate count: 2
- Build performed: false
- Patch performed: false
- KX108_ONLY preserved

## Classified blockers

- `REVIEW_NON_RUNTIME_NON_TEST_PATTERN` ? `scripts/audit_f45_canonical_observation_terminal_test_battery.py` ? matches: `['allowed_to_decide\\s*[:=]\\s*True']`
  - line 243: `_warn("F4: CONFIRMED_ARCHITECTURAL — base.update(data) merges correctly for current V1 modules (all module dicts carry correct BOUNDARY). But merge direction is unsafe by design: a future module returning {allowed_to_decide: True} would propagate without resistance. V1 runtime not exploitable via current routes.")`
- `REVIEW_NON_RUNTIME_NON_TEST_PATTERN` ? `scripts/f23a5_0_agents_branch_audit.py` ? matches: `['emits_act\\s*[:=]\\s*True', 'kernel_mutation\\s*[:=]\\s*True', 'x108_mutation\\s*[:=]\\s*True']`
  - line 51: `"emits_act=True",`
  - line 53: `"kernel_mutation=True",`
  - line 54: `"x108_mutation=True",`
- `REVIEW_NON_RUNTIME_NON_TEST_PATTERN` ? `scripts/f23a5_1_agents_validation.py` ? matches: `['emits_act\\s*[:=]\\s*True', 'kernel_mutation\\s*[:=]\\s*True', 'x108_mutation\\s*[:=]\\s*True', 'memory_write\\s*[:=]\\s*True', 'graphiti_write\\s*[:=]\\s*True']`
  - line 26: `"emits_act=True",`
  - line 27: `"memory_write=True",`
  - line 28: `"graphiti_write=True",`
- `REVIEW_NON_RUNTIME_NON_TEST_PATTERN` ? `scripts/f23a6_0_orchestrator_sigma_awareness_audit.py` ? matches: `['emits_act\\s*[:=]\\s*True', 'kernel_mutation\\s*[:=]\\s*True', 'x108_mutation\\s*[:=]\\s*True', 'memory_write\\s*[:=]\\s*True', 'graphiti_write\\s*[:=]\\s*True', 'neo4j_write\\s*[:=]\\s*True']`
  - line 49: `"emits_act=True",`
  - line 51: `"kernel_mutation=True",`
  - line 52: `"x108_mutation=True",`
- `REVIEW_NON_RUNTIME_NON_TEST_PATTERN` ? `scripts/f24_0_deferred_block_audit.py` ? matches: `['emits_act\\s*[:=]\\s*True', 'kernel_mutation\\s*[:=]\\s*True', 'x108_mutation\\s*[:=]\\s*True', 'memory_write\\s*[:=]\\s*True', 'graphiti_write\\s*[:=]\\s*True', 'neo4j_write\\s*[:=]\\s*True']`
  - line 43: `"emits_act=True",`
  - line 45: `"kernel_mutation=True",`
  - line 46: `"x108_mutation=True",`
- `REVIEW_NON_RUNTIME_NON_TEST_PATTERN` ? `scripts/f26_0_monitor_awareness_audit.py` ? matches: `['emits_act\\s*[:=]\\s*True', 'kernel_mutation\\s*[:=]\\s*True', 'x108_mutation\\s*[:=]\\s*True', 'memory_write\\s*[:=]\\s*True', 'graphiti_write\\s*[:=]\\s*True', 'neo4j_write\\s*[:=]\\s*True']`
  - line 41: `"emits_act=True",`
  - line 43: `"kernel_mutation=True",`
  - line 44: `"x108_mutation=True",`
- `REVIEW_NON_RUNTIME_NON_TEST_PATTERN` ? `scripts/f27_0_shazam_cognitif_audit.py` ? matches: `['emits_act\\s*[:=]\\s*True', 'kernel_mutation\\s*[:=]\\s*True', 'x108_mutation\\s*[:=]\\s*True', 'memory_write\\s*[:=]\\s*True', 'graphiti_write\\s*[:=]\\s*True', 'neo4j_write\\s*[:=]\\s*True']`
  - line 39: `"emits_act=True",`
  - line 41: `"kernel_mutation=True",`
  - line 42: `"x108_mutation=True",`
- `REVIEW_NON_RUNTIME_NON_TEST_PATTERN` ? `scripts/f28_1_governed_operator_runtime_audit.py` ? matches: `['emits_act\\s*[:=]\\s*True', 'kernel_mutation\\s*[:=]\\s*True', 'x108_mutation\\s*[:=]\\s*True', 'memory_write\\s*[:=]\\s*True', 'graphiti_write\\s*[:=]\\s*True', 'neo4j_write\\s*[:=]\\s*True']`
  - line 47: `"emits_act=True",`
  - line 49: `"kernel_mutation=True",`
  - line 50: `"x108_mutation=True",`
- `REVIEW_NON_RUNTIME_NON_TEST_PATTERN` ? `scripts/f29_0b_memory_graphiti_danger_classification.py` ? matches: `['emits_act\\s*[:=]\\s*True', 'kernel_mutation\\s*[:=]\\s*True', 'x108_mutation\\s*[:=]\\s*True', 'memory_write\\s*[:=]\\s*True', 'graphiti_write\\s*[:=]\\s*True', 'neo4j_write\\s*[:=]\\s*True']`
  - line 22: `"memory_write=True",`
  - line 23: `"graphiti_write=True",`
  - line 24: `"neo4j_write=True",`
- `REVIEW_NON_RUNTIME_NON_TEST_PATTERN` ? `scripts/f29_0_memory_graphiti_reconciliation_audit.py` ? matches: `['emits_act\\s*[:=]\\s*True', 'kernel_mutation\\s*[:=]\\s*True', 'x108_mutation\\s*[:=]\\s*True', 'memory_write\\s*[:=]\\s*True', 'graphiti_write\\s*[:=]\\s*True', 'neo4j_write\\s*[:=]\\s*True']`
  - line 59: `"memory_write=True",`
  - line 60: `"graphiti_write=True",`
  - line 61: `"neo4j_write=True",`
- `REVIEW_NON_RUNTIME_NON_TEST_PATTERN` ? `scripts/f30_0_workflow_sop_engine_audit.py` ? matches: `['emits_act\\s*[:=]\\s*True', 'kernel_mutation\\s*[:=]\\s*True', 'x108_mutation\\s*[:=]\\s*True', 'memory_write\\s*[:=]\\s*True', 'graphiti_write\\s*[:=]\\s*True', 'neo4j_write\\s*[:=]\\s*True']`
  - line 54: `"emits_act=True",`
  - line 56: `"kernel_mutation=True",`
  - line 57: `"x108_mutation=True",`
- `REVIEW_NON_RUNTIME_NON_TEST_PATTERN` ? `scripts/f30_1b_workflow_governance_v5_danger_classification.py` ? matches: `['emits_act\\s*[:=]\\s*True', 'kernel_mutation\\s*[:=]\\s*True', 'x108_mutation\\s*[:=]\\s*True', 'memory_write\\s*[:=]\\s*True', 'graphiti_write\\s*[:=]\\s*True', 'neo4j_write\\s*[:=]\\s*True']`
  - line 26: `"emits_act=True",`
  - line 28: `"kernel_mutation=True",`
  - line 29: `"x108_mutation=True",`
- `REVIEW_NON_RUNTIME_NON_TEST_PATTERN` ? `scripts/f30_1_workflow_governance_v5_audit.py` ? matches: `['emits_act\\s*[:=]\\s*True', 'kernel_mutation\\s*[:=]\\s*True', 'x108_mutation\\s*[:=]\\s*True', 'memory_write\\s*[:=]\\s*True', 'graphiti_write\\s*[:=]\\s*True', 'neo4j_write\\s*[:=]\\s*True']`
  - line 57: `"emits_act=True",`
  - line 59: `"kernel_mutation=True",`
  - line 60: `"x108_mutation=True",`
- `REVIEW_NON_RUNTIME_NON_TEST_PATTERN` ? `scripts/f30_2_copy_v5_readonly_module.py` ? matches: `['emits_act\\s*[:=]\\s*True', 'kernel_mutation\\s*[:=]\\s*True', 'x108_mutation\\s*[:=]\\s*True', 'memory_write\\s*[:=]\\s*True', 'graphiti_write\\s*[:=]\\s*True', 'neo4j_write\\s*[:=]\\s*True']`
  - line 22: `"emits_act=True",`
  - line 24: `"kernel_mutation=True",`
  - line 25: `"x108_mutation=True",`
- `REVIEW_NON_RUNTIME_NON_TEST_PATTERN` ? `scripts/f30_3_workflow_governance_import_compile_validate.py` ? matches: `['emits_act\\s*[:=]\\s*True', 'kernel_mutation\\s*[:=]\\s*True', 'x108_mutation\\s*[:=]\\s*True', 'memory_write\\s*[:=]\\s*True', 'graphiti_write\\s*[:=]\\s*True', 'neo4j_write\\s*[:=]\\s*True']`
  - line 23: `"emits_act=True",`
  - line 25: `"kernel_mutation=True",`
  - line 26: `"x108_mutation=True",`
- `REVIEW_NON_RUNTIME_NON_TEST_PATTERN` ? `scripts/f35_0_operator_demo_surface_audit.py` ? matches: `['emits_act\\s*[:=]\\s*True', 'kernel_mutation\\s*[:=]\\s*True', 'x108_mutation\\s*[:=]\\s*True', 'memory_write\\s*[:=]\\s*True', 'graphiti_write\\s*[:=]\\s*True', 'neo4j_write\\s*[:=]\\s*True']`
  - line 49: `"emits_act=True",`
  - line 52: `"kernel_mutation=True",`
  - line 53: `"x108_mutation=True",`
- `NON_BLOCKING_TEST_FIXTURE_OR_ASSERTION_CANDIDATE` ? `tests/api/test_f16_live_sources.py` ? matches: `['kernel_mutation\\s*[:=]\\s*True']`
  - line 118: `assert "kernel_mutation: True" not in src`
- `NON_BLOCKING_TEST_FIXTURE_OR_ASSERTION_CANDIDATE` ? `tests/non_sovereignty/test_x108_context_ingress_readonly_only.py` ? matches: `['allowed_to_decide\\s*[:=]\\s*True']`
  - line 40: `"""Packets with allowed_to_decide=True must be rejected."""`
- `BLOCKING_RUNTIME_FORBIDDEN_TRUE_PATTERN` ? `apps/obsidia_api/safe_response.py` ? matches: `['allowed_to_decide\\s*[:=]\\s*True']`
  - line 6: `overwrites). A module returning {allowed_to_decide: True} cannot propagate that`

## Conclusion

F73 blocking risks are only real blockers if they appear in runtime code. Patterns inside tests are classified separately as fixture/assertion candidates.

## Next

F73_BUILD_TESTS_OR_FINAL_SIGMA_BRANCH_REVIEW
