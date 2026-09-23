# OBSIDIA F29.0B — MEMORY / GRAPHITI DANGER CLASSIFICATION

Mode: DANGER_CLASSIFICATION_ONLY_NO_PATCH
Commit: NO
Tag: NO
Freeze: NO

HEAD: `1744efc`
Source F29.0 report: `C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\docs\runtime\OBSIDIA_F29_0_MEMORY_GRAPHITI_RECONCILIATION_AUDIT_20260529_003046.json`

## Summary

- Raw danger records: 7
- Classified hits: 35
- Confirmed runtime violations: 15
- Write-capable manual surfaces: 20
- Gate: `BLOCK_PATCH_UNTIL_REVIEW`

## Classified hits

- `periphery/brody_memory_readonly/graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only/brody_graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only_v1.py` L174 `MERGE `
  - classification: `MANUAL_GUARDED_WRITE_SURFACE_PRESENT`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: True
  - reason: A write-capable Cypher/manual apply surface exists, but it appears scoped to guarded/manual review flow rather than automatic runtime.
  - line: `MERGE (d:Document {id: $id})`
- `periphery/brody_memory_readonly/graphiti_import_apply_guarded_manual_only/brody_graphiti_import_apply_guarded_manual_only_v1.py` L256 `MERGE `
  - classification: `MANUAL_GUARDED_WRITE_SURFACE_PRESENT`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: True
  - reason: A write-capable Cypher/manual apply surface exists, but it appears scoped to guarded/manual review flow rather than automatic runtime.
  - line: `MERGE (d:BrodyMemoryDoc {id: $id})`
- `periphery/brody_memory_readonly/graphiti_import_apply_guarded_manual_only/brody_graphiti_import_apply_guarded_manual_only_v1.py` L257 `SET `
  - classification: `MANUAL_GUARDED_WRITE_SURFACE_PRESENT`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: True
  - reason: A write-capable Cypher/manual apply surface exists, but it appears scoped to guarded/manual review flow rather than automatic runtime.
  - line: `SET d.title = $title,`
- `periphery/brody_memory_readonly/graphiti_import_dry_run_from_post_human_prep_readonly/brody_graphiti_import_dry_run_from_post_human_prep_readonly_v1.py` L137 `MERGE `
  - classification: `MANUAL_GUARDED_WRITE_SURFACE_PRESENT`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: True
  - reason: A write-capable Cypher/manual apply surface exists, but it appears scoped to guarded/manual review flow rather than automatic runtime.
  - line: `"cypher_preview": "MERGE (d:Doc {id: $id}) SET d.title = $title, d.content = $content, d.source = $source",`
- `periphery/brody_memory_readonly/graphiti_import_dry_run_from_post_human_prep_readonly/brody_graphiti_import_dry_run_from_post_human_prep_readonly_v1.py` L137 `SET `
  - classification: `MANUAL_GUARDED_WRITE_SURFACE_PRESENT`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: True
  - reason: A write-capable Cypher/manual apply surface exists, but it appears scoped to guarded/manual review flow rather than automatic runtime.
  - line: `"cypher_preview": "MERGE (d:Doc {id: $id}) SET d.title = $title, d.content = $content, d.source = $source",`
- `periphery/brody_memory_readonly/neo4j_brody_guide_bridge_readonly/brody_neo4j_guide_bridge_readonly_v1.py` L115 `MERGE `
  - classification: `GRAPH_WRITE_SURFACE_REVIEW_REQUIRED`
  - confirmed_runtime_violation: True
  - confirmed_write_capability: True
  - reason: Graph write token appears without enough manual/guarded context.
  - line: `MERGE (d:BrodyMemoryDoc {id: doc.id})`
- `periphery/brody_memory_readonly/neo4j_brody_guide_bridge_readonly/brody_neo4j_guide_bridge_readonly_v1.py` L116 `SET `
  - classification: `GRAPH_WRITE_SURFACE_REVIEW_REQUIRED`
  - confirmed_runtime_violation: True
  - confirmed_write_capability: True
  - reason: Graph write token appears without enough manual/guarded context.
  - line: `SET d.title = doc.title,`
- `periphery/brody_memory_readonly/neo4j_brody_guide_bridge_readonly/brody_neo4j_guide_bridge_readonly_v1.py` L126 `MERGE `
  - classification: `GRAPH_WRITE_SURFACE_REVIEW_REQUIRED`
  - confirmed_runtime_violation: True
  - confirmed_write_capability: True
  - reason: Graph write token appears without enough manual/guarded context.
  - line: `MERGE (t:BrodyMemoryTag {name: tag})`
