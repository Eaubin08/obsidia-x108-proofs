from __future__ import annotations

"""R12-F3-A deterministic supervised mission step proposal.

This module performs one readonly supervisor step over an existing R12-F1/F2
mission projection. It selects the unique next eligible ticket and returns a
prepare-only proposal. It never marks work completed and never invokes Brody,
providers, R9/R10/R11 executors, KX108/Binder, Native Memory, filesystem writes,
commits, pushes, merges, or an autonomous loop.
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from obsidure_supervised_mission_state_v1 import (  # noqa: E402
    DECISION_AUTHORITY,
    STATUS_BLOCKED as F1_STATUS_BLOCKED,
    STATUS_COMPLETE as F1_STATUS_COMPLETE,
    STATUS_HELD as F1_STATUS_HELD,
    STATUS_PROJECTED as F1_STATUS_PROJECTED,
    STATUS_REJECTED as F1_STATUS_REJECTED,
    canonical_json,
    project_supervised_mission_state,
)

ADAPTER_SCHEMA_VERSION = "OBSIDURE_SUPERVISED_MISSION_STEPPER_V1"
STATUS_PROPOSED = "R12_F3_A_SUPERVISOR_STEP_PROPOSED"
STATUS_HELD = "R12_F3_A_SUPERVISOR_STEP_HELD"
STATUS_REJECTED = "R12_F3_A_SUPERVISOR_STEP_REJECTED"
REQUESTED_OPERATION = "PREPARE_ONLY"
SUPERVISOR_AUTHORITY = "NONE"

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
    "ticket_completed": False,
    "commit_created": False,
    "push_performed": False,
    "merge_performed": False,
    "autonomous_loop": False,
}


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _as_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return tuple(str(v).strip() for v in value if str(v).strip())
    return ()


def _fail(status: str, reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": status,
        "reason": reason,
        "requested_operation": REQUESTED_OPERATION,
        "step_proposal": None,
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": SUPERVISOR_AUTHORITY,
        **_NO_AUTHORITY_FIELDS,
        **extra,
    }


def _projection_from_input(value: Mapping[str, Any], *, observed_project_head: str | None) -> dict[str, Any]:
    looks_like_projection = any(
        key in value
        for key in (
            "schema_version",
            "f1_projection_status",
            "canonical_mission_status",
            "unique_next_ticket_id",
            "eligible_ticket_ids",
        )
    )
    if looks_like_projection:
        if observed_project_head is not None and isinstance(value.get("canonical_state"), Mapping):
            return project_supervised_mission_state(dict(value["canonical_state"]), observed_project_head=observed_project_head)
        return dict(value)
    return project_supervised_mission_state(value, observed_project_head=observed_project_head)

def _ticket_by_id(state: Mapping[str, Any], ticket_id: str) -> Mapping[str, Any] | None:
    for ticket in state.get("tickets") or ():
        if isinstance(ticket, Mapping) and ticket.get("ticket_id") == ticket_id:
            return ticket
    return None


def _completed_dependencies(state: Mapping[str, Any], ticket: Mapping[str, Any]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    by_id = {t.get("ticket_id"): t for t in state.get("tickets") or () if isinstance(t, Mapping)}
    for dep_id in _as_tuple(ticket.get("dependency_ids")):
        dep = by_id.get(dep_id)
        if not isinstance(dep, Mapping):
            refs.append({"dependency_id": dep_id, "status": "MISSING", "evidence_refs": []})
            continue
        refs.append(
            {
                "dependency_id": dep_id,
                "status": dep.get("status"),
                "evidence_refs": list(_as_tuple(dep.get("evidence_refs"))),
            }
        )
    return refs


def _budget_available(state: Mapping[str, Any]) -> dict[str, Any]:
    budget = dict(state.get("global_budget") or {})
    return {
        "remaining_actions": budget.get("remaining_actions"),
        "remaining_attempts": budget.get("remaining_attempts"),
        "remaining_tickets": budget.get("remaining_tickets"),
        "timebox": dict(state.get("timebox") or {}),
    }


def _validate_feedback(feedback: Mapping[str, Any] | None) -> str | None:
    if feedback is None:
        return None
    if not isinstance(feedback, Mapping):
        return "MALFORMED_FEEDBACK"
    status = str(feedback.get("status") or feedback.get("classification") or "").upper()
    if status not in {"EXECUTED_VERIFIED", "STOP_SUCCESS", "BLOCKED", "HOLD", "RETRY_CANDIDATE"}:
        return "MALFORMED_FEEDBACK"
    if not any(isinstance(feedback.get(key), str) and feedback.get(key).strip() for key in ("action_evidence_id", "receipt_id", "feedback_id")):
        return "MALFORMED_FEEDBACK"
    return None


def _proposal_id(projection_hash: str, mission_id: str, ticket_id: str) -> str:
    return "step-" + hashlib.sha256(f"{projection_hash}:{mission_id}:{ticket_id}:{REQUESTED_OPERATION}".encode("utf-8")).hexdigest()[:24]


def propose_supervised_mission_step(
    mission_projection_or_state: Mapping[str, Any],
    *,
    observed_project_head: str | None = None,
    prior_step_proposal: Mapping[str, Any] | None = None,
    feedback: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return one deterministic prepare-only supervisor step proposal."""

    if not isinstance(mission_projection_or_state, Mapping):
        return _fail(STATUS_REJECTED, "MISSION_PROJECTION_REQUIRED")

    feedback_reason = _validate_feedback(feedback)
    if feedback_reason:
        return _fail(STATUS_HELD, feedback_reason)

    projection = _projection_from_input(mission_projection_or_state, observed_project_head=observed_project_head)
    f1_status = projection.get("f1_projection_status") or projection.get("canonical_mission_status") or projection.get("status")
    if f1_status != F1_STATUS_PROJECTED:
        reason = projection.get("reason") or f"MISSION_NOT_PROJECTABLE:{f1_status}"
        status = STATUS_REJECTED if f1_status == F1_STATUS_REJECTED else STATUS_HELD
        return _fail(status, reason, f1_projection_status=f1_status, projection=projection)

    state = projection.get("canonical_state")
    if not isinstance(state, Mapping):
        return _fail(STATUS_REJECTED, "CANONICAL_STATE_REQUIRED", projection=projection)

    evidence_refs = _as_tuple(state.get("evidence_refs"))
    if not evidence_refs:
        return _fail(STATUS_HELD, "MISSION_EVIDENCE_REQUIRED", mission_id=state.get("mission_id"), projection=projection)

    eligible = list(projection.get("eligible_ticket_ids") or ())
    selected = projection.get("unique_next_ticket_id")
    if not isinstance(selected, str) or not selected:
        return _fail(STATUS_HELD, projection.get("reason") or "NO_UNIQUE_NEXT_TICKET", mission_id=state.get("mission_id"), projection=projection)
    if selected not in eligible:
        return _fail(
            STATUS_HELD,
            "AMBIGUOUS_TICKET_SELECTION",
            mission_id=state.get("mission_id"),
            eligible_ticket_ids=eligible,
            unique_next_ticket_id=selected,
            projection=projection,
        )

    ticket = _ticket_by_id(state, selected)
    if not isinstance(ticket, Mapping):
        return _fail(STATUS_REJECTED, "SELECTED_TICKET_NOT_FOUND", mission_id=state.get("mission_id"), selected_ticket_id=selected)
    if ticket.get("status") in {"COMPLETED", "EXECUTED_VERIFIED", "PASS", "DONE"}:
        return _fail(STATUS_HELD, "SELECTED_TICKET_ALREADY_TERMINAL", mission_id=state.get("mission_id"), selected_ticket_id=selected)

    projection_hash = projection.get("supervised_state_hash")
    if not isinstance(projection_hash, str) or not projection_hash:
        projection_hash = _canonical_hash(state)
    proposal_id = _proposal_id(projection_hash, str(state.get("mission_id")), selected)
    duplicate = False
    if isinstance(prior_step_proposal, Mapping):
        previous_id = prior_step_proposal.get("proposal_id") or prior_step_proposal.get("step_proposal", {}).get("proposal_id")
        duplicate = previous_id == proposal_id

    proposal = {
        "proposal_id": proposal_id,
        "schema_version": ADAPTER_SCHEMA_VERSION,
        "mission_id": state.get("mission_id"),
        "selected_ticket_id": selected,
        "project": {
            "repository_identity": state.get("repository_identity"),
            "local_root": state.get("local_root"),
            "worktree": state.get("worktree"),
            "branch": state.get("branch"),
            "base_sha": state.get("base_sha"),
        },
        "dependency_references": _completed_dependencies(state, ticket),
        "mandate_reference": state.get("human_mandate_reference"),
        "requested_operation": REQUESTED_OPERATION,
        "budget_available": _budget_available(state),
        "semantic_unknowns": list(_as_tuple(state.get("explicit_unknowns")) + _as_tuple(ticket.get("unknowns"))),
        "evidence_references": list(dict.fromkeys(evidence_refs + _as_tuple(ticket.get("evidence_refs")))),
        "expected_next_state": {
            "ticket_id": selected,
            "from_status": ticket.get("status"),
            "to_status": "PREPARED_AWAITING_VALIDATED_FEEDBACK",
            "completion_requires_independent_feedback": True,
        },
        "proposal_does_not_complete_ticket": True,
        "projection_hash": projection_hash,
        "canonical_state_json": projection.get("canonical_state_json") or canonical_json(state),
        "duplicate_of_prior_proposal": duplicate,
        "sequencer_concept_reused": "deterministic_unique_ready_selection_prepare_only",
        "completion_feedback_required_later": True,
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": SUPERVISOR_AUTHORITY,
        **_NO_AUTHORITY_FIELDS,
    }
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": STATUS_PROPOSED,
        "reason": None,
        "mission_id": state.get("mission_id"),
        "selected_ticket_id": selected,
        "requested_operation": REQUESTED_OPERATION,
        "step_proposal": proposal,
        "proposal_id": proposal_id,
        "duplicate_of_prior_proposal": duplicate,
        "f1_projection_status": f1_status,
        "state_immutable": True,
        "canonical_state_json_before": projection.get("canonical_state_json") or canonical_json(state),
        "canonical_state_json_after": projection.get("canonical_state_json") or canonical_json(state),
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": SUPERVISOR_AUTHORITY,
        **_NO_AUTHORITY_FIELDS,
    }


__all__ = [
    "ADAPTER_SCHEMA_VERSION",
    "REQUESTED_OPERATION",
    "STATUS_HELD",
    "STATUS_PROPOSED",
    "STATUS_REJECTED",
    "propose_supervised_mission_step",
]
