# X108_GATEWAY_DRY_RUN_HARNESS_FAILURE_MODES
# runtime_contracts/x108_gateway_dry_run_harness/failure_modes/
# Plan 3 P3 — Failure modes documentaires — NO RUNTIME EXECUTION
# Date: 2026-06-02

---

## Règle universelle

```
∀ failure mode f : f → fail_closed
∀ failure mode f : f → no_act
∀ failure mode f : f → requires_x108_review
∀ failure mode f : f ↛ allow_by_default
Priorité : BLOCK > HOLD > ALLOW  (aggregate4_fail_closed)
```

---

## Table complète (23 failure modes)

| # | Failure Mode | Déclencheur | Comportement fail_closed | Criticité | Invariant/Boundary |
|---|-------------|-------------|--------------------------|-----------|-------------------|
| 1 | `missing_intent_authority` | source_module absent ou non reconnu | fail_closed → BLOCK | CRITICAL | X108_GATEWAY_REQUIRED |
| 2 | `missing_irreversibility_level` | irreversibility_level absent ou null | fail_closed → HOLD | HIGH | IntentEnvelope contract §5 |
| 3 | `missing_criticality_level` | criticality_level absent ou null | fail_closed → HOLD | HIGH | IntentEnvelope contract §5 |
| 4 | `missing_context_packet` | context_packet_refs vide ou absent | fail_closed → BLOCK | CRITICAL | X108_GATEWAY_REQUIRED |
| 5 | `invalid_context_claim_scope` | claim_scope = CLAIMABLE_FORMAL sans LEAN_PROVEN | confiance réduite + flag → X108 pénalise | MEDIUM | EXTERNAL_SIGNALS_SIGNAL_ONLY |
| 6 | `peripheral_signal_attempts_decision` | PeripheralSignalPacket émet ALLOW/HOLD/BLOCK | VIOLATION boundary → BLOCK absolu | CRITICAL | NO_ACT_FROM_PERIPHERY |
| 7 | `external_signal_attempts_x108_override` | External Signals réautorise après BLOCK X108 | VIOLATION C473 → BLOCK + audit critique | CRITICAL | EXTERNAL_SIGNALS_SIGNAL_ONLY + C473 |
| 8 | `npl_attempts_verdict` | NPL émet un verdict de décision | fail_closed → BLOCK | CRITICAL | NPL_ADVISORY_ONLY |
| 9 | `p107_p161_proven_claim_attempted` | claim_scope = LEAN_PROVEN depuis P107/P161 | fail_closed → confiance refusée | HIGH | P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY |
| 10 | `audio_entropy_law_claim_attempted` | Audio/Entropy prétend être une loi physique certifiée | confiance réduite + advisory seulement | MEDIUM | AUDIO_ENTROPY_ADVISORY_ONLY |
| 11 | `rssi_certification_claim_attempted` | claim RSSI = sécurité certifiée | fail_closed → F03+F78B required | HIGH | RSSI_EVIDENCE_ONLY |
| 12 | `rgpd_compliance_claim_attempted` | claim RGPD = ISO conforme | fail_closed → F03+F10+F78B required | HIGH | RGPD_COMPLIANCE_SCOPE_GUARD |
| 13 | `stale_temporal_context` | expires_at_tick < current_tick | stale_risk_flag → fail_closed → HOLD | HIGH | C460 + skew_negative_implies_hold |
| 14 | `temporal_receipt_missing` | 52_temporal_receipt absent pour action CRITICAL | OS3EvidenceTicket incomplet → HOLD | HIGH | X108_GATEWAY_REQUIRED + C466 |
| 15 | `missing_os3_evidence_ref` | evidence_ticket_refs vide pour action CRITICAL | fail_closed → HOLD | HIGH | OS3EvidenceTicket contract §8 |
| 16 | `conflicting_contexts` | deux ContextPackets contradictoires sans réconciliation | fail_closed → X108 pénalise / HOLD | MEDIUM | FAIL_CLOSED_PRIORITY |
| 17 | `schema_invalid` | JSON IntentEnvelope ou ContextPacket invalide | reject immédiat → fail_closed | CRITICAL | FAIL_CLOSED_PRIORITY |
| 18 | `unknown_source_status` | source_status = UNKNOWN_SOURCE | unknown_source_flag → X108 pénalise → HOLD | MEDIUM | FAIL_CLOSED_PRIORITY |
| 19 | `action_without_x108` | ACT déclenché sans DecisionTicket X108 | VIOLATION absolue → BLOCK | CRITICAL | NO_ACT_FROM_PERIPHERY + E2_NO_ACT |
| 20 | `dry_run_attempts_world_action` | harness P3 tente d'exécuter une vraie action | PLAN3_P3_SPEC_VIOLATION → BLOCK | CRITICAL | NO_WORLD_ACTION |
| 21 | `source_pack_not_deep_diffed` | source pack utilisé sans F78B validé | block F03/F06/F07/F10 → fail_closed | HIGH | F78B_REQUIRED |
| 22 | `zip_content_assumed_imported` | zip assumé extrait sans vérification | source_review_required → fail_closed | HIGH | F78B_REQUIRED |
| 23 | `pack_runtime_ready_claim_without_F78B` | pack RSSI/RGPD/Atlas/Cognitive présenté comme runtime-ready sans F78B | overauthority_flag → fail_closed | CRITICAL | F78B_REQUIRED + claim_scope_lock |

