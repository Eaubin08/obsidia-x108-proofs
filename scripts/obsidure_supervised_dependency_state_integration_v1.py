from __future__ import annotations

"""R12-F4-B supervised dependency state integration.

This adapter consumes validated R12-F3-C prepare feedback, accepts the resulting
mission-state update only when it is correctly bound, refreshes the R12-F4-A
transitive dependency projection, and recomputes the next prepare-only step via
R12-F3-A. It is not an autonomous execution loop and it never invokes ACT,
executors, repair, KX108/Binder, Native Memory, filesystem mutation, network,
commit, push, or merge.
"""

import hashlib
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from obsidure_supervised_mission_state_v1 import DECISION_AUTHORITY, canonical_json  # noqa: E402
from obsidure_supervised_mission_stepper_v1 import (  # noqa: E402
    STATUS_PROPOSED as F3A_STATUS_PROPOSED,
    propose_supervised_mission_step,
)
from obsidure_supervised_prepare_feedback_projection_v1 import (  # noqa: E402
    STATUS_PROJECTED as F3C_STATUS_PROJECTED,
    project_supervised_prepare_feedback,
)
from obsidure_transitive_hold_projection_v1 import (  # noqa: E402
    STATUS_PROJECTED as F4A_STATUS_PROJECTED,
    project_transitive_dependency_blocks,
)

ADAPTER_SCHEMA_VERSION = "OBSIDURE_SUPERVISED_DEPENDENCY_STATE_INTEGRATION_V1"
STATUS_UPDATED = "R12_F4_B_DEPENDENCY_STATE_UPDATED"
STATUS_HELD = "R12_F4_B_DEPENDENCY_STATE_HELD"
STATUS_REJECTED = "R12_F4_B_DEPENDENCY_STATE_REJECTED"

_NO_AUTHORITY_FIELDS = {
    "approval_created": False,
    "kx108_called": False,
    "binder_mutation": False,
    "executor_invoked": False,
    "repair_loop_invoked": False,
    "filesystem_execution": False,
    "network_or_model_call": False,
    "memory_write": False,
    "native_memory_write": False,
    "commit_created": False,
    "push_performed": False,
    "merge_performed": False,
    "autonomous_loop": False,
    "automatic_retry": False,
    "ticket_completed": False,
}


def _sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [str(item) for item in value if str(item)]
    return []


def _fail(status: str, reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": status,
        "reason": reason,
        "mission_update_accepted": False,
        "dependency_projection_refreshed": False,
        "next_step_recomputed": False,
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": "NONE",
        **_NO_AUTHORITY_FIELDS,
        **extra,
    }


def _canonical_state(projection: Mapping[str, Any]) -> Mapping[str, Any] | None:
    state = projection.get("canonical_state") if isinstance(projection, Mapping) else None
    return state if isinstance(state, Mapping) else None


def _state_ticket_ids(state: Mapping[str, Any]) -> set[str]:
    return {str(ticket.get("ticket_id") or "") for ticket in state.get("tickets") or () if isinstance(ticket, Mapping)}


def _ticket_by_id(state: Mapping[str, Any], ticket_id: str) -> Mapping[str, Any] | None:
    for ticket in state.get("tickets") or ():
        if isinstance(ticket, Mapping) and ticket.get("ticket_id") == ticket_id:
            return ticket
    return None


def _scope_preserved(before: Mapping[str, Any], after: Mapping[str, Any]) -> str | None:
    top_level = (
        "mission_id",
        "human_mandate_reference",
        "repository_identity",
        "local_root",
        "worktree",
        "branch",
        "base_sha",
        "original_goal",
        "acceptance_criteria",
        "bounded_authorized_scope",
        "mission_authority",
    )
    for key in top_level:
        if before.get(key) != after.get(key):
            return "MISSION_SCOPE_MUTATED:" + key.upper()
    if _state_ticket_ids(before) != _state_ticket_ids(after):
        return "TICKET_SET_MUTATED"
    for ticket_id in sorted(_state_ticket_ids(before)):
        old = _ticket_by_id(before, ticket_id)
        new = _ticket_by_id(after, ticket_id)
        if not isinstance(old, Mapping) or not isinstance(new, Mapping):
            return "TICKET_SET_MUTATED"
        for key in ("ticket_id", "objective", "dependency_ids", "acceptance_criteria", "authorized_paths", "authorized_operations", "source_ids", "unknowns"):
            if old.get(key) != new.get(key):
                return f"TICKET_SCOPE_MUTATED:{ticket_id}:{key.upper()}"
    return None


def _hold_without_corruption(
    *,
    reason: str,
    mission_projection: Mapping[str, Any],
    f3c_result: Mapping[str, Any] | None = None,
    observed_project_head: str | None = None,
) -> dict[str, Any]:
    original_state = _canonical_state(mission_projection)
    original_dependency_projection = None
    if isinstance(original_state, Mapping):
        original_dependency_projection = project_transitive_dependency_blocks(original_state, observed_project_head=observed_project_head)
    return _fail(
        STATUS_HELD,
        reason,
        original_state_preserved=True,
        accepted_state=deepcopy(original_state) if isinstance(original_state, Mapping) else None,
        dependency_projection=original_dependency_projection,
        feedback_projection=f3c_result,
    )


