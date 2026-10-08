from __future__ import annotations

"""R12-F3-C supervised prepare feedback projection.

This adapter reduces validated R12-F3-B prepare handoff feedback back into the
canonical R12-F1 supervised mission-state projection. It is deliberately
prepare-phase only: PREPARED is not EXECUTED, VERIFIED, CLOSED, or human
approved, and this module never calls executors, repair loops, providers,
KX108/Binder, Native Memory, Git, network, commit, push, or merge.
"""

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from obsidure_supervised_mission_state_v1 import (  # noqa: E402
    DECISION_AUTHORITY,
    STATUS_HELD as F1_STATUS_HELD,
    STATUS_PROJECTED as F1_STATUS_PROJECTED,
    STATUS_REJECTED as F1_STATUS_REJECTED,
    canonical_json,
    project_supervised_mission_state,
)
from obsidure_supervised_mission_stepper_v1 import (  # noqa: E402
    STATUS_PROPOSED as F3A_STATUS_PROJECTED,
    propose_supervised_mission_step,
)

ADAPTER_SCHEMA_VERSION = "OBSIDURE_SUPERVISED_PREPARE_FEEDBACK_PROJECTION_V1"
STATUS_PROJECTED = "R12_F3_C_PREPARE_FEEDBACK_PROJECTED"
STATUS_HELD = "R12_F3_C_PREPARE_FEEDBACK_HELD"
STATUS_REJECTED = "R12_F3_C_PREPARE_FEEDBACK_REJECTED"

PREPARE_PROPOSED = "PREPARE_PROPOSED"
PREPARED_AWAITING_APPROVAL = "PREPARED_AWAITING_APPROVAL"
HOLD = "HOLD"
BLOCKED = "BLOCKED"

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
    "automatic_retry": False,
    "ticket_completed": False,
    "prepared_promoted_to_executed": False,
    "prepared_promoted_to_verified": False,
    "prepared_promoted_to_closed": False,
}

_PREPARED_ACTION_STATUS = "PREPARED_AWAITING_HUMAN_APPROVAL"
_EXPECTED_F3B_NEXT_STATE = "PREPARED_AWAITING_VALIDATED_FEEDBACK"
_REQUIRED_R9_REF_KEYS = (
    "r9_proposal_id",
    "r9_manifest_id",
    "r9_validation_id",
    "r9_handoff_id",
    "candidate_patch_hash",
)
_PROJECT_KEYS = ("repository_identity", "local_root", "worktree", "branch", "base_sha")


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


