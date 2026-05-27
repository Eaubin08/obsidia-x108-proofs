# LIVE_CONNECTORS_PHASE7D_FLOW_AUTH_METRICS_20260527

Status: PASS_WITH_OPTIONAL_CONNECTORS_PENDING

## Scope

Read-only diagnostic of live flow, authorization boundaries, and metrics after Phase 7C Workbench validation.

## Critical flow checks

- Workbench UI 5173 = OK HTTP 200
- Workbench -> Brody openapi = OK HTTP 200
- Brody API openapi 8012 = OK HTTP 200
- Brody Graphiti status = OK HTTP 200
- Brody Graphiti readiness = OK HTTP 200
- Brody Graphiti metrics = OK HTTP 200
- Memory status = OK HTTP 200
- Memory sources = OK HTTP 200
- Shell Graphiti status 8011 = OK HTTP 200
- Shell Graphiti readiness 8011 = OK HTTP 200

## Optional / non-critical checks

- Decision Gateway health 8001 = OK HTTP 200
- Decision Gateway audit chain /v1/audit/chain = FAIL
- Danswer optional 3002 /health = FAIL

## Boundary sample

- graphiti_source = GRAPHITI_V20_HTTP
- graphiti_proxy_source = GRAPHITI_V20_HTTP
- graphiti_decision_authority = KX108_ONLY
- graphiti_write = false
- neo4j_write = false
- emits_act = false
- emits_verdict = false
- memory_source = REAL_BACKEND
- memory_decision_authority = KX108_ONLY
- memory_write = false
- memory_readonly = true

## Decision

The critical live path is valid:

Workbench 5173 -> Brody API 8012 -> Graphiti V20 readonly proxy -> ObsidiaShell 8011.

No connector is granted decision authority.

KX108_ONLY remains sole decision authority.

## Pending

Decision Gateway audit chain requires a dedicated Phase 7E check.

Danswer 3002 is optional and not required for the current Brody/Graphiti/Workbench flow.

## Not changed

- No runtime patch.
- No kernel mutation.
- No X108 mutation.
- No Graphiti write.
- No Neo4j write.
- No secrets.
- No real .env file.