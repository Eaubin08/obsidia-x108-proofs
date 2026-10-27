# Conversation à partir d’archives

## Protocol ID
conversation_a_partir_d_archives

## Élément technique
EchoMorph

## Rôle
Branchement futur readonly/contextuel pour Obsidia.

## Source module
M04

## Boundary
```json
{
  "readonly": true,
  "advisory_only": true,
  "context_signal_only": true,
  "decision_authority": "KX108_ONLY",
  "allowed_to_decide": false,
  "allowed_to_act": false,
  "can_decide": false,
  "can_emit_act": false,
  "emits_act": false,
  "emits_verdict": false,
  "memory_write": false,
  "graphiti_write": false,
  "neo4j_write": false,
  "kernel_mutation": false,
  "x108_mutation": false,
  "runtime_execute": false
}
```

## Statut
SPEC_READY · READONLY_CONTEXT_ONLY
