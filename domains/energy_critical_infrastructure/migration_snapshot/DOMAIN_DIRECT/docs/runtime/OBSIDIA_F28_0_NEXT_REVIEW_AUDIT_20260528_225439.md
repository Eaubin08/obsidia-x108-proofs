# OBSIDIA F28.0 — NEXT REVIEW AUDIT

Mode: NEXT_REVIEW_AUDIT_NO_PATCH
Commit: NO
Tag: NO
Freeze: NO

HEAD: `eaeacd8`

## Palier chain

- `BRODY_F23A4_0_REFLEX_DIAGNOSTIC_PACKET_AUDIT_20260528`
- `BRODY_F23A4_1_REFLEX_DIAGNOSTIC_PACKET_MINIMAL_20260528`
- `BRODY_F23A4_SIGMA_RUNTIME_BRIDGE_PALIER_20260528`
- `BRODY_F23A5_AGENT_GOVERNANCE_AUDIT_PALIER_20260528`
- `BRODY_F23A6_SIGMA_BRODY_ORCHESTRATION_PALIER_20260528`
- `BRODY_F27_TREE_SIGNAL_COGNITIVE_BRIDGE_PALIER_20260528`

## Working tree

- Modified tracked files: 0
- Untracked files: 20

## F27 runtime smoke

```text
route=/api/periphery/cognitive/tree-signal
version=TREE_SIGNAL_PACKET_V1
decision_authority=KX108_ONLY
emits_act=false
runtime_smoke=PASS
```

## Next candidates

### F28_GOVERNED_OPERATOR_RUNTIME — SELECTED
- Title: Brody Operator Runtime unified view
- Reason: Sigma envelope + TreeSignalPacket now exist; next useful layer is an operator-facing runtime packet that exposes both together.
- Risk: LOW_MEDIUM
- Patch scope: apps/obsidia_api/brody_operator_view_packet.py, apps/obsidia_api/brody_runtime_context_adapter.py, apps/obsidia_api/routes/periphery_ops.py

### F29_MEMORY_GRAPHITI_RECONCILIATION — DEFERRED
- Title: Graphiti / memory sidecar reconciliation
- Reason: There are still memory/audit leftovers and known Graphiti/Brody material gaps; useful but touches sidecar semantics.
- Risk: MEDIUM
- Patch scope: periphery/brody_memory_readonly, periphery/graphiti, apps/obsidia_api/routes/brody_monitoring.py

### F30_WORKFLOW_SOP_ENGINE — DEFERRED
- Title: Workflow/SOP pseudo-deterministic engine
- Reason: Connects to the enterprise workflows idea: work as SOP graph, but must stay under KX108 and no-ACT boundaries.
- Risk: MEDIUM
- Patch scope: periphery/workflows, apps/obsidia_api/routes/periphery_ops.py, tests/api

### F31_CLEAN_UNTRACKED_RUNTIME_DEBT — DEFERRED
- Title: Clean untracked F23 audit debris
- Reason: Repo working tree remains noisy with old untracked F23A4/F23 meta/night audit files.
- Risk: LOW
- Patch scope: docs/runtime, scripts, sigma/*.bak_*

## Selected next

```text
F28.1_GOVERNED_OPERATOR_RUNTIME_AUDIT
```

## Boundary

```text
DECISION_AUTHORITY=KX108_ONLY
readonly=true
emits_act=false
kernel_mutation=false
x108_mutation=false
```

## Status

F28_0_NEXT_REVIEW_AUDIT_DONE
