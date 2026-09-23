# LIVE_CONNECTORS_FINAL_FREEZE_20260527

Status: FINAL_FREEZE_PASS

## Scope

Final freeze for Brody live connector restoration and validation.

## Canonical live flow

Workbench 5173 -> Brody API 8012 -> Graphiti V20 readonly proxy -> ObsidiaShell 8011.

## Frozen phases

### Phase 7A — live connectors precheck

Status: PASS.

Validated initial service map and confirmed the live connector perimeter.

### Phase 7B — Workbench/Brody port alignment

Status: PASS.

- Workbench Vite proxy aligned to Brody API 8012.
- Workbench client ENGINE_BASE aligned to 8012.
- tools/brody_chat.py aligned to Brody API 8012.
- Obsolete 8000/8001/bus health references removed from active live path.
- Patch reapplied byte-safe to avoid BOM/mojibake.

### Phase 7C — Workbench live validation

Status: PASS.

Validated:

- 5173 Workbench HTTP 200
- 5173 /api/engine/openapi.json HTTP 200
- /api/brody/chat visible through Workbench proxy
- 5173 -> 8012 -> 8011 Graphiti status = GRAPHITI_V20_HTTP

### Phase 7D — flow/auth/metrics

Status: PASS_WITH_OPTIONAL_CONNECTORS_PENDING.

Validated critical flow:

- Workbench UI
- Brody API openapi
- Brody Graphiti status/readiness/metrics
- Memory status/sources
- Shell Graphiti status/readiness

### Phase 7E — Decision Gateway 8001

Status: CLOSED_DIAGNOSTIC.

Decision:

- 8001 is Decision Gateway Docker, not Brody.
- 8001 is alive and protected by auth/HMAC.
- /v1/audit/chain is real but protected/fails without valid auth/HMAC.
- Current Brody live path does not depend on /v1/audit/chain.
- Decision Gateway remains outside Brody/Graphiti runtime flow.

### Phase 7F — Danswer/Onyx/3002

Status: OUT_OF_SCOPE_FOR_CURRENT_BRODY_FLOW.

Decision:

- 3002 is down.
- No active Docker service exposes 3002.
- Danswer/Onyx is not required for the current Brody live path.
- Danswer/Onyx receives no decision authority.

## Preserved Brody capabilities

The current live stack preserves:

- Brody French UTF-8 responses
- English understanding
- code/debug path
- terminal path
- Workbench UI path
- Graphiti V20 readonly context
- Memory status/sources
- KX108_ONLY boundary

## Boundary invariants

- decision_authority = KX108_ONLY
- readonly = true
- advisory_only = true
- emits_act = false
- emits_verdict = false
- memory_write = false
- graphiti_write = false
- neo4j_write = false
- kernel_mutation = false
- x108_mutation = false
- real_action = false

## Out of current critical flow

- Decision Gateway 8001 audit chain
- Danswer/Onyx 3002
- Graphiti write
- Neo4j write
- X108 mutation
- kernel mutation

## Final decision

The Brody live connector sequence is frozen.

The canonical active path is:

Workbench 5173 -> Brody API 8012 -> Graphiti V20 readonly proxy -> ObsidiaShell 8011.

Everything outside this path is documented as protected, optional, or out-of-scope for the current freeze.