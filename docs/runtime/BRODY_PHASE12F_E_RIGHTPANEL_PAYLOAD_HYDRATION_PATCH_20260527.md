# BRODY_PHASE12F_E_RIGHTPANEL_PAYLOAD_HYDRATION_PATCH_20260527

Status: PASS_READY_FOR_REVIEW

## Scope

Fix RightPanel live payload hydration after Phase 12F-C/D.

## Problem

12F-B patched RightPanel correctly.
12F-C API payload parity passed.
12F-D showed API sends true_voice_snapshot/domain_raccord data.

But manual UI still showed old/static Context Packet because RightPanel depends on lastBackendPayload, and App.tsx only populated lastBackendPayload after a live send in the current runtime.

When reloading or selecting a stored session, messages were restored but lastBackendPayload was not restored.

## Patched

- apps/obsidia-workbench/src/App.tsx

## Added

- getLastStoredBackendPayload(messages)
- initial lastBackendPayload hydration from initMsgs
- session selection restores last stored Brody backendPayload
- new session clears lastBackendPayload

## Preserved

- No backend change.
- No X108 change.
- No memory write.
- No Graphiti write.
- No kernel mutation.
- UI hydration only.
