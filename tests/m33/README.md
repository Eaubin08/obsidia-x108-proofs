# M33 RED suite — traceability (test documentation only)

Spec: `docs/architecture/M33_ARM_RECONSTRUCTION_SPEC_V1.md` at `M33_SPEC_BASE=20bffb2442fac0057318596af79784fef32551b9` (independently certified). Runtime target `app.reconstruction.m33` (absent at RED: runtime tests fail with « M33 runtime app/reconstruction/m33 is absent (certified RED) »).

Harness conventions (`_harness.py`): constructors called with keyword arguments only; enums referenced by member name and serialized by member name in identity preimages; derived ids (`item_id`, `relation_id`, `request_id`, `reconstruction_id`) are read, never passed; reference oracles compute expected values only and never build M33 objects. Not tested (certified nonblocking): `subject_ids` resolution, extra effects-field error code, extra collection bounds, original statuses after `UNDETERMINED`, per-support contributor provenance, positional constructor order.

## R1–R24

| R | Tests | Level |
|---|---|---|
| R1 | `test_r1_spec_distinguishes_source_levels_a_b_c`, `test_r1_level_a_row_carries_no_trajectory_vocabulary` | doc audit |
| R2 | `test_r2_material_requires_m32_datum`, `test_r2_duplicate_material_ids_rejected`, `test_r2_no_context_or_memory_lookup_surface` | runtime |
| R3 | `test_r3_reconstruction_item_exists_with_hex_id`, `test_r3_no_candidate_names_in_public_surface`, `test_r3_item_has_no_truth_or_promotion_fields` | runtime |
| R4 | `test_r4_support_kind_enum_exact`, `test_r4_evidence_shape_and_inference_basis`, `test_r4_kinds_preserved_on_aggregation` | runtime |
| R5 | `test_r5_integration_status_enum_exact`, `test_r5_absent_in_scope_requires_scope_ref`, `test_r5_b2_invalid_absent_not_sanitized_by_merge`, `test_r5_inspection_scope_is_material_set` | runtime |
| R6 | `test_r6_relation_identity_and_endpoints`, `test_r6_relation_cycle_allowed_unknown_endpoint_rejected`, `test_r6_no_graph_types_and_no_transitive_closure` | runtime |
| R7 | `test_r7_contradiction_preserves_both_items` | runtime |
| R8 | `test_r8_unresolved_reference_yields_partial`, `test_r8_status_and_issue_enums_distinct` | runtime |
| R9 | `test_r9_same_inputs_same_reconstruction_id`, `test_r9_nested_caller_mutation_does_not_change_identity`, `test_integration_merge_pairs_commutative` | runtime |
| R10 | `test_r10_item_id_matches_reference` (incl. floats), `test_r10_request_id_matches_reference`, `test_r10_result_id_matches_reference`, `test_r6_relation_identity_and_endpoints`, `test_nfc_equivalent_content_same_item_id` | runtime |
| R11 | `test_r11_provider_model_clock_excluded`, `test_r11_issue_change_changes_result_id`, `test_r11_bounds_change_request_id` | runtime |
| R12 | `test_r12_provenance_normalized` | runtime |
| R13 | `test_r13_bounds_invalid_values`, `test_r13_bounds_valid_extremes`, `test_r13_max_items_exceeded`, `test_r13_max_relations_and_supports_exceeded`, `test_r13_derivation_depth`, `test_derivation_cycle_rejected`, `test_no_scheduler_surface` | runtime |
| R14 | `test_r14_only_supplied_items_appear`, `test_r14_duplicate_contribution_ids_rejected` | runtime |
| R15 | `test_r15_r17_no_forbidden_imports` | static |
| R16 | `test_r16_r18_r24_no_competing_public_names`, `test_r16_role_ref_is_provenance_only` | static + runtime |
| R17 | `test_r15_r17_no_forbidden_imports`, `test_r3_no_candidate_names_in_public_surface` | static + runtime |
| R18 | `test_r16_r18_r24_no_competing_public_names`, `test_r18_relation_is_not_cognitive_path` | static + runtime |
| R19 | `test_r19_r23_effects_all_false`, `test_r15_r17_no_forbidden_imports` (IO/persistence) | runtime + static |
| R20 | `test_r20_no_confidence_or_utility_fields`, `test_no_scheduler_surface` | runtime |
| R21 | `test_r21_construction_error_origins`, `test_r21_lifecycle_error_origins`, `test_r21_invalid_result_on_direct_construction`, `test_r21_error_codes_are_not_statuses`, plus code-specific tests listed in R2/R4/R5/R6/R13/R14/R23 | runtime |
| R22 | `test_r22_status_table`, `test_r22_b1_1_*`, `test_r22_b1_2_*`, `test_r22_b1_3_*`, `test_r22_b1_4_*`, `test_r22_b1_5_*`, `test_r22_insufficient_material_never_raises` | runtime |
| R23 | `test_r19_r23_effects_all_false`, `test_r23_effects_true_rejected`, `test_r23_result_carries_false_effects`, `test_r23_reconstruct_takes_no_handles` | runtime |
| R24 | `test_r24_certified_public_surface_present`, `test_r16_r18_r24_no_competing_public_names`, `test_protected_paths_unchanged_since_m33_spec_base`, `test_runtime_location_outside_seal`, `test_foundation_sentinel_passes_with_m33_present` | runtime + static |

## A1–A24

