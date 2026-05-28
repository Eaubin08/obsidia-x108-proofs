from __future__ import annotations

from typing import Any, Dict

from ..agents.orchestrator_readonly import run_readonly_swarm
from ..constants import DECISION_AUTHORITY, READONLY_FLAGS
from ..primitives.workflow_replay_audit import build_workflow_replay_audit_from_result
from ..skills.skill_build_workbench_view import build_workbench_view_model
from ..skills.skill_generate_report_readonly import generate_workflow_governance_report

OPERATOR_SPEC = {
    "operator_id": "BRODY_WORKFLOW_OPERATOR_READONLY_V4",
    "role": "Cowork-style peripheral worker that prepares workflow governance material.",
    "can_decide": False,
    "can_execute": False,
    "can_call_x108_runtime": False,
    "can_mutate_kernel": False,
}


def build_brody_workflow_operator_packet_readonly(sop_text: str, title: str = "Untitled workflow") -> Dict[str, Any]:
    """Build Brody cowork-style operator packet.

    Brody may prepare context, report, replay audit and UI state. Brody cannot
    emit runtime authority or decide.
    """
    result = run_readonly_swarm(sop_text, title=title)
    replay = build_workflow_replay_audit_from_result(result)
    report_md = generate_workflow_governance_report(result)
    workbench_view = build_workbench_view_model(result)
    return {
        "operator_kind": "BRODY_WORKFLOW_OPERATOR_READONLY",
        "operator_spec": OPERATOR_SPEC,
        "decision_authority": DECISION_AUTHORITY,
        "swarm_result": result,
        "replay_audit_report": replay,
        "report_md": report_md,
        "workbench_view": workbench_view,
        "handoff_targets": ["ObsidiaShell workbench", "X108 readonly ingress candidate", "Claude Code terminal review"],
        "boundary": {"decision_authority": DECISION_AUTHORITY, **READONLY_FLAGS},
    }
