from __future__ import annotations

from typing import Any, Dict

from ..constants import DECISION_AUTHORITY, READONLY_FLAGS
from ..operators.brody_workflow_operator_readonly import build_brody_workflow_operator_packet_readonly
from ..operators.obsidiashell_workbench_adapter import build_obsidiashell_workbench_state_readonly

ROUTINE_SPEC = {
    "routine_id": "ROUTINE_BUILD_WORKFLOW_PACKET_READONLY_V4",
    "flow": "SOP → swarm → graph → IR → packet → envelope → replay/report/workbench",
    "runtime_binding": False,
    "kernel_binding": False,
}


def routine_build_workflow_packet_readonly(sop_text: str, title: str = "Untitled workflow") -> Dict[str, Any]:
    """One-shot readonly workflow packet build."""
    operator_packet = build_brody_workflow_operator_packet_readonly(sop_text, title=title)
    workbench_state = build_obsidiashell_workbench_state_readonly(operator_packet["swarm_result"])
    envelope = operator_packet["swarm_result"]["x108_readonly_ingress_envelope"]
    return {
        "routine_kind": "ROUTINE_BUILD_WORKFLOW_PACKET_READONLY",
        "routine_spec": ROUTINE_SPEC,
        "operator_packet": operator_packet,
        "obsidiashell_workbench_state": workbench_state,
        "x108_readonly_ingress_envelope": envelope,
        "decision_authority": DECISION_AUTHORITY,
        "boundary": {"decision_authority": DECISION_AUTHORITY, **READONLY_FLAGS},
    }