---

## Failure modes par criticité

### CRITICAL (rejet immédiat / BLOCK absolu)

| # | Failure | Raison |
|---|---------|--------|
| 1 | missing_intent_authority | Source inconnue → intention non admissible |
| 4 | missing_context_packet | Aucun contexte → gateway aveugle |
| 6 | peripheral_signal_attempts_decision | Violation NO_ACT_FROM_PERIPHERY absolue |
| 7 | external_signal_attempts_x108_override | Violation C473 — loi non-réautorisation |
| 8 | npl_attempts_verdict | Violation NPL_ADVISORY_ONLY |
| 17 | schema_invalid | Structure invalide → rejet immédiat |
| 19 | action_without_x108 | E2_NO_ACT — invariant kernel |
| 20 | dry_run_attempts_world_action | Violation P3 spec fondamentale |
| 23 | pack_runtime_ready_claim_without_F78B | Overauthority claim non vérifié |

### HIGH (fail_closed + HOLD ou BLOCK selon contexte)

| # | Failure | Comportement |
|---|---------|-------------|
| 2 | missing_irreversibility_level | → HOLD |
| 3 | missing_criticality_level | → HOLD |
| 9 | p107_p161_proven_claim_attempted | → claim refusé |
| 11 | rssi_certification_claim_attempted | → F03+F78B required |
| 12 | rgpd_compliance_claim_attempted | → F03+F10+F78B required |
| 13 | stale_temporal_context | → HOLD |
| 14 | temporal_receipt_missing | → HOLD |
| 15 | missing_os3_evidence_ref | → HOLD |
| 21 | source_pack_not_deep_diffed | → block import |
| 22 | zip_content_assumed_imported | → source_review_required |

### MEDIUM (flag + pénalité X108)

| # | Failure | Comportement |
|---|---------|-------------|
| 5 | invalid_context_claim_scope | → confiance réduite |
| 10 | audio_entropy_law_claim_attempted | → advisory uniquement |
| 16 | conflicting_contexts | → HOLD + X108 arbitre |
| 18 | unknown_source_status | → X108 pénalise |

---

## Sortie systématique de tout failure mode

```yaml
fail_closed_output:
  fail_closed_candidate: true
  no_act: true
  requires_x108_review: true
  allow_by_default: false  # JAMAIS
  suggested_decision: HOLD  # X108 décide en dernier
  failure_code: <failure_mode_name>
  dry_run: true
  world_action: false
```

---

## Tests futurs P4 (un par failure mode critique)

```
test_missing_intent_authority_blocks
test_missing_context_packet_blocks
test_peripheral_cannot_emit_decision
test_external_signal_c473_non_reauthorization
test_npl_no_verdict
test_schema_invalid_rejects_immediately
test_action_without_x108_blocks
test_dry_run_no_world_action
test_source_pack_without_f78b_blocks_import
test_pack_runtime_ready_claim_blocked_without_f78b
```
