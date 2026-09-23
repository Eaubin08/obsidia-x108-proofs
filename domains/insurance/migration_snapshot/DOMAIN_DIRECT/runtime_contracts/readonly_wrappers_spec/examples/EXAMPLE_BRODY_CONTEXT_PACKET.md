# EXAMPLE_BRODY_CONTEXT_PACKET
# runtime_contracts/readonly_wrappers_spec/examples/
# Plan 3 P6 — Exemple documentaire JSON — NO BRODY WRITE / NO EXECUTION
# Date: 2026-06-02
# Status: EXAMPLE_DOCUMENTATION_ONLY / NON_EXÉCUTABLE

---

## ContextPacket Brody safe (READ advisory)

```json
{
  "context_id": "CP-BRODY-EXAMPLE-001-READONLY",
  "source_layer": "brody",
  "source_module": "brody_readonly_wrapper",
  "readonly": true,
  "advisory_only": true,
  "confidence": 0.75,
  "claim_scope": "CONTEXT_REFERENCE",
  "labels": ["BRODY_CONTEXT_ONLY", "READONLY"],
  "emits_act": false,
  "emits_verdict": false,
  "can_decide": false,
  "decision_authority": "KX108_ONLY",
  "source_status": "READONLY",
  "context_payload": {
    "memory_refs": ["MEMORY_EXAMPLE_1"],
    "advisory_labels": ["CONTEXT_ADVISORY"],
    "interaction_trace": "ADVISORY_TRACE_PLACEHOLDER",
    "episodic_summary": "ADVISORY_SUMMARY_PLACEHOLDER",
    "brody_in_graphiti_v20": false
  },
  "dry_run": true,
  "_comment": "Brody readonly. Corpus absent Graphiti V20. Jamais d'écriture mémoire sans gate X108."
}
```

## ContextPacket Brody — écriture mémoire future (gate X108)

```json
{
  "_note": "Cet exemple montre ce qui sera requis PLUS TARD pour une écriture mémoire Brody.",
  "_not_p6": "En P6 : can_write_memory=false toujours.",
  "future_write_request": {
    "intent_type": "WRITE_MEMORY",
    "requires_x108": true,
    "gate_required": "X108_ALLOW + gate humaine",
    "write_allowed_in_p6": false,
    "_comment": "Écriture future = IntentEnvelope → X108 → ALLOW → écriture Brody"
  }
}
```
