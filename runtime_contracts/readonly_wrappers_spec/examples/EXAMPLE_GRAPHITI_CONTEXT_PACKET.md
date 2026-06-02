# EXAMPLE_GRAPHITI_CONTEXT_PACKET
# runtime_contracts/readonly_wrappers_spec/examples/
# Plan 3 P6 — Exemple documentaire JSON — NO GRAPHITI WRITE / NO EXECUTION
# Date: 2026-06-02
# Status: EXAMPLE_DOCUMENTATION_ONLY / NON_EXÉCUTABLE

---

## ContextPacket Graphiti safe (READ advisory)

```json
{
  "context_id": "CP-GRAPHITI-EXAMPLE-001-READONLY",
  "source_layer": "graphiti",
  "source_module": "graphiti_readonly_wrapper",
  "readonly": true,
  "advisory_only": true,
  "confidence": 0.82,
  "claim_scope": "CONTEXT_REFERENCE",
  "labels": ["GRAPHITI_CONTEXT_ONLY", "READONLY"],
  "emits_act": false,
  "emits_verdict": false,
  "can_decide": false,
  "decision_authority": "KX108_ONLY",
  "source_status": "READONLY",
  "context_payload": {
    "entities": ["ENTITY_EXAMPLE_1", "ENTITY_EXAMPLE_2"],
    "relations": ["RELATION_EXAMPLE_1"],
    "retrieval_trace": "ADVISORY_TRACE_PLACEHOLDER",
    "memory_summary": "ADVISORY_SUMMARY_PLACEHOLDER",
    "graphiti_version": "V20",
    "brody_corpus_present": false
  },
  "dry_run": true,
  "_comment": "ContextPacket Graphiti readonly. Jamais de décision. Jamais d'écriture. Brody absent de V20."
}
```

### Usage dans IntentEnvelope

```json
{
  "intent_id": "IE-EXAMPLE-GRAPHITI-001",
  "context_packet_refs": ["CP-GRAPHITI-EXAMPLE-001-READONLY"],
  "decision_authority": "KX108_ONLY",
  "_comment": "Graphiti enrichit — X108 décide"
}
```
