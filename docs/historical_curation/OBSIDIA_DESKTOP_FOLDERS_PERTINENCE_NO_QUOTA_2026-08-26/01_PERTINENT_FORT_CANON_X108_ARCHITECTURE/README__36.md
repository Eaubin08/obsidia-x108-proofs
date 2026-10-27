# OBSIDIA_BRANCHABLE_ATLAS_FULL_V0

Pack offline branchable.

## Statut
OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_READONLY_ZIP_PASS

## Counts
```json
{
  "final_world_domains_A": 10,
  "final_open_source_B": 7,
  "grimoire_concept_modules_M": 24,
  "external_actors": 41,
  "open_source_projects": 39,
  "agents": 185,
  "protocols": 188,
  "total_modules_in_registry": 41
}
```

## Validation
```bash
python -m pytest tests/test_world_protocol_atlas_readonly.py -q
```

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
