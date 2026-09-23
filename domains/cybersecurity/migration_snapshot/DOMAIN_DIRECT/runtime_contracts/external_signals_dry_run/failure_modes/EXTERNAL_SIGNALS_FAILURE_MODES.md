# EXTERNAL_SIGNALS_FAILURE_MODES
# runtime_contracts/external_signals_dry_run/failure_modes/
# Plan 3 P2 — Failure modes documentaires — NO RUNTIME EXECUTION
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

## Table complète des failure modes

| # | Failure Mode | Déclencheur | Comportement fail_closed | Invariant/Composant |
|---|-------------|-------------|--------------------------|---------------------|
| 1 | `missing_temporal_context` | tick_index absent ou null | fail_closed → HOLD candidat → X108 évalue avec pénalité | C460 validation |
| 2 | `invalid_tick` | expires_at_tick <= current_tick | stale_risk_flag = true → fail_closed → X108 → HOLD ou BLOCK | C460 + skew_negative_implies_hold |
| 3 | `stale_execution_detected` | tick_at_evaluation - tick_at_request > stale_threshold_ticks | stale_execution_check = FAIL → PeripheralSignalPacket(FAIL) → X108 → HOLD | C469 |
| 4 | `anti_replay_horizon_exceeded` | replay_seen = true OU nonce dans horizon | anti_replay_check = FAIL → fail_closed_candidate → X108 → BLOCK | C463 |
| 5 | `temporal_receipt_missing` | receipt_id absent pour CRITICAL action | evidence incomplet → OS3EvidenceTicket vide → X108 pénalise → HOLD ou BLOCK | C466/52 |
| 6 | `consequence_boundary_missing` | 53_consequence_boundary absent pour action irréversible | consequence_standing = UNKNOWN → fail_closed flag → X108 → HOLD | C472/53 |
| 7 | `external_signal_attempts_decision` | adapter émet ALLOW/HOLD/BLOCK directement | PLAN3_P2_BACKUP_GUARD_VIOLATION → reject → fail_closed → BLOCK | EXTERNAL_SIGNALS_SIGNAL_ONLY |
| 8 | `external_signal_attempts_act` | emits_act = true depuis adapter | PLAN3_P2_BACKUP_GUARD_VIOLATION → reject → fail_closed | NO_ACT_FROM_PERIPHERY |
| 9 | `external_signal_attempts_tool_call` | outil externe appelé depuis adapter | reject → fail_closed → BLOCK | NO_PACKAGES_RUNTIME_BOUNDARY |
| 10 | `external_signal_attempts_x108_override` | adapter réautorise décision refusée par X108 | VIOLATION C473 → reject → fail_closed → BLOCK absolu | EXTERNAL_SIGNALS_SIGNAL_ONLY + C473 |
| 11 | `source_status_unknown` | source_status = UNKNOWN_SOURCE | unknown_source_flag = true → X108 pénalise → HOLD candidat | FAIL_CLOSED_PRIORITY |
| 12 | `schema_invalid` | JSON PeripheralSignalPacket ou ContextPacket invalide | reject → fail_closed | FAIL_CLOSED_PRIORITY |
| 13 | `claim_scope_conflict` | claim_scope = CLAIMABLE_FORMAL sans LEAN_PROVEN | overauthority_flag → X108 pénalise → confiance réduite | EXTERNAL_SIGNALS_SIGNAL_ONLY |
| 14 | `signature_status_invalid` | signature_status = INVALID dans C460 | signature_invalid_flag → fail_closed → HOLD ou BLOCK | C460 validation |
| 15 | `low_temporal_quality` | temporal_quality = low | low_quality_flag → X108 réduit le poids du signal | C460 |
| 16 | `replay_pointer_missing` | replay_pointer absent dans 52_temporal_receipt | evidence_incomplete_flag → OS3EvidenceTicket partial | C466/52 |
| 17 | `consequence_standing_invalid` | executable_standing_status = INVALID | continuation_blocked_flag → fail_closed → HOLD | C472 |
| 18 | `wrapper_reauthoring_attempted` | adapter tente de réautoriser après BLOCK X108 | VIOLATION C473 → fail_closed → BLOCK + audit critique | C473 — loi non-réautorisation |
| 19 | `temporal_confidence_overclaim` | confidence = 1.0 depuis External Signals | overconfidence_flag → confiance max = 0.95 pour External Signals | FAIL_CLOSED_PRIORITY |
| 20 | `stale_external_signal_ref` | signal référencé dans IntentEnvelope mais expiré | stale_external_ref_flag → X108 ignore ou pénalise | C469 |

---

## Failure modes par criticité

### CRITICAL (rejet immédiat)

| Failure | Raison |
|---------|--------|
| external_signal_attempts_decision | Violation boundary fondamentale |
| external_signal_attempts_act | Violation NO_ACT absolu |
| external_signal_attempts_x108_override | Violation C473 — loi de non-réautorisation |
| wrapper_reauthoring_attempted | Violation C473 — BLOCK absolu + audit |

### HIGH (fail_closed + HOLD ou BLOCK)

| Failure | Comportement |
|---------|-------------|
| anti_replay_horizon_exceeded | → BLOCK |
| invalid_tick | → HOLD puis BLOCK si persistant |
| signature_status_invalid | → HOLD |
| consequence_standing_invalid | → HOLD |

### MEDIUM (flag + pénalité X108)

| Failure | Comportement |
|---------|-------------|
| missing_temporal_context | → HOLD candidat |
| stale_execution_detected | → HOLD signal |
| temporal_receipt_missing | → HOLD ou BLOCK selon criticality |
| source_status_unknown | → X108 pénalise |
| claim_scope_conflict | → confiance réduite |

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
  signal_type: EXTERNAL_TEMPORAL
  label: EXTERNAL_SIGNAL_ONLY
```

---

## Tests futurs (P4) — un par failure mode critique

- `test_anti_replay_fail_closes` → failure #4
- `test_stale_execution_hold_signal` → failure #3
- `test_external_signal_cannot_authorize_act` → failure #8
- `test_c473_wrapper_non_reauthoring` → failure #10 + #18
- `test_external_signal_no_decision` → failure #7
- `test_temporal_receipt_missing_hold` → failure #5
