# M32 RED suite — traceability (test documentation only)

Spec: `docs/architecture/M32_COMMON_COGNITIVE_PRIMITIVES_SPEC_V1.md` (certified; `M32_BASE=faf72a25fb912a27b4be9a71d1b1a07f0e8fca79`).
Runtime target: `app.primitives.m32` (absent at RED). Harness bindings for the unnamed registry/adapter spellings are centralized in `_harness.py`.

| Req | Tests |
|---|---|
| R1 | `test_r1_same_canonical_invocation_same_id`, `test_r1_id_matches_reference_preimage`, `test_lifecycle_draft_has_no_invocation_id_and_final_does` |
| R2 | `test_r2_different_type_different_id` |
| R3 | `test_r3_input_and_config_change_id`, `test_identity_nfc_equivalent_values_same_id`, `test_negative_zero_canonicalizes_to_zero` |
| R4 | `test_r4_wall_clock_and_host_excluded`, `test_r4_provider_and_environment_only_in_provenance`, `test_r4_provider_declared_in_config_changes_id` |
| R5 | `test_r5a_emits_act_true_unregistrable`, `test_r5b_outcome_with_act_field_rejected`, `test_r5_registered_specs_declare_no_act`, `test_run_receives_no_effect_capable_handle` |
| R6 | `test_r6a_memory_write_true_unregistrable`, `test_r6b_outcome_with_memory_write_field_rejected` |
| R7 | `test_r7a_mutation_flags_unregistrable`, `test_r7b_outcome_with_b8_mutation_field_rejected`, `test_r7c_b8_sealed_oracle` |
| R8 | `test_r8_unknown_status_and_null_output`, `test_statuses_are_branched_on_enum_not_truthiness` |
| R9 | `test_r9_not_applicable_vs_failed_runtime` |
| R10 | `test_r10_failed_runtime_shape` |
| R11 | `test_r11_*` (phases B, C, D, E), `test_nfc_equivalent_slot_names_are_duplicates`, `test_invalid_execution_request_before_phase_h` |
| R12 | `test_r12_provenance_retained`, `test_provenance_metadata_canonical` |
| R13 | `test_r13_composition_linkage_and_schema_mismatch`, `test_composition_no_fuzzy_type_match` |
| R14 | `test_r14_adapter_boundary`, `test_adapter_wrong_target_type_fails_closed` |
| R15 | `test_r15_b7_sealed_oracle` |
| R16 | `test_r16_b9_sealed_oracle` |
| R17 | `test_r17_foundation_sentinel_passes_with_m32_present` |
| R18 | `test_r18_two_implementations_same_id_distinct_records` |
| R19 | `test_r19_result_closed_shape`, `test_result_output_rules_enforced_at_construction` |
| R20 | `test_r20_unknown_upstream_yields_insufficient_input_downstream`, `test_missing_required_slot_flow` |

Other contract reds: registry/versioning (`test_registry_idempotent_conflict_unknown`, `test_v1_never_resolves_to_v2`, `test_implementation_registry_never_raises_type_codes`, `test_declared_slots_order_independent_and_nfc_unique`), immutability (`test_caller_mutation_does_not_alter_identity`), test-registry isolation (`test_test_namespace_rejected_in_production`, `test_test_registry_accepts_test_namespace`), location (`test_location_*`), protected diff since `M32_BASE` over all commits (`test_protected_path_diff_since_m32_base_is_zero`).

Edge cases with no named code in the spec (empty `semantic_refs` entry, `run` returning a non-outcome, adapter output not matching its target) assert fail-closed `InvocationValidationError` only; no code is invented.
