# EXAMPLE_MISSING_EVIDENCE_BLOCK
# runtime_contracts/os3_evidence_dry_run/examples/
# Plan 3 P5 — Exemple documentaire — NO EXECUTION
# Date: 2026-06-02
# Status: EXAMPLE_DOCUMENTATION_ONLY / NON_EXÉCUTABLE

---

## Statut

```
Ce document illustre des cas où evidence manquante → fail_closed.
Aucune exécution. Aucune donnée réelle.
```

---

## Exemple 1 — CRITICAL intent sans OS3EvidenceTicket

```json
{
  "intent_id": "IE-EXAMPLE-BLOCKED-EVIDENCE-001",
  "source_module": "example_critical_module",
  "action_candidate_type": "EXECUTE",
  "target_domain": "critical_system",
  "irreversibility_level": "IRREVERSIBLE",
  "criticality_level": "CRITICAL",
  "requires_x108": true,
  "context_packet_refs": ["CP-001"],
  "evidence_ticket_refs": [],
  "_VIOLATION": "evidence_ticket_refs vide pour action CRITICAL",
  "dry_run": true
}
```

### Failure mode déclenché

```json
{
  "failure_code": "evidence_missing_for_critical_intent",
  "trigger": "evidence_ticket_refs=[] pour criticality=CRITICAL",
  "fail_closed_candidate": true,
  "no_act": true,
  "requires_x108_review": true,
  "allow_by_default": false,
  "suggested_decision": "HOLD",
  "x108_note": "X108 évalue avec pénalité — evidence manquante = confiance réduite",
  "dry_run": true
}
```

---

## Exemple 2 — Temporal receipt absent pour action irréversible

```json
{
  "intent_id": "IE-EXAMPLE-BLOCKED-EVIDENCE-002",
  "action_candidate_type": "WRITE",
  "irreversibility_level": "IRREVERSIBLE",
  "criticality_level": "HIGH",
  "requires_x108": true,
  "context_packet_refs": ["CP-002"],
  "external_signal_flags": {
    "temporal_receipt": null,
    "_NOTE": "temporal_receipt absent — C466 requirement not met"
  },
  "evidence_ticket_refs": [],
  "_VIOLATION": "temporal_receipt null pour IRREVERSIBLE action",
  "dry_run": true
}
```

### Failure modes déclenchés

```json
{
  "failures": [
    {
      "failure_code": "temporal_receipt_missing",
      "trigger": "temporal_receipt=null pour IRREVERSIBLE",
      "boundary": "EXTERNAL_SIGNALS_SIGNAL_ONLY + C466",
      "suggested_decision": "HOLD",
      "fail_closed": true
    },
    {
      "failure_code": "evidence_missing_for_critical_intent",
      "trigger": "evidence_ticket_refs=[] pour HIGH+IRREVERSIBLE",
      "suggested_decision": "HOLD",
      "fail_closed": true
    }
  ],
  "aggregate_result": "HOLD",
  "dry_run": true
}
```

---

## Exemple 3 — OS3Evidence tentant de forcer un ALLOW

```json
{
  "evidence_id": "EV-EXAMPLE-FORGED-ALLOW",
  "evidence_type": "DECISION_OVERRIDE",
  "_VIOLATION": "OS3Evidence tente de produire ALLOW",
  "decision_override": "ALLOW",
  "can_decide": true,
  "_VIOLATION_2": "can_decide=true — violation absolue",
  "dry_run": true
}
```

### Failure modes déclenchés

```json
{
  "failures": [
    {
      "failure_code": "evidence_ticket_claims_decision",
      "trigger": "evidence contient decision_override=ALLOW",
      "boundary_violated": "X108_GATEWAY_REQUIRED",
      "fail_closed": true,
      "suggested_decision": "BLOCK",
      "priority": "CRITICAL"
    },
    {
      "failure_code": "os3_ticket_used_as_authority",
      "trigger": "can_decide=true dans OS3Evidence",
      "boundary_violated": "X108_GATEWAY_REQUIRED",
      "fail_closed": true,
      "suggested_decision": "BLOCK",
      "priority": "CRITICAL"
    }
  ],
  "aggregate_result": "BLOCK",
  "dry_run": true
}
```
