# EXAMPLE_SAFE_DRY_RUN_INTENT
# runtime_contracts/x108_gateway_dry_run_harness/examples/
# Plan 3 P3 — Exemple documentaire JSON — NO RUNTIME EXECUTION
# Date: 2026-06-02
# Status: EXAMPLE_DOCUMENTATION_ONLY / NON_EXÉCUTABLE

---

## Statut

```
Ce document contient uniquement des exemples JSON documentaires.
Aucune donnée réelle. Aucune exécution. Aucun tool call.
Ces exemples décrivent la forme attendue, pas un appel réel.
```

---

## Exemple : IntentEnvelope safe — lecture advisory

```json
{
  "intent_id": "IE-EXAMPLE-001-SAFE-READ-ADVISORY",
  "source_module": "example_readonly_module",
  "action_candidate_type": "READ",
  "target_domain": "knowledge_graph",
  "irreversibility_level": "REVERSIBLE",
  "criticality_level": "LOW",
  "requires_x108": false,
  "context_packet_refs": [
    "CP-EXAMPLE-graphiti-readonly-001"
  ],
  "peripheral_signal_refs": [],
  "external_signal_flags": {
    "temporal_receipt": null,
    "anti_replay_check": "NOT_CHECKED",
    "stale_execution_check": "NOT_CHECKED",
    "temporal_quality": "not_applicable",
    "consequence_standing": "NOT_APPLICABLE"
  },
  "claim_scope": "CLAIMABLE_SPEC_ONLY",
  "dry_run": true,
  "comment": "Lecture advisory — criticality LOW — X108 non requis"
}
```

### Résultat théorique X108

```json
{
  "theoretical_decision_ticket": {
    "ticket_id": "DT-EXAMPLE-001-THEORETICAL",
    "intent_envelope_ref": "IE-EXAMPLE-001-SAFE-READ-ADVISORY",
    "decision": "ALLOW",
    "decision_priority": "BLOCK > HOLD > ALLOW",
    "reason_codes": ["LOW_CRITICALITY", "REVERSIBLE", "CONTEXT_COMPLETE"],
    "x108_gate_status": "PASS",
    "tau_status": "NOT_REQUIRED",
    "irreversibility_status": "REVERSIBLE",
    "dry_run": true,
    "claim_scope": "THEORETICAL_ONLY",
    "comment": "X108 seul produit ce ticket — harness P3 décrit uniquement la forme"
  }
}
```

---

## Exemple : IntentEnvelope safe — External Signals temporal context enrichi

```json
{
  "intent_id": "IE-EXAMPLE-002-SAFE-TEMPORAL-ENRICHED",
  "source_module": "example_temporal_aware_module",
  "action_candidate_type": "READ",
  "target_domain": "temporal_context",
  "irreversibility_level": "REVERSIBLE",
  "criticality_level": "MEDIUM",
  "requires_x108": true,
  "context_packet_refs": [
    "CP-EXAMPLE-temporal-context-header-001",
    "CP-EXAMPLE-consequence-boundary-001"
  ],
  "peripheral_signal_refs": [
    "PSP-EXAMPLE-anti-replay-pass-001"
  ],
  "external_signal_flags": {
    "temporal_receipt": "TR-EXAMPLE-temporal_receipt-001",
    "anti_replay_check": "PASS",
    "stale_execution_check": "PASS",
    "temporal_quality": "high",
    "consequence_standing": "VALID"
  },
  "claim_scope": "CLAIMABLE_SPEC_ONLY",
  "dry_run": true,
  "comment": "IntentEnvelope enrichi par External Signals — X108 requis — signaux advisory"
}
```

### ContextPacket associé (forme documentaire)

```json
{
  "context_id": "CP-EXAMPLE-temporal-context-header-001",
  "source_layer": "external_signals",
  "source_module": "temporal_context_header_C460",
  "readonly": true,
  "advisory_only": true,
  "confidence": 0.88,
  "claim_scope": "CLAIMABLE_SPEC_ONLY",
  "labels": ["EXTERNAL_SIGNAL_ONLY"],
  "emits_act": false,
  "emits_verdict": false,
  "source_status": "SPEC_IMPORTED",
  "context_payload": {
    "temporal_context": {
      "tick_index": 4821,
      "temporal_nonce": "EXAMPLE_NONCE_REDACTED",
      "expires_at_tick": 5000,
      "temporal_quality": "high",
      "anti_replay_status": "PASS",
      "signature_status": "VALID"
    }
  },
  "dry_run": true
}
```

### OS3EvidenceTicket théorique associé

```json
{
  "evidence_id": "EV-EXAMPLE-temporal-receipt-001-THEORETICAL",
  "linked_decision_ticket": "DT-EXAMPLE-002-THEORETICAL",
  "evidence_type": "HASH_CHAIN",
  "source": "temporal_receipt_metadata_C466",
  "hash": "sha256(EXAMPLE_RECEIPT_ID + EXAMPLE_INTENT_HASH + EXAMPLE_TICK)",
  "replay_status": "NOT_RUN",
  "verification_status": "UNVERIFIED",
  "seal_status": "NOT_SEALED",
  "claim_scope": "THEORETICAL_ONLY",
  "dry_run": true,
  "comment": "Binding théorique uniquement — P3 ne scelle pas et ne rejoue pas"
}
```

---

## Invariants respectés dans cet exemple

| Invariant | Vérifié |
|-----------|---------|
| D1_DETERMINISM | Entrée déterministe — même tick → même contexte |
| E2_NO_ACT | Pas d'ACT déclenché |
| aggregate4_fail_closed | N/A — pas de failure ici |
| advisory_only = true | ContextPacket et PeripheralSignalPacket |
| X108_GATEWAY_REQUIRED | requires_x108 = true |
| claim_scope = THEORETICAL_ONLY | DecisionTicket et OS3Evidence |
