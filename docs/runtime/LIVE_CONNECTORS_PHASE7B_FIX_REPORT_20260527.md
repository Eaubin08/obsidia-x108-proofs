# LIVE_CONNECTORS_PHASE7B_FIX_REPORT_20260527

Status: PASS_READY_FOR_COMMIT

## Scope

Patch live connector drift after Brody/Graphiti readonly freeze.

## Fixed

- Workbench Vite proxy now targets Brody API 8012 instead of obsolete 8000.
- Workbench client ENGINE_BASE now defaults to 8012 instead of obsolete 8000.
- tools/brody_chat.py now targets Brody API 8012 instead of obsolete 8001/bus/health.
- Stale text references to 8000/8001/bus/health removed from patched files.
- Python global declaration in tools/brody_chat.py fixed.
- Patch reapplied byte-safe to avoid BOM/mojibake corruption.

## Validation

- STATIC_PORT_CHECK_OK
- No BOM on patched files
- 8012 /openapi.json = HTTP 200
- 8012 /api/graphiti/status = GRAPHITI_V20_HTTP
- pytest core = 9 passed
- python -m py_compile tools/brody_chat.py = PASS

## Current architecture

- 8012 = Brody API
- 8011 = ObsidiaShell Graphiti V20 frozen readonly
- 7688 = Neo4j bolt, live port available
- 7475 = Neo4j browser
- 5173 = Workbench target port, launch pending
- 8001 = Decision Gateway, not Brody bus
- 3002 = Danswer optional/obsolete for current flow

## Not changed

- No kernel mutation.
- No X108 mutation.
- No Graphiti write.
- No Neo4j write.
- No Decision Gateway integration.
- No Danswer integration.
- No secrets or real .env files.

## Boundary

KX108_ONLY remains sole decision authority.

Every connector remains readonly/advisory unless explicitly validated.
