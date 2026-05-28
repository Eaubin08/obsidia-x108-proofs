# OBSIDIA F22C — POST-FREEZE FULL STACK SMOKE

Date: 20260528_065516
Mode: READONLY_RUNTIME_SMOKE
Patch: NO

## Git

## main...origin/main ?? docs/runtime/F22C_8000_GRAPHITI_STATUS_20260528_065516.json ?? docs/runtime/F22C_BRODY_8000_20260528_065516.txt ?? docs/runtime/F22C_BRODY_8012_20260528_065516.txt ?? docs/runtime/F22C_GRAPHITI_8011_STATUS_20260528_065516.json ?? docs/runtime/F22C_GRAPHITI_WORKBENCH_8011_20260528_065516.json ?? docs/runtime/F22C_NEO4J_20260528_065516.txt ?? docs/runtime/F22C_NEO4J_CYPHER_20260528_065516.txt ?? docs/runtime/F22C_PORTS_20260528_065516.txt ?? docs/runtime/F22C_RUNTIME_DASHBOARD_SUMMARY_8000_20260528_065516.json ?? docs/runtime/F22C_UI_5173_20260528_065516.json

3860184 (HEAD -> main, tag: BRODY_F22B_RUNTIME_STATE_READONLY_INTENT_REPAIR_20260528, origin/main, origin/HEAD) fix: freeze F22B runtime state readonly intent

## Services expected

- Brody backend 8000
- Brody backend 8012
- Obsidia UI 5173
- Graphiti frozen bridge 8011
- Neo4j browser 7475
- Neo4j bolt 7688

## Evidence files

- F22C_PORTS_20260528_065516.txt
- F22C_NEO4J_20260528_065516.txt
- F22C_NEO4J_CYPHER_20260528_065516.txt
- F22C_GRAPHITI_8011_STATUS_20260528_065516.json
- F22C_8000_GRAPHITI_STATUS_20260528_065516.json
- F22C_RUNTIME_DASHBOARD_SUMMARY_8000_20260528_065516.json
- F22C_BRODY_8000_20260528_065516.txt
- F22C_BRODY_8012_20260528_065516.txt
- F22C_UI_5173_20260528_065516.json
- F22C_GRAPHITI_WORKBENCH_8011_20260528_065516.json

## Expected invariants

- KX108_ONLY
- readonly=true
- emits_act=false
- memory_write=false
- graphiti_write=false
- kernel_mutation=false
- x108_mutation=false
- Graphiti V20 frozen readonly
- Neo4j live readable
- RUNTIME_STATE_READONLY active
- write_boundary_required=false

## Status

F22C_POST_FREEZE_FULL_STACK_SMOKE_LOCAL_EVIDENCE_GENERATED
