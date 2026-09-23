# BRODY_PHASE9B4_UI_TERMINAL_RECONNECT_REPORT_20260527

Status: PASS_READY_FOR_COMMIT

## Scope

Reconnect UI and terminal support surfaces to Phase 9B2 OS Trad / IR / OS Reverse backend routes.

## Added

- scripts/smoke_os_trad_ir_reverse_support.ps1
- UI support helpers in apps/obsidia-workbench/src/api/obsidiaClient.ts:
  - callOSTradTranslateSupport
  - callIRCandidateSupport
  - callOSReverseProjectSupport
- CognitiveTree / getCognitiveTrees exports restored for TreeExplorer build compatibility.
- CognitiveTree now guarantees id, name, and domain for TypeScript safety.
- App.tsx now consumes support helpers after /api/brody/chat succeeds.
- Support language maps mixed -> auto for route compatibility.

## Fixed

- Active 8000 references removed from UI/scripts.
- Workbench default engine references aligned to 8012.
- Brody fallback comment aligned to port 8012.
- SettingsView displayed engine base aligned to 8012.
- Support routes enrich backend payload via support_routes / backend_support.

## Preserved

- /api/brody/chat remains primary spoken Brody interface.
- tools/brody_chat.py remains unchanged.
- sendBrodyMessage remains primary UI chat call.
- Workbench fallback remains intact.
- OS Trad / IR / Reverse routes are support surfaces only.
- Historical docs were not rewritten.
- No memory write.
- No Graphiti write.
- No kernel mutation.
- No X108 mutation.

## Validation

- Terminal OS Trad / IR / Reverse support smoke passed.
- Workbench build passed.
- Pytest core passed: 13 passed.
- Active 8000 recheck passed.
- BOM checks passed.
- KX108_ONLY boundary preserved.

## Non-blocking warnings

- Existing duplicate OpenAPI operation ID warning for x108_status.
- Existing duplicate OpenAPI operation ID warning for brody_cli_registry.
- These warnings do not block Phase 9B4.

## Decision

Phase 9B4 reconnects terminal and UI clients to OS Trad / IR / Reverse support routes without replacing Brody chat.