- `periphery/brody_memory_readonly/neo4j_brody_guide_bridge_readonly/brody_neo4j_guide_bridge_readonly_v1.py` L127 `MERGE `
  - classification: `GRAPH_WRITE_SURFACE_REVIEW_REQUIRED`
  - confirmed_runtime_violation: True
  - confirmed_write_capability: True
  - reason: Graph write token appears without enough manual/guarded context.
  - line: `MERGE (d)-[:HAS_TAG]->(t)`
- `periphery/brody_memory_readonly/neo4j_brody_guide_bridge_readonly/brody_neo4j_guide_bridge_readonly_v1.py` L137 `CREATE `
  - classification: `GRAPH_WRITE_SURFACE_REVIEW_REQUIRED`
  - confirmed_runtime_violation: True
  - confirmed_write_capability: True
  - reason: Graph write token appears without enough manual/guarded context.
  - line: `session.run("CREATE CONSTRAINT brody_memory_doc_id IF NOT EXISTS FOR (d:BrodyMemoryDoc) REQUIRE d.id IS UNIQUE")`
- `periphery/brody_memory_readonly/neo4j_brody_guide_bridge_readonly/brody_neo4j_guide_bridge_readonly_v1.py` L138 `CREATE `
  - classification: `GRAPH_WRITE_SURFACE_REVIEW_REQUIRED`
  - confirmed_runtime_violation: True
  - confirmed_write_capability: True
  - reason: Graph write token appears without enough manual/guarded context.
  - line: `session.run("CREATE CONSTRAINT brody_memory_tag_name IF NOT EXISTS FOR (t:BrodyMemoryTag) REQUIRE t.name IS UNIQUE")`
- `scripts/brody_memory_intake_gate.py` L225 `DELETE `
  - classification: `GRAPH_WRITE_SURFACE_REVIEW_REQUIRED`
  - confirmed_runtime_violation: True
  - confirmed_write_capability: True
  - reason: Graph write token appears without enough manual/guarded context.
  - line: `"// MATCH (n:BrodyImportedMemory {batch_id: 'brody-terminal-" + ts + "'}) DETACH DELETE n;",`
- `scripts/f23a1_memory_reflex_orchestrator_source_audit.py` L42 `write_transaction`
  - classification: `READONLY_BOUNDARY_REFERENCE`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: False
  - reason: Danger token appears near readonly/boundary metadata rather than a confirmed runtime write path.
  - line: `"session.write_transaction",`
- `scripts/f23a1_memory_reflex_orchestrator_source_audit.py` L42 `session.write_transaction`
  - classification: `READONLY_BOUNDARY_REFERENCE`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: False
  - reason: Danger token appears near readonly/boundary metadata rather than a confirmed runtime write path.
  - line: `"session.write_transaction",`
- `scripts/f23a1_memory_reflex_orchestrator_source_audit.py` L43 `execute_write`
  - classification: `READONLY_BOUNDARY_REFERENCE`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: False
  - reason: Danger token appears near readonly/boundary metadata rather than a confirmed runtime write path.
  - line: `"execute_write",`
- `scripts/f23a1_memory_reflex_orchestrator_source_audit.py` L44 `MERGE `
  - classification: `GRAPH_WRITE_SURFACE_REVIEW_REQUIRED`
  - confirmed_runtime_violation: True
  - confirmed_write_capability: True
  - reason: Graph write token appears without enough manual/guarded context.
  - line: `"MERGE ",`
- `scripts/f23a1_memory_reflex_orchestrator_source_audit.py` L45 `CREATE `
  - classification: `GRAPH_WRITE_SURFACE_REVIEW_REQUIRED`
  - confirmed_runtime_violation: True
  - confirmed_write_capability: True
  - reason: Graph write token appears without enough manual/guarded context.
  - line: `"CREATE ",`
- `scripts/f23a1_memory_reflex_orchestrator_source_audit.py` L46 `SET `
  - classification: `GRAPH_WRITE_SURFACE_REVIEW_REQUIRED`
  - confirmed_runtime_violation: True
  - confirmed_write_capability: True
  - reason: Graph write token appears without enough manual/guarded context.
  - line: `"SET ",`
