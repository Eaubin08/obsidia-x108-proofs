from __future__ import annotations

from typing import Any

from ..constants import DECISION_AUTHORITY, READONLY_FLAGS
from ..repo_aware.obsidia_x108_repo_map import REAL_REPO_PATHS, PROPOSED_INSTALL_PATHS, REPO_BASELINE
from ..routines.routine_build_workflow_packet import routine_build_workflow_packet_readonly

BRODY_AUTOMATION_COMPATIBILITY = {
    "target_file": "apps/obsidia_api/brody_automation_orchestrator.py",
    "target_function": "run_brody_automation_layer",
    "compatible_request_type": "STRUCTURAL_PREPARATION",
    "snapshot_key": "workflow_governance_snapshot",
    "patch_mode": "DEFERRED_PATCH_PLAN_ONLY",
    "brody_execute_allowed": False,
    "human_operator_required": True,
}


def build_brody_workflow_governance_snapshot(
    sop_text: str,
    title: str = "workflow governance candidate",
    session_id: str = "manual-session",
    request_type: str = "STRUCTURAL_PREPARATION",
) -> dict[str, Any]:
    """Build the packet shape that can be inserted later into Brody automation_snapshot.

    This does not import the repo Brody runtime, does not call operators, does not write
    memory, and does not bind X108. It only produces a compatible readonly snapshot.
    """
    routine = routine_build_workflow_packet_readonly(sop_text, title=title)
    envelope = routine["x108_readonly_ingress_envelope"]
    return {
        "snapshot_kind": "BRODY_WORKFLOW_GOVERNANCE_SNAPSHOT_READONLY_V5",
        "session_id": session_id,
        "request_type": request_type,
        "target_integration": BRODY_AUTOMATION_COMPATIBILITY,
        "repo_baseline": REPO_BASELINE,
        "real_paths_used": {
            "brody_automation_orchestrator": REAL_REPO_PATHS["brody_automation_orchestrator"],
            "brody_operator_view_packet": REAL_REPO_PATHS["brody_operator_view_packet"],
            "right_panel_component": REAL_REPO_PATHS["right_panel_component"],
            "install_root": PROPOSED_INSTALL_PATHS["module_root"],
        },
        "workflow_governance_packet": routine,
        "x108_readonly_ingress_envelope": envelope,
        "next_allowed_steps": [
            "copy_module_to_periphery_workflow_governance_readonly",
            "run_v5_audit_and_smoke",
            "create_patch_plan_for_brody_automation_snapshot",
            "create_patch_plan_for_rightpanel_visibility",
            "human_review_before_any_merge",
        ],
        "blocked_steps": [
            "direct_main_patch",
            "x108_runtime_binding",
            "kernel_mutation",
            "graphiti_write",
            "neo4j_write",
            "brody_execute_command",
            "auto_merge",
        ],
        "decision_authority": DECISION_AUTHORITY,
        "boundary": {"decision_authority": DECISION_AUTHORITY, **READONLY_FLAGS},
    }
