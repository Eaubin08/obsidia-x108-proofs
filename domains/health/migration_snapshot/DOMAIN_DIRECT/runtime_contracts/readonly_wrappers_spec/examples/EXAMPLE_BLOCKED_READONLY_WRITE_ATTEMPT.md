# EXAMPLE_BLOCKED_READONLY_WRITE_ATTEMPT
# runtime_contracts/readonly_wrappers_spec/examples/
# Plan 3 P6 — Exemple documentaire — NO EXECUTION
# Date: 2026-06-02
# Status: EXAMPLE_DOCUMENTATION_ONLY / NON_EXÉCUTABLE

---

## Exemple 1 — Graphiti tente graph_write

```json
{
  "wrapper_id": "graphiti_wrapper_VIOLATION",
  "attempted_operation": "graph_write",
  "node_to_create": {"id": "NEW_NODE", "type": "EXAMPLE"},
  "_VIOLATION": "graph_write depuis wrapper readonly — violation READONLY_CONTEXT_ONLY",
  "dry_run": true
}
```

### Failure mode déclenché

```json
{
  "failure_code": "graphiti_attempts_graph_write",
  "boundary_violated": "READONLY_CONTEXT_ONLY",
  "fail_closed": true,
  "no_act": true,
  "suggested_decision": "BLOCK",
  "priority": "CRITICAL"
}
```

---

## Exemple 2 — Brody tente memory_write

```json
{
  "wrapper_id": "brody_wrapper_VIOLATION",
  "attempted_operation": "memory_write",
  "memory_update": {"id": "MEM_001", "content": "NEW_CONTENT"},
  "_VIOLATION": "memory_write sans gate X108 — violation READONLY_CONTEXT_ONLY",
  "dry_run": true
}
```

### Failure mode déclenché

```json
{
  "failure_code": "brody_attempts_memory_write",
  "boundary_violated": "READONLY_CONTEXT_ONLY",
  "fail_closed": true,
  "suggested_decision": "BLOCK",
  "priority": "CRITICAL",
  "correct_path": "IntentEnvelope(WRITE_MEMORY) → X108 → ALLOW → écriture Brody"
}
```

---

## Exemple 3 — NPL tente diagnostic médical

```json
{
  "wrapper_id": "npl_wrapper_VIOLATION",
  "attempted_output": {
    "verdict_type": "MEDICAL_DIAGNOSIS",
    "diagnosis": "EXAMPLE_CONDITION",
    "_VIOLATION": "NPL ne peut jamais diagnostiquer — NPL_ADVISORY_ONLY"
  },
  "dry_run": true
}
```

### Failure mode déclenché

```json
{
  "failure_code": "npl_attempts_diagnosis",
  "boundary_violated": "NPL_ADVISORY_ONLY",
  "fail_closed": true,
  "suggested_decision": "BLOCK",
  "priority": "CRITICAL",
  "correct_output": "ContextPacket(claim_scope=ADVISORY, hypothesis=ADVISORY_ONLY)"
}
```

---

## Exemple 4 — NPL tente moral verdict

```json
{
  "wrapper_id": "npl_wrapper_VIOLATION_2",
  "attempted_output": {
    "verdict_type": "MORAL_VERDICT",
    "verdict": "L'action est moralement justifiée",
    "_VIOLATION": "NPL ne produit jamais de verdict moral"
  }
}
```

### Failure mode déclenché

```json
{
  "failure_code": "npl_attempts_moral_verdict",
  "boundary_violated": "NPL_ADVISORY_ONLY",
  "fail_closed": true,
  "suggested_decision": "BLOCK"
}
```

---

## Exemple 5 — Wrapper bypasse X108

```json
{
  "wrapper_id": "any_wrapper_VIOLATION",
  "attempted_bypass": "DecisionTicket émis directement sans X108",
  "forged_decision": "ALLOW",
  "_VIOLATION": "Wrapper ne peut jamais produire DecisionTicket"
}
```

### Failure mode déclenché

```json
{
  "failure_code": "readonly_wrapper_context_used_as_ticket",
  "boundary_violated": "X108_GATEWAY_REQUIRED",
  "fail_closed": true,
  "suggested_decision": "BLOCK",
  "priority": "CRITICAL"
}
```
