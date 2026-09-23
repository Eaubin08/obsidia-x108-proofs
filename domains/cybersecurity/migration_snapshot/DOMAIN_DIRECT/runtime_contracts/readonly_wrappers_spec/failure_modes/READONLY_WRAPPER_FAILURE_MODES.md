# READONLY_WRAPPER_FAILURE_MODES
# runtime_contracts/readonly_wrappers_spec/failure_modes/
# Plan 3 P6 — Failure modes documentaires — NO TEST EXECUTION
# Date: 2026-06-02

---

## Règle universelle

```
∀ failure mode f : f → fail_closed
∀ failure mode f : f → no_act
∀ failure mode f : f → requires_x108_review
∀ failure mode f : f ↛ allow_by_default
Priorité : BLOCK > HOLD > ALLOW
```

---

## Table complète (20 failure modes)

| # | Failure Mode | Déclencheur | Comportement fail_closed | Criticité | Boundary |
|---|-------------|-------------|--------------------------|-----------|---------|
| 1 | `graphiti_attempts_graph_write` | Graphiti wrapper tente d'écrire dans le graph | BLOCK absolu | CRITICAL | READONLY_CONTEXT_ONLY |
| 2 | `graphiti_attempts_decision` | Graphiti wrapper émet ALLOW/HOLD/BLOCK | BLOCK absolu | CRITICAL | X108_GATEWAY_REQUIRED |
| 3 | `graphiti_attempts_x108_override` | Graphiti réautorise après BLOCK X108 | BLOCK + audit C473 | CRITICAL | READONLY_CONTEXT_ONLY |
| 4 | `graphiti_context_claims_truth` | ContextPacket Graphiti claim_scope=VERIFIED_TRUTH | confiance réduite → HOLD | HIGH | READONLY_CONTEXT_ONLY |
| 5 | `brody_attempts_memory_write` | Brody wrapper tente d'écrire mémoire | BLOCK absolu | CRITICAL | READONLY_CONTEXT_ONLY |
| 6 | `brody_attempts_tool_call` | Brody wrapper appelle un outil | BLOCK absolu | CRITICAL | NO_ACT_FROM_PERIPHERY |
| 7 | `brody_attempts_decision` | Brody wrapper émet ALLOW/HOLD/BLOCK | BLOCK absolu | CRITICAL | X108_GATEWAY_REQUIRED |
| 8 | `brody_context_claims_authority` | ContextPacket Brody advisory_only=false | fail_closed → HOLD | HIGH | READONLY_CONTEXT_ONLY |
| 9 | `npl_attempts_proof_claim` | NPL émet claim LEAN_PROVEN ou VERIFIED_PROOF | fail_closed → BLOCK | CRITICAL | NPL_ADVISORY_ONLY |
| 10 | `npl_attempts_diagnosis` | NPL émet diagnostic (médical/légal/technique) | fail_closed → BLOCK | CRITICAL | NPL_ADVISORY_ONLY |
| 11 | `npl_attempts_moral_verdict` | NPL émet "l'action est juste/injuste" | fail_closed → BLOCK | CRITICAL | NPL_ADVISORY_ONLY |
| 12 | `npl_attempts_decision` | NPL émet ALLOW/HOLD/BLOCK directement | BLOCK absolu | CRITICAL | X108_GATEWAY_REQUIRED |
| 13 | `npl_attempts_act` | NPL déclenche ACT directement | BLOCK absolu | CRITICAL | NO_ACT_FROM_PERIPHERY |
| 14 | `readonly_wrapper_outputs_allow_hold_block` | Tout wrapper émet verdict | BLOCK absolu | CRITICAL | NO_ACT_FROM_PERIPHERY |
| 15 | `readonly_wrapper_skips_intent_envelope` | Wrapper soumets à X108 sans IntentEnvelope | fail_closed → HOLD | HIGH | X108_GATEWAY_REQUIRED |
| 16 | `readonly_wrapper_skips_x108` | Wrapper pipeline court-circuite X108 | BLOCK absolu | CRITICAL | X108_GATEWAY_REQUIRED |
| 17 | `readonly_wrapper_claim_scope_missing` | ContextPacket sans claim_scope déclaré | fail_closed → HOLD | HIGH | FAIL_CLOSED_PRIORITY |
| 18 | `readonly_wrapper_source_status_unknown` | source_status=UNKNOWN pour Graphiti/Brody/NPL | fail_closed → HOLD | MEDIUM | FAIL_CLOSED_PRIORITY |
| 19 | `readonly_wrapper_context_used_as_ticket` | ContextPacket présenté comme DecisionTicket | BLOCK absolu | CRITICAL | X108_GATEWAY_REQUIRED |
| 20 | `fail_open_on_readonly_violation` | Violation readonly → allow_by_default accepté | BLOCK absolu | CRITICAL | FAIL_CLOSED_PRIORITY |

---

## Failure modes par criticité

### CRITICAL (BLOCK absolu)

| # | Failure | Invariant |
|---|---------|----------|
| 1 | graphiti_attempts_graph_write | READONLY_CONTEXT_ONLY |
| 2 | graphiti_attempts_decision | X108_SOLE_AUTHORITY |
| 3 | graphiti_attempts_x108_override | C473_law |
| 5 | brody_attempts_memory_write | READONLY_CONTEXT_ONLY |
| 6 | brody_attempts_tool_call | E2_NO_ACT |
| 7 | brody_attempts_decision | X108_SOLE_AUTHORITY |
| 9 | npl_attempts_proof_claim | NPL_ADVISORY_ONLY |
| 10 | npl_attempts_diagnosis | NPL_ADVISORY_ONLY |
| 11 | npl_attempts_moral_verdict | NPL_ADVISORY_ONLY |
| 12 | npl_attempts_decision | X108_SOLE_AUTHORITY |
| 13 | npl_attempts_act | E2_NO_ACT |
| 14 | readonly_wrapper_outputs_allow_hold_block | E2_NO_ACT |
| 16 | readonly_wrapper_skips_x108 | X108_GATEWAY_REQUIRED |
| 19 | readonly_wrapper_context_used_as_ticket | X108_SOLE_AUTHORITY |
| 20 | fail_open_on_readonly_violation | FAIL_CLOSED_PRIORITY |

### HIGH (fail_closed + HOLD)

| # | Failure | Comportement |
|---|---------|-------------|
| 4 | graphiti_context_claims_truth | confiance réduite |
| 8 | brody_context_claims_authority | → HOLD |
| 15 | readonly_wrapper_skips_intent_envelope | → HOLD |
| 17 | readonly_wrapper_claim_scope_missing | → HOLD |

### MEDIUM

| # | Failure | Comportement |
|---|---------|-------------|
| 18 | readonly_wrapper_source_status_unknown | → HOLD + pénalité X108 |

---

## Sortie systématique

```yaml
fail_closed_output:
  fail_closed_candidate: true
  no_act: true
  requires_x108_review: true
  allow_by_default: false
  suggested_decision: HOLD
  failure_code: <failure_mode_name>
  dry_run: true
  world_action: false
  memory_write: false
  graph_write: false
```
