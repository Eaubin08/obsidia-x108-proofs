# BRODY_PHASE8C_CAPABILITY_ORIGIN_CONCLUSION_20260527

Status: PASS_CAPABILITY_ORIGIN_MAPPED

## Scope

Conclude Phase 8 after old-patch archaeology and live smoke testing.

Goal:

- verify the newly reconnected Brody live path
- identify which older layers likely explain Brody's already-good French, English, code/debug, and boundary behavior
- avoid patching before separating live backend behavior from frontend fallback/composer behavior

## Phase 8A result

Old patch and capability archaeology found that Brody capability is not explained by Danswer/Onyx/3002.

The relevant machinery is:

- /api/brody/chat
- periphery/brody
- periphery/bdf
- periphery/reverse_os
- tools/brody_chat.py
- scripts/smoke_brody_capabilities.ps1
- scripts/smoke_brody_routes.ps1
- tests/api/test_brody_capabilities_preserved.py
- tests/api/test_brody_routes_registered.py
- apps/obsidia-workbench/src/lib/brodyResponseComposer.ts
- apps/obsidia-workbench/src/lib/osTradPipeline.ts
- apps/obsidia-workbench/src/lib/osReverseProjection.ts
- apps/obsidia-workbench/OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md
- apps/obsidia-workbench/OS_TRAD_REVERSE_IR_BACKEND_BINDING_PLAN.md
- docs/freeze/V5B_PLUS_BRODY_RESPONSE_MODULE_AUDIT.md
- docs/freeze/BRODY_REAL_MODULE_DISCOVERY_FOR_API.md
- docs/freeze/BRODY_REAL_BACKEND_AUDIT_REPORT.md

## Important architecture finding

modules/os_trad is absent in the current repo.

OS Trad / Reverse behavior currently exists mostly through Workbench/frontend libraries and binding plans:

- osTradPipeline.ts
- osReverseProjection.ts
- brodyResponseComposer.ts
- OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md
- OS_TRAD_REVERSE_IR_BACKEND_BINDING_PLAN.md

Therefore, the old "good Brody speaking" behavior likely came from a hybrid layer:

- live /api/brody/chat backend when available
- frontend Brody response composer fallback
- OS Trad / Reverse OS trace layer
- readonly memory / Graphiti context
- periphery/brody language and context routing
- BDF double-brain / diffusion mix routing

## Phase 8B live smoke result

Live smoke pack passed.

Validated:

- Brody openapi = OK
- Brody Graphiti status = OK
- Brody memory status = OK
- Workbench = OK
- Workbench engine openapi = OK
- Workbench Graphiti proxy = OK
- BRODY_ROUTES_SMOKE_OK
- BRODY_CAPABILITY_SMOKE_OK
- francais_utf8 = OK
- english_understanding = OK
- code_debug = OK
- boundary = OK
- Graphiti V20 proxy smoke = OK
- pytest core = 9 passed

## Boundary readback

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

## Current canonical live path

Workbench 5173 -> Brody API 8012 -> Graphiti V20 readonly proxy -> ObsidiaShell 8011.

## Interpretation

The current live path is valid.

The old high-quality Brody response behavior should not be attributed to Danswer/Onyx/3002.

It should be attributed to the Brody + Workbench + OS Trad / Reverse OS / composer + readonly memory/context machinery.

## Watch items

Some stale references remain in frontend diagnostics/fallback comments, especially older port 8000 mentions in non-critical files.

These do not currently break the active live path because the active Workbench client now points to 8012.

They should be cleaned later in a targeted hygiene phase, not during this capability freeze.

## Decision

Phase 8 confirms:

- live Brody path works
- preserved capability tests pass
- French UTF-8 works
- English understanding works
- code/debug works
- boundary behavior works
- KX108_ONLY remains sole decision authority

No patch is required before freezing Phase 8.

## Next

Phase 8D should be a targeted stale-reference cleanup and deeper comparison:

- inspect e9e43e4 Brody real project memory commit
- inspect brodyResponseComposer.ts / osTradPipeline.ts / osReverseProjection.ts
- clean obsolete 8000 comments only if safe
- add explicit smoke proving Workbench fallback source vs real backend source