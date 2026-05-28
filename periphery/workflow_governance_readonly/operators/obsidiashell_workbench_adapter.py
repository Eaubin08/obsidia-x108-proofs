from __future__ import annotations

from typing import Any, Dict

from ..constants import DECISION_AUTHORITY, READONLY_FLAGS
from ..skills.skill_build_workbench_view import build_workbench_view_model

ADAPTER_SPEC = {
    "adapter_id": "OBSIDIASHELL_WORKBENCH_ADAPTER_READONLY_V4",
    "route_candidate": "/workflow/governance/readonly/workbench",
    "render_mode": "STATIC_READONLY",
    "allowed_post": False,
    "allowed_kernel_mutation": False,
    "allowed_x108_mutation": False,
}


def build_obsidiashell_workbench_state_readonly(result: Dict[str, Any]) -> Dict[str, Any]:
    """Return serializable state for a future ObsidiaShell readonly route."""
    view = build_workbench_view_model(result)
    return {
        "route_candidate": ADAPTER_SPEC["route_candidate"],
        "render_mode": ADAPTER_SPEC["render_mode"],
        "adapter_spec": ADAPTER_SPEC,
        "view_model": view,
        "allowed_post": False,
        "allowed_kernel_mutation": False,
        "allowed_x108_mutation": False,
        "decision_authority": DECISION_AUTHORITY,
        "boundary": {"decision_authority": DECISION_AUTHORITY, **READONLY_FLAGS},
    }
