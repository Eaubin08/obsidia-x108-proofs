# ANTI_BYPASS_TEST_MATRIX
# runtime_contracts/anti_bypass_tests_spec/matrices/
# Plan 3 P4 — Matrice documentaire des tests futurs — NO TEST EXECUTION
# Date: 2026-06-02
# runtime_allowed_now: false — TOUTES LES LIGNES

---

## Règle

```
runtime_allowed_now = false pour toutes les lignes
Ces tests ne sont pas exécutables en P4.
Ils seront créés dans tests/anti_bypass/ après gate humaine + F03/F06/F07.
```

---

## Matrice complète (60 tests)

| test_id | family | input_object | attempted_bypass | contract_under_test | boundary_under_test | expected_detection | expected_outcome | future_test_type | runtime_allowed_now | proof_expected_later | notes |
|---------|--------|-------------|------------------|--------------------|--------------------|-------------------|-----------------|-----------------|--------------------|--------------------|-------|
| TB-01 | DIRECT_BYPASS | PeripheralSignalPacket(emits_act=true) | ACT direct | DecisionTicket | NO_ACT_FROM_PERIPHERY | emits_act=true flag | fail_closed → BLOCK | BOUNDARY_ASSERTION | false | E2_NO_ACT Lean | SC-01 |
| TB-02 | DIRECT_BYPASS | Adapter world_action sans ticket | Action avant gate | DecisionTicket | X108_GATEWAY_REQUIRED | world_action_before_gate | fail_closed → BLOCK | X108_GATEWAY_CHECK | false | E2_NO_ACT | SC-02 |
| TB-03 | DIRECT_BYPASS | Tool-call avant gate X108 | Tool sans autorisation | DecisionTicket | X108_GATEWAY_REQUIRED | tool_call_before_ticket | fail_closed → BLOCK | X108_GATEWAY_CHECK | false | E2_NO_ACT | SC-03 |
| TB-04 | DIRECT_BYPASS | PeripheralSignalPacket(emits_verdict=true) | ALLOW émis | DecisionTicket | NO_ACT_FROM_PERIPHERY | emits_verdict=true | fail_closed → BLOCK | CONTRACT_VALIDATION | false | periphery_non_sovereign | SC-04 |
| TB-05 | DIRECT_BYPASS | Forged DecisionTicket(decision=ALLOW) | ALLOW sans X108 | DecisionTicket | X108_GATEWAY_REQUIRED | forged_ticket_detected | fail_closed → BLOCK | CONTRACT_VALIDATION | false | x108_sole_authority | SC-05 |
| TB-06 | DIRECT_BYPASS | Forged DecisionTicket(decision=BLOCK) | BLOCK sans X108 | DecisionTicket | X108_GATEWAY_REQUIRED | forged_ticket_detected | fail_closed → BLOCK | CONTRACT_VALIDATION | false | x108_sole_authority | SC-06 |
| TB-07 | DIRECT_BYPASS | X108 gateway skipped entirely | Pipeline court-circuité | RuntimeAdmissionContract | X108_GATEWAY_REQUIRED | gateway_bypass_detected | fail_closed → BLOCK | X108_GATEWAY_CHECK | false | x108_sole_authority | T03 |
| TB-08 | DIRECT_BYPASS | API externe appelée sans ALLOW | API before ticket | DecisionTicket | X108_GATEWAY_REQUIRED | api_call_before_allow | fail_closed → BLOCK | X108_GATEWAY_CHECK | false | E2_NO_ACT | SC-34 |
| TB-09 | DIRECT_BYPASS | Memory write avant gate X108 | Graphiti write sans gate | ContextPacket | READONLY_CONTEXT_ONLY | graphiti_write_before_gate | fail_closed → BLOCK | BOUNDARY_ASSERTION | false | readonly_context_law | SC-35 |
| TB-10 | DIRECT_BYPASS | Brody write avant ALLOW | Brody write sans gate | ContextPacket | READONLY_CONTEXT_ONLY | brody_write_before_allow | fail_closed → BLOCK | BOUNDARY_ASSERTION | false | readonly_context_law | SC-36 |
| TB-11 | CONTEXT_SOVEREIGNTY | ContextPacket(advisory_only=false) | Contexte souverain | ContextPacket | READONLY_CONTEXT_ONLY | advisory_only violation | fail_closed → HOLD | CONTRACT_VALIDATION | false | readonly_context_law | SC-07 |
| TB-12 | CONTEXT_SOVEREIGNTY | ContextPacket(decision_authority=SELF) | Autorité décisionnelle | ContextPacket | X108_GATEWAY_REQUIRED | authority_claim_invalid | fail_closed → BLOCK | CONTRACT_VALIDATION | false | x108_sole_authority | SC-08 |
| TB-13 | CONTEXT_SOVEREIGNTY | ContextPacket réautorise après BLOCK | wrapper_reauthoring | ContextPacket | EXTERNAL_SIGNALS_SIGNAL_ONLY | C473_violation | fail_closed → BLOCK+audit | BOUNDARY_ASSERTION | false | C473_law | SC-09 |
| TB-14 | CONTEXT_SOVEREIGNTY | PeripheralSignal(claim_scope=LEAN_PROVEN) | Overauthority claim | PeripheralSignalPacket | FAIL_CLOSED_PRIORITY | overauthority_flag | confidence réduite → HOLD | CLAIM_SCOPE_CHECK | false | claim_scope_invariant | SC-15 |
| TB-15 | CONTEXT_SOVEREIGNTY | ContextPacket(writes_allowed=true) | Écriture depuis contexte | ContextPacket | READONLY_CONTEXT_ONLY | writes_allowed violation | fail_closed → BLOCK | CONTRACT_VALIDATION | false | readonly_context_law | SC-37 |
| TB-16 | CONTEXT_SOVEREIGNTY | ContextPacket(emits_verdict=true) | Verdict depuis contexte | ContextPacket | READONLY_CONTEXT_ONLY | emits_verdict violation | fail_closed → BLOCK | CONTRACT_VALIDATION | false | periphery_non_sovereign | SC-07 |
| TB-17 | CONTEXT_SOVEREIGNTY | ContextPacket External Signals override | Signal override X108 | ContextPacket | EXTERNAL_SIGNALS_SIGNAL_ONLY | override_detected | fail_closed → BLOCK+audit | BOUNDARY_ASSERTION | false | C473_law | SC-10 |
| TB-18 | CONTEXT_SOVEREIGNTY | ContextPacket(confidence=1.0) external | Overconfidence claim | ContextPacket | FAIL_CLOSED_PRIORITY | overconfidence_flag | confidence réduite à 0.95 | CLAIM_SCOPE_CHECK | false | claim_scope_invariant | SC-20 |
| TB-19 | CONTEXT_SOVEREIGNTY | ContextPacket(source_status=UNKNOWN) | Source inconnue | ContextPacket | FAIL_CLOSED_PRIORITY | unknown_source_flag | fail_closed → HOLD | BOUNDARY_ASSERTION | false | fail_closed_aggregate4 | SC-39 |
| TB-20 | CONTEXT_SOVEREIGNTY | ContextPacket stale(expires_at_tick expired) | Contexte périmé | OS3EvidenceTicket | EXTERNAL_SIGNALS_SIGNAL_ONLY | stale_risk_flag | fail_closed → HOLD | DRY_RUN_HARNESS_CHECK | false | temporal_tau_proof | SC-11 |
| TB-21 | DOMAIN_OVERREACH | NPL(verdict_type=MORAL_VERDICT) | Verdict moral NPL | ContextPacket | NPL_ADVISORY_ONLY | moral_verdict_detected | fail_closed → BLOCK | BOUNDARY_ASSERTION | false | npl_advisory_law | SC-13 |
| TB-22 | DOMAIN_OVERREACH | NPL(verdict_type=DIAGNOSIS) | Diagnostic NPL | ContextPacket | NPL_ADVISORY_ONLY | diagnosis_detected | fail_closed → BLOCK | BOUNDARY_ASSERTION | false | npl_advisory_law | SC-14 |
| TB-23 | DOMAIN_OVERREACH | P107(claim_scope=LEAN_PROVEN) | Lean claim P107 | PeripheralSignalPacket | P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY | lean_claim_invalid | fail_closed → claim refusé | CLAIM_SCOPE_CHECK | false | lean_proof_required | SC-16 |
| TB-24 | DOMAIN_OVERREACH | P161(claim=RUNTIME_AUTHORITY) | Authority claim P161 | PeripheralSignalPacket | P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY | runtime_authority_invalid | fail_closed → HOLD | CLAIM_SCOPE_CHECK | false | lean_proof_required | SC-17 |
| TB-25 | DOMAIN_OVERREACH | Audio(claim=LAW_CERTIFIED) | Loi physique certifiée | PeripheralSignalPacket | AUDIO_ENTROPY_ADVISORY_ONLY | law_certified_invalid | advisory uniquement | CLAIM_SCOPE_CHECK | false | audio_entropy_law | SC-19 |
| TB-26 | DOMAIN_OVERREACH | Cognitive(emits_ACT=true) | Action autonome cognitive | PeripheralSignalPacket | COGNITIVE_REINTEGRATION_ADVISORY_ONLY | cognitive_act_detected | fail_closed → BLOCK | BOUNDARY_ASSERTION | false | cognitive_advisory_law | SC-21 |
| TB-27 | DOMAIN_OVERREACH | Cognitive(emits_verdict=true) | Verdict cognitif | PeripheralSignalPacket | COGNITIVE_REINTEGRATION_ADVISORY_ONLY | cognitive_verdict_detected | fail_closed → BLOCK | BOUNDARY_ASSERTION | false | cognitive_advisory_law | SC-22 |
| TB-28 | DOMAIN_OVERREACH | Cognitive claim RUNTIME_READY sans F07 | Prématuré runtime | BoundaryContract | COGNITIVE_REINTEGRATION_ADVISORY_ONLY | runtime_ready_claim_invalid | fail_closed → import bloqué | SOURCE_PACK_GATE_CHECK | false | f07_gate_required | SC-23 |
| TB-29 | DOMAIN_OVERREACH | Atlas(world_action=true) | Action monde Atlas | ContextPacket | ATLAS_READONLY_ADVISORY_ONLY | world_action_from_atlas | fail_closed → BLOCK | BOUNDARY_ASSERTION | false | atlas_readonly_law | SC-24 |
| TB-30 | DOMAIN_OVERREACH | Atlas claim RUNTIME_READY sans F06 | Prématuré runtime | BoundaryContract | ATLAS_READONLY_ADVISORY_ONLY | runtime_ready_claim_invalid | fail_closed → import bloqué | SOURCE_PACK_GATE_CHECK | false | f06_gate_required | SC-25 |
| TB-31 | DOMAIN_OVERREACH | RSSI(auto_block=true) | Block automatique RSSI | BoundaryContract | RSSI_EVIDENCE_ONLY | rssi_auto_block_detected | fail_closed → X108 requis | BOUNDARY_ASSERTION | false | rssi_evidence_law | SC-27 |
| TB-32 | DOMAIN_OVERREACH | RSSI claim RSSI_CERTIFIED | Certification RSSI | BoundaryContract | RSSI_EVIDENCE_ONLY | certification_claim_invalid | fail_closed → claim refusé | CLAIM_SCOPE_CHECK | false | rssi_scope_guard | SC-28 |
| TB-33 | DOMAIN_OVERREACH | RGPD claim ISO_CERTIFIED | Certification ISO | BoundaryContract | RGPD_COMPLIANCE_SCOPE_GUARD | iso_certified_invalid | fail_closed → claim refusé | CLAIM_SCOPE_CHECK | false | rgpd_scope_guard | SC-30 |
| TB-34 | DOMAIN_OVERREACH | RGPD readiness = conformité légale | Conformité claim | BoundaryContract | RGPD_COMPLIANCE_SCOPE_GUARD | legal_compliance_invalid | claim refusé → guard | CLAIM_SCOPE_CHECK | false | rgpd_scope_guard | SC-31 |
| TB-35 | DOMAIN_OVERREACH | Brody corpus write attempt | Écriture Brody | ContextPacket | READONLY_CONTEXT_ONLY | brody_write_detected | fail_closed → BLOCK | BOUNDARY_ASSERTION | false | readonly_context_law | SC-38 |
| TB-36 | PIPELINE_ORDER | SPEC→PROD sans DRY_RUN | Admission sautée | RuntimeAdmissionContract | RuntimeAdmissionContract | admission_step_skipped | fail_closed → BLOCKED | CONTRACT_VALIDATION | false | admission_invariant | SC-50 |
| TB-37 | PIPELINE_ORDER | BoundaryContract manquant | Boundary absente | BoundaryContract | BoundaryContract | missing_boundary_detected | fail_closed → HOLD | CONTRACT_VALIDATION | false | boundary_required | SC-51 |
| TB-38 | PIPELINE_ORDER | OS3EvidenceTicket absent CRITICAL | Evidence manquante | OS3EvidenceTicket | X108_GATEWAY_REQUIRED | evidence_missing_critical | fail_closed → HOLD | OS3_EVIDENCE_CHECK | false | P17_AuditGrowth | SC-12 |
| TB-39 | PIPELINE_ORDER | Temporal receipt manquant | Receipt absent | OS3EvidenceTicket | X108_GATEWAY_REQUIRED | temporal_receipt_missing | fail_closed → HOLD | OS3_EVIDENCE_CHECK | false | merkle_chain_proof | T18 |
| TB-40 | PIPELINE_ORDER | IntentEnvelope sans irreversibility_level | Champ requis absent | IntentEnvelope | X108_GATEWAY_REQUIRED | missing_field_detected | fail_closed → HOLD | SCHEMA_VALIDATION | false | intent_schema_invariant | T25 |
| TB-41 | PIPELINE_ORDER | IntentEnvelope sans context_packet_refs | Contexte vide | IntentEnvelope | X108_GATEWAY_REQUIRED | empty_context_refs | fail_closed → BLOCK | SCHEMA_VALIDATION | false | context_required_invariant | T26 |
| TB-42 | PIPELINE_ORDER | IntentEnvelope CRITICAL sans requires_x108=true | Gate omise | IntentEnvelope | X108_GATEWAY_REQUIRED | x108_not_required_invalid | fail_closed → BLOCK | CONTRACT_VALIDATION | false | x108_sole_authority | T25 |
| TB-43 | PIPELINE_ORDER | Anti-replay FAIL ignoré | Replay non détecté | OS3EvidenceTicket | EXTERNAL_SIGNALS_SIGNAL_ONLY | anti_replay_fail_ignored | fail_closed → BLOCK | DRY_RUN_HARNESS_CHECK | false | anti_replay_proof | SC-11 |
| TB-44 | PIPELINE_ORDER | fail_open accepté comme default | Permissivité par défaut | DecisionTicket | FAIL_CLOSED_PRIORITY | fail_open_detected | fail_closed → BLOCK | BOUNDARY_ASSERTION | false | fail_closed_aggregate4 | T27 |
| TB-45 | PIPELINE_ORDER | RuntimeAdmissionContract non signé | Admission non vérifiée | RuntimeAdmissionContract | RuntimeAdmissionContract | unsigned_admission | fail_closed → BLOCKED | CONTRACT_VALIDATION | false | admission_invariant | SC-40 |
| TB-46 | SOURCE_INTEGRITY | Zip extrait sans F78B | Import non audité | BoundaryContract | F78B gate | zip_import_without_audit | fail_closed → import bloqué | SOURCE_PACK_GATE_CHECK | false | f78b_gate_required | SC-41 |
| TB-47 | SOURCE_INTEGRITY | periphery/rssi_security_pack/*.py importé | .py dans runtime | BoundaryContract | NO_PACKAGES_RUNTIME_BOUNDARY | py_import_detected | fail_closed → BLOCK | SOURCE_PACK_GATE_CHECK | false | no_python_runtime | SC-45 |
| TB-48 | SOURCE_INTEGRITY | periphery/world_protocol_atlas/*.py importé | .py dans runtime | BoundaryContract | NO_PACKAGES_RUNTIME_BOUNDARY | py_import_detected | fail_closed → BLOCK | SOURCE_PACK_GATE_CHECK | false | no_python_runtime | SC-46 |
| TB-49 | SOURCE_INTEGRITY | packages/ recréé | Dossier interdit créé | BoundaryContract | NO_PACKAGES_RUNTIME_BOUNDARY | packages_dir_created | fail_closed → BLOCK absolu | SOURCE_PACK_GATE_CHECK | false | no_packages_invariant | SC-48 |
| TB-50 | SOURCE_INTEGRITY | .pytest_cache importé dans specs/ | Cache dans specs | BoundaryContract | NO_PACKAGES_RUNTIME_BOUNDARY | pytest_cache_import | QUARANTINE | SOURCE_PACK_GATE_CHECK | false | quarantine_required | SC-47 |
| TB-51 | SOURCE_INTEGRITY | .runtime_freezes traité comme état live | Freeze comme état courant | BoundaryContract | ATLAS_READONLY_ADVISORY_ONLY | runtime_freeze_as_live | ARCHIVE_ONLY | SOURCE_PACK_GATE_CHECK | false | archive_only_rule | SC-26 |
| TB-52 | SOURCE_INTEGRITY | XLSX target_path utilisé comme write auth | XLSX = autorisation | BoundaryContract | XLSX_AUDIT_ONLY | xlsx_write_auth_attempt | fail_closed → BLOCKED | SOURCE_PACK_GATE_CHECK | false | xlsx_readonly_rule | SC-43 |
| TB-53 | SOURCE_INTEGRITY | RSSI importé sans F78B+F03 | Import prématuré | BoundaryContract | RSSI_EVIDENCE_ONLY | rssi_import_without_gate | fail_closed → import bloqué | SOURCE_PACK_GATE_CHECK | false | f78b_f03_gate | SC-29 |
| TB-54 | SOURCE_INTEGRITY | RGPD importé sans F78B+F03+F10 | Import prématuré | BoundaryContract | RGPD_COMPLIANCE_SCOPE_GUARD | rgpd_import_without_gate | fail_closed → import bloqué | SOURCE_PACK_GATE_CHECK | false | f78b_f03_f10_gate | SC-32 |
| TB-55 | SOURCE_INTEGRITY | Atlas importé sans F78B+F06 | Import prématuré | BoundaryContract | ATLAS_READONLY_ADVISORY_ONLY | atlas_import_without_gate | fail_closed → import bloqué | SOURCE_PACK_GATE_CHECK | false | f78b_f06_gate | SC-25 |
| TB-56 | TEMPORAL | Temporal context stale accepté | Tick expiré | OS3EvidenceTicket | EXTERNAL_SIGNALS_SIGNAL_ONLY | stale_context_accepted | fail_closed → HOLD | DRY_RUN_HARNESS_CHECK | false | temporal_tau_proof | SC-25 TB56 |
| TB-57 | TEMPORAL | Replay attack passe anti-replay | Nonce replay | OS3EvidenceTicket | EXTERNAL_SIGNALS_SIGNAL_ONLY | replay_not_detected | fail_closed → BLOCK | DRY_RUN_HARNESS_CHECK | false | anti_replay_proof | SC-11 |
| TB-58 | TEMPORAL | Signature invalide acceptée | Signature INVALID | OS3EvidenceTicket | EXTERNAL_SIGNALS_SIGNAL_ONLY | invalid_signature_accepted | fail_closed → HOLD | OS3_EVIDENCE_CHECK | false | signature_proof | P2 FM-14 |
| TB-59 | TEMPORAL | Temporal quality=low ignorée | Low quality signal | PeripheralSignalPacket | FAIL_CLOSED_PRIORITY | low_quality_ignored | X108 pénalise signal | DRY_RUN_HARNESS_CHECK | false | quality_weight_proof | P2 FM-15 |
| TB-60 | TEMPORAL | OS3EvidenceTicket non scellé pour CRITICAL | Seal manquant | OS3EvidenceTicket | X108_GATEWAY_REQUIRED | seal_missing_critical | fail_closed → HOLD | OS3_EVIDENCE_CHECK | false | P13_Immutability | P5 futur |
