# OBSIDIA F30.0 — WORKFLOW / SOP ENGINE AUDIT

Mode: AUDIT_ONLY_NO_PATCH
Commit: NO
Tag: NO
Freeze: NO

HEAD: `79f329c`
Tags on HEAD: `BRODY_F26_MONITOR_GOVERNED_RUNTIME_PALIER_20260528`

## Summary

- Existing target files: 6
- Missing target files: 0
- Active workflow records: 6
- Danger records: 0
- Gaps: 3

## Active workflow/SOP related files

- `apps/obsidia_api/brody_runtime_context_adapter.py`
  - L4 `runtime_context` — Assembles runtime_context top-level snapshot from all peripheral snapshots.
  - L6 `runtime_context` — runtime_context is the single top-level envelope that the true_voice adapter
  - L10 `KX108_ONLY` — Boundary: readonly, KX108_ONLY.
  - L10 `readonly` — Boundary: readonly, KX108_ONLY.
  - L23 `readonly` — "readonly": True,
  - L27 `emits_act` — "emits_act": False,
  - L29 `kernel_mutation` — "kernel_mutation": False,
  - L30 `x108_mutation` — "x108_mutation": False,
- `apps/obsidia_api/routes/brody_monitoring.py`
  - L2 `readonly` — Brody CLI Registry — monitoring endpoint for brody_memory_readonly scripts.
  - L6 `readonly` — - Monitoring adapters expose Sigma readonly envelope.
  - L21 `operator_view_packet` — from apps.obsidia_api.brody_operator_view_packet import build_operator_view_packet
  - L22 `runtime_context` — from apps.obsidia_api.brody_runtime_context_adapter import build_runtime_context
  - L32 `readonly` — from periphery.brody_memory_readonly.session_memory_ledger_readonly.brody_session_memory_ledger_readonly_v2 import (
  - L39 `readonly` — from periphery.brody_memory_readonly.session_trace_ledger.brody_session_trace_ledger_readonly_v1_6_3 import (
  - L45 `tree_signal_packet` — from periphery.cognitive_trees.tree_signal_packet import build_tree_signal_packet
  - L51 `readonly` — "readonly": True,
- `apps/obsidia_api/routes/periphery_ops.py`
  - L12 `operator_view_packet` — from apps.obsidia_api.brody_operator_view_packet import build_operator_view_packet
  - L13 `runtime_context` — from apps.obsidia_api.brody_runtime_context_adapter import build_runtime_context
  - L37 `ActionSequence` — from periphery.action_sequence_governor import govern_action_sequence, ActionSequence, ActionStep
  - L37 `ActionStep` — from periphery.action_sequence_governor import govern_action_sequence, ActionSequence, ActionStep
  - L37 `govern_action_sequence` — from periphery.action_sequence_governor import govern_action_sequence, ActionSequence, ActionStep
  - L38 `workflow` — from periphery.github.github_workflow_guard import guard_workflow_action
  - L38 `guard_workflow_action` — from periphery.github.github_workflow_guard import guard_workflow_action
  - L48 `tree_signal_packet` — from periphery.cognitive_trees.tree_signal_packet import build_tree_signal_packet
- `periphery/action_sequence_governor.py`
  - L10 `ActionStep` — class ActionStep:
  - L20 `ActionSequence` — class ActionSequence:
  - L22 `ActionStep` — steps: list[ActionStep]
  - L24 `ActionSequence` — def govern_action_sequence(action: ActionCandidate, sequence: ActionSequence) -> PeripheralSignalPacket:
  - L24 `govern_action_sequence` — def govern_action_sequence(action: ActionCandidate, sequence: ActionSequence) -> PeripheralSignalPacket:
- `periphery/agents/action_sequence_agent.py`
  - L5 `ActionSequence` — from ..action_sequence_governor import ActionSequence, ActionStep, govern_action_sequence
  - L5 `ActionStep` — from ..action_sequence_governor import ActionSequence, ActionStep, govern_action_sequence
  - L5 `govern_action_sequence` — from ..action_sequence_governor import ActionSequence, ActionStep, govern_action_sequence
  - L26 `ActionStep` — ActionStep(
  - L37 `ActionSequence` — seq = ActionSequence(action_id=action.action_id, steps=steps)
  - L38 `govern_action_sequence` — return govern_action_sequence(action, seq)
- `periphery/github/github_workflow_guard.py`
  - L2 `Workflow` — GitHub Workflow Guard: issue -> plan -> branch -> patch -> tests -> PR -> audit -> human review.
  - L16 `Workflow` — class WorkflowGuardDecision:
  - L31 `workflow` — def guard_workflow_action(action: str) -> WorkflowGuardDecision:
  - L31 `Workflow` — def guard_workflow_action(action: str) -> WorkflowGuardDecision:
  - L31 `guard_workflow_action` — def guard_workflow_action(action: str) -> WorkflowGuardDecision:
  - L35 `Workflow` — return WorkflowGuardDecision(
  - L43 `Workflow` — return WorkflowGuardDecision(
  - L51 `Workflow` — return WorkflowGuardDecision(

## Gaps

- `F30_G01` — No dedicated periphery/workflows package detected.
  - target_phase: F30.1
  - target_file: `periphery/workflows`
  - patch_now: False
- `F30_G02` — No explicit SOP model detected.
  - target_phase: F30.1
  - target_file: `periphery/workflows/sop_contracts.py`
  - patch_now: False
- `F30_G04` — No explicit typed workflow/SOP step contract detected.
  - target_phase: F30.1
  - target_file: `periphery/workflows/sop_contracts.py`
  - patch_now: False

## Interpretation

```text
Company work = SOP graph
SOP graph = pseudo-deterministic workflow
Workflow evaluation = readonly context signal
Execution authority = KX108_ONLY
ACT emission = forbidden
```

## Boundary

```text
DECISION_AUTHORITY=KX108_ONLY
readonly=true
advisory_only=true
context_signal_only=true
emits_act=false
emits_verdict=false
runtime_execute=false
kernel_mutation=false
x108_mutation=false
```

## Next

F30.1_WORKFLOW_SOP_CONTRACTS_PATCH

## Status

F30_0_WORKFLOW_SOP_ENGINE_AUDIT_DONE
