# OBSIDIA F19B — THERMO / COHERENCE / TIME UNIFIED PACKET

Date: 20260528_032132
CHECKPOINT: F19B_THERMO_COHERENCE_TIME_UNIFIED
MODE: PATCH
STATUS: PASS_LOCAL_AWAITING_COMMIT

## Root cause

F19A/F19A2 classified the runtime as:
EXISTING_ROUTES_AND_THERMO_PACKET_NEED_UNIFICATION.

Existing sources:
- Brody thermodynamics_packet
- periphery.energy_thermo.run_energy_thermo
- x108 replay coherence semantics
- temporal/time shadow context

## Patch

Created:
- apps/obsidia_api/brody_thermo_coherence_time_unified.py

Patched:
- apps/obsidia_api/routes/brody.py

Runtime now exposes:
- thermo_unified_packet

## Expected runtime fields

- version=THERMO_COHERENCE_TIME_UNIFIED_PACKET_V1
- status=THERMO_COHERENCE_TIME_UNIFIED_READONLY_PASS
- source=BRODY_F19B_UNIFIED_THERMO_COHERENCE_TIME
- scores.thermo_coherence_temperature
- scores.energy_efficiency
- scores.replay_coherence_score
- scores.time_pressure
- composite_temperature
- stability_state
- energy_thermo_packet
- coherence_shadow_packet
- time_shadow_packet

## Runtime payloads

- docs/runtime/F19B_8000_THERMO_COHERENCE_TIME_UNIFIED_PAYLOAD.json
- docs/runtime/F19B_8012_THERMO_COHERENCE_TIME_UNIFIED_PAYLOAD.json

## Terminal checks

- docs/runtime/F19B_TERMINAL_THERMO_UNIFIED_8000.txt
- docs/runtime/F19B_TERMINAL_THERMO_UNIFIED_8012.txt

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
