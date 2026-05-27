# BRODY_GRAPHITI_V20_PROXY_VALIDATION_REPORT

Status: PASS

## Scope

This phase reconnects Target /api/graphiti/* routes to the local ObsidiaShell Graphiti V20 frozen gateway on 127.0.0.1:8011.

The reconnect is readonly only.

## Changed files

- apps/obsidia_api/graphiti_v20_readonly_client.py
- apps/obsidia_api/routes/graphiti.py
- scripts/smoke_graphiti_v20_proxy.ps1
- tests/api/test_graphiti_v20_proxy_readonly.py

## Validation

Smoke command:

powershell -ExecutionPolicy Bypass -File .\scripts\smoke_graphiti_v20_proxy.ps1 -Base "http://127.0.0.1:8012"

Smoke result:

GRAPHITI_V20_PROXY_SMOKE_DONE

Pytest command:

python -m pytest tests/api/test_graphiti_v20_proxy_readonly.py tests/api/test_brody_routes_registered.py tests/api/test_brody_capabilities_preserved.py tests/api/test_brody_boundary_readonly.py -q

Pytest result:

9 passed in 3.57s

## Graphiti V20 proxy results

/api/graphiti/status now reports:

- source = GRAPHITI_V20_HTTP
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

Preserved:

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

## Important limitation

Query:

/api/graphiti/context?q=Brody&limit=5

returns:

- source = GRAPHITI_V20_HTTP
- count = 0
- warnings = NO_ENTITY_MATCH_IN_FROZEN_V20, NO_RELATION_MATCH_IN_FROZEN_V20

Interpretation:

The proxy works. The frozen V20 corpus does not currently contain Brody entity/relation material for this query.

Useful known Graphiti V20 coverage exists for:

- X-108
- CANON
- Kernel
- Proof
- Freeze

## Decision

This reconnect is accepted as readonly Graphiti V20 proxy.

It does not merge Graphiti into X108.

It does not bind Graphiti to the kernel.

It does not grant Graphiti decision authority.

## Next phase

PHASE 6 — commit only safe files.

Exclude:

- _BRODY_RECONNECT_WORK/
- backups
- raw smoke outputs
- audit CSVs
- node_modules
- .venv
- records
- secrets
