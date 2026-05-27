# BRODY_PHASE11D_TERMINAL_NATIVE_DISPLAY_20260527

Status: PASS_READY_FOR_REVIEW

## Scope

Expose the native Brody machination payload in the classic terminal client.

## Patched

- tools/brody_chat.py

## Added terminal display sections

- MACHINATION NATIVE
- CONTRATS / PERMISSIONS
- BOUNDARY

## Added CLI mode

- --once

## Validated

- py_compile passed
- terminal once smoke passed for action boundary input
- terminal once smoke passed for code debug input

## Expected terminal payload

The terminal now reads /api/brody/chat and displays:

- support_summary
- contracts
- permission_matrix
- machination_packet
- boundary_contract
- kernel_contract
- signal_contract

## Boundary

Preserved:

- /api/brody/chat remains primary
- readonly=true
- emits_act=false
- memory_write=false
- graphiti_write=false
- kernel_mutation=false
- x108_mutation=false
- decision_authority=KX108_ONLY
