# BRODY_PHASE11E_RIGHTPANEL_NATIVE_DISPLAY_20260527

Status: PASS_READY_FOR_REVIEW

## Scope

Expose native Brody machination in the Workbench RightPanel.

## Patched

- apps/obsidia-workbench/src/components/RightPanel.tsx

## Added RightPanel sections

- Native Machination
- Contracts / Permission Matrix
- Native Boundary

## Displayed native fields

- support_summary
- contracts
- permission_matrix
- machination_packet
- boundary_contract
- kernel_contract
- signal_contract
- forbidden_output_contract

## Validated

- BOM=false
- npm run build passed
- static check found native UI sections

## Boundary

The UI only displays the /api/brody/chat native payload.

It does not decide, act, write memory, write Graphiti, mutate kernel, or mutate X108.
