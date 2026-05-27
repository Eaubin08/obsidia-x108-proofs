# LIVE_CONNECTORS_PHASE7C_WORKBENCH_VALIDATION_20260527

Status: PASS_READY_FOR_COMMIT

## Scope

Validate Workbench live connector after Brody/Graphiti readonly reconnect.

## Validated flow

Workbench 5173 -> Vite proxy /api/engine -> Brody API 8012 -> Graphiti V20 readonly proxy -> ObsidiaShell 8011.

## Results

- Workbench 5173 = HTTP 200
- /api/engine/openapi.json = HTTP 200
- /api/brody/chat route visible through Workbench proxy
- WORKBENCH_TO_BRODY_ROUTE_OK
- /api/engine/api/graphiti/status = GRAPHITI_V20_HTTP

## Graphiti V20 through Workbench proxy

- graphiti_status = FROZEN_READONLY
- entity_count = 167
- relation_count = 477
- indexed_episodes = 20
- failed_episodes = 0
- live_neo4j_dependency = false
- x108_merge_status = NOT_MERGED
- commit_status = LOCAL_ONLY
- proxy_source = GRAPHITI_V20_HTTP

## Boundary invariants

- readonly = true
- advisory_only = true
- emits_act = false
- emits_verdict = false
- decision_authority = KX108_ONLY
- memory_write = false
- kernel_mutation = false
- x108_mutation = false
- graphiti_write = false
- neo4j_write = false
- real_action = false

## Not changed

- No runtime patch.
- No kernel mutation.
- No X108 mutation.
- No Graphiti write.
- No Neo4j write.
- No Decision Gateway integration.
- No Danswer integration.
- No secret or real .env file.

## Current live map

- 5173 = Workbench UI
- 8012 = Brody API
- 8011 = ObsidiaShell Graphiti V20 frozen readonly
- 7688 = Neo4j bolt live port available
- 7475 = Neo4j browser available
- 8001 = Decision Gateway, not Brody bus
- 3002 = optional / not required for current flow

## Decision

Phase 7C is accepted.

The UI layer is now connected to the validated Brody/Graphiti readonly path.