- `scripts/f23a1_memory_reflex_orchestrator_source_audit.py` L47 `DELETE `
  - classification: `GRAPH_WRITE_SURFACE_REVIEW_REQUIRED`
  - confirmed_runtime_violation: True
  - confirmed_write_capability: True
  - reason: Graph write token appears without enough manual/guarded context.
  - line: `"DELETE ",`
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py` L59 `memory_write=True`
  - classification: `READONLY_BOUNDARY_REFERENCE`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: False
  - reason: Danger token appears near readonly/boundary metadata rather than a confirmed runtime write path.
  - line: `"memory_write=True",`
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py` L60 `graphiti_write=True`
  - classification: `READONLY_BOUNDARY_REFERENCE`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: False
  - reason: Danger token appears near readonly/boundary metadata rather than a confirmed runtime write path.
  - line: `"graphiti_write=True",`
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py` L61 `neo4j_write=True`
  - classification: `READONLY_BOUNDARY_REFERENCE`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: False
  - reason: Danger token appears near readonly/boundary metadata rather than a confirmed runtime write path.
  - line: `"neo4j_write=True",`
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py` L62 `kernel_mutation=True`
  - classification: `READONLY_BOUNDARY_REFERENCE`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: False
  - reason: Danger token appears near readonly/boundary metadata rather than a confirmed runtime write path.
  - line: `"kernel_mutation=True",`
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py` L63 `x108_mutation=True`
  - classification: `READONLY_BOUNDARY_REFERENCE`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: False
  - reason: Danger token appears near readonly/boundary metadata rather than a confirmed runtime write path.
  - line: `"x108_mutation=True",`
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py` L64 `emits_act=True`
  - classification: `READONLY_BOUNDARY_REFERENCE`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: False
  - reason: Danger token appears near readonly/boundary metadata rather than a confirmed runtime write path.
  - line: `"emits_act=True",`
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py` L65 `can_emit_act=True`
  - classification: `READONLY_BOUNDARY_REFERENCE`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: False
  - reason: Danger token appears near readonly/boundary metadata rather than a confirmed runtime write path.
  - line: `"can_emit_act=True",`
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py` L66 `runtime_execute=True`
  - classification: `READONLY_BOUNDARY_REFERENCE`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: False
  - reason: Danger token appears near readonly/boundary metadata rather than a confirmed runtime write path.
  - line: `"runtime_execute=True",`
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py` L67 `write_transaction`
  - classification: `READONLY_BOUNDARY_REFERENCE`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: False
  - reason: Danger token appears near readonly/boundary metadata rather than a confirmed runtime write path.
  - line: `"write_transaction",`
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py` L68 `execute_write`
  - classification: `READONLY_BOUNDARY_REFERENCE`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: False
  - reason: Danger token appears near readonly/boundary metadata rather than a confirmed runtime write path.
  - line: `"execute_write",`
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py` L69 `write_transaction`
  - classification: `READONLY_BOUNDARY_REFERENCE`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: False
  - reason: Danger token appears near readonly/boundary metadata rather than a confirmed runtime write path.
  - line: `"session.write_transaction",`
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py` L69 `session.write_transaction`
  - classification: `READONLY_BOUNDARY_REFERENCE`
  - confirmed_runtime_violation: False
  - confirmed_write_capability: False
  - reason: Danger token appears near readonly/boundary metadata rather than a confirmed runtime write path.
  - line: `"session.write_transaction",`
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py` L70 `CREATE `
  - classification: `GRAPH_WRITE_SURFACE_REVIEW_REQUIRED`
  - confirmed_runtime_violation: True
  - confirmed_write_capability: True
  - reason: Graph write token appears without enough manual/guarded context.
  - line: `"CREATE ",`
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py` L71 `MERGE `
  - classification: `GRAPH_WRITE_SURFACE_REVIEW_REQUIRED`
  - confirmed_runtime_violation: True
  - confirmed_write_capability: True
  - reason: Graph write token appears without enough manual/guarded context.
  - line: `"MERGE ",`
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py` L72 `DELETE `
  - classification: `GRAPH_WRITE_SURFACE_REVIEW_REQUIRED`
  - confirmed_runtime_violation: True
  - confirmed_write_capability: True
  - reason: Graph write token appears without enough manual/guarded context.
  - line: `"DELETE ",`
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py` L73 `SET `
  - classification: `GRAPH_WRITE_SURFACE_REVIEW_REQUIRED`
  - confirmed_runtime_violation: True
  - confirmed_write_capability: True
  - reason: Graph write token appears without enough manual/guarded context.
  - line: `"SET ",`

## Next

F29.1_QUARANTINE_OR_GUARD_GRAPHITI_WRITE_SURFACES

## Boundary

```text
DECISION_AUTHORITY=KX108_ONLY
readonly=true
memory_write=false
graphiti_write=false
neo4j_write=false
emits_act=false
runtime_execute=false
kernel_mutation=false
x108_mutation=false
```

## Status

F29_0B_MEMORY_GRAPHITI_DANGER_CLASSIFICATION_DONE
