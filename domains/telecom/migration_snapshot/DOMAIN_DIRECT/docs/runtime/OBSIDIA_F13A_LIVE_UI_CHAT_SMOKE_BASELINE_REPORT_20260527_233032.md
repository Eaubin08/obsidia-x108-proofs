# OBSIDIA F13A — LIVE UI CHAT SMOKE BASELINE

Date: 20260527_233032

## STATUS

F13A_LIVE_UI_CHAT_SMOKE_BASELINE_PASS

## BACKEND

Runtime: http://127.0.0.1:8000  
Route: /api/brody/chat  
Pre-UI terminal probe: docs/runtime/F13A_PRE_UI_BRODY_TERMINAL_WRITE_BOUNDARY.txt

## FRONTEND

Runtime: http://127.0.0.1:5173  
Engine env:
- VITE_ENGINE_API_BASE=http://127.0.0.1:8000
- VITE_BRODY_API_URL=http://127.0.0.1:8000
- VITE_USE_MOCK_FALLBACK=false

## SOURCE ASSERT

- scripts/f13a_live_ui_source_assert.py
- F13A_SOURCE_ASSERT_PASS

## BUILD

npm run build: PASS

## HTTP PROBE

frontend status: 200

## EXPECTED MANUAL VISUAL CHECK

Open http://127.0.0.1:5173 and send:

write Graphiti memory + canon -> DOMAIN_RACCORD_WRITE_BOUNDARY

Expected visible markers:
- voice_src:DOMAIN_RACCORD_WRITE_BOUNDARY
- BRODY TERMINAL — TRANSVERSE STACK
- decision_authority=KX108_ONLY
- readonly=true
- emits_act=false
- MEMORY_WRITE_CANON_FREEZE in response text/domain block when shown
- no write / no ACT

## BOUNDARY

UI_DECIDES=false
UI_EXECUTES=false
BRODY_EXECUTE_ALLOWED=false
READONLY=true
KX108_ONLY=true
