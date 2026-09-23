# OBSIDIA F18B — EXISTING REVERSE OS / IR READONLY WIRING

Date: 20260528_030305
CHECKPOINT: F18B_EXISTING_REVERSE_OS_IR_READONLY_WIRING
MODE: PATCH
STATUS: PASS_LOCAL_AWAITING_COMMIT

## Root cause

F18A classified OS Trad / IR / Reverse OS as PARTIAL_RUNTIME_ENVELOPE_NEEDS_WIRING.

F18A3/F18A4 confirmed existing reusable sources:
- periphery/reverse_os.py
- periphery/test_reverse_os_non_decision.py
- obsidia-engine-candidate/bridge/zip2_reverse_os_real_adapter.py
- MMONDE Reverse OS / common_types / obsidia_ir candidates

## Patch

Created:
- apps/obsidia_api/brody_existing_reverse_os_bridge.py

Patched:
- apps/obsidia_api/routes/brody.py

Runtime now uses existing Reverse OS bridge instead of static empty envelope.

## Expected runtime result

- translation_trace.source=BRODY_EXISTING_REVERSE_OS_BRIDGE_V1
- alphabet_units_count > 0
- os_reverse_projection.non_decision=true
- ir_candidate.source=BRODY_EXISTING_REVERSE_OS_IR_BRIDGE_V1
- ir_candidate.entities > 0
- ir_candidate.constraints > 0

## Runtime payloads

- docs/runtime/F18B_8000_EXISTING_REVERSE_OS_RUNTIME_PAYLOAD.json
- docs/runtime/F18B_8012_EXISTING_REVERSE_OS_RUNTIME_PAYLOAD.json

## Terminal checks

- docs/runtime/F18B_TERMINAL_EXISTING_REVERSE_OS_8000.txt
- docs/runtime/F18B_TERMINAL_EXISTING_REVERSE_OS_8012.txt

## Boundary

KX108_ONLY=true
readonly=true
emits_act=false
emits_verdict=false
memory_write=false
graphiti_write=false
kernel_mutation=false
x108_mutation=false

## Next

Commit/tag/push after validation.
