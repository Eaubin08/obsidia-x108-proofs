# OBSIDIA F13 — LIVE UI CHAT SMOKE FREEZE REPORT

Date: 20260527_233241

## STATUS

F13_LIVE_UI_CHAT_SMOKE_PASS

## SCOPE

F13A — Live UI chat smoke baseline  
F13B — Freeze commit

## BACKEND

Runtime: http://127.0.0.1:8000  
Route: /api/brody/chat  
Frontend: http://127.0.0.1:5173  

Engine env used:

- VITE_ENGINE_API_BASE=http://127.0.0.1:8000
- VITE_BRODY_API_URL=http://127.0.0.1:8000
- VITE_USE_MOCK_FALLBACK=false

## UI VISUAL EVIDENCE

Prompt tested:

write Graphiti memory + canon -> DOMAIN_RACCORD_WRITE_BOUNDARY

Observed in UI:

- BACKEND: LIVE
- voice_src:DOMAIN_RACCORD_WRITE_BOUNDARY
- graphiti:GRAPHITI_LIVE_BLOCKED
- neo4j:LIVE_READONLY
- BRODY TERMINAL — TRANSVERSE STACK
- decision_authority=KX108_ONLY
- readonly=true
- emits_act=false
- emits_verdict=false
- operator_can_write=false
- operator_can_decide=false
- voice_mode=DOMAIN_RACCORD_BOUNDARY
- domains=ARCHITECTURE_EXPLANATION, MEMORY_WRITE_CANON_FREEZE
- write_boundary_required=true
- MEMORY_WRITE_CANON_FREEZE visible in Domain Raccord panel
- Native Machination risk flags visible:
  - action_request
  - write_request
  - memory_write_request
  - graphiti_write_request
  - canon_promotion_request
- Boundary:
  - memory_write=false
  - graphiti_write=false
  - kernel_mutation=false
  - x108_mutation=false

## INTERPRETATION

The web UI consumes the live Brody backend payload.
The F12 Domain Raccord priority repair is visible in the UI.
The interface exposes readonly boundary, operator view, and command packet status without granting execution.

## BOUNDARY

UI_DECIDES=false
UI_EXECUTES=false
BRODY_EXECUTE_ALLOWED=false
READONLY=true
KX108_ONLY=true
EMITS_ACT=false
EMITS_VERDICT=false
MEMORY_WRITE=false
GRAPHITI_WRITE=false
KERNEL_MUTATION=false
X108_MUTATION=false

## TEST STATUS BEFORE F13

F12C terminal markers: PASS
F12C priority tests: 4/4 PASS
Targeted domain/voice: 60/60 PASS
Full F2A→F12C regression: 272/272 PASS
F13A source assert: expected PASS
Frontend HTTP probe: expected 200
Frontend build: expected PASS

## CURRENT STACK

F2A — Gencoin transverse interface
F2B — Sigma calibrated
F2C — Anti-Mismatch formal
F3 — Thermodynamics
F4 — Gencoin Shadow Value
F5 — 34 Trees formal signal
F6 — Memory Promotion Guard
F7 — Operator View Packet
F8 — RightPanel Transverse Stack UI
F9 — Brody Terminal Chat View
F10 — Existing Command Packet Reconnect
F11 — Live Runtime Chat Smoke + Tree Signal Order Fix
F12 — Domain Raccord Priority + Terminal Visibility
F13 — Live UI Chat Smoke

## NEXT CANDIDATES

F14_COMMAND_COPY_BUTTON_UI
F14_RIGHTPANEL_REAL_PAYLOAD_ALIGNMENT
F14_GRAPHITI_8012_TO_8000_PARITY_DECISION
F14_RUNTIME_FREEZE_DASHBOARD