| A | Requirement | Test | Oracle |
|---|---|---|---|
| A1 | R1 | `test_r1_level_a_row_carries_no_trajectory_vocabulary` | doc text |
| A2 | R3, R17 | `test_r3_no_candidate_names_in_public_surface`, `test_r16_r18_r24_no_competing_public_names` | no `*Candidate*` |
| A3 | R4 | `test_r4_evidence_shape_and_inference_basis` | `INVALID_DERIVATION` |
| A4 | R3, R20 | `test_r3_item_has_no_truth_or_promotion_fields`, `test_r4_support_kind_enum_exact` | no verified field/value |
| A5 | R5 | `test_r5_absent_in_scope_requires_scope_ref` | `INVALID_INTEGRATION_STATUS` |
| A6 | R5, R8 | `test_r5_integration_status_enum_exact`, `test_r8_status_and_issue_enums_distinct` | no UNKNOWN/FALSE members |
| A7 | R7 | `test_r7_contradiction_preserves_both_items` | both items kept |
| A8 | R9 | `test_r9_same_inputs_same_reconstruction_id`, `test_r6_no_graph_types_and_no_transitive_closure` | distinct ids never merged |
| A9 | R16 | `test_r16_r18_r24_no_competing_public_names` | AST |
| A10 | R17 | `test_r15_r17_no_forbidden_imports` | AST |
| A11 | R18 | `test_r16_r18_r24_no_competing_public_names`, `test_r18_relation_is_not_cognitive_path` | AST + shape |
| A12 | R24 | `test_r16_r18_r24_no_competing_public_names` | M32 names |
| A13 | R24 | `test_m32_does_not_register_m33_primitives` | no registration call |
| A14 | R19 | `test_r19_r23_effects_all_false`, `test_r15_r17_no_forbidden_imports` | effects + imports |
| A15 | R11 | `test_r11_provider_model_clock_excluded` | same id |
| A16 | R11 | `test_r11_provider_model_clock_excluded` | patched clock |
| A17 | R9 | `test_r9_nested_caller_mutation_does_not_change_identity` | same id |
| A18 | R13, R21 | `test_derivation_cycle_rejected` | `DERIVATION_CYCLE` |
| A19 | R14 | `test_r14_only_supplied_items_appear`, `test_no_scheduler_surface` | signature/surface |
| A20 | R20 | `test_r20_no_confidence_or_utility_fields` | no field |
| A21 | R23 | `test_r23_reconstruct_takes_no_handles` | signature |
| A22 | R23 | `test_r19_r23_effects_all_false`, `test_r15_r17_no_forbidden_imports` | effects + imports |
| A23 | R20, R24 | `test_r16_r18_r24_no_competing_public_names` (defined names), `test_r3_no_candidate_names_in_public_surface` (public surface); detector control `test_pc7_flux_and_report_label_guards` | explicit `Flux*` name check on defined and public names (comments/strings/private names not matched) |
| A24 | R3, R20 | `test_a24_report_labels_not_canonical_runtime_vocabulary`, `test_r3_item_has_no_truth_or_promotion_fields`; detector control `test_pc7_flux_and_report_label_guards` | historical report labels (SOLID, EVOKED, FORGOTTEN, LATENT, OPEN_QUESTIONS, REPORT_LABEL) are not public names, enum members or fields — exact standalone match, so `EVOKED_NOT_LOCKED` is valid; report projection != runtime truth/status/promotion |

## X1–X12

| X | Test |
|---|---|
| X1 arbitrary scope ref | `test_r5_inspection_scope_is_material_set` |
| X2 EVIDENCE vs INFERENCE same item | `test_r4_kinds_preserved_on_aggregation` |
| X3 FAILED + successful | `test_r22_b1_4_mixed_failure_discards_items` |
| X4 opposite-order merges | `test_integration_merge_pairs_commutative` |
| X5 contradiction + RECONSTRUCTED | `test_r7_contradiction_preserves_both_items` |
| X6 unknown evidence source ref | `test_r21_lifecycle_error_origins` |
| X7 provider-only change | `test_r11_provider_model_clock_excluded` |
| X8 issue change changes result id | `test_r11_issue_change_changes_result_id` |
| X9 relation cycle vs derivation cycle | `test_r6_relation_cycle_allowed_unknown_endpoint_rejected`, `test_derivation_cycle_rejected` |
| X10 aggregation keeps contributors | `test_r12_provenance_normalized` |
| X11 bounds change request id | `test_r11_bounds_change_request_id` |
| X12 FAILED stale payload | `test_r22_b1_5_failed_contribution_payload_rejected` |

## B1/B2 mutants

| Mutant | Test |
|---|---|
| M_B1_1 short-circuit FAILED_RUNTIME | `test_r22_b1_1_validation_beats_failed_runtime_dangling` |
| M_B1_2 skip FAILED payload validation | `test_r22_b1_5_failed_contribution_payload_rejected` |
| M_B1_3 ignore cycle because of failure | `test_r22_b1_2_validation_beats_failed_runtime_cycle` |
| M_B2_1 merge ABSENT before validation | `test_r5_b2_invalid_absent_not_sanitized_by_merge` |
| M_B2_2 sanitize ABSENT into UNDETERMINED | `test_r5_b2_invalid_absent_not_sanitized_by_merge` |

Positive controls PC1–PC7 and self-mutation checks SM1–SM7: `test_m33_harness_selfcheck_red.py`.
