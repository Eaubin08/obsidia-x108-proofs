# BRODY_PHASE12F_B_RIGHTPANEL_PARITY_PATCH_20260527

Status: PASS_READY_FOR_REVIEW

## Scope

Patch Obsidia Workbench RightPanel so UI exposes the frozen Brody 12E6 surface.

## 12F-A finding

- API exposes full 12E6 payload.
- UI calls /api/brody/chat.
- RightPanel already exposes machination/contracts/boundary.
- UI did not expose true_voice_snapshot/domain_raccord_snapshot.
- ui_files_with_full_brody_surface=0.

## Patched

- apps/obsidia-workbench/src/components/RightPanel.tsx

## Added UI sections

- True Voice / LLM Obsidien
- Domain Raccord / Structure-First
- 12E6 Boundary Envelope

## Preserved

- UI only.
- No backend change.
- No X108 change.
- No memory write.
- No Graphiti write.
- No kernel mutation.
