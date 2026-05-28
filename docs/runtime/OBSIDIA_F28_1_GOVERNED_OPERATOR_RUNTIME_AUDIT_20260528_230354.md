# OBSIDIA F28.1 — GOVERNED OPERATOR RUNTIME AUDIT

Mode: AUDIT_ONLY_NO_PATCH
Commit: NO
Tag: NO
Freeze: NO

HEAD: `eaeacd8`
Tags on HEAD: `BRODY_F27_TREE_SIGNAL_COGNITIVE_BRIDGE_PALIER_20260528`

## Summary

- Existing target files: 6
- Missing target files: 0
- Danger records: 0
- Gaps: 1

## Gaps

- `F28_G07` — Runtime context does not visibly carry tree_signal_packet snapshot.
  - target_phase: F28.2
  - target_file: `apps/obsidia_api/brody_runtime_context_adapter.py`
  - patch_now: False

## Boundary

```text
DECISION_AUTHORITY=KX108_ONLY
readonly=true
advisory_only=true
context_signal_only=true
emits_act=false
emits_verdict=false
kernel_mutation=false
x108_mutation=false
```

## Next

F28.2_GOVERNED_OPERATOR_RUNTIME_ROUTE

## Status

F28_1_GOVERNED_OPERATOR_RUNTIME_AUDIT_DONE
