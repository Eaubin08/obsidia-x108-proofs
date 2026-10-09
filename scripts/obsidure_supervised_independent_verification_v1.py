from __future__ import annotations

"""R12-F5-C2 independent ticket verification and mission closure.

This reducer consumes the accepted R12-F5-C1 execution-feedback projection plus
independent verification evidence. It may close a ticket and, only when the full
mission is proven complete, produce a mission completion proof. It never
executes, authorizes, retries, repairs, writes memory, or mutates KX108/Binder.
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
from obsidure_supervised_execution_feedback_projection_v1 import STATUS_PROJECTED as F5C1_STATUS_PROJECTED  # noqa: E402
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

ADAPTER_SCHEMA_VERSION = "OBSIDURE_SUPERVISED_INDEPENDENT_VERIFICATION_V1"
STATUS_VERIFIED = "R12_F5_C2_INDEPENDENT_VERIFICATION_ACCEPTED"
STATUS_HELD = "R12_F5_C2_INDEPENDENT_VERIFICATION_HELD"
STATUS_REJECTED = "R12_F5_C2_INDEPENDENT_VERIFICATION_REJECTED"

LEVEL_EXISTS = "EXISTS"
LEVEL_WIRED = "WIRED"
LEVEL_TESTED = "TESTED"
LEVEL_REAL_INPUT_TESTED = "REAL_INPUT_TESTED"
LEVEL_INDEPENDENTLY_VERIFIED = "INDEPENDENTLY_VERIFIED"
LEVEL_CLOSED = "CLOSED"

_PROJECT_KEYS = ("repository_identity", "local_root", "worktree", "branch", "base_sha")
_SUCCESS_TICKET_STATUSES = {"COMPLETED", "EXECUTED_VERIFIED", "PASS", "DONE"}

_NO_AUTHORITY_FIELDS = {
    "approval_created": False,
    "kx108_called": False,
    "kx108_called_by_supervisor": False,
    "binder_mutation": False,
    "executor_invoked": False,
    "repair_loop_invoked": False,
    "automatic_retry": False,
    "filesystem_execution": False,
    "network_or_model_call": False,
    "memory_write": False,
    "native_memory_write": False,
    "commit_created": False,
    "push_performed": False,
    "merge_performed": False,
    "autonomous_loop": False,
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
        "ticket_verified": False,
        "ticket_closed": False,
        "mission_done": False,
        "mission_completion_proof": None,
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
        if isinstance(ticket, Mapping) and str(ticket.get("ticket_id") or "") == ticket_id:
            return ticket
    return None


def _project_from_state(state: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "repository_identity": state.get("repository_identity"),
        "local_root": state.get("local_root"),
        "worktree": state.get("worktree"),
        "branch": state.get("branch"),
        "base_sha": state.get("base_sha"),
    }


def _project_matches_state(state: Mapping[str, Any], evidence: Mapping[str, Any]) -> bool:
    project = evidence.get("project") if isinstance(evidence.get("project"), Mapping) else _project_from_state(state)
    return all(str(project.get(key) or "") == str(state.get(key) or "") for key in _PROJECT_KEYS)


def _evidence_hash(evidence: Mapping[str, Any]) -> str:
    return _sha256(
        {
            "verification_id": evidence.get("verification_id"),
            "mission_id": evidence.get("mission_id"),
            "ticket_id": evidence.get("ticket_id"),
            "mandate_reference": evidence.get("mandate_reference"),
            "action_evidence_id": evidence.get("action_evidence_id"),
            "execution_attempt_id": evidence.get("execution_attempt_id"),
            "prepared_proposal_id": evidence.get("prepared_proposal_id"),
            "prepared_patch_hash": evidence.get("prepared_patch_hash"),
            "reviewer_verdict": evidence.get("reviewer_verdict"),
            "acceptance_criteria_results": evidence.get("acceptance_criteria_results"),
            "test_evidence": evidence.get("test_evidence"),
            "r8_replay": evidence.get("r8_replay"),
            "realized_state_reconciliation": evidence.get("realized_state_reconciliation"),
        }
    )


def _duplicate_reason(evidence: Mapping[str, Any], prior: Mapping[str, Any] | None) -> tuple[str | None, bool]:
    if prior is None:
        return None, False
    if not isinstance(prior, Mapping):
        return "PRIOR_VERIFICATION_EVIDENCE_INVALID", False
    same_identity = any(
        evidence.get(key) and prior.get(key) and evidence.get(key) == prior.get(key)
        for key in ("verification_id", "action_evidence_id", "execution_attempt_id")
    )
    if not same_identity:
        return None, False
    if _evidence_hash(evidence) == _evidence_hash(prior):
        return None, True
    return "DUPLICATE_VERIFICATION_EVIDENCE_CONFLICT", False


def _criteria_status(criteria: Sequence[str], results: Any) -> tuple[bool, str | None, list[str]]:
    if not isinstance(results, Sequence) or isinstance(results, (str, bytes, bytearray)):
        return False, "ACCEPTANCE_VERIFICATION_REQUIRED", []
    by_criterion: dict[str, Mapping[str, Any]] = {}
    refs: list[str] = []
    for raw in results:
        if not isinstance(raw, Mapping):
            return False, "ACCEPTANCE_RESULT_MALFORMED", refs
        criterion = str(raw.get("criterion") or "").strip()
        if criterion:
            by_criterion[criterion] = raw
        refs.extend(_as_list(raw.get("evidence_ref") or raw.get("evidence_refs")))
    for criterion in criteria:
        item = by_criterion.get(str(criterion))
        if item is None:
            return False, "ACCEPTANCE_CRITERION_UNVERIFIED:" + str(criterion), refs
        if str(item.get("status") or item.get("result") or "").upper() != "PASS":
            return False, "ACCEPTANCE_CRITERION_NOT_MET:" + str(criterion), refs
        if not _as_list(item.get("evidence_ref") or item.get("evidence_refs")):
            return False, "ACCEPTANCE_CRITERION_EVIDENCE_REQUIRED:" + str(criterion), refs
    return True, None, refs


def _tests_status(evidence: Mapping[str, Any]) -> tuple[bool, str | None, list[str], str]:
    tests = evidence.get("test_evidence")
    if not isinstance(tests, Sequence) or isinstance(tests, (str, bytes, bytearray)) or not tests:
        return False, "INDEPENDENT_TEST_EVIDENCE_REQUIRED", [], LEVEL_WIRED
    refs: list[str] = []
    real_input = False
    for raw in tests:
        if not isinstance(raw, Mapping):
            return False, "TEST_EVIDENCE_MALFORMED", refs, LEVEL_WIRED
        refs.extend(_as_list(raw.get("evidence_ref") or raw.get("evidence_refs") or raw.get("test_id")))
        if raw.get("independently_checked") is not True:
            return False, "TEST_EVIDENCE_NOT_INDEPENDENT", refs, LEVEL_TESTED
        if str(raw.get("status") or raw.get("result") or "").upper() != "PASS":
            return False, "INDEPENDENT_TEST_FAILED", refs, LEVEL_TESTED
        real_input = real_input or raw.get("real_input_tested") is True
    return True, None, refs, LEVEL_REAL_INPUT_TESTED if real_input else LEVEL_TESTED


def _r8_reason(evidence: Mapping[str, Any]) -> str | None:
    action_evidence_id = evidence.get("action_evidence_id")
    if not isinstance(action_evidence_id, str) or not action_evidence_id.startswith("aev-"):
        return "ACTION_EVIDENCE_ID_REQUIRED"
    replay = evidence.get("r8_replay")
    if not isinstance(replay, Mapping):
        return "R8_REPLAY_REQUIRED"
    if replay.get("action_evidence_id") != action_evidence_id:
        return "R8_REPLAY_ACTION_EVIDENCE_MISMATCH"
    
    verdict = replay.get("replay_verdict")
    if verdict == _R8_REPLAY.VERDICT_VERIFIED_WITH_LIMITS and replay.get("binder_replay_status") == "INLINE_STATUS_ONLY":
        return "BINDER_DECISION_RECONSTRUCTION_REQUIRED"
    if verdict != _R8_REPLAY.VERDICT_VERIFIED:
        return "R8_REPLAY_NOT_FULLY_VERIFIED"
        
    reconciliation = evidence.get("realized_state_reconciliation")
    if not isinstance(reconciliation, Mapping):
        return "R8_RECONCILIATION_REQUIRED"
    if reconciliation.get("action_evidence_id") != action_evidence_id:
        return "R8_RECONCILIATION_ACTION_EVIDENCE_MISMATCH"
    if reconciliation.get("reconciliation_status") not in {_R8_RECONCILE.STATUS_MATCH, _R8_RECONCILE.STATUS_NOOP_CONFIRMED}:
        return "R8_RECONCILIATION_NOT_CONFIRMED:" + str(reconciliation.get("reconciliation_status") or "")
    if reconciliation.get("conflicts"):
        return "R8_RECONCILIATION_CONFLICTS_PRESENT"
    return None


def _binding_reason(state: Mapping[str, Any], ticket: Mapping[str, Any], projection: Mapping[str, Any], evidence: Mapping[str, Any]) -> str | None:
    checks = (
        ("mission_id", state.get("mission_id"), evidence.get("mission_id")),
        ("ticket_id", ticket.get("ticket_id"), evidence.get("ticket_id")),
        ("mandate_reference", state.get("human_mandate_reference"), evidence.get("mandate_reference")),
        ("action_evidence_id", projection.get("action_evidence_id"), evidence.get("action_evidence_id")),
        ("execution_attempt_id", projection.get("execution_attempt_id"), evidence.get("execution_attempt_id")),
    )
    for key, expected, got in checks:
        if expected and got != expected:
            return "VERIFICATION_BINDING_MISMATCH:" + key.upper()
    if not _project_matches_state(state, evidence):
        return "PROJECT_BINDING_MISMATCH"
    return None


def _git_state_reason(state: Mapping[str, Any], projection: Mapping[str, Any], evidence: Mapping[str, Any], observed_project_head: str | None) -> str | None:
    observed = evidence.get("observed_project") if isinstance(evidence.get("observed_project"), Mapping) else {}
    original_base = str(observed.get("original_base_sha") or state.get("base_sha") or "")
    if original_base != str(state.get("base_sha") or ""):
        return "ORIGINAL_BASE_SHA_MISMATCH"
    post_action = str((projection.get("git_base_evolution") or {}).get("observed_post_action_head") or (state.get("observed_project_state") or {}).get("post_action_head") or "")
    current_head = str(observed_project_head or observed.get("current_head") or "")
    if current_head and current_head != str(state.get("base_sha") or ""):
        if not post_action or current_head != post_action or observed.get("authorized_state_evolution") is not True:
            return "UNAUTHORIZED_PROJECT_DRIFT"
        if not evidence.get("authority_reference") and not observed.get("state_evolution_authority_reference"):
            return "MISSING_EVOLUTION_AUTHORITY_EVIDENCE"
    if observed.get("scope_drift_observed") is True:
        if not observed.get("scope_drift_approved"):
            return "UNAPPROVED_SCOPE_DRIFT"
        if not evidence.get("authority_reference") and not observed.get("scope_drift_authority_reference"):
            return "MISSING_SCOPE_DRIFT_AUTHORITY_EVIDENCE"
    return None


def _has_blocking_dependency(projection: Mapping[str, Any], ticket_id: str) -> str | None:
    for block in list(projection.get("transitive_dependency_blocks") or []) + list(projection.get("root_dependency_blocks") or []):
        if isinstance(block, Mapping) and block.get("ticket_id") == ticket_id and block.get("root_ticket_id") != ticket_id:
            return str(block.get("reason") or "BLOCKED_DEPENDENCY")
    return None


def _updated_state(state: Mapping[str, Any], ticket_id: str, evidence: Mapping[str, Any], refs: Sequence[str]) -> dict[str, Any]:
    updated = deepcopy(dict(state))
    updated["tickets"] = deepcopy(list(updated.get("tickets") or []))
    for ticket in updated["tickets"]:
        if not isinstance(ticket, dict) or str(ticket.get("ticket_id") or "") != ticket_id:
            continue
        ticket["status"] = "COMPLETED"
        ticket["dependency_classification"] = "PASS"
        ticket["verification_level"] = LEVEL_CLOSED
        ticket["independent_verification_status"] = "PASS"
        ticket["independent_verification_id"] = evidence.get("verification_id")
        ticket["verified"] = True
        ticket["closed"] = True
        ticket["hold_reason"] = ""
        ticket["blocked_reason"] = ""
        ticket["evidence_refs"] = _dedupe(_as_list(ticket.get("evidence_refs")) + list(refs))
        break
    updated["evidence_refs"] = _dedupe(_as_list(updated.get("evidence_refs")) + list(refs))
    updated["verification_history"] = _dedupe(_as_list(updated.get("verification_history")) + _as_list(evidence.get("verification_id")))
    return updated


def _all_tickets_closed(state: Mapping[str, Any]) -> bool:
    tickets = [ticket for ticket in state.get("tickets") or () if isinstance(ticket, Mapping)]
    return bool(tickets) and all(str(ticket.get("status") or "").upper() in _SUCCESS_TICKET_STATUSES and ticket.get("closed") is True for ticket in tickets)


def _completion_proof(state: Mapping[str, Any], dependency_projection: Mapping[str, Any], evidence: Mapping[str, Any], mission_refs: Sequence[str]) -> dict[str, Any]:
    observed = evidence.get("observed_project") if isinstance(evidence.get("observed_project"), Mapping) else {}
    proof = {
        "schema_version": "OBSIDURE_SUPERVISED_MISSION_COMPLETION_PROOF_V1",
        "mission_id": state.get("mission_id"),
        "human_mandate_reference": state.get("human_mandate_reference"),
        "original_goal": state.get("original_goal"),
        "acceptance_criteria": list(_as_list(state.get("acceptance_criteria"))),
        "ticket_ids": [ticket.get("ticket_id") for ticket in state.get("tickets") or () if isinstance(ticket, Mapping)],
        "ticket_statuses": {ticket.get("ticket_id"): ticket.get("status") for ticket in state.get("tickets") or () if isinstance(ticket, Mapping)},
        "ticket_closed": {ticket.get("ticket_id"): bool(ticket.get("closed")) for ticket in state.get("tickets") or () if isinstance(ticket, Mapping)},
        "evidence_refs": _dedupe(_as_list(state.get("evidence_refs")) + list(mission_refs)),
        "reviewer_verdict": evidence.get("reviewer_verdict"),
        "final_observed_state": observed,
        "dependency_graph_resolved": not dependency_projection.get("root_dependency_blocks") and not dependency_projection.get("transitive_dependency_blocks"),
        "scope_drift_approved": bool(observed.get("scope_drift_approved")),
        "decision_authority": DECISION_AUTHORITY,
    }
    proof["completion_proof_digest"] = _sha256(proof)
    return proof


def verify_supervised_ticket_and_mission_closure(
    *,
    execution_feedback_projection: Mapping[str, Any],
    verification_evidence: Mapping[str, Any],
    prior_verification_evidence: Mapping[str, Any] | None = None,
    checkpoint_store_dir: str | Path | None = None,
    observed_project_head: str | None = None,
) -> dict[str, Any]:
    """Close a ticket and maybe the mission using independent readonly evidence."""

    if not isinstance(execution_feedback_projection, Mapping) or execution_feedback_projection.get("status") != F5C1_STATUS_PROJECTED:
        return _fail(STATUS_REJECTED, "ACCEPTED_F5C1_PROJECTION_REQUIRED")
    if not isinstance(verification_evidence, Mapping):
        return _fail(STATUS_REJECTED, "VERIFICATION_EVIDENCE_REQUIRED")
    state = execution_feedback_projection.get("accepted_state")
    if not isinstance(state, Mapping):
        return _fail(STATUS_REJECTED, "ACCEPTED_STATE_REQUIRED")
    ticket_id = str(verification_evidence.get("ticket_id") or execution_feedback_projection.get("selected_ticket_id") or "")
    ticket = _ticket_by_id(state, ticket_id)
    if not isinstance(ticket, Mapping):
        return _fail(STATUS_REJECTED, "VERIFICATION_TICKET_NOT_FOUND", accepted_state=deepcopy(dict(state)))
    if state.get("mandate_revoked") is True or str(state.get("mandate_status") or "ACTIVE").upper() == "REVOKED":
        return _fail(STATUS_HELD, "HUMAN_MANDATE_REVOKED", accepted_state=deepcopy(dict(state)))
    if str(ticket.get("status") or "").upper() in _SUCCESS_TICKET_STATUSES and ticket.get("closed") is True:
        duplicate_reason, duplicate_idempotent = _duplicate_reason(verification_evidence, prior_verification_evidence)
        if duplicate_reason:
            return _fail(STATUS_HELD, duplicate_reason, accepted_state=deepcopy(dict(state)))
        return _fail(STATUS_HELD, "TICKET_ALREADY_CLOSED", accepted_state=deepcopy(dict(state)), duplicate_idempotent=duplicate_idempotent)
    if str(ticket.get("execution_phase") or "") != "AWAITING_INDEPENDENT_VERIFICATION":
        return _fail(STATUS_HELD, "TICKET_NOT_AWAITING_INDEPENDENT_VERIFICATION", accepted_state=deepcopy(dict(state)))

    duplicate_reason, duplicate_idempotent = _duplicate_reason(verification_evidence, prior_verification_evidence)
    if duplicate_reason:
        return _fail(STATUS_HELD, duplicate_reason, accepted_state=deepcopy(dict(state)))
    binding_reason = _binding_reason(state, ticket, execution_feedback_projection, verification_evidence)
    if binding_reason:
        return _fail(STATUS_REJECTED, binding_reason, accepted_state=deepcopy(dict(state)))
    blocked_reason = _has_blocking_dependency(execution_feedback_projection, ticket_id)
    if blocked_reason:
        return _fail(STATUS_HELD, "TICKET_BLOCKED_BY_DEPENDENCY:" + blocked_reason, accepted_state=deepcopy(dict(state)))
    if verification_evidence.get("contradictions"):
        return _fail(STATUS_HELD, "CONTRADICTORY_CRITICAL_EVIDENCE", accepted_state=deepcopy(dict(state)))
    if str(verification_evidence.get("reviewer_verdict") or "").upper() != "PASS" or verification_evidence.get("reviewer_independent") is not True:
        return _fail(STATUS_HELD, "INDEPENDENT_REVIEWER_PASS_REQUIRED", verification_level=LEVEL_REAL_INPUT_TESTED, accepted_state=deepcopy(dict(state)))

    r8_reason = _r8_reason(verification_evidence)
    if r8_reason:
        return _fail(STATUS_HELD, r8_reason, verification_level=LEVEL_EXISTS, accepted_state=deepcopy(dict(state)))
    tests_ok, tests_reason, test_refs, test_level = _tests_status(verification_evidence)
    if not tests_ok:
        return _fail(STATUS_HELD, tests_reason or "INDEPENDENT_TESTS_NOT_PASSING", verification_level=test_level, defect_open=True, accepted_state=deepcopy(dict(state)))
    criteria_ok, criteria_reason, criteria_refs = _criteria_status(_as_list(ticket.get("acceptance_criteria")), verification_evidence.get("acceptance_criteria_results"))
    if not criteria_ok:
        return _fail(STATUS_HELD, criteria_reason or "ACCEPTANCE_CRITERIA_NOT_MET", verification_level=test_level, accepted_state=deepcopy(dict(state)))
    git_reason = _git_state_reason(state, execution_feedback_projection, verification_evidence, observed_project_head)
    if git_reason:
        return _fail(STATUS_HELD, git_reason, verification_level=LEVEL_INDEPENDENTLY_VERIFIED, accepted_state=deepcopy(dict(state)))

    refs = _dedupe(
        _as_list(verification_evidence.get("verification_id"))
        + _as_list(verification_evidence.get("action_evidence_id"))
        + _as_list(verification_evidence.get("execution_attempt_id"))
        + _as_list(verification_evidence.get("prepared_proposal_id"))
        + _as_list(verification_evidence.get("prepared_patch_hash"))
        + _as_list(verification_evidence.get("reviewer_reference"))
        + test_refs
        + criteria_refs
    )
    updated_state = _updated_state(state, ticket_id, verification_evidence, refs)
    dependency_projection = project_transitive_dependency_blocks(updated_state, observed_project_head=None)
    if dependency_projection.get("status") != F4A_STATUS_PROJECTED:
        return _fail(STATUS_HELD, str(dependency_projection.get("reason") or "DEPENDENCY_REPROJECTION_HELD"), accepted_state=deepcopy(dict(state)), dependency_projection=dependency_projection)
    next_step = propose_supervised_mission_step(dependency_projection)
    mission_criteria_ok, mission_criteria_reason, mission_refs = _criteria_status(
        _as_list(updated_state.get("acceptance_criteria")),
        verification_evidence.get("mission_acceptance_criteria_results"),
    )
    all_closed = _all_tickets_closed(updated_state)
    dependency_resolved = not dependency_projection.get("root_dependency_blocks") and not dependency_projection.get("transitive_dependency_blocks")
    mission_done = bool(all_closed and mission_criteria_ok and dependency_resolved)
    mission_completion_proof = _completion_proof(updated_state, dependency_projection, verification_evidence, mission_refs) if mission_done else None
    mission_hold_reason = None
    if all_closed and not mission_criteria_ok:
        mission_hold_reason = mission_criteria_reason or "MISSION_ACCEPTANCE_CRITERIA_NOT_MET"
    elif all_closed and not dependency_resolved:
        mission_hold_reason = "MISSION_DEPENDENCIES_UNRESOLVED"

    result = {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": STATUS_VERIFIED,
        "reason": mission_hold_reason,
        "ticket_verified": True,
        "ticket_closed": True,
        "mission_done": mission_done,
        "mission_completion_proof": mission_completion_proof,
        "mission_update_accepted": True,
        "dependency_projection_refreshed": True,
        "next_step_recomputed": True,
        "mission_id": updated_state.get("mission_id"),
        "selected_ticket_id": ticket_id,
        "verification_id": verification_evidence.get("verification_id"),
        "verification_level": LEVEL_CLOSED,
        "duplicate_idempotent": duplicate_idempotent,
        "accepted_state": updated_state,
        "accepted_state_hash": _sha256(updated_state),
        "previous_state_hash": _sha256(state),
        "dependency_projection": dependency_projection,
        "next_step": next_step,
        "unique_next_ticket_id": dependency_projection.get("unique_next_ticket_id"),
        "eligible_ticket_ids": list(dependency_projection.get("eligible_ticket_ids") or []),
        "transitive_dependency_blocks": list(dependency_projection.get("transitive_dependency_blocks") or []),
        "root_dependency_blocks": list(dependency_projection.get("root_dependency_blocks") or []),
        "prepare_available": next_step.get("status") == F3A_STATUS_PROPOSED,
        "r8_proof_bound": True,
        "independent_tests_bound": True,
        "acceptance_criteria_met": True,
        "mission_acceptance_criteria_met": mission_criteria_ok,
        "git_state_revalidated": True,
        "checkpoint": None,
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
    "LEVEL_CLOSED",
    "LEVEL_EXISTS",
    "LEVEL_INDEPENDENTLY_VERIFIED",
    "LEVEL_REAL_INPUT_TESTED",
    "LEVEL_TESTED",
    "LEVEL_WIRED",
    "STATUS_HELD",
    "STATUS_REJECTED",
    "STATUS_VERIFIED",
    "verify_supervised_ticket_and_mission_closure",
]
