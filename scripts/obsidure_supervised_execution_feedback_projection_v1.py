from __future__ import annotations

"""R12-F5-C1 supervised execution feedback state integration.

This reducer accepts validated R12-F5-B governed execution outcomes and folds
their evidence back into the canonical supervised mission state. Execution is
recorded as evidence, not as verification, closure, mission completion,
authorization, or an automatic repair/retry trigger.
"""

import hashlib
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_canonical_receipt_replay_v1 as _R8_REPLAY  # noqa: E402
import obsidia_realized_state_reconciliation_v1 as _R8_RECONCILE  # noqa: E402
from obsidure_supervised_dependency_state_integration_v1 import STATUS_UPDATED as F4B_STATUS_UPDATED  # noqa: E402
from obsidure_supervised_execution_outcome_bridge_v1 import (  # noqa: E402
    PHASE_AWAITING_VERIFICATION,
    PHASE_EXECUTED_OBSERVED,
    PHASE_EXECUTION_FAILED,
    PHASE_OUTCOME_UNCERTAIN,
    STATUS_EXECUTION_OUTCOME as F5B_STATUS_EXECUTION_OUTCOME,
    STATUS_HELD as F5B_STATUS_HELD,
)
from obsidure_supervised_mission_checkpoint_v1 import save_supervised_mission_checkpoint  # noqa: E402
from obsidure_supervised_mission_state_v1 import DECISION_AUTHORITY, canonical_json  # noqa: E402
from obsidure_supervised_mission_stepper_v1 import (  # noqa: E402
    STATUS_PROPOSED as F3A_STATUS_PROPOSED,
    propose_supervised_mission_step,
)
from obsidure_transitive_hold_projection_v1 import (  # noqa: E402
    STATUS_PROJECTED as F4A_STATUS_PROJECTED,
    project_transitive_dependency_blocks,
)

ADAPTER_SCHEMA_VERSION = "OBSIDURE_SUPERVISED_EXECUTION_FEEDBACK_PROJECTION_V1"
STATUS_PROJECTED = "R12_F5_C1_EXECUTION_FEEDBACK_PROJECTED"
STATUS_HELD = "R12_F5_C1_EXECUTION_FEEDBACK_HELD"
STATUS_REJECTED = "R12_F5_C1_EXECUTION_FEEDBACK_REJECTED"

_PROJECT_KEYS = ("repository_identity", "local_root", "worktree", "branch", "base_sha")

