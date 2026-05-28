from __future__ import annotations

from typing import Any

from ..constants import DECISION_AUTHORITY, READONLY_FLAGS
from ..repo_aware.obsidia_x108_repo_map import REAL_REPO_PATHS


def build_rightpanel_workbench_contract() -> dict[str, Any]:
    """Readonly UI contract for apps/obsidia-workbench/src/components/RightPanel.tsx."""
    return {
        "contract_id": "WORKFLOW_GOVERNANCE_RIGHTPANEL_VIEW_CONTRACT_V5",
        "target_file": REAL_REPO_PATHS["right_panel_component"],
        "view_key": "workflow_governance_snapshot",
        "display_sections": [
            "workflow_title",
            "critical_action_summary",
            "six_agent_swarm_status",
            "required_evidence",
            "x108_readonly_ingress_envelope",
            "blocked_steps",
            "boundary_flags",
        ],
        "typescript_shape_hint": {
            "workflow_governance_snapshot": {
                "snapshot_kind": "string",
                "workflow_governance_packet": "object",
                "x108_readonly_ingress_envelope": "object",
                "next_allowed_steps": "string[]",
                "blocked_steps": "string[]",
                "boundary": "ReadonlyBoundary",
            }
        },
        "ui_constraints": {
            "copy_only": True,
            "run_button_allowed": False,
            "execute_button_allowed": False,
            "merge_button_allowed": False,
            "human_review_required": True,
        },
        "boundary": {"decision_authority": DECISION_AUTHORITY, **READONLY_FLAGS},
    }