def _dedupe(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _fail(status: str, reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": status,
        "reason": reason,
        "prepare_phase_status": None,
        "feedback_projected": False,
        "duplicate_idempotent": False,
        "budget_consumed": False,
        "decision_authority": DECISION_AUTHORITY,
        "obsidure_authority": "NONE",
        "supervisor_authority": "NONE",
        **_NO_AUTHORITY_FIELDS,
        **extra,
    }


def _proposal_from_step(supervisor_step: Mapping[str, Any]) -> Mapping[str, Any] | None:
    proposal = supervisor_step.get("step_proposal") if isinstance(supervisor_step, Mapping) else None
    if isinstance(proposal, Mapping):
        return proposal
    if isinstance(supervisor_step, Mapping) and supervisor_step.get("requested_operation") == "PREPARE_ONLY":
        return supervisor_step
    return None


def _feedback_payload(prepare_feedback: Mapping[str, Any]) -> Mapping[str, Any] | None:
    if not isinstance(prepare_feedback, Mapping):
        return None
    nested = prepare_feedback.get("prepare_handoff")
    if isinstance(nested, Mapping):
        return nested
    return prepare_feedback


def _project_matches(proposal: Mapping[str, Any], feedback: Mapping[str, Any]) -> bool:
    proposal_project = proposal.get("project") if isinstance(proposal.get("project"), Mapping) else {}
    feedback_project = feedback.get("project") if isinstance(feedback.get("project"), Mapping) else {}
    return all(str(proposal_project.get(key) or "") == str(feedback_project.get(key) or "") for key in _PROJECT_KEYS)


def _binding_reason(proposal: Mapping[str, Any], feedback: Mapping[str, Any], mission_projection: Mapping[str, Any]) -> str | None:
    if str(feedback.get("mission_id") or "") != str(proposal.get("mission_id") or ""):
        return "FEEDBACK_MISSION_MISMATCH"
    if str(feedback.get("selected_ticket_id") or "") != str(proposal.get("selected_ticket_id") or ""):
        return "FEEDBACK_TICKET_MISMATCH"
    if str(feedback.get("mandate_reference") or "") != str(proposal.get("mandate_reference") or ""):
        return "FEEDBACK_MANDATE_MISMATCH"
    if str(feedback.get("proposal_id") or "") != str(proposal.get("proposal_id") or ""):
        return "FEEDBACK_PROPOSAL_ID_MISMATCH"
    if str(feedback.get("proposal_hash") or "") != _sha256(proposal):
        return "FEEDBACK_PROPOSAL_HASH_MISMATCH"
    if not _project_matches(proposal, feedback):
        return "FEEDBACK_PROJECT_MISMATCH"
    canonical_state_json = feedback.get("canonical_state_json")
    if canonical_state_json and canonical_state_json != mission_projection.get("canonical_state_json"):
        return "FEEDBACK_CANONICAL_STATE_MISMATCH"
    return None


def _side_effect_reason(feedback: Mapping[str, Any]) -> str | None:
    for key in (
        "preparation_is_execution",
        "executor_invoked",
        "physical_mutation",
        "approval_created",
        "kx108_called",
        "binder_mutation",
        "memory_write",
        "native_memory_write",
        "filesystem_execution",
        "network_or_model_call",
        "commit_created",
        "push_performed",
        "merge_performed",
    ):
        if key == "preparation_is_execution":
            if feedback.get(key) is True:
                return "PREPARATION_CLAIMS_EXECUTION"
            continue
        if feedback.get(key) is True:
            return "PREPARE_FEEDBACK_SIDE_EFFECT:" + key.upper()
    prepared_action = feedback.get("prepared_action_reference")
    if isinstance(prepared_action, Mapping):
        if prepared_action.get("executor_invoked") is True:
            return "PREPARED_ACTION_EXECUTOR_INVOKED"
        if prepared_action.get("physical_mutation") is True:
            return "PREPARED_ACTION_PHYSICAL_MUTATION"
    return None


def _derive_phase(feedback: Mapping[str, Any]) -> tuple[str | None, str]:
    outcome = str(feedback.get("preparation_outcome") or feedback.get("status") or "").upper()
    reason = str(feedback.get("reason") or "").strip()
    if "BLOCK" in outcome:
        return BLOCKED, reason or "PREPARE_FEEDBACK_BLOCKED"
    if "HOLD" in outcome or "HELD" in outcome:
        return HOLD, reason or "PREPARE_FEEDBACK_HOLD"
    if outcome in {PREPARE_PROPOSED, "R12_F3_A_SUPERVISOR_STEP_PROPOSED"}:
        return PREPARE_PROPOSED, reason or PREPARE_PROPOSED

    prepared_action = feedback.get("prepared_action_reference")
    action_status = prepared_action.get("status") if isinstance(prepared_action, Mapping) else None
    if action_status == _PREPARED_ACTION_STATUS or "PREPARED" in outcome:
        return PREPARED_AWAITING_APPROVAL, reason or PREPARED_AWAITING_APPROVAL
    return None, "PREPARE_PHASE_STATUS_UNRECOGNIZED"


def _evidence_reason(proposal: Mapping[str, Any], feedback: Mapping[str, Any], phase: str) -> str | None:
    feedback_refs = set(_as_list(feedback.get("evidence_references")))
    proposal_refs = set(_as_list(proposal.get("evidence_references")))
    if proposal_refs and not proposal_refs.issubset(feedback_refs):
        return "FEEDBACK_EVIDENCE_BINDING_MISMATCH"
    if phase != PREPARED_AWAITING_APPROVAL:
        return None
    if not feedback_refs:
        return "PREPARATION_EVIDENCE_REQUIRED"
    r9_ref = feedback.get("r9_candidate_reference")
    if not isinstance(r9_ref, Mapping):
        return "R9_PREPARE_REFERENCE_REQUIRED"
    missing = [key for key in _REQUIRED_R9_REF_KEYS if not r9_ref.get(key)]
    if missing:
        return "R9_PREPARE_REFERENCE_INCOMPLETE:" + ",".join(missing)
    prepared_action = feedback.get("prepared_action_reference")
    if not isinstance(prepared_action, Mapping):
        return "PREPARED_ACTION_REFERENCE_REQUIRED"
    if prepared_action.get("status") != _PREPARED_ACTION_STATUS:
        return "PREPARED_ACTION_STATUS_NOT_AWAITING_APPROVAL"
    if not prepared_action.get("execution_authority_hash"):
        return "PREPARED_ACTION_AUTHORITY_HASH_REQUIRED"
    if not prepared_action.get("v2_exec_id"):
        return "PREPARED_ACTION_ID_REQUIRED"
    return None


def _duplicate_reason(feedback: Mapping[str, Any], prior_feedback: Mapping[str, Any] | None) -> tuple[str | None, bool]:
    if prior_feedback is None:
        return None, False
    prior = _feedback_payload(prior_feedback)
    if not isinstance(prior, Mapping):
        return "PRIOR_FEEDBACK_INVALID", False
    same_identity = any(
        prior.get(key) and feedback.get(key) and prior.get(key) == feedback.get(key)
        for key in ("feedback_id", "proposal_id", "proposal_hash")
    )
    if not same_identity:
        return None, False
    if _sha256(prior) == _sha256(feedback):
        return None, True
    return "DUPLICATE_FEEDBACK_CONFLICT", False


def _updated_state_for_feedback(
    state: Mapping[str, Any],
    *,
    ticket_id: str,
    phase: str,
    reason: str,
    feedback: Mapping[str, Any],
) -> dict[str, Any]:
    updated = deepcopy(dict(state))
    updated["tickets"] = deepcopy(list(updated.get("tickets") or []))
    feedback_refs = _as_list(feedback.get("evidence_references"))
    feedback_identity_refs = _as_list(
        [
            feedback.get("feedback_id"),
            feedback.get("proposal_id"),
            feedback.get("proposal_hash"),
        ]
    )
    r9_ref = feedback.get("r9_candidate_reference")
    if isinstance(r9_ref, Mapping):
        feedback_identity_refs.extend(_as_list(list(r9_ref.values())))
    prepared_action = feedback.get("prepared_action_reference")
    if isinstance(prepared_action, Mapping):
        feedback_identity_refs.extend(_as_list([prepared_action.get("execution_authority_hash"), prepared_action.get("v2_exec_id")]))

    for ticket in updated["tickets"]:
        if not isinstance(ticket, dict) or str(ticket.get("ticket_id") or "") != ticket_id:
            continue
        ticket["evidence_refs"] = _dedupe(_as_list(ticket.get("evidence_refs")) + feedback_refs + feedback_identity_refs)
        if phase == BLOCKED:
            ticket["status"] = "BLOCKED"
            ticket["blocked_reason"] = reason or BLOCKED
            ticket["hold_reason"] = ""
        else:
            ticket["status"] = "HELD"
            ticket["hold_reason"] = reason or phase
            ticket["blocked_reason"] = ""
        break

    updated["evidence_refs"] = _dedupe(_as_list(updated.get("evidence_refs")) + feedback_refs + feedback_identity_refs)
    return updated


def project_supervised_prepare_feedback(
    mission_projection: Mapping[str, Any],
    supervisor_step: Mapping[str, Any],
    prepare_feedback: Mapping[str, Any],
    *,
    prior_prepare_feedback: Mapping[str, Any] | None = None,
    observed_project_head: str | None = None,
) -> dict[str, Any]:
    """Reduce F3-B prepare feedback into a fresh F1 supervised projection."""

    if not isinstance(mission_projection, Mapping):
        return _fail(STATUS_REJECTED, "MISSION_PROJECTION_REQUIRED")
    if mission_projection.get("status") not in {F1_STATUS_PROJECTED, STATUS_PROJECTED}:
        return _fail(
            STATUS_HELD if mission_projection.get("status") == F1_STATUS_HELD else STATUS_REJECTED,
            str(mission_projection.get("reason") or "MISSION_PROJECTION_NOT_PROJECTED"),
            source_projection_status=mission_projection.get("status"),
        )
    canonical_state = mission_projection.get("canonical_state")
    if not isinstance(canonical_state, Mapping):
        return _fail(STATUS_REJECTED, "CANONICAL_STATE_REQUIRED")

    replayed_step = propose_supervised_mission_step(mission_projection, observed_project_head=observed_project_head)
    if replayed_step.get("status") != F3A_STATUS_PROJECTED:
        return _fail(
            STATUS_HELD if replayed_step.get("status") != F1_STATUS_REJECTED else STATUS_REJECTED,
            str(replayed_step.get("reason") or "SUPERVISOR_STEP_NOT_PROJECTED"),
            step_status=replayed_step.get("status"),
            step_feedback=replayed_step,
        )

    proposal = _proposal_from_step(supervisor_step)
    replayed_proposal = _proposal_from_step(replayed_step)
    if proposal is None or replayed_proposal is None:
        return _fail(STATUS_REJECTED, "SUPERVISOR_STEP_PROPOSAL_REQUIRED")
    if _sha256(proposal) != _sha256(replayed_proposal):
        return _fail(STATUS_REJECTED, "SUPERVISOR_STEP_PROPOSAL_NOT_REPLAYABLE")

    feedback = _feedback_payload(prepare_feedback)
    if not isinstance(feedback, Mapping):
        return _fail(STATUS_REJECTED, "PREPARE_FEEDBACK_REQUIRED")
    feedback = dict(feedback)

    duplicate_reason, duplicate_idempotent = _duplicate_reason(feedback, prior_prepare_feedback)
    if duplicate_reason:
        return _fail(STATUS_REJECTED, duplicate_reason, feedback_id=feedback.get("feedback_id"))

    binding_reason = _binding_reason(proposal, feedback, mission_projection)
    if binding_reason:
        return _fail(STATUS_REJECTED, binding_reason, feedback_id=feedback.get("feedback_id"))

    side_effect_reason = _side_effect_reason(feedback)
    if side_effect_reason:
        return _fail(STATUS_REJECTED, side_effect_reason, feedback_id=feedback.get("feedback_id"))

    phase, phase_reason = _derive_phase(feedback)
    if phase is None:
        return _fail(STATUS_REJECTED, phase_reason, feedback_id=feedback.get("feedback_id"))

    evidence_reason = _evidence_reason(proposal, feedback, phase)
    if evidence_reason:
        return _fail(STATUS_HELD, evidence_reason, feedback_id=feedback.get("feedback_id"), prepare_phase_status=phase)

    ticket_id = str(proposal.get("selected_ticket_id") or "")
    updated_state = _updated_state_for_feedback(canonical_state, ticket_id=ticket_id, phase=phase, reason=phase_reason, feedback=feedback)
    reduced_projection = project_supervised_mission_state(updated_state, observed_project_head=observed_project_head)

    if reduced_projection.get("status") == F1_STATUS_REJECTED:
        return _fail(
            STATUS_REJECTED,
            str(reduced_projection.get("reason") or "REDUCED_PROJECTION_REJECTED"),
            prepare_phase_status=phase,
            reduced_projection=reduced_projection,
        )

    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": STATUS_PROJECTED,
        "reason": None,
        "prepare_phase_status": phase,
        "feedback_projected": True,
        "feedback_id": feedback.get("feedback_id"),
        "mission_id": feedback.get("mission_id"),
        "selected_ticket_id": ticket_id,
        "proposal_id": feedback.get("proposal_id"),
        "proposal_hash": feedback.get("proposal_hash"),
        "duplicate_idempotent": duplicate_idempotent,
        "budget_consumed": False,
        "updated_mission_state": updated_state,
        "reduced_projection": reduced_projection,
        "expected_next_state": reduced_projection.get("unique_next_ticket_id"),
        "pending_approval_is_completion": False,
        "one_to_one_feedback_binding": True,
        "source_projection_hash": _sha256(mission_projection.get("canonical_state", {})),
        "updated_projection_hash": _sha256(reduced_projection.get("canonical_state", {})) if reduced_projection.get("canonical_state") else None,
        "decision_authority": DECISION_AUTHORITY,
        "obsidure_authority": "NONE",
        "supervisor_authority": "NONE",
        **_NO_AUTHORITY_FIELDS,
    }


__all__ = [
    "ADAPTER_SCHEMA_VERSION",
    "BLOCKED",
    "HOLD",
    "PREPARED_AWAITING_APPROVAL",
    "PREPARE_PROPOSED",
    "STATUS_HELD",
    "STATUS_PROJECTED",
    "STATUS_REJECTED",
    "project_supervised_prepare_feedback",
]
