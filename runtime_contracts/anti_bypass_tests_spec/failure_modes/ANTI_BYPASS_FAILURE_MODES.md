# ANTI_BYPASS_FAILURE_MODES
# runtime_contracts/anti_bypass_tests_spec/failure_modes/
# Plan 3 P4 — Failure modes documentaires — NO TEST EXECUTION
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

## Table complète (25 failure modes)

| # | Failure Mode | Déclencheur | Comportement fail_closed | Criticité | Tests associés |
|---|-------------|-------------|--------------------------|-----------|---------------|
| 1 | `direct_act_attempt` | Module émet ACT sans DecisionTicket | BLOCK absolu → no_act | CRITICAL | TB-01, TB-02 |
| 2 | `direct_decision_attempt` | Module émet ALLOW/HOLD/BLOCK sans X108 | BLOCK → audit | CRITICAL | TB-04, TB-05, TB-06 |
| 3 | `x108_gateway_skipped` | Pipeline X108 court-circuité | BLOCK absolu | CRITICAL | TB-07 |
| 4 | `decision_ticket_forged` | DecisionTicket produit hors X108 | BLOCK absolu + audit critique | CRITICAL | TB-05, TB-06 |
| 5 | `os3_evidence_missing` | OS3EvidenceTicket absent pour CRITICAL | fail_closed → HOLD | HIGH | TB-38, TB-39 |
| 6 | `boundary_contract_missing` | BoundaryContract absent pour module | fail_closed → HOLD | HIGH | TB-37 |
| 7 | `runtime_admission_skipped` | SPEC→PROD sans DRY_RUN | BLOCKED → admission refusée | HIGH | TB-36, TB-45 |
| 8 | `tool_call_before_ticket` | Outil appelé avant DecisionTicket | BLOCK → no_act | CRITICAL | TB-03, TB-08 |
| 9 | `memory_write_before_gate` | Écriture mémoire avant X108 gate | BLOCK → no_act | CRITICAL | TB-09, TB-10 |
| 10 | `graph_write_from_readonly` | Graphiti/Brody write depuis couche readonly | BLOCK → no_act | CRITICAL | TB-15, TB-35 |
| 11 | `external_signal_override` | External Signals réautorise après BLOCK | BLOCK absolu + audit C473 | CRITICAL | TB-13, TB-17 |
| 12 | `npl_verdict_attempt` | NPL émet verdict moral ou diagnostic | BLOCK | CRITICAL | TB-21, TB-22 |
| 13 | `p107_p161_proof_claim_attempt` | P107/P161 claim LEAN_PROVEN | claim refusé → HOLD | HIGH | TB-23, TB-24 |
| 14 | `audio_entropy_law_claim_attempt` | Audio/Entropy claim loi physique certifiée | advisory uniquement | MEDIUM | TB-25 |
| 15 | `rssi_auto_block_attempt` | RSSI tente BLOCK automatique sans X108 | BLOCK → X108 requis | HIGH | TB-31 |
| 16 | `rgpd_certification_claim_attempt` | RGPD claim ISO_CERTIFIED | claim refusé → guard | HIGH | TB-33, TB-34 |
| 17 | `atlas_runtime_action_attempt` | Atlas scenario déclenche action monde | BLOCK | HIGH | TB-29 |
| 18 | `cognitive_agent_autonomy_attempt` | Agent cognitif action autonome | BLOCK | HIGH | TB-26, TB-27 |
| 19 | `source_pack_import_without_F78B` | Import zip sans audit F78B | import bloqué | HIGH | TB-46, TB-53, TB-54, TB-55 |
| 20 | `xlsx_target_path_write_authorization_attempt` | XLSX target_path = write auth | BLOCKED | HIGH | TB-52 |
| 21 | `python_file_import_from_source_pack` | .py zip importé dans runtime | BLOCK absolu | CRITICAL | TB-47, TB-48 |
| 22 | `packages_path_recreation_attempt` | packages/ recréé dans repo | BLOCK absolu | CRITICAL | TB-49 |
| 23 | `stale_temporal_context_accepted` | Contexte temporel périmé ignoré | fail_closed → HOLD | HIGH | TB-20, TB-56 |
| 24 | `unknown_source_runtime_admission` | Source UNKNOWN admise en runtime | fail_closed → HOLD | MEDIUM | TB-19 |
| 25 | `fail_open_behavior_detected` | fail_open accepté comme défaut | BLOCK absolu | CRITICAL | TB-44 |

---

## Failure modes par criticité

### CRITICAL (BLOCK absolu)

| # | Failure | Invariant noyau |
|---|---------|----------------|
| 1 | direct_act_attempt | E2_NO_ACT |
| 2 | direct_decision_attempt | X108_SOLE_AUTHORITY |
| 3 | x108_gateway_skipped | X108_GATEWAY_REQUIRED |
| 4 | decision_ticket_forged | X108_SOLE_AUTHORITY |
| 8 | tool_call_before_ticket | E2_NO_ACT |
| 9 | memory_write_before_gate | E2_NO_ACT |
| 10 | graph_write_from_readonly | READONLY_CONTEXT_ONLY |
| 11 | external_signal_override | C473 law |
| 12 | npl_verdict_attempt | NPL_ADVISORY_ONLY |
| 21 | python_file_import_from_source_pack | NO_PACKAGES_RUNTIME_BOUNDARY |
| 22 | packages_path_recreation_attempt | NO_PACKAGES_RUNTIME_BOUNDARY |
| 25 | fail_open_behavior_detected | FAIL_CLOSED_PRIORITY |

### HIGH (fail_closed + HOLD ou BLOCK selon contexte)

| # | Failure | Boundary |
|---|---------|---------|
| 5 | os3_evidence_missing | OS3EvidenceTicket |
| 6 | boundary_contract_missing | BoundaryContract |
| 7 | runtime_admission_skipped | RuntimeAdmissionContract |
| 13 | p107_p161_proof_claim_attempt | P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY |
| 15 | rssi_auto_block_attempt | RSSI_EVIDENCE_ONLY |
| 16 | rgpd_certification_claim_attempt | RGPD_COMPLIANCE_SCOPE_GUARD |
| 17 | atlas_runtime_action_attempt | ATLAS_READONLY_ADVISORY_ONLY |
| 18 | cognitive_agent_autonomy_attempt | COGNITIVE_REINTEGRATION_ADVISORY_ONLY |
| 19 | source_pack_import_without_F78B | F78B gate |
| 20 | xlsx_target_path_write_authorization_attempt | XLSX_AUDIT_ONLY |
| 23 | stale_temporal_context_accepted | EXTERNAL_SIGNALS_SIGNAL_ONLY |

### MEDIUM (flag + pénalité X108)

| # | Failure | Comportement |
|---|---------|-------------|
| 14 | audio_entropy_law_claim_attempt | advisory uniquement |
| 24 | unknown_source_runtime_admission | HOLD + X108 pénalise |

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
  runtime_allowed_now: false
```
