# BRODY_PHASE8F_ADAPTATION_POSITION_FREEZE_20260527

Status: PASS_POSITION_CORRECTED

## Scope

Freeze the corrected interpretation of Brody adaptation after Phase 8D/8E audits.

## Corrected position

Brody adaptation is not only UI.

It exists across three layers:

1. Terminal layer
2. Live API layer
3. Workbench/UI layer

## Terminal layer

Confirmed files:

- tools/brody_chat.py
- scripts/run_brody_terminal.ps1
- scripts/smoke_brody_capabilities.ps1
- scripts/smoke_brody_routes.ps1
- tests/api/test_brody_capabilities_preserved.py
- tests/api/test_brody_routes_registered.py
- tests/api/test_brody_boundary_readonly.py

Confirmed behavior:

- Terminal Brody targets http://127.0.0.1:8012/api/brody/chat
- Terminal mode is readonly
- Boundary command exposes decision_authority=KX108_ONLY
- Smoke cases cover francais_utf8, english_understanding, code_debug, boundary
- Boundary tests preserve emits_act=false and memory_write=false

## Live API layer

Confirmed live routes:

- /api/brody/chat
- /api/graphiti/status
- /api/memory/status

Confirmed missing dedicated backend routes:

- /api/os-trad/translate
- /api/ir/candidate
- /api/os-reverse/project

## Workbench/UI layer

Confirmed files:

- apps/obsidia-workbench/src/lib/language.ts
- apps/obsidia-workbench/src/lib/symbolicAlphabet.ts
- apps/obsidia-workbench/src/lib/irCandidateBuilder.ts
- apps/obsidia-workbench/src/lib/osTradPipeline.ts
- apps/obsidia-workbench/src/lib/osReverseProjection.ts
- apps/obsidia-workbench/src/lib/brodyResponseComposer.ts
- apps/obsidia-workbench/src/api/obsidiaClient.ts
- apps/obsidia-workbench/src/App.tsx

Confirmed behavior:

- App.tsx imports and uses sendBrodyMessage
- App.tsx imports and uses runOSTradPipeline
- App.tsx imports and uses composeBrodyResponse
- Workbench is backend-first
- Frontend mock/composer only applies when source is FRONTEND_MOCK
- UI layer preserves readonly, emits_act=false, memory_write=false, decision_authority=KX108_ONLY

## Final interpretation

The missing piece is not adaptation itself.

The missing piece is backend route decomposition for OS Trad / IR / OS Reverse.

Current state:

- Minimal Brody adaptation = present
- Terminal adaptation = present
- Live /api/brody/chat adaptation = present
- Workbench/UI OS Trad / IR / Reverse adaptation = present
- Dedicated backend OS Trad / IR / Reverse routes = absent

## Boundary

- No patch in this phase.
- No runtime mutation.
- No kernel mutation.
- No X108 mutation.
- KX108_ONLY remains sole decision authority.

## Next

Phase 9 should port the existing minimal Workbench/UI OS Trad / IR / Reverse behavior into backend routes, without deleting the fallback.

Target routes:

- POST /api/os-trad/translate
- GET or POST /api/ir/candidate
- POST /api/os-reverse/project

The goal is backend decomposition, not reinvention.