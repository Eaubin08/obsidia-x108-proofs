# OS3_EVIDENCE_FAILURE_MODES
# runtime_contracts/os3_evidence_dry_run/failure_modes/
# Plan 3 P5 — Failure modes documentaires — NO TEST EXECUTION
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

## Table complète (20 failure modes)

| # | Failure Mode | Déclencheur | Comportement fail_closed | Criticité | Invariant/Boundary |
|---|-------------|-------------|--------------------------|-----------|-------------------|
| 1 | `evidence_ticket_claims_decision` | OS3Evidence prétend produire ALLOW/HOLD/BLOCK | BLOCK absolu | CRITICAL | X108_GATEWAY_REQUIRED |
| 2 | `evidence_ticket_claims_act` | OS3Evidence émet ACT directement | BLOCK absolu | CRITICAL | NO_ACT_FROM_PERIPHERY |
| 3 | `evidence_missing_for_critical_intent` | CRITICAL intent sans evidence_ticket_refs | fail_closed → HOLD | HIGH | X108_GATEWAY_REQUIRED |
| 4 | `decision_ticket_ref_missing` | OS3Evidence sans linked_decision_ticket valide | fail_closed → HOLD | HIGH | OS3EvidenceTicket contract |
| 5 | `linked_decision_ticket_missing` | DecisionTicket absent pour l'evidence_id référencé | fail_closed → HOLD | HIGH | OS3EvidenceTicket contract |
| 6 | `hash_claim_without_hash` | hash_status=VERIFIED sans calcul réel | fail_closed → claim refusé | HIGH | NO_REAL_HASH_CLAIM |
| 7 | `seal_claim_without_seal` | seal_status=SEALED sans seal réel | fail_closed → claim refusé | HIGH | NO_REAL_SEAL_CLAIM |
| 8 | `merkle_claim_without_merkle` | merkle_status=VERIFIED sans Merkle réel | fail_closed → claim refusé | HIGH | NO_REAL_MERKLE_CLAIM |
| 9 | `replay_claim_without_replay` | replay_status=COMPLETED sans replay réel | fail_closed → claim refusé | HIGH | NO_REAL_REPLAY_CLAIM |
| 10 | `verification_claim_without_verification` | verification_status=VERIFIED sans vérification | fail_closed → claim refusé | HIGH | NO_PROOF_CLAIM |
| 11 | `temporal_receipt_missing` | receipt_id absent pour action CRITICAL | fail_closed → HOLD | HIGH | EXTERNAL_SIGNALS_SIGNAL_ONLY |
| 12 | `stale_temporal_receipt_used` | expires_at_tick < current_tick | fail_closed → HOLD | HIGH | C460 + skew_negative_implies_hold |
| 13 | `anti_bypass_evidence_missing` | bypass_check_refs absents pour CRITICAL | fail_closed → HOLD | MEDIUM | NO_ACT_FROM_PERIPHERY |
| 14 | `rssi_evidence_claims_certification` | RSSI evidence prétend à RSSI_CERTIFIED | fail_closed → claim refusé | HIGH | RSSI_EVIDENCE_ONLY |
| 15 | `rgpd_evidence_claims_compliance` | RGPD evidence prétend à ISO_CERTIFIED | fail_closed → claim refusé | HIGH | RGPD_COMPLIANCE_SCOPE_GUARD |
| 16 | `source_pack_evidence_without_F78B` | Pack non audité F78B utilisé comme source OS3 | fail_closed → import bloqué | HIGH | F78B gate |
| 17 | `xlsx_plan_claims_import` | XLSX target_path présenté comme evidence d'import | fail_closed → BLOCKED | HIGH | XLSX_AUDIT_ONLY |
| 18 | `os3_ticket_used_as_authority` | OS3Evidence présenté comme décision | BLOCK absolu | CRITICAL | X108_GATEWAY_REQUIRED |
| 19 | `evidence_overrides_x108` | OS3Evidence réautorise décision BLOCK X108 | BLOCK absolu + audit C473 | CRITICAL | C473 law |
| 20 | `fail_open_on_missing_evidence` | Evidence manquante → allow_by_default accepté | BLOCK absolu | CRITICAL | FAIL_CLOSED_PRIORITY |

---

## Failure modes par criticité

### CRITICAL (BLOCK absolu)

| # | Failure | Invariant |
|---|---------|----------|
| 1 | evidence_ticket_claims_decision | X108_SOLE_AUTHORITY |
| 2 | evidence_ticket_claims_act | E2_NO_ACT |
| 18 | os3_ticket_used_as_authority | X108_GATEWAY_REQUIRED |
| 19 | evidence_overrides_x108 | C473_law |
| 20 | fail_open_on_missing_evidence | FAIL_CLOSED_PRIORITY |

### HIGH (fail_closed + HOLD ou claim refusé)

| # | Failure | Comportement |
|---|---------|-------------|
| 3 | evidence_missing_for_critical_intent | → HOLD |
| 4 | decision_ticket_ref_missing | → HOLD |
| 5 | linked_decision_ticket_missing | → HOLD |
| 6 | hash_claim_without_hash | → claim refusé |
| 7 | seal_claim_without_seal | → claim refusé |
| 8 | merkle_claim_without_merkle | → claim refusé |
| 9 | replay_claim_without_replay | → claim refusé |
| 10 | verification_claim_without_verification | → claim refusé |
| 11 | temporal_receipt_missing | → HOLD |
| 12 | stale_temporal_receipt_used | → HOLD |
| 14 | rssi_evidence_claims_certification | → claim refusé |
| 15 | rgpd_evidence_claims_compliance | → claim refusé |
| 16 | source_pack_evidence_without_F78B | → import bloqué |
| 17 | xlsx_plan_claims_import | → BLOCKED |

### MEDIUM

| # | Failure | Comportement |
|---|---------|-------------|
| 13 | anti_bypass_evidence_missing | → HOLD (si CRITICAL) |

---

## Sortie systématique de tout failure mode

```yaml
fail_closed_output:
  fail_closed_candidate: true
  no_act: true
  requires_x108_review: true
  allow_by_default: false   # JAMAIS
  suggested_decision: HOLD  # X108 décide en dernier
  failure_code: <failure_mode_name>
  dry_run: true
  world_action: false
  evidence_is_real: false   # jamais affirmer en P5
```