def integrate_supervised_dependency_state(
    *,
    mission_projection: Mapping[str, Any],
    supervisor_step: Mapping[str, Any],
    prepare_feedback: Mapping[str, Any],
    prior_prepare_feedback: Mapping[str, Any] | None = None,
    observed_project_head: str | None = None,
) -> dict[str, Any]:
    """Accept F3-C feedback and refresh F4-A/F3-A mission readiness."""

    if not isinstance(mission_projection, Mapping):
        return _fail(STATUS_REJECTED, "MISSION_PROJECTION_REQUIRED")
    before_state = _canonical_state(mission_projection)
    if not isinstance(before_state, Mapping):
        reason = str(mission_projection.get("reason") or "CANONICAL_STATE_REQUIRED")
        upstream_status = str(mission_projection.get("status") or "")
        status = STATUS_HELD if "HELD" in upstream_status or "BLOCKED" in upstream_status else STATUS_REJECTED
        return _fail(status, reason, source_projection_status=mission_projection.get("status"), source_projection=mission_projection)

    feedback_result = project_supervised_prepare_feedback(
        mission_projection,
        supervisor_step,
        prepare_feedback,
        prior_prepare_feedback=prior_prepare_feedback,
        observed_project_head=observed_project_head,
    )
    if feedback_result.get("status") != F3C_STATUS_PROJECTED:
        return _hold_without_corruption(
            reason=str(feedback_result.get("reason") or "PREPARE_FEEDBACK_NOT_ACCEPTED"),
            mission_projection=mission_projection,
            f3c_result=feedback_result,
            observed_project_head=observed_project_head,
        )

    updated_state = feedback_result.get("updated_mission_state")
    if not isinstance(updated_state, Mapping):
        return _hold_without_corruption(
            reason="UPDATED_MISSION_STATE_REQUIRED",
            mission_projection=mission_projection,
            f3c_result=feedback_result,
            observed_project_head=observed_project_head,
        )
    scope_reason = _scope_preserved(before_state, updated_state)
    if scope_reason:
        return _hold_without_corruption(
            reason=scope_reason,
            mission_projection=mission_projection,
            f3c_result=feedback_result,
            observed_project_head=observed_project_head,
        )

    dependency_projection = project_transitive_dependency_blocks(updated_state, observed_project_head=observed_project_head)
    if dependency_projection.get("status") != F4A_STATUS_PROJECTED:
        return _hold_without_corruption(
            reason=str(dependency_projection.get("reason") or "DEPENDENCY_PROJECTION_HELD"),
            mission_projection=mission_projection,
            f3c_result=feedback_result,
            observed_project_head=observed_project_head,
        )

    next_step = propose_supervised_mission_step(dependency_projection, observed_project_head=observed_project_head)
    next_step_ready = next_step.get("status") == F3A_STATUS_PROPOSED
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": STATUS_UPDATED,
        "reason": None,
        "mission_id": updated_state.get("mission_id"),
        "mission_update_accepted": True,
        "dependency_projection_refreshed": True,
        "next_step_recomputed": True,
        "feedback_id": feedback_result.get("feedback_id"),
        "duplicate_idempotent": bool(feedback_result.get("duplicate_idempotent")),
        "accepted_state": updated_state,
        "accepted_state_hash": _sha256(updated_state),
        "previous_state_hash": _sha256(before_state),
        "dependency_projection": dependency_projection,
        "next_step": next_step,
        "unique_next_ticket_id": dependency_projection.get("unique_next_ticket_id"),
        "eligible_ticket_ids": list(dependency_projection.get("eligible_ticket_ids") or []),
        "transitive_dependency_blocks": list(dependency_projection.get("transitive_dependency_blocks") or []),
        "root_dependency_blocks": list(dependency_projection.get("root_dependency_blocks") or []),
        "independent_continuation": bool(dependency_projection.get("independent_continuation")),
        "prepare_available": next_step_ready,
        "blocked_descendant_prepared": False,
        "original_mandate_preserved": before_state.get("human_mandate_reference") == updated_state.get("human_mandate_reference"),
        "acceptance_criteria_preserved": before_state.get("acceptance_criteria") == updated_state.get("acceptance_criteria"),
        "semantic_unknowns_preserved": before_state.get("explicit_unknowns") == updated_state.get("explicit_unknowns"),
        "evidence_references": _as_list(updated_state.get("evidence_refs")),
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": "NONE",
        **_NO_AUTHORITY_FIELDS,
    }


__all__ = [
    "ADAPTER_SCHEMA_VERSION",
    "STATUS_HELD",
    "STATUS_REJECTED",
    "STATUS_UPDATED",
    "integrate_supervised_dependency_state",
]
