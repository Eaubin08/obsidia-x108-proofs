# EXAMPLE_BLOCKED_DRY_RUN_INTENT
# runtime_contracts/x108_gateway_dry_run_harness/examples/
# Plan 3 P3 — Exemple documentaire JSON — NO RUNTIME EXECUTION
# Date: 2026-06-02
# Status: EXAMPLE_DOCUMENTATION_ONLY / NON_EXÉCUTABLE

---

## Statut

```
Ce document contient uniquement des exemples JSON documentaires.
Aucune donnée réelle. Aucune exécution. Aucun tool call.
Ces exemples montrent des intentions bloquées pour illustration.
```

---

## Exemple 1 : IntentEnvelope BLOQUÉ — peripheral prétend à la décision

```json
{
  "intent_id": "IE-EXAMPLE-BLOCKED-001-PERIPHERAL-DECISION",
  "source_module": "example_rogue_peripheral",
  "action_candidate_type": "DECIDE",
  "target_domain": "x108_gateway",
  "irreversibility_level": "IRREVERSIBLE",
  "criticality_level": "CRITICAL",
  "requires_x108": false,
  "_VIOLATION": "peripheral tente de décider sans X108",
  "claim_scope": "CLAIMABLE_FORMAL",
  "_VIOLATION_CLAIM": "CLAIMABLE_FORMAL sans LEAN_PROVEN — overauthority",
  "dry_run": true
}
```

### Failure modes déclenchés

```json
{
  "failure_analysis": {
    "failures": [
      {
        "code": "missing_x108_requirement",
        "reason": "criticality=CRITICAL mais requires_x108=false",
        "result": "fail_closed",
        "suggested_decision": "BLOCK"
      },
      {
        "code": "peripheral_signal_attempts_decision",
        "reason": "action_candidate_type=DECIDE depuis périphérie",
        "result": "fail_closed",
        "suggested_decision": "BLOCK",
        "priority": "CRITICAL"
      },
      {
        "code": "invalid_context_claim_scope",
        "reason": "CLAIMABLE_FORMAL sans LEAN_PROVEN",
        "result": "confidence_penalty",
        "suggested_decision": "HOLD"
      }
    ],
    "aggregate_result": "BLOCK",
    "reasoning": "BLOCK > HOLD > ALLOW — priorité absolue",
    "theoretical_decision": "BLOCK",
    "dry_run": true
  }
}
```

---

## Exemple 2 : IntentEnvelope BLOQUÉ — temporal context stale

```json
{
  "intent_id": "IE-EXAMPLE-BLOCKED-002-STALE-TEMPORAL",
  "source_module": "example_delayed_module",
  "action_candidate_type": "EXECUTE",
  "target_domain": "execution_layer",
  "irreversibility_level": "IRREVERSIBLE",
  "criticality_level": "HIGH",
  "requires_x108": true,
  "context_packet_refs": [
    "CP-EXAMPLE-stale-temporal-001"
  ],
  "external_signal_flags": {
    "temporal_receipt": null,
    "anti_replay_check": "FAIL",
    "_NOTE": "anti_replay_check=FAIL — nonce déjà vu dans horizon",
    "stale_execution_check": "FAIL",
    "_NOTE2": "stale_execution_check=FAIL — tick expiré"
  },
  "dry_run": true
}
```

### ContextPacket stale (forme documentaire)

```json
{
  "context_id": "CP-EXAMPLE-stale-temporal-001",
  "source_layer": "external_signals",
  "source_module": "temporal_context_header_C460",
  "readonly": true,
  "advisory_only": true,
  "context_payload": {
    "temporal_context": {
      "tick_index": 1000,
      "expires_at_tick": 900,
      "_STALE": "expires_at_tick < tick_index — contexte périmé"
    }
  }
}
```

### Failure modes déclenchés

```json
{
  "failure_analysis": {
    "failures": [
      {
        "code": "stale_temporal_context",
        "reason": "expires_at_tick=900 < current_tick=1000",
        "result": "stale_risk_flag=true → fail_closed",
        "suggested_decision": "HOLD"
      },
      {
        "code": "anti_replay_horizon_exceeded",
        "reason": "anti_replay_check=FAIL — nonce replay détecté",
        "result": "fail_closed",
        "suggested_decision": "BLOCK",
        "invariant": "C463"
      },
      {
        "code": "temporal_receipt_missing",
        "reason": "IRREVERSIBLE action sans temporal_receipt",
        "result": "OS3EvidenceTicket incomplet → fail_closed",
        "suggested_decision": "HOLD or BLOCK"
      }
    ],
    "aggregate_result": "BLOCK",
    "reasoning": "BLOCK > HOLD — anti_replay BLOCK prend priorité",
    "theoretical_decision": "BLOCK",
    "dry_run": true
  }
}
```

---

## Exemple 3 : IntentEnvelope BLOQUÉ — NPL prétend au verdict

```json
{
  "intent_id": "IE-EXAMPLE-BLOCKED-003-NPL-VERDICT-ATTEMPT",
  "source_module": "example_npl_module",
  "action_candidate_type": "WRITE",
  "target_domain": "memory_graph",
  "irreversibility_level": "PARTIALLY_REVERSIBLE",
  "criticality_level": "HIGH",
  "requires_x108": true,
  "context_packet_refs": ["CP-EXAMPLE-npl-001"],
  "_VIOLATION": "ContextPacket NPL contient emits_verdict=true",
  "dry_run": true
}
```

### ContextPacket NPL violant (forme documentaire)

```json
{
  "context_id": "CP-EXAMPLE-npl-001",
  "source_layer": "npl",
  "source_module": "narrative_provenance_layer",
  "readonly": true,
  "advisory_only": false,
  "_VIOLATION": "advisory_only=false — NPL prétend à la souveraineté",
  "emits_verdict": true,
  "_VIOLATION_2": "emits_verdict=true — violation NPL_ADVISORY_ONLY"
}
```

### Failure modes déclenchés

```json
{
  "failure_analysis": {
    "failures": [
      {
        "code": "npl_attempts_verdict",
        "reason": "emits_verdict=true depuis NPL",
        "boundary_violated": "NPL_ADVISORY_ONLY",
        "result": "fail_closed",
        "suggested_decision": "BLOCK",
        "priority": "CRITICAL"
      }
    ],
    "aggregate_result": "BLOCK",
    "theoretical_decision": "BLOCK",
    "dry_run": true
  }
}
```
