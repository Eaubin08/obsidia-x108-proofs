# EXAMPLE_NPL_ADVISORY_CONTEXT_PACKET
# runtime_contracts/readonly_wrappers_spec/examples/
# Plan 3 P6 — Exemple documentaire JSON — NO NPL DECISION / NO EXECUTION
# Date: 2026-06-02
# Status: EXAMPLE_DOCUMENTATION_ONLY / NON_EXÉCUTABLE

---

## ContextPacket NPL advisory safe

```json
{
  "context_id": "CP-NPL-EXAMPLE-001-ADVISORY",
  "source_layer": "npl",
  "source_module": "npl_readonly_wrapper",
  "readonly": true,
  "advisory_only": true,
  "confidence": 0.72,
  "claim_scope": "ADVISORY",
  "labels": ["NPL_ADVISORY_NOT_SOVEREIGN", "ADVISORY"],
  "emits_act": false,
  "emits_verdict": false,
  "can_decide": false,
  "decision_authority": "KX108_ONLY",
  "source_status": "SPEC_IMPORTED",
  "context_payload": {
    "narrative_provenance": "ADVISORY_NARRATIVE_PLACEHOLDER",
    "hypothesis": "ADVISORY_HYPOTHESIS_PLACEHOLDER",
    "metric_advisory": {
      "narrative_confidence": 0.72,
      "provenance_score": 0.68,
      "hypothesis_weight": 0.65
    },
    "claim_scope": "ADVISORY",
    "sovereign": false,
    "can_decide": false
  },
  "dry_run": true,
  "_comment": "NPL advisory. Jamais de verdict moral. Jamais de diagnostic. Confiance max 0.80."
}
```

## PeripheralSignalPacket NPL optionnel

```json
{
  "signal_id": "PSP-NPL-EXAMPLE-001-METRIC",
  "signal_type": "NPL_ADVISORY_METRIC",
  "source_module": "npl_readonly_wrapper",
  "source_status": "SPEC_IMPORTED",
  "metric_name": "narrative_confidence",
  "metric_value": 0.72,
  "metric_range": {"min": 0.0, "max": 0.80},
  "advisory_only": true,
  "emits_act": false,
  "emits_allow_hold_block": false,
  "label": "NPL_ADVISORY_NOT_SOVEREIGN",
  "boundary": "NPL_ADVISORY_ONLY",
  "dry_run": true,
  "_comment": "Signal NPL advisory uniquement. X108 utilise ce signal pour enrichir reason_codes. Jamais décision directe."
}
```