_NO_AUTHORITY_FIELDS = {
    "approval_created": False,
    "kx108_called_by_supervisor": False,
    "binder_mutation": False,
    "executor_invoked": False,
    "memory_write": False,
    "native_memory_write": False,
    "automatic_retry": False,
    "repair_loop_invoked": False,
    "ticket_verified": False,
    "ticket_closed": False,
    "mission_done": False,
    "commit_created": False,
    "push_performed": False,
    "merge_performed": False,
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


def _dedupe(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _fail(status: str, reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": status,
        "reason": reason,
        "execution_feedback_projected": False,
        "mission_update_accepted": False,
        "dependency_projection_refreshed": False,
        "next_step_recomputed": False,
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": "NONE",
        **_NO_AUTHORITY_FIELDS,
        **extra,
    }


def _ticket_by_id(state: Mapping[str, Any], ticket_id: str) -> Mapping[str, Any] | None:
    for ticket in state.get("tickets") or ():
        if isinstance(ticket, Mapping) and ticket.get("ticket_id") == ticket_id:
            return ticket
    return None


def _handoff_feedback(prepare_handoff_result: Mapping[str, Any]) -> Mapping[str, Any] | None:
    feedback = prepare_handoff_result.get("handoff_feedback")
    return feedback if isinstance(feedback, Mapping) else None


def _prepared_action(prepare_handoff_result: Mapping[str, Any]) -> Mapping[str, Any] | None:
    prepared = prepare_handoff_result.get("r9_prepare_result")
    if isinstance(prepared, Mapping) and isinstance(prepared.get("prepared_action"), Mapping):
        return prepared["prepared_action"]
    feedback = _handoff_feedback(prepare_handoff_result)
    if isinstance(feedback, Mapping) and isinstance(feedback.get("prepared_action_reference"), Mapping):
        return feedback["prepared_action_reference"]
    return None


def _patch_hash(prepare_handoff_result: Mapping[str, Any], action: Mapping[str, Any]) -> str:
    if action.get("patch_sha256"):
        return str(action.get("patch_sha256"))
    feedback = _handoff_feedback(prepare_handoff_result) or {}
    r9_ref = feedback.get("r9_candidate_reference")
    if isinstance(r9_ref, Mapping):
        return str(r9_ref.get("candidate_patch_hash") or "")
    return ""


def _project_matches(state: Mapping[str, Any], feedback: Mapping[str, Any]) -> bool:
    project = feedback.get("project") if isinstance(feedback.get("project"), Mapping) else {}
    return all(str(project.get(key) or "") == str(state.get("repository_identity" if key == "repository_identity" else key) or "") for key in _PROJECT_KEYS)


def _outcome_hash(outcome: Mapping[str, Any]) -> str:
    return _sha256(
        {
            "mission_id": outcome.get("mission_id"),
            "selected_ticket_id": outcome.get("selected_ticket_id"),
            "mandate_reference": outcome.get("mandate_reference"),
            "prepared_proposal_id": outcome.get("prepared_proposal_id"),
            "prepared_patch_hash": outcome.get("prepared_patch_hash"),
            "authority_reference": outcome.get("authority_reference"),
            "action_evidence_id": outcome.get("action_evidence_id"),
            "execution_phase": outcome.get("execution_phase"),
            "r8_replay": outcome.get("r8_replay"),
            "realized_state_reconciliation": outcome.get("realized_state_reconciliation"),
        }
    )


def _duplicate_reason(outcome: Mapping[str, Any], prior: Mapping[str, Any] | None) -> tuple[str | None, bool]:
    if prior is None:
        return None, False
    if not isinstance(prior, Mapping):
        return "PRIOR_EXECUTION_FEEDBACK_INVALID", False
    same_identity = any(
        outcome.get(key) and prior.get(key) and outcome.get(key) == prior.get(key)
        for key in ("execution_attempt_id", "action_evidence_id")
    )
    if not same_identity:
        return None, False
    if _outcome_hash(outcome) == _outcome_hash(prior):
        return None, True
    return "DUPLICATE_EXECUTION_FEEDBACK_CONFLICT", False


def _r8_reason(outcome: Mapping[str, Any]) -> str | None:
    action_evidence_id = outcome.get("action_evidence_id")
    if not isinstance(action_evidence_id, str) or not action_evidence_id.startswith("aev-"):
        return "ACTION_EVIDENCE_ID_REQUIRED"
    replay = outcome.get("r8_replay")
    if not isinstance(replay, Mapping):
        return "R8_REPLAY_REQUIRED"
    if replay.get("action_evidence_id") != action_evidence_id:
        return "R8_REPLAY_ACTION_EVIDENCE_MISMATCH"
    if replay.get("replay_verdict") not in {_R8_REPLAY.VERDICT_VERIFIED, _R8_REPLAY.VERDICT_VERIFIED_WITH_LIMITS}:
        return "R8_REPLAY_NOT_VERIFIED"
    reconciliation = outcome.get("realized_state_reconciliation")
    if not isinstance(reconciliation, Mapping):
        return "R8_RECONCILIATION_REQUIRED"
    if reconciliation.get("action_evidence_id") != action_evidence_id:
        return "R8_RECONCILIATION_ACTION_EVIDENCE_MISMATCH"
    return None


def _phase_status(phase: str, reconciliation: Mapping[str, Any]) -> tuple[str, str, str]:
    rec_status = str(reconciliation.get("reconciliation_status") or "")
    if phase == PHASE_EXECUTED_OBSERVED:
        if rec_status not in {_R8_RECONCILE.STATUS_MATCH, _R8_RECONCILE.STATUS_NOOP_CONFIRMED}:
            return "HELD", PHASE_OUTCOME_UNCERTAIN, "R8_RECONCILIATION_NOT_CONFIRMED:" + rec_status
        return "HELD", PHASE_AWAITING_VERIFICATION, PHASE_AWAITING_VERIFICATION
    if phase == PHASE_EXECUTION_FAILED:
        return "EXECUTION_FAILED", PHASE_EXECUTION_FAILED, str(reconciliation.get("outcome") or PHASE_EXECUTION_FAILED)
    if phase == PHASE_OUTCOME_UNCERTAIN:
        return "HELD", PHASE_OUTCOME_UNCERTAIN, PHASE_OUTCOME_UNCERTAIN
    return "HELD", PHASE_AWAITING_VERIFICATION, PHASE_AWAITING_VERIFICATION


def _updated_state(
    state: Mapping[str, Any],
    *,
    outcome: Mapping[str, Any],
    ticket_id: str,
    ticket_status: str,
    reason: str,
    phase: str,
    budget_delta: int,
) -> dict[str, Any]:
    updated = deepcopy(dict(state))
    updated["tickets"] = deepcopy(list(updated.get("tickets") or []))
    refs = _dedupe(
        _as_list(outcome.get("action_evidence_id"))
        + _as_list(outcome.get("execution_attempt_id"))
        + _as_list(outcome.get("prepared_proposal_id"))
        + _as_list(outcome.get("prepared_patch_hash"))
        + _as_list((outcome.get("authority_reference") or {}).get("execution_authority_hash") if isinstance(outcome.get("authority_reference"), Mapping) else None)
    )
    for ticket in updated["tickets"]:
        if not isinstance(ticket, dict) or str(ticket.get("ticket_id") or "") != ticket_id:
            continue
        ticket["status"] = ticket_status
        if ticket_status == "HELD":
            ticket["hold_reason"] = reason
            ticket["blocked_reason"] = ""
        else:
            ticket["blocked_reason"] = reason
            ticket["hold_reason"] = ""
        ticket["execution_phase"] = phase
        ticket["action_evidence_id"] = outcome.get("action_evidence_id")
        ticket["execution_attempt_id"] = outcome.get("execution_attempt_id")
        ticket["pending_verification_status"] = outcome.get("pending_verification_status") or PHASE_AWAITING_VERIFICATION
        ticket["evidence_refs"] = _dedupe(_as_list(ticket.get("evidence_refs")) + refs)
        ticket["r10_repair_classification"] = deepcopy(dict(outcome.get("r10_repair_classification") or {}))
        ticket["verified"] = False
        ticket["closed"] = False
        break
    updated["evidence_refs"] = _dedupe(_as_list(updated.get("evidence_refs")) + refs)
    budget = dict(updated.get("global_budget") or {})
    if budget_delta:
        budget["consumed_actions"] = int(budget.get("consumed_actions") or 0) + budget_delta
        if isinstance(budget.get("remaining_actions"), int):
            budget["remaining_actions"] = max(0, int(budget["remaining_actions"]) - budget_delta)
    updated["global_budget"] = budget
    observed = dict(updated.get("observed_project_state") or {})
    observed["post_action_head"] = outcome.get("observed_post_action_head") or outcome.get("post_action_head") or ""
    observed["original_base_sha_preserved"] = updated.get("base_sha")
    observed["base_revalidation_required"] = bool(observed.get("post_action_head"))
    updated["observed_project_state"] = observed
    updated["execution_feedback_history"] = _dedupe(_as_list(updated.get("execution_feedback_history")) + refs)
    return updated


def project_supervised_execution_feedback(
    *,
    mission_update: Mapping[str, Any],
    prepare_handoff_result: Mapping[str, Any],
    execution_outcome: Mapping[str, Any],
    prior_execution_feedback: Mapping[str, Any] | None = None,
    checkpoint_store_dir: str | Path | None = None,
    observed_post_action_head: str | None = None,
) -> dict[str, Any]:
    """Accept one validated execution outcome and refresh supervised state."""

    if not isinstance(mission_update, Mapping) or mission_update.get("mission_update_accepted") is not True:
        return _fail(STATUS_REJECTED, "ACCEPTED_MISSION_UPDATE_REQUIRED")
    if not isinstance(prepare_handoff_result, Mapping) or prepare_handoff_result.get("prepare_handoff") is not True:
        return _fail(STATUS_REJECTED, "VALID_PREPARE_HANDOFF_REQUIRED")
    if not isinstance(execution_outcome, Mapping):
        return _fail(STATUS_REJECTED, "EXECUTION_OUTCOME_REQUIRED")
    if execution_outcome.get("status") not in {F5B_STATUS_EXECUTION_OUTCOME, F5B_STATUS_HELD}:
        return _fail(STATUS_REJECTED, "VALID_F5B_EXECUTION_OUTCOME_REQUIRED")
    if execution_outcome.get("status") == F5B_STATUS_HELD and execution_outcome.get("execution_phase") != PHASE_OUTCOME_UNCERTAIN:
        return _fail(STATUS_HELD, str(execution_outcome.get("reason") or "EXECUTION_OUTCOME_HELD"))
    state = mission_update.get("accepted_state")
    feedback = _handoff_feedback(prepare_handoff_result)
    action = _prepared_action(prepare_handoff_result)
    if not isinstance(state, Mapping) or not isinstance(feedback, Mapping) or not isinstance(action, Mapping):
        return _fail(STATUS_REJECTED, "MISSION_PREPARE_BINDING_REQUIRED")

    ticket_id = str(execution_outcome.get("selected_ticket_id") or feedback.get("selected_ticket_id") or "")
    ticket = _ticket_by_id(state, ticket_id)
    if not isinstance(ticket, Mapping):
        return _fail(STATUS_REJECTED, "EXECUTION_TICKET_NOT_FOUND")
    if state.get("mandate_revoked") is True or str(state.get("mandate_status") or "ACTIVE").upper() == "REVOKED":
        return _fail(STATUS_HELD, "HUMAN_MANDATE_REVOKED", accepted_state=deepcopy(dict(state)))
    if execution_outcome.get("mission_id") != state.get("mission_id"):
        return _fail(STATUS_REJECTED, "EXECUTION_MISSION_MISMATCH", accepted_state=deepcopy(dict(state)))
    if execution_outcome.get("mandate_reference") != state.get("human_mandate_reference"):
        return _fail(STATUS_REJECTED, "EXECUTION_MANDATE_MISMATCH", accepted_state=deepcopy(dict(state)))
    if execution_outcome.get("prepared_proposal_id") != feedback.get("proposal_id"):
        return _fail(STATUS_REJECTED, "EXECUTION_PROPOSAL_MISMATCH", accepted_state=deepcopy(dict(state)))
    duplicate_reason, duplicate_idempotent = _duplicate_reason(execution_outcome, prior_execution_feedback)
    if duplicate_reason:
        return _fail(STATUS_HELD, duplicate_reason, accepted_state=deepcopy(dict(state)))
    expected_patch = _patch_hash(prepare_handoff_result, action)
    if expected_patch and execution_outcome.get("prepared_patch_hash") != expected_patch:
        return _fail(STATUS_REJECTED, "EXECUTION_PATCH_HASH_MISMATCH", accepted_state=deepcopy(dict(state)))
    authority = execution_outcome.get("authority_reference") if isinstance(execution_outcome.get("authority_reference"), Mapping) else {}
    if authority.get("execution_authority_hash") != action.get("execution_authority_hash"):
        return _fail(STATUS_REJECTED, "EXECUTION_AUTHORITY_HASH_MISMATCH", accepted_state=deepcopy(dict(state)))
    if not _project_matches(state, feedback):
        return _fail(STATUS_REJECTED, "PREPARE_PROJECT_BINDING_MISMATCH", accepted_state=deepcopy(dict(state)))

    r8_reason = _r8_reason(execution_outcome)
    if r8_reason:
        return _fail(STATUS_HELD, r8_reason, accepted_state=deepcopy(dict(state)))

    reconciliation = execution_outcome.get("realized_state_reconciliation")
    phase = str(execution_outcome.get("execution_phase") or "")
    ticket_status, ticket_phase, ticket_reason = _phase_status(phase, reconciliation if isinstance(reconciliation, Mapping) else {})
    if phase == PHASE_OUTCOME_UNCERTAIN:
        ticket_status, ticket_phase, ticket_reason = "HELD", PHASE_OUTCOME_UNCERTAIN, execution_outcome.get("reason") or PHASE_OUTCOME_UNCERTAIN
    refs_already_recorded = bool(execution_outcome.get("action_evidence_id") in _as_list(state.get("evidence_refs")))
    budget_consumed = 0 if duplicate_idempotent else int(execution_outcome.get("budget_consumed") or 0)
    budget_delta = 0 if refs_already_recorded else int(execution_outcome.get("budget_consumed") or 0)
    enriched_outcome = dict(execution_outcome)
    if observed_post_action_head:
        enriched_outcome["observed_post_action_head"] = observed_post_action_head
    updated_state = _updated_state(
        state,
        outcome=enriched_outcome,
        ticket_id=ticket_id,
        ticket_status=ticket_status,
        reason=ticket_reason,
        phase=ticket_phase,
        budget_delta=budget_delta,
    )

    dependency_projection = project_transitive_dependency_blocks(updated_state)
    if dependency_projection.get("status") != F4A_STATUS_PROJECTED:
        return _fail(STATUS_HELD, str(dependency_projection.get("reason") or "DEPENDENCY_PROJECTION_HELD"), accepted_state=deepcopy(dict(state)), dependency_projection=dependency_projection)
    next_step = propose_supervised_mission_step(dependency_projection)
    checkpoint = None
    result = {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": STATUS_PROJECTED,
        "reason": None,
        "execution_feedback_projected": True,
        "mission_update_accepted": True,
        "dependency_projection_refreshed": True,
        "next_step_recomputed": True,
        "mission_id": updated_state.get("mission_id"),
        "selected_ticket_id": ticket_id,
        "execution_phase": ticket_phase,
        "action_evidence_id": execution_outcome.get("action_evidence_id"),
        "execution_attempt_id": execution_outcome.get("execution_attempt_id"),
        "duplicate_idempotent": duplicate_idempotent,
        "budget_consumed": budget_consumed,
        "accepted_state": updated_state,
        "accepted_state_hash": _sha256(updated_state),
        "previous_state_hash": _sha256(state),
        "dependency_projection": dependency_projection,
        "next_step": next_step,
        "unique_next_ticket_id": dependency_projection.get("unique_next_ticket_id"),
        "eligible_ticket_ids": list(dependency_projection.get("eligible_ticket_ids") or []),
        "transitive_dependency_blocks": list(dependency_projection.get("transitive_dependency_blocks") or []),
        "root_dependency_blocks": list(dependency_projection.get("root_dependency_blocks") or []),
        "independent_continuation": bool(dependency_projection.get("independent_continuation")),
        "prepare_available": next_step.get("status") == F3A_STATUS_PROPOSED,
        "r8_evidence_bound": True,
        "r10_repair_classification": deepcopy(dict(execution_outcome.get("r10_repair_classification") or {})),
        "git_base_evolution": {
            "original_base_sha": state.get("base_sha"),
            "observed_post_action_head": enriched_outcome.get("observed_post_action_head") or "",
            "base_revalidation_required": bool(enriched_outcome.get("observed_post_action_head")),
        },
        "checkpoint": checkpoint,
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": "NONE",
        **_NO_AUTHORITY_FIELDS,
    }
    if checkpoint_store_dir is not None:
        checkpoint_update = dict(result)
        checkpoint_update["status"] = F4B_STATUS_UPDATED
        result["checkpoint"] = save_supervised_mission_checkpoint(checkpoint_update, checkpoint_store_dir=checkpoint_store_dir)
    return result


__all__ = [
    "ADAPTER_SCHEMA_VERSION",
    "STATUS_HELD",
    "STATUS_PROJECTED",
    "STATUS_REJECTED",
    "project_supervised_execution_feedback",
]
