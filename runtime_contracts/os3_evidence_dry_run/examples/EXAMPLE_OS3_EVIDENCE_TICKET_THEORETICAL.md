# EXAMPLE_OS3_EVIDENCE_TICKET_THEORETICAL
# runtime_contracts/os3_evidence_dry_run/examples/
# Plan 3 P5 — Exemple documentaire JSON — NO PROOF / NO HASH / NO EXECUTION
# Date: 2026-06-02
# Status: EXAMPLE_DOCUMENTATION_ONLY / NON_EXÉCUTABLE

---

## Statut

```
Ce document contient uniquement des exemples JSON documentaires.
Aucune donnée réelle. Aucune exécution. Aucun hash calculé. Aucun seal apposé.
Ces exemples décrivent la forme attendue, pas un ticket réel.
```

---

## Exemple 1 — OS3EvidenceTicket lié à un DecisionTicket safe (READ advisory)

### Context
L'exemple correspond au scénario `EXAMPLE_SAFE_DRY_RUN_INTENT.md` de P3.
IntentEnvelope READ advisory — criticality=LOW — X108 produit ALLOW théorique.

```json
{
  "evidence_id": "EV-EXAMPLE-001-THEORETICAL",
  "linked_decision_ticket": "DT-EXAMPLE-001-THEORETICAL",
  "evidence_type": "HASH_CHAIN",
  "source": "temporal_receipt_metadata_C466",
  "source_status": "SPEC_IMPORTED",

  "hash": "sha256(PLACEHOLDER_receipt_id + PLACEHOLDER_intent_hash + PLACEHOLDER_tick)",
  "hash_status": "PLACEHOLDER_ONLY",

  "replay_ref": null,
  "replay_status": "NOT_AVAILABLE_IN_P5",

  "seal_ref": null,
  "seal_status": "PLACEHOLDER_ONLY",

  "merkle_ref": null,
  "merkle_status": "PLACEHOLDER_ONLY",

  "verification_status": "NOT_VERIFIED_IN_P5",
  "custody_status": "DOCUMENTARY_ONLY",

  "temporal_context": {
    "tick_index": 4821,
    "tick_window": "EXAMPLE_TICK_WINDOW",
    "anti_replay_status": "PASS",
    "expires_at_tick": 5000
  },

  "bypass_check_refs": [],
  "reason_codes_trace": ["LOW_CRITICALITY", "REVERSIBLE", "CONTEXT_COMPLETE"],

  "claim_scope": "THEORETICAL_ONLY",
  "dry_run": true,
  "can_decide": false,
  "can_emit_act": false,
  "advisory_only": true,
  "world_action": false,

  "_comment": "X108 seul produit le DecisionTicket. OS3Evidence annote après décision. Hash/seal/merkle = PLACEHOLDER en P5."
}
```

### DecisionTicket lié (forme théorique)

```json
{
  "ticket_id": "DT-EXAMPLE-001-THEORETICAL",
  "decision": "ALLOW",
  "evidence_ticket_refs": ["EV-EXAMPLE-001-THEORETICAL"],
  "x108_gate_status": "PASS",
  "tau_status": "NOT_REQUIRED",
  "dry_run": true,
  "claim_scope": "THEORETICAL_ONLY",
  "_comment": "X108 seul produit ALLOW. OS3Evidence s'attache après."
}
```

---

## Exemple 2 — OS3EvidenceTicket avec temporal receipt enrichi

### Context
IntentEnvelope EXECUTE — criticality=HIGH — External Signals temporal context inclus.
X108 évalue avec OS3EvidenceTicket temporel.

```json
{
  "evidence_id": "EV-EXAMPLE-002-TEMPORAL-THEORETICAL",
  "linked_decision_ticket": "DT-EXAMPLE-002-THEORETICAL",
  "evidence_type": "HASH_CHAIN",
  "source": "temporal_receipt_metadata_C466",
  "source_status": "SPEC_IMPORTED",

  "hash": "sha256(PLACEHOLDER_TR-EX-002 + PLACEHOLDER_hash_REDACTED + PLACEHOLDER_4821)",
  "hash_status": "PLACEHOLDER_ONLY",

  "replay_ref": "REPLAY-EXAMPLE-002-PLACEHOLDER",
  "replay_status": "NOT_AVAILABLE_IN_P5",

  "seal_ref": null,
  "seal_status": "PLACEHOLDER_ONLY",

  "merkle_ref": null,
  "merkle_status": "PLACEHOLDER_ONLY",

  "verification_status": "NOT_VERIFIED_IN_P5",
  "custody_status": "DOCUMENTARY_ONLY",

  "temporal_context": {
    "receipt_id": "TR-EXAMPLE-002",
    "tick_window": "EXAMPLE_TICK_4821-4900",
    "anti_replay_status": "PASS",
    "policy_version": "POL-001",
    "signature_status": "VALID",
    "replay_pointer": "PLACEHOLDER_POINTER"
  },

  "effect_receipt_rule": "effect_receipt_only_after_ACT",

  "bypass_check_refs": ["TB-20", "TB-43", "TB-57"],
  "reason_codes_trace": ["HIGH_CRITICALITY", "TEMPORAL_CONTEXT_ENRICHED"],

  "claim_scope": "THEORETICAL_ONLY",
  "dry_run": true,
  "can_decide": false,
  "can_emit_act": false,
  "advisory_only": true,

  "_comment": "kx108_decision dans receipt = post-décision uniquement. OS3Evidence ne décide pas."
}
```

---

## Exemple 3 — OS3EvidenceTicket BYPASS_AUDIT_TRACE

### Context
P4 anti-bypass checks spec — trace d'audit bypass.

```json
{
  "evidence_id": "EV-EXAMPLE-003-BYPASS-AUDIT",
  "linked_decision_ticket": "DT-EXAMPLE-003-THEORETICAL",
  "evidence_type": "BYPASS_AUDIT_TRACE",
  "source": "anti_bypass_spec_p4",
  "source_status": "SPEC_ONLY",

  "hash": "sha256(PLACEHOLDER_bypass_check_refs + PLACEHOLDER_tick)",
  "hash_status": "PLACEHOLDER_ONLY",

  "replay_status": "NOT_AVAILABLE_IN_P5",
  "seal_status": "PLACEHOLDER_ONLY",
  "merkle_status": "PLACEHOLDER_ONLY",
  "verification_status": "NOT_VERIFIED_IN_P5",

  "bypass_check_refs": ["TB-01", "TB-04", "TB-07", "TB-21"],
  "bypass_failures_detected": [],
  "bypass_audit_status": "SPEC_ONLY_P4",

  "claim_scope": "SPEC_ONLY",
  "dry_run": true,
  "can_decide": false,
  "_comment": "Anti-bypass checks = SPEC_ONLY en P4. Evidence = SPEC_ONLY en P5. Aucun bypass prouvé."
}
```

### Invariants vérifiés dans cet exemple

| Invariant | Status en P5 |
|-----------|-------------|
| OS3Evidence ne décide pas | ✅ can_decide=false |
| Hash = PLACEHOLDER | ✅ PLACEHOLDER_ONLY |
| Replay indisponible | ✅ NOT_AVAILABLE_IN_P5 |
| Seal = PLACEHOLDER | ✅ PLACEHOLDER_ONLY |
| Merkle = PLACEHOLDER | ✅ PLACEHOLDER_ONLY |
| Bypass pas prouvé | ✅ SPEC_ONLY_P4 |
| X108 seul décideur | ✅ linked_decision_ticket produit par X108 |
